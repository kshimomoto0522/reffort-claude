"""
Chatwork認証情報（cookie+localStorage）をPlaywright形式で保存する初回セットアップ。

使い方：
    python setup_chatwork_auth.py

ブラウザが開いたら社長が手動でChatworkにログインし、ログイン完了後に
ターミナルでEnterキーを押す。auth_stateが保存される。
保存先: education/campers/scripts/.chatwork_auth.json (gitignored)

セッションが切れたら同じスクリプトを再実行するだけ。
"""
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = Path(__file__).parent.resolve()
AUTH_FILE = SCRIPT_DIR / ".chatwork_auth.json"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="ja-JP",
        )
        page = context.new_page()
        page.goto("https://www.chatwork.com/login.php")

        print("=" * 60)
        print("Chatworkにログインしてください。")
        print("ログイン完了後、このターミナルに戻って Enter を押してください。")
        print("=" * 60)
        input("ログインが終わったら Enter ▶ ")

        if "chatwork.com" not in page.url:
            print(f"⚠️  現在のURLが想定と違います: {page.url}")
            print("ログイン後のChatwork画面のままEnterを押してください。中止します。")
            browser.close()
            sys.exit(1)

        context.storage_state(path=str(AUTH_FILE))
        print(f"✅ 認証情報を保存しました: {AUTH_FILE}")
        print(f"   サイズ: {AUTH_FILE.stat().st_size:,} bytes")
        browser.close()


if __name__ == "__main__":
    main()
