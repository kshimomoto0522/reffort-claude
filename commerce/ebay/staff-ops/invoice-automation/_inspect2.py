"""追加調査：仕入管理表アクセス、収支表のSKU列、累計式フル取得"""

import os, sys
import gspread
from google.oauth2.service_account import Credentials

sys.stdout.reconfigure(encoding='utf-8')

CREDS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'analytics', 'reffort-sheets-fcbca5a4bbc2.json'
)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

SHEET_KEISHI = '1t_GHxn2PQY2F78Xgx9B0o602Wl0CeJSeBlA1Wo1ngME'
SHEET_SHIIRE = '1B1kFIiu8M5Pw8U8YuERK8ApKUa4S--GfIzBkW53kY3g'
SHEET_SASAKI = '1cKiRQIUHb2LM0p8yrxkQ4voorEkjGgprf4ox8WOrrKY'

creds = Credentials.from_service_account_file(CREDS, scopes=SCOPES)
gc = gspread.authorize(creds)


def section(title):
    print('\n' + '=' * 70)
    print(title)
    print('=' * 70)


# ===== 1. 仕入管理表 =====
section('1. 仕入管理表 / シート一覧 + 報酬管理AH26')
try:
    ss = gc.open_by_key(SHEET_SHIIRE)
    print(f'  spreadsheet title: {ss.title}')
    titles = [w.title for w in ss.worksheets()]
    print(f'  worksheets: {titles}')
    for t in titles:
        if '報酬' in t or '報奨' in t or 'reward' in t.lower():
            ws = ss.worksheet(t)
            print(f'\n  シート [{t}] のサイズ: {ws.row_count} x {ws.col_count}')
            # ヘッダー行（1-5行）と20-30行を表示
            head = ws.get('A1:AJ5', value_render_option='FORMATTED_VALUE')
            print(f'  ヘッダー A1:AJ5:')
            for r_idx, row in enumerate(head):
                print(f'    R{r_idx+1}: {row}')
            print(f'\n  20-30行 A20:AJ30:')
            mid = ws.get('A20:AJ30', value_render_option='FORMATTED_VALUE')
            for r_idx, row in enumerate(mid):
                print(f'    R{20+r_idx}: {row}')
            print(f'\n  AH列 AH1:AH35 数式:')
            ah_f = ws.get('AH1:AH35', value_render_option='FORMULA')
            for r_idx, row in enumerate(ah_f):
                if row and row[0]:
                    print(f'    AH{r_idx+1}: {row[0]}')
except Exception as e:
    import traceback
    print(f'  ERROR: {e!r}')
    traceback.print_exc()

# ===== 2. 収支表202602 のSKU列特定 =====
section('2. 収支表202602 / B:U 全列ヘッダー + サンプル3行')
try:
    ss = gc.open_by_key(SHEET_KEISHI)
    ws = ss.worksheet('収支表202602')
    head = ws.get('A1:AN15', value_render_option='FORMATTED_VALUE')
    for r_idx, row in enumerate(head):
        if row:
            print(f'    R{r_idx+1}: {row}')
    print('\n  各列の最初の非空値:')
    for col_idx in range(1, 25):
        col_vals = ws.col_values(col_idx)
        first_nonempty = next(((i+1, v) for i, v in enumerate(col_vals) if v not in ('', None)), None)
        col_letter = chr(ord('A') + col_idx - 1)
        if first_nonempty:
            print(f'    {col_letter}列: 初出R{first_nonempty[0]}={first_nonempty[1]!r}')
    # SKU列を探す: F列(SKU列ヘッダー候補)を確認
    print('\n  F列（実績管理表でのSKUに該当する位置）の上から20件:')
    f_col = ws.col_values(6)[:20]
    for i, v in enumerate(f_col):
        if v:
            print(f'    F{i+1}: {v!r}')
except Exception as e:
    import traceback
    print(f'  ERROR: {e}')
    traceback.print_exc()

# ===== 3. 実績管理表 累計式フル取得 =====
section('3. 実績管理表 / G3 I3 の累計式（フル）')
try:
    ss = gc.open_by_key(SHEET_SASAKI)
    ws = ss.worksheets()[0]
    # 個別セルでフル取得
    g3 = ws.acell('G3', value_render_option='FORMULA').value
    i3 = ws.acell('I3', value_render_option='FORMULA').value
    h3 = ws.acell('H3', value_render_option='FORMULA').value
    print(f'  G3: {g3}')
    print(f'  H3: {h3}')
    print(f'  I3: {i3}')
    # 各月集計行のリスト推定（G3の参照）
    # G3に列挙されている R7, R21, ... をすべて取り出して、それらが集計行であることを確認
    import re
    refs_g = re.findall(r'R(\d+)', g3 or '')
    refs_i = re.findall(r'S(\d+)', i3 or '')
    print(f'  G3が参照する集計行（R）: {refs_g}')
    print(f'  I3が参照する集計行（S）: {refs_i}')
    # 最後の参照行から、新月（3月）はその次の集計行になることを確認
    if refs_g:
        last_summary_row = int(refs_g[-1])
        print(f'  最後の集計行: R{last_summary_row}')
        # その行のE列（月名）を見る
        e_val = ws.acell(f'E{last_summary_row}', value_render_option='FORMATTED_VALUE').value
        b_val = ws.acell(f'B{last_summary_row}', value_render_option='FORMATTED_VALUE').value
        print(f'  R{last_summary_row}: B={b_val!r}, E={e_val!r}')
except Exception as e:
    import traceback
    print(f'  ERROR: {e}')
    traceback.print_exc()

# ===== 4. 8528-8540行 の状態確認（前月明細終端と空白行）=====
section('4. 実績管理表 / 8525-8540行（前月明細終端と空白）')
try:
    ss = gc.open_by_key(SHEET_SASAKI)
    ws = ss.worksheets()[0]
    around = ws.get('A8525:V8540', value_render_option='FORMATTED_VALUE')
    for r_idx, row in enumerate(around):
        marker = '  '
        # 空行ならマークする
        if not any(c.strip() if isinstance(c, str) else c for c in row):
            marker = '空'
        print(f'  {marker} R{8525+r_idx}: {row[:8]}')
except Exception as e:
    print(f'  ERROR: {e}')

print('\n=== END ===')
