"""
eBay 無在庫リサーチツール — オーケストレーター（Ver.1）

【動作】
1. eBay Browse API で「日本セラー（itemLocationCountry:JP）」が出している商品を
   キーワード × カテゴリで網羅検索する（= ライバルが日本から無在庫で売っている確証）
2. 各商品のタイトルから型番・ブランドを抽出 → 楽天市場 + Yahoo!ショッピングを並列検索
3. 一致スコア >= 閾値の最安候補を採用
4. 全コスト（FVF・送料・関税・為替・国内コスト）を入れた利益計算
5. CSV + HTML レポートを生成

【根拠】
- eBay 検索ページのスクレイピングは User Agreement 違反 → Browse API のみ使用
- 楽天/Yahoo は公式 API キー社長登録待ちのため robots.txt 範囲内のスクレイピングで暫定動作
- 利益計算は 2026/4/29 リサーチ調査を反映（De Minimis 廃止 + Section 122 10% 等）

【使い方】
    python orchestrator.py             # デフォルトキーワードセットで実行
    python orchestrator.py --quick     # キーワード少なめで素早くテスト
"""

import os
import sys
import csv
import json
import time
import argparse
from datetime import datetime
from typing import Optional

sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, 'results')

import ebay_browse
import rakuten_search
import yahoo_shopping
import matcher
import pricing
import fx


# 「日本に強み・eBay で米国向け定番」のリサーチ対象キーワード
# 理由は CLAUDE.md / suppliers.md / 実データを参考に Reffort が現在主戦場としている領域 + 周辺
DEFAULT_KEYWORDS = [
    # スニーカー（FVF 8% / Reffort コア領域）
    'Nike Dunk Low',
    'Nike Air Jordan 1',
    'Onitsuka Tiger Mexico 66',
    'New Balance 990',
    'Asics Gel-Lyte III',
    'Mizuno Wave Rider',

    # カメラ（関税 10%・日本に強み）
    'Sony Alpha 7C',
    'Canon EOS R6',
    'Fujifilm X100V',

    # 楽器
    'Yamaha THR10',
    'Boss GT-1000',

    # ホビー（関税 10%・日本独自需要）
    'Tamiya Mini 4WD',
    'Bandai Gunpla MG',
    'Pokemon TCG Japanese',
]

QUICK_KEYWORDS = [
    'Nike Dunk Low',
    'Onitsuka Tiger Mexico 66',
    'Sony Alpha 7C',
    'Tamiya Mini 4WD',
]


def fetch_ebay_competitors(
    keyword: str,
    *,
    min_price: Optional[float],
    max_price: Optional[float],
    limit: int,
) -> list[dict]:
    """
    eBay US マーケットで日本セラー（itemLocationCountry=JP）の出品を取得。
    """
    try:
        items = ebay_browse.search_us_marketplace(
            keyword,
            min_price=min_price,
            max_price=max_price,
            condition_new=True,
            fixed_price_only=True,
            seller_country='JP',
            limit=limit,
        )
    except Exception as e:
        print(f'  ⚠️ eBay 検索失敗 [{keyword}]: {e}')
        return []
    return items


def find_supplier_match(ebay_title: str) -> Optional[dict]:
    """
    eBay タイトル → 楽天 + Yahoo!ショッピング → 一致スコア最大の候補を返す。
    """
    keyword = matcher.build_search_keyword(ebay_title, max_words=4)
    if not keyword:
        return None

    # 楽天で検索（最大 15 件）
    try:
        rakuten_items = rakuten_search.search_by_keyword(keyword, max_items=15)
    except Exception as e:
        print(f'    ⚠️ 楽天失敗: {e}')
        rakuten_items = []

    # Yahoo!ショッピングで検索（最大 15 件）
    try:
        yahoo_items = yahoo_shopping.search_by_keyword(keyword, max_items=15)
    except Exception as e:
        print(f'    ⚠️ Yahoo!失敗: {e}')
        yahoo_items = []

    candidates = rakuten_items + yahoo_items
    return matcher.best_supplier_match(ebay_title, candidates, min_score=45.0)


