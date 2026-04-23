"""
Marketing API 接続テスト
既存のOAuth トークンでMarketing APIにアクセスできるか確認する
"""
import sys, json, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8')

# 既存のOAuth認証モジュールを使用
from ebay_oauth import get_access_token, has_valid_tokens

if not has_valid_tokens():
    print('❌ OAuthトークンがありません')
    sys.exit(1)

token = get_access_token()
print(f'✅ OAuth トークン取得: {token[:20]}...')

# ===== テスト1: キャンペーン一覧取得 =====
print('\n--- テスト1: Marketing API (キャンペーン一覧) ---')
url = 'https://api.ebay.com/sell/marketing/v1/ad_campaign?limit=5'
req = urllib.request.Request(url)
req.add_header('Authorization', f'Bearer {token}')
req.add_header('Content-Type', 'application/json')
req.add_header('X-EBAY-C-MARKETPLACE-ID', 'EBAY_US')

try:
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.loads(res.read().decode())
        campaigns = data.get('campaigns', [])
        print(f'✅ 成功！キャンペーン数: {data.get("total", 0)}')
        for c in campaigns[:5]:
            name = c.get('campaignName', 'N/A')
            status = c.get('campaignStatus', 'N/A')
            ctype = c.get('fundingStrategy', {}).get('fundingModel', 'N/A')
            print(f'  - [{status}] {name} (型: {ctype})')
except urllib.error.HTTPError as e:
    body = e.read().decode() if e.fp else ''
    print(f'❌ エラー {e.code}: {e.reason}')
    if e.code == 403:
        print('  → スコープ不足。sell.marketing スコープが必要です')
    try:
        err = json.loads(body)
        for error in err.get('errors', []):
            print(f'  → {error.get("message", "")}')
    except:
        print(f'  → {body[:200]}')

# ===== テスト2: Offsiteレポートメタデータ取得 =====
print('\n--- テスト2: レポートメタデータ取得 ---')
url2 = 'https://api.ebay.com/sell/marketing/v1/ad_report_metadata/report_type/CAMPAIGN_PERFORMANCE_REPORT?funding_model=COST_PER_CLICK'
req2 = urllib.request.Request(url2)
req2.add_header('Authorization', f'Bearer {token}')
req2.add_header('Content-Type', 'application/json')
req2.add_header('X-EBAY-C-MARKETPLACE-ID', 'EBAY_US')

try:
    with urllib.request.urlopen(req2, timeout=30) as res:
        data = json.loads(res.read().decode())
        dims = data.get('dimensionMetadata', [])
        metrics = data.get('metricKeys', data.get('metricMetadata', []))
        print(f'✅ 成功！')
        print(f'  利用可能なメトリクス:')
        if isinstance(metrics, list):
            for m in metrics:
                if isinstance(m, dict):
                    print(f'    - {m.get("metricKey", m)}')
                else:
                    print(f'    - {m}')
except urllib.error.HTTPError as e:
    body = e.read().decode() if e.fp else ''
    print(f'❌ エラー {e.code}: {e.reason}')
    if e.code == 403:
        print('  → スコープ不足')
    try:
        err = json.loads(body)
        for error in err.get('errors', []):
            print(f'  → {error.get("message", "")}')
    except:
        print(f'  → {body[:200]}')

print('\n--- 結論 ---')
print('Marketing APIにアクセスできた場合: → このままOffsiteデータ取得に進めます')
print('403エラーの場合: → OAuth再認証が必要（sell.marketingスコープを追加）')
