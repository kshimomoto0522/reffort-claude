# -*- coding: utf-8 -*-
"""
合成テストケース生成スクリプト（40ケース版）
====================================================================
BayChat AI Reply の 真のテスト環境を作るため、
「会話ステージ（S1〜S4）× 目的カテゴリ（A〜H）」のマトリクスで
40シナリオを設計し、AIで現実的な履歴を生成する。

方針:
- 商品ジャンルを意図的に多様化（BayChatは全セラー向けSaaSのため）
  スニーカー・カメラ・時計・トレカ・楽器・着物・フィギュア・ゲーム機等
- S1新規/S2進行中/S3局面切替/S4クロージング
- A購入前/B発送前/C到着前/D満足/E不満/Fリクエスト/G複合/H交渉
- バイヤー最新メッセージは「セラー応答待ち」の状態で終わる
- 英語中心だが数件は非英語（独・西）を含める

出力: test_cases/synthetic_40cases_v1.json

使い方:
    python generate_synthetic_cases.py
"""
import os
import sys
import io
import json
import time
import random
import re
from datetime import datetime, timedelta
from dotenv import dotenv_values

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.dirname(SCRIPT_DIR)
OUT_PATH = os.path.join(SCRIPT_DIR, "test_cases", "synthetic_40cases_v1.json")

# .env
env = dotenv_values(os.path.join(AI_DIR, ".env"))
OPENAI_API_KEY = env.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

# ============================================================
# 40シナリオの設計
# ============================================================

STAGE_DESC = {
    "S1": "NEW INQUIRY — buyer sends first message (little or no prior history)",
    "S2": "IN PROGRESS — issue is unresolved, back-and-forth already happened",
    "S3": "NEW DEVELOPMENT — a new situation emerged mid-conversation",
    "S4": "CLOSING — buyer is thanking / closing the conversation",
}

