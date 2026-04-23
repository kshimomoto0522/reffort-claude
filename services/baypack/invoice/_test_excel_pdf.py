"""
Excel COM 経由で Google Sheets → xlsx → PDF 変換を試す
ローカルの Meiryo フォントが使われることを検証
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
SHEET_TITLE = "請求書（2603）"
OUTPUT_PDF = r"C:\Users\KEISUKE SHIMOMOTO\Desktop\請求書\_test_B_excel_【BayPack】共同運営費_請求書（2603）.pdf"

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

# ===== 1. xlsx としてダウンロード =====
print("[1] xlsx ダウンロード中 ...")
creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
authed = AuthorizedSession(creds)
url = f"https://docs.google.com/spreadsheets/d/{TARGET_SS_ID}/export?format=xlsx"
resp = authed.get(url)
resp.raise_for_status()

# 一時xlsxファイル
tmp_dir = tempfile.gettempdir()
tmp_xlsx = os.path.join(tmp_dir, "baypack_invoice_tmp.xlsx")
with open(tmp_xlsx, 'wb') as f:
    f.write(resp.content)
print(f"    OK: {tmp_xlsx} ({len(resp.content):,} bytes)")

# ===== 2. Excel COM で開く =====
print("[2] Excel起動 & xlsx を開く ...")
excel = win32com.client.Dispatch('Excel.Application')
excel.Visible = False
excel.DisplayAlerts = False

try:
    wb = excel.Workbooks.Open(os.path.abspath(tmp_xlsx))
    print(f"    ブック開いた: {wb.Name}")
    print(f"    シート一覧: {[wb.Sheets(i+1).Name for i in range(wb.Sheets.Count)]}")

    # ===== 3. 該当シートを選択して PDF エクスポート =====
    print(f"[3] '{SHEET_TITLE}' を選択してPDFエクスポート ...")
    ws = wb.Sheets(SHEET_TITLE)
    ws.Select()

    # ExportAsFixedFormat: 0=PDF, 1=XPS
    # Quality: 0=Standard, 1=Minimum
    os.makedirs(os.path.dirname(OUTPUT_PDF), exist_ok=True)
    ws.ExportAsFixedFormat(
        Type=0,
        Filename=os.path.abspath(OUTPUT_PDF),
        Quality=0,
        IncludeDocProperties=True,
        IgnorePrintAreas=False,
        OpenAfterPublish=False,
    )
    print(f"    OK: {OUTPUT_PDF}")

    wb.Close(SaveChanges=False)
finally:
    excel.Quit()

# ===== 4. 一時xlsx削除 =====
os.remove(tmp_xlsx)
print(f"[4] 一時ファイル削除: {tmp_xlsx}")

# ===== 5. サイズ確認 =====
pdf_size = os.path.getsize(OUTPUT_PDF)
print(f"\n完了: {OUTPUT_PDF} ({pdf_size:,} bytes)")
