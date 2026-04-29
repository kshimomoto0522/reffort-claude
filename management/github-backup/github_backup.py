"""
reffort + memory フォルダの自動GitHubバックアップ
旧 Claude scheduled-task `daily-github-backup` の Windows 移管版（2026-04-29）

- 起動: Windowsタスクスケジューラ `DailyGithubBackup` から毎日0:05
- 役割: ① memory フォルダを .claude/memory_backup/ にミラー同期
        ② reffort 配下の変更を機密ファイル混入チェック後にcommit & push
        ③ 失敗時は社長個人DMに箱型カードで通知
- 機密混入検出時は git reset で解除してから報告（コミットしない）
- 旧SKILL.mdの全ロジックを Python に移植
"""

import os
import sys
import re
import shutil
import subprocess
import traceback
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / ".env", override=True)

# ── 設定 ──
CW_TOKEN          = os.getenv("CHATWORK_API_TOKEN")
ROOM_ID_PRESIDENT = int(os.getenv("CHATWORK_ROOM_ID_PRESIDENT", "426170119"))
DRY_RUN           = os.getenv("DRY_RUN", "false").lower() == "true"

REFFORT_ROOT = Path("C:/Users/KEISUKE SHIMOMOTO/Desktop/reffort")
MEM_SRC      = Path("C:/Users/KEISUKE SHIMOMOTO/.claude/projects/C--Users-KEISUKE-SHIMOMOTO-Desktop-reffort/memory")
MEM_DST      = REFFORT_ROOT / ".claude" / "memory_backup"
BRANCH       = "master"

JST = timezone(timedelta(hours=9))


# ──────────────────────────────────────────────
# Chatwork通知
# ──────────────────────────────────────────────
def cw_post_president(body: str) -> None:
    if DRY_RUN or not CW_TOKEN:
        print(f"[DRY_RUN/no-token] would notify:\n{body[:300]}\n")
        return
    url = f"https://api.chatwork.com/v2/rooms/{ROOM_ID_PRESIDENT}/messages"
    data = urllib.parse.urlencode({"body": body}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("X-ChatWorkToken", CW_TOKEN)
    urllib.request.urlopen(req, timeout=15).read()


def report_failure(step: str, detail: str, suggestion: str = "") -> None:
    now = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
    body = (
        f"[info][title]🚨 GitHub自動バックアップ 異常｜{now}[/title]"
        f"■ 失敗ステップ: {step}\n"
        f"■ 検出内容: {detail[:1000]}\n"
        f"■ 起動経路: Windowsタスクスケジューラ DailyGithubBackup\n"
        + (f"■ 対応提案: {suggestion}\n" if suggestion else "")
        + f"対応: 社長確認をお願いします。[/info]"
    )
    try:
        cw_post_president(body)
    except Exception:
        traceback.print_exc()


# ──────────────────────────────────────────────
# サブプロセス実行
# ──────────────────────────────────────────────
def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True, encoding="utf-8")
    if res.stdout:
        print(res.stdout.rstrip())
    if res.stderr:
        print(res.stderr.rstrip(), file=sys.stderr)
    if check and res.returncode != 0:
        raise RuntimeError(f"command failed (exit {res.returncode}): {' '.join(cmd)}\nSTDERR: {res.stderr}")
    return res


# ──────────────────────────────────────────────
# STEP 0: memory フォルダを .claude/memory_backup/ へ同期
# ──────────────────────────────────────────────
def step0_sync_memory() -> None:
    print("=== STEP 0: memory mirror sync ===")
    if not MEM_SRC.exists():
        raise RuntimeError(f"memory source not found: {MEM_SRC}")

    # 削除追従のため宛先をクリーンに作り直す
    if MEM_DST.exists():
        shutil.rmtree(MEM_DST)
    MEM_DST.mkdir(parents=True, exist_ok=True)
    archive_dst = MEM_DST / "archive"
    archive_dst.mkdir(exist_ok=True)

    # ルート配下の .md を全コピー
    md_count = 0
    for f in MEM_SRC.glob("*.md"):
        shutil.copy2(f, MEM_DST / f.name)
        md_count += 1

    # archive サブフォルダの .md
    archive_src = MEM_SRC / "archive"
    if archive_src.exists():
        for f in archive_src.glob("*.md"):
            shutil.copy2(f, archive_dst / f.name)
            md_count += 1

    if md_count < 3:
        raise RuntimeError(f"memory同期失敗: {md_count}件しかコピーされていません（最低3件期待）")

    print(f"  ✅ memory synced: {md_count} files")


