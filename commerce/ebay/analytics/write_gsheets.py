"""Google Sheets 直接書き込みモジュール（eBay週次レポート v4）

使い方:
  create_weekly_report_v3.py の末尾で
    from write_gsheets import write_report
    write_report(globals())
  を呼ぶ。globals() で分析済みデータを丸ごと渡す。

機能:
  - 全12シートをGoogleスプレッドシートに直接書き込み
  - ヘッダー固定（freeze panes）全シート対応
  - 備考欄の永続化（weekly_notes.json + スプレッドシートから読み取り）
  - 週別推移列（W1-W4）追加
  - 前週比較列追加
  - 改善追跡シート
  - コア売れ筋・削除候補の月間版シート
  - Item IDにeBayハイパーリンク付与
"""

import json, os, time, sys
import gspread
from google.oauth2.service_account import Credentials

sys.stdout.reconfigure(encoding='utf-8')

# ===== 設定 =====
_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_FILE = os.path.join(_DIR, 'reffort-sheets-fcbca5a4bbc2.json')
NOTES_FILE = os.path.join(_DIR, 'weekly_notes.json')
SPREADSHEET_ID = '1AT4x_qyohYiEs08RSHs5uFgqBAm51IRsY1ajybsJe0s'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# シート定義
SHEET_DEFS = [
    '💬 AI総評',
    '📊 サマリー',
    '🔥 コア売れ筋TOP15',
    '🚨 コア落ち',
    '⭐ 準売れ筋',
    '🌱 育成候補',
    '⚠️ 要調査',
    '🗑 削除候補',
    '🔥 コア売れ筋（月間）',
    '🗑 削除候補（月間）',
    '📈 改善追跡',
    '📋 週次履歴',
]

# ===== 色・書式ヘルパー =====
def _c(h):
    """hex→Google Sheets RGB dict"""
    h = h.lstrip('#')
    return {'red': int(h[0:2],16)/255, 'green': int(h[2:4],16)/255, 'blue': int(h[4:6],16)/255}

_BSTYLE = {'style': 'SOLID', 'colorStyle': {'rgbColor': _c('CCCCCC')}}
_BORDERS = {'top': _BSTYLE, 'bottom': _BSTYLE, 'left': _BSTYLE, 'right': _BSTYLE}

def _hdr(bg, fg='FFFFFF'):
    """ヘッダー行の書式"""
    return {
        'backgroundColor': _c(bg),
        'textFormat': {'bold': True, 'foregroundColor': _c(fg), 'fontFamily': 'Meiryo', 'fontSize': 10},
        'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE',
        'borders': _BORDERS, 'wrapStrategy': 'WRAP',
    }

def _body(bg=None, bold=False, wrap=False):
    """データ行の書式"""
    f = {
        'textFormat': {'fontFamily': 'Meiryo', 'fontSize': 9, 'bold': bold},
        'verticalAlignment': 'MIDDLE', 'borders': _BORDERS,
    }
    if bg: f['backgroundColor'] = _c(bg)
    if wrap: f['wrapStrategy'] = 'WRAP'
    return f

def _title_fmt(bg):
    """タイトル行の書式"""
    return {
        'backgroundColor': _c(bg),
        'textFormat': {'bold': True, 'foregroundColor': _c('FFFFFF'), 'fontFamily': 'Meiryo', 'fontSize': 12},
        'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE',
    }

def _note_fmt(bg='F5F5F5'):
    """説明行の書式"""
    return {
        'backgroundColor': _c(bg),
        'textFormat': {'fontFamily': 'Meiryo', 'fontSize': 9, 'italic': False},
        'horizontalAlignment': 'LEFT', 'verticalAlignment': 'MIDDLE',
        'wrapStrategy': 'WRAP',
    }

def _cl(n):
    """0-indexed列番号→列文字（A, B, ..., Z, AA, AB, ...）"""
    r = ''
    n += 1
    while n > 0:
        n -= 1
        r = chr(n % 26 + 65) + r
        n //= 26
    return r

def _rng(r1, c1, r2, c2):
    """行列番号(1-indexed)→A1形式"""
    return f'{_cl(c1-1)}{r1}:{_cl(c2-1)}{r2}'

# ===== ハイパーリンクヘルパー =====
def _add_links(ws, col_idx, id_row_pairs):
    """Item ID列にeBayハイパーリンクを追加"""
    if not id_row_pairs:
        return
    col = _cl(col_idx)
    cells = []
    for row_num, iid in id_row_pairs:
        cells.append({
            'range': f'{col}{row_num}',
            'values': [[f'=HYPERLINK("https://www.ebay.com/itm/{iid}","{iid}")']]
        })
    if cells:
        ws.batch_update(cells, value_input_option='USER_ENTERED')

# ===== CVR再計算ヘルパー =====
def _calc_weekly_cvr(item, week_idx):
    """週次CVRを取得（0の場合はsold/pvから再計算）"""
    cvr = item.get('weekly_cvr', [0]*4)[week_idx]
    if cvr > 0:
        return cvr
    sold = item.get('weekly_sold', [0]*4)[week_idx]
    pv = item.get('weekly_pv', [0]*4)[week_idx]
    if pv > 0 and sold > 0:
        return sold / pv * 100
    return 0.0

# ===== 接続 =====
def _connect():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    return gc.open_by_key(SPREADSHEET_ID)

# ===== ノート管理 =====
def _load_notes():
    """weekly_notes.jsonからノートを読み込む"""
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def _save_notes(notes):
    """weekly_notes.jsonにノートを保存する"""
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

def _read_sheet_notes(ws, id_col_idx, note_col_idx):
    """シートからItemIDとノートのペアを読み取る（0-indexed列番号）"""
    notes = {}
    try:
        data = ws.get_all_values()
        for row in data[4:]:  # ヘッダー（3-4行目）以降のデータ行
            if len(row) > max(id_col_idx, note_col_idx):
                iid = str(row[id_col_idx]).strip()
                note = str(row[note_col_idx]).strip()
                if iid and note:
                    notes[iid] = note
    except Exception:
        pass
    return notes

def _collect_all_notes(sh):
    """全シートから備考を収集してマージ"""
    notes = _load_notes()
    # 要調査: B列=ItemID(1), Q列=備考(16)
    try:
        ws = sh.worksheet('⚠️ 要調査')
        notes.update(_read_sheet_notes(ws, 1, 16))
    except Exception:
        pass
    # 削除候補: B列=ItemID(1), M列=備考(12)
    try:
        ws = sh.worksheet('🗑 削除候補')
        notes.update(_read_sheet_notes(ws, 1, 12))
    except Exception:
        pass
    # 準売れ筋: C列=ItemID(2), R列=備考(17)
    try:
        ws = sh.worksheet('⭐ 準売れ筋')
        notes.update(_read_sheet_notes(ws, 2, 17))
    except Exception:
        pass
    # 育成候補: B列=ItemID(1), Q列=備考(16)
    try:
        ws = sh.worksheet('🌱 育成候補')
        notes.update(_read_sheet_notes(ws, 1, 16))
    except Exception:
        pass
    return notes

# ===== シート管理 =====
def _setup_sheets(sh):
    """必要なシートを作成（既存シートの並び順はユーザー設定を尊重して変更しない）"""
    existing = {ws.title: ws for ws in sh.worksheets()}

    # 必要なシートを作成（存在しないもののみ）
    for name in SHEET_DEFS:
        if name not in existing:
            sh.add_worksheet(title=name, rows=1000, cols=30)
            time.sleep(0.5)

    # デフォルトシート削除
    ws_map = {ws.title: ws for ws in sh.worksheets()}
    for default_name in ('Sheet1', 'シート1'):
        if default_name in ws_map and len(ws_map) > len(SHEET_DEFS):
            try:
                sh.del_worksheet(ws_map[default_name])
            except Exception:
                pass

def _set_widths(sh, ws, pixel_widths):
    """列幅をピクセル単位で一括設定"""
    reqs = []
    for i, px in enumerate(pixel_widths):
        reqs.append({'updateDimensionProperties': {
            'properties': {'pixelSize': px},
            'range': {'sheetId': ws.id, 'dimension': 'COLUMNS',
                      'startIndex': i, 'endIndex': i + 1},
            'fields': 'pixelSize',
        }})
    sh.batch_update({'requests': reqs})

def _merge_cells(sh, ws, range_str):
    """セルをマージ（A1形式）"""
    grid = gspread.utils.a1_range_to_grid_range(range_str, ws.id)
    sh.batch_update({'requests': [{'mergeCells': {'range': grid, 'mergeType': 'MERGE_ALL'}}]})

