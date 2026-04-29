"""3月明細の値を、前月8374と同じ「列ごとの型」で再書込み。

列ごとのルール（B=0始まり）:
  D(2): 日付（USER_ENTERED解釈）
  H,I,J,L,M,N,O (6,7,8,10,11,12,13): USD文字列「$XX.XX」のまま
  K(9), T(18): %は数値化（0.07形式）
  P,Q,R,S (14,15,16,17): ¥/カンマ除去して数値化（SUM対象のため必須）
  その他: そのまま
"""

import sys
from inv_common import get_gc

sys.stdout.reconfigure(encoding='utf-8')

KEISHI = '1t_GHxn2PQY2F78Xgx9B0o602Wl0CeJSeBlA1Wo1ngME'
SASAKI = '1cKiRQIUHb2LM0p8yrxkQ4voorEkjGgprf4ox8WOrrKY'

USD_COL_INDICES = {6, 7, 8, 10, 11, 12, 13}     # H, I, J, L, M, N, O
PCT_COL_INDICES = {9, 18}                       # K, T
JPY_COL_INDICES = {14, 15, 16, 17}              # P, Q, R, S


def transform(col_idx, value):
    """前月の値型に合わせて変換"""
    if value is None or value == '':
        return ''
    s = str(value).strip()
    if not s:
        return ''
    if col_idx in USD_COL_INDICES:
        # 文字列のまま（前月と同じ）
        return s
    if col_idx in PCT_COL_INDICES:
        if s.endswith('%'):
            try:
                return float(s[:-1].replace(',', '')) / 100
            except ValueError:
                return s
        return s
    if col_idx in JPY_COL_INDICES:
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


gc = get_gc()

print('=== 1. 収支表202603 から FORMATTED_VALUE で再取得 ===')
ss_kei = gc.open_by_key(KEISHI)
ws_bs = ss_kei.worksheet('収支表202603')

b_col = ws_bs.col_values(2)
last_row = max((i + 1 for i, v in enumerate(b_col) if v not in ('', None)), default=17)
raw = ws_bs.get(f'B17:T{last_row}', value_render_option='FORMATTED_VALUE')

s_rows_raw = []
for row in raw:
    if len(row) > 4 and isinstance(row[4], str) and row[4].startswith('S'):
        padded = list(row) + [''] * (19 - len(row))
        s_rows_raw.append(padded[:19])

print(f'  抽出件数: {len(s_rows_raw)}')

# 列ごとに型変換
s_rows_typed = []
for row in s_rows_raw:
    typed = [transform(i, v) for i, v in enumerate(row)]
    s_rows_typed.append(typed)

print(f'  最初の行（変換後）:')
cols = list('BCDEFGHIJKLMNOPQRST')
for c, v in zip(cols, s_rows_typed[0]):
    print(f'    {c}: {v!r}')

if len(s_rows_typed) != 130:
    print(f'\n⚠️ 件数が130と異なります: {len(s_rows_typed)}')
    sys.exit(1)

print('\n=== 2. 8531〜8660 を上書き ===')
ss_sas = gc.open_by_key(SASAKI)
ws_jis = ss_sas.worksheets()[0]

end_row = 8531 + len(s_rows_typed) - 1
ws_jis.update(
    range_name=f'B8531:T{end_row}',
    values=s_rows_typed,
    value_input_option='USER_ENTERED',
)
print(f'  ✅ 上書き完了: B8531:T{end_row}')

print('\n=== 3. 集計行確認 ===')
sm = ws_jis.get('B8530:U8530', value_render_option='FORMATTED_VALUE')[0]
for c, v in zip(list('BCDEFGHIJKLMNOPQRSTU'), sm):
    if v:
        print(f'  {c}8530: {v!r}')

i3 = ws_jis.acell('I3', value_render_option='FORMATTED_VALUE').value
print(f'\n  I3 粗利累計: {i3}')

print('\n=== 完了 ===')
