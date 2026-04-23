"""
広告最適化アクションリスト作成
- 週次レポートのデータ（Traffic API + GetOrders API）
- Offsiteリスティングレポート
を突合して以下を出力:
1. 削除候補 × Offsiteクリック浪費リスト（即削除推奨）
2. PLGインクリメンタリティテスト対象リスト（売上ゼロ・PLG停止候補）
"""
import sys, csv, io, json, os
sys.stdout.reconfigure(encoding='utf-8')

# ===== Offsiteレポート読み込み =====
offsite_file = r'C:\Users\KEISUKE SHIMOMOTO\Downloads\Campaign 12_10_2022 18_56_47_Listing_20260326.csv'
with open(offsite_file, encoding='utf-8-sig') as f:
    lines = f.readlines()
data = io.StringIO(''.join(lines[2:]))
reader = csv.DictReader(data)

def to_f(s):
    v = s.replace('$', '').replace(',', '').strip()
    if not v or v == '-':
        return 0.0
    return float(v)

offsite_data = {}  # item_id -> {clicks, imps, sold, sales}
for row in reader:
    # ヘッダーにスペースが入っている場合があるので、全キーをstrip
    row = {k.strip(): v for k, v in row.items()}
    iid = row.get('Item ID', '').strip()
    if not iid:
        continue
    imps = int(to_f(row.get('Impressions', '0')))
    clicks = int(to_f(row.get('Clicks', '0')))
    sold = int(to_f(row.get('Sold quantity', '0')))
    sales = to_f(row.get('Sales', '0'))
    offsite_data[iid] = {'clicks': clicks, 'imps': imps, 'sold': sold, 'sales': sales}

print(f'Offsiteレポート: {len(offsite_data)}商品読み込み')

# ===== Advertising Sales Report 読み込み =====
ads_file = r'C:\Users\KEISUKE SHIMOMOTO\Downloads\rioxxrinaxjapan_advertising_sales_report_20260315.csv'
from collections import defaultdict
ad_by_item = defaultdict(lambda: {'plg_s': 0, 'plg_f': 0, 'plp_s': 0})
with open(ads_file, encoding='utf-8-sig') as f:
    ads_lines = f.readlines()
ads_data = io.StringIO(''.join(ads_lines[2:]))
for row in csv.DictReader(ads_data):
    iid = row.get('Item ID', '').strip()
    if not iid:
        continue
    st = row.get('Campaign strategy', '')
    sale_type = row.get('Sale type', '')
    s = to_f(row.get('Sales', '0'))
    fee = to_f(row.get('Ad fees (General)', '-'))
    if 'Priority' in st:
        ad_by_item[iid]['plp_s'] += s
    elif 'General' in st and 'Halo' not in sale_type:
        ad_by_item[iid]['plg_s'] += s
        ad_by_item[iid]['plg_f'] += fee

print(f'広告CSV: {len(ad_by_item)}商品読み込み')

# ===== seller_cache読み込み（ウォッチ数・生涯販売数・在庫数） =====
cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ebay_seller_cache.json')
seller_cache = {}
if os.path.exists(cache_file):
    with open(cache_file, encoding='utf-8') as f:
        seller_cache = json.load(f)
    print(f'seller_cache: {len(seller_cache)}商品読み込み')

# ===== weekly_history読み込み（TOP15・準売れ筋リスト） =====
history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weekly_history.json')
with open(history_file, encoding='utf-8') as f:
    history = json.load(f)
latest = list(history.values())[0]  # 最新データ
top15_ids = set(latest.get('top15_ids', []))
junureshji_ids = set(latest.get('準売れ筋_ids', []))
protected_ids = top15_ids | junureshji_ids  # これらは触らない

print(f'保護対象: TOP15={len(top15_ids)} 準売れ筋={len(junureshji_ids)} 合計={len(protected_ids)}')

# ===== 分析・リスト作成 =====

