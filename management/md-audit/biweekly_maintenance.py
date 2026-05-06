#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
biweekly-claude-maintenance — 隔週Claude Codeメンテナンス

第1・第3月曜 10:00 にスケジュールタスクから自動実行されることを想定:
1. 現状計測（CLAUDE.md行数・memory・settings・hook発火件数の前回比）
2. Chatwork個人DM(426170119)に現状報告＋「/隔週メンテナンス で詳細分析」誘導
3. audit_log.csv に追記・reports/YYYY-MM-DD.md に詳細レポート保存

詳細な5層最新情報調査・松竹梅提案は /隔週メンテナンス スラッシュコマンド（T13）で実施。
本スクリプトは「定量計測＋通知トリガー」に専念する設計。
"""

import os
import sys
import csv
import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timedelta

# Windows CP932 環境でも絵文字のprintが通るようUTF-8を強制（Python 3.7+）
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ python-dotenv 未インストール。`pip install python-dotenv` で導入してください。")
    sys.exit(2)

# プロジェクトルート判定（__file__基準・相対パス）
SCRIPT_DIR = Path(__file__).resolve().parent  # management/md-audit/
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # reffort/

# .env から CW_TOKEN 読込（commerce/ebay/analytics/.env を流用）
ENV_PATH = PROJECT_ROOT / "commerce/ebay/analytics/.env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()  # カレント or その他の .env を探す

CW_TOKEN = os.getenv("CW_TOKEN")
CHATWORK_ROOM_ID = "426170119"  # 社長個人DM

# 3段階分類の閾値
THRESHOLD_GREEN = 200
THRESHOLD_YELLOW = 300


def measure_claude_md():
    """全プロジェクト配下のCLAUDE.md行数を計測（archive/除外）"""
    results = []
    for md in PROJECT_ROOT.rglob("CLAUDE.md"):
        # archive/ や .git/ を除外
        parts_str = str(md).replace("\\", "/")
        if "/archive/" in parts_str or "/.git/" in parts_str:
            continue
        try:
            lines = len(md.read_text(encoding="utf-8").splitlines())
            rel = md.relative_to(PROJECT_ROOT).as_posix()
            if lines <= THRESHOLD_GREEN:
                status = "🟢"
            elif lines <= THRESHOLD_YELLOW:
                status = "🟡"
            else:
                status = "🔴"
            results.append({"path": rel, "lines": lines, "status": status})
        except Exception as e:
            results.append({"path": str(md), "lines": 0, "status": f"❌ {e}"})
    return sorted(results, key=lambda x: -x["lines"])


def measure_settings():
    """settings.local.json の allow件数・deny件数・全体行数"""
    settings_path = PROJECT_ROOT / ".claude/settings.local.json"
    if not settings_path.exists():
        return {"total_lines": 0, "allow_count": 0, "deny_count": 0}
    content = settings_path.read_text(encoding="utf-8")
    total_lines = len(content.splitlines())
    try:
        data = json.loads(content)
        allow_count = len(data.get("permissions", {}).get("allow", []))
        deny_count = len(data.get("permissions", {}).get("deny", []))
    except json.JSONDecodeError:
        allow_count = 0
        deny_count = 0
    return {"total_lines": total_lines, "allow_count": allow_count, "deny_count": deny_count}


def measure_memory():
    """memory/ のファイル数・合計行数（archive/除外）"""
    memory_dir = Path.home() / ".claude/projects/C--Users-KEISUKE-SHIMOMOTO-Desktop-reffort/memory"
    if not memory_dir.exists():
        return {"file_count": 0, "total_lines": 0}
    files = [f for f in memory_dir.glob("*.md") if f.is_file()]
    total_lines = 0
    for f in files:
        try:
            total_lines += len(f.read_text(encoding="utf-8").splitlines())
        except Exception:
            pass
    return {"file_count": len(files), "total_lines": total_lines}


def measure_effort_booster_log():
    """effort_booster.log の直近2週間の発火件数"""
    log_path = PROJECT_ROOT / ".claude/hooks/effort_booster.log"
    if not log_path.exists():
        return {"total_fires_2weeks": 0, "last_line": "(ログ未生成)"}
    try:
        lines = log_path.read_text(encoding="utf-8").splitlines()
        now = datetime.now()
        two_weeks_ago = now - timedelta(days=14)
        count = 0
        for line in lines:
            # 先頭 YYYY-MM-DD を判定
            if len(line) >= 10 and line[4] == "-" and line[7] == "-":
                try:
                    dt = datetime.strptime(line[:10], "%Y-%m-%d")
                    if dt >= two_weeks_ago:
                        count += 1
                except ValueError:
                    continue
        return {"total_fires_2weeks": count, "last_line": lines[-1] if lines else ""}
    except Exception:
        return {"total_fires_2weeks": 0, "last_line": ""}


def load_previous_snapshot():
    """audit_log.csv の最新行を前回値として返す"""
    log_path = SCRIPT_DIR / "audit_log.csv"
    if not log_path.exists():
        return None
    try:
        with log_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        return rows[-1] if rows else None
    except Exception:
        return None


def format_diff(current, previous):
    """前回比の表示（+N / -N / ±0）"""
    if previous is None:
        return "初回"
    try:
        prev = int(previous)
        cur = int(current)
        diff = cur - prev
        if diff == 0:
            return "±0"
        return f"{'+' if diff > 0 else ''}{diff}"
    except (ValueError, TypeError):
        return "—"


def save_audit_log(snapshot):
    """audit_log.csv に追記"""
    log_path = SCRIPT_DIR / "audit_log.csv"
    is_new = not log_path.exists()
    with log_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(snapshot.keys()))
        if is_new:
            writer.writeheader()
        writer.writerow(snapshot)


def save_detailed_report(date_str, content):
    """reports/YYYY-MM-DD.md に詳細レポート保存"""
    reports_dir = SCRIPT_DIR / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / f"{date_str}.md"
    report_path.write_text(content, encoding="utf-8")


def post_to_chatwork(body):
    """Chatwork個人DM(426170119)に箱型カード形式で通知"""
    if not CW_TOKEN:
        print("❌ CW_TOKEN が未設定（.env確認）")
        return False
    url = f"https://api.chatwork.com/v2/rooms/{CHATWORK_ROOM_ID}/messages"
    data = urllib.parse.urlencode({"body": body}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("X-ChatWorkToken", CW_TOKEN)
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            print(f"✅ Chatwork通知送信完了")
            return True
    except Exception as e:
        print(f"❌ Chatwork送信失敗: {e}")
        return False


def build_chatwork_body(claude_md_list, settings, memory, effort_log, prev):
    """Chatwork通知本文（箱型カード）を構築"""
    today = datetime.now().strftime("%Y-%m-%d")

    # 前回比のキー
    prev_root_lines = prev.get("root_claude_md_lines") if prev else None
    prev_allow = prev.get("settings_allow") if prev else None
    prev_memory = prev.get("memory_file_count") if prev else None

    root_claude = next((c for c in claude_md_list if c["path"] == "CLAUDE.md"), None)
    root_lines = root_claude["lines"] if root_claude else 0
    root_status = root_claude["status"] if root_claude else "❌"

    # 3段階の件数
    green = sum(1 for c in claude_md_list if c["status"] == "🟢")
    yellow = sum(1 for c in claude_md_list if c["status"] == "🟡")
    red = sum(1 for c in claude_md_list if c["status"] == "🔴")

    top3 = claude_md_list[:3]
    top3_str = "\n".join([f"・{c['status']} {c['path']}: {c['lines']}行" for c in top3])

    body = f"""[info][title]📊 隔週Claude Codeメンテナンス｜{today}[/title]
