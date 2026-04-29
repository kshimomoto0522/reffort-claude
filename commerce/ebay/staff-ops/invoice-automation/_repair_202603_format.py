"""3月明細の数値書式リペア

8531〜8660 の明細を「FORMATTED_VALUE」で再取得して上書き。
USER_ENTEREDで書込むことで「$159.00」が通貨型として解釈され、前月と同じ表示になる。
"""

import sys
from inv_common import get_gc

sys.stdout.reconfigure(encoding='utf-8')

KEISHI = '1t_GHxn2PQY2F78Xgx9B0o602Wl0CeJSeBlA1Wo1ngME'
SASAKI = '1cKiRQIUHb2LM0p8yrxkQ4voorEkjGgprf4ox8WOrrKY'

gc = get_gc()

print('=== 1. 収支表202603からFORMATTED_VALUEで再取得 ===')
ss_kei = gc.open_by_key(KEISHI)
ws_bs = ss_kei.worksheet('収支表202603')

b_col = ws_bs.col_values(2)
last_row = max((i + 1 for i, v in enumerate(b_col) if v not in ('', None)), default=17)

raw = ws_bs.get(
    f'B17:T{last_row}',
    value_render_option='FORMATTED_VALUE',
)

# SKU列はF列 = index 4
s_rows = []
for row in raw:
    if len(row) > 4 and isinstance(row[4], str) and row[4].startswith('S'):
        padded = list(row) + [''] * (19 - len(row))
        s_rows.append(padded[:19])

print(f'  抽出件数: {len(s_rows)}')
if s_rows:
    print(f'  最初の行: {s_rows[0]}')
    print(f'  最後の行: {s_rows[-1]}')

# 件数が想定外の場合は停止
if len(s_rows) != 130:
    print(f'\n⚠️ 警告: 抽出件数が130と異なります（{len(s_rows)}件）')
    print('  既存の8531-8660の上書き範囲との不整合を確認してください')
    sys.exit(1)

print('\n=== 2. 8531〜8660 を上書き ===')
ss_sas = gc.open_by_key(SASAKI)
ws_jis = ss_sas.worksheets()[0]

end_row = 8531 + len(s_rows) - 1
ws_jis.update(
    range_name=f'B8531:T{end_row}',
    values=s_rows,
    value_input_option='USER_ENTERED',
)
print(f'  ✅ 上書き完了: B8531:T{end_row} ({len(s_rows)}行)')

print('\n=== 完了 ===')
print('画面で以下を確認:')
print('  - H列(販売価格)・I列(送料)・J列(合計)・L〜O列の手数料: $XX.XX 表示')
print('  - K列(7.00%)・T列(利益率): % 表示')
print('  - P列(仕入値)・R列(売上)・S列(利益): ¥XX,XXX 表示')