def _batch_merge_and_freeze(sh, ws, merge_ranges, freeze_rows):
    """unfreeze→全merge→re-freezeを1回のbatch_updateで実行（APIコール削減）"""
    reqs = []
    # 1. freeze解除
    reqs.append({'updateSheetProperties': {
        'properties': {'sheetId': ws.id, 'gridProperties': {'frozenRowCount': 0, 'frozenColumnCount': 0}},
        'fields': 'gridProperties.frozenRowCount,gridProperties.frozenColumnCount',
    }})
    # 2. 既存mergeをクリア（row3-4のみ）
    reqs.append({'unmergeCells': {
        'range': {'sheetId': ws.id, 'startRowIndex': 2, 'endRowIndex': 4,
                  'startColumnIndex': 0, 'endColumnIndex': 100},
    }})
    # 3. 全merge
    for range_str in merge_ranges:
        grid = gspread.utils.a1_range_to_grid_range(range_str, ws.id)
        reqs.append({'mergeCells': {'range': grid, 'mergeType': 'MERGE_ALL'}})
    # 4. re-freeze
    reqs.append({'updateSheetProperties': {
        'properties': {'sheetId': ws.id, 'gridProperties': {'frozenRowCount': freeze_rows}},
        'fields': 'gridProperties.frozenRowCount',
    }})
    sh.batch_update({'requests': reqs})

def _write_two_row_header(ws, sh, row3, row4, merge_groups, h_merge_groups, ncols, hdr_color):
    """2段ヘッダーを書き込み、マージリクエストを返す

    Args:
        ws: ワークシート
        sh: スプレッドシート
        row3: カテゴリ行（行3）の値リスト
        row4: サブヘッダー行（行4）の値リスト
        merge_groups: 縦マージ対象の列インデックスリスト（0-indexed）— row3とrow4を結合
        h_merge_groups: 横マージ対象の (start_col, end_col) タプルリスト（0-indexed）— row3内で結合
        ncols: 列数
        hdr_color: ヘッダー背景色（hex）

    Returns:
        (fmts, merge_ops) — fmtsはbatch_format用、merge_opsは後で実行するマージ操作リスト
    """
    fmts = [
        {'range': _rng(3, 1, 3, ncols), 'format': _hdr(hdr_color)},
        {'range': _rng(4, 1, 4, ncols), 'format': _hdr(hdr_color)},
    ]
    merge_ops = []
    # 縦マージ（単独列：row3とrow4を結合）
    for col_idx in merge_groups:
        cl = _cl(col_idx)
        merge_ops.append(f'{cl}3:{cl}4')
    # 横マージ（グループ列：row3内で結合）
    for start_c, end_c in h_merge_groups:
        merge_ops.append(f'{_cl(start_c)}3:{_cl(end_c)}3')
    return fmts, merge_ops


def _add_dropdown(sh, ws, col_idx, start_row, end_row, values_list):
    """ドロップダウンバリデーション"""
    sh.batch_update({'requests': [{'setDataValidation': {
        'range': {'sheetId': ws.id, 'startRowIndex': start_row - 1, 'endRowIndex': end_row,
                  'startColumnIndex': col_idx, 'endColumnIndex': col_idx + 1},
        'rule': {
            'condition': {'type': 'ONE_OF_LIST',
                          'values': [{'userEnteredValue': v} for v in values_list]},
            'showCustomUi': True, 'strict': False,
        }
    }}]})

# ===== データ取得ヘルパー（globals()から必要な関数・データを取り出す）=====
class _G:
    """globals()のデータをまとめて保持するコンテキスト"""
    pass

def _init_ctx(g):
    """globals() dictからコンテキストを構築"""
    ctx = _G()
    # 基本設定
    ctx.period = g['PERIOD_LABEL']
    ctx.today = g['TODAY']
    ctx.weeks = g['WEEKS']
    ctx.week_stats = g['week_stats']
    ctx.wt = g['weekly_traffic_totals']
    ctx.use_weekly = g['USE_WEEKLY_TRAFFIC']

    # 集計値
    ctx.total_imps = g['total_imps_t']
    ctx.total_pv = g['total_pv_t']
    ctx.total_sold = g['total_sold_t']
    ctx.overall_cvr = g['overall_cvr']
    ctx.overall_ctr = g['overall_ctr']
    ctx.total_items = g['total_items']
    ctx.zero_sold_cnt = g['zero_sold_cnt']
    ctx.week_sold_skus = g['week_sold_skus']
    ctx.total_orders = g['total_orders']
    ctx.total_gross = g['total_gross']
    ctx.total_fvf = g['total_fvf']
    ctx.total_intl = g['total_intl']
    ctx.total_plg = g['total_plg_fee_tx']
    ctx.total_off = g['total_off_fee']
    ctx.plp_fee = g['PLP_FEE_TOTAL']
    ctx.net = g['net_after_plp']

    # サイト別
    ctx.site_stats = g['site_stats']
    ctx.site_week = g.get('site_week_stats', {})
    ctx.site_order = g['SITE_ORDER']

    # カテゴリ別
    ctx.top15 = g['top15']
    ctx.top15_ids = g['top15_ids']
    ctx.コア落ち = g.get('コア落ち', [])
    ctx.準売れ筋 = g['準売れ筋']
    ctx.準売れ筋_cnt = g['準売れ筋_sku_cnt']
    ctx.育成 = g['育成']
    ctx.育成_cnt = g['育成_sku_cnt']
    ctx.要調査 = g['要調査']
    ctx.要調査_cnt = g['要調査_sku_cnt']
    ctx.要調査_ids = g['要調査_ids']
    ctx.削除L1 = g['削除L1']
    ctx.削除L1_cnt = g['削除L1_sku_cnt']
    ctx.削除L1_ids = g['削除L1_ids']
    ctx.削除L2 = g['削除L2']
    ctx.削除L2_cnt = g['削除L2_sku_cnt']
    ctx.削除L2_ids = g['削除L2_ids']
    ctx.items = g['items']
    ctx.items_by_id = g['items_by_id']

    # 履歴
    ctx.history = g['history']
    ctx.last_data = g['last_data']
    ctx.history_key = g['HISTORY_DATE_KEY']

    # AI分析
    ctx.ai_review = g['ai_review']
    ctx.suggestions = g['suggestions']

    # セラーキャッシュ・関数
    ctx.seller_cache = g['seller_cache']
    ctx.get_item_api_data = g['get_item_api_data']
    ctx.get_prev_category = g['get_prev_category']
    ctx.get_current_category = g['get_current_category']
    ctx.pct_change = g['pct_change']
    ctx.IKUSEI_PV = g['IKUSEI_PV_THRESHOLD']

    # ノート（後で設定）
    ctx.notes = {}

    return ctx

def _apply_exclude_filter(ctx):
    """備考欄が『削除』のアイテムを全カテゴリリストから除外する。
    高橋紗英 2026-04-21 要望「備考欄に『削除』と記載のある行は、行ごと削除してほしい」反映。
    判定: trim後の備考が完全一致『削除』（『削除NG』『削除しない』等の否定形は対象外）。
    """
    excluded = {iid for iid, note in ctx.notes.items()
                if note and str(note).strip() == '削除'}
    ctx.excluded_count = len(excluded)
    if not excluded:
        return

    print(f'   🗑️ 「削除」マーク行の除外: {len(excluded)}件（高橋紗英 要望反映）')

    def _drop(seq):
        return [i for i in seq if i.get('id') not in excluded]

    ctx.items = _drop(ctx.items)
    ctx.items_by_id = {iid: i for iid, i in ctx.items_by_id.items() if iid not in excluded}
    ctx.top15 = _drop(ctx.top15)
    ctx.top15_ids = [iid for iid in ctx.top15_ids if iid not in excluded]
    ctx.コア落ち = _drop(ctx.コア落ち)
    ctx.準売れ筋 = _drop(ctx.準売れ筋)
    ctx.育成 = _drop(ctx.育成)
    ctx.要調査 = _drop(ctx.要調査)
    ctx.要調査_ids = [iid for iid in ctx.要調査_ids if iid not in excluded]
    ctx.削除L1 = _drop(ctx.削除L1)
    ctx.削除L1_ids = [iid for iid in ctx.削除L1_ids if iid not in excluded]
    ctx.削除L2 = _drop(ctx.削除L2)
    ctx.削除L2_ids = [iid for iid in ctx.削除L2_ids if iid not in excluded]

    ctx.準売れ筋_cnt = len({i['id'] for i in ctx.準売れ筋})
    ctx.育成_cnt = len({i['id'] for i in ctx.育成})
    ctx.要調査_cnt = len({i['id'] for i in ctx.要調査})
    ctx.削除L1_cnt = len({i['id'] for i in ctx.削除L1})
    ctx.削除L2_cnt = len({i['id'] for i in ctx.削除L2})


def _swl(ctx, idx):
    """短縮週ラベル（W1, W2, etc.）"""
    return ctx.weeks[idx][0].split('\n')[0]

def _item_sku(ctx, item_id):
    """ItemIDからSKUを取得"""
    return ctx.seller_cache.get(item_id, {}).get('sku', '')

def _ebay_url(item_id):
    """eBayリンク"""
    return f'https://www.ebay.com/itm/{item_id}'

# ===== 終了済み商品フィルタ =====
def _is_ended_item(ctx, item):
    """商品が終了済み（seller_cacheに存在しない or 在庫0＆トラフィックゼロ）かを判定"""
    iid = item['id']
    if iid not in ctx.seller_cache:
        return True
    sc = ctx.seller_cache[iid]
    if sc.get('qty', 0) == 0 and item.get('imps', 0) == 0 and item.get('pv', 0) == 0:
        return True
    return False

# ===== 各シート書き込み関数 =====

