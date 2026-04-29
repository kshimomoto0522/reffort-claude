"""書込後検証：3シートの主要セルを読み取って結果を確認"""

import sys
from inv_common import get_gc, fmt_money

sys.stdout.reconfigure(encoding='utf-8')

KEISHI = '1t_GHxn2PQY2F78Xgx9B0o602Wl0CeJSeBlA1Wo1ngME'
SASAKI = '1cKiRQIUHb2LM0p8yrxkQ4voorEkjGgprf4ox8WOrrKY'

gc = get_gc()


def section(t):
    print('\n' + '=' * 70)
    print(t)
    print('=' * 70)


# 本間
section('本間請求書（2026） / 3月分（AC:AP）')
ws = gc.open_by_key(KEISHI).worksheet('本間請求書（2026）')
for cell in ['AD8', 'AP5', 'AK15', 'AK11']:
    v = ws.acell(cell, value_render_option='FORMATTED_VALUE').value
    print(f'  {cell}: {v!r}')


# 清水
section('清水請求書（2026） / 3月分（AC:AP）')
ws = gc.open_by_key(KEISHI).worksheet('清水請求書（2026）')
for cell in ['AD8', 'AP5', 'AK15', 'AK11']:
    v = ws.acell(cell, value_render_option='FORMATTED_VALUE').value
    print(f'  {cell}: {v!r}')


# 佐々木請求書
section('佐々木請求書（2026） / 3月分（AC:AP）')
ws = gc.open_by_key(KEISHI).worksheet('佐々木請求書（2026）')
for cell in ['AD8', 'AP5', 'AK15', 'AK16', 'AK17', 'AN17', 'AK18', 'AK11']:
    v = ws.acell(cell, value_render_option='FORMATTED_VALUE').value
    print(f'  {cell}: {v!r}')


# 佐々木実績管理表 8530集計行
section('【佐々木さん】実績管理表 / 8530行（3月集計行）')
ws = gc.open_by_key(SASAKI).worksheets()[0]
row_v = ws.get('A8530:V8530', value_render_option='FORMATTED_VALUE')[0]
row_f = ws.get('A8530:V8530', value_render_option='FORMULA')[0]
for i, (v, f) in enumerate(zip(row_v, row_f)):
    if v or f:
        col = chr(65 + i) if i < 26 else 'A' + chr(65 + i - 26)
        print(f'  {col}8530: 値={v!r}, 式={f!r}')


# 累計セル G3 / I3 / J3
section('【佐々木さん】実績管理表 / 上部累計（G3/I3/J3）')
for cell in ['G3', 'I3', 'J3']:
    v = ws.acell(cell, value_render_option='FORMATTED_VALUE').value
    f = ws.acell(cell, value_render_option='FORMULA').value
    print(f'  {cell}: 値={v!r}')
    if f and len(f) > 200:
        print(f'      式: ...(末尾) {f[-80:]!r}')
    else:
        print(f'      式: {f!r}')


# 明細範囲の先頭・末尾チェック
section('【佐々木さん】実績管理表 / 明細範囲の先頭(8531)と末尾(8660)・予備(8661)')
for r in [8531, 8660, 8661]:
    row = ws.row_values(r)
    print(f'  R{r}: {row[:8]}')


print('\n=== 検証完了 ===')
