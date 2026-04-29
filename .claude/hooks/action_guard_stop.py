#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stop hook: Claudeの最終応答テキストを走査し、社長に作業を丸投げするNGフレーズを検知して警告。

警告のみ（ブロックしない）。stderr出力＋exit 0。
将来的に証拠照合型（claim phrase × tool call evidence）に強化可能。

NG検知パターン:
  - 「ダブルクリックしてください」等の手動操作依頼
  - 「開いて確認してください」「探してください」等のファイル操作丸投げ
  - 「パスは〇〇です」だけで終わるpath-only応答
"""
import json
import sys
import os
import re
from pathlib import Path

try:
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass


# 検知パターン（再現性のあるものだけ厳選・誤検知を避ける）
NG_PATTERNS = [
    (re.compile(r"ダブルクリック"), "ダブルクリック依頼"),
    (re.compile(r"開いて(確認|チェック|レビュー)(してください|お願い|ください)"), "ファイルオープン依頼"),
    (re.compile(r"(エクスプローラー|フォルダ)で.*?(探|開いて)"), "フォルダから探させる依頼"),
    (re.compile(r"確認(してください|お願いします)$", re.MULTILINE), "確認依頼で終了（自分で開いて見せろ）"),
    (re.compile(r"右クリック.*?(開い|実行)"), "右クリック手動操作依頼"),
]


def read_last_assistant_text(transcript_path: str) -> str:
    """transcript JSONLから最終アシスタントメッセージのテキストを抽出。"""
    if not os.path.exists(transcript_path):
        return ""
    last_text = ""
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("type") != "assistant":
                    continue
                msg = obj.get("message", {})
                content = msg.get("content", [])
                if isinstance(content, str):
                    last_text = content
                elif isinstance(content, list):
                    parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            parts.append(block.get("text", ""))
                    last_text = "\n".join(parts)
    except Exception:
        return ""
    return last_text


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    transcript_path = data.get("transcript_path", "")
    if not transcript_path:
        sys.exit(0)

    text = read_last_assistant_text(transcript_path)
    if not text:
        sys.exit(0)

    hits = []
    for pat, label in NG_PATTERNS:
        if pat.search(text):
            hits.append(label)

    if not hits:
        sys.exit(0)

    # 警告のみ・ブロックしない
    print(
        "[action_guard] ⚠️ 自己完結原則違反の疑い検出（次回応答で修正してください）:\n"
        + "\n".join(f"  - {h}" for h in hits)
        + "\n  → Claudeが出来る事（開く/探す/確認）を社長に依頼するのは禁止です。"
        + "\n  → ファイルがあるなら `start \"\"` で開く・存在確認は自分でRead等で行う。"
        + "\n  → 詳細: .claude/rules/honesty_and_self_completion.md",
        file=sys.stderr,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