SCENARIOS = [
    # ========== A: 購入前の問い合わせ ==========
    dict(id="A1_cam_stock",
         category="discount", stage="S1", product_name="Leica M3 Double Stroke 1957 Rangefinder",
         product_category="Vintage Cameras",
         emotion="neutral", language="en", desc_provided=False,
         situation="First inquiry. Buyer asks if the item is still available and asks for more photos of the shutter condition."),
    dict(id="A2_jacket_sizing",
         category="general", stage="S1", product_name="Vintage Levi's Type III Trucker Jacket (Size L)",
         product_category="Men's Clothing / Vintage",
         emotion="neutral", language="en", desc_provided=False,
         situation="First inquiry. Buyer asks about exact chest and shoulder measurements since vintage sizes run different."),
    dict(id="A3_guitar_ship_time",
         category="general", stage="S1", product_name="1978 Fender Stratocaster Olympic White (USA)",
         product_category="Musical Instruments / Guitars",
         emotion="mild_anxiety", language="en", desc_provided=False,
         situation="First inquiry. Buyer wants to know shipping time to the US West Coast and if the item is insured."),
    dict(id="A4_pokemon_condition",
         category="general", stage="S2", product_name="Pokemon Base Set Charizard 1st Edition PSA 9",
         product_category="Collectible Card Games",
         emotion="neutral", language="en", desc_provided=False,
         situation="Buyer already asked one question about centering. Now asks for a scan of the back edges to confirm no whitening."),

    # ========== B: 購入後〜発送前 ==========
    dict(id="B1_ps5_ship_date",
         category="tracking", stage="S1", product_name="Sony PlayStation 5 Disc Edition (CFI-1200A01)",
         product_category="Video Game Consoles",
         emotion="neutral", language="en", desc_provided=False,
         situation="Buyer just purchased. Asks when it will be shipped."),
    dict(id="B2_kimono_address_change",
         category="general", stage="S2", product_name="Vintage Silk Kimono Furisode with Crane Embroidery",
         product_category="Asian Antiques / Kimono",
         emotion="slightly_anxious", language="en", desc_provided=False,
         situation="Bought 1 day ago. Realizes they entered an old address. Asks seller to change shipping address before shipment."),
    dict(id="B3_figure_cancel_mistake",
         category="cancel", stage="S2", product_name="Bandai Soul of Chogokin GX-31 Dancouga (2014 Edition)",
         product_category="Anime Collectibles / Figures",
         emotion="apologetic", language="en", desc_provided=False,
         situation="Buyer purchased by accident (clicked Buy It Now instead of Watch). Asks to cancel."),
    dict(id="B4_trading_card_combine",
         category="general", stage="S2", product_name="MTG Dual Land Revised - Tropical Island",
         product_category="Collectible Card Games",
         emotion="neutral", language="en", desc_provided=False,
         situation="Buyer bought 1 card and is considering buying 2 more from the seller's other listings. Asks if shipping can be combined."),
    dict(id="B5_watch_change_mind",
         category="cancel", stage="S3", product_name="Seiko Prospex SLA017 Limited 55th Anniversary",
         product_category="Wristwatches / Divers",
         emotion="hesitant", language="en", desc_provided=False,
         situation="Buyer purchased 2 days ago. Seller has already sent a shipping confirmation. Buyer asks if they can still cancel because they 'found a better deal locally'. A new development mid-conversation."),

    # ========== C: 発送後〜到着前 ==========
    dict(id="C1_bag_tracking_req",
         category="tracking", stage="S1", product_name="Louis Vuitton Monogram Speedy 30 Handbag",
         product_category="Women's Bags / LV",
         emotion="neutral", language="en", desc_provided=False,
         situation="Shipped 1 day ago. Buyer has not received tracking number notification and asks for it."),
    dict(id="C2_guitar_shipping_delay",
         category="tracking", stage="S2", product_name="Gibson Les Paul Standard 1959 Reissue R9",
         product_category="Musical Instruments / Guitars",
         emotion="anxious", language="en", desc_provided=False,
         situation="Shipped 8 days ago but tracking shows no update for 5 days. Buyer is worried and asks seller to check with the carrier."),
    dict(id="C3_cam_customs_stuck",
         category="tracking", stage="S3", product_name="Rolleiflex 2.8F TLR Medium Format Camera",
         product_category="Vintage Cameras",
         emotion="confused", language="en", desc_provided=False,
         situation="Item stuck at US customs for 10 days. Buyer reports customs is asking for an invoice. A new development — buyer needs seller's help with documentation."),
    dict(id="C4_retro_game_wrong_address",
         category="tracking", stage="S2", product_name="Super Famicom Nintendo 64 Chrono Trigger JP Cartridge",
         product_category="Retro Video Games",
         emotion="panicked", language="en", desc_provided=False,
         situation="Just realized shipping address is wrong (moved last month). Tracking shows item already left JP. Asks if seller can contact the carrier to redirect."),
    dict(id="C5_kimono_delivery_missed",
         category="tracking", stage="S3", product_name="Antique Meiji Era Silk Kimono Uchikake",
         product_category="Asian Antiques",
         emotion="worried", language="en", desc_provided=False,
         situation="Tracking says 'delivered' but buyer did not receive. Suspects carrier left it at wrong address."),
    dict(id="C6_car_part_deadline",
         category="tracking", stage="S2", product_name="Nismo S-tune Rear Spoiler for Nissan Skyline R34",
         product_category="Automotive Parts",
         emotion="mild_frustration", language="en", desc_provided=False,
         situation="Buyer needed the part for a car show next weekend. Item is taking longer than estimated. Expresses frustration and asks for an updated ETA."),

    # ========== D: 到着後満足 ==========
    dict(id="D1_sneakers_arrival_thanks",
         category="general", stage="S4", product_name="Nike Air Jordan 1 Retro High OG Chicago",
         product_category="Sneakers / Athletic Shoes",
         emotion="happy", language="en", desc_provided=False,
         situation="Sneakers arrived in perfect condition. Buyer thanks seller with a short message."),
    dict(id="D2_card_feedback_promise",
         category="general", stage="S4", product_name="Yu-Gi-Oh! Blue-Eyes White Dragon 1st Edition LOB",
         product_category="Collectible Card Games",
         emotion="very_happy", language="en", desc_provided=False,
         situation="Card arrived perfectly packaged. Buyer says they'll leave positive feedback and will buy more."),
    dict(id="D3_fishing_repeat",
         category="general", stage="S4", product_name="Daiwa Saltist 15000 Spinning Reel Japanese Model",
         product_category="Fishing Reels",
         emotion="happy", language="en", desc_provided=False,
         situation="Reel arrived. Buyer loves the quality and asks if seller has other Japanese fishing gear."),

    # ========== E: 到着後不満・トラブル ==========
    dict(id="E1_denim_size_wrong",
         category="return", stage="S1", product_name="Vintage 1947 Levi's 501 Big E Selvedge Jeans (W34)",
         product_category="Vintage Clothing",
         emotion="frustrated", language="en", desc_provided=False,
         situation="Jeans arrived but the waist is clearly smaller than listed W34. Buyer is upset because vintage measurements should be accurate."),
    dict(id="E2_ceramic_broken",
         category="claim", stage="S1", product_name="Antique Imari Ware Porcelain Vase Meiji Period",
         product_category="Asian Antiques / Ceramics",
         emotion="very_upset", language="en", desc_provided=False,
         situation="Vase arrived shattered. Buyer sent photos of the broken pieces and packaging. Very disappointed."),
    dict(id="E3_bag_authenticity",
         category="claim", stage="S2", product_name="Hermès Birkin 30 Togo Leather Bag",
         product_category="Luxury Bags / Hermès",
         emotion="angry", language="en", desc_provided=False,
         situation="Bag arrived. Buyer had it authenticated by a third party who says it's a counterfeit. Has already exchanged 2 messages with seller. Demands immediate full refund."),
    dict(id="E4_shirt_color_diff",
         category="claim", stage="S2", product_name="Supreme Box Logo Hoodie FW20 Dark Green",
         product_category="Streetwear / Hoodies",
         emotion="disappointed", language="en", desc_provided=False,
         situation="Hoodie arrived but the color is much darker than in photos. Buyer has asked once and is now pushing for a partial refund."),
    dict(id="E5_audio_defective",
         category="claim", stage="S3", product_name="Luxman L-507uXII Integrated Amplifier",
         product_category="Audio Equipment",
         emotion="frustrated", language="en", desc_provided=False,
         situation="Amp arrived but right channel has distortion. Buyer had initial OK correspondence, now reports new development: defect found after 2 days of use."),
    dict(id="E6_jewelry_not_received",
         category="claim", stage="S1", product_name="Mikimoto Pearl Akoya Necklace 7mm 18k Gold Clasp",
         product_category="Jewelry / Pearls",
         emotion="panicked", language="en", desc_provided=False,
         situation="Tracking says delivered 5 days ago but buyer never received. High value item. First time contacting seller, clearly anxious."),

    # ========== F: リクエスト対応 ==========
    dict(id="F1_sneakers_return_size",
         category="return", stage="S2", product_name="New Balance 990v6 Made in USA Grey",
         product_category="Sneakers",
         emotion="neutral", language="en", desc_provided=False,
         situation="Buyer says the shoes don't fit — narrow toe box. Has already discussed once with seller and now formally requests a return."),
    dict(id="F2_figure_exchange",
         category="return", stage="S2", product_name="Good Smile Company Nendoroid 1234 Marin Kitagawa",
         product_category="Anime Collectibles",
         emotion="politely_concerned", language="en", desc_provided=False,
         situation="Buyer received wrong variant (received 'Dress Ver' but ordered 'Swimsuit Ver'). Requests exchange. Polite but firm."),
    dict(id="F3_watch_partial_refund",
         category="return", stage="S2", product_name="Omega Speedmaster Professional Moonwatch 3570.50",
         product_category="Wristwatches / Luxury",
         emotion="disappointed", language="en", desc_provided=False,
         situation="Minor scratches not visible in photos. Buyer asks for $200 partial refund instead of return."),
    dict(id="F4_camera_case_inr",
         category="claim", stage="S3", product_name="Hasselblad 500C/M Medium Format Camera Body",
         product_category="Vintage Cameras",
         emotion="cold_and_firm", language="en", desc_provided=False,
         situation="Item not received 18 days after delivery estimate. Buyer has opened an eBay case. New development that changes the tone."),
    dict(id="F5_game_return_shipping",
         category="return", stage="S2", product_name="Sony PlayStation 2 Original Slim (JP Region, Modded)",
         product_category="Video Game Consoles",
         emotion="dissatisfied", language="en", desc_provided=False,
         situation="Console has issue. Buyer received return label but thinks return shipping cost should be covered fully. Argues the defect is seller's fault."),
    dict(id="F6_card_return_thanks",
         category="general", stage="S4", product_name="Pokemon 151 Japanese Booster Box Sealed",
         product_category="Collectible Card Games",
         emotion="relieved", language="en", desc_provided=False,
         situation="Return was resolved smoothly. Buyer says thanks."),
    dict(id="F7_guitar_return_howto",
         category="return", stage="S1", product_name="Martin D-28 Standard Acoustic Guitar",
         product_category="Musical Instruments / Guitars",
         emotion="first_time_buyer", language="en", desc_provided=False,
         situation="First time using eBay returns. Item has a finish defect. Asks seller what to do — doesn't know the process."),

    # ========== G: 複合・複雑ケース ==========
    dict(id="G1_watch_customs_refund",
         category="claim", stage="S2", product_name="Grand Seiko SBGA413 Shunbun Spring Drive",
         product_category="Wristwatches / Luxury",
         emotion="angry", language="en", desc_provided=False,
         situation="Buyer paid $280 customs fees. Item has a condition issue. Now wants return + customs reimbursement + refund of original payment. Multi-issue complaint."),
    dict(id="G2_train_wrong_item",
         category="claim", stage="S2", product_name="Kato N-Gauge Shinkansen 500 Series 16-car Set",
         product_category="Model Trains",
         emotion="annoyed", language="en", desc_provided=False,
         situation="Received wrong item (got 700 series instead of 500). Also shipment was delayed 10 days. Now requests cancellation AND wants compensation for hassle."),
    dict(id="G3_antique_long_silence",
         category="claim", stage="S3", product_name="Japanese Tanto Dagger Edo Period with Koshirae",
         product_category="Samurai / Nihonto",
         emotion="frustrated", language="en", desc_provided=False,
         situation="Bought 6 weeks ago. Shipped but tracking has been stuck for 4 weeks at overseas customs. Buyer had given up, now reaches out angrily after long silence."),
    dict(id="G4_cam_german",
         category="discount", stage="S2", product_name="Contax G2 Body with 45mm Planar Lens Kit",
         product_category="Vintage Cameras",
         emotion="polite_but_pushing", language="de", desc_provided=False,
         situation="German-speaking buyer negotiating price — 2nd round of negotiation. Writes in German."),
    dict(id="G5_perfume_spanish",
         category="return", stage="S2", product_name="Chanel No. 5 Eau de Parfum 100ml Vintage Formula",
         product_category="Perfume / Fragrance",
         emotion="worried", language="es", desc_provided=False,
         situation="Spanish-speaking buyer. Received perfume but suspects it's not authentic. Wants refund. Writes in Spanish."),

    # ========== H: 交渉・オファー ==========
    dict(id="H1_bag_price_offer",
         category="discount", stage="S1", product_name="Chanel Classic Flap Medium Caviar Leather Black GHW",
         product_category="Luxury Bags / Chanel",
         emotion="confident", language="en", desc_provided=False,
         situation="Listed at $7,500. Buyer offers $6,200 directly in a message (not through Best Offer feature)."),
    dict(id="H2_cards_bulk",
         category="discount", stage="S1", product_name="Magic: The Gathering Modern Horizons 3 Booster Box",
         product_category="Collectible Card Games",
         emotion="neutral", language="en", desc_provided=False,
         situation="Buyer asks: 'If I buy 3 boxes, can you offer a discount?'"),
    dict(id="H3_watch_re_nego",
         category="discount", stage="S2", product_name="Seiko Credor Eichi II Porcelain Dial Platinum",
         product_category="Wristwatches / Luxury",
         emotion="persistent", language="en", desc_provided=False,
         situation="Seller declined first offer. Buyer counters with higher offer and pushes for a deal."),
    dict(id="H4_sneakers_reoffer",
         category="discount", stage="S1", product_name="Nike Air Force 1 Off-White Virgil Abloh 'The Ten' Volt",
         product_category="Sneakers / Limited Edition",
         emotion="casual", language="en", desc_provided=False,
         situation="Seller's Best Offer auto-declined buyer's previous attempt. Buyer now sends a message outside Best Offer asking 'what's your best price?'"),
]


