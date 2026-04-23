# -*- coding: utf-8 -*-
"""
購入前シナリオ9ケースを再生成するスクリプト。
元の generate_synthetic_cases.py では system event: purchase_completed が全ケースに
付与されてしまうバグがあったため、購入前シナリオのみ events=[] で再生成する。
"""
import os, sys, json, time
from dotenv import dotenv_values

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.dirname(SCRIPT_DIR)

env = dotenv_values(os.path.join(AI_DIR, ".env"))
OPENAI_API_KEY = env.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

# ============================================================
# 購入前シナリオ 9件
# ============================================================
PREPURCHASE_SCENARIOS = [
    dict(id="A1_cam_stock", category="discount", stage="S1",
         product_name="Leica M3 Double Stroke 1957 Rangefinder",
         product_category="Vintage Cameras",
         emotion="neutral", language="en",
         situation="First inquiry. Buyer asks if the item is still available and asks for more photos of the shutter condition."),
    dict(id="A2_jacket_sizing", category="general", stage="S1",
         product_name="Vintage Levi's Type III Trucker Jacket (Size L)",
         product_category="Men's Clothing / Vintage",
         emotion="neutral", language="en",
         situation="First inquiry. Buyer asks about exact chest and shoulder measurements since vintage sizes run different."),
    dict(id="A3_guitar_ship_time", category="general", stage="S1",
         product_name="1978 Fender Stratocaster Olympic White (USA)",
         product_category="Musical Instruments / Guitars",
         emotion="mild_anxiety", language="en",
         situation="First inquiry. Buyer wants to know shipping time to the US West Coast and if the item is insured."),
    dict(id="A4_pokemon_condition", category="general", stage="S2",
         product_name="Pokemon Base Set Charizard 1st Edition PSA 9",
         product_category="Collectible Card Games",
         emotion="neutral", language="en",
         situation="Buyer already asked one question about centering. Now asks for a scan of the back edges to confirm no whitening. This is pre-purchase negotiation, no purchase has been made yet."),
    dict(id="G4_cam_german", category="discount", stage="S2",
         product_name="Contax G2 Body with 45mm Planar Lens Kit",
         product_category="Vintage Cameras",
         emotion="polite_but_pushing", language="de",
         situation="German-speaking buyer negotiating price - 2nd round of negotiation. Writes in German. Pre-purchase stage, has not bought yet."),
    dict(id="H1_bag_price_offer", category="discount", stage="S1",
         product_name="Chanel Classic Flap Medium Caviar Leather Black GHW",
         product_category="Luxury Bags / Chanel",
         emotion="confident", language="en",
         situation="Listed at $7,500. Buyer offers $6,200 directly in a message (not through Best Offer feature). Pre-purchase."),
    dict(id="H2_cards_bulk", category="discount", stage="S1",
         product_name="Magic: The Gathering Modern Horizons 3 Booster Box",
         product_category="Collectible Card Games",
         emotion="neutral", language="en",
         situation="Buyer asks: 'If I buy 3 boxes, can you offer a discount?' Pre-purchase question about bulk discount."),
    dict(id="H3_watch_re_nego", category="discount", stage="S2",
         product_name="Seiko Credor Eichi II Porcelain Dial Platinum",
         product_category="Wristwatches / Luxury",
         emotion="persistent", language="en",
         situation="Seller declined first offer. Buyer counters with higher offer and pushes for a deal. Pre-purchase, still negotiating."),
    dict(id="H4_sneakers_reoffer", category="discount", stage="S1",
         product_name="Nike Air Force 1 Off-White Virgil Abloh 'The Ten' Volt",
         product_category="Sneakers / Limited Edition",
         emotion="casual", language="en",
         situation="Seller's Best Offer auto-declined buyer's previous attempt. Buyer now sends a message outside Best Offer asking 'what's your best price?' Pre-purchase."),
]


