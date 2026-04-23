"""
マルチモデル比較スクリプト v2.0
GPT-4.1-Mini vs Gemini 2.5 Flash vs Claude 3.5 Haiku を同一プロンプトで比較する。
APIキーが未設定のモデルは自動スキップするため、Claudeキー未取得でも実行可能。
"""

import json
import sys
import os
import io
import re
import time

# Windows環境での文字化け対策
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# .envファイルからAPIキーを読み込む（services/baychat/ai/.env）
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)

from openai import OpenAI

# ===== APIキー取得（未設定の場合はNone） =====
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or None  # 空文字はNoneとして扱う

# ===== スクリプトのベースディレクトリ（絶対パス） =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ===== テスト対象ファイル（本番データ全10件） =====
TARGET_FILES = [
    "gpt_request_2.json", "gpt_request_3.json", "gpt_request_4.json",
    "gpt_request_5.json", "gpt_request_6.json", "gpt_request_7.json",
    "gpt_request_8.json", "gpt_request_9.json", "gpt_request_10.json",
    "gpt_request.json",
]

# ===== 比較モデル定義 =====
# (表示ラベル, プロバイダー, モデルID, input$/1Mトークン, output$/1Mトークン)
MODELS = [
    ("GPT-4.1-Mini（現在）",        "openai",    "gpt-4.1-mini",                      0.40,  1.60),
    ("Gemini 2.5 Flash（次期候補）", "gemini",    "gemini-2.5-flash",                  0.075, 0.30),
    ("Claude Haiku 4.5（参考）",      "anthropic", "claude-haiku-4-5-20251001",         0.80,  4.00),
]

# ===== 為替レート =====
JPY_RATE = 150  # 1ドル = 150円


# ============================================================
# プロンプト読み込み・差し替え関数
# ============================================================

def load_prompt_from_md(version: str) -> str:
    """
    prompt_admin_v{version}.md の ```ブロック``` からプロンプト本文を取り出す。
    例: load_prompt_from_md("2.1") → prompt_admin_v2.1.md を読む
    """
    md_file = os.path.join(BASE_DIR, f"prompt_admin_v{version}.md")
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"```\n(.*?)```", content, re.DOTALL)
    if not match:
        raise ValueError(f"プロンプト本文が見つかりません: {md_file}")
    return match.group(1).strip()


def is_admin_prompt(content: str) -> bool:
    """developerメッセージがadminプロンプト（CS設定）かどうかを判定する"""
    return "ROLE" in content and "CONVERSATION STAGE DETECTION" in content and "TONE" in content


def replace_admin_prompt(messages: list, new_prompt: str) -> list:
    """messagesリストの中のadminプロンプトを最新版に差し替える"""
    replaced = []
    for msg in messages:
        if msg["role"] == "developer" and is_admin_prompt(msg.get("content", "")):
            replaced.append({"role": "developer", "content": "\n" + new_prompt + "\n"})
        else:
            replaced.append(msg)
    return replaced


def get_latest_buyer_messages(messages: list) -> list:
    """最後のassistant（セラー）メッセージ以降のバイヤーメッセージをすべて返す"""
    last_assistant_idx = -1
    for i, m in enumerate(messages):
        if m["role"] == "assistant":
            last_assistant_idx = i
    unread = []
    for m in messages[last_assistant_idx + 1:]:
        if m["role"] == "user":
            unread.append(m["content"])
    return unread


# ============================================================
# メッセージ形式変換関数
# ============================================================

