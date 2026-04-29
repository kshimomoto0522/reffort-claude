"""2026年3月分の修正リペアスクリプト

修正内容:
  1. 3請求書の AC:AP の列幅を O:AB と同じに揃える
  2. 佐々木実績管理表 8530行（集計行）の書式を 8373行から書式コピー
  3. 佐々木実績管理表 8531-8660行（明細）の書式を 8374行から書式コピー（繰り返し）
  4. 佐々木実績管理表 8531-8660 の U列をクリア（収支表の還付金が誤って入っているため）
"""

import sys
import time
from inv_common import get_gc, copy_column_widths, copy_format

sys.stdout.reconfigure(encoding='utf-8')

KEISHI = '1t_GHxn2PQY2F78Xgx9B0o602Wl0CeJSeBlA1Wo1ngME'
SASAKI = '1cKiRQIUHb2LM0p8yrxkQ4voorEkjGgprf4ox8WOrrKY'

gc = get_gc()


def section(t):
    print('\n' + '=' * 70)
    print(t)
    print('=' * 70)


# ===== 1. 3請求書の列幅修正 =====
section('1. 3請求書 AC:AP 列幅修正（O:AB 列幅をコピー）')

ss_kei = gc.open_by_key(KEISHI)
sheets = ['本間請求書（2026）', '清水請求書（2026）', '佐々木請求書（2026）']
for sheet_name in sheets:
    ws = ss_kei.worksheet(sheet_name)
    # O:AB = column index 14-27 (0-indexed)
    # AC:AP = column index 28-41
    copy_column_widths(ss_kei, ws.id,
                       src_col_start_idx=14,
                       dst_col_start_idx=28,
                       count=14)
    print(f'  ✅ {sheet_name}: O:AB → AC:AP 列幅コピー完了')
    time.sleep(1)  # APIレートリミット対策


# ===== 2. 佐々木実績管理表 書式コピー =====
section('2. 佐々木実績管理表 書式コピー')

ss_sas = gc.open_by_key(SASAKI)
ws_jis = ss_sas.worksheets()[0]

# 集計行 8373 → 8530 (A:V = column 0-21, 22列)
copy_format(ss_sas, ws_jis.id,
            src_row_start_idx=8372, src_row_end_idx=8373,  # 8373行目（1-indexed）
            src_col_start_idx=0, src_col_end_idx=22,
            dst_row_start_idx=8529, dst_row_end_idx=8530,
            dst_col_start_idx=0, dst_col_end_idx=22)
print('  ✅ 集計行 8373 → 8530 書式コピー完了')
time.sleep(1)

# 明細1行目 8374 → 明細N行 8531-8660 (繰り返し)
copy_format(ss_sas, ws_jis.id,
            src_row_start_idx=8373, src_row_end_idx=8374,
            src_col_start_idx=0, src_col_end_idx=22,
            dst_row_start_idx=8530, dst_row_end_idx=8660,  # 8531-8660 = index 8530-8659+1
            dst_col_start_idx=0, dst_col_end_idx=22)
print('  ✅ 明細 8374 → 8531-8660 書式コピー完了')
time.sleep(1)


# ===== 3. U列クリア（不要な還付金データ削除） =====
section('3. 佐々木実績管理表 U8531:U8660 クリア')

ws_jis.batch_clear(['U8531:U8660'])
print('  ✅ U8531:U8660 クリア完了')


print('\n=== すべての修正完了 ===')
print('画面で確認してください:')
print('  - 3請求書（収支表KeiS 2026）AC:AP の列幅')
print('  - 【佐々木さん】実績管理表 8530行(集計行)・8531-8660行(明細)の書式')
print('  - 【佐々木さん】実績管理表 U8531-U8660 が空白')
