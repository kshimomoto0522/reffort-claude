"""
eBay 輸出（日本→米国）利益計算モジュール

【出典】
リサーチ Agent（2026-04-29 実施）が公式ドキュメント・eBay ヘルプ・FedEx/DHL 公開料金・
US 大統領令を横断調査して提示した数値テーブルを採用。

【特に重要な前提（2026 年版）】
- **De Minimis $800 免税は 2025/8/29 に廃止・継続中** → 全パッケージ関税対象
- **Section 122 全国 10% サーチャージは 2026/2/24 施行・2026/7/24 失効予定**
- スニーカー $150 以上は FVF 8%・per-order 免除（2024 年 StockX 対抗で導入）
- 売上税は eBay が買い手から徴収して州へ送金 → セラー粗利には**入れない**

【参考】
- eBay 手数料公式: https://www.ebay.com/help/selling/fees-credits-invoices/selling-fees?id=4822
- White House De Minimis Suspension (2026/2): https://www.whitehouse.gov/presidential-actions/2026/02/...
- Section 122 解説: https://www.tariffstool.com/guides/section-122-tariff-rates-2026
- Orange Connex SpeedPAK 2026 改定: https://www.orangeconnex.jp/newsDetail?title=...
"""

from dataclasses import dataclass
from typing import Optional


# -----------------------------------------------------------------------------
# 1. eBay FVF テーブル（2026 年 4 月時点・米国マーケット）
# -----------------------------------------------------------------------------
EBAY_FVF_TABLE: dict[str, dict] = {
    "sneakers_high":   {"rate": 0.080,  "tier_threshold": 7500.0, "tier_rate": 0.0235, "per_order_waived": True},
    "sneakers_low":    {"rate": 0.1325, "tier_threshold": 7500.0, "tier_rate": 0.0235, "per_order_waived": False},
    "cameras":         {"rate": 0.109,  "tier_threshold": 7500.0, "tier_rate": 0.0235, "per_order_waived": False},
    "electronics":     {"rate": 0.109,  "tier_threshold": 7500.0, "tier_rate": 0.0235, "per_order_waived": False},
    "musical_inst":    {"rate": 0.129,  "tier_threshold": 7500.0, "tier_rate": 0.0235, "per_order_waived": False},
    "toys":            {"rate": 0.149,  "tier_threshold": 7500.0, "tier_rate": 0.0235, "per_order_waived": False},
    "watches_under5k": {"rate": 0.149,  "tier_threshold": 7500.0, "tier_rate": 0.0235, "per_order_waived": False},
    "clothing":        {"rate": 0.136,  "tier_threshold": 7500.0, "tier_rate": 0.0235, "per_order_waived": False},
    "default":         {"rate": 0.136,  "tier_threshold": 7500.0, "tier_rate": 0.0235, "per_order_waived": False},
}

# Anchor Store 加入時の FVF 割引（約 0.9pt）
ANCHOR_STORE_DISCOUNT = 0.009


# -----------------------------------------------------------------------------
# 2. 米国輸入関税テーブル（HTS 概略 + Section 122 10% / 2026 年 4 月）
# -----------------------------------------------------------------------------
US_IMPORT_DUTY_TABLE: dict[str, dict] = {
    "sneakers_textile_rubber": {"mfn": 0.20,  "section_122": 0.10},  # 6404.11 — 30%
    "sneakers_leather":        {"mfn": 0.085, "section_122": 0.10},  # 6403.59 — 18.5%
    "cameras":                 {"mfn": 0.00,  "section_122": 0.10},  # 8525.81 — 10%
    "electronics":             {"mfn": 0.00,  "section_122": 0.10},  # 10%
    "musical_inst":            {"mfn": 0.067, "section_122": 0.10},  # 9202.90 — 16.7%平均
    "toys":                    {"mfn": 0.00,  "section_122": 0.10},  # 9503 — 10%
    "watches":                 {"mfn": 0.06,  "section_122": 0.10},  # 9102 — 簡易
    "clothing_cotton":         {"mfn": 0.165, "section_122": 0.10},  # 6109.10 — 26.5%
    "default":                 {"mfn": 0.05,  "section_122": 0.10},  # 不明時の安全側
}


# -----------------------------------------------------------------------------
# 3. 国際送料テーブル（JPY・実勢概算 / 2026 年 4 月）
# -----------------------------------------------------------------------------
SHIPPING_TABLE: dict[str, list[tuple[float, int]]] = {
    "speedpak_economy": [(1.0, 3020), (2.0, 5000), (3.0, 7000), (5.0, 10500), (10.0, 19000)],
    "speedpak_fedex":   [(1.0, 4500), (2.0, 7000), (3.0, 9500), (5.0, 13500), (10.0, 24000)],
    "fedex_priority":   [(1.0, 6500), (2.0, 9800), (3.0, 13000), (5.0, 19000), (10.0, 35000)],
    "fedex_economy":    [(1.0, 5300), (2.0, 8000), (3.0, 10500), (5.0, 15500), (10.0, 28000)],
    "dhl_express":      [(1.0, 7500), (2.0, 11000), (3.0, 14500), (5.0, 21500), (10.0, 38000)],
}


