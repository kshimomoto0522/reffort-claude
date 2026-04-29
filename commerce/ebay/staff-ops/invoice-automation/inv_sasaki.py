"""佐々木請求書ロジック（最複雑）

フロー:
  1. 当月収支表（収支表YYYYMM）からSKU=Sの行を抽出（B:Uの20列）
  2. 実績管理表のG3式から前月集計行・前月明細範囲を自動検出
  3. 新月集計行 = 前月予備空白行+1
  4. ドライラン推定: I3現在値 + 当月S合計×0.95 で当月累計推定
  5. 5万切捨で当月対象額・19%でインセンティブ・備考を生成
  6. 実書込時はI3に+U{nsr}追記後の確定値で再計算してから請求書側に反映
"""

import re

from inv_common import (
    get_gc, col_letter, block_start_col, month_end_str,
    ensure_columns, copy_block, copy_column_widths, copy_format,
    fmt_money, floor_to,
)


def _detect_summary_position(ws_jis):
    """G3式から前月集計行と新月開始行を自動検出"""
    g3_old = ws_jis.acell('G3', value_render_option='FORMULA').value or ''
    i3_old = ws_jis.acell('I3', value_render_option='FORMULA').value or ''
    refs_g = re.findall(r'R(\d+)', g3_old)
    if not refs_g:
        raise ValueError(f'G3式に集計行参照がありません: {g3_old[:200]}')
    prev_summary_row = int(refs_g[-1])

    prev_r_formula = ws_jis.acell(f'R{prev_summary_row}', value_render_option='FORMULA').value or ''
    cleaned = prev_r_formula.replace(' ', '')
    m = re.match(r'=SUM\(R(\d+):R(\d+)\)', cleaned)
    if not m:
        raise ValueError(f'R{prev_summary_row} のSUM式が想定外: {prev_r_formula}')
    prev_detail_start = int(m.group(1))
    prev_spare_row = int(m.group(2))
    new_summary_row = prev_spare_row + 1

    return {
        'g3_old': g3_old,
        'i3_old': i3_old,
        'prev_summary_row': prev_summary_row,
        'prev_detail_start': prev_detail_start,
        'prev_spare_row': prev_spare_row,
        'new_summary_row': new_summary_row,
    }


# 明細列の型変換ルール（B=index 0 起点）
# USD列(H,I,J,L,M,N,O): 文字列「$XX.XX」のまま保存（前月と同じ）
# %列(K,T): 数値化（0.07 形式）
# JPY列(P,Q,R,S): ¥/カンマ除去して数値化（SUM対象のため必須）
_USD_COL_INDICES = {6, 7, 8, 10, 11, 12, 13}
_PCT_COL_INDICES = {9, 18}
_JPY_COL_INDICES = {14, 15, 16, 17}


def _transform_cell(col_idx: int, value):
    """前月8374の値型に合わせて変換"""
    if value is None or value == '':
        return ''
    s = str(value).strip()
    if not s:
        return ''
    if col_idx in _USD_COL_INDICES:
        return s  # 文字列のまま
    if col_idx in _PCT_COL_INDICES:
        if s.endswith('%'):
            try:
                return float(s[:-1].replace(',', '')) / 100
            except ValueError:
                return s
        return s
    if col_idx in _JPY_COL_INDICES:
        cleaned = s.replace('¥', '').replace('￥', '').replace(',', '').strip()
        sign = 1
        if cleaned.startswith('-'):
            sign = -1
            cleaned = cleaned[1:].strip()
        if not cleaned:
            return ''
        try:
            n = float(cleaned)
            return sign * (int(n) if n == int(n) else n)
        except ValueError:
            return s
    return s


def _extract_monthly_details(ws_bs, config) -> list:
    """当月収支表から SKU=S の明細を抽出。
    FORMATTED_VALUEで取得 → 列ごとの型変換 → 前月と同じ値型で返す。
    """
    sasaki_cfg = config['sasaki']
    data_start = sasaki_cfg['monthly_balance_data_start_row']
    end_col = sasaki_cfg['monthly_balance_cols']['end_col']
    sku_idx = sasaki_cfg['monthly_balance_cols']['sku_col_index']
    paste_end_idx = sasaki_cfg['monthly_balance_cols']['paste_end_col_index']

    b_col = ws_bs.col_values(2)
    last_row = max((i + 1 for i, v in enumerate(b_col) if v not in ('', None)), default=data_start)
    if last_row < data_start:
        last_row = data_start

    raw = ws_bs.get(
        f'B{data_start}:{end_col}{last_row}',
        value_render_option='FORMATTED_VALUE',
    )

    s_rows = []
    for row in raw:
        if len(row) > sku_idx:
            sku = row[sku_idx]
            if isinstance(sku, str) and sku.startswith('S'):
                padded = list(row) + [''] * (paste_end_idx + 1 - len(row))
                typed = [_transform_cell(i, v) for i, v in enumerate(padded[:paste_end_idx + 1])]
                s_rows.append(typed)
    return s_rows