def calculate_for_item(ebay_item: dict, supplier: dict, *, fx_rate: float) -> dict:
    """
    eBay 出品 + 仕入候補 → 利益計算結果を返す。
    """
    sell_price_usd = float(ebay_item.get('price', {}).get('value', 0) or 0)

    # eBay 提示の送料（無料 or 固定）
    shipping_options = ebay_item.get('shippingOptions') or []
    buyer_paid_shipping_usd = 0.0
    for so in shipping_options:
        cost = (so.get('shippingCost') or {}).get('value')
        if cost is not None:
            try:
                buyer_paid_shipping_usd = float(cost)
                break
            except (TypeError, ValueError):
                pass

    title = ebay_item.get('title', '') or ''
    fvf_key, duty_key = pricing.infer_category_keys(title)

    # 重量推定: スニーカーで 1.5kg、楽器で 3kg、それ以外 1kg
    weight_kg = 1.0
    if fvf_key in ('sneakers_high', 'sneakers_low'):
        weight_kg = 1.5
    elif fvf_key == 'musical_inst':
        weight_kg = 3.0
    elif fvf_key == 'cameras':
        weight_kg = 1.2

    inputs = pricing.ProfitInputs(
        sell_price_usd=sell_price_usd,
        buyer_paid_shipping_usd=buyer_paid_shipping_usd,
        purchase_price_jpy=int(supplier.get('price_jpy', 0)),
        weight_kg=weight_kg,
        category_key=fvf_key,
        duty_key=duty_key,
        shipping_service='speedpak_economy',  # 最も一般的かつ安い
        store_tier='anchor',
        promoted_listing_rate=0.03,
        domestic_shipping_jpy=500,
        consumption_tax_refund=True,
        fx_rate_usd_jpy=fx_rate,
        fx_provider_markup=0.0085,
    )
    return pricing.calculate_profit(inputs)


def orchestrate(
    keywords: list[str],
    *,
    items_per_keyword: int = 8,
    min_price: float = 50.0,
    max_price: float = 600.0,
) -> list[dict]:
    """
    キーワード一覧 → eBay 検索 → 仕入マッチ → 利益計算 を回す。
    """
    print(f'▼ 為替取得')
    fx_rate = fx.get_usdjpy()
    print(f'   USD/JPY = {fx_rate}')

    print(f'▼ キーワード対象数: {len(keywords)} 件')
    candidates: list[dict] = []

    for ki, kw in enumerate(keywords, 1):
        print(f'\n[{ki}/{len(keywords)}] eBay 検索: {kw}')
        ebay_items = fetch_ebay_competitors(
            kw, min_price=min_price, max_price=max_price, limit=items_per_keyword
        )
        print(f'   日本セラー出品: {len(ebay_items)} 件')

        for ei, eitem in enumerate(ebay_items, 1):
            title = eitem.get('title', '')
            sell_price = (eitem.get('price') or {}).get('value', '')
            seller = (eitem.get('seller') or {}).get('username', '')
            print(f'   [{ei}/{len(ebay_items)}] ${sell_price} | {title[:55]}')

            # 仕入候補マッチング
            supplier = find_supplier_match(title)
            if not supplier:
                print(f'      → 仕入候補マッチなし（スキップ）')
                continue
            print(f'      → 仕入: {supplier["source"]} ¥{supplier["price_jpy"]:,} '
                  f'(score={supplier["match_score"]}) {supplier["name"][:40]}')

            # 利益計算
            try:
                calc = calculate_for_item(eitem, supplier, fx_rate=fx_rate)
            except Exception as e:
                print(f'      ⚠️ 利益計算失敗: {e}')
                continue

            # 統合レコード
            record = {
                'keyword': kw,
                'ebay_title': title,
                'ebay_url': eitem.get('itemWebUrl', ''),
                'ebay_seller': seller,
                'ebay_seller_feedback': (eitem.get('seller') or {}).get('feedbackPercentage', ''),
                'ebay_seller_score': (eitem.get('seller') or {}).get('feedbackScore', ''),
                'ebay_price_usd': calc['sell_price_usd'],
                'ebay_buyer_shipping_usd': calc['buyer_paid_shipping_usd'],
                'ebay_image': (eitem.get('image') or {}).get('imageUrl', ''),
                'supplier_source': supplier['source'],
                'supplier_name': supplier['name'],
                'supplier_url': supplier.get('item_url', ''),
                'supplier_price_jpy': supplier['price_jpy'],
                'supplier_shop': supplier.get('shop_name') or supplier.get('store_id', ''),
                'match_score': supplier['match_score'],
                'fvf_category': calc['category_key'],
                'duty_category': calc['duty_key'],
                'weight_kg': calc['weight_kg'],
                'gross_revenue_usd': calc['gross_revenue_usd'],
                'total_ebay_fees_usd': calc['total_ebay_fees_usd'],
                'shipping_cost_usd': calc['shipping_cost_usd'],
                'shipping_cost_jpy': calc['shipping_cost_jpy'],
                'purchase_price_usd': calc['purchase_price_usd'],
                'fx_loss_usd': calc['fx_loss_usd'],
                'us_import_duty_usd_buyer_pays': calc['us_import_duty_usd_buyer_pays'],
                'us_import_duty_rate': calc['us_import_duty_rate'],
                'net_profit_usd': calc['net_profit_usd'],
                'net_profit_jpy': calc['net_profit_jpy'],
                'profit_margin_pct': calc['profit_margin_pct'],
                'breakeven_purchase_jpy': calc['breakeven_purchase_jpy'],
                'fx_rate_usd_jpy': calc['fx_rate_usd_jpy'],
            }
            candidates.append(record)
            print(f'      💰 利益: ${calc["net_profit_usd"]} (¥{calc["net_profit_jpy"]:,}) / '
                  f'マージン {calc["profit_margin_pct"]}%')

    # 利益順にソート（赤字も残すが下位に）
    candidates.sort(key=lambda r: r['net_profit_usd'], reverse=True)
    return candidates