def estimate_shipping_jpy(weight_kg: float, service: str = "speedpak_economy") -> int:
    rates = SHIPPING_TABLE.get(service, SHIPPING_TABLE["speedpak_economy"])
    for w, jpy in rates:
        if weight_kg <= w:
            return jpy
    # 超過時は最大重量の比例で外挿
    return int(rates[-1][1] * (weight_kg / rates[-1][0]))


# -----------------------------------------------------------------------------
# 4. 自動カテゴリ判定（タイトル/カテゴリ ID から FVF と関税のキーを推定）
# -----------------------------------------------------------------------------

# eBay カテゴリ ID（部分一致）→ pricing キー
# 参考: https://www.ebay.com/sch/allcategories/all-categories
CATEGORY_HINTS: list[tuple[str, str, str]] = [
    # (タイトル正規表現の小文字, fvf_key, duty_key)
    (r"sneaker|nike|jordan|adidas|new balance|asics|onitsuka|reebok|puma|converse", "sneakers_high", "sneakers_textile_rubber"),
    (r"\bboot|leather shoe", "sneakers_leather", "sneakers_leather"),
    (r"camera|sony alpha|canon eos|nikon z|fujifilm|leica|olympus|lens", "cameras", "cameras"),
    (r"laptop|tablet|smartphone|iphone|ipad|playstation|nintendo switch|console", "electronics", "electronics"),
    (r"guitar|bass|drum|piano|amplifier|synthesizer|microphone", "musical_inst", "musical_inst"),
    (r"figure|gundam|lego|toy|action figure|funko|plush|gunpla", "toys", "toys"),
    (r"watch|seiko|grand seiko|casio g-shock|citizen", "watches_under5k", "watches"),
    (r"shirt|jacket|hoodie|jeans|dress|coat", "clothing", "clothing_cotton"),
]


def infer_category_keys(ebay_title: str) -> tuple[str, str]:
    """
    eBay タイトル文字列から FVF キーと関税キーを推定する。
    マッチしなかった場合は default。
    """
    import re
    title = (ebay_title or '').lower()
    for pat, fvf_key, duty_key in CATEGORY_HINTS:
        if re.search(pat, title):
            return fvf_key, duty_key
    return "default", "default"


# -----------------------------------------------------------------------------
# 5. メイン計算関数
# -----------------------------------------------------------------------------
@dataclass
class ProfitInputs:
    sell_price_usd: float                    # eBay 想定販売価格（買い手表示・税抜）
    purchase_price_jpy: int                  # 日本仕入れ価格（消費税込み）
    weight_kg: float = 1.0
    buyer_paid_shipping_usd: float = 0.0     # 買い手負担送料（FVF 対象に含まれる）
    category_key: str = "default"
    duty_key: str = "default"
    shipping_service: str = "speedpak_economy"
    store_tier: str = "anchor"               # "none" or "anchor"
    promoted_listing_rate: float = 0.02      # 0.02 = 2%
    international_fee_rate: float = 0.0165
    domestic_shipping_jpy: int = 500         # 仕入先→倉庫
    forwarder_fee_jpy: int = 0
    consumption_tax_refund: bool = True      # 課税事業者なら True
    fx_rate_usd_jpy: float = 159.0           # 呼び出し側で fx.get_usdjpy() を渡す
    fx_provider_markup: float = 0.0085       # Wise 基準（Payoneer なら 0.02）
    insertion_fee_usd: float = 0.0


