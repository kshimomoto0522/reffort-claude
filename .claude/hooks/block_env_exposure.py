#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PreToolUse hook: Block any Bash command that would expose .env file contents
to the conversation stdout.

Blocks read-out commands (cat/type/more/less/head/tail/grep/rg/awk/sed/cut/strings)
when combined with a path containing ".env" (.env, .env.local, .env.vps, etc.).

Allows safe patterns:
  - python -c "... os.getenv(...) ... print('SET' if val else 'UNSET')"
  - dotenv programmatic usage
  - ls/find/stat on .env (metadata only, not contents)

Exit code 2 with stderr message = block. Exit code 0 = allow.
"""

import io
import json
import re
import sys

# Windowsコンソールで日本語が文字化けしないようstderrをUTF-8化
try:
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        # 入力不正時は安全側：ブロックしない（他のフックや通常処理に任せる）
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    tool_input = payload.get("tool_input", {}) or {}
    command = tool_input.get("command", "") or ""

    if not command:
        sys.exit(0)

    # ========================================
    # .env ファイル参照の検出
    # ========================================
    # .env単独 or .env.xxx（.env.local, .env.vps, .env.prod など）にマッチ
    # ファイル名区切り文字の直後が .env で始まるケース
    env_pattern = re.compile(r"(?:^|[\s/\\'\"=])\.env(?:\.[A-Za-z0-9_-]+)?(?=[\s'\"]|$|[;|&><])")

    if not env_pattern.search(command):
        sys.exit(0)

    # ========================================
    # 読み出し系コマンド検出
    # ========================================
    # コマンド名（パイプ・複合文の各セグメント頭）で判定する
    readout_cmds = {
        "cat", "type", "more", "less", "head", "tail",
        "grep", "rg", "ripgrep", "awk", "sed", "cut",
        "strings", "xxd", "od", "hexdump",
        "echo",  # echo $VAR で値を出す用途も含め一応
        "printenv", "env",
        "select-string", "gc", "get-content",
    }

    # コマンドを ; | && || でスプリットして各セグメントの先頭トークンを見る
    segments = re.split(r"(?:\|\||&&|\||;|`|\$\()", command)
    triggered_cmd = None
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        # 先頭トークン抽出（"cat foo" -> "cat"）
        m = re.match(r"\s*([A-Za-z0-9_.\\/\-]+)", seg)
        if not m:
            continue
        head_token = m.group(1).lower()
        # フルパス指定の場合は末尾だけ比較（/bin/cat -> cat）
        base = head_token.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        if base in readout_cmds and env_pattern.search(seg):
            triggered_cmd = base
            break

    if not triggered_cmd:
        # 読み出し系コマンドではない（pythonやdotenvでのプログラム的読み込み等は許可）
        sys.exit(0)

    # ========================================
    # ブロック（exit 2 + stderrメッセージ）
    # ========================================
    msg = (
        "\n=============================================================\n"
        "🛑 BLOCKED: .env ファイルの中身をチャットに出力する操作を禁止しています\n"
        "=============================================================\n"
        f"検出コマンド: {triggered_cmd}\n"
        f"コマンド全体: {command[:300]}\n"
        "-------------------------------------------------------------\n"
        "理由: .env にはAPIキー・DBパスワード等の機密が含まれます。\n"
        "      cat/grep等でstdoutに出すとClaudeセッションのログに残ります。\n"
        "\n"
        "✅ 正しい確認方法（値は表示せずSET/UNSETのみ）:\n"
        "   python -c \"import os; from dotenv import load_dotenv; load_dotenv(); print('SET' if os.getenv('KEY_NAME') else 'UNSET')\"\n"
        "\n"
        "✅ キー名だけ一覧したい場合:\n"
        "   python -c \"from dotenv import dotenv_values; print(list(dotenv_values('.env').keys()))\"\n"
        "\n"
        "✅ 値を書き込む必要がある場合（スクリプト経由のみ）:\n"
        "   Pythonで dotenv_values() → 編集 → 書き戻し。catやechoで中身を出さない。\n"
        "=============================================================\n"
    )
    sys.stderr.write(msg)
    sys.exit(2)  # ClaudeにブロックしたことをフィードバックするExit code


if __name__ == "__main__":
    main()