def _check_new_summary_row_clean(ws_jis, new_summary_row, n_details):
    """新月集計行＋明細予定範囲が空であることを確認"""
    # 集計行＋明細N行＋予備空白行 を一括取得
    last_row = new_summary_row + n_details + 1
    rng = f'A{new_summary_row}:U{last_row}'
    rows = ws_jis.get(rng, value_render_option='FORMATTED_VALUE')
    occupied = []
    for r_idx, row in enumerate(rows):
        if any((c.strip() if isinstance(c, str) else c) for c in row):
            occupied.append(new_summary_row + r_idx)
    return occupied


def plan_sasaki(year: int, month: int, config: dict) -> dict:
    """書込プラン生成（全データを事前取得・推定値も含む）"""
    gc = get_gc()
    sasaki_cfg = config['sasaki']
    layout = config['invoice_layout']

    # ==== 実績管理表 ====
    ss_sas = gc.open_by_key(config['spreadsheets']['sasaki'])
    ws_jis = ss_sas.worksheet(sasaki_cfg['jisseki_sheet'])

    pos = _detect_summary_position(ws_jis)
    prev_acc_u_raw = ws_jis.acell('I3', value_render_option='UNFORMATTED_VALUE').value
    prev_acc_u = float(prev_acc_u_raw) if prev_acc_u_raw not in (None, '') else 0.0

    # ==== 当月収支表 ====
    bs_name = sasaki_cfg['monthly_balance_sheet_pattern'].format(yyyymm=f'{year}{month:02d}')
    ss_kei = gc.open_by_key(config['spreadsheets']['keishi'])
    try:
        ws_bs = ss_kei.worksheet(bs_name)
    except Exception as e:
        raise ValueError(f'当月の収支表シート「{bs_name}」が見つかりません: {e}')

    s_rows = _extract_monthly_details(ws_bs, config)
    n = len(s_rows)

    # ==== 占有チェック ====
    nsr = pos['new_summary_row']
    occupied = _check_new_summary_row_clean(ws_jis, nsr, n)

    detail_start = nsr + 1
    detail_end = detail_start + n - 1
    spare_row = detail_start + n  # = detail_end + 1

    # 当月S合計（明細17列目=S列）→ U推定
    # _transform_cell でJPY列は数値化済み
    monthly_s_sum = sum(
        r[17] if len(r) > 17 and isinstance(r[17], (int, float)) else 0
        for r in s_rows
    )
    estimated_monthly_u = monthly_s_sum * sasaki_cfg['jisseki_ratio']

    estimated_acc = prev_acc_u + estimated_monthly_u
    prev_floor = floor_to(prev_acc_u, sasaki_cfg['floor_unit'])
    estimated_floor = floor_to(estimated_acc, sasaki_cfg['floor_unit'])
    estimated_target = estimated_floor - prev_floor
    estimated_incentive = int(estimated_target * sasaki_cfg['incentive_rate'])
    estimated_target_man = estimated_target // 10000
    estimated_acc_man = estimated_floor // 10000
    estimated_remarks = sasaki_cfg['remarks_template'].format(
        target_man=estimated_target_man,
        acc_man=f'{estimated_acc_man:,}',
    )

    # ==== 請求書側 ====
    src_col = block_start_col(month - 1, layout['block_width'])
    dst_col = block_start_col(month, layout['block_width'])
    needed = dst_col + layout['block_width'] - 1

    return {
        'staff': '佐々木',
        # 請求書
        'sheet': config['invoice_sheets']['sasaki'],
        'src_block': f'{col_letter(src_col)}:{col_letter(src_col + layout["block_width"] - 1)}',
        'dst_block': f'{col_letter(dst_col)}:{col_letter(dst_col + layout["block_width"] - 1)}',
        'src_col': src_col,
        'dst_col': dst_col,
        'needed_col_count': needed,
        # 実績管理表
        'jisseki_sheet': sasaki_cfg['jisseki_sheet'],
        'monthly_balance_sheet': bs_name,
        'prev_summary_row': pos['prev_summary_row'],
        'prev_detail_start': pos['prev_detail_start'],
        'prev_spare_row': pos['prev_spare_row'],
        'new_summary_row': nsr,
        'detail_start_row': detail_start,
        'detail_end_row': detail_end,
        'spare_blank_row': spare_row,
        'detail_count': n,
        'details': s_rows,
        'g3_old': pos['g3_old'],
        'i3_old': pos['i3_old'],
        'g3_new_tail': f'+R{nsr}',
        'i3_new_tail': f'+U{nsr}',
        'occupied_rows': occupied,
        # 推定インセンティブ
        'prev_acc_u': prev_acc_u,
        'monthly_s_sum': monthly_s_sum,
        'estimated_monthly_u': estimated_monthly_u,
        'estimated_acc': estimated_acc,
        'prev_floor': prev_floor,
        'estimated_floor': estimated_floor,
        'estimated_target': estimated_target,
        'estimated_incentive': estimated_incentive,
        'estimated_remarks': estimated_remarks,
    }