def _write_ai_review(sh, ws, ctx):
    """💬 AI総評"""
    rows = [[f'💬 AI総評 ― {ctx.period}  （生成日: {ctx.today.strftime("%Y/%m/%d")}）']]
    for line in ctx.ai_review:
        rows.append([line])

    ws.update(values=rows, range_name='A1')

    # 書式
    fmts = [{'range': 'A1', 'format': _title_fmt('2E7D32')}]
    for i in range(len(ctx.ai_review)):
        r = i + 2
        line = ctx.ai_review[i] if i < len(ctx.ai_review) else ''
        if line.startswith('【'):
            fmts.append({'range': f'A{r}', 'format': {
                'textFormat': {'bold': True, 'foregroundColor': _c('1B5E20'), 'fontFamily': 'Meiryo', 'fontSize': 10},
                'backgroundColor': _c('F1F8E9'), 'wrapStrategy': 'WRAP',
            }})
        elif line.startswith('  '):
            fmts.append({'range': f'A{r}', 'format': {
                'textFormat': {'foregroundColor': _c('333333'), 'fontFamily': 'Meiryo', 'fontSize': 9},
                'backgroundColor': _c('F1F8E9'), 'wrapStrategy': 'WRAP',
            }})
        else:
            fmts.append({'range': f'A{r}', 'format': {
                'textFormat': {'foregroundColor': _c('1B5E20'), 'fontFamily': 'Meiryo', 'fontSize': 9},
                'backgroundColor': _c('F1F8E9'), 'wrapStrategy': 'WRAP',
            }})
    ws.batch_format(fmts)
    _set_widths(sh, ws, [900])
    ws.freeze(rows=1)


def _write_summary(sh, ws, ctx):
    """📊 サマリー"""
    rows = []
    fmts = []
    r = 1

    # タイトル
    rows.append([f'📊 eBay 週次レポート  {ctx.period}  （生成日: {ctx.today.strftime("%Y/%m/%d")}）',
                 '', '', '', '', '', ''])
    fmts.append({'range': _rng(r,1,r,7), 'format': _title_fmt('1A237E')})
    r += 1

    # セクション: パフォーマンス指標
    rows.append(['■ パフォーマンス指標（週別）', '', '', '', '', '', ''])
    fmts.append({'range': _rng(r,1,r,7), 'format': _note_fmt('E8EAF6')})
    r += 1

    # ヘッダー行
    wl = [ctx.weeks[i][0].replace('\n', ' ') for i in range(4)]
    rows.append(['指標', wl[0], wl[1], wl[2], wl[3], '合計', 'W3→W4変化'])
    fmts.append({'range': _rng(r,1,r,7), 'format': _hdr('1A237E')})
    r += 1

    wt = ctx.wt

    # 総出品数を週別に取得（weekly_history.jsonから各週末時点の値を参照）
    weekly_items = []
    for i in range(4):
        w_end = ctx.weeks[i][2]  # 各週の終了日（日曜）
        w_key = w_end.strftime('%Y-%m-%d')
        if w_key in ctx.history:
            weekly_items.append(ctx.history[w_key].get('total_items', None))
        else:
            weekly_items.append(None)
    # W4（最新週）は今回の値で上書き
    weekly_items[3] = ctx.total_items
    # 履歴がない週は直近の既知値で埋める（右から左へ）
    for i in range(2, -1, -1):
        if weekly_items[i] is None:
            weekly_items[i] = weekly_items[i + 1] if i + 1 < 4 and weekly_items[i + 1] is not None else ctx.total_items

    # W3→W4変化
    items_delta = weekly_items[3] - weekly_items[2]
    items_delta_str = f'{items_delta:+,}件' if items_delta != 0 else '±0'

    kpi_rows = []
    if ctx.use_weekly:
        kpi_rows = [
            ('🔵 Impressions（表示回数）',
             [f'{wt[i]["imps"]:,.0f}' for i in range(4)], f'{ctx.total_imps:,.0f}',
             ctx.pct_change(wt[3]['imps'], wt[2]['imps']), 'E3F2FD', True),
            ('👁 Page Views（閲覧数）',
             [f'{wt[i]["pv"]:,.0f}' for i in range(4)], f'{ctx.total_pv:,.0f}',
             ctx.pct_change(wt[3]['pv'], wt[2]['pv']), 'E3F2FD', True),
            ('🛒 Sold（販売数）',
             [f'{wt[i]["sold"]:.0f}件' for i in range(4)], f'{ctx.total_sold:.0f}件',
             ctx.pct_change(wt[3]['sold'], wt[2]['sold']), 'E3F2FD', True),
            ('📈 CTR（クリック率）',
             [f'{(wt[i]["pv"]/wt[i]["imps"]*100 if wt[i]["imps"]>0 else 0):.3f}%' for i in range(4)],
             f'{ctx.overall_ctr:.3f}%', '', None, False),
            ('💰 CVR（コンバージョン率）',
             [f'{(wt[i]["sold"]/wt[i]["pv"]*100 if wt[i]["pv"]>0 else 0):.3f}%' for i in range(4)],
             f'{ctx.overall_cvr:.3f}%', '', 'E3F2FD', True),
            ('📦 総出品数（SKU）',
             [f'{weekly_items[i]:,}件' for i in range(4)], '', items_delta_str, None, False),
            ('📉 売上ゼロ比率',
             [f'{(ctx.total_items - len(ctx.week_sold_skus[i]))/ctx.total_items*100:.1f}%'
              if ctx.total_items > 0 else '—' for i in range(4)],
             '', f'{((ctx.total_items-len(ctx.week_sold_skus[3]))/ctx.total_items*100 - (ctx.total_items-len(ctx.week_sold_skus[2]))/ctx.total_items*100):+.1f}%'
              if ctx.total_items > 0 and len(ctx.week_sold_skus[2]) > 0 else '', 'E3F2FD', True),
        ]

    for item in kpi_rows:
        label, wvals, total_str, change_str = item[0], item[1], item[2], item[3]
        bg = item[4] if len(item) > 4 else None
        bold = item[5] if len(item) > 5 else False
        rows.append([label] + wvals + [total_str, change_str])
        if bg:
            fmts.append({'range': _rng(r,1,r,7), 'format': _body(bg, bold)})
        else:
            fmts.append({'range': _rng(r,1,r,7), 'format': _body(bold=bold)})
        r += 1

    # 空行
    rows.append([''] * 7)
    r += 1

    # セクション: 週別売上
    rows.append(['■ 週別売上（全サイト合計 → サイト別内訳・USD換算）', '', '', '', '', '', ''])
    fmts.append({'range': _rng(r,1,r,7), 'format': _note_fmt('E8EAF6')})
    r += 1

    rows.append(['指標'] + wl + ['合計', 'W3→W4変化'])
    fmts.append({'range': _rng(r,1,r,7), 'format': _hdr('1A237E')})
    r += 1

    # 全サイト注文数
    ws_data = ctx.week_stats
    rows.append(['【全サイト】注文数'] + [f'{ws_data[i]["orders"]}件' for i in range(4)] +
                [f'{ctx.total_orders}件', ctx.pct_change(ws_data[3]['orders'], ws_data[2]['orders'])])
    fmts.append({'range': _rng(r,1,r,7), 'format': _body('E3F2FD', True)})
    r += 1

    # 全サイト売上
    rows.append(['【全サイト】売上（USD）'] + [f'${ws_data[i]["gross"]:,.0f}' for i in range(4)] +
                [f'${ctx.total_gross:,.0f}', ctx.pct_change(ws_data[3]['gross'], ws_data[2]['gross'])])
    fmts.append({'range': _rng(r,1,r,7), 'format': _body('FFF3E0', True)})
    r += 1

    # サイト別
    site_label = {'US': '【US】', 'UK': '【UK】', 'EU (DE/IT)': '【EU】',
                  'Australia': '【AU】', 'Canada': '【CA】'}
    for sname in ctx.site_order:
        ss = ctx.site_stats.get(sname)
        if not ss or ss['orders'] == 0:
            continue
        sw = ctx.site_week.get(sname, [{'orders':0,'gross':0.0}]*4)
        pct = ss['gross_usd'] / ctx.total_gross * 100 if ctx.total_gross > 0 else 0
        sl = site_label.get(sname, sname)
        rows.append([f'{sl} 注文数'] + [f'{sw[i]["orders"]}件' for i in range(4)] +
                    [f'{ss["orders"]}件（{pct:.0f}%）', ctx.pct_change(sw[3]['orders'], sw[2]['orders'])])
        fmts.append({'range': _rng(r,1,r,7), 'format': _body('E3F2FD')})
        r += 1
        rows.append([f'{sl} 売上'] + [f'${sw[i]["gross"]:,.0f}' for i in range(4)] +
                    [f'${ss["gross_usd"]:,.0f}', ctx.pct_change(sw[3]['gross'], sw[2]['gross'])])
        fmts.append({'range': _rng(r,1,r,7), 'format': _body('FFF3E0')})
        r += 1

    # 空行
    rows.append([''] * 7)
    r += 1

    # セクション: 手数料
    rows.append(['■ 週別手数料・手取り推定（全サイト・USD）', '', '', '', '', '', ''])
    fmts.append({'range': _rng(r,1,r,7), 'format': _note_fmt('E8EAF6')})
    r += 1
    rows.append(['指標'] + wl + ['合計', 'W3→W4変化'])
    fmts.append({'range': _rng(r,1,r,7), 'format': _hdr('1A237E')})
    r += 1

    fee_rows = [
        ('FVF（最終価値手数料）', 'fvf', True),
        ('International fee', 'intl', True),
        ('PLG広告費', 'plg_fee', True),
        ('Offsite広告費', 'off_fee', True),
    ]
    for label, key, is_cost in fee_rows:
        rows.append([label] + [f'-${ws_data[i][key]:,.0f}' for i in range(4)] +
                    [f'-${sum(ws_data[i][key] for i in range(4)):,.0f}',
                     ctx.pct_change(ws_data[3][key], ws_data[2][key])])
        fmts.append({'range': _rng(r,1,r,7), 'format': _body('FFF3E0')})
        r += 1

    rows.append(['手取り推定'] + [f'${ws_data[i]["net"]:,.0f}' for i in range(4)] +
                [f'${ctx.net:,.0f}  ※PLP-${ctx.plp_fee:.0f}控除後',
                 ctx.pct_change(ws_data[3]['net'], ws_data[2]['net'])])
    fmts.append({'range': _rng(r,1,r,7), 'format': _body('E8F5E9', True)})
    r += 1

    # 空行
    rows.append([''] * 7)
    r += 1

    # セクション: 収支サマリー
    rows.append(['■ 収支サマリー（期間全体）', '', '', '', '', '', ''])
    fmts.append({'range': _rng(r,1,r,7), 'format': _note_fmt('E8EAF6')})
    r += 1
    rows.append(['項目', '金額（USD）', '備考', '', '', '', ''])
    fmts.append({'range': _rng(r,1,r,7), 'format': _hdr('1A237E')})
    r += 1

    finance = [
        ('売上合計（Gross）', f'${ctx.total_gross:,.2f}', f'USD注文 {ctx.total_orders}件', None, True),
        ('FVF（最終価値手数料）', f'-${ctx.total_fvf:,.2f}',
         f'実質率: {ctx.total_fvf/ctx.total_gross*100:.1f}%' if ctx.total_gross>0 else '', 'FFF3E0', False),
        ('International fee', f'-${ctx.total_intl:,.2f}', '', 'FFF3E0', False),
        ('PLG広告費', f'-${ctx.total_plg:,.2f}',
         f'ROAS: {ctx.total_gross/ctx.total_plg:.1f}x' if ctx.total_plg>0 else '', 'FFF3E0', False),
        ('Offsite広告費', f'-${ctx.total_off:,.2f}', 'CPC課金', 'FFF3E0', False),
        ('PLP広告費', f'-${ctx.plp_fee:,.2f}', '⚠ Seller Hub広告管理画面の実績値', 'FFF3E0', False),
        ('eBay控除後 手取り（推定）', f'${ctx.net:,.2f}',
         f'収益率: {ctx.net/ctx.total_gross*100:.1f}%' if ctx.total_gross>0 else '', 'E8F5E9', True),
    ]
    for label, amount, note, bg, bold in finance:
        rows.append([label, amount, note, '', '', '', ''])
        fmts.append({'range': _rng(r,1,r,7), 'format': _body(bg, bold)})
        r += 1

    # 書き込み
    ws.update(values=rows, range_name='A1')
    ws.batch_format(fmts)

    # マージ（タイトル行）
    _merge_cells(sh, ws, 'A1:G1')

    # 列幅
    _set_widths(sh, ws, [250, 120, 120, 120, 120, 160, 100])
    ws.freeze(rows=1)