# ============================================================
# AI生成プロンプト
# ============================================================

GEN_PROMPT_TEMPLATE = """You are generating a realistic eBay chat conversation for testing BayChat AI Reply system.

SCENARIO:
- Product: {product_name} (category: {product_category})
- Stage: {stage} — {stage_desc}
- Situation: {situation}
- Buyer's emotional state: {emotion}
- Language: {language}

TASK: Return a JSON object with:

{{
  "item_info": {{
    "ItemID": "<11-digit random number>",
    "Title": "<product title — match the given product name>",
    "PrimaryCategoryName": "<eBay category path like 'Cameras & Photo:Film Cameras:Rangefinder'>",
    "ListingType": "FixedPriceItem",
    "StartPrice": "<price in USD, string>",
    "CurrentPrice": "<same as StartPrice>",
    "Quantity": "<int as string, e.g. '1' for unique items>",
    "ListingStatus": "Active",
    "ShippingType": "Flat",
    "ShippingService": "<like 'US_ExpeditedSppedPAK' or 'EMS International'>",
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
    // START with 1 system event if applicable (like "event: [timestamp] purchase_completed")
    // THEN a realistic back-and-forth between user(buyer) and assistant(seller)
    // EACH content for user/assistant should begin with [ISO-8601 timestamp]
    // FINALLY end with ONE user message — the "latest" buyer message matching the scenario
    // DO NOT include seller's reply to that latest message (AI Reply will generate it)
    {{"role": "system", "content": "event: [2026-03-DDTHH:MM:SS.000Z] purchase_completed"}},
    {{"role": "assistant", "content": "[2026-03-DDTHH:MM:SS.000Z] Hello buyer, ..."}},
    {{"role": "user", "content": "[2026-04-DDTHH:MM:SS.000Z] Buyer's latest message here"}}
  ],
  "latest_buyer_message": "<same as the last user content, without timestamp>"
}}

CONSTRAINTS:
1. Timestamps should be realistic — purchase 2-4 weeks ago for shipped items, days apart for recent messages
2. Seller replies should be professional eBay CS — polite, solution-focused, signed naturally
3. The LAST message in `messages` MUST be from `user` (buyer) — this is what AI Reply will answer
4. Buyer's final message should reflect the specified emotion
5. For Stage S1 (new inquiry): little or no history (1 system event + maybe 1 user message)
6. For Stage S2 (in progress): 3-7 back-and-forth exchanges already happened
7. For Stage S3 (new development): some history then a new situation emerges in the final buyer message
8. For Stage S4 (closing): history of resolution, then buyer thanks/closes
9. Write messages in the specified language ({language})
10. If language is "de" (German) or "es" (Spanish), write the user/assistant messages in that language
11. Include realistic product detail (title, size, color variations if relevant) in item_info
12. Seller can be named varied ("Kei", "Tanaka", "Yamamoto Yuki", or a shop name) — do not always use the same seller name; match to product genre

Output ONLY valid JSON. No markdown, no commentary."""


