"""
AI Reply プロンプトテストスクリプト
指定したgpt_request_*.jsonをOpenAI APIに投げて結果を確認する

使い方:
  python test_prompt.py                          # gpt_request_6.json × 現行プロンプト
  python test_prompt.py gpt_request_2.json       # 指定ファイル × 現行プロンプト
  python test_prompt.py gpt_request_6.json v2    # 指定ファイル × v2.0プロンプトで差し替え
  python test_prompt.py gpt_request_6.json v1 v2 # 両バージョンを並べて比較
"""

import json
import sys
import os
import io
import re

# UTF-8出力（Windowsの文字化け対策）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from openai import OpenAI

# APIキーは.envファイルから読み込む（直接書かない）
API_KEY = os.getenv("OPENAI_API_KEY")

# モデル（BayChatで使用中）
MODEL = "gpt-4.1-mini"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_prompt_from_md(version: str) -> str:
    """
    prompt_admin_v{version}.md からプロンプト本文（```ブロック内）を取り出す
    """
    md_file = os.path.join(BASE_DIR, f"prompt_admin_v{version}.md")
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    # ```〜``` の中身を抽出
    match = re.search(r"```\n(.*?)```", content, re.DOTALL)
    if not match:
        raise ValueError(f"{md_file} のプロンプト本文（```ブロック）が見つかりません")

    return match.group(1).strip()


def is_admin_prompt(content: str) -> bool:
    """
    developerメッセージがadminプロンプトかどうかを判定
    （ROLE・CONVERSATION STAGE DETECTION・TONEを含む長いもの）
    """
    return ("ROLE" in content and
            "CONVERSATION STAGE DETECTION" in content and
            "TONE" in content)


def replace_admin_prompt(messages: list, new_prompt: str) -> list:
    """
    messagesリストの中のadminプロンプトを新しいプロンプトに差し替える
    """
    replaced = []
    found = False
    for msg in messages:
        if msg["role"] == "developer" and is_admin_prompt(msg.get("content", "")):
            replaced.append({"role": "developer", "content": "\n" + new_prompt + "\n"})
            found = True
        else:
            replaced.append(msg)

    if not found:
        raise ValueError("adminプロンプトに該当するdeveloperメッセージが見つかりませんでした")

    return replaced


def run_test(json_file: str, prompt_version: str = None) -> dict:
    """
    指定ファイルでテストを実行して結果を返す
    prompt_version: "1", "2" など。Noneなら差し替えなし（JSONそのまま）
    """
    with open(json_file, "r", encoding="utf-8") as f:
        messages = json.load(f)

    # プロンプト差し替え
    if prompt_version:
        new_prompt = load_prompt_from_md(prompt_version)
        messages = replace_admin_prompt(messages, new_prompt)

    # OpenAI API呼び出し
    client = OpenAI(api_key=API_KEY)

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7
    )

    result_text = response.choices[0].message.content

    # JSONパース試行
    try:
        result_json = json.loads(result_text)
        buyer_reply = result_json.get("buyerLanguage", "（buyerLanguageフィールドなし）")
        jpn_reply = result_json.get("jpnLanguage", "（jpnLanguageフィールドなし）")
        parse_ok = True
    except json.JSONDecodeError:
        buyer_reply = result_text
        jpn_reply = "（JSONパース失敗）"
        parse_ok = False

    return {
        "buyer_reply": buyer_reply,
        "jpn_reply": jpn_reply,
        "parse_ok": parse_ok,
        "tokens": response.usage.total_tokens,
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
    }


def print_result(label: str, result: dict):
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")
    print("\n【バイヤーへの返信（英語）】")
    print(result["buyer_reply"])
    print("\n【日本語訳】")
    print(result["jpn_reply"])
    print(f"\n使用トークン: {result['tokens']} (入力:{result['prompt_tokens']} / 出力:{result['completion_tokens']})")
    if not result["parse_ok"]:
        print("⚠️  JSON形式で返ってきませんでした")


if __name__ == "__main__":
    args = sys.argv[1:]

    # 引数解析
    json_arg = None
    versions = []

    for arg in args:
        if arg.endswith(".json"):
            json_arg = arg
        elif arg.lower().startswith("v"):
            versions.append(arg[1:])  # "v2" → "2"
        elif arg.isdigit():
            versions.append(arg)

    # JSONファイル決定
    if json_arg:
        target = json_arg if os.path.isabs(json_arg) else os.path.join(BASE_DIR, json_arg)
    else:
        target = os.path.join(BASE_DIR, "gpt_request_6.json")

    # バイヤーの最新メッセージを表示
    with open(target, "r", encoding="utf-8") as f:
        raw_messages = json.load(f)

    user_messages = [m for m in raw_messages if m["role"] == "user"]
    print(f"\nテストファイル: {os.path.basename(target)}")
    if user_messages:
        print("\n【バイヤーの最新メッセージ】")
        print(user_messages[-1]["content"])

    # バージョン指定なし → JSONそのまま（現行）
    if not versions:
        result = run_test(target, prompt_version=None)
        print_result("現行プロンプト（JSONそのまま）", result)

    # バージョン1つ → そのバージョンで差し替え
    elif len(versions) == 1:
        v = versions[0]
        result = run_test(target, prompt_version=v)
        print_result(f"v{v}.0 プロンプト", result)

    # バージョン2つ → 並べて比較
    else:
        print(f"\n▶ 比較モード: v{versions[0]} vs v{versions[1]}")
        for v in versions:
            result = run_test(target, prompt_version=v)
            print_result(f"v{v}.0 プロンプト", result)