def convert_to_gemini_format(messages: list) -> tuple:
    """
    OpenAI形式のmessagesをGemini API形式に変換する。

    OpenAI → Gemini のroleマッピング:
      "developer" → system_instruction にまとめる
      "system"    → system_instruction にまとめる
      "user"      → role: "user"
      "assistant" → role: "model"  ← Geminiはassistantをmodelというroleで扱う

    返り値:
      system_instruction: str  （developer/systemロールをまとめた文字列）
      contents: list           （user/modelのやり取りリスト）
    """
    system_parts = []
    contents = []

    for msg in messages:
        role    = msg.get("role", "")
        content = msg.get("content", "")

        if role in ("developer", "system"):
            # システム系のメッセージはsystem_instructionに集約
            system_parts.append(content)
        elif role == "user":
            contents.append({"role": "user",  "parts": [{"text": content}]})
        elif role == "assistant":
            # GeminiはassistantをmodelというroleIDで扱う
            contents.append({"role": "model", "parts": [{"text": content}]})

    system_instruction = "\n\n".join(system_parts)
    return system_instruction, contents


def convert_to_claude_format(messages: list) -> tuple:
    """
    OpenAI形式のmessagesをClaude（Anthropic）API形式に変換する。

    OpenAI → Claude のroleマッピング:
      "developer" → systemパラメータにまとめる
      "system"    → systemパラメータにまとめる
      "user"      → role: "user"
      "assistant" → role: "assistant"

    ⚠️ Claude APIはuserとassistantが交互である必要がある。
    同じroleが連続する場合は改行でつなげて一つのメッセージにまとめる。

    返り値:
      system_text: str   （developer/systemロールをまとめた文字列）
      messages: list     （user/assistantのやり取りリスト）
    """
    system_parts = []
    raw_messages = []

    for msg in messages:
        role    = msg.get("role", "")
        content = msg.get("content", "")

        if role in ("developer", "system"):
            system_parts.append(content)
        elif role in ("user", "assistant"):
            raw_messages.append({"role": role, "content": content})

    # 同じroleが連続する場合は結合する（Claude APIの制約対応）
    merged_messages = []
    for msg in raw_messages:
        if merged_messages and merged_messages[-1]["role"] == msg["role"]:
            merged_messages[-1]["content"] += "\n" + msg["content"]
        else:
            merged_messages.append(dict(msg))

    system_text = "\n\n".join(system_parts)
    return system_text, merged_messages


# ============================================================
# 各モデルへのAPI呼び出し関数
# ============================================================

