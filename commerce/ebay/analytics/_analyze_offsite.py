"""Offsite広告 商品別レポート分析"""
import sys, csv, io
sys.stdout.reconfigure(encoding='utf-8')

file = r'C:\Users\KEISUKE SHIMOMOTO\Downloads\Campaign 12_10_2022 18_56_47_Listing_20260326.csv'
with open(file, encoding='utf-8-sig') as f:
    lines = f.readlines()

data = io.StringIO(''.join(lines[2:]))
reader = csv.DictReader(data)

def to_f(s):
    return float(s.replace('$', '').replace(',', '').strip() or '0')

total_imps = total_clicks = total_fees = total_sales = total_sold = 0
items_with_clicks = items_with_sales = items_with_imps = items_zero = total_items = 0
item_list = []

for row in reader:
    total_items += 1
    imps = int(to_f(row.get('Impressions', '0').strip()))
    clicks = int(to_f(row.get('Clicks', '0').strip()))
    fees = to_f(row.get('Ad fees', '0'))
    sales = to_f(row.get('Sales', '0'))
    sold = int(to_f(row.get('Sold quantity', '0').strip()))
    title = row.get('Title', '').strip().replace('\u200b', '')
    iid = row.get('Item ID', '').strip()

    total_imps += imps
    total_clicks += clicks
    total_fees += fees
    total_sales += sales
    total_sold += sold

    if imps > 0: items_with_imps += 1
    if clicks > 0: items_with_clicks += 1
    if sold > 0: items_with_sales += 1
    if imps == 0 and clicks == 0: items_zero += 1

    item_list.append({
        'id': iid, 'title': title, 'imps': imps,
        'clicks': clicks, 'fees': fees, 'sales': sales, 'sold': sold
    })

print('=' * 60)
print('Offsite広告 商品別レポート分析')
print('=' * 60)

print(f'\n■ 全体サマリー')
print(f'  対象商品数: {total_items}')
print(f'  インプレッションあり: {items_with_imps} ({items_with_imps/total_items*100:.1f}%)')
print(f'  クリックあり: {items_with_clicks} ({items_with_clicks/total_items*100:.1f}%)')
print(f'  売上あり: {items_with_sales} ({items_with_sales/total_items*100:.1f}%)')
print(f'  完全ゼロ: {items_zero} ({items_zero/total_items*100:.1f}%)')
print(f'  広告費合計: ${total_fees:,.2f}')
print(f'  売上合計: ${total_sales:,.2f}')

# 広告費TOP20
print(f'\n■ Offsite広告費TOP20（クリック課金で費用が高い商品）')
sorted_by_fees = sorted(item_list, key=lambda x: x['fees'], reverse=True)
for i, item in enumerate(sorted_by_fees[:20]):
    roas_str = f"{item['sales']/item['fees']:.0f}x" if item['fees'] > 0 else '-'
    print(f"  {i+1:>2}. ${item['fees']:>7.2f} | {item['clicks']:>4}cl | sold:{item['sold']} | ${item['sales']:>8.2f} | ROAS:{roas_str:>5} | {item['title'][:42]}")

# 売上あり商品
sold_items = sorted([i for i in item_list if i['sold'] > 0], key=lambda x: x['sales'], reverse=True)
print(f'\n■ Offsiteで売れた商品（全{len(sold_items)}件）')
for item in sold_items:
    roas_str = f"{item['sales']/item['fees']:.0f}x" if item['fees'] > 0 else 'FREE'
    print(f"  ${item['sales']:>8.2f} ({item['sold']}個) 費用:${item['fees']:>6.2f} ROAS:{roas_str:>6} | {item['title'][:45]}")

# 無駄（クリックあり・売上ゼロ）
wasted = sorted([i for i in item_list if i['clicks'] > 0 and i['sold'] == 0], key=lambda x: x['fees'], reverse=True)
total_wasted_fees = sum(i['fees'] for i in wasted)
total_wasted_clicks = sum(i['clicks'] for i in wasted)
print(f'\n■ 無駄なOffsite広告（クリックあり・売上ゼロ）')
print(f'  該当商品数: {len(wasted)}')
print(f'  無駄な広告費: ${total_wasted_fees:,.2f} (全体の{total_wasted_fees/total_fees*100:.1f}%)')
print(f'  無駄なクリック: {total_wasted_clicks:,}')
print(f'  TOP10:')
for item in wasted[:10]:
    print(f"    ${item['fees']:>7.2f} | {item['clicks']:>4}cl | {item['imps']:>6}imps | {item['title'][:42]}")

# インプレッションの集中度
sorted_by_imps = sorted(item_list, key=lambda x: x['imps'], reverse=True)
top50_imps = sum(i['imps'] for i in sorted_by_imps[:50])
print(f'\n■ Offsiteインプレッションの集中度')
print(f'  全体: {total_imps:,}')
print(f'  TOP50商品: {top50_imps:,} ({top50_imps/total_imps*100:.1f}%)')
print(f'  TOP50のうち売上あり: {sum(1 for i in sorted_by_imps[:50] if i["sold"]>0)}商品')
