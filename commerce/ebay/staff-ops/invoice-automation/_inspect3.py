"""最終確認：仕入管理表AH26、本間W15、佐々木固定単価、備考セル位置"""

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

creds = Credentials.from_service_account_file(CREDS, scopes=SCOPES)
gc = gspread.authorize(creds)


def sec(t): print('\n' + '='*70 + '\n' + t + '\n' + '='*70)


# ===== 1. 仕入管理表 報酬管理 AH26 =====
sec('仕入管理表 / 報酬管理 / AH列の月別構造')
ss = gc.open_by_key(SHEET_SHIIRE)
print(f'  ss title: {ss.title}')
print(f'  worksheets: {[w.title for w in ss.worksheets()]}')
ws = ss.worksheet('報酬管理')
print(f'  size: {ws.row_count} x {ws.col_count}')

# AH列の値と数式を全部
ah_v = ws.get('AH1:AH40', value_render_option='FORMATTED_VALUE')
ah_f = ws.get('AH1:AH40', value_render_option='FORMULA')
print('  AH列 全行（値 / 数式）:')
for i in range(min(40, len(ah_v))):
    v = ah_v[i][0] if ah_v[i] else ''
    f = ah_f[i][0] if ah_f[i] else ''
    if v or f:
        print(f'    AH{i+1}: 値={v!r}, 式={f!r}')

# AH26周辺の前後列も出してコンテクスト確認
sec('仕入管理表 / 報酬管理 / 月名列を特定（A-AI 24-30行）')
mid = ws.get('A24:AI30', value_render_option='FORMATTED_VALUE')
for i, row in enumerate(mid):
    print(f'  R{24+i}: {row}')


# ===== 2. 本間請求書 W15 =====
sec('本間請求書（2026） / W15単価セル + 周辺')
ss = gc.open_by_key(SHEET_KEISHI)
ws = ss.worksheet('本間請求書（2026）')
# 1月ブロック単価=I15, 2月=W15
for cell in ['I15', 'W15', 'I8', 'W8', 'B8', 'P8', 'N5', 'AB5']:
    v = ws.acell(cell, value_render_option='FORMATTED_VALUE').value
    f = ws.acell(cell, value_render_option='FORMULA').value
    print(f'  {cell}: 値={v!r}, 式={f!r}')

# 本間の請求書フォーマット全体（行14-25）を結合セル含めて
sec('本間請求書 全体構造（A1:AB25 値 + 数式混在で）')
combo = ws.get('A1:AB25', value_render_option='FORMATTED_VALUE')
for i, row in enumerate(combo):
    if any(c.strip() if isinstance(c, str) else c for c in row):
        # 列番号付きで非空セルだけ
        cells = [(chr(65+j) if j < 26 else 'A'+chr(65+j-26), c) for j, c in enumerate(row) if (c.strip() if isinstance(c, str) else c)]
        print(f'  R{i+1}: {cells}')


# ===== 3. 佐々木請求書 固定単価・備考 =====
sec('佐々木請求書（2026） / R15-R18 単価行 + 備考セル位置')
ws = ss.worksheet('佐々木請求書（2026）')
# 1月ブロック: I15(出品単価), I16, I17, I18 / 備考L17
# 2月ブロック: W15, W16, W17, W18 / 備考Z17
for row in range(15, 19):
    for col_letter in ['I', 'L', 'W', 'Z']:
        cell = f'{col_letter}{row}'
        v = ws.acell(cell, value_render_option='FORMATTED_VALUE').value
        f = ws.acell(cell, value_render_option='FORMULA').value
        if v or f:
            print(f'  {cell}: 値={v!r}, 式={f!r}')


# ===== 4. 清水請求書 単価セル確認 =====
sec('清水請求書（2026） / 単価セル + 件名 + 日付')
ws = ss.worksheet('清水請求書（2026）')
for cell in ['I15', 'W15', 'B8', 'P8', 'N5', 'AB5', 'I11', 'W11']:
    v = ws.acell(cell, value_render_option='FORMATTED_VALUE').value
    f = ws.acell(cell, value_render_option='FORMULA').value
    if v or f:
        print(f'  {cell}: 値={v!r}, 式={f!r}')

# 清水の請求書フォーマット詳細（行14-20）
sec('清水請求書 行14-22 詳細（O:AB ＝ 2月分）')
combo = ws.get('A14:AB22', value_render_option='FORMATTED_VALUE')
for i, row in enumerate(combo):
    if any(c.strip() if isinstance(c, str) else c for c in row):
        cells = [(chr(65+j) if j < 26 else 'A'+chr(65+j-26), c) for j, c in enumerate(row) if (c.strip() if isinstance(c, str) else c)]
        print(f'  R{14+i}: {cells}')

# ===== 5. 結合セル確認（本間用）=====
sec('本間請求書 結合セル一覧（O:AB ＝ 2月分の範囲）')
import gspread
meta = ss.fetch_sheet_metadata()
for s in meta['sheets']:
    if s['properties']['title'] == '本間請求書（2026）':
        merges = s.get('merges', [])
        # O:AB = 列15-28 (0-indexed: 14-27)
        for m in merges:
            sc = m.get('startColumnIndex', 0)
            ec = m.get('endColumnIndex', 0)
            sr = m.get('startRowIndex', 0)
            er = m.get('endRowIndex', 0)
            if 14 <= sc < 28:  # 2月ブロック範囲
                sl = chr(65+sc) if sc < 26 else 'A'+chr(65+sc-26)
                el = chr(65+(ec-1)) if (ec-1) < 26 else 'A'+chr(65+(ec-1)-26)
                print(f'  R{sr+1}-{er} / {sl}{sr+1}:{el}{er}')

print('\n=== END ===')
