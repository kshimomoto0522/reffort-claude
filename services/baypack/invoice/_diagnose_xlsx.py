"""
xlsxダウンロード後のシート状態を診断する
- 印刷範囲の設定状況
- シェイプ（ロゴ・印鑑等の画像）の数
- グリッドライン設定
"""
import os
import sys
import tempfile
import gspread
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import AuthorizedSession
import win32com.client

sys.stdout.reconfigure(encoding='utf-8')

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_FILE = os.path.normpath(os.path.join(
    _SCRIPT_DIR, '..', '..', '..', 'commerce', 'ebay', 'analytics',
    'reffort-sheets-fcbca5a4bbc2.json'
))
TARGET_SS_ID = "1e0axm3HzbQY1_a1nJQ5kKbtmozCt2NfF82nFfPaDHJQ"

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
authed = AuthorizedSession(creds)
url = f"https://docs.google.com/spreadsheets/d/{TARGET_SS_ID}/export?format=xlsx"
resp = authed.get(url)
resp.raise_for_status()

tmp_xlsx = os.path.join(tempfile.gettempdir(), "baypack_diag.xlsx")
with open(tmp_xlsx, 'wb') as f:
    f.write(resp.content)
print(f"xlsx DL: {len(resp.content):,} bytes")

excel = win32com.client.Dispatch('Excel.Application')
excel.Visible = False
excel.DisplayAlerts = False

try:
    wb = excel.Workbooks.Open(os.path.abspath(tmp_xlsx))

    for i in range(1, wb.Sheets.Count + 1):
        ws = wb.Sheets(i)
        ps = ws.PageSetup
        used = ws.UsedRange
        print(f"\n=== {ws.Name} ===")
        print(f"  Shapes数: {ws.Shapes.Count}")
        for j in range(1, ws.Shapes.Count + 1):
            sh = ws.Shapes(j)
            print(f"    - Shape[{j}]: name={sh.Name}, type={sh.Type}, Top={sh.Top:.0f}, Left={sh.Left:.0f}, W={sh.Width:.0f}, H={sh.Height:.0f}")
        print(f"  UsedRange: {used.Address}")
        print(f"  PrintArea: '{ps.PrintArea}'")
        print(f"  Orientation: {ps.Orientation}  (1=縦, 2=横)")
        print(f"  PaperSize: {ps.PaperSize}  (9=A4)")
        print(f"  PrintGridlines: {ps.PrintGridlines}")
        print(f"  FitToPagesWide: {ps.FitToPagesWide}")
        print(f"  FitToPagesTall: {ps.FitToPagesTall}")
        print(f"  Zoom: {ps.Zoom}")

    wb.Close(False)
finally:
    excel.Quit()

os.remove(tmp_xlsx)
