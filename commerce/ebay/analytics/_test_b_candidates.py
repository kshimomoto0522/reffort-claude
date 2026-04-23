"""テストB候補: 生涯販売1-10・保護対象外・PLG 5%→2%テスト"""
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
sku_data = defaultdict(lambda: {
    'title': '', 'lifetime_sold': 0, 'max_watch': 0, 'qty': 0, 'price': 0, 'main_id': ''
})
for iid, c in cache.items():
    sku = c.get('sku', '').strip()
    if not sku:
        continue
    d = sku_data[sku]
    if not d['title']:
        d['title'] = c.get('title', '').replace('\u200b', '')
    ls = c.get('lifetime_sold', 0) or 0
    if ls > d['lifetime_sold']:
        d['lifetime_sold'] = ls
        d['main_id'] = iid
    w = c.get('watch', 0) or 0
    d['max_watch'] = max(d['max_watch'], w)
    d['qty'] = max(d['qty'], c.get('qty', 0) or 0)
    p = c.get('price', 0) or 0
    if p > d['price']:
        d['price'] = p

# 広告CSV（期間中の広告売上）
ads_file = r'C:\Users\KEISUKE SHIMOMOTO\Downloads\rioxxrinaxjapan_advertising_sales_report_20260315.csv'
with open(ads_file, encoding='utf-8-sig') as f:
    alines = f.readlines()
sku_ad = defaultdict(lambda: {'sales': 0, 'qty': 0, 'fee': 0})
for row in csv.DictReader(io.StringIO(''.join(alines[2:]))):
    iid = row.get('Item ID', '').strip()
    if not iid:
        continue
    sku = cache.get(iid, {}).get('sku', '').strip()
    if not sku:
        continue
    sku_ad[sku]['sales'] += to_f(row.get('Sales', '0'))
    sku_ad[sku]['qty'] += int(to_f(row.get('Sold quantity', '0')))
    sku_ad[sku]['fee'] += to_f(row.get('Ad fees (General)', '-'))

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

# テストB: 生涯販売1-10 & 保護対象外 & 在庫あり
candidates = []
for sku, d in sku_data.items():
    if sku in protected_skus:
        continue
    if d['lifetime_sold'] < 1 or d['lifetime_sold'] > 10:
        continue
    if d['qty'] < 1:
        continue
    ad = sku_ad.get(sku, {})
    off = sku_off.get(sku, {'imps': 0, 'clicks': 0})
    candidates.append({
        'sku': sku, 'title': d['title'][:55],
        'ls': d['lifetime_sold'], 'watch': d['max_watch'],
        'qty': d['qty'], 'price': d['price'],
        'ad_sales': ad.get('sales', 0), 'ad_qty': ad.get('qty', 0),
        'ad_fee': ad.get('fee', 0),
        'off_imps': off.get('imps', 0), 'off_clicks': off.get('clicks', 0),
    })

# 期間中に広告売上がある商品を優先（PLGが実際に機能しているか測れる）
has_ad_sales = sorted(
    [c for c in candidates if c['ad_qty'] > 0],
    key=lambda x: x['ad_sales'], reverse=True
)
no_ad_sales = sorted(
    [c for c in candidates if c['ad_qty'] == 0 and c['off_imps'] > 50],
    key=lambda x: x['ls'], reverse=True
)

print('=' * 85)
print('テストB: PLG 5%→2% 候補（生涯販売1-10・保護対象外）')
print('=' * 85)

print(f'\n【優先候補】期間中に広告経由で売れている（{len(has_ad_sales)}商品）')
print('→ PLGが実際に機能している商品。2%に下げても売れ続けるかが直接測れる')
print()
for i, c in enumerate(has_ad_sales[:20]):
    print(f"  {i+1:>2}. LS:{c['ls']:>2} 期間売:{c['ad_qty']}個 PLG費:${c['ad_fee']:>5.0f} W:{c['watch']:>3} qty:{c['qty']:>2} ${c['price']:>3.0f} imp:{c['off_imps']:>5} | 【{c['sku']}】{c['title']}")

print(f'\n【参考】期間中は売れてないが生涯実績あり（{len(no_ad_sales)}商品）')
print()
for i, c in enumerate(no_ad_sales[:10]):
    print(f"  {i+1:>2}. LS:{c['ls']:>2} W:{c['watch']:>3} qty:{c['qty']:>2} ${c['price']:>3.0f} imp:{c['off_imps']:>5} | 【{c['sku']}】{c['title']}")

# 価格帯分布
print(f'\n【価格帯分布（優先候補）】')
for lo, hi, lbl in [(100,149,'$100-149'), (150,199,'$150-199'), (200,249,'$200-249'), (250,999,'$250+')]:
    cnt = len([c for c in has_ad_sales if lo <= c['price'] <= hi])
    print(f'  {lbl}: {cnt}商品')
