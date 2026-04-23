"""
send_weekly_report.py
毎週月曜日に実行。eBay週次レポートのExcelファイルを生成し、
Chatwork【AI】eBay運営グループに自動アップロードする。
TEST_MODE=True のとき社長DM宛に送信して事前確認できる。
"""

import json, os, sys, glob, urllib.request, urllib.parse
from datetime import date
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

# .envファイルから機密情報を読み込む
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

# ===== 設定 =====
# 相対パス化：このスクリプトと同じフォルダ(commerce/ebay/analytics/)を基準にする
EBAY_DIR      = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE  = os.path.join(EBAY_DIR, "weekly_history.json")
CW_TOKEN      = os.getenv('CW_TOKEN')

CW_GROUP_ROOM = 426169912   # 【AI】eBay運営（本番）
CW_TEST_ROOM  = 426170119   # 下元 敬介 DM（テスト）

TEST_MODE = False  # True=社長DM / False=グループチャット本番

# ===== 最新Excelを取得 =====
def get_latest_excel():
    files = glob.glob(rf"{EBAY_DIR}\eBay週次レポート_v3_*.xlsx")
    if not files:
        return None
    return max(files, key=os.path.getmtime)

# ===== Chatworkにファイルをアップロード =====
def upload_file_to_chatwork(room_id, filepath, message):
    url      = f'https://api.chatwork.com/v2/rooms/{room_id}/files'
    filename = os.path.basename(filepath)
    boundary = b'----CWBoundary'

    body  = b'--' + boundary + b'\r\n'
    body += b'Content-Disposition: form-data; name="message"\r\n\r\n'
    body += message.encode('utf-8') + b'\r\n'

    with open(filepath, 'rb') as f:
        file_data = f.read()
    body += b'--' + boundary + b'\r\n'
    body += f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode('utf-8')
    body += b'Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n'
    body += file_data + b'\r\n'
    body += b'--' + boundary + b'--\r\n'

    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('X-ChatWorkToken', CW_TOKEN)
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary.decode()}')
    with urllib.request.urlopen(req, timeout=60) as res:
        return res.read().decode('utf-8')

# ===== 先週比コメントを生成 =====
def make_comparison_comment(history):
    keys = sorted(history.keys())
    if len(keys) < 2:
        return '（前週データなし）'
    cur  = history[keys[-1]]
    prev = history[keys[-2]]

    cur_orders  = cur.get('total_orders', 0)
    prev_orders = prev.get('total_orders', 0)
    delta = cur_orders - prev_orders

    cur_gross  = cur.get('total_gross', '$0').replace('$','').replace(',','')
    prev_gross = prev.get('total_gross', '$0').replace('$','').replace(',','')
    try:
        delta_gross = float(cur_gross) - float(prev_gross)
        gross_str = f'{"+" if delta_gross>=0 else ""}{delta_gross:,.0f}'
    except Exception:
        gross_str = '不明'

    cur_cvr  = cur.get('overall_cvr',  '?')
    prev_cvr = prev.get('overall_cvr', '?')

    lines = [f'受注: {cur_orders}件（前週比 {"+" if delta>=0 else ""}{delta}件）',
             f'売上: {cur.get("total_gross","?")}（前週比 ${gross_str}）',
             f'CVR: {cur_cvr}（前週: {prev_cvr}）']
    return '\n'.join(lines)

# ===== メイン処理 =====
def main():
    room_id = CW_TEST_ROOM if TEST_MODE else CW_GROUP_ROOM

    excel_path = get_latest_excel()
    if not excel_path:
        print('ERROR: Excelファイルが見つかりません')
        return
    print(f'送信ファイル: {os.path.basename(excel_path)}')

    with open(HISTORY_FILE, encoding='utf-8') as f:
        history = json.load(f)

    comparison = make_comparison_comment(history)
    today_str  = date.today().strftime('%Y/%m/%d')

    # 本番はスタッフ向け挨拶、テストは社長向け
    if TEST_MODE:
        greeting = f'[テスト確認] {today_str} - 月曜本番配信のテストです。'
    else:
        greeting = f'おはようございます。{today_str} eBay週次レポートをお届けします。'

    # Googleスプレッドシートのリンク
    gsheets_url = 'https://docs.google.com/spreadsheets/d/1AT4x_qyohYiEs08RSHs5uFgqBAm51IRsY1ajybsJe0s'

    message = (f'{greeting}\n\n'
               f'【先週との比較】\n{comparison}\n\n'
               f'📊 Googleスプレッドシート版（推奨）:\n{gsheets_url}\n'
               f'※ Excel版も添付しています')

    print('Chatworkに送信中...')
    result = upload_file_to_chatwork(room_id, excel_path, message)
    print(f'送信完了: {result}')

if __name__ == '__main__':
    main()