def _write_core_top15(sh, ws, ctx):
    """🔥 コア売れ筋TOP15（W3/W4比較・デルタ列付き）"""
    w3l = _swl(ctx, 2)
    w4l = _swl(ctx, 3)
    w4p = ctx.weeks[3][0].replace('\n', ' ')
    title = f'🔥 コア売れ筋 TOP15 ― 前週 {w4p} の販売数ランキング'

    ncols = 18
    rows = [[title] + [''] * (ncols - 1)]
    rows.append([])  # 空行（説明不要）

    # 2段ヘッダー（18列）
    row3 = ['順位', '商品タイトル', 'Item ID', 'SKU',
            '販売数', '', 'CVR', '', 'PV', '', 'インプレッション', '',
            '価格(USD)', '在庫数', 'ウォッチ', '生涯販売', 'PLP', '前週カテゴリ']
    row4 = ['', '', '', '',
            w4l, 'Δ', w4l, 'Δ', w4l, 'Δ', w4l, 'Δ',
            '', '', '', '', '', '']
    rows.append(row3)
    rows.append(row4)

    hdr_fmts, hdr_merges = _write_two_row_header(
        ws, sh, row3, row4,
        merge_groups=[0, 1, 2, 3, 12, 13, 14, 15, 16, 17],
        h_merge_groups=[(4, 5), (6, 7), (8, 9), (10, 11)],
        ncols=ncols, hdr_color='1B5E20')

    fmts = [
        {'range': _rng(1,1,1,ncols), 'format': _title_fmt('1B5E20')},
    ] + hdr_fmts

    # Item IDリンク用ペア収集
    id_row_pairs = []

    # データ行
    for rank, item in enumerate(ctx.top15, 1):
        sku, watch, lsold, price, _ = ctx.get_item_api_data(item['id'])
        price_str = f'${price:.2f}' if isinstance(price, float) and price > 0 else '—'
        w4s = int(item.get('weekly_sold', [0]*4)[3])
        w3s = int(item.get('weekly_sold', [0]*4)[2])
        w4_cvr = _calc_weekly_cvr(item, 3)
        w3_cvr = _calc_weekly_cvr(item, 2)
        w4_pv = int(item.get('weekly_pv', [0]*4)[3])
        w3_pv = int(item.get('weekly_pv', [0]*4)[2])
        w4_imp = int(item.get('weekly_imps', [0]*4)[3])
        w3_imp = int(item.get('weekly_imps', [0]*4)[2])

        # デルタ計算
        d_sold = w4s - w3s
        d_sold_str = f'+{d_sold}' if d_sold > 0 else str(d_sold) if d_sold < 0 else '0'
        d_cvr = w4_cvr - w3_cvr
        d_cvr_str = f'{d_cvr:+.1f}%'
        d_pv = w4_pv - w3_pv
        d_pv_str = f'+{d_pv}' if d_pv > 0 else str(d_pv) if d_pv < 0 else '0'
        d_imp = w4_imp - w3_imp
        d_imp_str = f'+{d_imp:,}' if d_imp > 0 else f'{d_imp:,}' if d_imp < 0 else '0'

        prev_cat = ctx.get_prev_category(item['id'])
        plp_flag = '✅' if item.get('plp_s', 0) > 0 else ''
        bg = 'C8E6C9' if rank <= 3 else 'E8F5E9'

        row_num = rank + 4  # タイトル(1) + 空行(2) + ヘッダーrow3(3) + ヘッダーrow4(4) + データ開始
        id_row_pairs.append((row_num, item['id']))

        rows.append([rank, item['title'], item['id'], sku,
                     w4s, d_sold_str, f'{w4_cvr:.1f}%', d_cvr_str,
                     w4_pv, d_pv_str, f'{w4_imp:,}', d_imp_str,
                     price_str, int(item['qty']),
                     watch if watch != '?' else '—', lsold if lsold != '?' else '—',
                     plp_flag, prev_cat])
        fmts.append({'range': _rng(row_num, 1, row_num, ncols), 'format': _body(bg, rank<=3)})

    ws.update(values=rows, range_name='A1')
    ws.batch_format(fmts)
    _add_links(ws, 2, id_row_pairs)  # C列（0-indexed: 2）にハイパーリンク
    all_merges = [f'A1:{_cl(ncols-1)}1'] + hdr_merges
    _batch_merge_and_freeze(sh, ws, all_merges, 4)
    _set_widths(sh, ws, [50, 330, 110, 95, 65, 65, 65, 65, 65, 65, 90, 80, 75, 60, 75, 75, 55, 100])


