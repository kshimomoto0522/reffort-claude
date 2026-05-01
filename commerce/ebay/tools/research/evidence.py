"""
販売実績の代理指標スコアリング（sales evidence score）

【目的】
Browse API で取得可能な複数シグナルから「この商品が本当に売れる根拠」を
0-100 スコアで定量化する。Marketplace Insights API（SOLD データ・実質取得困難）
の代替として、合法的・無申請で取れる「需要・競合・価格・時間軸」シグナルの
複合判断で意思決定する。

【設計思想（Agent D 2026-05-01 リサーチ反映）】
1. 単一シグナルは決定的ではない → 複数シグナルの加点方式
2. watch_count は無申請では取れない → Optional・あれば強力加点・無くても破綻しない
3. 各シグナルに方向性ラベル（strong/moderate/weak/unavailable）を付与
4. 競合セラー数は釣鐘型評価（少なすぎ＝需要不明、多すぎ＝飽和、8-25が健全）

【根拠（2026/5 時点）】
- eBay User Agreement 2026/2/20 改訂で AI/LLM bot scraping 全面禁止 → Browse API のみ
- Browse API search response の `total` = 出品総数（無申請）
- itemSummaries の seller.username 集計 = ユニークセラー数（無申請）
- price.value 集計 = 価格分布（無申請）
- watchCount = restricted field（要 App Check 申請）
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


# 重み（合計 100 点・watch_count 未取得時は 25 点を他シグナルに按分）
WEIGHTS = {
    'watch_count':              25.0,
    'competitor_count':         20.0,
    'same_model_seller_count':  15.0,
    'listing_total_count':      10.0,
    'price_competitiveness':    15.0,
    'days_since_first_listed':  10.0,
    'top_seller_feedback_score': 5.0,
}


@dataclass
class SignalBreakdown:
    name: str
    raw_value: object
    contribution: float
    label: str  # 'strong' / 'moderate' / 'weak' / 'unavailable'


# ---- 個別シグナル ---------------------------------------------------------


def _score_watch_count(watch: Optional[int], weight: float) -> SignalBreakdown:
    if watch is None:
        return SignalBreakdown('watch_count', None, 0.0, 'unavailable')
    if watch >= 50:
        return SignalBreakdown('watch_count', watch, weight, 'strong')
    if watch >= 20:
        return SignalBreakdown('watch_count', watch, weight * 0.7, 'moderate')
    if watch >= 5:
        return SignalBreakdown('watch_count', watch, weight * 0.35, 'weak')
    return SignalBreakdown('watch_count', watch, 0.0, 'weak')


def _score_competitor_count(count: int, weight: float) -> SignalBreakdown:
    """釣鐘型評価: 8-25 が健全、少なすぎ・多すぎは減点。"""
    if count == 0:
        return SignalBreakdown('competitor_count', 0, 0.0, 'weak')
    if 8 <= count <= 25:
        return SignalBreakdown('competitor_count', count, weight, 'strong')
    if 3 <= count <= 7:
        return SignalBreakdown('competitor_count', count, weight * 0.55, 'moderate')
    if 26 <= count <= 50:
        return SignalBreakdown('competitor_count', count, weight * 0.55, 'moderate')
    if count >= 51:
        penalty = min(0.4, (count - 50) / 200)
        return SignalBreakdown('competitor_count', count, weight * (0.4 - penalty), 'weak')
    return SignalBreakdown('competitor_count', count, weight * 0.2, 'weak')


def _score_same_model(count: int, weight: float) -> SignalBreakdown:
    """同型番セラー多 = ライバル成功している証拠。"""
    if count >= 5:
        return SignalBreakdown('same_model_seller_count', count, weight, 'strong')
    if count >= 3:
        return SignalBreakdown('same_model_seller_count', count, weight * 0.65, 'moderate')
    if count == 2:
        return SignalBreakdown('same_model_seller_count', count, weight * 0.35, 'weak')
    return SignalBreakdown('same_model_seller_count', count, 0.0, 'weak')


def _score_listing_total(total: int, weight: float) -> SignalBreakdown:
    if total >= 200:
        return SignalBreakdown('listing_total_count', total, weight, 'strong')
    if total >= 50:
        return SignalBreakdown('listing_total_count', total, weight * 0.7, 'moderate')
    if total >= 10:
        return SignalBreakdown('listing_total_count', total, weight * 0.4, 'weak')
    return SignalBreakdown('listing_total_count', total, 0.0, 'weak')


def _score_price(median_usd: float, target_usd: float, weight: float) -> tuple[SignalBreakdown, str]:
    if median_usd <= 0 or target_usd <= 0:
        return SignalBreakdown('price_competitiveness', None, 0.0, 'unavailable'), 'parity'
    ratio = target_usd / median_usd
    if 0.92 <= ratio <= 0.98:
        return SignalBreakdown('price_competitiveness', round(ratio, 3), weight, 'strong'), 'wins'
    if 0.99 <= ratio <= 1.05:
        return SignalBreakdown('price_competitiveness', round(ratio, 3), weight * 0.65, 'moderate'), 'parity'
    if 0.85 <= ratio < 0.92:
        return SignalBreakdown('price_competitiveness', round(ratio, 3), weight * 0.55, 'moderate'), 'wins'
    if 1.06 <= ratio <= 1.15:
        return SignalBreakdown('price_competitiveness', round(ratio, 3), weight * 0.30, 'weak'), 'loses'
    return SignalBreakdown('price_competitiveness', round(ratio, 3), 0.0, 'weak'), 'loses'


def _score_days_listed(days: int, weight: float) -> SignalBreakdown:
    if days >= 90:
        return SignalBreakdown('days_since_first_listed', days, weight, 'strong')
    if days >= 30:
        return SignalBreakdown('days_since_first_listed', days, weight * 0.65, 'moderate')
    if days >= 7:
        return SignalBreakdown('days_since_first_listed', days, weight * 0.4, 'moderate')
    return SignalBreakdown('days_since_first_listed', days, 0.0, 'weak')


def _score_top_seller(score: int, weight: float) -> SignalBreakdown:
    if score >= 10000:
        return SignalBreakdown('top_seller_feedback_score', score, weight, 'strong')
    if score >= 1000:
        return SignalBreakdown('top_seller_feedback_score', score, weight * 0.6, 'moderate')
    if score >= 100:
        return SignalBreakdown('top_seller_feedback_score', score, weight * 0.3, 'weak')
    return SignalBreakdown('top_seller_feedback_score', score, 0.0, 'weak')


# ---- 統合スコア ----------------------------------------------------------


def sales_evidence_score(
    *,
    watch_count: Optional[int],
    competitor_count: int,
    same_model_seller_count: int,
    listing_total_count: int,
    price_median_usd: float,
    target_price_usd: float,
    days_since_first_listed: int,
    top_seller_feedback_score: int,
) -> dict:
    """
    0-100 スコアを返す。
      score >= 75 : strong（自信もって出品候補）
      score >= 60 : moderate（条件次第で出品可）
      score >= 45 : weak（要追加調査）
      score < 45  : insufficient（候補にしない）
    """
    weights = WEIGHTS.copy()
    if watch_count is None:
        unavailable = weights.pop('watch_count')
        for k in weights:
            weights[k] += unavailable / len(weights)

    breakdown: list[SignalBreakdown] = []

    if watch_count is not None:
        breakdown.append(_score_watch_count(watch_count, weights['watch_count']))
    breakdown.append(_score_competitor_count(competitor_count, weights['competitor_count']))
    breakdown.append(_score_same_model(same_model_seller_count, weights['same_model_seller_count']))
    breakdown.append(_score_listing_total(listing_total_count, weights['listing_total_count']))
    price_signal, price_label = _score_price(price_median_usd, target_price_usd, weights['price_competitiveness'])
    breakdown.append(price_signal)
    breakdown.append(_score_days_listed(days_since_first_listed, weights['days_since_first_listed']))
    breakdown.append(_score_top_seller(top_seller_feedback_score, weights['top_seller_feedback_score']))

    score = round(max(0.0, min(100.0, sum(b.contribution for b in breakdown))), 1)

    if score >= 75:
        verdict = 'strong'
    elif score >= 60:
        verdict = 'moderate'
    elif score >= 45:
        verdict = 'weak'
    else:
        verdict = 'insufficient'

    # demand_signal: watch / total / days_listed のうち strong がいくつあるか
    demand_strong = sum(1 for b in breakdown
                        if b.name in ('watch_count', 'listing_total_count', 'days_since_first_listed')
                        and b.label == 'strong')
    demand_signal = 'high' if demand_strong >= 2 else ('medium' if demand_strong == 1 else 'low')

    if competitor_count >= 51:
        competition_signal = 'saturated'
    elif competitor_count >= 8:
        competition_signal = 'healthy'
    else:
        competition_signal = 'sparse'

    parts = []
    if watch_count is not None:
        parts.append(f'watch={watch_count}')
    parts.append(f'競合セラー={competitor_count}人({competition_signal})')
    parts.append(f'同型番={same_model_seller_count}セラー')
    parts.append(f'総出品={listing_total_count}件')
    parts.append(f'$ {target_price_usd:.0f}vs中央$ {price_median_usd:.0f}({price_label})')
    parts.append(f'最古出品から{days_since_first_listed}日')
    parts.append(f'上位セラー評価={top_seller_feedback_score}')

    return {
        'score': score,
        'verdict': verdict,
        'demand_signal': demand_signal,
        'competition_signal': competition_signal,
        'price_competitiveness': price_label,
        'breakdown': [
            {'name': b.name, 'value': b.raw_value, 'points': round(b.contribution, 2), 'label': b.label}
            for b in breakdown
        ],
        'rationale': ' / '.join(parts),
    }


# ---- Browse API レスポンス → スコア入力の集約 -----------------------------


def aggregate_signals_from_browse(
    *,
    item_summaries: list[dict],
    total: int,
    target_price_usd: float,
    target_model_code: Optional[str] = None,
    target_watch_count: Optional[int] = None,
) -> dict:
    """
    Browse API search の itemSummaries 配列 → sales_evidence_score の入力 dict。
    """
    sellers = {(it.get('seller') or {}).get('username')
               for it in item_summaries
               if (it.get('seller') or {}).get('username')}
    competitor_count = len(sellers)

    same_model_seller_count = 0
    if target_model_code:
        m_low = target_model_code.lower()
        same = {(it.get('seller') or {}).get('username')
                for it in item_summaries
                if m_low in (it.get('title') or '').lower() and (it.get('seller') or {}).get('username')}
        same_model_seller_count = len(same)

    prices = []
    for it in item_summaries:
        try:
            v = float((it.get('price') or {}).get('value') or 0)
            if v > 0:
                prices.append(v)
        except (TypeError, ValueError):
            continue
    if prices:
        prices.sort()
        if len(prices) >= 4:
            q1 = prices[len(prices) // 4]
            q3 = prices[3 * len(prices) // 4]
            iqr = q3 - q1
            lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            cleaned = [p for p in prices if lo <= p <= hi]
            price_median_usd = statistics.median(cleaned) if cleaned else statistics.median(prices)
        else:
            price_median_usd = statistics.median(prices)
    else:
        price_median_usd = 0.0

    oldest_dates = []
    for it in item_summaries:
        d = it.get('itemCreationDate')
        if d:
            try:
                dt = datetime.fromisoformat(d.replace('Z', '+00:00'))
                oldest_dates.append(dt)
            except ValueError:
                continue
    days_since_first_listed = 0
    if oldest_dates:
        days_since_first_listed = (datetime.now(timezone.utc) - min(oldest_dates)).days

    top_score = 0
    for it in item_summaries:
        try:
            fs = int((it.get('seller') or {}).get('feedbackScore') or 0)
            if fs > top_score:
                top_score = fs
        except (TypeError, ValueError):
            continue

    return {
        'watch_count': target_watch_count,
        'competitor_count': competitor_count,
        'same_model_seller_count': same_model_seller_count,
        'listing_total_count': total,
        'price_median_usd': round(price_median_usd, 2),
        'target_price_usd': target_price_usd,
        'days_since_first_listed': days_since_first_listed,
        'top_seller_feedback_score': top_score,
    }


if __name__ == '__main__':
    print('▼ ケース1: 健全な競合・watch なし（典型ケース）')
    inp = {
        'watch_count': None,
        'competitor_count': 15,
        'same_model_seller_count': 6,
        'listing_total_count': 180,
        'price_median_usd': 160.0,
        'target_price_usd': 153.0,
        'days_since_first_listed': 120,
        'top_seller_feedback_score': 8500,
    }
    r = sales_evidence_score(**inp)
    print(f'  score={r["score"]} verdict={r["verdict"]} '
          f'demand={r["demand_signal"]} competition={r["competition_signal"]} '
          f'price={r["price_competitiveness"]}')
    print(f'  {r["rationale"]}')

    print('\n▼ ケース2: 高すぎ・飽和・watch なし')
    r2 = sales_evidence_score(**{
        'watch_count': None,
        'competitor_count': 80,
        'same_model_seller_count': 4,
        'listing_total_count': 520,
        'price_median_usd': 120.0,
        'target_price_usd': 180.0,
        'days_since_first_listed': 200,
        'top_seller_feedback_score': 15000,
    })
    print(f'  score={r2["score"]} verdict={r2["verdict"]} {r2["rationale"]}')

    print('\n▼ ケース3: ニッチ過ぎ（候補にしない）')
    r3 = sales_evidence_score(**{
        'watch_count': None,
        'competitor_count': 1,
        'same_model_seller_count': 1,
        'listing_total_count': 4,
        'price_median_usd': 200.0,
        'target_price_usd': 200.0,
        'days_since_first_listed': 5,
        'top_seller_feedback_score': 80,
    })
    print(f'  score={r3["score"]} verdict={r3["verdict"]} {r3["rationale"]}')
