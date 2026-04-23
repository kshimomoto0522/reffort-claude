"""
広告テスト候補 最終版
テストA: PLG停止（生涯販売ゼロの30商品）
テストB: PLP追加（実績あり・需要高い商品）
"""
import sys, csv, io, json
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

with open('ebay_seller_cache.json', encoding='utf-8') as f:
    cache = json.load(f)
with open('weekly_history.json', encoding='utf-8') as f:
    history = json.load(f)
latest = list(history.values())[0]

# 保護対象SKU
protected_skus = set()
for iid in set(latest.get('top15_ids', [])) | set(latest.get('準売れ筋_ids', [])):
    sku = cache.get(iid, {}).get('sku', '').strip()
    if sku:
        protected_skus.add(sku)

# SKU集約
sku_data = defaultdict(lambda: {
    'title': '', 'lifetime_sold': 0, 'max_watch': 0,
    'qty': 0, 'price': 0, 'ids': [],
})
for iid, c in cache.items():
    sku = c.get('sku', '').strip()
    if not sku:
        continue
    d = sku_data[sku]
    d['ids'].append(iid)
    if not d['title']:
        d['title'] = c.get('title', '').replace('\u200b', '')
    d['lifetime_sold'] = max(d['lifetime_sold'], c.get('lifetime_sold', 0) or 0)
    d['max_watch'] = max(d['max_watch'], c.get('watch', 0) or 0)
    d['qty'] = max(d['qty'], c.get('qty', 0) or 0)
    p = c.get('price', 0) or 0
    if p > d['price']:
        d['price'] = p

# Offsite（SKU単位）
off_file = r'C:\Users\KEISUKE SHIMOMOTO\Downloads\Campaign 12_10_2022 18_56_47_Listing_20260326.csv'
with open(off_file, encoding='utf-8-sig') as f:
    olines = f.readlines()

def to_f(s):
    v = s.replace('$', '').replace(',', '').strip()
    return float(v) if v and v != '-' else 0.0

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

# 広告CSV
ads_file = r'C:\Users\KEISUKE SHIMOMOTO\Downloads\rioxxrinaxjapan_advertising_sales_report_20260315.csv'
with open(ads_file, encoding='utf-8-sig') as f:
    alines = f.readlines()
sku_ad = defaultdict(lambda: {'sales': 0, 'qty': 0})
plp_skus = set()
for row in csv.DictReader(io.StringIO(''.join(alines[2:]))):
    iid = row.get('Item ID', '').strip()
    if not iid:
        continue
    sku = cache.get(iid, {}).get('sku', '').strip()
    if not sku:
        continue
    sku_ad[sku]['sales'] += to_f(row.get('Sales', '0'))
    sku_ad[sku]['qty'] += int(to_f(row.get('Sold quantity', '0')))
    if 'Priority' in row.get('Campaign strategy', ''):
        plp_skus.add(sku)

# ========================================
# テストA: PLG停止 30商品
# ========================================
plg_test = []
for sku, d in sku_data.items():
    if sku in protected_skus:
        continue
    if d['lifetime_sold'] > 0:
        continue
    ad = sku_ad.get(sku, {})
    if ad.get('qty', 0) > 0:
        continue
    off = sku_off.get(sku, {'imps': 0, 'clicks': 0})
    if off.get('imps', 0) < 100:
        continue
    plg_test.append({
        'sku': sku, 'title': d['title'],
        'watch': d['max_watch'], 'ls': d['lifetime_sold'],
        'qty': d['qty'], 'price': d['price'],
        'off_imps': off['imps'], 'off_clicks': off['clicks'],
    })
plg_test.sort(key=lambda x: x['off_imps'], reverse=True)
plg_30 = plg_test[:30]

print('=' * 85)
print('テストA: PLG停止 30商品（3/26→4/9 2週間）')
print('=' * 85)
print('全商品が生涯販売ゼロ。PLGを止めても売上リスクなし。')
print('目的: PLGを止めたらインプレッション/クリックがどう変わるか測定')
print()
for i, c in enumerate(plg_30):
    t = c['title'][:52]
    print(f"{i+1:>2}. imp:{c['off_imps']:>5} cl:{c['off_clicks']:>3} W:{c['watch']:>2} qty:{c['qty']:>2} ${c['price']:>6.0f} | 【{c['sku']}】{t}")

# ========================================
# テストB: PLP追加候補
# ========================================
plp_test = []
for sku, d in sku_data.items():
    if sku in plp_skus:
        continue
    if d['lifetime_sold'] < 5:
        continue
    if d['qty'] < 2:
        continue
    if d['max_watch'] < 20:
        continue
    off = sku_off.get(sku, {})
    ad = sku_ad.get(sku, {})
    is_prot = sku in protected_skus
    plp_test.append({
        'sku': sku, 'title': d['title'],
        'watch': d['max_watch'], 'ls': d['lifetime_sold'],
        'qty': d['qty'], 'price': d['price'],
        'off_imps': off.get('imps', 0), 'off_clicks': off.get('clicks', 0),
        'ad_sales': ad.get('sales', 0), 'ad_qty': ad.get('qty', 0),
        'protected': is_prot,
    })
# 生涯販売 × ウォッチで需要の強さをスコアリング
plp_test.sort(key=lambda x: x['ls'] * x['watch'], reverse=True)

print()
print('=' * 85)
print('テストB: PLP追加候補（3/26→4/9 2週間）')
print('=' * 85)
print('選定基準: 生涯販売5個+, ウォッチ20+, 在庫2+, PLP未適用')
print('PLP = 検索トップ枠を取れる → 競争激しい人気商品に効果大')
print()
for i, c in enumerate(plp_test[:20]):
    prot = '★' if c['protected'] else ' '
    t = c['title'][:50]
    print(f"{i+1:>2}.{prot} LS:{c['ls']:>3} W:{c['watch']:>3} qty:{c['qty']:>2} ${c['price']:>6.0f} 期間売:{c['ad_qty']:>2}個 imp:{c['off_imps']:>5} | 【{c['sku']}】{t}")

print()
print('★ = 現在TOP15または準売れ筋')
print()
print('広告担当の推奨: 上位5〜6商品にPLPを適用。日予算$3〜5で開始。')
