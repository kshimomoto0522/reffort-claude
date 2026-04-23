"""
BayPack共同運営費の請求書を自動生成するスクリプト
===============================================

処理の流れ:
1. まとめシート(row14 共同運営費 支払額)から対象月と金額を取得
2. 請求書スプレッドシートで最新シートを複製し、一番左に配置
3. N1(物件番号)・N3(発行日)・B9(件名)・I16(金額) を更新
4. Google Drive API経由でPDFエクスポート → Desktop/請求書/ に保存

使い方:
  python generate_invoice.py                         # 最新月を自動検出して生成
  python generate_invoice.py --month 2026-03         # 月指定
  python generate_invoice.py --dry-run               # 実行計画のみ表示（変更なし）
  python generate_invoice.py --amount 262735         # 金額を手動指定
  python generate_invoice.py --issue-date 2026-04-22 # 発行日を手動指定

認証:
  commerce/ebay/analytics/reffort-sheets-fcbca5a4bbc2.json のサービスアカウント鍵を流用。
  両スプレッドシートで reffort-claude@reffort-sheets.iam.gserviceaccount.com の権限が必要。
"""
import os
import sys
import re
import argparse
from datetime import date, datetime

import gspread
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import AuthorizedSession

sys.stdout.reconfigure(encoding='utf-8')

# ========== 定数（このスクリプトと同じ場所基準の相対パス） ==========
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# サービスアカウント鍵は commerce/ebay/analytics/ のものを流用
CREDS_FILE = os.path.normpath(os.path.join(
    _SCRIPT_DIR, '..', '..', '..', 'commerce', 'ebay', 'analytics',
    'reffort-sheets-fcbca5a4bbc2.json'
))

# ========== スプレッドシート設定 ==========
SOURCE_SS_ID = "1pnW_NcHdFmiTj0O9a7gwL79CaFt2ZUNEjUFqSQcvtx4"  # BayPack売上表_まとめ
SOURCE_SHEET_NAME = "まとめ"
SOURCE_AMOUNT_ROW = 14  # 「共同運営費 支払額」行
SOURCE_HEADER_ROW = 2   # 月ヘッダー行（'2026年3月'形式）

TARGET_SS_ID = "1e0axm3HzbQY1_a1nJQ5kKbtmozCt2NfF82nFfPaDHJQ"  # 【BayPack】Reffort請求書

# 出力
OUTPUT_DIR_DEFAULT = r"C:\Users\KEISUKE SHIMOMOTO\Desktop\請求書"

# 物件番号の月毎振分番号（固定）
BRANCH_NO = "05"

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]


# ========== ユーティリティ関数 ==========

def calc_fiscal_year(year, month):
    """弊社決算6月基準で「期」を計算（1期=Jul 2022-Jun 2023）

    例: 2026-03 → 4期 / 2026-07 → 5期 / 2027-01 → 5期
    """
    if month >= 7:
        return year - 2021  # 7-12月は年-2021
    return year - 2022      # 1-6月は年-2022


def format_yymm(year, month):
    """'2603' 形式に整形"""
    return f"{year % 100:02d}{month:02d}"


def parse_amount(s):
    """'¥262,735' または '262,735' 等を int にパース"""
    if not s:
        return None
    cleaned = re.sub(r'[^\d\-]', '', str(s))
    if not cleaned:
        return None
    return int(cleaned)


def auto_detect_latest_month(matome_ws):
    """まとめシートの row14 の最右非空セル＝最新月を検出

    Returns: (year, month, amount, col_1indexed)
    """
    row_hdr = matome_ws.row_values(SOURCE_HEADER_ROW)
    row_amt = matome_ws.row_values(SOURCE_AMOUNT_ROW)

    latest_col_idx = None
    latest_amount = None
    # 右から走査
    for i in range(len(row_amt) - 1, -1, -1):
        val = row_amt[i]
        parsed = parse_amount(val)
        if parsed is not None and parsed > 0:
            latest_col_idx = i
            latest_amount = parsed
            break

    if latest_col_idx is None:
        raise RuntimeError("まとめシート Row14 に有効な請求金額が見つかりません")

    # 対応する月ヘッダー取得
    if latest_col_idx >= len(row_hdr):
        raise RuntimeError(f"列インデックス {latest_col_idx} に対応する月ヘッダーがありません")
    month_header = row_hdr[latest_col_idx]
    m = re.match(r'(\d{4})年(\d{1,2})月', month_header)
    if not m:
        raise RuntimeError(f"月ヘッダー '{month_header}' の書式が 'YYYY年M月' と違います")
    return int(m.group(1)), int(m.group(2)), latest_amount, latest_col_idx + 1