# カテゴリ1: 即削除推奨（Offsiteクリック浪費 × 削除候補条件）
# 条件: 売上ゼロ + Offsiteクリックあり + 保護対象外
delete_candidates = []
plg_test_candidates = []

for iid, od in offsite_data.items():
    cache = seller_cache.get(iid, {})
    watch = cache.get('watch', 0)
    lifetime_sold = cache.get('sold', 0)
    qty = cache.get('qty', 0)
    title = cache.get('title', '')[:60]
    start_date = cache.get('start', '')

    ad = ad_by_item.get(iid, {})
    plg_fee = ad.get('plg_f', 0)
    plg_sales = ad.get('plg_s', 0)

    # 保護対象はスキップ
    if iid in protected_ids:
        continue

    # 売上ゼロの商品
    if od['sold'] == 0 and plg_sales == 0:
        item_info = {
            'id': iid, 'title': title,
            'off_clicks': od['clicks'], 'off_imps': od['imps'],
            'plg_fee': plg_fee,
            'watch': watch, 'lifetime_sold': lifetime_sold, 'qty': qty,
            'start': start_date,
        }

        # 削除候補条件: ウォッチ10以下 & 生涯販売0
        if watch <= 10 and lifetime_sold == 0 and od['clicks'] > 0:
            delete_candidates.append(item_info)

        # PLGテスト候補: Offsiteインプレッションがあるがどこでも売れてない
        if od['imps'] > 0:
            plg_test_candidates.append(item_info)

# ソート
delete_candidates.sort(key=lambda x: x['off_clicks'], reverse=True)
plg_test_candidates.sort(key=lambda x: x['off_imps'], reverse=True)

# ===== 出力 =====
print()
print('=' * 70)
print('1. 即削除推奨リスト（Offsiteクリック浪費 × 売上ゼロ × ウォッチ低）')
print('=' * 70)
print(f'該当: {len(delete_candidates)}商品')
print(f'このグループのPLG広告費合計: ${sum(d["plg_fee"] for d in delete_candidates):,.0f}')
print()
for i, d in enumerate(delete_candidates[:30]):
    print(f'{i+1:>3}. [{d["id"]}] OFFcl:{d["off_clicks"]:>3} OFFimp:{d["off_imps"]:>5} PLG費:${d["plg_fee"]:>5.0f} W:{d["watch"]:>2} LS:{d["lifetime_sold"]} | {d["title"]}')

print()
print('=' * 70)
print('2. PLG停止テスト候補（売上ゼロ × インプレッションあり × 保護対象外）')
print('=' * 70)
print(f'該当: {len(plg_test_candidates)}商品')
print(f'このグループのPLG広告費合計: ${sum(d["plg_fee"] for d in plg_test_candidates):,.0f}')
print()
print('上位30（インプレッション順）:')
for i, d in enumerate(plg_test_candidates[:30]):
    print(f'{i+1:>3}. [{d["id"]}] OFFimp:{d["off_imps"]:>6} OFFcl:{d["off_clicks"]:>3} PLG費:${d["plg_fee"]:>5.0f} W:{d["watch"]:>2} LS:{d["lifetime_sold"]} | {d["title"]}')

# サマリー
print()
print('=' * 70)
print('サマリー')
print('=' * 70)
print(f'全Offsite対象商品: {len(offsite_data)}')
print(f'保護対象(TOP15+準売れ筋): {len(protected_ids)} → 触らない')
print(f'即削除推奨: {len(delete_candidates)}商品')
print(f'  → PLG広告費節約: ${sum(d["plg_fee"] for d in delete_candidates):,.0f}/期間')
print(f'  → Offsiteクリック解放: {sum(d["off_clicks"] for d in delete_candidates):,}クリック分')
print(f'PLG停止テスト候補: {len(plg_test_candidates)}商品')
print(f'  → 現在のPLG広告費: ${sum(d["plg_fee"] for d in plg_test_candidates):,.0f}/期間')
