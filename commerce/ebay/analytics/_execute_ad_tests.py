"""
広告テスト実行スクリプト
テストA: 30商品のPLG完全停止
テストB: 6商品のPLG 5%→2%
テストC: 6商品にPLP追加
"""
import sys, json, urllib.request, urllib.error, time
sys.stdout.reconfigure(encoding='utf-8')
from ebay_oauth import get_access_token

token = get_access_token()
H = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
}

with open('ebay_seller_cache.json', encoding='utf-8') as f:
    cache = json.load(f)

# SKU → メインItem ID（US版＝ウォッチ最多のID）
def sku_to_main_id(sku):
    best_id = ''
    best_watch = -1
    for iid, c in cache.items():
        if c.get('sku', '') == sku:
            w = c.get('watch', 0) or 0
            if w > best_watch:
                best_watch = w
                best_id = iid
    return best_id

# SKU → 全Item ID
def sku_to_all_ids(sku):
    return [iid for iid, c in cache.items() if c.get('sku', '') == sku]

# APIヘルパー
def api_get(url):
    req = urllib.request.Request(url)
    for k, v in H.items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode())

def api_post(url, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    for k, v in H.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            try:
                return json.loads(res.read().decode()), res.getcode()
            except:
                return {}, res.getcode()
    except urllib.error.HTTPError as e:
        body_text = e.read().decode() if e.fp else ''
        return {'error': body_text}, e.code

def api_delete(url):
    req = urllib.request.Request(url, method='DELETE')
    for k, v in H.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.getcode()
    except urllib.error.HTTPError as e:
        return e.code

# PLG(CPS)キャンペーンID一覧
PLG_CAMPAIGN_IDS = [
    '149928632019',  # Basis 4%
    '149928627019',  # General 4%
    '46395952019',   # AUTO 5%
    '43474504019',   # General 4%
    '36918858019',   # Campaign Nov 2024 5%
    '36918398019',   # Campaign Oct 2024 5%
    '13744874019',   # Campaign Jun 2023 5%
    '13688059019',   # Campaign Jun 2023 5%
    '13561705019',   # Campaign Apr 2023 4%
    '13359389019',   # Campaign Jan 2023 5%
]

# ===== テスト対象商品 =====

# テストA: PLG完全停止 30商品（生涯販売ゼロ）
TEST_A_SKUS = [
    'H01430', 'H01087', 'H01386', 'H01574', 'M00225',
    'H01572', 'M00249', 'M00273', 'H01617', 'H01597',
    'H01603', 'H01564', 'S05641', 'H01443', 'H01600',
    'S05640', 'M00104', 'M00219', 'H01225', 'H01477',
    'S05713', 'S05401', 'S05294', 'S05330', 'V0619',
    'M00220', 'H01552', 'H01118', 'H01391', 'V0568',
]

# テストB: PLG 5%→2% 6商品（在庫2以上・期間中PLG売上あり）
TEST_B_SKUS = [
    'M00186',  # Reebok PREMIER ROAD ULTRA Purple (qty:7)
    'S04094',  # On Cloudhorizon Waterproof (qty:4)
    'H01548',  # NIKE Air Max 90 Valentine's Day (qty:11)
    'S05474',  # ASICS GEL-NIMBUS 28 (qty:9)
    'S05505',  # ASICS Women's NOVABLAST 5 (qty:7)
    'M00118',  # adidas KYOTO (qty:7)
    # V0572除外（在庫1）、S04895除外（在庫12だが念のため確認 → 含める）
]
# S04895を追加確認: qty:12なので含めてOK
TEST_B_SKUS.append('S04895')  # ASICS UNPRE ARS 3 (qty:12)
# → テストBは7商品に

# テストC: PLP追加 6商品
TEST_C_SKUS = [
    'V0298',   # Onitsuka Tiger GSM CREAM BLACK
    'S00444',  # ASICS WINJOB CP214 TS BOA
    'V0299',   # Onitsuka Tiger GSM CREAM HIKING GREEN
    'H01399',  # PUMA Speed Cat Wedge Totally Taupe
    'V0347',   # Onitsuka Tiger MEXICO 66 SD YELLOW BLACK
    'H01258',  # NIKE Air More Uptempo Low
]

# ===== 実行 =====

print('=' * 70)
print('テストA: PLG完全停止（30商品）')
print('=' * 70)

test_a_removed = 0
test_a_errors = 0
for sku in TEST_A_SKUS:
    all_ids = sku_to_all_ids(sku)
    if not all_ids:
        print(f'  ⚠️ 【{sku}】Item ID見つからず')
        continue

    for item_id in all_ids:
        for camp_id in PLG_CAMPAIGN_IDS:
            # キャンペーンからこのリスティングのadを取得
            ad_url = f'https://api.ebay.com/sell/marketing/v1/ad_campaign/{camp_id}/ad?listing_ids={item_id}&limit=10'
            try:
                ad_data = api_get(ad_url)
                ads = ad_data.get('ads', [])
                for ad in ads:
                    ad_id = ad.get('adId', '')
                    if ad_id:
                        del_url = f'https://api.ebay.com/sell/marketing/v1/ad_campaign/{camp_id}/ad/{ad_id}'
                        code = api_delete(del_url)
                        if code in [200, 204]:
                            test_a_removed += 1
                        else:
                            test_a_errors += 1
            except:
                pass
        time.sleep(0.3)  # レート制限対策

    print(f'  ✅ 【{sku}】全キャンペーンから削除')

print(f'\nテストA結果: {test_a_removed}件削除 / {test_a_errors}件エラー')

# ===== テストB: 5%→2% =====
print()
print('=' * 70)
print('テストB: PLG 5%→2%（7商品）')
print('=' * 70)

# Step 1: 新規2%キャンペーン作成
print('2%キャンペーン作成中...')
new_camp_body = {
    'campaignName': 'PLG Test 2% (3/26-4/9)',
    'marketplaceId': 'EBAY_US',
    'fundingStrategy': {
        'fundingModel': 'COST_PER_SALE',
        'bidPercentage': '2.0',
    },
}
camp_url = 'https://api.ebay.com/sell/marketing/v1/ad_campaign'
data = json.dumps(new_camp_body).encode()
req = urllib.request.Request(camp_url, data=data, method='POST')
for k, v in H.items():
    req.add_header(k, v)
try:
    with urllib.request.urlopen(req, timeout=30) as res:
        location = res.headers.get('Location', '')
        new_camp_id = location.split('/')[-1] if location else ''
        print(f'  ✅ 2%キャンペーン作成: {new_camp_id}')
except urllib.error.HTTPError as e:
    body_text = e.read().decode() if e.fp else ''
    print(f'  ❌ エラー: {e.code} {body_text[:200]}')
    new_camp_id = ''

# Step 2: 既存PLGキャンペーンから削除
test_b_removed = 0
for sku in TEST_B_SKUS:
    all_ids = sku_to_all_ids(sku)
    for item_id in all_ids:
        for camp_id in PLG_CAMPAIGN_IDS:
            try:
                ad_data = api_get(f'https://api.ebay.com/sell/marketing/v1/ad_campaign/{camp_id}/ad?listing_ids={item_id}&limit=10')
                for ad in ad_data.get('ads', []):
                    ad_id = ad.get('adId', '')
                    if ad_id:
                        code = api_delete(f'https://api.ebay.com/sell/marketing/v1/ad_campaign/{camp_id}/ad/{ad_id}')
                        if code in [200, 204]:
                            test_b_removed += 1
            except:
                pass
        time.sleep(0.3)
    print(f'  ✅ 【{sku}】既存PLGから削除')

# Step 3: 2%キャンペーンに追加
if new_camp_id:
    test_b_added = 0
    for sku in TEST_B_SKUS:
        all_ids = sku_to_all_ids(sku)
        listing_ids = [{'listingId': iid} for iid in all_ids]
        if listing_ids:
            add_url = f'https://api.ebay.com/sell/marketing/v1/ad_campaign/{new_camp_id}/bulk_create_ads_by_listing_id'
            result, code = api_post(add_url, {'requests': listing_ids})
            if code in [200, 201]:
                test_b_added += len(listing_ids)
                print(f'  ✅ 【{sku}】2%キャンペーンに追加（{len(listing_ids)} IDs）')
            else:
                print(f'  ⚠️ 【{sku}】追加エラー: {code}')
            time.sleep(0.3)

    print(f'\nテストB結果: {test_b_removed}件削除 → {test_b_added}件を2%に追加')

# ===== テストC: PLP追加 =====
print()
print('=' * 70)
print('テストC: PLP追加（6商品）')
print('=' * 70)

# Mexico 66キャンペーン(157755261019)に追加するか、新規PLPキャンペーンを作るか
# 新規で作る方がテスト管理しやすい
print('PLPテストキャンペーン作成中...')
plp_camp_body = {
    'campaignName': 'PLP Test (3/26-4/9)',
    'marketplaceId': 'EBAY_US',
    'fundingStrategy': {
        'fundingModel': 'COST_PER_CLICK',
    },
    'budget': {
        'amount': {
            'currency': 'USD',
            'value': '5.00',
        },
        'budgetType': 'DAILY',
    },
}
req = urllib.request.Request(camp_url, json.dumps(plp_camp_body).encode(), method='POST')
for k, v in H.items():
    req.add_header(k, v)
try:
    with urllib.request.urlopen(req, timeout=30) as res:
        location = res.headers.get('Location', '')
        plp_camp_id = location.split('/')[-1] if location else ''
        print(f'  ✅ PLPテストキャンペーン作成: {plp_camp_id}')
except urllib.error.HTTPError as e:
    body_text = e.read().decode() if e.fp else ''
    print(f'  ❌ エラー: {e.code} {body_text[:300]}')
    plp_camp_id = ''

if plp_camp_id:
    test_c_added = 0
    for sku in TEST_C_SKUS:
        main_id = sku_to_main_id(sku)
        if main_id:
            add_url = f'https://api.ebay.com/sell/marketing/v1/ad_campaign/{plp_camp_id}/bulk_create_ads_by_listing_id'
            result, code = api_post(add_url, {'requests': [{'listingId': main_id}]})
            if code in [200, 201]:
                test_c_added += 1
                print(f'  ✅ 【{sku}】PLP追加')
            else:
                print(f'  ⚠️ 【{sku}】エラー: {code} {str(result)[:150]}')
            time.sleep(0.3)

    print(f'\nテストC結果: {test_c_added}商品をPLPキャンペーンに追加')

# ===== サマリー =====
print()
print('=' * 70)
print('テスト開始完了サマリー')
print('=' * 70)
print(f'テストA: PLG完全停止 {len(TEST_A_SKUS)}商品')
print(f'テストB: PLG 5%→2% {len(TEST_B_SKUS)}商品 (キャンペーン: {new_camp_id})')
print(f'テストC: PLP追加 {len(TEST_C_SKUS)}商品 (キャンペーン: {plp_camp_id})')
print(f'期間: 3/26 → 4/9（2週間）')
print(f'測定日: 4/9に全テスト結果を分析')