def find_month_column(matome_ws, target_year, target_month):
    """指定月の列を header row から検索（0-indexed col index を返す）"""
    row_hdr = matome_ws.row_values(SOURCE_HEADER_ROW)
    target = f"{target_year}年{target_month}月"
    for i, h in enumerate(row_hdr):
        if h == target:
            return i
    return None


def fetch_amount_for_month(matome_ws, target_year, target_month):
    """指定月の金額を取得"""
    col_idx = find_month_column(matome_ws, target_year, target_month)
    if col_idx is None:
        raise RuntimeError(f"まとめシートに '{target_year}年{target_month}月' 列がありません")
    row_amt = matome_ws.row_values(SOURCE_AMOUNT_ROW)
    if col_idx >= len(row_amt):
        return None
    return parse_amount(row_amt[col_idx])


def check_existing_invoice(target_ss, new_title):
    """同名の請求書シートが既にあるかチェック"""
    for ws in target_ss.worksheets():
        if ws.title == new_title:
            raise RuntimeError(
                f"'{new_title}' は既に存在しています。\n"
                f"再生成するには、まず当該シートを削除してください。"
            )


def copy_latest_invoice(target_ss, new_title):
    """最新シート（一番左）を複製し、新タイトルで先頭に配置"""
    sheets = target_ss.worksheets()
    if not sheets:
        raise RuntimeError("請求書テンプレートシートが存在しません")
    source_ws = sheets[0]
    new_ws = target_ss.duplicate_sheet(
        source_sheet_id=source_ws.id,
        insert_sheet_index=0,
        new_sheet_name=new_title,
    )
    return new_ws, source_ws


def update_cells(ws, bukken_no, issue_date_str, subject, amount):
    """N1/N3/B9/I16 の4セルを一括更新"""
    ws.batch_update([
        {'range': 'N1',  'values': [[bukken_no]]},
        {'range': 'N3',  'values': [[issue_date_str]]},
        {'range': 'B9',  'values': [[subject]]},
        {'range': 'I16', 'values': [[amount]]},
    ], value_input_option='USER_ENTERED')


def export_sheet_pdf(creds, ss_id, sheet_id, output_path):
    """Google Drive API経由で指定シートをPDFとしてエクスポート"""
    authed = AuthorizedSession(creds)
    params = {
        'format': 'pdf',
        'gid': str(sheet_id),
        'portrait': 'true',     # 縦向き
        'size': 'A4',
        'fitw': 'true',         # 幅をページに合わせる
        'top_margin': '0.5',
        'bottom_margin': '0.5',
        'left_margin': '0.5',
        'right_margin': '0.5',
        'sheetnames': 'false',
        'printtitle': 'false',
        'pagenumbers': 'false',
        'gridlines': 'false',
        'fzr': 'false',
    }
    url = f"https://docs.google.com/spreadsheets/d/{ss_id}/export"
    resp = authed.get(url, params=params)
    resp.raise_for_status()
    with open(output_path, 'wb') as f:
        f.write(resp.content)
    return len(resp.content)


# ========== メイン処理 ==========

