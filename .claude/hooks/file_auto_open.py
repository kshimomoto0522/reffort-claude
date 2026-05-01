#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostToolUse hook: 社長が直接操作するファイルのみWrite/Edit直後に自動オープン。

■ 自動オープン対象（厳選）:
  .env / .env.*    : 値入力用（社長が手入力する必要がある）
  .xlsx / .xlsm    : 表計算（成果物・納品物）
  .pptx            : スライド（成果物・納品物）
  .pdf             : 文書（成果物・納品物）

■ 自動オープン対象外（Claudeが手動判断で開く）:
  .md / .html / .txt / .csv : 頻繁に編集されるため自動オープンすると大量に開く。
    Claudeが成果物・結果・社長確認必要と判断した時だけ手動で start する。
  .py / .json / .yml / .toml / .sh 等 : コード/設定ファイル

■ ディレクトリ除外:
  .claude/, archive/, memory/, node_modules/, .git/, __pycache__/
"""
import json
import sys
import os
import re
from pathlib import Path

# stderrをUTF-8強制 (Claude Code側がUTF-8で読むため)
try:
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass


ENV_BASENAME_RE = re.compile(r"^\.env(\..+)?$")
# 成果物・社長が直接操作するファイルのみ（.md/.html/.txt/.csvはClaude手動判断）
DELIVERABLE_EXTS = {".xlsx", ".xlsm", ".pptx", ".pdf"}
EXCLUDE_DIR_NAMES = {".claude", "archive", "memory", "node_modules", ".git", "__pycache__"}


def is_excluded_path(p: Path) -> bool:
    parts_lower = {part.lower() for part in p.parts}
    return bool(EXCLUDE_DIR_NAMES & parts_lower)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    tool_input = data.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    p = Path(file_path)
    if not p.exists():
        sys.exit(0)

    basename = p.name
    suffix = p.suffix.lower()

    # .env 系判定（拡張子ではなくbasenameで判定）
    is_env = bool(ENV_BASENAME_RE.match(basename))

    if is_env:
        target = p
    else:
        if is_excluded_path(p):
            sys.exit(0)
        if suffix not in DELIVERABLE_EXTS:
            sys.exit(0)
        target = p

    # 既定アプリで開く
    try:
        os.startfile(str(target))  # type: ignore[attr-defined]
        kind = ".env(値入力用)" if is_env else f"{suffix}(成果物)"
        print(
            f"[file_auto_open] Opened: {target} [{kind}]\n"
            f"[file_auto_open] REMINDER: 社長に「{target.name} を開きました」と必ず先に宣言してから次に進むこと。",
            file=sys.stderr,
        )
    except Exception as e:
        print(
            f"[file_auto_open] Failed to open {target}: {e}\n"
            f"[file_auto_open] 手動で `start \"\" \"{target}\"` を実行してください。",
            file=sys.stderr,
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