def print_plan(plan: dict):
    print(f"\n--- {plan['staff']}請求書 ---")
    print(f"  請求書シート: {plan['sheet']}")
    print(f"  ブロックコピー: {plan['src_block']} → {plan['dst_block']}")
    print(f"  必要列数: {plan['needed_col_count']}")
    print()
    print(f"  【実績管理表側】")
    print(f"    実績シート: {plan['jisseki_sheet']}")
    print(f"    当月収支表: {plan['monthly_balance_sheet']}")
    print(f"    前月集計行: {plan['prev_summary_row']}行 (明細{plan['prev_detail_start']}〜{plan['prev_spare_row']-1}・予備{plan['prev_spare_row']})")
    print(f"    新月集計行: {plan['new_summary_row']}行")
    print(f"    明細書込: {plan['detail_start_row']}〜{plan['detail_end_row']} ({plan['detail_count']}行)")
    print(f"    予備空白: {plan['spare_blank_row']}行")
    if plan['occupied_rows']:
        print(f"    ⚠️  既存データ検出行: {plan['occupied_rows']} ← 書込前に要確認！")
    else:
        print(f"    ✓ 書込予定範囲はすべて空")
    print(f"    G3末尾追記: {plan['g3_new_tail']}")
    print(f"    I3末尾追記: {plan['i3_new_tail']}")
    print()
    print(f"  【推定インセンティブ計算】")
    print(f"    前月までの累計U (I3現在値): {fmt_money(plan['prev_acc_u'])}円")
    print(f"    当月S列合計（明細{plan['detail_count']}行）: {fmt_money(plan['monthly_s_sum'])}円")
    print(f"    当月U推定 (S×0.95): {fmt_money(plan['estimated_monthly_u'])}円")
    print(f"    当月累計推定: {fmt_money(plan['estimated_acc'])}円")
    print(f"    前月累計5万切捨: {fmt_money(plan['prev_floor'])}円 ({plan['prev_floor']//10000}万円)")
    print(f"    当月累計5万切捨: {fmt_money(plan['estimated_floor'])}円 ({plan['estimated_floor']//10000:,}万円)")
    print(f"    当月対象額: {fmt_money(plan['estimated_target'])}円 ({plan['estimated_target']//10000}万円)")
    print(f"    インセンティブ (×19%): {fmt_money(plan['estimated_incentive'])}円")
    print(f"    備考予定: {plan['estimated_remarks']!r}")
    print()
    print(f"  【請求書側書込（推定）】")
    layout_offsets = {
        'subject': 1,
        'date': 13,
        'incentive_unit': 8,
        'incentive_remarks': 11,
    }
    dc = plan['dst_col']
    print(f"    {col_letter(dc + layout_offsets['subject'])}8 = '出品・リサーチ業務（X月）' ← 当月名")
    print(f"    {col_letter(dc + layout_offsets['date'])}5 = 月末日")
    print(f"    {col_letter(dc + layout_offsets['incentive_unit'])}17 = {fmt_money(plan['estimated_incentive'])} (推定)")
    print(f"    {col_letter(dc + layout_offsets['incentive_remarks'])}17 = 備考 (推定)")
    print(f"    ※ 出品単価30/リサーチ単価50/メンテ15,000および出品数・リサーチ数はコピペで前月値が維持される（社長手修正想定）")


