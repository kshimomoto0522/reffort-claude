#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostToolUse hook: .envファイルをWrite/Editした直後に自動でエクスプローラ/既定エディタで開く。

目的:
  社長がAPIキー等を貼り付けられる状態にファイルを即座に開くルールを機械化。
  feedback_env_file_handling.md + feedback_file_delivery.md に対応する実装。

発火条件:
  tool_name == "Write" or "Edit"
  かつ 対象ファイルの basename が .env または .env.* にマッチ

動作:
  1. os.startfile(file_path) で既定アプリで開く (Windows)
  2. stderrに通知を出し、Claude側に「開きました」宣言を促す
"""
import json
import sys
import os
import re

# stderrをUTF-8強制 (Claude Code側がUTF-8で読むため)
try:
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass


ENV_BASENAME_RE = re.compile(r"^\.env(\..+)?$")


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

    basename = os.path.basename(file_path)
    if not ENV_BASENAME_RE.match(basename):
        sys.exit(0)

    if not os.path.exists(file_path):
        sys.exit(0)

    # Windows: 既定アプリで開く
    try:
        os.startfile(file_path)  # type: ignore[attr-defined]
        # Claudeに通知 (stderrはtranscriptに出る)
        print(
            f"[env_auto_open] Opened: {file_path}\n"
            f"[env_auto_open] REMINDER: 社長に『{basename} を開きました』と必ず宣言してから次に進むこと。",
            file=sys.stderr,
        )
    except Exception as e:
        print(
            f"[env_auto_open] Failed to open {file_path}: {e}\n"
            f"[env_auto_open] 手動で `start \"\" \"{file_path}\"` を実行してください。",
            file=sys.stderr,
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
