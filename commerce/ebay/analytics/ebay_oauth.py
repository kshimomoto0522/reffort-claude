"""
eBay OAuth 2.0 認証管理
初回のみブラウザでの認証が必要（1回だけ）。
その後はrefresh_tokenで自動更新（18ヶ月有効）。

【初回セットアップ手順】
1. eBay Developer Portal (https://developer.ebay.com) にログイン
2. Application Keys → Production → OAuth Redirect Settings
3. RuNameを確認し、Accept URLに http://localhost:9090/callback を追加
4. .envに EBAY_RUNAME=（RuName値） を追加
5. python ebay_oauth.py を実行 → ブラウザが開く → eBayにログインして「I Agree」
6. 完了。以降は自動。
"""

import os, sys, json, time, base64, urllib.request, urllib.parse, webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

# .envから設定読み込み
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, 'ebay_oauth_tokens.json')

# eBay OAuth 2.0 エンドポイント（Production）
AUTH_URL  = 'https://auth.ebay.com/oauth2/authorize'
TOKEN_URL = 'https://api.ebay.com/identity/v1/oauth2/token'

APP_ID   = os.getenv('EBAY_APP_ID')
CERT_ID  = os.getenv('EBAY_CERT_ID')
RUNAME   = os.getenv('EBAY_RUNAME', '')

# 必要なスコープ（Traffic Report API + Marketing API）
SCOPES = ' '.join([
    'https://api.ebay.com/oauth/api_scope/sell.analytics.readonly',  # Traffic Report
    'https://api.ebay.com/oauth/api_scope/sell.marketing',           # Marketing API（広告管理・レポート）
    'https://api.ebay.com/oauth/api_scope/sell.marketing.readonly',  # Marketing API（読み取り専用）
])

# ローカルサーバー設定（認証コード受取用）
CALLBACK_PORT = 9090
CALLBACK_PATH = '/callback'


