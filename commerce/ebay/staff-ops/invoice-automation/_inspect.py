"""請求書半自動化プロジェクト 事前構造調査（読み取り専用・書込なし）

3シートを開いて以下を確認:
  1. 収支表（KeiS）2026: シート一覧、本間/清水/佐々木請求書のフォーマット、収支表202602/202603の有無
  2. 仕入管理表: 報酬管理シートのAH列・26行目の値
  3. 【佐々木さん】実績管理表: 8373行目周辺の構造、累計行の数式
"""

import os, sys, json
import gspread
from google.oauth2.service_account import Credentials

sys.stdout.reconfigure(encoding='utf-8')

CREDS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'analytics', 'reffort-sheets-fcbca5a4bbc2.json'
)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

SHEET_KEISHI    = '1t_GHxn2PQY2F78Xgx9B0o602Wl0CeJSeBlA1Wo1ngME'  # 収支表（KeiS）2026
SHEET_SHIIRE    = '1B1kFIiu8M5Pw8U8YuERK8ApKUa4S--GfIzBkW53kY3g'  # 仕入管理表
SHEET_SASAKI    = '1cKiRQIUHb2LM0p8yrxkQ4voorEkjGgprf4ox8WOrrKY'  # 【佐々木さん】実績管理表

creds = Credentials.from_service_account_file(CREDS, scopes=SCOPES)
gc = gspread.authorize(creds)


def section(title):
    print('\n' + '=' * 70)
    print(title)
    print('=' * 70)


def dump_sheet_titles(ss, label):
    section(f'{label} / シート一覧')
    for ws in ss.worksheets():
        print(f'  - {ws.title}  ({ws.row_count} rows x {ws.col_count} cols)')


# ========== 1. 収支表（KeiS）2026 ==========
ss_kei = gc.open_by_key(SHEET_KEISHI)
dump_sheet_titles(ss_kei, '収支表（KeiS）2026')

# 本間請求書フォーマット確認
section('本間請求書（2026） / O:AB の2月分構造')
try:
    ws = ss_kei.worksheet('本間請求書（2026）')
    # O:AB は 列15-28、行1-50 を取って中身確認（値と数式両方）
    vals = ws.get('A1:AC50', value_render_option='FORMATTED_VALUE')
    formulas = ws.get('A1:AC50', value_render_option='FORMULA')
    print(f'rows: {len(vals)}')
    # 件名行・日付行・主要行だけ表示
    for r_idx in range(min(50, len(vals))):
        row = vals[r_idx]
        if any(c.strip() if isinstance(c, str) else False for c in row):
            # 列O(15)以降だけ抜粋
            o_cell = row[14] if len(row) > 14 else ''
            ab_cell = row[27] if len(row) > 27 else ''
            print(f'  R{r_idx+1:02d}: A={row[0] if row else "":<20.20}  O={str(o_cell):<25.25}  AB={str(ab_cell):<15.15}')
except Exception as e:
    print(f'ERROR: {e}')

# 清水請求書フォーマット確認
section('清水請求書（2026） / 直近月分の列構造')
try:
    ws = ss_kei.worksheet('清水請求書（2026）')
    print(f'  size: {ws.row_count} rows x {ws.col_count} cols')
    # ヘッダー行の存在列を確認するため A1:AZ8 を取得
    head = ws.get('A1:AZ10', value_render_option='FORMATTED_VALUE')
    for r_idx, row in enumerate(head):
        if any(c.strip() if isinstance(c, str) else False for c in row):
            print(f'  R{r_idx+1}: {row[:30]}')
except Exception as e:
    print(f'ERROR: {e}')

# 佐々木請求書フォーマット確認
section('佐々木請求書（2026） / 直近月分の列構造')
try:
    ws = ss_kei.worksheet('佐々木請求書（2026）')
    print(f'  size: {ws.row_count} rows x {ws.col_count} cols')
    head = ws.get('A1:AZ25', value_render_option='FORMATTED_VALUE')
    for r_idx, row in enumerate(head):
        if any(c.strip() if isinstance(c, str) else False for c in row):
            print(f'  R{r_idx+1}: {row[:30]}')
except Exception as e:
    print(f'ERROR: {e}')

