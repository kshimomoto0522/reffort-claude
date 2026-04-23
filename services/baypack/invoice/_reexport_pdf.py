"""
既存シートのPDFを再エクスポート（調整用ユーティリティ）

パラメータを最小化し、Google SheetsのUI「ファイル→ダウンロード→PDF」と
同じ挙動になるように再出力する。
"""
import os
import sys
import gspread
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import AuthorizedSession

sys.stdout.reconfigure(encoding='utf-8')

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_FILE = os.path.normpath(os.path.join(
    _SCRIPT_DIR, '..', '..', '..', 'commerce', 'ebay', 'analytics',
    'reffort-sheets-fcbca5a4bbc2.json'
))

TARGET_SS_ID = "1e0axm3HzbQY1_a1nJQ5kKbtmozCt2NfF82nFfPaDHJQ"
SHEET_TITLE = "請求書（2603）"
OUTPUT_DIR = r"C:\Users\KEISUKE SHIMOMOTO\Desktop\請求書"

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
gc = gspread.authorize(creds)

tgt = gc.open_by_key(TARGET_SS_ID)
ws = tgt.worksheet(SHEET_TITLE)
print(f"Sheet: {ws.title} (id={ws.id})")

authed = AuthorizedSession(creds)

# パターンA: 最小パラメータ（format=pdf + gid のみ）
# Google Sheetsが保存した印刷設定（シート固有）をそのまま使う
params_minimal = {
    'format': 'pdf',
    'gid': str(ws.id),
}
url = f"https://docs.google.com/spreadsheets/d/{TARGET_SS_ID}/export"
resp = authed.get(url, params=params_minimal)
resp.raise_for_status()

output_a = os.path.join(OUTPUT_DIR, "_test_A_minimal_【BayPack】共同運営費_請求書（2603）.pdf")
with open(output_a, 'wb') as f:
    f.write(resp.content)
print(f"[A] 最小パラメータ: {output_a} ({len(resp.content):,} bytes)")