def apply_sasaki(year: int, month: int, config: dict) -> dict:
    """実書込（3フェーズ）"""
    plan = plan_sasaki(year, month, config)

    if plan['occupied_rows']:
        raise RuntimeError(
            f'実績管理表の書込予定範囲に既存データあり: {plan["occupied_rows"]}。'
            f'手動確認後に再実行してください。'
        )

    sasaki_cfg = config['sasaki']
    layout = config['invoice_layout']
    gc = get_gc()

    # ===== Phase 1: 実績管理表書込 =====
    ss_sas = gc.open_by_key(config['spreadsheets']['sasaki'])
    ws_jis = ss_sas.worksheet(sasaki_cfg['jisseki_sheet'])

    nsr = plan['new_summary_row']
    detail_start = plan['detail_start_row']
    spare = plan['spare_blank_row']

    # 1-1. 明細N行（B:T = 19列、U列の還付金は不要）
    if plan['details']:
        ws_jis.update(
            range_name=f'B{detail_start}:T{plan["detail_end_row"]}',
            values=plan['details'],
            value_input_option='USER_ENTERED',
        )

    # 1-2. 集計行（B:Uの20列・U列はS*0.95の式）
    summary = [''] * 20  # B(0)..U(19)
    summary[0]  = f'{year}年{month}月'
    summary[4]  = '販売数'
    summary[5]  = f'=COUNTA(F{detail_start}:F{spare})'
    summary[8]  = '実績 '
    summary[16] = f'=SUM(R{detail_start}:R{spare})'
    summary[17] = f'=SUM(S{detail_start}:S{spare})'
    summary[18] = f'=S{nsr}/R{nsr}'
    summary[19] = f'=S{nsr}*0.95'
    ws_jis.update(
        range_name=f'B{nsr}:U{nsr}',
        values=[summary],
        value_input_option='USER_ENTERED',
    )

    # 1-3. 書式コピー（前月集計行→新月集計行、前月明細1行目→新月明細N行）
    # A:V (0-21) の22列分の書式をコピー
    copy_format(ss_sas, ws_jis.id,
                src_row_start_idx=plan['prev_summary_row'] - 1,
                src_row_end_idx=plan['prev_summary_row'],
                src_col_start_idx=0, src_col_end_idx=22,
                dst_row_start_idx=nsr - 1,
                dst_row_end_idx=nsr,
                dst_col_start_idx=0, dst_col_end_idx=22)
    if plan['detail_count'] > 0:
        copy_format(ss_sas, ws_jis.id,
                    src_row_start_idx=plan['prev_detail_start'] - 1,
                    src_row_end_idx=plan['prev_detail_start'],
                    src_col_start_idx=0, src_col_end_idx=22,
                    dst_row_start_idx=detail_start - 1,
                    dst_row_end_idx=plan['detail_end_row'],
                    dst_col_start_idx=0, dst_col_end_idx=22)

    # 1-4. G3, I3 累計式更新
    ws_jis.batch_update(
        [
            {'range': 'G3', 'values': [[plan['g3_old'] + plan['g3_new_tail']]]},
            {'range': 'I3', 'values': [[plan['i3_old'] + plan['i3_new_tail']]]},
        ],
        value_input_option='USER_ENTERED',
    )

    # ===== Phase 2: I3確定値で再計算 =====
    cur_acc_raw = ws_jis.acell('I3', value_render_option='UNFORMATTED_VALUE').value
    cur_acc_u = float(cur_acc_raw) if cur_acc_raw not in (None, '') else 0.0

    prev_floor = floor_to(plan['prev_acc_u'], sasaki_cfg['floor_unit'])
    cur_floor = floor_to(cur_acc_u, sasaki_cfg['floor_unit'])
    target = cur_floor - prev_floor
    incentive = int(target * sasaki_cfg['incentive_rate'])
    target_man = target // 10000
    acc_man = cur_floor // 10000
    remarks = sasaki_cfg['remarks_template'].format(
        target_man=target_man,
        acc_man=f'{acc_man:,}',
    )

    # ===== Phase 3: 請求書書込 =====
    ss_kei = gc.open_by_key(config['spreadsheets']['keishi'])
    ws_inv = ss_kei.worksheet(plan['sheet'])

    ensure_columns(ws_inv, plan['needed_col_count'])
    copy_block(ss_kei, ws_inv.id,
               src_col_start=plan['src_col'],
               dst_col_start=plan['dst_col'],
               width=layout['block_width'],
               rows=layout['copy_rows'])
    copy_column_widths(ss_kei, ws_inv.id,
                       src_col_start_idx=plan['src_col'] - 1,
                       dst_col_start_idx=plan['dst_col'] - 1,
                       count=layout['block_width'])

    dc = plan['dst_col']
    inv_updates = [
        {'range': f'{col_letter(dc + layout["offsets"]["subject_col"])}{layout["rows"]["subject"]}',
         'values': [[sasaki_cfg['subject_template'].format(month=month)]]},
        {'range': f'{col_letter(dc + layout["offsets"]["date_col"])}{layout["rows"]["date"]}',
         'values': [[month_end_str(year, month)]]},
        {'range': f'{col_letter(dc + layout["offsets"]["unit_col"])}{layout["rows"]["incentive"]}',
         'values': [[incentive]]},
        {'range': f'{col_letter(dc + layout["offsets"]["remarks_col"])}{layout["rows"]["incentive"]}',
         'values': [[remarks]]},
    ]
    ws_inv.batch_update(inv_updates, value_input_option='USER_ENTERED')

    return {
        'plan': plan,
        'status': 'applied',
        'final': {
            'cur_acc_u': cur_acc_u,
            'cur_floor': cur_floor,
            'prev_floor': prev_floor,
            'target': target,
            'incentive': incentive,
            'remarks': remarks,
        },
    }