# 収支表202602 / 収支表202603 の存在確認 + 構造
section('収支表202602 / SKU=S オーダー抽出テスト')
try:
    ws = ss_kei.worksheet('収支表202602')
    print(f'  size: {ws.row_count} rows x {ws.col_count} cols')
    head = ws.get('A1:V5', value_render_option='FORMATTED_VALUE')
    for r_idx, row in enumerate(head):
        print(f'  R{r_idx+1}: {row[:22]}')
    # B列のSKUがSで始まるものを件数だけカウント
    b_col = ws.col_values(2)  # B列
    s_count = sum(1 for v in b_col if isinstance(v, str) and v.strip().startswith('S'))
    print(f'  B列SKUがSで始まる件数: {s_count}')
except Exception as e:
    print(f'ERROR: {e}')

section('収支表202603 / 存在確認のみ')
try:
    ws = ss_kei.worksheet('収支表202603')
    print(f'  size: {ws.row_count} rows x {ws.col_count} cols, B列上から3件: {ws.col_values(2)[:5]}')
except Exception as e:
    print(f'ERROR: {e}')


# ========== 2. 仕入管理表 / 報酬管理 / AH26 ==========
section('仕入管理表 / 報酬管理シート / AH列周辺')
try:
    ss_shi = gc.open_by_key(SHEET_SHIIRE)
    titles = [w.title for w in ss_shi.worksheets()]
    print(f'  シート一覧: {titles}')
    ws = ss_shi.worksheet('報酬管理')
    # AH列を上から30行
    ah = ws.range('AH1:AH30')
    print('  AH1:AH30 値:')
    for c in ah:
        if c.value:
            print(f'    AH{c.row}: {c.value!r}')
    # AH26 周辺の周辺列も併記
    surround = ws.get('A24:AI28', value_render_option='FORMATTED_VALUE')
    print('  A24:AI28 構造:')
    for r_idx, row in enumerate(surround):
        print(f'    R{24+r_idx}: {row}')
except Exception as e:
    print(f'ERROR: {e}')


# ========== 3. 【佐々木さん】実績管理表 / 8373行目周辺 ==========
section('【佐々木さん】実績管理表 / 8373行目周辺')
try:
    ss_sas = gc.open_by_key(SHEET_SASAKI)
    titles = [w.title for w in ss_sas.worksheets()]
    print(f'  シート一覧: {titles}')
    ws = ss_sas.worksheets()[0]
    print(f'  デフォルトシート: {ws.title}, size: {ws.row_count} x {ws.col_count}')

    # ヘッダー（1-3行）
    print('  1-5行ヘッダー:')
    head = ws.get('A1:V5', value_render_option='FORMATTED_VALUE')
    for r_idx, row in enumerate(head):
        print(f'    R{r_idx+1}: {row[:22]}')

    # 上部累計行確認（I3, U3 など）
    print('\n  累計セル数式（I3, S3, U3 周辺）:')
    top_formulas = ws.get('A1:V10', value_render_option='FORMULA')
    for r_idx, row in enumerate(top_formulas):
        for c_idx, cell in enumerate(row):
            if isinstance(cell, str) and cell.startswith('='):
                col_letter = chr(ord('A') + c_idx) if c_idx < 26 else 'A' + chr(ord('A') + c_idx - 26)
                print(f'    {col_letter}{r_idx+1}: {cell[:120]}')

    # 8373行目周辺（前月集計行）
    print('\n  8370-8378行（2月集計行周辺）値:')
    around = ws.get('A8370:V8378', value_render_option='FORMATTED_VALUE')
    for r_idx, row in enumerate(around):
        print(f'    R{8370+r_idx}: {row[:22]}')
    print('\n  8370-8378行（2月集計行周辺）数式:')
    around_f = ws.get('A8370:V8378', value_render_option='FORMULA')
    for r_idx, row in enumerate(around_f):
        for c_idx, cell in enumerate(row):
            if isinstance(cell, str) and cell.startswith('='):
                col_letter = chr(ord('A') + c_idx) if c_idx < 26 else 'A' + chr(ord('A') + c_idx - 26)
                print(f'    {col_letter}{8370+r_idx}: {cell[:160]}')

    # 最終データ行を探す（S列・U列）
    print('\n  実データの最終行を推定（U列が空でない最後の行）:')
    u_col = ws.col_values(21)  # U列 = 21
    last_filled = max((i+1 for i, v in enumerate(u_col) if v not in ('', None)), default=0)
    print(f'    U列最終非空行: {last_filled}')
    s_col = ws.col_values(19)  # S列
    last_s = max((i+1 for i, v in enumerate(s_col) if v not in ('', None)), default=0)
    print(f'    S列最終非空行: {last_s}')

except Exception as e:
    import traceback
    print(f'ERROR: {e}')
    traceback.print_exc()

section('調査完了')
