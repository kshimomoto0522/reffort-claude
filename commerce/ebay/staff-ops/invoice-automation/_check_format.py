"""8374行(2月明細1行目・正解)と8531行(3月明細1行目・問題)の数値書式を比較"""

import sys, json
from inv_common import get_gc

sys.stdout.reconfigure(encoding='utf-8')

SASAKI = '1cKiRQIUHb2LM0p8yrxkQ4voorEkjGgprf4ox8WOrrKY'

gc = get_gc()
ss = gc.open_by_key(SASAKI)
ws = ss.worksheets()[0]

url = f'https://sheets.googleapis.com/v4/spreadsheets/{ss.id}'
params = {
    'fields': 'sheets(properties(title,sheetId),data(rowData(values(userEnteredFormat(numberFormat),effectiveFormat(numberFormat),userEnteredValue,formattedValue))))',
    'ranges': [f'{ws.title}!B8374:U8374', f'{ws.title}!B8531:U8531'],
}
resp = ss.client.session.get(url, params=params)
resp.raise_for_status()
data = resp.json()

cols = ['B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U']

for s_idx, sheet_block in enumerate(data['sheets'][0]['data']):
    label = '8374 (2月明細・正解)' if s_idx == 0 else '8531 (3月明細・問題)'
    print(f'\n=== {label} ===')
    rows = sheet_block.get('rowData', [])
    if not rows:
        print('  (no data)')
        continue
    values = rows[0].get('values', [])
    for col_idx, cell in enumerate(values):
        if col_idx >= len(cols):
            break
        col = cols[col_idx]
        ue_fmt = cell.get('userEnteredFormat', {}).get('numberFormat')
        ef_fmt = cell.get('effectiveFormat', {}).get('numberFormat')
        formatted = cell.get('formattedValue')
        print(f'  {col}: formatted={formatted!r}, userEntered={ue_fmt}, effective={ef_fmt}')
