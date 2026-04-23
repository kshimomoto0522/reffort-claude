"""テストA: PLG停止候補を価格帯で2グループに分割"""
import sys, csv, io, json
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

with open('ebay_seller_cache.json', encoding='utf-8') as f:
    cache = json.load(f)
with open('weekly_history.json', encoding='utf-8') as f:
    history = json.load(f)
latest = list(history.values())[0]

protected_skus = set()
for iid in set(latest.get('top15_ids', [])) | set(latest.get('準売れ筋_ids', [])):
    sku = cache.get(iid, {}).get('sku', '').strip()
    if sku:
        protected_skus.add(sku)

def to_f(s):
    v = s.replace('$', '').replace(',', '').strip()
    return float(v) if v and v != '-' else 0.0

# SKU集約
sku_data = defaultdict(lambda: {'title': '', 'lifetime_sold': 0, 'max_watch': 0, 'qty': 0, 'price': 0})
for iid, c in cache.items():
    sku = c.get('sku', '').strip()
    if not sku:
        continue
    d = sku_data[sku]
    if not d['title']:
        d['title'] = c.get('title', '').replace('\u200b', '')
    d['lifetime_sold'] = max(d['lifetime_sold'], c.get('lifetime_sold', 0) or 0)
    d['max_watch'] = max(d['max_watch'], c.get('watch', 0) or 0)
    d['qty'] = max(d['qty'], c.get('qty', 0) or 0)
    p = c.get('price', 0) or 0
    if p > d['price']:
        d['price'] = p

# 広告CSV
ads_file = r'C:\Users\KEISUKE SHIMOMOTO\Downloads\rioxxrinaxjapan_advertising_sales_report_20260315.csv'
with open(ads_file, encoding='utf-8-sig') as f:
    alines = f.readlines()
sku_ad = defaultdict(lambda: {'qty': 0})
for row in csv.DictReader(io.StringIO(''.join(alines[2:]))):
    iid = row.get('Item ID', '').strip()
    if not iid:
        continue
    sku = cache.get(iid, {}).get('sku', '').strip()
    if not sku:
        continue
    sku_ad[sku]['qty'] += int(to_f(row.get('Sold quantity', '0')))

# Offsite
off_file = r'C:\Users\KEISUKE SHIMOMOTO\Downloads\Campaign 12_10_2022 18_56_47_Listing_20260326.csv'
with open(off_file, encoding='utf-8-sig') as f:
    olines = f.readlines()
sku_off = defaultdict(lambda: {'imps': 0, 'clicks': 0})
for row in csv.DictReader(io.StringIO(''.join(olines[2:]))):
    row = {k.strip(): v for k, v in row.items()}
    iid = row.get('Item ID', '').strip()
    if not iid:
        continue
    sku = cache.get(iid, {}).get('sku', '').strip()
    if not sku:
        continue
    imps = int(to_f(row.get('Impressions', '0')))
    sku_off[sku]['imps'] = max(sku_off[sku]['imps'], imps)
    sku_off[sku]['clicks'] += int(to_f(row.get('Clicks', '0')))

# 共通条件: 生涯販売ゼロ & 期間売上ゼロ & 保護対象外
def get_candidates(price_lo, price_hi, min_imps):
    result = []
    for sku, d in sku_data.items():
        if sku in protected_skus:
            continue
        if d['lifetime_sold'] > 0:
            continue
        if sku_ad.get(sku, {}).get('qty', 0) > 0:
            continue
        if d['price'] < price_lo or d['price'] > price_hi:
            continue
        off = sku_off.get(sku, {'imps': 0, 'clicks': 0})
        if off.get('imps', 0) < min_imps:
            continue
        result.append({
            'sku': sku, 'title': d['title'][:55],
            'watch': d['max_watch'], 'qty': d['qty'], 'price': d['price'],
            'off_imps': off.get('imps', 0), 'off_clicks': off.get('clicks', 0),
        })
    result.sort(key=lambda x: x['off_imps'], reverse=True)
    return result

high = get_candidates(200, 9999, 100)
mid = get_candidates(150, 199, 50)

print('=' * 85)
print('テストA: PLG停止 30商品（3/26 → 4/9 2週間）')
print('=' * 85)

print(f'\n【グループ1】$200超・生涯販売ゼロ — 15商品（候補{len(high)}から選定）')
print()
for i, c in enumerate(high[:15]):
    print(f"  {i+1:>2}. ${c['price']:>3.0f} imp:{c['off_imps']:>5} cl:{c['off_clicks']:>3} W:{c['watch']:>2} qty:{c['qty']:>2} | 【{c['sku']}】{c['title']}")

print(f'\n【グループ2】$150-199・生涯販売ゼロ — 15商品（候補{len(mid)}から選定）')
print()
for i, c in enumerate(mid[:15]):
    print(f"  {i+1:>2}. ${c['price']:>3.0f} imp:{c['off_imps']:>5} cl:{c['off_clicks']:>3} W:{c['watch']:>2} qty:{c['qty']:>2} | 【{c['sku']}】{c['title']}")
