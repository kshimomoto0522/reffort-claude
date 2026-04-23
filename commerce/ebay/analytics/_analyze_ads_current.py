"""
eBay広告 現状分析スクリプト（一時的な分析用）
2/13〜3/15のAdvertising Sales Report CSVを分析
"""
import csv, io
from collections import defaultdict

file = r'C:\Users\KEISUKE SHIMOMOTO\Downloads\rioxxrinaxjapan_advertising_sales_report_20260315.csv'
with open(file, encoding='utf-8-sig') as f:
    lines = f.readlines()

data = io.StringIO(''.join(lines[2:]))
reader = csv.DictReader(data)

# 全体集計
plg_sales = plg_fees = plg_count = 0
plp_sales = plp_count = 0
off_sales = off_count = 0
halo_sales = halo_count = 0

# 商品別集計
items = defaultdict(lambda: {
    'title': '', 'plg_s': 0, 'plg_f': 0, 'plg_n': 0,
    'plp_s': 0, 'plp_n': 0, 'off_s': 0, 'off_n': 0,
    'halo_s': 0, 'total_s': 0
})

for row in reader:
    iid = row.get('Item ID', '').strip()
    title = row.get('Item title', '').strip()
    ad = row.get('Ad type', '')
    st = row.get('Campaign strategy', '')
    sale_type = row.get('Sale type', '')
    s_str = row.get('Sales', '0').replace('$', '').replace(',', '').strip()
    fe_str = row.get('Ad fees (General)', '-').replace('$', '').replace(',', '').strip()
    s = float(s_str) if s_str else 0
    fee = float(fe_str) if fe_str not in ['-', ''] else 0

    key = iid if iid else f'_halo_{title}'
    if title:
        items[key]['title'] = title

    if 'Offsite' in ad:
        off_sales += s; off_count += 1
        items[key]['off_s'] += s; items[key]['off_n'] += 1
    elif 'Priority' in st:
        plp_sales += s; plp_count += 1
        items[key]['plp_s'] += s; items[key]['plp_n'] += 1
    elif 'General' in st:
        if 'Halo' in sale_type:
            halo_sales += s; halo_count += 1
            items[key]['halo_s'] += s
        else:
            plg_sales += s; plg_fees += fee; plg_count += 1
            items[key]['plg_s'] += s
            items[key]['plg_f'] += fee
            items[key]['plg_n'] += 1

    items[key]['total_s'] += s

# ===== レポート出力 =====
total_gross = 66724  # weekly_historyから
total_ad_sales = plg_sales + plp_sales + off_sales + halo_sales

print('=' * 60)
print('eBay広告 現状分析レポート（2/13〜3/15）')
print('=' * 60)

print(f'\n■ 全体の売上に対する広告の割合')
print(f'  総売上: ${total_gross:,.0f}')
print(f'  広告帰属売上: ${total_ad_sales:,.0f} ({total_ad_sales/total_gross*100:.1f}%)')
print(f'  広告帰属外の売上: ${total_gross-total_ad_sales:,.0f} ({(total_gross-total_ad_sales)/total_gross*100:.1f}%)')

print(f'\n■ 広告タイプ別')
print(f'  PLG (General):')
print(f'    売上: ${plg_sales:,.0f} / 件数: {plg_count}')
print(f'    広告費: ${plg_fees:,.0f}')
if plg_fees > 0:
    print(f'    ROAS: {plg_sales/plg_fees:.1f}x')
    print(f'    ACOS: {plg_fees/plg_sales*100:.1f}%')

print(f'  PLP (Priority):')
print(f'    売上: ${plp_sales:,.0f} / 件数: {plp_count}')
print(f'    広告費: $491 (手入力)')
if plp_sales > 0:
    print(f'    ROAS: {plp_sales/491:.1f}x')
    print(f'    ACOS: {491/plp_sales*100:.1f}%')

print(f'  Offsite:')
print(f'    売上: ${off_sales:,.0f} / 件数: {off_count}')
print(f'    広告費: 不明（Seller Hub確認必要）')

print(f'  Halo (PLG追加売上):')
print(f'    売上: ${halo_sales:,.0f} / 件数: {halo_count}')

