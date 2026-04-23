"""レート制限解除を待ってレポート生成→Chatwork送信する自動リトライスクリプト"""
import sys, os, time, subprocess, json, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_RETRIES = 12  # 最大12回（= 2時間）
WAIT_SECONDS = 600  # 10分間隔

def check_rate_limit():
    """Traffic APIが使えるか確認"""
    from ebay_oauth import get_access_token
    token = get_access_token()
    filter_str = 'date_range:[20260317..20260323],marketplace_ids:{EBAY_US}'
    params = urllib.parse.urlencode({
        'dimension': 'DAY',
        'metric': 'LISTING_IMPRESSION_TOTAL',
        'filter': filter_str,
    })
    url = f'https://api.ebay.com/sell/analytics/v1/traffic_report?{params}'
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return True
    except urllib.error.HTTPError:
        return False

def send_chatwork_message(room_id, message):
    """Chatworkにメッセージ送信"""
    cw_token = os.getenv('CW_TOKEN')
    data = urllib.parse.urlencode({'body': message}).encode()
    req = urllib.request.Request(
        f'https://api.chatwork.com/v2/rooms/{room_id}/messages',
        data=data, method='POST')
    req.add_header('X-ChatWorkToken', cw_token)
    with urllib.request.urlopen(req) as res:
        return res.read().decode()

print(f'レート制限解除待ち開始（最大{MAX_RETRIES}回 × {WAIT_SECONDS}秒）')
for attempt in range(MAX_RETRIES):
    print(f'チェック {attempt+1}/{MAX_RETRIES}...', end=' ')
    if check_rate_limit():
        print('OK! レート制限解除!')
        # レポート生成
        print('レポート生成中...')
        result = subprocess.run(
            ['python', os.path.join(SCRIPT_DIR, 'create_weekly_report_v3.py')],
            capture_output=True, text=True, encoding='utf-8', cwd=SCRIPT_DIR
        )
        print(result.stdout[-500:] if result.stdout else '')
        if result.returncode != 0:
            print(f'エラー: {result.stderr[-300:] if result.stderr else ""}')
            send_chatwork_message('426170119', f'⚠️ レポート生成エラー\n{result.stderr[-200:] if result.stderr else "不明"}')
            sys.exit(1)
        
        # Chatwork送信
        print('Chatwork送信中...')
        result2 = subprocess.run(
            ['python', os.path.join(SCRIPT_DIR, 'send_weekly_report.py')],
            capture_output=True, text=True, encoding='utf-8', cwd=SCRIPT_DIR
        )
        print(result2.stdout if result2.stdout else '')
        if result2.returncode != 0:
            print(f'送信エラー: {result2.stderr[-300:] if result2.stderr else ""}')
        else:
            print('完了!')
        sys.exit(0)
    else:
        print(f'まだ制限中。{WAIT_SECONDS}秒待機...')
        if attempt < MAX_RETRIES - 1:
            time.sleep(WAIT_SECONDS)

print('最大リトライ回数に達しました。手動で再実行してください。')
send_chatwork_message('426170119', '⚠️ eBay Traffic APIのレート制限が2時間以上解除されませんでした。手動確認が必要です。')
