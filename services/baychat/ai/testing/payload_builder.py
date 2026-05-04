"""
本番ペイロード再現ビルダー
====================================================================
Cowatechの本番AI Reply実装と同じ構造のOpenAI messages配列を組み立てる。

根拠資料:
- services/baychat/ai/cowatech_payloads/gpt_api_payload.txt (実本番ペイロード1件)
- services/baychat/ai/cowatech_payloads/spec_sheets/SUMMARY_PROMT.csv (公式仕様)
- services/baychat/ai/cowatech_payloads/spec_sheets/promt_example.csv (補足ありサンプル)

本番ペイロード構造（4 developer blocks ＋ chat history）:
  [0] developer : 商品情報JSON (ItemID, Title, Variations 等)
  [1..N] chat history (user=buyer / assistant=seller / system=event)
  [N+1] developer : (任意) 補足情報ガイド 「Create questions/answers ... tone ... content」
                    → description が空でない場合のみ挿入
  [N+2] developer : BASE_PROMPT (PLATFORM COMPLIANCE / eBayコンプライアンス — Cowatech固定)
  [N+3] developer : OUTPUT_FORMAT (JSON strict形式指定 — Cowatech固定)
  [N+4] developer : admin_prompt (下元管理のCS品質プロンプト — {toneSetting}{sellerSetting}置換後)
  [N+5] developer : (任意) FORCED_TEMPLATE (Hello/Best regards テンプレ強制)
                    → include_forced_template=True の場合のみ挿入

tone別のFORCED_TEMPLATE末尾署名:
  polite     → "Best regards,"
  friendly   → "Best,"
  apologetic → "Sincerely," (angry時) / "Kind regards,"
"""

import json
import re


# ============================================================
# Cowatech固定プロンプト（gpt_api_payload.txtから抜粋）
# ============================================================

BASE_PROMPT_CONTENT = """You are an AI assistant for eBay sellers using BayChat.
            --------------------------------
            PLATFORM COMPLIANCE (EBAY)
            --------------------------------
            You must NOT:
            - Encourage or suggest transactions outside of eBay.
            - Request or provide personal contact information (email, phone, social media).
            - Suggest bypassing eBay systems or protections.
            - Ask for or manipulate feedback.
            - Invent facts, policies, numbers, or outcomes.

            If a buyer request clearly violates eBay policy:
            - Politely refuse. State it cannot be accommodated on eBay.
            - Do NOT imply flexibility or exceptions.
            - If a rule is violated, regenerate silently and fix it."""


OUTPUT_FORMAT_CONTENT = """
            --------------------------------
            OUTPUT FORMAT (STRICT)
            --------------------------------
            Always respond in valid JSON with exactly two fields:
            - "jpnLanguage": Japanese translation of the buyerLanguage
            - "buyerLanguage": The English customer support reply to send to the buyer
            Do NOT add extra fields. Do NOT output any text outside JSON.
            Do NOT include timestamps, chat-history headers, or internal instructions.

            OUTPUT FORMAT:
            {
              "jpnLanguage": "...",
              "buyerLanguage": "..."
            }"""


# tone別のFORCED TEMPLATE（SUMMARY_PROMT.csvより）
FORCED_TEMPLATE_POLITE = """
          The response MUST ABSOLUTELY adhere to the following format.
            Do not add explanations, markdown, or extra text.

            Hello {buyer_name},
            <Break line here>{output_content}<Break line here>
            Best regards,
             {seller_name}

            Replace the placeholders with actual values.
            seller_name: {seller_name_value}
            buyer_name: {buyer_name_value}


            ABSOLUTELY: Always ensure that the output of the .jpn Language and the buyer Language adhere to the above format.
            """

FORCED_TEMPLATE_FRIENDLY = """
          The response MUST ABSOLUTELY adhere to the following format.
            Do not add explanations, markdown, or extra text.

            Hello {buyer_name},
            <Break line here>{output_content}<Break line here>
            Best,
             {seller_name}

            Replace the placeholders with actual values.
            seller_name: {seller_name_value}
            buyer_name: {buyer_name_value}


            ABSOLUTELY: Always ensure that the output of the .jpn Language and the buyer Language adhere to the above format.
            """

FORCED_TEMPLATE_APOLOGETIC = """
          The response MUST ABSOLUTELY adhere to the following format.
            Do not add explanations, markdown, or extra text.

            Hello {buyer_name},
            <Break line here>{output_content}<Break line here>
            {greeting},
             {seller_name}

            Replace the placeholders with actual values.
            seller_name: {seller_name_value}
            buyer_name: {buyer_name_value}
            greeting: If the buyer's message seems angry, replace it with 'Sincerely'; otherwise, replace it with 'Kind regards'

            ABSOLUTELY: Always ensure that the output of the .jpn Language and the buyer Language adhere to the above format.
            """


