"""
指定ケースをv2 vs v2.1で並べて比較するスクリプト
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


def load_prompt(version: str) -> str:
    # "2" → prompt_admin_v2.md, "2.1" → prompt_admin_v2.1.md
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


def call_api(messages: list) -> dict:
    client = OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7
    )
    text = response.choices[0].message.content
    try:
        j = json.loads(text)
        return {
            "buyer": j.get("buyerLanguage", "(buyerLanguage missing)"),
            "jpn":   j.get("jpnLanguage",   "(jpnLanguage missing)"),
            "ok": True,
            "tokens": response.usage.total_tokens
        }
    except json.JSONDecodeError:
        return {"buyer": text, "jpn": "(JSON parse failed)", "ok": False,
                "tokens": response.usage.total_tokens}


def get_last_buyer_messages(messages):
    last_assistant = -1
    for i, m in enumerate(messages):
        if m["role"] == "assistant":
            last_assistant = i
    result = []
    for m in messages[last_assistant + 1:]:
        if m["role"] == "user":
            result.append(m["content"])
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# テスト対象：ケース番号とバイヤーメッセージの説明
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CASES = [
    {
        "file": "gpt_request_2.json",
        "label": "ケース#2 — バイヤー「Thank you」",
        "note": "問題：単純な感謝に余計な返信を生成している",
    },
    {
        "file": "gpt_request_3.json",
        "label": "ケース#3 — キャンセル懸念→住所確認済み",
        "note": "問題：解決済みのキャンセル話題を蒸し返している",
    },
    {
        "file": "gpt_request_5.json",
        "label": "ケース#5 — 発送日・商品問い合わせ",
        "note": "問題：聞かれていない「発送を早められない」を勝手に付け加えている",
    },
]

VERSIONS = ["2", "2.1"]

prompt_v2   = load_prompt("2")
prompt_v2_1 = load_prompt("2.1")
prompts = {"2": prompt_v2, "2.1": prompt_v2_1}

for case in CASES:
    filepath = os.path.join(BASE_DIR, case["file"])
    with open(filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)

    last_buyer = get_last_buyer_messages(raw)

    print(f"\n{'█' * 70}")
    print(f"  {case['label']}")
    print(f"  ⚠ {case['note']}")
    print(f"{'█' * 70}")
    print("\n【バイヤーの最新メッセージ】")
    if last_buyer:
        for msg in last_buyer:
            print(msg)
    else:
        # 最後のuserメッセージを探す
        for m in reversed(raw):
            if m["role"] == "user":
                print(m["content"])
                break

    results = {}
    for v in VERSIONS:
        msgs = replace_admin_prompt(raw, prompts[v])
        results[v] = call_api(msgs)
        time.sleep(1)

    print(f"\n{'─' * 35} v2.0 {'─' * 35}")
    print(f"\n[英語]\n{results['2']['buyer']}")
    print(f"\n[日本語]\n{results['2']['jpn']}")
    print(f"\nトークン: {results['2']['tokens']}")

    print(f"\n{'─' * 34} v2.1 {'─' * 34}")
    print(f"\n[英語]\n{results['2.1']['buyer']}")
    print(f"\n[日本語]\n{results['2.1']['jpn']}")
    print(f"\nトークン: {results['2.1']['tokens']}")

print("\n\n完了")
