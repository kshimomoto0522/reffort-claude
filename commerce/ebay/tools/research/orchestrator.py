"""
eBay 無在庫リサーチツール — オーケストレーター（Ver.1.5）

【Ver.1 → Ver.1.5 改善】
1. 新品/中古フィルタ厳格化（楽天/Yahoo/Amazon/フリマすべて）
2. 仕入先 4 サイトに拡張: 楽天・Yahoo!ショッピング・Amazon.co.jp・Yahoo!フリマ
3. eBay 市場全体のシグナル取得（出品総数・価格中央値・ユニークセラー数・日本セラー数）
4. 「売れる根拠スコア（sales evidence score）」0-100 を全候補に付与
5. 赤字除外ゲート: マージン 15% 未満 / 純利益 $15 未満 / 根拠スコア 45 未満を除外
6. キーワードを 12 カテゴリ全網羅に拡張（スニーカー過度な比率を縮小）
7. HTML レポートに「根拠」セクション追加

【根拠（2026/5 リサーチ反映）】
- スニーカーは「47%しか利益が出ない」レッドオーシャン化（NPR 2026/1）
- 利益出やすい：JDM 自動車パーツ・カメラ・トレカ・腕時計・楽器・釣具・レトロゲーム・万年筆
- eBay 検索ページのスクレイピングは User Agreement 違反 → Browse API のみ
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
import amazon_search
import yahoo_furima
import surugaya_search
import matcher
import pricing
import evidence
import fx


# ----------------------------------------------------------------------------
# キーワード設定（Agent E 2026-05-01 提供の 12 カテゴリリスト準拠）
# 「松」高利益・低競争 / 「竹」標準・実績豊富 / 「梅」薄利多売
# ----------------------------------------------------------------------------

DEFAULT_KEYWORDS = [
    # 【松】高利益・低競争
    'JDM headlight Honda Civic Type R',
    'Skyline GT-R R34 OEM',
    'HKS turbo Toyota Supra',
    'Canon EF 70-200 F2.8 L IS',
    'Contax T2 film camera',
    'Helios 44 Takumar lens',
    'Ichiban Kuji Dragon Ball Masterlise',
    'Studio Ghibli figure limited',
    'One Piece P.O.P MAX Japan',

    # 【竹】標準・実績豊富
    'Pokemon Japanese SAR PSA 10',
    'One Piece OP SEC SR Japanese',
    'Yu-Gi-Oh 25th secret rare Japanese',
    'Casio G-Shock MR-G Japan',
    'Seiko Prospex SPB Japan',
    'Grand Seiko SBGA SBGV',
    'BOSS pedal DD-200 Japan',
    'Roland JC-22 amplifier',
    'Ibanez TS808 Tube Screamer',
    'Shimano Stella SW Japan',
    'Daiwa Saltiga Steez Japan',
    'Megabass Jackall lure JDM',
    'Famicom Disk System Japan',
    'PlayStation Suikoden Klonoa Japan',
    'Pokemon Crystal Gold Silver GBC',

    # 【梅】薄利多売・初心者向け
    'Pilot Custom 823 fountain pen',
    'Sailor Pro Gear King of Pen',
    'Namiki Yukari maki-e',
    'Japanese chef knife Tojiro Shun',
    'Edo kiriko sake glass crystal',
    'Comme des Garcons Porter',
    'Champion Reverse Weave 90s',

    # スニーカー（縮小・厳選 2 銘柄）
    'Onitsuka Tiger Mexico 66 Japan exclusive',
    'New Balance 990v6 Made in Japan',
]

QUICK_KEYWORDS = [
    'Pokemon Japanese SAR PSA 10',
    'Casio G-Shock MR-G Japan',
    'Ichiban Kuji Dragon Ball Masterlise',
    'Pilot Custom 823 fountain pen',
    'Onitsuka Tiger Mexico 66 Japan exclusive',
    'Helios 44 Takumar lens',
    'Shimano Stella SW Japan',
    'Famicom Disk System Japan',
]

# ゲートしきい値
MIN_PROFIT_USD = 15.0
MIN_MARGIN_PCT = 15.0
MIN_EVIDENCE_SCORE = 45.0


# ----------------------------------------------------------------------------
# 各層の関数
# ----------------------------------------------------------------------------


def fetch_ebay_market_and_jp_sellers(
    keyword: str,
    *,
    min_price: Optional[float],
    max_price: Optional[float],
    market_sample: int,
    jp_seller_limit: int,
) -> tuple[dict, list[dict]]:
    """
    1 キーワードに対して 2 種類の Browse API 呼び出し:
      A) 市場全体スナップショット（米国マーケット・新品・上限 100 件サンプル）
      B) 日本セラー出品リスト（リサーチ対象候補）
    """
    market: dict = {}
    try:
        market = ebay_browse.market_overview(
            keyword, min_price=min_price, max_price=max_price, sample_size=market_sample
        )
    except Exception as e:
        print(f'  ⚠️ market_overview 失敗: {e}')
        market = {
            'total_listed': 0, 'sampled': 0, 'unique_sellers': 0,
            'jp_seller_count': 0, 'us_seller_count': 0,
            'price_min_usd': 0.0, 'price_median_usd': 0.0,
            'price_p25_usd': 0.0, 'price_p75_usd': 0.0, 'price_max_usd': 0.0,
            'top_sellers': [],
        }

    jp_items: list[dict] = []
    try:
        jp_items = ebay_browse.search_us_marketplace(
            keyword,
            min_price=min_price, max_price=max_price,
            condition_new=True, fixed_price_only=True,
            seller_country='JP', limit=jp_seller_limit,
        )
    except Exception as e:
        print(f'  ⚠️ JP セラー検索失敗: {e}')

    return market, jp_items


def find_supplier_match(ebay_title: str) -> Optional[dict]:
    """
    eBay タイトル → 4 サイト並列検索 → 一致スコア最大の最安候補。
    新品のみ（new_only=True）厳格化。
    """
    keyword = matcher.build_search_keyword(ebay_title, max_words=4)
    if not keyword:
        return None

    candidates: list[dict] = []
    sources_attempted: list[str] = []

    # 楽天
    sources_attempted.append('rakuten')
    try:
        candidates.extend(rakuten_search.search_by_keyword(keyword, max_items=10, new_only=True))
    except Exception as e:
        print(f'    ⚠️ 楽天失敗: {e}')

    # Yahoo!ショッピング
    sources_attempted.append('yahoo_shopping')
    try:
        candidates.extend(yahoo_shopping.search_by_keyword(keyword, max_items=10, new_only=True))
    except Exception as e:
        print(f'    ⚠️ Yahoo!ショッピング失敗: {e}')

    # Amazon.co.jp
    sources_attempted.append('amazon')
    try:
        candidates.extend(amazon_search.search_by_keyword(keyword, max_items=10, new_only=True))
    except Exception as e:
        print(f'    ⚠️ Amazon 失敗: {e}')

    # Yahoo!フリマ
    sources_attempted.append('yahoo_furima')
    try:
        candidates.extend(yahoo_furima.search_by_keyword(keyword, max_items=10, new_only=True, on_sale_only=True))
    except Exception as e:
        print(f'    ⚠️ Yahoo!フリマ失敗: {e}')

    # 駿河屋（コレクター・ゲーム・トレカ・フィギュアで強い）
    sources_attempted.append('surugaya')
    try:
        candidates.extend(surugaya_search.search_by_keyword(keyword, max_items=10, new_only=True))
    except Exception as e:
        print(f'    ⚠️ 駿河屋失敗: {e}')

    # 一致スコアで採点して採用
    return matcher.best_supplier_match(ebay_title, candidates, min_score=45.0)


def calculate_for_item(ebay_item: dict, supplier: dict, *, fx_rate: float) -> dict:
    sell_price_usd = float(ebay_item.get('price', {}).get('value', 0) or 0)

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

    weight_kg = 1.0
    if fvf_key in ('sneakers_high', 'sneakers_low'):
        weight_kg = 1.5
    elif fvf_key == 'musical_inst':
        weight_kg = 3.0
    elif fvf_key == 'cameras':
        weight_kg = 1.2
    elif fvf_key == 'toys':
        weight_kg = 0.6
    elif fvf_key == 'watches_under5k':
        weight_kg = 0.4

    inputs = pricing.ProfitInputs(
        sell_price_usd=sell_price_usd,
        buyer_paid_shipping_usd=buyer_paid_shipping_usd,
        purchase_price_jpy=int(supplier.get('price_jpy', 0)),
        weight_kg=weight_kg,
        category_key=fvf_key,
        duty_key=duty_key,
        shipping_service='speedpak_economy',
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
    items_per_keyword: int,
    min_price: float,
    max_price: float,
    market_sample: int,
) -> tuple[list[dict], list[dict]]:
    """
    Returns: (passed_candidates, all_evaluated)
      passed_candidates: ゲート通過した候補のみ（HTML レポートに出す）
      all_evaluated: 全評価結果（CSV/JSON でログとして出す・赤字含む）
    """
    print(f'▼ 為替取得')
    fx_rate = fx.get_usdjpy()
    print(f'   USD/JPY = {fx_rate}')
    print(f'▼ キーワード対象数: {len(keywords)} 件')

    all_records: list[dict] = []

    for ki, kw in enumerate(keywords, 1):
        print(f'\n[{ki}/{len(keywords)}] キーワード: {kw}')

        market, jp_items = fetch_ebay_market_and_jp_sellers(
            kw,
            min_price=min_price, max_price=max_price,
            market_sample=market_sample, jp_seller_limit=items_per_keyword,
        )
        print(f'   市場: 出品総数 {market["total_listed"]:,} 件 / '
              f'ユニーク {market["unique_sellers"]} セラー / '
              f'JP={market["jp_seller_count"]} US={market["us_seller_count"]} / '
              f'価格 ${market["price_min_usd"]:.0f}-${market["price_max_usd"]:.0f} '
              f'(中央 ${market["price_median_usd"]:.0f})')
        print(f'   日本セラー出品: {len(jp_items)} 件')

        if not jp_items:
            continue

        market_summaries = ebay_browse.search_us_marketplace(
            kw, min_price=min_price, max_price=max_price,
            condition_new=True, fixed_price_only=True, limit=min(market_sample, 200),
        ) if market_sample > 0 else []

        for ei, eitem in enumerate(jp_items, 1):
            title = eitem.get('title', '')
            sell_price = (eitem.get('price') or {}).get('value', '')
            seller = (eitem.get('seller') or {}).get('username', '')
            print(f'   [{ei}/{len(jp_items)}] ${sell_price} | {title[:55]}')

            supplier = find_supplier_match(title)
            if not supplier:
                print(f'      → 仕入候補マッチなし（スキップ）')
                continue
            print(f'      → 仕入: {supplier["source"]} ¥{supplier["price_jpy"]:,} '
                  f'(score={supplier["match_score"]}) [{supplier.get("condition", "n/a")}]')

            try:
                calc = calculate_for_item(eitem, supplier, fx_rate=fx_rate)
            except Exception as e:
                print(f'      ⚠️ 利益計算失敗: {e}')
                continue

            # 売れる根拠スコア
            target_model = matcher.extract_model_code(title)
            try:
                target_price_usd = float(sell_price) if sell_price else 0.0
                signal_inputs = evidence.aggregate_signals_from_browse(
                    item_summaries=market_summaries,
                    total=market['total_listed'],
                    target_price_usd=target_price_usd,
                    target_model_code=target_model,
                    target_watch_count=eitem.get('watchCount'),
                )
                evid = evidence.sales_evidence_score(**signal_inputs)
            except Exception as e:
                print(f'      ⚠️ evidence 計算失敗: {e}')
                evid = {'score': 0, 'verdict': 'insufficient', 'rationale': 'evidence calc failed',
                        'demand_signal': 'low', 'competition_signal': 'sparse', 'price_competitiveness': 'parity'}

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
                'supplier_condition': supplier.get('condition', 'n/a'),
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

                # 市場シグナル
                'market_total_listed': market['total_listed'],
                'market_unique_sellers': market['unique_sellers'],
                'market_jp_sellers': market['jp_seller_count'],
                'market_us_sellers': market['us_seller_count'],
                'market_price_min_usd': market['price_min_usd'],
                'market_price_median_usd': market['price_median_usd'],
                'market_price_p75_usd': market['price_p75_usd'],
                'market_price_max_usd': market['price_max_usd'],

                # 売れる根拠
                'evidence_score': evid['score'],
                'evidence_verdict': evid['verdict'],
                'demand_signal': evid['demand_signal'],
                'competition_signal': evid['competition_signal'],
                'price_competitiveness': evid['price_competitiveness'],
                'evidence_rationale': evid['rationale'],
                'evidence_breakdown': evid.get('breakdown', []),
            }
            all_records.append(record)
            print(f'      💰 利益 ${calc["net_profit_usd"]} ({calc["profit_margin_pct"]}%) / '
                  f'根拠 {evid["score"]}点 [{evid["verdict"]}/{evid["demand_signal"]}/{evid["competition_signal"]}/{evid["price_competitiveness"]}]')

    # ゲート: 黒字 + マージン15%以上 + 利益$15以上 + evidence45以上
    passed = [
        r for r in all_records
        if r['net_profit_usd'] >= MIN_PROFIT_USD
        and r['profit_margin_pct'] >= MIN_MARGIN_PCT
        and r['evidence_score'] >= MIN_EVIDENCE_SCORE
    ]
    # 強い順にソート: evidence_score → net_profit_usd
    passed.sort(key=lambda r: (-r['evidence_score'], -r['net_profit_usd']))
    return passed, all_records


def save_csv(records: list[dict], path: str) -> None:
    if not records:
        return
    keys = [k for k in records[0].keys() if k != 'evidence_breakdown']
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        w.writeheader()
        w.writerows(records)


def save_json(records: list[dict], path: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2, default=str)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true', help='短いキーワードセットでテスト')
    parser.add_argument('--items', type=int, default=6, help='キーワードあたりの eBay 取得件数（日本セラー出品）')
    parser.add_argument('--min-price', type=float, default=30.0)
    parser.add_argument('--max-price', type=float, default=2000.0)
    parser.add_argument('--market-sample', type=int, default=100, help='市場全体のサンプリング件数')
    args = parser.parse_args()

    keywords = QUICK_KEYWORDS if args.quick else DEFAULT_KEYWORDS
    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    t0 = time.time()
    passed, all_records = orchestrate(
        keywords,
        items_per_keyword=args.items,
        min_price=args.min_price,
        max_price=args.max_price,
        market_sample=args.market_sample,
    )
    elapsed = time.time() - t0

    print(f'\n=== 完了: 全評価 {len(all_records)} 件 / ゲート通過 {len(passed)} 件（所要 {elapsed:.1f} 秒）===')
    print(f'   ゲート: 利益≥${MIN_PROFIT_USD} & マージン≥{MIN_MARGIN_PCT}% & 根拠≥{MIN_EVIDENCE_SCORE}点')

    csv_path = os.path.join(RESULTS_DIR, f'research_{timestamp}_all.csv')
    json_path = os.path.join(RESULTS_DIR, f'research_{timestamp}_all.json')
    save_csv(all_records, csv_path)
    save_json(all_records, json_path)

    try:
        import report
        html_path = os.path.join(RESULTS_DIR, f'research_{timestamp}.html')
        report.render_html(passed, html_path, generated_at=timestamp,
                            all_evaluated_count=len(all_records))
        print(f'\n📊 HTML（ゲート通過のみ）: {html_path}')
    except Exception as e:
        print(f'   ⚠️ HTML 生成スキップ: {e}')

    print(f'📁 CSV : {csv_path}')
    print(f'📁 JSON: {json_path}')

    if passed:
        print('\n🥇 ゲート通過 TOP 10:')
        for r in passed[:10]:
            print(f'  根拠 {r["evidence_score"]:>4.1f} | 利益 ${r["net_profit_usd"]:>6.2f} '
                  f'({r["profit_margin_pct"]:.0f}%) | {r["ebay_title"][:55]}')
            print(f'     仕入 {r["supplier_source"]} ¥{r["supplier_price_jpy"]:,} → 売価 ${r["ebay_price_usd"]} '
                  f'/ {r["competition_signal"]}/{r["demand_signal"]}/{r["price_competitiveness"]}')


if __name__ == '__main__':
    main()
