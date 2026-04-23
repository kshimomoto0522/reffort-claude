import csv
import io

file = r"C:\Users\KEISUKE SHIMOMOTO\Downloads\rioxxrinaxjapan_advertising_sales_report_20260315.csv"

plg_s = plg_f = plg_n = 0
plp_s = plp_n = 0
off_s = off_n = 0
halo_s = halo_n = 0

with open(file, encoding='utf-8-sig') as f:
    lines = f.readlines()

# 3行目（index=2）がヘッダー行
data = io.StringIO(''.join(lines[2:]))
reader = csv.DictReader(data)

for row in reader:
    ad = row.get('Ad type', '')
    st = row.get('Campaign strategy', '')
    sale = row.get('Sale type', '')
    s_str = row.get('Sales', '0').replace('$', '').replace(',', '').strip()
    fe_str = row.get('Ad fees (General)', '-').replace('$', '').replace(',', '').strip()
    s = float(s_str) if s_str else 0
    fee = float(fe_str) if fe_str not in ['-', ''] else 0

    if 'Offsite' in ad:
        off_s += s; off_n += 1
    elif 'Priority' in st:
        plp_s += s; plp_n += 1
    elif 'General' in st:
        if sale == 'Halo item sale':
            halo_s += s; halo_n += 1
        else:
            plg_s += s; plg_f += fee; plg_n += 1

print("=== Ad Summary (Feb 13 - Mar 15, 2026) ===")
print(f"PLG (Promoted Listings General)")
print(f"  Orders: {plg_n}")
print(f"  Sales: ${plg_s:,.2f}")
print(f"  Ad Fees: ${plg_f:,.2f}")
if plg_f > 0:
    print(f"  ROAS: {plg_s/plg_f:.1f}x")
    print(f"  Ad Fee Rate: {plg_f/plg_s*100:.1f}%")
print()
print(f"PLG Halo (additional items sold with PLG ad)")
print(f"  Orders: {halo_n}")
print(f"  Sales: ${halo_s:,.2f}")
print()
print(f"PLP (Promoted Listings Priority)")
print(f"  Orders: {plp_n}")
print(f"  Sales: ${plp_s:,.2f}")
print(f"  NOTE: Cost not in this report, check Seller Hub separately")
print()
print(f"Offsite (Promoted Offsite)")
print(f"  Orders: {off_n}")
print(f"  Sales: ${off_s:,.2f}")
print(f"  NOTE: Cost not in this report, check Seller Hub separately")
print()
total = plg_s + plp_s + off_s + halo_s
print(f"Total Ad-Attributed Sales: ${total:,.2f}")
