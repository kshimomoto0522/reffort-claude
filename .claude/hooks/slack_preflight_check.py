#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PreToolUse hook: Slack送信ルール違反を機械的にブロック
====================================================================
対象ツール:
  - mcp__slack__slack_post_message
  - mcp__slack__slack_reply_to_thread

チェック項目:
  1. post_message で本文（改行含む）を直接投稿 → ブロック（スレッドタイトルのみ許可）
  2. メンションが <@U...> 形式でない → ブロック
  3. 「ベトナム語」を含む → ブロック
  4. reply_to_thread に thread_ts がない → ブロック

Exit code 2 + stderrメッセージ = ブロック。Exit code 0 = 許可。

再発防止の根拠:
  2026-04-06: チャンネル直投稿でスレッド構造無視
  2026-04-16: 同じミスを再発 + メンション形式誤り + ベトナム語OK記載
  → 人間の注意力に依存せず、フックで機械的にブロックする
"""

import io
import json
import re
import sys

# Windowsコンソール文字化け対策
try:
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass


def block(reason: str, detail: str = "") -> None:
    """ブロックメッセージを出してexit 2"""
    msg = (
        "\n=============================================================\n"
        f"🛑 BLOCKED: Slack送信ルール違反\n"
        "=============================================================\n"
        f"違反: {reason}\n"
    )
    if detail:
        msg += f"詳細: {detail}\n"
    msg += (
        "-------------------------------------------------------------\n"
        "正しい手順:\n"
        "  1. slack_post_message でスレッドタイトル（太字1行のみ）を投稿\n"
        "  2. 返ってきた ts を使って slack_reply_to_thread でメンション付き本文を返信\n"
        "  3. メンションは <@USER_ID> 形式（テキスト @名前 は不可）\n"
        "  4. 言語は日本語のみ（「ベトナム語でもOK」等は禁止）\n"
        "\n"
        "User IDs:\n"
        "  クエットさん: <@U04HGPBABQU>\n"
        "  社長: <@U048ZRU4KLG>\n"
        "=============================================================\n"
    )
    sys.stderr.write(msg)
    sys.exit(2)


def check_post_message(text: str) -> None:
    """slack_post_message のテキストをチェック"""
    # ルール1: 改行を含むテキストはスレッドタイトルではない → ブロック
    if "\n" in text:
        block(
            "post_message に改行を含む本文を直接投稿しようとしています",
            "スレッドタイトル（太字1行）のみ許可。本文は reply_to_thread を使ってください。"
        )

    # ルール1補足: 長すぎるテキストもタイトルではない可能性
    if len(text) > 200:
        block(
            "post_message のテキストが200文字を超えています",
            f"現在 {len(text)} 文字。スレッドタイトルは短い太字1行のみ許可。"
        )


def check_common(text: str) -> None:
    """post_message / reply_to_thread 共通チェック"""
    # ルール2: @名前 形式のメンション（<@U...> でない）を検出
    # @で始まり、直後に<がない（= Slack API形式でない）パターンを検出
    # ただし メールアドレス（xxx@yyy.zzz）は除外
    plain_mention = re.findall(r"(?<!\S)@(?!<)([A-Za-z][A-Za-z0-9_ ]{2,30})", text)
    if plain_mention:
        block(
            "メンションが <@USER_ID> 形式になっていません",
            f"検出されたテキストメンション: {plain_mention}。"
            " Slack APIでは @名前 と書いてもメンションにならない。"
            " <@U04HGPBABQU> のような形式を使うこと。"
        )

    # ルール3: ベトナム語への言及を禁止
    if "ベトナム語" in text:
        block(
            "「ベトナム語」への言及が含まれています",
            "社長が読めない言語での回答を求めない。日本語のみ。"
        )


def check_reply_to_thread(tool_input: dict) -> None:
    """reply_to_thread 固有チェック"""
    thread_ts = tool_input.get("thread_ts", "")
    if not thread_ts:
        block(
            "reply_to_thread に thread_ts が指定されていません",
            "必ず先に post_message でスレッドを作成し、返却された ts を指定すること。"
        )


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}

    if tool_name == "mcp__slack__slack_post_message":
        text = tool_input.get("text", "")
        check_common(text)
        check_post_message(text)

    elif tool_name == "mcp__slack__slack_reply_to_thread":
        text = tool_input.get("text", "")
        check_common(text)
        check_reply_to_thread(tool_input)

    else:
        # Slack送信ツール以外は対象外
        sys.exit(0)

    # すべてのチェックを通過 → 許可
    sys.exit(0)


if __name__ == "__main__":
    main()
