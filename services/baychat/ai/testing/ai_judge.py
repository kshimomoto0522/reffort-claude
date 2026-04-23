"""
AI審判モジュール — AIが生成した返信の品質を自動採点する
=====================================================
強いモデル（Claude Sonnet）を使って、AI Replyの出力を5項目で採点する。

採点項目（各1〜5点、合計25点満点）:
  1. 正確性  — 商品情報・ポリシーに基づいた正しい回答か
  2. トーン  — プロフェッショナルで共感的か
  3. 完全性  — バイヤーの質問すべてに答えているか
  4. アクション明確性 — 次のステップが具体的に示されているか
  5. 自然さ  — 不自然な英語・AI臭い表現がないか

使い方:
  from ai_judge import judge_reply

  score = judge_reply(
      buyer_message="I want to cancel my order",
      ai_reply="Thank you for reaching out...",
      product_info={"title": "Nike Air Max", "price": 150},
      conversation_history=[...],
      judge_model="claude"  # または "openai" / "gemini"
  )
  print(score)
  # → {"accuracy": 4, "tone": 5, "completeness": 3, ...}
"""

import json
import os
import sys
from dotenv import dotenv_values

# .envファイルのパス（services/baychat/ai/.env）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

# ===== 採点プロンプト =====
JUDGE_PROMPT = """You are an expert quality evaluator for eBay customer service AI replies.

You will be given:
- The buyer's message (what the customer said)
- The AI-generated reply (what the AI wrote back)
- Product information (item details)
- Conversation history (previous messages for context)

Rate the AI reply on these 5 criteria, each on a scale of 1-5:

1. **Accuracy** (正確性): Is the reply factually correct based on the product info and eBay policies? Does it provide accurate information?
   - 5: Perfectly accurate, all details correct
   - 3: Mostly accurate, minor issues
   - 1: Contains incorrect information or misleading statements

2. **Tone** (トーン): Is the reply professional, empathetic, and appropriate for the situation?
   - 5: Perfectly professional and empathetic, matches the situation
   - 3: Acceptable tone but could be more empathetic
   - 1: Inappropriate, cold, or overly casual

3. **Completeness** (完全性): Does the reply address ALL of the buyer's questions/concerns?
   - 5: Addresses every point the buyer raised
   - 3: Addresses main point but misses some details
   - 1: Misses major concerns or questions

4. **Action Clarity** (アクション明確性): Are the next steps clearly communicated?
   - 5: Very clear what happens next and what the buyer should do
   - 3: Some guidance but could be clearer
   - 1: No clear next steps or confusing instructions

5. **Naturalness** (自然さ): Does the reply sound natural, not robotic or AI-generated?
   - 5: Sounds completely natural, like a skilled human CS agent
   - 3: Mostly natural but some AI-ish phrases
   - 1: Obviously AI-generated, template-like, or awkward

Also identify any specific issues:
- **critical_issues**: Problems that would damage the customer relationship (wrong info, rude tone, etc.)
- **improvements**: Suggestions for making the reply better

Respond in this exact JSON format:
{
  "accuracy": <1-5>,
  "tone": <1-5>,
  "completeness": <1-5>,
  "action_clarity": <1-5>,
  "naturalness": <1-5>,
  "total": <sum of all scores>,
  "critical_issues": ["issue1", "issue2"],
  "improvements": ["suggestion1", "suggestion2"],
  "summary_ja": "<1-2文の日本語サマリー>"
}"""