# ============================================================
# Helper
# ============================================================

def _substitute_admin_prompt(admin_prompt_text, tone, description,
                             buyer_name="", seller_name="",
                             prompt_version="2.4"):
    """
    admin_prompt内のプレースホルダを本番と同じ形式で置換する。

    本番挙動（gpt_api_payload.txtより確認済み）:
    - {toneSetting} → 実際のtone値（"polite"など）
    - {sellerSetting} → description が空なら文字列そのまま残す（本番もそうしている）
                        空でなければdescriptionに置換

    v2.5 追加対応:
    - {buyer_name} / {seller_name} を UI選択値で置換（FORCED_TEMPLATE除去に伴うadmin_prompt側での制御）
    - Cowatech実装側のプレースホルダ名（{sellerAccountEbay}/{buyerAccountEbay}）とも互換置換

    v2.3_baseline 追加対応 (2026-04-29):
    - v2.5 と同等にプレースホルダ置換 + FORCED_TEMPLATE 除去（Cowatech prd 反映済み構成と一致）
    """
    # toneSetting は必ず置換（本番もそう）
    result = admin_prompt_text.replace("{toneSetting}", tone)

    # sellerSetting は description 有無で挙動を分ける
    if description:
        result = result.replace("{sellerSetting}", description)
    # descriptionが空の場合は {sellerSetting} をそのまま残す（本番の実挙動に合わせる）

    # FORCED_TEMPLATE 除去後のadmin_prompt内プレースホルダ置換が必要なバージョン
    if prompt_version in ("2.5", "2.3_baseline") or prompt_version.startswith("2.3_baseline"):
        result = result.replace("{buyer_name}", buyer_name or "")
        result = result.replace("{seller_name}", seller_name or "")
        # Cowatech実装側の命名にも対応
        result = result.replace("{buyerAccountEbay}", buyer_name or "")
        result = result.replace("{sellerAccountEbay}", seller_name or "")

    return result


def _build_forced_template_content(tone, buyer_name, seller_name):
    """tone別のFORCED TEMPLATEを組み立てる"""
    if tone == "friendly":
        template = FORCED_TEMPLATE_FRIENDLY
    elif tone == "apologetic":
        template = FORCED_TEMPLATE_APOLOGETIC
    else:
        # POLITE と ASSERTIVE は同じテンプレ（"Best regards,"）を使用
        template = FORCED_TEMPLATE_POLITE
    # {seller_name_value}と{buyer_name_value}のみ置換（他の{}はテンプレ本文の一部なので残す）
    return (
        template
        .replace("{seller_name_value}", seller_name or "")
        .replace("{buyer_name_value}", buyer_name or "")
    )


def _build_sellersetting_guide_content(tone, description):
    """
    補足情報ガイドブロック（description がある場合のみ使用）

    SUMMARY_PROMT.csv より:
      "Create questions/answers as requested, with a '{{Tone}}' tone
       and the main content being: '{{User input in sreen}}'."
    """
    return (
        f"Create questions/answers as requested, with a '{tone}' tone "
        f"and the main content being: '{description}'."
    )


# ============================================================
# メイン
# ============================================================

