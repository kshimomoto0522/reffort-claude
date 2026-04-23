import csv, io, sys
from collections import defaultdict

# 文字コード問題を回避：結果をファイルに書き出す
OUTPUT_FILE = r"C:\Users\KEISUKE SHIMOMOTO\Desktop\reffort\commerce\ebay\analytics\result_transaction.txt"

file = r"C:\Users\KEISUKE SHIMOMOTO\Downloads\Transaction-Mar-16-2026-01_18_10-0700-13288723972.csv"

with open(file, encoding='utf-8-sig') as f:
    lines = f.readlines()

# Line12（index=11）がヘッダー行
rows_all = list(csv.DictReader(io.StringIO(''.join(lines[11:]))))

def to_float(s):
    try:
        return float(str(s).replace(',','').replace('$','').strip())
    except:
        return 0.0

def clean(s):
    # 制御文字・ゼロ幅スペース等を除去
    return ''.join(c for c in s if c.isprintable() and c not in '\u200b\u200c\u200d\ufeff')

# USD（USサイト）のみ対象
total_item_sub = 0
total_shipping = 0
total_ebay_tax = 0
total_gross = 0
total_fvf_fixed = 0
total_fvf_var = 0
total_intl_fee = 0
total_net = 0
refund_amount = 0
refund_count = 0
orders = []

for row in rows_all:
    cur = row.get('Transaction currency','').strip()
    t = row.get('Type','').strip()
    if cur != 'USD':
        continue

    if t == 'Order':
        item_sub = to_float(row.get('Item subtotal', 0))
        shipping = to_float(row.get('Shipping and handling', 0))
        ebay_tax = to_float(row.get('eBay collected tax', 0))
        gross = to_float(row.get('Gross transaction amount', 0))
        fvf_fixed = to_float(row.get('Final Value Fee - fixed', 0))
        fvf_var = to_float(row.get('Final Value Fee - variable', 0))
        intl_fee = to_float(row.get('International fee', 0))
        net = to_float(row.get('Net amount', 0))

        total_item_sub += item_sub
        total_shipping += shipping
        total_ebay_tax += ebay_tax
        total_gross += gross
        total_fvf_fixed += fvf_fixed
        total_fvf_var += fvf_var
        total_intl_fee += intl_fee
        total_net += net

        orders.append({
            'item_id': row.get('Item ID','').strip(),
            'title': clean(row.get('Item title','').strip()),
            'date': row.get('Transaction creation date','').strip(),
            'item_subtotal': item_sub,
            'gross': gross,
            'net': net,
            'fvf': fvf_fixed + fvf_var,
        })

    elif t == 'Refund':
        refund_amount += to_float(row.get('Net amount', 0))
        refund_count += 1

total_fvf = total_fvf_fixed + total_fvf_var
# eBay手数料合計（FVF + International fee）
total_ebay_fees = total_fvf + total_intl_fee
# 手取り（送料・税抜き商品売上から見た実質手数料率）
fee_rate = abs(total_ebay_fees) / total_item_sub * 100 if total_item_sub else 0

# 商品別売上TOP15
item_sales = defaultdict(lambda: {'title':'', 'sales':0, 'n':0, 'net':0, 'fvf':0})
for o in orders:
    key = o['item_id'] or o['title'][:40]
    item_sales[key]['title'] = o['title']
    item_sales[key]['sales'] += o['item_subtotal']
    item_sales[key]['n'] += 1
    item_sales[key]['net'] += o['net']
    item_sales[key]['fvf'] += o['fvf']

top15 = sorted(item_sales.items(), key=lambda x: -x[1]['sales'])[:15]

# 結果を書き出し
lines_out = []
lines_out.append("=" * 60)
lines_out.append("  売上・手数料サマリー（USサイトのみ・USD）")
lines_out.append("  期間: 2026年2月13日〜3月15日（約30日間）")
lines_out.append("=" * 60)
lines_out.append(f"  注文件数:                   {len(orders)}件")
lines_out.append(f"  返金件数:                   {refund_count}件")
lines_out.append("")
lines_out.append(f"【収入】")
lines_out.append(f"  商品売上（Item subtotal）:  ${total_item_sub:>10,.2f}")
lines_out.append(f"  送料収入:                   ${total_shipping:>10,.2f}")
lines_out.append(f"  eBay代行徴収税（非収入）:   ${total_ebay_tax:>10,.2f}")
lines_out.append(f"  Gross合計（受取総額）:       ${total_gross:>10,.2f}")
lines_out.append("")
lines_out.append(f"【eBay手数料】")
lines_out.append(f"  Final Value Fee（固定）:    ${total_fvf_fixed:>10,.2f}")
lines_out.append(f"  Final Value Fee（変動）:    ${total_fvf_var:>10,.2f}")
lines_out.append(f"  FVF合計:                    ${total_fvf:>10,.2f}")
lines_out.append(f"  International fee:          ${total_intl_fee:>10,.2f}")
lines_out.append(f"  eBay手数料合計:             ${total_ebay_fees:>10,.2f}")
lines_out.append(f"  手数料率（商品売上比）:             {fee_rate:.1f}%")
lines_out.append("")
lines_out.append(f"【手取り】")
lines_out.append(f"  Net（eBay手数料差引後）:    ${total_net:>10,.2f}")
lines_out.append("")
if refund_count > 0:
    lines_out.append(f"  返金合計:                   ${refund_amount:>10,.2f}（{refund_count}件）")
    lines_out.append("")

lines_out.append("=" * 60)
lines_out.append("  売れ筋TOP15（商品売上ベース）")
lines_out.append("=" * 60)
for rank, (iid, d) in enumerate(top15, 1):
    lines_out.append(f"  {rank:2}. {d['title'][:55]}")
    lines_out.append(f"      {d['n']}件 / 売上: ${d['sales']:,.2f} / 手取参考: ${d['net']:,.2f}")
lines_out.append("")

result = '\n'.join(lines_out)

# ファイル書き出し（UTF-8）
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(result)

print(f"Done. -> {OUTPUT_FILE}")
print(result)
