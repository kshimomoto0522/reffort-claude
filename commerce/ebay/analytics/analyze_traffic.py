import csv, io, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

file = r"C:\Users\KEISUKE SHIMOMOTO\Downloads\eBay-ListingsTrafficReport-Mar-15-2026-21_56_24-0700-13288691549.csv"
ads_file = r"C:\Users\KEISUKE SHIMOMOTO\Downloads\rioxxrinaxjapan_advertising_sales_report_20260315.csv"
OUTPUT = r"C:\Users\KEISUKE SHIMOMOTO\Desktop\reffort\commerce\ebay\analytics\result_traffic.txt"

with open(file, encoding='utf-8-sig') as f:
    lines = f.readlines()

# Line6（index=5）がヘッダー行
data = io.StringIO(''.join(lines[5:]))
rows = list(csv.DictReader(data))

def to_float(s):
    try:
        return float(str(s).replace(',','').replace('%','').strip())
    except:
        return 0.0

def clean(s):
    return ''.join(c for c in str(s) if c.isprintable() and c not in '\u200b\u200c\u200d\ufeff\u2022')

total_listings = len(rows)
total_impressions = 0
total_pageviews = 0
total_sold = 0
zero_sold = 0
zero_impressions = 0

# 商品別データ収集
items = []
for row in rows:
    title = clean(row.get('Listing title',''))
    item_id = row.get('eBay item ID','').strip().replace('=','').replace('"','').strip()
    impressions = to_float(row.get('Total impressions', 0))
    pageviews = to_float(row.get('Total page views', 0))
    sold = to_float(row.get('Quantity sold', 0))
    ctr_str = row.get('Click-through rate = Page views from eBay site/Total impressions','').strip().replace('%','')
    cvr_str = row.get('Sales conversion rate = Quantity sold/Total page views','').strip().replace('%','')
    qty_avail = to_float(row.get('Quantity available', 0))
    pl_status = clean(row.get('Current promoted listings status',''))

    try:
        ctr = float(ctr_str)
    except:
        ctr = 0.0
    try:
        cvr = float(cvr_str)
    except:
        cvr = 0.0

    total_impressions += impressions
    total_pageviews += pageviews
    total_sold += sold

    if sold == 0:
        zero_sold += 1
    if impressions == 0:
        zero_impressions += 1

    items.append({
        'title': title,
        'item_id': item_id,
        'impressions': impressions,
        'pageviews': pageviews,
        'sold': sold,
        'ctr': ctr,
        'cvr': cvr,
        'qty_avail': qty_avail,
        'pl_status': pl_status,
    })

# 全体CVR・CTR
overall_ctr = (total_pageviews / total_impressions * 100) if total_impressions > 0 else 0
overall_cvr = (total_sold / total_pageviews * 100) if total_pageviews > 0 else 0

# 売れ筋TOP15（販売数ベース）
top_sold = sorted(items, key=lambda x: -x['sold'])[:15]

# ゼロ売上ワースト15（インプレッション多いのに売れていない）
wasted = [i for i in items if i['sold'] == 0 and i['impressions'] > 500]
wasted_sorted = sorted(wasted, key=lambda x: -x['impressions'])[:15]

# インプレッションあるのに超低CVR（育成候補）
育成 = [i for i in items if i['sold'] > 0 and i['cvr'] < 1.0 and i['impressions'] > 1000]
育成_sorted = sorted(育成, key=lambda x: -x['impressions'])[:10]

lines_out = []
lines_out.append("=" * 60)
lines_out.append("  Traffic Report サマリー（USサイト推定）")
lines_out.append("  期間: 〜2026年3月15日")
lines_out.append("=" * 60)
lines_out.append(f"  総出品数:              {total_listings:,}件")
lines_out.append(f"  売上ゼロ商品:          {zero_sold:,}件 ({zero_sold/total_listings*100:.1f}%)")
lines_out.append(f"  インプレッションゼロ:  {zero_impressions:,}件 ({zero_impressions/total_listings*100:.1f}%)")
lines_out.append("")
lines_out.append(f"  総インプレッション:    {total_impressions:,.0f}")
lines_out.append(f"  総ページビュー:        {total_pageviews:,.0f}")
lines_out.append(f"  総販売数:              {total_sold:,.0f}個")
lines_out.append("")
lines_out.append(f"  全体CTR（表示→閲覧）: {overall_ctr:.2f}%")
lines_out.append(f"  全体CVR（閲覧→購入）: {overall_cvr:.2f}%")
lines_out.append("")

lines_out.append("=" * 60)
lines_out.append("  売れ筋TOP15（販売数ベース）")
lines_out.append("=" * 60)
for rank, item in enumerate(top_sold, 1):
    lines_out.append(f"  {rank:2}. {item['title'][:52]}")
    lines_out.append(f"      販売:{item['sold']:.0f}件 | CVR:{item['cvr']:.1f}% | 閲覧:{item['pageviews']:,.0f} | 在庫:{item['qty_avail']:.0f}")
lines_out.append("")

lines_out.append("=" * 60)
lines_out.append("  【削除候補】インプレッション500超なのに売上ゼロ TOP15")
lines_out.append("  → 見られているのに買われていない = 価格・品質・競合問題")
lines_out.append("=" * 60)
for rank, item in enumerate(wasted_sorted, 1):
    lines_out.append(f"  {rank:2}. {item['title'][:52]}")
    lines_out.append(f"      表示:{item['impressions']:,.0f} | 閲覧:{item['pageviews']:,.0f} | CTR:{item['ctr']:.1f}% | 在庫:{item['qty_avail']:.0f}")
lines_out.append("")