def calculate_profit(p: ProfitInputs) -> dict:
    # ---- 売上総額（FVF 対象）
    gross_revenue_usd = p.sell_price_usd + p.buyer_paid_shipping_usd

    # ---- FVF 段階計算 + ストア割引
    fvf_cfg = EBAY_FVF_TABLE.get(p.category_key, EBAY_FVF_TABLE["default"])
    base_rate = fvf_cfg["rate"] - (ANCHOR_STORE_DISCOUNT if p.store_tier == "anchor" else 0)
    threshold = fvf_cfg["tier_threshold"]
    tier_rate = fvf_cfg["tier_rate"]

    if gross_revenue_usd <= threshold:
        ebay_fvf_usd = gross_revenue_usd * base_rate
    else:
        ebay_fvf_usd = (threshold * base_rate) + ((gross_revenue_usd - threshold) * tier_rate)

    # ---- per-order fee（スニーカー $150+ は免除）
    if fvf_cfg.get("per_order_waived") and p.sell_price_usd >= 150:
        per_order_fee_usd = 0.0
    else:
        per_order_fee_usd = 0.30 if gross_revenue_usd <= 10 else 0.40

    # ---- International Fee 1.65%
    international_fee_usd = gross_revenue_usd * p.international_fee_rate

    # ---- Promoted Listings Standard
    promoted_fee_usd = gross_revenue_usd * p.promoted_listing_rate

    # ---- 国際送料（JPY → USD 換算）
    shipping_cost_jpy = estimate_shipping_jpy(p.weight_kg, p.shipping_service)
    shipping_cost_usd = shipping_cost_jpy / p.fx_rate_usd_jpy

    # ---- 米国輸入関税（買い手払い・参考表示）
    duty_cfg = US_IMPORT_DUTY_TABLE.get(p.duty_key, US_IMPORT_DUTY_TABLE["default"])
    us_import_duty_rate = duty_cfg["mfn"] + duty_cfg["section_122"]
    us_import_duty_usd_buyer_pays = p.sell_price_usd * us_import_duty_rate

    # ---- 日本仕入価格（消費税還付の場合は税抜換算）
    if p.consumption_tax_refund:
        purchase_price_net_jpy = int(p.purchase_price_jpy / 1.10)
    else:
        purchase_price_net_jpy = p.purchase_price_jpy
    purchase_price_usd = purchase_price_net_jpy / p.fx_rate_usd_jpy

    # ---- 為替手数料（受取 USD → JPY 換金時のスプレッド）
    fx_loss_usd = (gross_revenue_usd - ebay_fvf_usd - per_order_fee_usd) * p.fx_provider_markup

    # ---- 純利益
    total_ebay_fees_usd = (
        ebay_fvf_usd
        + per_order_fee_usd
        + international_fee_usd
        + promoted_fee_usd
        + p.insertion_fee_usd
    )
    domestic_jpy_costs = p.domestic_shipping_jpy + p.forwarder_fee_jpy
    total_costs_usd = (
        total_ebay_fees_usd
        + shipping_cost_usd
        + purchase_price_usd
        + fx_loss_usd
        + domestic_jpy_costs / p.fx_rate_usd_jpy
    )

    net_profit_usd = gross_revenue_usd - total_costs_usd
    net_profit_jpy = net_profit_usd * p.fx_rate_usd_jpy
    profit_margin_pct = (net_profit_usd / gross_revenue_usd * 100) if gross_revenue_usd else 0

    # 損益分岐に必要な「最低 仕入れ価格 JPY」（粗利ゼロライン）
    breakeven_purchase_jpy = max(0, int((gross_revenue_usd - (total_ebay_fees_usd + shipping_cost_usd + fx_loss_usd) - domestic_jpy_costs / p.fx_rate_usd_jpy) * p.fx_rate_usd_jpy * (1.10 if p.consumption_tax_refund else 1.0)))

    return {
        # Inputs echo
        "sell_price_usd": p.sell_price_usd,
        "buyer_paid_shipping_usd": p.buyer_paid_shipping_usd,
        "purchase_price_jpy": p.purchase_price_jpy,
        "weight_kg": p.weight_kg,
        "fx_rate_usd_jpy": p.fx_rate_usd_jpy,
        "category_key": p.category_key,
        "duty_key": p.duty_key,
        "shipping_service": p.shipping_service,

        # Revenue
        "gross_revenue_usd": round(gross_revenue_usd, 2),

        # eBay fees
        "ebay_fvf_usd": round(ebay_fvf_usd, 2),
        "ebay_fvf_rate_effective": round(base_rate, 4),
        "per_order_fee_usd": round(per_order_fee_usd, 2),
        "international_fee_usd": round(international_fee_usd, 2),
        "promoted_fee_usd": round(promoted_fee_usd, 2),
        "insertion_fee_usd": round(p.insertion_fee_usd, 2),
        "total_ebay_fees_usd": round(total_ebay_fees_usd, 2),

        # Shipping
        "shipping_cost_jpy": shipping_cost_jpy,
        "shipping_cost_usd": round(shipping_cost_usd, 2),

        # Purchase
        "purchase_price_jpy_net": purchase_price_net_jpy,
        "purchase_price_usd": round(purchase_price_usd, 2),
        "domestic_jpy_costs": domestic_jpy_costs,

        # FX
        "fx_loss_usd": round(fx_loss_usd, 2),

        # Buyer-side info (参考表示)
        "us_import_duty_usd_buyer_pays": round(us_import_duty_usd_buyer_pays, 2),
        "us_import_duty_rate": round(us_import_duty_rate, 4),

        # Bottom line
        "net_profit_usd": round(net_profit_usd, 2),
        "net_profit_jpy": int(round(net_profit_jpy, 0)),
        "profit_margin_pct": round(profit_margin_pct, 2),

        # Useful derived
        "breakeven_purchase_jpy": breakeven_purchase_jpy,
    }


if __name__ == "__main__":
    # 検算: スニーカー $180 / 仕入 ¥15,000 / 1.5kg / Anchor Store / PL 3% / Wise
    inp = ProfitInputs(
        sell_price_usd=180.0,
        buyer_paid_shipping_usd=25.0,
        purchase_price_jpy=15000,
        weight_kg=1.5,
        category_key="sneakers_high",
        duty_key="sneakers_textile_rubber",
        shipping_service="speedpak_fedex",
        store_tier="anchor",
        promoted_listing_rate=0.03,
        domestic_shipping_jpy=500,
        consumption_tax_refund=True,
        fx_rate_usd_jpy=159.74,
        fx_provider_markup=0.0085,
    )
    res = calculate_profit(inp)
    for k, v in res.items():
        print(f"  {k:35s} {v}")