# ============================================================
# 実行
# ============================================================

def generate_case(scenario, client):
    """1シナリオ分のテストケースを生成"""
    prompt = GEN_PROMPT_TEMPLATE.format(
        product_name=scenario["product_name"],
        product_category=scenario["product_category"],
        stage=scenario["stage"],
        stage_desc=STAGE_DESC[scenario["stage"]],
        situation=scenario["situation"],
        emotion=scenario["emotion"],
        language=scenario["language"],
    )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,  # 多様性重視
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def build_test_case(scenario, gen_result):
    """既存テストケース構造に変換"""
    item_info = gen_result.get("item_info", {})
    messages = gen_result.get("messages", [])
    latest_buyer = gen_result.get("latest_buyer_message", "")

    # input配列を構築: [0]=商品情報(developer) + chat history
    input_messages = [
        {"role": "developer", "content": json.dumps(item_info, ensure_ascii=False)}
    ]
    input_messages.extend(messages)

    # buyer_ebay は item_info から取れないので固定名
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
        "buyer_message_ja": "",  # 後付け
        "history_ja": [],  # 後付け
        "num_messages": len(messages),
        "has_seller_history": any(m.get("role") == "assistant" for m in messages),
        "input": input_messages,
    }


def main():
    if not OPENAI_API_KEY:
        print("[ERROR] OPENAI_API_KEY not found in .env")
        return

    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    print(f"[1] 40シナリオ設計済み")
    print(f"[2] GPT-4.1-Mini で履歴本文を生成中...")

    results = []
    failed = []
    for i, scenario in enumerate(SCENARIOS, 1):
        print(f"  [{i:2d}/40] {scenario['id']} ({scenario['stage']} / {scenario['language']}) ...", end="", flush=True)
        try:
            gen = generate_case(scenario, client)
            tc = build_test_case(scenario, gen)
            results.append(tc)
            n_msg = tc["num_messages"]
            print(f" OK ({n_msg} msgs)")
            time.sleep(0.3)
        except Exception as e:
            print(f" FAILED: {e}")
            failed.append((scenario["id"], str(e)))

    print(f"\n[3] 生成成功: {len(results)}/40件, 失敗: {len(failed)}件")

    # 保存
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[4] 保存完了: {OUT_PATH}")

    # サマリ
    print("\n=== シナリオ分布 ===")
    from collections import Counter
    by_category = Counter(r["category"] for r in results)
    by_stage = Counter(r["stage"] for r in results)
    by_lang = Counter(r["language"] for r in results)
    print(f"  カテゴリ: {dict(by_category)}")
    print(f"  ステージ: {dict(by_stage)}")
    print(f"  言語: {dict(by_lang)}")

    if failed:
        print("\n=== 失敗リスト ===")
        for sid, err in failed:
            print(f"  {sid}: {err}")


if __name__ == "__main__":
    main()