■ 現状計測（前回比）
・ルートCLAUDE.md: {root_lines}行 ({format_diff(root_lines, prev_root_lines)}) {root_status}
・settings.local.json allow: {settings['allow_count']}件 ({format_diff(settings['allow_count'], prev_allow)})
・memory: {memory['file_count']}ファイル ({format_diff(memory['file_count'], prev_memory)}) / 合計{memory['total_lines']}行
・effort_booster 直近2週間発火: {effort_log['total_fires_2weeks']}件

■ CLAUDE.md 3段階分類（全{len(claude_md_list)}ファイル）
・🟢正常 ≤200行: {green}件
・🟡警告 201-300行: {yellow}件
・🔴超過 301行以上: {red}件

■ 行数Top 3
{top3_str}

■ 次のアクション
新セッションで「/隔週メンテナンス」を実行すると、Claudeが5層（公式・Boris Cherny・GitHub Trending・コミュニティ・事業側）を調査して松竹梅提案を生成します。社長判断→実行→結果を本DMに再送信。

詳細レポート: management/md-audit/reports/{today}.md[/info]"""

    return body


def build_detailed_report(date_str, claude_md_list, settings, memory, effort_log, prev):
    """reports/YYYY-MM-DD.md の詳細レポート本文"""
    lines_detail = []
    lines_detail.append(f"# 隔週Claude Codeメンテナンス レポート {date_str}")
    lines_detail.append("")
    lines_detail.append("## 現状計測")
    lines_detail.append("")
    lines_detail.append("### CLAUDE.md 全ファイル行数（archive除外）")
    lines_detail.append("")
    lines_detail.append("| パス | 行数 | 3段階 |")
    lines_detail.append("|------|-----:|:---:|")
    for c in claude_md_list:
        lines_detail.append(f"| {c['path']} | {c['lines']} | {c['status']} |")
    lines_detail.append("")
    lines_detail.append("### settings.local.json")
    lines_detail.append(f"- 全体行数: {settings['total_lines']}")
    lines_detail.append(f"- allow件数: {settings['allow_count']}")
    lines_detail.append(f"- deny件数: {settings['deny_count']}")
    lines_detail.append("")
    lines_detail.append("### memory/")
    lines_detail.append(f"- ファイル数: {memory['file_count']}")
    lines_detail.append(f"- 合計行数: {memory['total_lines']}")
    lines_detail.append("")
    lines_detail.append("### effort_booster.log")
    lines_detail.append(f"- 直近2週間の発火件数: {effort_log['total_fires_2weeks']}")
    lines_detail.append(f"- 最終行: `{effort_log['last_line']}`")
    lines_detail.append("")
    lines_detail.append("## 前回比")
    if prev:
        lines_detail.append("| 項目 | 前回 | 今回 | 差分 |")
        lines_detail.append("|------|-----:|-----:|:----:|")
        root_claude = next((c for c in claude_md_list if c["path"] == "CLAUDE.md"), None)
        root_now = root_claude["lines"] if root_claude else 0
        lines_detail.append(f"| ルートCLAUDE.md行数 | {prev.get('root_claude_md_lines', '—')} | {root_now} | {format_diff(root_now, prev.get('root_claude_md_lines'))} |")
        lines_detail.append(f"| settings allow件数 | {prev.get('settings_allow', '—')} | {settings['allow_count']} | {format_diff(settings['allow_count'], prev.get('settings_allow'))} |")
        lines_detail.append(f"| memoryファイル数 | {prev.get('memory_file_count', '—')} | {memory['file_count']} | {format_diff(memory['file_count'], prev.get('memory_file_count'))} |")
    else:
        lines_detail.append("初回のため前回比なし")
    lines_detail.append("")
    lines_detail.append("## 次のアクション")
    lines_detail.append("- Claude Codeで `/隔週メンテナンス` を実行 → 5層調査＋松竹梅提案を生成")
    lines_detail.append("- 社長判断の上で改善実施")
    lines_detail.append("")
    return "\n".join(lines_detail)


def is_first_or_third_monday():
    """今日が第1月曜 or 第3月曜なら True（cron単独では表現不可のためPython側でガード）"""
    today = datetime.now()
    if today.weekday() != 0:  # 0=Monday
        return False
    return 1 <= today.day <= 7 or 15 <= today.day <= 21


def main():
    # 第1・第3月曜ガード（--force で強制実行可）
    # --dry-run 指定時は計測のみで、レポート保存／audit_log追記／Chatwork送信を全てスキップ
    force = "--force" in sys.argv
    dry_run = "--dry-run" in sys.argv

    if not force and not is_first_or_third_monday():
        today = datetime.now()
        print(f"⏭ スキップ: {today.strftime('%Y-%m-%d (%A)')} は第1・第3月曜ではありません。--force で強制実行可")
        return 0

    mode_label = "[DRY-RUN] " if dry_run else ""
    print(f"=== {mode_label}biweekly-claude-maintenance 実行: {datetime.now().isoformat()} ===")

    print("[1/5] 現状計測...")
    claude_md_list = measure_claude_md()
    settings = measure_settings()
    memory = measure_memory()
    effort_log = measure_effort_booster_log()

    print(f"  CLAUDE.md: {len(claude_md_list)}ファイル")
    print(f"  settings allow: {settings['allow_count']}件")
    print(f"  memory: {memory['file_count']}ファイル / {memory['total_lines']}行")

    print("[2/5] 前回スナップショット読込...")
    prev = load_previous_snapshot()

    print("[3/5] レポート生成...")
    today = datetime.now().strftime("%Y-%m-%d")
    detailed = build_detailed_report(today, claude_md_list, settings, memory, effort_log, prev)
    if dry_run:
        print(f"  [DRY-RUN] reports/{today}.md 保存スキップ")
    else:
        save_detailed_report(today, detailed)
        print(f"  reports/{today}.md 保存完了")

    print("[4/5] audit_log.csv 追記...")
    root_claude = next((c for c in claude_md_list if c["path"] == "CLAUDE.md"), None)
    snapshot = {
        "date": today,
        "root_claude_md_lines": root_claude["lines"] if root_claude else 0,
        "claude_md_count": len(claude_md_list),
        "claude_md_green": sum(1 for c in claude_md_list if c["status"] == "🟢"),
        "claude_md_yellow": sum(1 for c in claude_md_list if c["status"] == "🟡"),
        "claude_md_red": sum(1 for c in claude_md_list if c["status"] == "🔴"),
        "settings_total": settings["total_lines"],
        "settings_allow": settings["allow_count"],
        "settings_deny": settings["deny_count"],
        "memory_file_count": memory["file_count"],
        "memory_total_lines": memory["total_lines"],
        "effort_booster_fires_2weeks": effort_log["total_fires_2weeks"],
    }
    if dry_run:
        print("  [DRY-RUN] audit_log.csv 追記スキップ")
    else:
        save_audit_log(snapshot)

    print("[5/5] Chatwork個人DMへ送信...")
    if dry_run:
        print("  [DRY-RUN] Chatwork送信スキップ（プレビューのみ表示）")
        body = build_chatwork_body(claude_md_list, settings, memory, effort_log, prev)
        print("--- 送信予定本文（プレビュー） ---")
        print(body)
        print("--- ここまで ---")
        success = True
    else:
        body = build_chatwork_body(claude_md_list, settings, memory, effort_log, prev)
        success = post_to_chatwork(body)

    if success:
        suffix = "（DRY-RUNのため副作用なし）" if dry_run else ""
        print(f"\n✅ 隔週メンテナンス実行完了{suffix}")
        return 0
    else:
        print("\n⚠️ Chatwork送信失敗（レポート・ログは保存済み）")
        return 1


if __name__ == "__main__":
    sys.exit(main())
