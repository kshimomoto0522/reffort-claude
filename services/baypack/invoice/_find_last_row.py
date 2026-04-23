"""請求書(2602)の実際のデータ最終行を特定"""
import os, sys, tempfile
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

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
gc = gspread.authorize(creds)
ss = gc.open_by_key(TARGET_SS_ID)
ws = ss.worksheet("請求書（2602）")

# A1:N50 を読んで、最終行を特定
data = ws.get('A1:N50')
print(f"取得 {len(data)} 行")
for i, row in enumerate(data, start=1):
    # 空行以外を表示
    non_empty = [c for c in row if c.strip()]
    if non_empty:
        print(f"Row {i}: {row}")
