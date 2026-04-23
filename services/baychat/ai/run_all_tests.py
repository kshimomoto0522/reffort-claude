"""
全テストケースをv2プロンプトで一括実行するスクリプト
"""

import json
import sys
import os
import io
import re
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from openai import OpenAI

# APIキーは.envファイルから読み込む（直接書かない）
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4.1-mini"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_prompt_from_md(version: str) -> str:
    md_file = os.path.join(BASE_DIR, f"prompt_admin_v{version}.md")
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"```\n(.*?)```", content, re.DOTALL)
    if not match:
        raise ValueError(f"プロンプト本文が見つかりません: {md_file}")
    return match.group(1).strip()


def is_admin_prompt(content: str) -> bool:
    return "ROLE" in content and "CONVERSATION STAGE DETECTION" in content and "TONE" in content


def replace_admin_prompt(messages: list, new_prompt: str) -> list:
    replaced = []
    for msg in messages:
        if msg["role"] == "developer" and is_admin_prompt(msg.get("content", "")):
            replaced.append({"role": "developer", "content": "\n" + new_prompt + "\n"})
        else:
            replaced.append(msg)
    return replaced


def get_latest_buyer_messages(messages: list) -> list:
    """最後のassistantメッセージ以降のuserメッセージをすべて返す"""
    last_assistant_idx = -1
    for i, m in enumerate(messages):
        if m["role"] == "assistant":
            last_assistant_idx = i

    unread = []
    for m in messages[last_assistant_idx + 1:]:
        if m["role"] == "user":
            unread.append(m["content"])
    return unread


if __name__ == "__main__":
    prompt_v2 = load_prompt_from_md("2.1")
    client = OpenAI(api_key=API_KEY)

    # 対象ファイル（番号付きのみ）
    test_files = sorted([
        f for f in os.listdir(BASE_DIR)
        if f.startswith("gpt_request_") and f.endswith(".json")
    ])

    print(f"対象ファイル: {len(test_files)}件")
    print(f"プロンプト: v2.1")
    print("=" * 70)

    total_tokens = 0

    for filename in test_files:
        filepath = os.path.join(BASE_DIR, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                raw = f.read().strip()
                if not raw or raw.startswith("<"):
                    print(f"\n⚠️  {filename}: スキップ（JSONではありません）")
                    continue
                parsed = json.loads(raw)
                # 新形式 {"model": ..., "input": [...]} と旧形式 [...] の両対応
                if isinstance(parsed, dict) and "input" in parsed:
                    messages = parsed["input"]
                else:
                    messages = parsed
        except Exception as e:
            print(f"\n⚠️  {filename}: 読み込みエラー ({e})")
            continue

        # プロンプト差し替え
        messages = replace_admin_prompt(messages, prompt_v2)

        # バイヤーの未読メッセージ
        unread = get_latest_buyer_messages(messages)

        print(f"\n{'━' * 70}")
        print(f"  ケース: {filename}")
        print(f"{'━' * 70}")

        # 会話履歴を全件表示（developerロール=プロンプト系は省略）
        print("【会話履歴（全件）】")
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "developer":
                if is_admin_prompt(content):
                    print(f"  [developer: adminプロンプト（省略）]")
                else:
                    # ベースプロンプトやフォーマットブロックは短く表示
                    preview = content.strip()[:80].replace("\n", " ")
                    print(f"  [developer]: {preview}...")
            elif role == "user":
                print(f"  [buyer]: {content}")
            elif role == "assistant":
                print(f"  [seller]: {content}")
            elif role == "system":
                print(f"  [event]: {content}")
        print()

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.7
            )
            result_text = response.choices[0].message.content
            tokens = response.usage.total_tokens
            total_tokens += tokens

            try:
                result_json = json.loads(result_text)
                buyer_reply = result_json.get("buyerLanguage", "（buyerLanguageなし）")
                jpn_reply   = result_json.get("jpnLanguage", "（jpnLanguageなし）")
                print("\n【生成された返信（英語）】")
                print(buyer_reply)
                print("\n【日本語訳】")
                print(jpn_reply)
            except json.JSONDecodeError:
                print("\n【生成結果（JSONパース失敗）】")
                print(result_text)

            print(f"\nトークン: {tokens}")

        except Exception as e:
            print(f"\n❌ APIエラー: {e}")

        time.sleep(1)  # レート制限対策

    print(f"\n{'=' * 70}")
    print(f"完了。合計トークン使用量: {total_tokens}")