def _load_tokens():
    """保存済みトークンを読み込む"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {}


def _save_tokens(tokens):
    """トークンをJSON保存"""
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(tokens, f, indent=2)


def _basic_auth():
    """APP_ID:CERT_IDのBase64エンコード（eBay OAuth認証ヘッダー用）"""
    cred = f'{APP_ID}:{CERT_ID}'.encode()
    return base64.b64encode(cred).decode()


def get_consent_url():
    """ブラウザで開くeBay認証URL"""
    params = {
        'client_id': APP_ID,
        'redirect_uri': RUNAME,
        'response_type': 'code',
        'scope': SCOPES,
    }
    return f'{AUTH_URL}?{urllib.parse.urlencode(params)}'


def exchange_code_for_tokens(auth_code):
    """認証コード → アクセストークン + リフレッシュトークン"""
    data = urllib.parse.urlencode({
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': RUNAME,
    }).encode()

    req = urllib.request.Request(TOKEN_URL, data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    req.add_header('Authorization', f'Basic {_basic_auth()}')

    with urllib.request.urlopen(req, timeout=30) as res:
        result = json.loads(res.read().decode())

    tokens = {
        'access_token':  result['access_token'],
        'refresh_token': result['refresh_token'],
        'expires_at':    time.time() + result.get('expires_in', 7200) - 60,
        'created':       time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    _save_tokens(tokens)
    print(f'✅ トークン取得完了（refresh_token有効期限: 約18ヶ月）')
    return tokens


def refresh_access_token():
    """refresh_tokenで新しいaccess_tokenを取得（自動・無人）"""
    tokens = _load_tokens()
    if not tokens.get('refresh_token'):
        raise Exception('refresh_tokenがありません。初回認証を実行してください: python ebay_oauth.py')

    data = urllib.parse.urlencode({
        'grant_type': 'refresh_token',
        'refresh_token': tokens['refresh_token'],
        'scope': SCOPES,
    }).encode()

    req = urllib.request.Request(TOKEN_URL, data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    req.add_header('Authorization', f'Basic {_basic_auth()}')

    with urllib.request.urlopen(req, timeout=30) as res:
        result = json.loads(res.read().decode())

    tokens['access_token'] = result['access_token']
    tokens['expires_at']   = time.time() + result.get('expires_in', 7200) - 60
    tokens['refreshed']    = time.strftime('%Y-%m-%d %H:%M:%S')
    _save_tokens(tokens)
    return tokens


def get_access_token():
    """有効なaccess_tokenを返す（期限切れなら自動リフレッシュ）"""
    tokens = _load_tokens()
    if not tokens.get('access_token'):
        raise Exception('トークンがありません。初回認証を実行してください: python ebay_oauth.py')

    # 期限切れチェック（60秒のマージン込み）
    if time.time() >= tokens.get('expires_at', 0):
        print('🔄 OAuth トークン自動リフレッシュ中...')
        tokens = refresh_access_token()
        print('✅ リフレッシュ完了')

    return tokens['access_token']


def has_valid_tokens():
    """有効なトークンが存在するか"""
    tokens = _load_tokens()
    return bool(tokens.get('refresh_token'))


# ===== 初回セットアップ（ブラウザ認証フロー）=====
class _CallbackHandler(BaseHTTPRequestHandler):
    """eBayからのリダイレクトを受け取るローカルHTTPサーバー"""
    auth_code = None

    def do_GET(self):
        # URLからcodeパラメータを取得
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if 'code' in params:
            _CallbackHandler.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write('✅ 認証成功！このページを閉じてください。'.encode('utf-8'))
        else:
            self.send_response(400)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            error = params.get('error', ['不明'])[0]
            self.wfile.write(f'❌ 認証失敗: {error}'.encode('utf-8'))

    def log_message(self, format, *args):
        pass  # ログを抑制


def run_setup():
    """初回セットアップ: ブラウザ認証 → トークン取得"""
    if not RUNAME:
        print('❌ EBAY_RUNAMEが設定されていません。')
        print()
        print('【設定手順】')
        print('1. https://developer.ebay.com にログイン')
        print('2. Application Keys → Production → OAuth Redirect Settings')
        print('3. RuNameを確認')
        print(f'4. Accept URL に http://localhost:{CALLBACK_PORT}{CALLBACK_PATH} を追加して保存')
        print('5. .envファイルに EBAY_RUNAME=（確認したRuName値） を追加')
        print('6. もう一度 python ebay_oauth.py を実行')
        return

    print('🔑 eBay OAuth 2.0 初回セットアップ')
    print(f'   RuName: {RUNAME}')
    print(f'   コールバック: http://localhost:{CALLBACK_PORT}{CALLBACK_PATH}')
    print()

    # ローカルサーバー起動
    server = HTTPServer(('localhost', CALLBACK_PORT), _CallbackHandler)
    server.timeout = 120  # 2分タイムアウト

    # ブラウザで認証ページを開く
    url = get_consent_url()
    print('📎 ブラウザで認証ページを開いています...')
    print(f'   （自動で開かない場合はこのURLをコピーしてブラウザに貼り付け）')
    print(f'   {url}')
    print()
    webbrowser.open(url)

    # コールバック待ち
    print('⏳ eBayでの認証を待っています...（最大2分）')
    while _CallbackHandler.auth_code is None:
        server.handle_request()
        if _CallbackHandler.auth_code is None:
            print('⏰ タイムアウト。もう一度実行してください。')
            return

    print(f'📨 認証コードを受信しました')

    # トークン交換
    try:
        tokens = exchange_code_for_tokens(_CallbackHandler.auth_code)
        print()
        print('🎉 セットアップ完了！')
        print(f'   トークン保存先: {TOKEN_FILE}')
        print('   以降は自動でトークンが更新されます。')
    except Exception as e:
        print(f'❌ トークン交換エラー: {e}')


if __name__ == '__main__':
    if has_valid_tokens():
        print('✅ 有効なトークンが存在します。')
        try:
            token = get_access_token()
            print(f'   access_token: {token[:20]}...')
        except Exception as e:
            print(f'⚠️ トークンリフレッシュエラー: {e}')
            print('   再セットアップを実行します...')
            run_setup()
    else:
        run_setup()