print(f'\n■ 広告費トータル')
print(f'  PLG広告費: ${plg_fees:,.0f}')
print(f'  PLP広告費: $491')
offsite_est = total_gross * 0.037
print(f'  Offsite広告費: 推定${offsite_est:,.0f} (売上の3.7%推定)')
total_est_fees = plg_fees + 491 + offsite_est
print(f'  合計推定広告費: ${total_est_fees:,.0f}')
print(f'  売上に対する広告費率: {total_est_fees/total_gross*100:.1f}%')

# 商品別: PLG費用TOP15
print(f'\n■ PLG広告費が高い商品TOP15')
sorted_items = sorted(items.items(), key=lambda x: x[1]['plg_f'], reverse=True)
for iid, d in sorted_items[:15]:
    if d['plg_f'] > 0:
        roas = d['plg_s'] / d['plg_f']
        short_title = d['title'][:45]
        print(f'  {iid:<16} 費用${d["plg_f"]:>7,.0f}  売上${d["plg_s"]:>9,.0f}  ROAS:{roas:.1f}x  {short_title}')

# ROASが低い商品
print(f'\n■ PLGでROASが低い商品（20x未満＝5%広告費で元が取れていない可能性）')
low_roas = [(iid, d) for iid, d in items.items()
            if d['plg_f'] > 0 and d['plg_s'] / d['plg_f'] < 20]
low_roas.sort(key=lambda x: x[1]['plg_f'], reverse=True)
total_low_fees = sum(d['plg_f'] for _, d in low_roas)
print(f'  該当商品数: {len(low_roas)}')
print(f'  このグループの総PLG費用: ${total_low_fees:,.0f}')
for iid, d in low_roas[:10]:
    roas = d['plg_s'] / d['plg_f']
    print(f'  {iid:<16} 費用${d["plg_f"]:>6,.0f}  売上${d["plg_s"]:>8,.0f}  ROAS:{roas:.1f}x  {d["title"][:45]}')

# PLP分析
print(f'\n■ PLP経由で売れた商品')
plp_items = [(iid, d) for iid, d in items.items() if d['plp_s'] > 0]
plp_items.sort(key=lambda x: x[1]['plp_s'], reverse=True)
for iid, d in plp_items:
    print(f'  {iid:<16} 売上${d["plp_s"]:>9,.0f} ({d["plp_n"]}件)  {d["title"][:50]}')

# 統計
real_items = {k: v for k, v in items.items() if not k.startswith('_halo_')}
print(f'\n■ 統計')
print(f'  広告が帰属された商品数: {len(real_items)} / 全出品2,856')
print(f'  広告帰属率: {len(real_items)/2856*100:.1f}%')

# PLG費用の分布
fees_list = sorted([d['plg_f'] for d in real_items.values() if d['plg_f'] > 0], reverse=True)
if fees_list:
    print(f'\n■ PLG費用の集中度')
    print(f'  PLG費用が発生した商品数: {len(fees_list)}')
    print(f'  上位10商品の合計: ${sum(fees_list[:10]):,.0f} ({sum(fees_list[:10])/sum(fees_list)*100:.1f}%)')
    print(f'  上位20商品の合計: ${sum(fees_list[:20]):,.0f} ({sum(fees_list[:20])/sum(fees_list)*100:.1f}%)')
    print(f'  全体PLG費用: ${sum(fees_list):,.0f}')

# 1月帰属変更の影響分析
print(f'\n■ 2026年1月帰属変更の影響（推定）')
print(f'  広告帰属売上比率: {total_ad_sales/total_gross*100:.1f}%')
print(f'  ※ 変更前の一般的な帰属率は約50%')
print(f'  ※ 変更後は80-90%以上に上昇が報告されている')
print(f'  ※ 御社の比率が高ければ、帰属変更の影響を受けている可能性が高い')

# PLG全取引のうちHaloの割合
total_plg_related = plg_count + halo_count
print(f'\n■ PLG取引の内訳')
print(f'  Attributed sale（直接帰属）: {plg_count}件 ${plg_sales:,.0f}')
print(f'  Halo item sale（関連商品帰属）: {halo_count}件 ${halo_sales:,.0f}')
if total_plg_related > 0:
    print(f'  Halo比率: {halo_count/total_plg_related*100:.1f}%')