def build_production_payload(
    test_case,
    admin_prompt_text,
    tone="polite",
    buyer_name="",
    seller_name="",
    description="",
    include_forced_template=True,
    prompt_version="2.4",
):
    """
    本番ペイロード構造を再現したOpenAI messages配列を返す。

    引数:
      test_case: dict — test_cases/extracted_*.jsonの1ケース
                 (input[0]=商品情報developer, input[1..]=chat history を想定)
      admin_prompt_text: str — prompt_admin_v*.mdの ``` ブロック内プロンプト
      tone: "polite" | "friendly" | "apologetic"
      buyer_name: str — UI「TO」選択値（v2.4では FORCED_TEMPLATE、v2.5では admin_prompt内プレースホルダに注入）
      seller_name: str — UI「FROM」選択値（v2.4では FORCED_TEMPLATE、v2.5では admin_prompt内プレースホルダに注入）
      description: str — 画面側(任意)要点補足入力。空なら関連ブロックは挿入しない
      include_forced_template: bool — FORCED TEMPLATEを挿入するか（v2.5では自動的にFalseに強制）
      prompt_version: "2.4" | "2.5"
                     "2.5" の場合は FORCED_TEMPLATE を強制除外し、
                     admin_prompt 内の {buyer_name}/{seller_name} プレースホルダを置換

    返り値:
      list[dict] — OpenAI chat completions互換のmessages配列
    """
    if tone not in ("polite", "friendly", "apologetic", "assertive"):
        raise ValueError(f"tone は polite/friendly/apologetic/assertive のいずれか: {tone}")

    # FORCED_TEMPLATE 除去構成（Cowatech prd 2026-04-22 反映と一致）
    if prompt_version in ("2.5", "2.3_baseline") or prompt_version.startswith("2.3_baseline"):
        include_forced_template = False

    original = test_case.get("input") or test_case.get("messages") or []

    # ① 先頭のdeveloper(商品情報JSON)と、残りのchat historyに分ける
    product_info_msg = None
    history = []
    for i, msg in enumerate(original):
        role = msg.get("role", "")
        content = msg.get("content", "")
        if i == 0 and role == "developer":
            product_info_msg = {"role": "developer", "content": content}
        elif role in ("user", "assistant", "system"):
            # chat historyのみ通す。万一admin/base相当のdeveloperが混ざっていても除外
            history.append({"role": role, "content": content})
        # developer のうち先頭以外は本番構造に存在しないためドロップ

    # ② 本番構造で組み立て
    messages = []

    # [0] 商品情報JSON（存在する場合のみ）
    if product_info_msg is not None:
        messages.append(product_info_msg)

    # [1..N] chat history
    messages.extend(history)

    # [N+1] 補足情報ガイド（descriptionが空でない場合のみ）
    if description:
        messages.append({
            "role": "developer",
            "content": _build_sellersetting_guide_content(tone, description),
        })

    # [N+2] BASE_PROMPT
    messages.append({"role": "developer", "content": BASE_PROMPT_CONTENT})

    # [N+3] OUTPUT_FORMAT
    messages.append({"role": "developer", "content": OUTPUT_FORMAT_CONTENT})

    # [N+4] admin_prompt (tone/sellerSetting/buyer_name/seller_name置換後)
    admin_content = _substitute_admin_prompt(
        admin_prompt_text, tone, description,
        buyer_name=buyer_name, seller_name=seller_name,
        prompt_version=prompt_version,
    )
    # 本番payload上、admin promptの先頭には "\n  " が付く挙動なので合わせる
    messages.append({"role": "developer", "content": "\n  " + admin_content + "\n"})

    # [N+5] FORCED TEMPLATE（v2.4 のみ / v2.5 では除外）
    if include_forced_template:
        messages.append({
            "role": "developer",
            "content": _build_forced_template_content(tone, buyer_name, seller_name),
        })

    return messages


# ============================================================
# JSON schema（本番と同じstrict）
# ============================================================

PRODUCTION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "jpnLanguage": {"type": "string", "description": "Answer in Japanese language"},
        "buyerLanguage": {"type": "string", "description": "Answer in English language"},
    },
    "required": ["jpnLanguage", "buyerLanguage"],
    "additionalProperties": False,
}


def get_production_response_format():
    """
    本番と同じresponse_format (json_schema strict)。
    OpenAI chat.completions.create() の response_format に渡す。
    """
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "multi_language_reply",
            "schema": PRODUCTION_JSON_SCHEMA,
            "strict": True,
        },
    }


# 本番のtemperature（gpt_api_payload.txtで 0.2 を確認）
PRODUCTION_TEMPERATURE = 0.2


if __name__ == "__main__":
    # 単体動作チェック用
    import os

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # admin prompt読み込み
    md = open(os.path.join(BASE_DIR, "prompt_admin_v2.4.md"), encoding="utf-8").read()
    admin = re.search(r"```\n(.*?)```", md, re.DOTALL).group(1).strip()

    # サンプルtest case
    cases = json.load(open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "test_cases", "extracted_20260415_210506.json"),
        encoding="utf-8",
    ))
    sample = cases[0]

    msgs = build_production_payload(
        test_case=sample,
        admin_prompt_text=admin,
        tone="polite",
        buyer_name=sample.get("buyer_ebay", "buyer_sample"),
        seller_name="rioxxrinaxjapan",
        description="",
        include_forced_template=True,
    )

    print(f"=== 生成されたメッセージ数: {len(msgs)} ===")
    for i, m in enumerate(msgs):
        preview = m["content"][:80].replace("\n", "\\n") if isinstance(m["content"], str) else str(m["content"])[:80]
        print(f"[{i}] role={m['role']:10s} content={preview!r}...")