def main():
    parser = argparse.ArgumentParser(
        description='BayPack共同運営費の請求書を自動生成する',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--month', help='対象月 YYYY-MM (省略時はまとめシートの最新月を自動検出)')
    parser.add_argument('--amount', type=int, help='金額（円、整数）を手動指定')
    parser.add_argument('--issue-date', help='発行日 YYYY-MM-DD (省略時は今日)')
    parser.add_argument('--output-dir', default=OUTPUT_DIR_DEFAULT, help='PDF出力先フォルダ')
    parser.add_argument('--dry-run', action='store_true', help='実際の変更は行わず、実行計画のみ表示')
    args = parser.parse_args()

    print("=" * 64)
    print(" BayPack共同運営費 請求書自動生成")
    print("=" * 64)

    # ---------- 認証 ----------
    print(f"[1/6] サービスアカウント認証中 ...")
    if not os.path.exists(CREDS_FILE):
        raise FileNotFoundError(f"認証鍵が見つかりません: {CREDS_FILE}")
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    print(f"      OK  ({os.path.basename(CREDS_FILE)})")

    # ---------- まとめシートから対象月・金額を取得 ----------
    print(f"[2/6] まとめシートから金額を取得中 ...")
    src = gc.open_by_key(SOURCE_SS_ID)
    matome = src.worksheet(SOURCE_SHEET_NAME)

    if args.month:
        m = re.match(r'^(\d{4})-(\d{1,2})$', args.month)
        if not m:
            raise ValueError(f"--month の形式が不正: '{args.month}' (例: 2026-03)")
        target_y = int(m.group(1))
        target_m = int(m.group(2))
        amount_from_src = fetch_amount_for_month(matome, target_y, target_m)
    else:
        target_y, target_m, amount_from_src, _ = auto_detect_latest_month(matome)

    # 金額の上書き（手動指定優先）
    amount = args.amount if args.amount is not None else amount_from_src
    if amount is None or amount <= 0:
        raise RuntimeError(
            f"{target_y}年{target_m}月 の金額が取得できません。\n"
            f"--amount で手動指定してください。"
        )

    print(f"      対象月: {target_y}年{target_m}月")
    print(f"      金額（まとめシート）: ¥{amount_from_src:,}" if amount_from_src else "      金額（まとめシート）: N/A")
    if args.amount is not None:
        print(f"      金額（手動指定）: ¥{args.amount:,}")
    print(f"      採用する金額: ¥{amount:,}")

    # ---------- 各値の組み立て ----------
    target_yymm = format_yymm(target_y, target_m)
    fiscal_year = calc_fiscal_year(target_y, target_m)
    bukken_no = f"RF{fiscal_year:02d}-{target_m:02d}-{BRANCH_NO}"
    subject = f"BayPack共同運営費（{target_m}月）"
    new_sheet_title = f"請求書（{target_yymm}）"

    if args.issue_date:
        d = datetime.strptime(args.issue_date, '%Y-%m-%d').date()
    else:
        d = date.today()
    issue_date_str = f"{d.year}/{d.month}/{d.day}"

    pdf_name = f"【BayPack】共同運営費_請求書（{target_yymm}）.pdf"

    # ---------- 実行プラン表示 ----------
    print(f"[3/6] 実行プラン:")
    print(f"      新シート名  : {new_sheet_title}")
    print(f"      N1 物件番号  : {bukken_no}")
    print(f"      N3 発行日    : {issue_date_str}")
    print(f"      B9 件名      : {subject}")
    print(f"      I16 金額     : {amount:,}")
    print(f"      PDF ファイル : {pdf_name}")
    print(f"      出力先       : {args.output_dir}")

    if args.dry_run:
        print()
        print("*** --dry-run モード：実際の変更は行いません ***")
        return 0

    # ---------- 既存シートチェック ----------
    print(f"[4/6] ターゲットシート複製中 ...")
    tgt = gc.open_by_key(TARGET_SS_ID)
    check_existing_invoice(tgt, new_sheet_title)
    new_ws, src_ws = copy_latest_invoice(tgt, new_sheet_title)
    print(f"      コピー元: '{src_ws.title}'")
    print(f"      作成: '{new_ws.title}' (id={new_ws.id})")

    # ---------- セル更新 ----------
    print(f"[5/6] セル更新中 ...")
    update_cells(new_ws, bukken_no, issue_date_str, subject, amount)
    print(f"      OK  (N1 / N3 / B9 / I16)")

    # ---------- PDF出力 ----------
    print(f"[6/6] PDFエクスポート中 ...")
    os.makedirs(args.output_dir, exist_ok=True)
    pdf_path = os.path.join(args.output_dir, pdf_name)
    size = export_sheet_pdf(creds, TARGET_SS_ID, new_ws.id, pdf_path)
    print(f"      OK  {pdf_path}")
    print(f"      サイズ: {size:,} bytes")

    print()
    print("=" * 64)
    print(" 完了")
    print(f"   シート: {new_sheet_title}")
    print(f"   PDF   : {pdf_path}")
    print("=" * 64)
    return 0


if __name__ == '__main__':
    sys.exit(main())