GEN_PROMPT = """You are generating a realistic eBay chat conversation for testing BayChat AI Reply.

SCENARIO:
- Product: {product_name} ({product_category})
- Stage: {stage} (S1=first inquiry, S2=in-progress negotiation/question)
- Situation: {situation}
- Buyer emotion: {emotion}
- Language: {language}
- PRE-PURCHASE SCENARIO: The buyer has NOT purchased the item yet. No purchase events occurred.

TASK: Return a JSON object:

{{
  "item_info": {{
    "ItemID": "<11-digit random number>",
    "Title": "<match the given product name exactly or similar>",
    "PrimaryCategoryName": "<like 'Cameras & Photo:Film Cameras:Rangefinder'>",
    "ListingType": "FixedPriceItem",
    "StartPrice": "<price in USD, string>",
    "CurrentPrice": "<same>",
    "Quantity": "<int as string>",
    "ListingStatus": "Active",
    "ShippingType": "Flat",
    "ShippingService": "<like 'EMS International' or 'US_ExpeditedSppedPAK'>",
    "ShippingServiceCost": "<cost>",
    "ReturnsAcceptedOption": "ReturnsAccepted",
    "RefundOption": "MoneyBack",
    "ReturnsWithinOption": "Days_60",
    "ShippingCostPaidByOption": "Buyer",
    "Country": "JP",
    "Location": "<Japanese city>",
    "Currency": "USD",
    "whoPaysShipping": "Buyer"
  }},
  "messages": [
    // ABSOLUTELY DO NOT include any "role": "system" message with purchase_completed, best_offer_created, or any other event.
    // This is a pre-purchase inquiry conversation — NO events have occurred.
    //
    // For S1 (first inquiry):
    //   Start with ONE user message (the buyer's first question).
    //   No assistant reply yet. This is what AI Reply will answer.
    //   Example: [{{"role":"user","content":"[2026-04-20T14:30:00.000Z] Hello, is this still available? ..."}}]
    //
    // For S2 (in-progress negotiation):
    //   3-5 back-and-forth exchanges between buyer (user) and seller (assistant).
    //   End with buyer's LATEST message (seller has not replied yet to this one).
    //   Example: user question → assistant answer → user follow-up → assistant reply → user final message
    //
    // EACH user/assistant content must start with [ISO-8601 timestamp]
  ],
  "latest_buyer_message": "<same as the last user content, WITHOUT the timestamp prefix>"
}}

CRITICAL CONSTRAINTS:
1. NO `role: system` messages at all. No events.
2. The LAST message in `messages` MUST be from `user` (buyer).
3. For S1, the ONLY message might be from `user` (no assistant reply yet).
4. Timestamps realistic (hours or 1-2 days apart for S2).
5. Seller assistant replies professional eBay CS style — polite, solution-oriented, signed naturally (use varied names matching product genre, not always "Kei").
6. Write all messages in the specified language ({language}).
7. Reflect the buyer's specified emotion in word choice.

Output ONLY valid JSON. No markdown, no commentary."""


def generate_case(sc, client):
    prompt = GEN_PROMPT.format(**sc)
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)


def build_test_case(scenario, gen_result):
    item_info = gen_result.get("item_info", {})
    messages = gen_result.get("messages", [])
    latest_buyer = gen_result.get("latest_buyer_message", "")

    # システムメッセージ混入を防ぐバリデーション
    system_messages = [m for m in messages if m.get("role") == "system"]
    if system_messages:
        print(f"  ⚠️ {scenario['id']}: systemメッセージ {len(system_messages)}件を除去")
        messages = [m for m in messages if m.get("role") != "system"]

    input_messages = [{"role": "developer", "content": json.dumps(item_info, ensure_ascii=False)}]
    input_messages.extend(messages)

    buyer_ebay = scenario["id"].split("_")[0]

    return {
        "id": f"synth_{scenario['id']}",
        "category": scenario["category"],
        "stage": scenario["stage"],
        "product_category": scenario["product_category"],
        "emotion": scenario["emotion"],
        "language": scenario["language"],
        "situation": scenario["situation"],
        "buyer_ebay": buyer_ebay,
        "buyer_message": latest_buyer,
        "buyer_message_ja": "",
        "history_ja": [],
        "num_messages": len(messages),
        "has_seller_history": any(m.get("role") == "assistant" for m in messages),
        "input": input_messages,
    }


def main():
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    # 再生成
    print(f"[1] 購入前9シナリオを再生成（events=[]・systemなし）...")
    new_cases = []
    for i, sc in enumerate(PREPURCHASE_SCENARIOS, 1):
        print(f"  [{i}/9] {sc['id']} ...", end="", flush=True)
        try:
            gen = generate_case(sc, client)
            tc = build_test_case(sc, gen)
            new_cases.append(tc)
            print(f" OK ({tc['num_messages']} msgs)")
            time.sleep(0.3)
        except Exception as e:
            print(f" FAILED: {e}")

    # 既存の40ケースJSONから該当9件を置換
    json_path = os.path.join(SCRIPT_DIR, "test_cases", "synthetic_40cases_v1.json")
    all_cases = json.load(open(json_path, encoding="utf-8"))

    target_ids = {c["id"] for c in new_cases}
    kept = [c for c in all_cases if c["id"] not in target_ids]
    merged = kept + new_cases
    # 元の順序を維持するため、元の順序でソート
    order = {c["id"]: i for i, c in enumerate(all_cases)}
    merged.sort(key=lambda c: order.get(c["id"], 999))

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"[2] 既存JSONの9件を置換完了: {json_path}")

    # 9件だけの別JSONも作成（再テスト用）
    prep_path = os.path.join(SCRIPT_DIR, "test_cases", "synthetic_9prepurchase_v2.json")
    with open(prep_path, "w", encoding="utf-8") as f:
        json.dump(new_cases, f, ensure_ascii=False, indent=2)
    print(f"[3] 再テスト用9件JSON作成: {prep_path}")


if __name__ == "__main__":
    main()