def call_openai(model_id: str, messages: list) -> tuple:
    """
    OpenAI APIを呼び出す。
    返り値: (result_text, input_tokens, output_tokens, elapsed_seconds)
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    start = time.time()
    response = client.chat.completions.create(
        model=model_id,
        messages=messages,
        temperature=0.7
    )
    elapsed       = time.time() - start
    result_text   = response.choices[0].message.content
    input_tokens  = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    return result_text, input_tokens, output_tokens, elapsed


def call_gemini(model_id: str, messages: list) -> tuple:
    """
    Gemini API（google-genai）を呼び出す。
    返り値: (result_text, input_tokens, output_tokens, elapsed_seconds)
    """
    import google.genai as genai
    from google.genai import types

    client = genai.Client(api_key=GEMINI_API_KEY)
    system_instruction, contents = convert_to_gemini_format(messages)

    start = time.time()
    response = client.models.generate_content(
        model=model_id,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
            response_mime_type="application/json",  # JSON形式で出力を強制（コードブロック混入を防ぐ）
        )
    )
    elapsed = time.time() - start

    result_text   = response.text
    # Geminiのトークン使用量取得
    input_tokens  = response.usage_metadata.prompt_token_count
    output_tokens = response.usage_metadata.candidates_token_count
    return result_text, input_tokens, output_tokens, elapsed


def call_anthropic(model_id: str, messages: list) -> tuple:
    """
    Anthropic（Claude）APIを呼び出す。
    返り値: (result_text, input_tokens, output_tokens, elapsed_seconds)
    """
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    system_text, claude_messages = convert_to_claude_format(messages)

    start = time.time()
    response = client.messages.create(
        model=model_id,
        max_tokens=1024,
        system=system_text,
        messages=claude_messages,
        temperature=1.0,  # Claude APIはtemperature=1が推奨（拡張思考以外）
    )
    elapsed = time.time() - start

    result_text   = response.content[0].text
    input_tokens  = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    return result_text, input_tokens, output_tokens, elapsed


def call_model(provider: str, model_id: str, messages: list) -> tuple:
    """
    プロバイダーに応じた呼び出し関数にルーティングする。
    返り値: (result_text, input_tokens, output_tokens, elapsed_seconds)
    """
    if provider == "openai":
        return call_openai(model_id, messages)
    elif provider == "gemini":
        return call_gemini(model_id, messages)
    elif provider == "anthropic":
        return call_anthropic(model_id, messages)
    else:
        raise ValueError(f"未知のプロバイダー: {provider}")


# ============================================================
# コスト計算関数
# ============================================================

def calc_cost_usd(input_tokens: int, output_tokens: int,
                  in_price: float, out_price: float) -> float:
    """
    ドルコストを計算する。
    in_price / out_price は 1Mトークンあたりのドル単価。
    """
    return (input_tokens / 1_000_000 * in_price) + (output_tokens / 1_000_000 * out_price)


# ============================================================
# メイン処理
# ============================================================

if __name__ == "__main__":

    # ===== プロンプト読み込み =====
    prompt = load_prompt_from_md("2.1")

    # ===== APIキーの状況を確認してスキップ対象を決める =====
    available_models = []
    for label, provider, model_id, in_price, out_price in MODELS:
        if provider == "openai"    and not OPENAI_API_KEY:
            print(f"[SKIP] {label}: OPENAI_API_KEY が未設定のためスキップします")
            continue
        if provider == "gemini"    and not GEMINI_API_KEY:
            print(f"[SKIP] {label}: GEMINI_API_KEY が未設定のためスキップします")
            continue
        if provider == "anthropic" and not ANTHROPIC_API_KEY:
            print(f"[SKIP] {label}: ANTHROPIC_API_KEY が未設定のためスキップします")
            continue
        available_models.append((label, provider, model_id, in_price, out_price))

    if not available_models:
        print("利用可能なモデルがありません。.envファイルを確認してください。")
        sys.exit(1)

    print("=" * 70)
    print("  マルチモデル比較テスト（BayChat AI Reply）")
    print(f"  対象モデル: {len(available_models)}件")
    for label, provider, model_id, _, _ in available_models:
        print(f"    - {label} ({model_id})")
    print("=" * 70)

    # ===== トークン集計用辞書（月額コスト試算に使用） =====
    totals = {label: {"input": 0, "output": 0}
              for label, _, _, _, _ in available_models}

    # ===== ケースごとにループ =====
    for filename in TARGET_FILES:
        filepath = os.path.join(BASE_DIR, filename)

        # JSONファイル読み込み
        # 新形式 {"model":..., "input":[...]} と旧形式 [...] の両方に対応
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read().strip()
        parsed = json.loads(raw)
        if isinstance(parsed, dict) and "input" in parsed:
            messages_orig = parsed["input"]
        else:
            messages_orig = parsed

        # adminプロンプトを最新版（v2.1）に差し替え
        messages = replace_admin_prompt(messages_orig, prompt)

        # バイヤーの最新未読メッセージを取得（表示用）
        unread = get_latest_buyer_messages(messages)

        print(f"\n{'━' * 70}")
        print(f"  ケース: {filename}")
        print(f"{'━' * 70}")
        print("【バイヤーの最新メッセージ】")
        for msg in unread:
            print(f"  {msg}")
        print()

        # ===== 各モデルで実行 =====
        results = {}
        for label, provider, model_id, in_price, out_price in available_models:
            print(f"  [{label}] 実行中...", end="", flush=True)
            try:
                result_text, in_tok, out_tok, elapsed = call_model(provider, model_id, messages)

                # 集計に加算
                totals[label]["input"]  += in_tok
                totals[label]["output"] += out_tok

                # JSONパース（buyerLanguage と jpnLanguage を取り出す）
                try:
                    result_json = json.loads(result_text)
                    buyer_reply = result_json.get("buyerLanguage", "（buyerLanguageなし）")
                    jpn_reply   = result_json.get("jpnLanguage",   "（jpnLanguageなし）")
                    parse_ok    = True
                except json.JSONDecodeError:
                    buyer_reply = result_text
                    jpn_reply   = "（JSONパース失敗）"
                    parse_ok    = False

                cost_usd = calc_cost_usd(in_tok, out_tok, in_price, out_price)
                cost_jpy = cost_usd * JPY_RATE

                results[label] = {
                    "buyer":    buyer_reply,
                    "jpn":      jpn_reply,
                    "in_tok":   in_tok,
                    "out_tok":  out_tok,
                    "time":     elapsed,
                    "cost_usd": cost_usd,
                    "cost_jpy": cost_jpy,
                    "parse_ok": parse_ok,
                    "in_price": in_price,
                    "out_price": out_price,
                }
                print(f" 完了（{elapsed:.1f}秒）")

            except Exception as e:
                results[label] = {"error": str(e)}
                print(f" エラー: {e}")

            time.sleep(1)  # APIレート制限対策（連続リクエストの間に1秒待機）

        # ===== ケース結果の表示 =====
        for label, provider, model_id, in_price, out_price in available_models:
            r = results.get(label, {})
            if "error" in r:
                print(f"\n【{label}】エラー: {r['error']}")
            else:
                parse_status = "OK" if r["parse_ok"] else "JSONパース失敗"
                print(f"\n【{label}】")
                print(f"  応答時間: {r['time']:.1f}秒  |  "
                      f"入力: {r['in_tok']:,}tok  出力: {r['out_tok']:,}tok  |  "
                      f"コスト: ${r['cost_usd']:.5f}（約¥{r['cost_jpy']:.2f}）  |  "
                      f"JSON: {parse_status}")
                print(f"  英語返信: {r['buyer']}")
                print(f"  日本語:   {r['jpn']}")

    # ===== 月額コストシミュレーション =====
    print("\n" + "=" * 70)
    print("  月額コストシミュレーション")
    print("=" * 70)

    case_count = len(TARGET_FILES)
    print(f"\n※ テスト{case_count}件の平均トークンをもとに試算（1ドル={JPY_RATE}円）")
    print(f"※ ユーザー527名・利用率・1日あたり生成回数の3パターン\n")

    # シミュレーションシナリオ定義
    scenarios = [
        ("控えめ想定",   527, 0.20, 3),   # 20%のユーザーが1日3回利用
        ("中程度想定",   527, 0.35, 5),   # 35%のユーザーが1日5回利用
        ("フル活用想定", 527, 0.50, 8),   # 50%のユーザーが1日8回利用
    ]

    for label, provider, model_id, in_price, out_price in available_models:
        avg_in  = totals[label]["input"]  / case_count
        avg_out = totals[label]["output"] / case_count

        print(f"  {label}")
        print(f"  平均トークン: 入力 {avg_in:.0f} / 出力 {avg_out:.0f}")

        for s_name, users, rate, daily in scenarios:
            monthly_requests = users * rate * daily * 30
            cost_usd = calc_cost_usd(
                avg_in  * monthly_requests,
                avg_out * monthly_requests,
                in_price, out_price
            )
            cost_jpy = cost_usd * JPY_RATE
            per_user = cost_jpy / users if users > 0 else 0
            print(f"    [{s_name}] {users}人x{rate*100:.0f}%x{daily}回/日"
                  f" -> 月{monthly_requests:,.0f}回"
                  f" -> 月${cost_usd:.1f}（約¥{cost_jpy:,.0f}）"
                  f" -> 1人あたり¥{per_user:.1f}/月")
        print()

    print("=" * 70)
    print("完了")