def save_csv(records: list[dict], path: str) -> None:
    if not records:
        return
    keys = list(records[0].keys())
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(records)


def save_json(records: list[dict], path: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2, default=str)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true', help='短いキーワードセットでテスト')
    parser.add_argument('--items', type=int, default=8, help='キーワードあたりの eBay 取得件数')
    parser.add_argument('--min-price', type=float, default=50.0)
    parser.add_argument('--max-price', type=float, default=600.0)
    args = parser.parse_args()

    keywords = QUICK_KEYWORDS if args.quick else DEFAULT_KEYWORDS

    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    t0 = time.time()
    records = orchestrate(
        keywords,
        items_per_keyword=args.items,
        min_price=args.min_price,
        max_price=args.max_price,
    )
    elapsed = time.time() - t0

    print(f'\n=== 完了: {len(records)} 件の利益計算済み候補（所要 {elapsed:.1f} 秒）===')
    profitable = [r for r in records if r['net_profit_usd'] > 0]
    print(f'   うち黒字候補: {len(profitable)} 件')

    csv_path = os.path.join(RESULTS_DIR, f'research_{timestamp}.csv')
    json_path = os.path.join(RESULTS_DIR, f'research_{timestamp}.json')
    save_csv(records, csv_path)
    save_json(records, json_path)

    # HTML レポート
    try:
        import report
        html_path = os.path.join(RESULTS_DIR, f'research_{timestamp}.html')
        report.render_html(records, html_path, generated_at=timestamp)
        print(f'\n📊 HTML: {html_path}')
    except Exception as e:
        print(f'   ⚠️ HTML 生成スキップ: {e}')

    print(f'📁 CSV : {csv_path}')
    print(f'📁 JSON: {json_path}')

    if profitable:
        print('\n🥇 黒字候補 TOP 5:')
        for r in profitable[:5]:
            print(f'  ${r["net_profit_usd"]:>7.2f} ({r["profit_margin_pct"]:.1f}%) | '
                  f'{r["ebay_title"][:60]}')
            print(f'     仕入 {r["supplier_source"]} ¥{r["supplier_price_jpy"]:,} → 売価 ${r["ebay_price_usd"]}')


if __name__ == '__main__':
    main()
