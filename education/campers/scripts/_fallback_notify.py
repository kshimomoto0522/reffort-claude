"""run_campers_removal.bat から起動失敗時のみ呼ばれるフォールバック通知。
campers_member_removal.py 自身がDM送信しない異常事態（Python起動失敗・スクリプトクラッシュ等）でDM送信。
"""
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parents[2]

# .env から CW_TOKEN を取得
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / "commerce" / "ebay" / "analytics" / ".env")
except Exception:
    pass

CW_TOKEN = os.getenv("CW_TOKEN")
PRESIDENT_DM = "426170119"


def main():
    exit_code = sys.argv[1] if len(sys.argv) > 1 else "?"
    log_path = sys.argv[2] if len(sys.argv) > 2 else ""

    log_tail = ""
    if log_path and os.path.exists(log_path):
        try:
            with open(log_path, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            log_tail = "".join(lines[-30:])[-1500:]
        except Exception as e:
            log_tail = f"(ログ読み取り失敗: {e})"

    body = (
        "[info][title]⚠️ Campersメンバー削除タスク 起動失敗[/title]"
        f"campers_member_removal.py の実行に失敗しました（Pythonプロセス自体が異常終了）。\n\n"
        f"■ 終了コード: {exit_code}\n"
        f"■ ログファイル: {log_path}\n\n"
        f"■ ログ末尾:\n{log_tail}\n\n"
        f"対応手順:\n"
        f"1) `python \"{SCRIPT_DIR}\\campers_member_removal.py\"` を手動実行\n"
        f"2) auth切れの場合は `1_setup_auth.bat` で再ログイン\n"
        f"[/info]"
    )

    if not CW_TOKEN:
        print("⚠️ CW_TOKEN なし、DM送信スキップ")
        return

    data = urllib.parse.urlencode({"body": body}).encode()
    req = urllib.request.Request(
        f"https://api.chatwork.com/v2/rooms/{PRESIDENT_DM}/messages",
        data=data, method="POST"
    )
    req.add_header("X-ChatWorkToken", CW_TOKEN)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            r.read()
        print("✅ フォールバックDM送信")
    except Exception as e:
        print(f"❌ DM送信失敗: {e}")


if __name__ == "__main__":
    main()