def _write_core_drop(sh, ws, ctx):
    """🚨 コア落ちアラート"""
    title = f'🚨 コア落ちアラート ― W3→W4でTOP15から外れた商品（{len(ctx.コア落ち)}件）'
    ncols = 12

    rows = [[title] + [''] * (ncols - 1)]

    if not ctx.コア落ち:
        rows.append(['✅ 今週はコア落ちなし。全員が先週と同様にTOP15をキープしています。'] + [''] * (ncols - 1))
    else:
        rows.append(['→ W3(前週)のTOP15からW4(直近週)で外れた商品。必ず今週中に原因を調査。'] + [''] * (ncols - 1))

    # 2段ヘッダー（12列）
    row3 = ['商品タイトル', 'Item ID', 'SKU', '販売数', '', '', 'CVR', '価格(USD)', '在庫数', '前週カテゴリ', '今週カテゴリ', '原因（自動推測）']
    row4 = ['', '', '', _swl(ctx,2), _swl(ctx,3), 'Δ', _swl(ctx,3), '', '', '', '', '']
    rows.append(row3)
    rows.append(row4)

    hdr_fmts, hdr_merges = _write_two_row_header(
        ws, sh, row3, row4,
        merge_groups=[0, 1, 2, 6, 7, 8, 9, 10, 11],
        h_merge_groups=[(3, 5)],
        ncols=ncols, hdr_color='AD1457')

    fmts = [
        {'range': _rng(1,1,1,ncols), 'format': _title_fmt('AD1457')},
        {'range': _rng(2,1,2,ncols), 'format': _note_fmt('FCE4EC')},
    ] + hdr_fmts

    # Item IDリンク用ペア収集
    id_row_pairs = []

    for i, ko in enumerate(ctx.コア落ち):
        sku, _, _, price, _ = ctx.get_item_api_data(ko['id'])
        if not sku:
            sku = _item_sku(ctx, ko['id'])
        price_str = f'${price:.2f}' if isinstance(price, float) and price > 0 else '—'
        delta = ko['delta_sold']
        delta_str = f'+{delta}' if delta > 0 else str(delta) if delta < 0 else '0'
        prev_cat = ctx.get_prev_category(ko['id'])
        row_num = i + 5
        id_row_pairs.append((row_num, ko['id']))
        rows.append([ko['title'], ko['id'], sku,
                     int(ko['prev_sold']), int(ko['curr_sold']), delta_str,
                     f'{ko["curr_cvr"]:.1f}%', price_str, ko['qty'],
                     prev_cat, ko['curr_cat'], ko['reason']])
        fmts.append({'range': _rng(row_num, 1, row_num, ncols), 'format': _body('FCE4EC')})

    ws.update(values=rows, range_name='A1')
    ws.batch_format(fmts)
    _add_links(ws, 1, id_row_pairs)  # B列（0-indexed: 1）にハイパーリンク
    all_merges = [f'A1:{_cl(ncols-1)}1', f'A2:{_cl(ncols-1)}2'] + hdr_merges
    _batch_merge_and_freeze(sh, ws, all_merges, 4)
    _set_widths(sh, ws, [330, 110, 95, 65, 65, 80, 65, 75, 60, 100, 100, 250])


def _write_semi_core(sh, ws, ctx):
    """⭐ 準売れ筋（週別推移列 + 備考追加）"""
    ncols = 18  # A〜R
    title = (f'⭐ 準売れ筋（{ctx.準売れ筋_cnt}件SKU）― ポテンシャルスコア順（CVR×PV）'
             f'― S=最重点 / A=重点 / B=普通 / C=後回し')

    rows = [[title] + [''] * (ncols - 1)]
    rows.append(['【優先度】S🔥→今週必ず対処 / A⭐→今週中 / B🌱→来週以降 / C→後回し  '
                 '【ポテンシャル】CVR×PV'] + [''] * (ncols - 1))

    # 2段ヘッダー（18列）
    row3 = ['優先度', '商品タイトル', 'Item ID', 'SKU', 'ポテンシャル(CVR×PV)',
            '販売数(全期間)', 'CVR', 'PV', 'インプ',
            '販売数推移', '', '',
            '在庫数', '掲載日数', 'ウォッチ', '価格USD', '前週カテゴリ', '備考']
    row4 = ['', '', '', '', '', '', '', '', '',
            _swl(ctx,2), _swl(ctx,3), 'Δ',
            '', '', '', '', '', '']
    rows.append(row3)
    rows.append(row4)

    hdr_fmts, hdr_merges = _write_two_row_header(
        ws, sh, row3, row4,
        merge_groups=[0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 13, 14, 15, 16, 17],
        h_merge_groups=[(9, 11)],
        ncols=ncols, hdr_color='0D47A1')

    fmts = [
        {'range': _rng(1,1,1,ncols), 'format': _title_fmt('0D47A1')},
        {'range': _rng(2,1,2,ncols), 'format': _note_fmt('E3F2FD')},
    ] + hdr_fmts

    PRIO_BG = {'S 🔥': 'C8E6C9', 'A ⭐': 'E3F2FD', 'B 🌱': 'FFFDE7', 'C —': 'F5F5F5'}

    # Item IDリンク用ペア収集
    id_row_pairs = []

    for i, item in enumerate(ctx.準売れ筋):
        sku, watch, _, price, _ = ctx.get_item_api_data(item['id'])
        prev_cat = ctx.get_prev_category(item['id'])
        bg = PRIO_BG.get(item['priority'], 'E3F2FD')
        price_str = f'${price:.2f}' if isinstance(price, float) and price > 0 else '—'
        w3s = int(item.get('weekly_sold', [0]*4)[2])
        w4s = int(item.get('weekly_sold', [0]*4)[3])
        delta = w4s - w3s
        delta_str = f'+{delta}' if delta > 0 else str(delta) if delta < 0 else '0'
        note = ctx.notes.get(item['id'], '')
        row_num = i + 5
        id_row_pairs.append((row_num, item['id']))

        rows.append([item['priority'], item['title'], item['id'], sku,
                     item['pot_score'], int(item['sold']), f'{item["cvr"]:.1f}%',
                     int(item['pv']), f'{item["imps"]:,}',
                     w3s, w4s, delta_str,
                     int(item['qty']), f'{item["days"]}日',
                     watch if watch != '?' else '—', price_str,
                     prev_cat, note])
        fmts.append({'range': _rng(row_num, 1, row_num, ncols), 'format': _body(bg, item['priority']=='S 🔥')})

    ws.update(values=rows, range_name='A1')
    ws.batch_format(fmts)
    _add_links(ws, 2, id_row_pairs)  # C列（0-indexed: 2）にハイパーリンク
    all_merges = [f'A1:{_cl(ncols-1)}1', f'A2:{_cl(ncols-1)}2'] + hdr_merges
    _batch_merge_and_freeze(sh, ws, all_merges, 4)
    _set_widths(sh, ws, [55, 350, 110, 95, 85, 65, 65, 65, 90,
                         55, 55, 55, 60, 65, 75, 80, 100, 150])


def _write_nurture(sh, ws, ctx):
    """🌱 育成候補（週別推移 + 備考追加）"""
    ncols = 17
    title = (f'🌱 育成候補（{ctx.育成_cnt}件SKU）― PV{ctx.IKUSEI_PV}以上・売上ゼロ・要調査除外 '
             f'― クリックされているが購入に繋がっていない')

    rows = [[title] + [''] * (ncols - 1)]
    rows.append(['確認①価格（競合比較）②サイズ在庫 ③タイトル写真 ④送料設定'] + [''] * (ncols - 1))

    # 2段ヘッダー（17列）
    row3 = ['商品タイトル', 'Item ID', 'SKU', 'PV', 'インプ', 'CTR',
            'PV推移', '', '',
            '価格(USD)', '在庫数', '掲載日数', '広告状態', 'Organic比',
            'ウォッチ', '前週カテゴリ', '備考']
    row4 = ['', '', '', '', '', '',
            _swl(ctx,2), _swl(ctx,3), 'Δ',
            '', '', '', '', '', '', '', '']
    rows.append(row3)
    rows.append(row4)

    hdr_fmts, hdr_merges = _write_two_row_header(
        ws, sh, row3, row4,
        merge_groups=[0, 1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 16],
        h_merge_groups=[(6, 8)],
        ncols=ncols, hdr_color='E65100')

    fmts = [
        {'range': _rng(1,1,1,ncols), 'format': _title_fmt('E65100')},
        {'range': _rng(2,1,2,ncols), 'format': _note_fmt('FFF9C4')},
    ] + hdr_fmts

    # Item IDリンク用ペア収集
    id_row_pairs = []

    for i, item in enumerate(ctx.育成):
        sku, watch, _, price, _ = ctx.get_item_api_data(item['id'])
        price_str = f'${price:.2f}' if isinstance(price, float) and price > 0 else '—'
        org = f'{item["org_imps"]/item["imps"]*100:.0f}%' if item['imps'] > 0 and item['org_imps'] > 0 else '—'
        prev_cat = ctx.get_prev_category(item['id'])
        w3pv = int(item.get('weekly_pv', [0]*4)[2])
        w4pv = int(item.get('weekly_pv', [0]*4)[3])
        dpv = w4pv - w3pv
        dpv_str = f'+{dpv}' if dpv > 0 else str(dpv) if dpv < 0 else '0'
        note = ctx.notes.get(item['id'], '')
        row_num = i + 5
        id_row_pairs.append((row_num, item['id']))

        rows.append([item['title'], item['id'], sku,
                     int(item['pv']), f'{item["imps"]:,}', f'{item["ctr"]:.2f}%',
                     w3pv, w4pv, dpv_str,
                     price_str, int(item['qty']), f'{item["days"]}日', item['promo'], org,
                     watch if watch != '?' else '—', prev_cat, note])
        fmts.append({'range': _rng(row_num, 1, row_num, ncols), 'format': _body('FFF9C4')})

    ws.update(values=rows, range_name='A1')
    ws.batch_format(fmts)
    _add_links(ws, 1, id_row_pairs)  # B列（0-indexed: 1）にハイパーリンク
    all_merges = [f'A1:{_cl(ncols-1)}1', f'A2:{_cl(ncols-1)}2'] + hdr_merges
    _batch_merge_and_freeze(sh, ws, all_merges, 4)
    _set_widths(sh, ws, [330, 110, 95, 65, 90, 65,
                         55, 55, 55, 75, 60, 65, 90, 70, 75, 100, 150])


