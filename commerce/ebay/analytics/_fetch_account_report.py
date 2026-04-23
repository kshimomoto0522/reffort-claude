"""
Marketing API: アカウントパフォーマンスレポート取得
PLG + Offsite + Organic の全データを日別で取得する
"""
import sys, json, urllib.request, urllib.error, time, gzip
sys.stdout.reconfigure(encoding='utf-8')
from ebay_oauth import get_access_token

token = get_access_token()
HEADERS = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
}

url = 'https://api.ebay.com/sell/marketing/v1/ad_report_task'

# CPC版（Offsite + PLP）— oa_メトリクスはCPC fundingでのみ利用可能
body = {
    'reportType': 'ACCOUNT_PERFORMANCE_REPORT',
    'fundingModels': ['COST_PER_CLICK'],
    'marketplaceId': 'EBAY_US',
    'dateFrom': '2026-02-13T00:00:00.000Z',
    'dateTo': '2026-03-15T23:59:59.000Z',
    'reportFormat': 'TSV_GZIP',
    'dimensionKeys': ['day'],
    'metricKeys': [
        # PLP (CPC on eBay)
        'cpc_clicks', 'cpc_attributed_sales',
        'cpc_ad_fees_listingsite_currency', 'cpc_sale_amount_listingsite_currency',
        'cpc_return_on_ad_spend', 'cpc_ctr',
        # Offsite Ads
        'oa_clicks', 'oa_attributed_sales',
        'oa_ad_fees_listingsite_currency', 'oa_sale_amount_listingsite_currency',
        'oa_return_on_ad_spend', 'oa_cost_per_click',
    ]
}

print('ACCOUNT_PERFORMANCE_REPORT (CPC: PLP+Offsite) 作成中...')
data_bytes = json.dumps(body).encode()
req = urllib.request.Request(url, data=data_bytes, method='POST')
for k, v in HEADERS.items():
    req.add_header(k, v)

try:
    with urllib.request.urlopen(req, timeout=30) as res:
        location = res.headers.get('Location', '')
        task_id = location.split('/')[-1] if location else ''
        print(f'タスク作成: {task_id}')
except urllib.error.HTTPError as e:
    body_text = e.read().decode() if e.fp else ''
    print(f'エラー {e.code}')
    try:
        err = json.loads(body_text)
        for error in err.get('errors', []):
            print(f'  {error.get("message", "")[:300]}')
    except:
        print(f'  {body_text[:300]}')
    sys.exit(1)

# 完了待ち
print('生成待ち...')
for i in range(20):
    time.sleep(5)
    check_url = f'https://api.ebay.com/sell/marketing/v1/ad_report_task/{task_id}'
    req2 = urllib.request.Request(check_url)
    for k, v in HEADERS.items():
        req2.add_header(k, v)
    with urllib.request.urlopen(req2, timeout=30) as res:
        task = json.loads(res.read().decode())
        status = task.get('reportTaskStatus', '')
        if i % 3 == 0:
            print(f'  [{i*5}秒] {status}')
        if status == 'SUCCESS':
            print('  完了！')
            break
        elif status == 'FAILED':
            print('  失敗')
            sys.exit(1)
else:
    print('タイムアウト')
    sys.exit(1)

# ダウンロード
print('ダウンロード中...')
dl_url = f'https://api.ebay.com/sell/marketing/v1/ad_report_task/{task_id}/report'
req3 = urllib.request.Request(dl_url)
for k, v in HEADERS.items():
    req3.add_header(k, v)

with urllib.request.urlopen(req3, timeout=60) as res:
    raw = res.read()
    try:
        content = gzip.decompress(raw).decode('utf-8')
    except:
        content = raw.decode('utf-8')

lines = content.strip().split('\n')
headers_row = lines[0].split('\t')
print(f'ヘッダー({len(headers_row)}列): {headers_row}')

# 集計
total = {}
for h in headers_row:
    total[h] = 0.0

for line in lines[1:]:
    cols = line.split('\t')
    row = dict(zip(headers_row, cols))
    for h in headers_row:
        if h == 'day':
            continue
        try:
            val = row.get(h, '0') or '0'
            total[h] += float(val)
        except:
            pass

print()
print('=' * 60)
print('期間合計（2/13〜3/15）')
print('=' * 60)

cpc_fees = total.get('cpc_ad_fees_listingsite_currency', 0)
cpc_sales = total.get('cpc_sale_amount_listingsite_currency', 0)
cpc_clicks = total.get('cpc_clicks', 0)
cpc_sales_n = total.get('cpc_attributed_sales', 0)

oa_fees = total.get('oa_ad_fees_listingsite_currency', 0)
oa_sales = total.get('oa_sale_amount_listingsite_currency', 0)
oa_clicks = total.get('oa_clicks', 0)
oa_sales_n = total.get('oa_attributed_sales', 0)

print(f'\n■ PLP (Promoted Listings Priority / CPC)')
print(f'  クリック: {cpc_clicks:,.0f}')
print(f'  売上件数: {cpc_sales_n:,.0f}')
print(f'  売上額: ${cpc_sales:,.2f}')
print(f'  広告費: ${cpc_fees:,.2f}')
if cpc_fees > 0:
    print(f'  ROAS: {cpc_sales/cpc_fees:.1f}x')
    print(f'  ACOS: {cpc_fees/cpc_sales*100:.1f}%')

print(f'\n■ Offsite Ads')
print(f'  クリック: {oa_clicks:,.0f}')
print(f'  売上件数: {oa_sales_n:,.0f}')
print(f'  売上額: ${oa_sales:,.2f}')
print(f'  広告費: ${oa_fees:,.2f}')
if oa_fees > 0 and oa_sales > 0:
    print(f'  ROAS: {oa_sales/oa_fees:.1f}x')
    print(f'  ACOS: {oa_fees/oa_sales*100:.1f}%')
if oa_clicks > 0 and oa_fees > 0:
    print(f'  平均CPC: ${oa_fees/oa_clicks:.2f}')

print(f'\n■ 全広告費サマリー')
print(f'  PLG広告費: $3,446 (CSV確認済み)')
print(f'  PLP広告費: ${cpc_fees:,.2f} (API)')
print(f'  Offsite広告費: ${oa_fees:,.2f} (API)')
total_all = 3446 + cpc_fees + oa_fees
print(f'  ---')
print(f'  広告費合計: ${total_all:,.2f}')
print(f'  総売上($66,724)に対する広告費率: {total_all/66724*100:.1f}%')
print(f'  年間換算: ${total_all * 12:,.0f}')
