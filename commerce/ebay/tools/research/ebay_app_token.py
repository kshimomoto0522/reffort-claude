"""
eBay Application Access Token 取得モジュール

【目的】
Browse API（パブリック検索）など「ユーザーデータを必要としない」エンドポイントは
client_credentials grant で取れる Application Access Token で叩ける。
Authorization Code grant（社長アカウントの販売データ用）と用途が違うので別ファイルにする。

【参考】
- 既存: ../analytics/ebay_oauth.py（Authorization Code grant 版・販売データ用）
- 公式: https://developer.ebay.com/api-docs/static/oauth-client-credentials-grant.html

【取得scope】
Browse API は `https://api.ebay.com/oauth/api_scope` の最小scopeで叩ける。

【トークン有効期限】
約 7200 秒（2 時間）。期限切れたら自動取得し直す。
"""

import os
import sys
import json
import time
import base64
import urllib.parse
import urllib.request
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 認証情報は既存の analytics/.env を流用する（社長の手間を増やさない）
ANALYTICS_ENV = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'analytics', '.env'))
load_dotenv(ANALYTICS_ENV)

# 念のためツール側の .env も読む（上書き想定）
LOCAL_ENV = os.path.join(SCRIPT_DIR, '.env')
if os.path.exists(LOCAL_ENV):
    load_dotenv(LOCAL_ENV, override=True)

TOKEN_FILE = os.path.join(SCRIPT_DIR, 'cache', 'ebay_app_token.json')
TOKEN_URL = 'https://api.ebay.com/identity/v1/oauth2/token'

APP_ID = os.getenv('EBAY_APP_ID')
CERT_ID = os.getenv('EBAY_CERT_ID')

# Browse API に必要な最小 scope
SCOPE = 'https://api.ebay.com/oauth/api_scope'


def _basic_auth() -> str:
    """APP_ID:CERT_ID の Base64（eBay OAuth ヘッダー用）"""
    if not APP_ID or not CERT_ID:
        raise RuntimeError(
            f'EBAY_APP_ID / EBAY_CERT_ID が読めません。\n'
            f'  読み先: {ANALYTICS_ENV}\n'
            f'  分析側 .env が存在するかと、APP_ID/CERT_ID キー名を確認してください。'
        )
    cred = f'{APP_ID}:{CERT_ID}'.encode()
    return base64.b64encode(cred).decode()


def _load_cached_token() -> dict:
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {}


def _save_token(token: dict) -> None:
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(token, f, indent=2)


def fetch_new_token() -> dict:
    """
    client_credentials grant で新規 Application Token を取得する。
    """
    data = urllib.parse.urlencode({
        'grant_type': 'client_credentials',
        'scope': SCOPE,
    }).encode()

    req = urllib.request.Request(TOKEN_URL, data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    req.add_header('Authorization', f'Basic {_basic_auth()}')

    with urllib.request.urlopen(req, timeout=30) as res:
        result = json.loads(res.read().decode())

    token = {
        'access_token': result['access_token'],
        'expires_at': time.time() + result.get('expires_in', 7200) - 60,
        'token_type': result.get('token_type', 'Bearer'),
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    _save_token(token)
    return token


def get_app_token() -> str:
    """
    有効な Application Token を返す。期限切れなら自動再取得。
    """
    cached = _load_cached_token()
    if cached.get('access_token') and time.time() < cached.get('expires_at', 0):
        return cached['access_token']
    print('🔄 eBay Application Token を取得中...')
    token = fetch_new_token()
    print(f'✅ 取得完了 (expires_at={time.strftime("%H:%M:%S", time.localtime(token["expires_at"]))})')
    return token['access_token']


if __name__ == '__main__':
    # 動作確認
    print(f'EBAY_APP_ID 末尾: ...{(APP_ID or "")[-6:]}')
    print(f'EBAY_CERT_ID 末尾: ...{(CERT_ID or "")[-6:]}')
    token = get_app_token()
    print(f'access_token (先頭20): {token[:20]}...')
    print('✅ Application Token 取得 OK')