lines_out.append("=" * 60)
lines_out.append("  【育成候補】売れているがCVR1%未満・インプレッション1000超 TOP10")
lines_out.append("  → 少し改善で伸びる可能性あり")
lines_out.append("=" * 60)
for rank, item in enumerate(育成_sorted, 1):
    lines_out.append(f"  {rank:2}. {item['title'][:52]}")
    lines_out.append(f"      販売:{item['sold']:.0f}件 | CVR:{item['cvr']:.2f}% | 閲覧:{item['pageviews']:,.0f}")
lines_out.append("")

# ===== Advertising Report: 商品別売上・広告費を集計 =====
with open(ads_file, encoding='utf-8-sig') as f:
    ads_lines = f.readlines()
ads_data = io.StringIO(''.join(ads_lines[2:]))
ads_reader = csv.DictReader(ads_data)

# item_id → {plg_sales, plg_fee, plp_sales, offsite_sales}
ad_by_item = defaultdict(lambda: {'plg_s':0,'plg_fee':0,'plp_s':0,'off_s':0,'plg_n':0,'plp_n':0,'off_n':0})

def to_f2(s):
    try: return float(str(s).replace('$','').replace(',','').strip())
    except: return 0.0

for row in ads_reader:
    item_id = row.get('Item ID','').strip()
    ad = row.get('Ad type','')
    st = row.get('Campaign strategy','')
    sale_type = row.get('Sale type','')
    s = to_f2(row.get('Sales','0'))
    fee = to_f2(row.get('Ad fees (General)','-'))

    if 'Offsite' in ad:
        ad_by_item[item_id]['off_s'] += s
        ad_by_item[item_id]['off_n'] += 1
    elif 'Priority' in st:
        ad_by_item[item_id]['plp_s'] += s
        ad_by_item[item_id]['plp_n'] += 1
    elif 'General' in st and sale_type != 'Halo item sale':
        ad_by_item[item_id]['plg_s'] += s
        ad_by_item[item_id]['plg_fee'] += fee
        ad_by_item[item_id]['plg_n'] += 1

# itemsにad情報をマージ
for item in items:
    iid = item['item_id']
    ad = ad_by_item.get(iid, {})
    item['plg_s'] = ad.get('plg_s', 0)
    item['plg_fee'] = ad.get('plg_fee', 0)
    item['plp_s'] = ad.get('plp_s', 0)
    item['off_s'] = ad.get('off_s', 0)
    item['ad_sales'] = item['plg_s'] + item['plp_s'] + item['off_s']

# ===== 完全死蔵（インプ・PV・売上 全ゼロ）=====
dead = [i for i in items if i['impressions'] == 0 and i['pageviews'] == 0 and i['sold'] == 0]

# ===== 出力 =====
lines_out = []
lines_out.append("=" * 65)
lines_out.append("  Traffic × Advertising 統合レポート（2/13〜3/15）")
lines_out.append("=" * 65)
lines_out.append(f"  総出品数:                  {total_listings:,}件")
lines_out.append(f"  売上ゼロ商品:              {zero_sold:,}件 ({zero_sold/total_listings*100:.1f}%)")
lines_out.append(f"  完全死蔵（インプ・PVゼロ）: {len(dead):,}件 ({len(dead)/total_listings*100:.1f}%)")
lines_out.append(f"  インプレッション合計:      {total_impressions:,.0f}")
lines_out.append(f"  ページビュー合計:          {total_pageviews:,.0f}")
lines_out.append(f"  販売数合計:                {total_sold:.0f}件")
lines_out.append(f"  全体CTR（表示→閲覧）:      {overall_ctr:.3f}%")
lines_out.append(f"  全体CVR（閲覧→購入）:      {overall_cvr:.3f}%")
lines_out.append("")

lines_out.append("=" * 65)
lines_out.append("  🔥 売れ筋TOP15（販売数ベース）")
lines_out.append("=" * 65)
for rank, item in enumerate(top_sold, 1):
    ad_s = item['ad_sales']
    ad_s_str = f"${ad_s:,.0f}" if ad_s > 0 else "-"
    lines_out.append(f"  {rank:2}. {item['title']}")
    lines_out.append(f"      ID:{item['item_id']} | 売:{item['sold']:.0f}件 | CVR:{item['cvr']:.1f}% | PV:{item['pageviews']:,.0f} | Imp:{item['impressions']:,.0f} | 広告売:{ad_s_str}")
lines_out.append("")

lines_out.append("=" * 65)
lines_out.append("  🌱 育成候補：PVあり・売上ゼロ TOP20（価格・サイズ・競合確認）")
lines_out.append("  → 需要はある。何かが購入を妨げている")
lines_out.append("=" * 65)
育成 = sorted([i for i in items if i['sold'] == 0 and i['pageviews'] >= 20], key=lambda x: -x['pageviews'])[:20]
for rank, item in enumerate(育成, 1):
    lines_out.append(f"  {rank:2}. {item['title']}")
    lines_out.append(f"      ID:{item['item_id']} | PV:{item['pageviews']:,.0f} | Imp:{item['impressions']:,.0f} | 在庫:{item['qty_avail']:.0f}")
lines_out.append("")

lines_out.append("=" * 65)
lines_out.append(f"  🗑 完全死蔵リスト（{len(dead)}件）インプ・PV・売上すべてゼロ → 削除推奨")
lines_out.append("=" * 65)
for item in dead:
    lines_out.append(f"  ID:{item['item_id']}")
    lines_out.append(f"  {item['title']}")
lines_out.append("")

result = '\n'.join(lines_out)
with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(result)

print(result)
print(f"\n=> {OUTPUT} に保存しました")