def _build_judge_messages(buyer_message, ai_reply, product_info, conversation_history):
    """
    AI審判に渡すメッセージを組み立てる。
    """
    # 会話履歴を読みやすい形式に変換
    history_text = ""
    if conversation_history:
        for msg in conversation_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if role == "user":
                history_text += f"[Buyer]: {content}\n"
            elif role == "assistant":
                history_text += f"[Seller]: {content}\n"
            elif role == "system":
                history_text += f"[Event]: {content}\n"
            # developerロール（プロンプト）は省略

    # 商品情報の要約
    if isinstance(product_info, dict):
        product_text = json.dumps(product_info, ensure_ascii=False, indent=2)
    elif isinstance(product_info, str):
        try:
            product_text = json.dumps(json.loads(product_info), ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            product_text = product_info
    else:
        product_text = str(product_info)

    user_content = f"""## Product Information
{product_text}

## Conversation History
{history_text}

## Buyer's Latest Message
{buyer_message}

## AI-Generated Reply to Evaluate
{ai_reply}

Please evaluate the AI reply based on the 5 criteria."""

    return user_content


def judge_with_claude(user_content):
    """Claude APIで採点する"""
    import anthropic

    env = dotenv_values(ENV_PATH)
    api_key = env.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY が.envに設定されていません")

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=JUDGE_PROMPT,
        messages=[{"role": "user", "content": user_content}],
        temperature=0.3,  # 採点なので低めの温度
    )
    return response.content[0].text


def judge_with_openai(user_content):
    """OpenAI APIで採点する"""
    from openai import OpenAI

    env = dotenv_values(ENV_PATH)
    api_key = env.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY が.envに設定されていません")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


def judge_with_gemini(user_content):
    """Gemini APIで採点する"""
    import google.genai as genai
    from google.genai import types

    env = dotenv_values(ENV_PATH)
    api_key = env.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY が.envに設定されていません")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[{"role": "user", "parts": [{"text": user_content}]}],
        config=types.GenerateContentConfig(
            system_instruction=JUDGE_PROMPT,
            temperature=0.3,
            response_mime_type="application/json",
        )
    )
    return response.text


def judge_reply(buyer_message, ai_reply, product_info=None,
                conversation_history=None, judge_model="claude"):
    """
    AI返信の品質を採点する。

    引数:
      buyer_message: バイヤーの最新メッセージ（str）
      ai_reply: AIが生成した返信（str）
      product_info: 商品情報（dict or str）
      conversation_history: 会話履歴（list of dict）
      judge_model: 採点に使うモデル（"claude" / "openai" / "gemini"）

    返り値:
      dict: 採点結果（5項目のスコア + 合計 + コメント）
    """
    user_content = _build_judge_messages(
        buyer_message, ai_reply, product_info, conversation_history
    )

    # モデル別に採点
    if judge_model == "claude":
        raw_result = judge_with_claude(user_content)
    elif judge_model == "openai":
        raw_result = judge_with_openai(user_content)
    elif judge_model == "gemini":
        raw_result = judge_with_gemini(user_content)
    else:
        raise ValueError(f"未知の審判モデル: {judge_model}")

    # JSONパース
    try:
        result = json.loads(raw_result)
    except json.JSONDecodeError:
        # JSON部分を抽出してリトライ
        import re
        match = re.search(r'\{.*\}', raw_result, re.DOTALL)
        if match:
            result = json.loads(match.group())
        else:
            result = {
                "accuracy": 0, "tone": 0, "completeness": 0,
                "action_clarity": 0, "naturalness": 0, "total": 0,
                "critical_issues": ["JSONパース失敗"],
                "improvements": [],
                "summary_ja": "採点結果のパースに失敗しました",
                "raw_output": raw_result
            }

    return result


# ===== 直接実行時のテスト =====
if __name__ == "__main__":
    sys.stdout = sys.stdout if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding == 'utf-8' else \
        __import__('io').TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    # サンプルテスト
    score = judge_reply(
        buyer_message="I ordered it on accident. Could you please cancel the order?",
        ai_reply="Thank you for reaching out. I understand you'd like to cancel your order. I've processed the cancellation for you. You should see your refund within 3-5 business days. Is there anything else I can help you with?",
        product_info={"title": "Onitsuka Tiger MEXICO 66", "price": 150},
        conversation_history=[],
        judge_model="openai"  # コスト安めのOpenAIでテスト
    )

    print("=== AI審判テスト結果 ===")
    print(json.dumps(score, ensure_ascii=False, indent=2))