def _write_investigate(sh, ws, ctx):
    """⚠️ 要調査（週別推移 + 備考）― 終了済み商品を除外"""
    ncols = 17
    # 終了済み商品を除外
    filtered = [item for item in ctx.要調査 if not _is_ended_item(ctx, item)]
    filtered_cnt = len(filtered)

    title = (f'⚠️ 要調査 TOP50（全{filtered_cnt}件SKU中）'
             f'― インプ500以上・売上ゼロ・掲載90日以上')

    rows = [[title] + [''] * (ncols - 1)]
    rows.append([f'確認①在庫ツールURL ②仕入先在庫 ③価格・競合  '
                 f'| 前週も要調査の商品は優先して調査'] + [''] * (ncols - 1))

    # 2段ヘッダー（17列）
    row3 = ['商品タイトル', 'Item ID', 'SKU', 'インプ', 'PV',
            'インプ推移', '',
            '在庫数', '掲載日数', '広告状態', 'Organic比',
            'ウォッチ', '生涯販売', '価格USD',
            '前週カテゴリ', '調査済✅', '備考']
    row4 = ['', '', '', '', '',
            _swl(ctx,2), _swl(ctx,3),
            '', '', '', '', '', '', '', '', '', '']
    rows.append(row3)
    rows.append(row4)

    hdr_fmts, hdr_merges = _write_two_row_header(
        ws, sh, row3, row4,
        merge_groups=[0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
        h_merge_groups=[(5, 6)],
        ncols=ncols, hdr_color='BF360C')

    fmts = [
        {'range': _rng(1,1,1,ncols), 'format': _title_fmt('BF360C')},
        {'range': _rng(2,1,2,ncols), 'format': _note_fmt('FFF3E0')},
    ] + hdr_fmts

    # Item IDリンク用ペア収集
    id_row_pairs = []

    for i, item in enumerate(filtered):
        sku, watch, lsold, price, _ = ctx.get_item_api_data(item['id'])
        org = f'{item["org_imps"]/item["imps"]*100:.0f}%' if item['imps'] > 0 and item['org_imps'] > 0 else '—'
        prev_cat = ctx.get_prev_category(item['id'])
        price_str = f'${price:.2f}' if isinstance(price, float) and price > 0 else '—'
        bg = 'FFCC80' if prev_cat == '⚠️ 要調査' else 'FFF3E0'
        w3i = int(item.get('weekly_imps', [0]*4)[2])
        w4i = int(item.get('weekly_imps', [0]*4)[3])
        note = ctx.notes.get(item['id'], '')
        row_num = i + 5
        id_row_pairs.append((row_num, item['id']))

        rows.append([item['title'], item['id'], sku,
                     f'{item["imps"]:,}', int(item['pv']),
                     f'{w3i:,}', f'{w4i:,}',
                     int(item['qty']), f'{item["days"]}日', item['promo'], org,
                     watch if watch != '?' else '—', lsold if lsold != '?' else '—', price_str,
                     prev_cat, '', note])
        fmts.append({'range': _rng(row_num, 1, row_num, ncols), 'format': _body(bg)})

    ws.update(values=rows, range_name='A1')
    ws.batch_format(fmts)
    _add_links(ws, 1, id_row_pairs)  # B列（0-indexed: 1）にハイパーリンク
    all_merges = [f'A1:{_cl(ncols-1)}1', f'A2:{_cl(ncols-1)}2'] + hdr_merges
    _batch_merge_and_freeze(sh, ws, all_merges, 4)
    _set_widths(sh, ws, [350, 110, 95, 90, 65, 80, 80,
                         60, 65, 90, 70, 75, 75, 80, 100, 65, 150])

    # ドロップダウン（調査済✅列: P列=index15）
    if len(filtered) > 0:
        _add_dropdown(sh, ws, 15, 5, 4 + len(filtered), ['✅', ''])


def _write_delete(sh, ws, ctx):
    """🗑 削除候補（備考欄追加）― 終了済み商品を除外"""
    ncols = 14  # 「⚠️ 重複」列を追加（佐藤大将 2026-04-10 要望反映）

    # 終了済み商品を除外
    filtered_l1 = [item for item in ctx.削除L1 if not _is_ended_item(ctx, item)]
    filtered_l2 = [item for item in ctx.削除L2 if not _is_ended_item(ctx, item)]
    l1_cnt = len(filtered_l1)
    l2_cnt = len(filtered_l2)

    # 重複出品の検出：削除候補（L1+L2）内で同一SKUが複数Item IDに紐づくケース
    sku_to_count = {}
    for item in filtered_l1 + filtered_l2:
        s, _, _, _, _ = ctx.get_item_api_data(item['id'])
        if s and str(s).strip():
            sku_to_count[s] = sku_to_count.get(s, 0) + 1

    def _dup_warning(s):
        n = sku_to_count.get(s, 0) if s else 0
        return f'⚠️ 重複出品の可能性 ({n}件)' if n >= 2 else ''

    title = f'🗑 削除候補 — L1即削除: {l1_cnt}件SKU ／ L2要確認: {l2_cnt}件SKU'

    rows = [[title] + [''] * (ncols - 1)]
    rows.append(['⚠️ 削除前に必ず確認：①ウォッチ数 ②生涯販売数 → 両方ゼロに近い場合のみ削除推奨'] + [''] * (ncols - 1))

    # L1ヘッダー
    hdr_l1 = [f'【L1：即削除】インプ・PV・売上すべてゼロ（{l1_cnt}件SKU）',
              'Item ID', 'SKU', '価格(USD)', '在庫数', '掲載日数', '広告状態',
              'ウォッチ(API)', '生涯販売(API)', '前週カテゴリ', '削除判定',
              '⚠️ 重複', '削除済✅', '備考']
    rows.append(hdr_l1)

    fmts = [
        {'range': _rng(1,1,1,ncols), 'format': _title_fmt('B71C1C')},
        {'range': _rng(2,1,2,ncols), 'format': _note_fmt('FFEBEE')},
        {'range': _rng(3,1,3,ncols), 'format': _hdr('B71C1C')},
    ]

    # Item IDリンク用ペア収集
    id_row_pairs = []

    r = 4
    for item in filtered_l1:
        prev_cat = ctx.get_prev_category(item['id'])
        sku, w, ls, price, judge = ctx.get_item_api_data(item['id'])
        price_str = f'${price:.2f}' if isinstance(price, float) and price > 0 else '—'
        if judge == '🚫 削除NG': bg = 'FFCC80'
        elif judge == '⚠️ 要確認': bg = 'FFF9C4'
        else: bg = 'FFCDD2'
        note = ctx.notes.get(item['id'], '')
        id_row_pairs.append((r, item['id']))

        rows.append([item['title'], item['id'], sku,
                     price_str, int(item['qty']), f'{item["days"]}日', item['promo'],
                     w, ls, prev_cat, judge,
                     _dup_warning(sku), '', note])
        fmts.append({'range': _rng(r, 1, r, ncols), 'format': _body(bg)})
        r += 1

    # L2セクション区切り
    rows.append([''] * ncols)
    r += 1

    hdr_l2 = [f'【L2：要確認削除】掲載180日以上・インプ50未満・売上ゼロ（{l2_cnt}件SKU）',
              'Item ID', 'SKU', '価格(USD)', 'インプ', 'PV',
              '在庫数', '掲載日数', 'ウォッチ(API)',
              '前週カテゴリ', '削除判定',
              '⚠️ 重複', '削除済✅', '備考']
    rows.append(hdr_l2)
    fmts.append({'range': _rng(r, 1, r, ncols), 'format': _hdr('7B1FA2')})
    r += 1

    for item in filtered_l2:
        prev_cat = ctx.get_prev_category(item['id'])
        sku, w, _, price, judge = ctx.get_item_api_data(item['id'])
        price_str = f'${price:.2f}' if isinstance(price, float) and price > 0 else '—'
        if judge == '🚫 削除NG': bg = 'FFCC80'
        elif judge == '⚠️ 要確認': bg = 'FFF9C4'
        else: bg = 'F3E5F5'
        note = ctx.notes.get(item['id'], '')
        id_row_pairs.append((r, item['id']))

        rows.append([item['title'], item['id'], sku,
                     price_str, f'{item["imps"]:,}', int(item['pv']),
                     int(item['qty']), f'{item["days"]}日', w,
                     prev_cat, judge,
                     _dup_warning(sku), '', note])
        fmts.append({'range': _rng(r, 1, r, ncols), 'format': _body(bg)})
        r += 1

    ws.update(values=rows, range_name='A1')
    ws.batch_format(fmts)
    _add_links(ws, 1, id_row_pairs)  # B列（0-indexed: 1）にハイパーリンク
    _merge_cells(sh, ws, f'A1:{_cl(ncols-1)}1')
    _merge_cells(sh, ws, f'A2:{_cl(ncols-1)}2')
    _set_widths(sh, ws, [330, 110, 95, 75, 65, 65, 90, 75, 75, 100, 90, 140, 65, 150])
    ws.freeze(rows=3)

    # ドロップダウン（削除済✅列: M列=index12 / 重複列追加で1つシフト）
    if r > 4:
        _add_dropdown(sh, ws, 12, 4, r, ['✅', ''])


def _write_core_monthly(sh, ws, ctx):
    """🔥 コア売れ筋（月間）― 4週間合計のTOP15"""
    ncols = 12
    title = f'🔥 コア売れ筋（月間）― {ctx.period} 販売数合計ランキング'

    rows = [[title] + [''] * (ncols - 1)]
    rows.append(['月間版：4週合計の販売数でランキング。週次TOP15との比較で安定した売れ筋を把握する'] + [''] * (ncols - 1))

    hdr = ['順位', '商品タイトル', 'Item ID', 'SKU',
           '販売数(合計)', 'CVR', 'PV', 'インプ',
           '在庫数', 'ウォッチ(API)', '生涯販売(API)', '現在価格(API)']
    rows.append(hdr)

    fmts = [
        {'range': _rng(1,1,1,ncols), 'format': _title_fmt('1B5E20')},
        {'range': _rng(2,1,2,ncols), 'format': _note_fmt('E8F5E9')},
        {'range': _rng(3,1,3,ncols), 'format': _hdr('1B5E20')},
    ]

    # 月間ランキング（4週合計sold）
    monthly_ranked = sorted(ctx.items, key=lambda x: -x['sold'])
    monthly_top = [i for i in monthly_ranked[:15] if i['sold'] > 0]

    # Item IDリンク用ペア収集
    id_row_pairs = []

    for rank, item in enumerate(monthly_top, 1):
        sku, watch, lsold, price, _ = ctx.get_item_api_data(item['id'])
        price_str = f'${price:.2f}' if isinstance(price, float) and price > 0 else '—'
        bg = 'C8E6C9' if rank <= 3 else 'E8F5E9'
        row_num = rank + 3
        id_row_pairs.append((row_num, item['id']))

        rows.append([rank, item['title'], item['id'], sku,
                     int(item['sold']), f'{item["cvr"]:.1f}%',
                     int(item['pv']), f'{item["imps"]:,}',
                     int(item['qty']),
                     watch if watch != '?' else '—', lsold if lsold != '?' else '—',
                     price_str])
        fmts.append({'range': _rng(row_num, 1, row_num, ncols), 'format': _body(bg, rank<=3)})

    ws.update(values=rows, range_name='A1')
    ws.batch_format(fmts)
    _add_links(ws, 2, id_row_pairs)  # C列（0-indexed: 2）にハイパーリンク
    _merge_cells(sh, ws, f'A1:{_cl(ncols-1)}1')
    _merge_cells(sh, ws, f'A2:{_cl(ncols-1)}2')
    _set_widths(sh, ws, [50, 350, 110, 95, 75, 65, 65, 90, 60, 75, 75, 80])
    ws.freeze(rows=3)


def _write_delete_monthly(sh, ws, ctx):
    """🗑 削除候補（月間）― 4週間ずっと売上ゼロの長期死蔵"""
    ncols = 12  # 「⚠️ 重複」列を追加
    title = f'🗑 削除候補（月間）― 4週間売上ゼロ・掲載90日以上'

    rows = [[title] + [''] * (ncols - 1)]
    rows.append(['月間版：週次と異なり4週間の合計で判定。確実に死蔵している商品を特定する'] + [''] * (ncols - 1))

    hdr = ['商品タイトル', 'Item ID', 'SKU', '価格(USD)', 'インプ(全期間)', 'PV(全期間)',
           '掲載日数', 'ウォッチ(API)', '生涯販売(API)', '削除判定', '⚠️ 重複', '備考']
    rows.append(hdr)

    fmts = [
        {'range': _rng(1,1,1,ncols), 'format': _title_fmt('B71C1C')},
        {'range': _rng(2,1,2,ncols), 'format': _note_fmt('FFEBEE')},
        {'range': _rng(3,1,3,ncols), 'format': _hdr('B71C1C')},
    ]

    # 全期間sold=0 & 掲載90日以上 & imps順（少ないものから=より死蔵）
    monthly_dead = sorted(
        [i for i in ctx.items if i['sold'] == 0 and i['days'] >= 90],
        key=lambda x: x['imps']
    )[:50]  # TOP50

    # 重複出品の検出：月間死蔵候補内で同一SKUが複数Item IDに紐づくケース
    sku_to_count = {}
    for it in monthly_dead:
        s, _, _, _, _ = ctx.get_item_api_data(it['id'])
        if s and str(s).strip():
            sku_to_count[s] = sku_to_count.get(s, 0) + 1

    def _dup_warning(s):
        n = sku_to_count.get(s, 0) if s else 0
        return f'⚠️ 重複出品の可能性 ({n}件)' if n >= 2 else ''

    # Item IDリンク用ペア収集
    id_row_pairs = []

    for i, item in enumerate(monthly_dead):
        sku, w, ls, price, judge = ctx.get_item_api_data(item['id'])
        price_str = f'${price:.2f}' if isinstance(price, float) and price > 0 else '—'
        note = ctx.notes.get(item['id'], '')
        if judge == '🚫 削除NG': bg = 'FFCC80'
        elif judge == '⚠️ 要確認': bg = 'FFF9C4'
        else: bg = 'FFCDD2'
        row_num = i + 4
        id_row_pairs.append((row_num, item['id']))

        rows.append([item['title'], item['id'], sku,
                     price_str, f'{item["imps"]:,}', int(item['pv']),
                     f'{item["days"]}日', w, ls, judge,
                     _dup_warning(sku), note])
        fmts.append({'range': _rng(row_num, 1, row_num, ncols), 'format': _body(bg)})

    ws.update(values=rows, range_name='A1')
    ws.batch_format(fmts)
    _add_links(ws, 1, id_row_pairs)  # B列（0-indexed: 1）にハイパーリンク
    _merge_cells(sh, ws, f'A1:{_cl(ncols-1)}1')
    _merge_cells(sh, ws, f'A2:{_cl(ncols-1)}2')
    _set_widths(sh, ws, [330, 110, 95, 75, 90, 65, 65, 75, 75, 90, 140, 150])
    ws.freeze(rows=3)


def _write_improvement(sh, ws, ctx):
    """📈 改善追跡 ― 前週データとの詳細メトリクス比較"""
    ncols = 19

    # 改善追跡データを構築
    # 前週「要調査」「削除候補」だった商品 → 今週sold>0 = 改善成功
    improved = []
    still_working = []

    if ctx.last_data:
        prev_problem_ids = set(
            ctx.last_data.get('要調査_ids', []) +
            ctx.last_data.get('削除L1_ids', []) +
            ctx.last_data.get('削除L2_ids', [])
        )
        prev_per_item = ctx.last_data.get('per_item', {})

        for iid in prev_problem_ids:
            item = ctx.items_by_id.get(iid)
            if not item:
                continue
            prev_cat = ctx.get_prev_category(iid)
            curr_cat = ctx.get_current_category(iid)
            note = ctx.notes.get(iid, '')

            # 前週データ取得
            prev_data = prev_per_item.get(iid, {})
            prev_sold = prev_data.get('sold', 0)
            prev_pv = prev_data.get('pv', 0)
            prev_imps = prev_data.get('imps', 0)

            # 今週データ
            curr_sold = int(item['sold'])
            curr_pv = int(item['pv'])
            curr_imps = int(item.get('imps', 0))

            # デルタ計算
            d_pv = curr_pv - prev_pv
            d_imps = curr_imps - prev_imps

            # API情報（現在）
            sku, _, _, price, _ = ctx.get_item_api_data(iid)
            price_str = f'${price:.2f}' if isinstance(price, float) and price > 0 else '—'
            qty = int(item.get('qty', 0))

            # 前週の価格・在庫（weekly_history.jsonから取得）
            prev_price = prev_data.get('price', 0)
            prev_qty = prev_data.get('qty', 0)
            prev_price_str = f'${prev_price:.2f}' if isinstance(prev_price, (int, float)) and prev_price > 0 else '—'

            entry = {
                'title': item['title'], 'id': iid, 'sku': sku,
                'prev_cat': prev_cat, 'curr_cat': curr_cat,
                'prev_sold': prev_sold, 'curr_sold': curr_sold,
                'prev_pv': prev_pv, 'curr_pv': curr_pv, 'd_pv': d_pv,
                'prev_imps': prev_imps, 'curr_imps': curr_imps, 'd_imps': d_imps,
                'prev_price': prev_price_str, 'price': price_str,
                'prev_qty': prev_qty, 'qty': qty,
                'note': note,
            }

            if curr_sold > 0:
                improved.append(entry)
            elif note:  # ノートがある=改善を試みている
                still_working.append(entry)

    improved.sort(key=lambda x: -x['curr_sold'])
    still_working.sort(key=lambda x: -x['curr_pv'])

    title = f'📈 改善追跡 ― 前週「要調査・削除候補」から改善が見られた商品'
    rows = [[title] + [''] * (ncols - 1)]
    rows.append([f'改善成功: {len(improved)}件 | 改善中（備考あり・未販売）: {len(still_working)}件  '
                 f'スタッフの行動が結果に繋がった商品をここで確認'] + [''] * (ncols - 1))

    # 2段ヘッダー（19列）
    row3 = ['状態', '商品タイトル', 'Item ID', 'SKU',
            'カテゴリ', '', '販売数', '', 'PV', '', '', 'インプレッション', '', '', '価格', '', '在庫', '', '備考']
    row4 = ['', '', '', '',
            '前週', '今週', '前週', '今週', '前週', '今週', 'Δ', '前週', '今週', 'Δ', '前週', '現在', '前週', '現在', '']
    rows.append(row3)
    rows.append(row4)

    hdr_fmts, hdr_merges = _write_two_row_header(
        ws, sh, row3, row4,
        merge_groups=[0, 1, 2, 3, 18],
        h_merge_groups=[(4, 5), (6, 7), (8, 10), (11, 13), (14, 15), (16, 17)],
        ncols=ncols, hdr_color='00695C')

    fmts = [
        {'range': _rng(1,1,1,ncols), 'format': _title_fmt('00695C')},
        {'range': _rng(2,1,2,ncols), 'format': _note_fmt('E0F2F1')},
    ] + hdr_fmts

    # Item IDリンク用ペア収集
    id_row_pairs = []

    r = 5
    # 改善成功
    for entry in improved:
        d_pv_str = f'+{entry["d_pv"]}' if entry['d_pv'] > 0 else str(entry['d_pv']) if entry['d_pv'] < 0 else '0'
        d_imps_str = f'+{entry["d_imps"]:,}' if entry['d_imps'] > 0 else f'{entry["d_imps"]:,}' if entry['d_imps'] < 0 else '0'
        id_row_pairs.append((r, entry['id']))
        rows.append(['✅ 改善成功', entry['title'], entry['id'], entry['sku'],
                     entry['prev_cat'], entry['curr_cat'],
                     entry['prev_sold'], entry['curr_sold'],
                     entry['prev_pv'], entry['curr_pv'], d_pv_str,
                     f'{entry["prev_imps"]:,}', f'{entry["curr_imps"]:,}', d_imps_str,
                     entry['prev_price'], entry['price'], entry['prev_qty'], entry['qty'], entry['note']])
        fmts.append({'range': _rng(r, 1, r, ncols), 'format': _body('C8E6C9', True)})
        r += 1

    # 改善中
    for entry in still_working:
        d_pv_str = f'+{entry["d_pv"]}' if entry['d_pv'] > 0 else str(entry['d_pv']) if entry['d_pv'] < 0 else '0'
        d_imps_str = f'+{entry["d_imps"]:,}' if entry['d_imps'] > 0 else f'{entry["d_imps"]:,}' if entry['d_imps'] < 0 else '0'
        id_row_pairs.append((r, entry['id']))
        rows.append(['🔄 改善中', entry['title'], entry['id'], entry['sku'],
                     entry['prev_cat'], entry['curr_cat'],
                     entry['prev_sold'], entry['curr_sold'],
                     entry['prev_pv'], entry['curr_pv'], d_pv_str,
                     f'{entry["prev_imps"]:,}', f'{entry["curr_imps"]:,}', d_imps_str,
                     entry['prev_price'], entry['price'], entry['prev_qty'], entry['qty'], entry['note']])
        fmts.append({'range': _rng(r, 1, r, ncols), 'format': _body('FFF9C4')})
        r += 1

    if not improved and not still_working:
        rows.append(['前週データなし、または改善対象の商品がありません'] + [''] * (ncols - 1))
        fmts.append({'range': _rng(r, 1, r, ncols), 'format': _body('F5F5F5')})

    ws.update(values=rows, range_name='A1')
    ws.batch_format(fmts)
    _add_links(ws, 2, id_row_pairs)  # C列（0-indexed: 2）にハイパーリンク
    all_merges = [f'A1:{_cl(ncols-1)}1', f'A2:{_cl(ncols-1)}2'] + hdr_merges
    _batch_merge_and_freeze(sh, ws, all_merges, 4)
    _set_widths(sh, ws, [85, 280, 110, 95, 100, 100, 65, 65, 65, 65, 55, 80, 80, 70, 75, 75, 65, 65, 180])


def _write_history(sh, ws, ctx):
    """📋 週次履歴"""
    ncols = 10
    title = '📋 週次履歴 ― レポート実行ごとに自動蓄積（前週比較の基礎データ）'

    rows = [[title] + [''] * (ncols - 1)]
    rows.append(['→ このシートは毎週自動更新（weekly_history.json）。削除しないこと。'] + [''] * (ncols - 1))

    hdr = ['レポート日', '期間', '注文数', '売上Gross', '手取り推定',
           'CVR', 'CTR', '出品数', 'コア落ち', '要調査件数']
    rows.append(hdr)

    fmts = [
        {'range': _rng(1,1,1,ncols), 'format': _title_fmt('1A237E')},
        {'range': _rng(2,1,2,ncols), 'format': _note_fmt('E8EAF6')},
        {'range': _rng(3,1,3,ncols), 'format': _hdr('1A237E')},
    ]

    r = 4
    # 過去データ（新しい順）
    for dk in sorted(ctx.history.keys(), reverse=True):
        hd = ctx.history[dk]
        rows.append([dk, hd.get('period', '—'), hd.get('total_orders', '—'),
                     hd.get('total_gross', '—'), hd.get('net_after_plp', '—'),
                     hd.get('overall_cvr', '—'), hd.get('overall_ctr', '—'),
                     hd.get('total_items', '—'), '—', hd.get('要調査_count', '—')])
        fmts.append({'range': _rng(r, 1, r, ncols), 'format': _body('E3F2FD')})
        r += 1

    # 今週
    rows.append([f'{ctx.today.strftime("%Y/%m/%d")}（今週）', ctx.period,
                 ctx.total_orders, f'${ctx.total_gross:,.0f}',
                 f'${ctx.net:,.0f}', f'{ctx.overall_cvr:.3f}%',
                 f'{ctx.overall_ctr:.3f}%', ctx.total_items,
                 len(ctx.コア落ち), ctx.要調査_cnt])
    fmts.append({'range': _rng(r, 1, r, ncols), 'format': _body('C8E6C9', True)})

    ws.update(values=rows, range_name='A1')
    ws.batch_format(fmts)
    _merge_cells(sh, ws, f'A1:{_cl(ncols-1)}1')
    _merge_cells(sh, ws, f'A2:{_cl(ncols-1)}2')
    _set_widths(sh, ws, [120, 170, 65, 100, 100, 65, 65, 65, 65, 80])
    ws.freeze(rows=3)


# ===== メイン関数 =====
def write_report(g):
    """全シートをGoogleスプレッドシートに直接書き込む

    引数: g = globals() (create_weekly_report_v3.pyのグローバル変数)
    """
    print('📊 Google Sheets に直接書き込み中...')
    print(f'   対象: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}')

    # コンテキスト構築
    ctx = _init_ctx(g)

    # 接続
    sh = _connect()
    print('   ✅ スプレッドシートに接続')

    # 既存のノートを収集（上書き前に読み取る）
    print('   📝 既存の備考を読み取り中...')
    ctx.notes = _collect_all_notes(sh)
    json_notes = _load_notes()
    # JSONの方が古い場合はシートの値で上書き、新しい場合はマージ
    merged = {**json_notes, **ctx.notes}
    ctx.notes = merged
    print(f'   ✅ 備考 {len(ctx.notes)}件を読み取り')

    # 備考欄が「削除」のアイテムを全シートから除外（高橋紗英 2026-04-21 要望）
    _apply_exclude_filter(ctx)

    # シートセットアップ
    print('   📋 シートを準備中...')
    _setup_sheets(sh)
    time.sleep(1)

    # 各シートを書き込み（シート間に2秒待機してレート制限を回避）
    writers = [
        ('💬 AI総評',          _write_ai_review),
        ('📊 サマリー',        _write_summary),
        ('🔥 コア売れ筋TOP15', _write_core_top15),
        ('🚨 コア落ち',        _write_core_drop),
        ('⭐ 準売れ筋',        _write_semi_core),
        ('🌱 育成候補',        _write_nurture),
        ('⚠️ 要調査',          _write_investigate),
        ('🗑 削除候補',        _write_delete),
        ('🔥 コア売れ筋（月間）', _write_core_monthly),
        ('🗑 削除候補（月間）',   _write_delete_monthly),
        ('📈 改善追跡',        _write_improvement),
        ('📋 週次履歴',        _write_history),
    ]

    for name, writer_fn in writers:
        try:
            ws = sh.worksheet(name)
            ws.clear()
            # 既存のセルマージをクリア（ncols変更時のmergeCellsエラー回避）
            try:
                sh.batch_update({'requests': [{'unmergeCells': {
                    'range': {'sheetId': ws.id,
                              'startRowIndex': 0, 'endRowIndex': 1000,
                              'startColumnIndex': 0, 'endColumnIndex': 30}
                }}]})
            except Exception:
                pass
            time.sleep(0.5)
            writer_fn(sh, ws, ctx)
            print(f'   ✅ {name}')
            time.sleep(3)  # レート制限回避（60req/min制限・2段ヘッダー対応で増加）
        except Exception as e:
            print(f'   ❌ {name}: {e}')

    # ノートを保存（次週引き継ぎ用）
    _save_notes(ctx.notes)
    print(f'   💾 備考を保存: {NOTES_FILE}（{len(ctx.notes)}件）')

    print(f'')
    print(f'✅ Google Sheets 書き込み完了！')
    print(f'   🔗 https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}')
    print(f'   📋 {len(writers)}シート / 備考{len(ctx.notes)}件引き継ぎ')
