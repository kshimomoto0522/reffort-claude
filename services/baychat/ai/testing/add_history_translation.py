# -*- coding: utf-8 -*-
"""
既存のテストケースJSONに history_ja と buyer_message_ja を後付けするスクリプト。
extract_cases.py の translate_to_japanese() を再利用。

使い方:
    python add_history_translation.py test_cases/balanced_18cases_v25_20260421.json
"""
import os
import sys
import json
import argparse

# Windows環境のコンソール出力をUTF-8化
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from extract_cases import translate_to_japanese


def extract_user_assistant_contents(input_messages):
    """input配列からuser/assistantメッセージのcontentだけ抽出（system除外）"""
    results = []
    for msg in input_messages:
        role = msg.get("role", "")
        if role in ("user", "assistant"):
            content = msg.get("content", "")
            # タイムスタンプを除いた本文を渡す（翻訳の品質向上）
            results.append(content)
    return results


def main(json_path):
    cases = json.load(open(json_path, encoding="utf-8"))
    print(f"[1] {len(cases)}ケース読み込み完了")

    # 1. buyer_message の翻訳
    buyer_messages = [c.get("buyer_message", "") for c in cases]
    print(f"[2] buyer_message 翻訳中 ({len(buyer_messages)}件)...")
    buyer_jas = translate_to_japanese(buyer_messages)

    for i, c in enumerate(cases):
        c["buyer_message_ja"] = buyer_jas[i] if i < len(buyer_jas) else ""

    # 2. 各ケースの input 配列 user/assistant を翻訳
    print(f"[3] 各ケースの会話履歴を翻訳中...")
    for idx, c in enumerate(cases, 1):
        ua_contents = extract_user_assistant_contents(c.get("input", []))
        if not ua_contents:
            c["history_ja"] = []
            continue
        print(f"  ケース {idx}/{len(cases)} ({c.get('id')}): {len(ua_contents)}件")
        history_ja = translate_to_japanese(ua_contents)
        c["history_ja"] = history_ja

    # 3. 保存
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    print(f"[4] 保存完了: {json_path}")

    # サンプル確認
    print()
    print("=== サンプル: ケース1 ===")
    c = cases[0]
    print(f"id: {c.get('id')}")
    print(f"buyer_message_ja: {c.get('buyer_message_ja', '')[:80]}")
    print(f"history_ja ({len(c.get('history_ja', []))}件):")
    for i, ja in enumerate(c.get("history_ja", [])[:3]):
        print(f"  [{i}] {ja[:80]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", help="テストケースJSONへのパス")
    args = parser.parse_args()
    main(args.json_path)