# ──────────────────────────────────────────────
# STEP 1: git status 確認
# ──────────────────────────────────────────────
def step1_check_status() -> bool:
    """変更があれば True。"""
    print("=== STEP 1: git status check ===")
    res = run(["git", "status", "--short"], cwd=REFFORT_ROOT)
    has_changes = bool(res.stdout.strip())
    print(f"  changes: {'YES' if has_changes else 'no'}")
    return has_changes


# ──────────────────────────────────────────────
# STEP 2-3: 機密ファイル混入チェック
# ──────────────────────────────────────────────
SENSITIVE_NAME_PATTERNS = [
    re.compile(r"(^|/)\.env(?:\.|$)"),                                  # .env, .env.vps, .env.local 等
    re.compile(r"\.env\.[A-Za-z0-9_-]+$"),                              # foo.env.bak 等の末尾
    re.compile(r"(credentials|secret|token|private_key|apikey|api_key|access_key)", re.IGNORECASE),
    re.compile(r"\.(pem|key|p12|pfx)$"),
]


def detect_sensitive_files(file_list: list[str]) -> list[str]:
    hits = []
    for f in file_list:
        for pat in SENSITIVE_NAME_PATTERNS:
            if pat.search(f):
                hits.append(f)
                break
    return hits


def step2_stage_and_check() -> list[str]:
    """ステージングして機密ファイル混入をチェック。混入あれば例外。"""
    print("=== STEP 2: stage and sensitive-file check ===")
    run(["git", "add", "-A"], cwd=REFFORT_ROOT)
    # --diff-filter=AM で「追加・変更」のみチェック（削除commitは機密混入とみなさない）
    res = run(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"], cwd=REFFORT_ROOT)
    staged_files = [l.strip() for l in res.stdout.splitlines() if l.strip()]
    print(f"  staged (A/M only for sensitive check): {len(staged_files)} files")

    sensitive = detect_sensitive_files(staged_files)
    if sensitive:
        # 即座にreset
        print(f"  🚨 sensitive files detected: {sensitive}")
        run(["git", "reset", "HEAD"], cwd=REFFORT_ROOT, check=False)
        raise RuntimeError(f"機密ファイル混入検出: {sensitive}")

    return staged_files


# ──────────────────────────────────────────────
# STEP 3: commit & push
# ──────────────────────────────────────────────
def step3_commit_and_push() -> None:
    print("=== STEP 3: commit & push ===")
    today = datetime.now(JST).strftime("%Y-%m-%d")
    msg = f"自動バックアップ：{today}（memory同期込み）"
    if DRY_RUN:
        print(f"  [DRY_RUN] would commit with: {msg!r} and push to origin/{BRANCH}")
        return
    run(["git", "commit", "-m", msg], cwd=REFFORT_ROOT)
    run(["git", "push", "origin", BRANCH], cwd=REFFORT_ROOT)
    print(f"  ✅ pushed to origin/{BRANCH}")


# ──────────────────────────────────────────────
# メイン
# ──────────────────────────────────────────────
def main() -> int:
    print(f"=== daily-github-backup 開始 (DRY_RUN={DRY_RUN}) ===")
    step = "init"
    try:
        step = "STEP 0 memory sync"
        step0_sync_memory()

        step = "STEP 1 git status"
        if not step1_check_status():
            print("=== 完了 (変更なし・終了) ===")
            return 0

        step = "STEP 2 stage and sensitive check"
        staged = step2_stage_and_check()

        step = "STEP 3 commit and push"
        step3_commit_and_push()

        print(f"=== 完了 ({len(staged)} files) ===")
        return 0

    except BaseException as e:
        traceback.print_exc()
        detail = str(e)[:1500]
        suggestion = ""
        if "機密ファイル混入検出" in detail:
            suggestion = ".gitignore への追加を検討してください"
        elif "Authentication failed" in detail or "could not read Username" in detail:
            suggestion = "GitHub認証情報を再設定してください（gh auth login）"
        elif "rejected" in detail or "non-fast-forward" in detail:
            suggestion = "リモートと履歴がズレています。手動で git pull --rebase を試してください"
        report_failure(step, detail, suggestion)
        return 1


if __name__ == "__main__":
    sys.exit(main())
