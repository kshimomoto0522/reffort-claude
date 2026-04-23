"""
Marketing API: 全キャンペーン詳細 + Offsiteレポート取得
"""
import sys, json, time, urllib.request, urllib.error, urllib.parse, gzip
sys.stdout.reconfigure(encoding='utf-8')
from ebay_oauth import get_access_token

token = get_access_token()
HEADERS = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
}

def api_get(url):
    req = urllib.request.Request(url)
    for k, v in HEADERS.items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode())

def api_post(url, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    for k, v in HEADERS.items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=30) as res:
        # createReportTaskは201を返し、LocationヘッダーにタスクURLが入る
        location = res.headers.get('Location', '')
        try:
            result = json.loads(res.read().decode())
        except:
            result = {}
        return result, location

# ===== 1. 全キャンペーン一覧 =====
print('='*60)
print('全キャンペーン一覧')
print('='*60)

all_campaigns = []
offset = 0
while True:
    url = f'https://api.ebay.com/sell/marketing/v1/ad_campaign?limit=100&offset={offset}'
    data = api_get(url)
    campaigns = data.get('campaigns', [])
    all_campaigns.extend(campaigns)
    if len(all_campaigns) >= data.get('total', 0):
        break
    offset += 100

# キャンペーンタイプ別に分類
running_cps = []  # PLG (Cost Per Sale)
running_cpc = []  # PLP (Cost Per Click)
ended = []
offsite_campaigns = []

for c in all_campaigns:
    cid = c.get('campaignId', '')
    name = c.get('campaignName', '')
    status = c.get('campaignStatus', '')
    funding = c.get('fundingStrategy', {})
    model = funding.get('fundingModel', '')
    bid_pct = funding.get('bidPercentage', '')
    budget = c.get('budget', {})
    daily_budget = budget.get('amount', {}).get('value', '') if budget else ''
    start = c.get('startDate', '')[:10] if c.get('startDate') else ''
    end = c.get('endDate', '')[:10] if c.get('endDate') else '継続中'

    # チャンネル情報（ON_SITE / OFF_SITE）
    channels = c.get('marketingChannels', [])

    info = {
        'id': cid, 'name': name, 'status': status,
        'model': model, 'bid_pct': bid_pct,
        'daily_budget': daily_budget, 'channels': channels,
        'start': start, 'end': end
    }

    if 'OFF_SITE' in channels:
        offsite_campaigns.append(info)

    if status == 'RUNNING':
        if model == 'COST_PER_SALE':
            running_cps.append(info)
        elif model == 'COST_PER_CLICK':
            running_cpc.append(info)
    else:
        ended.append(info)

print(f'\n■ 実行中のPLG（Cost Per Sale）キャンペーン: {len(running_cps)}件')
for c in running_cps:
    ch = ','.join(c['channels']) if c['channels'] else 'N/A'
    print(f'  [{c["id"]}] {c["name"]}  広告率:{c["bid_pct"]}%  チャンネル:{ch}  開始:{c["start"]}')

print(f'\n■ 実行中のPLP（Cost Per Click）キャンペーン: {len(running_cpc)}件')
for c in running_cpc:
    ch = ','.join(c['channels']) if c['channels'] else 'N/A'
    budget = f'${c["daily_budget"]}/日' if c['daily_budget'] else 'N/A'
    print(f'  [{c["id"]}] {c["name"]}  予算:{budget}  チャンネル:{ch}  開始:{c["start"]}')

print(f'\n■ Offsiteキャンペーン: {len(offsite_campaigns)}件')
for c in offsite_campaigns:
    print(f'  [{c["id"]}] {c["name"]}  状態:{c["status"]}  開始:{c["start"]}  終了:{c["end"]}')

print(f'\n■ 終了済みキャンペーン: {len(ended)}件')
for c in ended[:10]:
    ch = ','.join(c['channels']) if c['channels'] else 'N/A'
    print(f'  [{c["id"]}] {c["name"]}  型:{c["model"]}  チャンネル:{ch}')

# ===== 2. Offsiteレポート作成リクエスト =====
print('\n' + '='*60)
print('Offsiteレポート取得')
print('='*60)

# まずレポートメタデータを確認（利用可能なメトリクスを取得）
# CPC型のレポートとCPS型のレポートを両方試す
for report_type in ['CAMPAIGN_PERFORMANCE_REPORT', 'ACCOUNT_PERFORMANCE_REPORT']:
    for funding in ['COST_PER_CLICK', 'COST_PER_SALE']:
        print(f'\n--- {report_type} / {funding} ---')
        try:
            body = {
                'reportType': report_type,
                'fundingModels': [funding],
                'marketplaceId': 'EBAY_US',
                'dateFrom': '2026-02-13',
                'dateTo': '2026-03-15',
                'reportFormat': 'JSON',
            }

            url = 'https://api.ebay.com/sell/marketing/v1/ad_report_task'
            data_bytes = json.dumps(body).encode()
            req = urllib.request.Request(url, data=data_bytes, method='POST')
            for k, v in HEADERS.items():
                req.add_header(k, v)

            with urllib.request.urlopen(req, timeout=30) as res:
                location = res.headers.get('Location', '')
                task_id = location.split('/')[-1] if location else 'unknown'
                print(f'  ✅ レポートタスク作成: {task_id}')

        except urllib.error.HTTPError as e:
            body_text = e.read().decode() if e.fp else ''
            print(f'  ❌ エラー {e.code}')
            try:
                err = json.loads(body_text)
                for error in err.get('errors', []):
                    print(f'    {error.get("message", "")}')
            except:
                print(f'    {body_text[:200]}')

# ===== 3. 既存のレポートタスク一覧を確認 =====
print('\n' + '='*60)
print('レポートタスク一覧')
print('='*60)

try:
    tasks_data = api_get('https://api.ebay.com/sell/marketing/v1/ad_report_task?limit=10')
    tasks = tasks_data.get('reportTasks', [])
    print(f'タスク数: {tasks_data.get("total", 0)}')
    for t in tasks:
        tid = t.get('reportTaskId', '')
        status = t.get('reportTaskStatus', '')
        rtype = t.get('reportType', '')
        created = t.get('reportTaskCreationDate', '')[:19] if t.get('reportTaskCreationDate') else ''
        print(f'  [{tid}] {rtype} 状態:{status} 作成:{created}')
except urllib.error.HTTPError as e:
    print(f'エラー {e.code}')
