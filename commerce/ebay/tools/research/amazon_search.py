"""
Amazon.co.jp 検索結果スクレイパー

【方針】
- 公式 PA-API は 2026/5/15 廃止 + 直近 30 日 10 件売上要件で実質不可
- リサーチ Agent（2026-05-01）の検証で `curl_cffi 0.14.0` + chrome131 TLS 偽装で
  日本 IP から status=200 / 60 カード取得確認済み
- 新品/中古フィルタは URL の `rh` パラメータで明示的に切り替え

【レート制限ポリシー】
- 1 リクエストあたり 2 ± 0.5 秒間隔（一定間隔だと機械検知される）
- 1 日合計 500 クエリ未満を目安

【参考】
- robots.txt の `/s` パスは Disallow されていない（明示禁止対象外）
- ただし Amazon Conditions of Use 上、商用無在庫リサーチは「社内補助」用途に留める

【取れる情報】
- ASIN（Amazon の商品 ID）
- 商品名・価格（円）・評価点・レビュー数
- Prime 適用フラグ
- 商品 URL
"""

import os
import re
import sys
import time
import random
import urllib.parse
from typing import Optional

from curl_cffi import requests as ccr
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

# 商品状態フィルタ（amazon.co.jp で実機確認済み）
# rh=p_n_condition-type%3A<id>
CONDITION_RH = {
    'new':  'p_n_condition-type%3A2224371051',
    'used': 'p_n_condition-type%3A2224372051',
    'all':  None,
}

DEFAULT_HEADERS = {
    'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

LAST_REQUEST_TIME = [0.0]
MIN_INTERVAL_SEC = 2.0
JITTER_SEC = 0.5


def _polite_sleep():
    """Poisson 風のジッタ付きスリープ（一定間隔だとボット検知される）。"""
    elapsed = time.time() - LAST_REQUEST_TIME[0]
    target = MIN_INTERVAL_SEC + random.uniform(-JITTER_SEC, JITTER_SEC)
    if elapsed < target:
        time.sleep(target - elapsed)
    LAST_REQUEST_TIME[0] = time.time()


def _is_blocked_html(text: str) -> bool:
    return 'api-services-support@amazon.com' in text or 'detected unusual activity' in text.lower()


def _fetch_html(url: str) -> str:
    _polite_sleep()
    for attempt in range(3):
        try:
            r = ccr.get(url, impersonate='chrome131', headers=DEFAULT_HEADERS, timeout=30)
            if r.status_code == 200 and not _is_blocked_html(r.text):
                return r.text
            if r.status_code in (429, 503):
                time.sleep(5 * (attempt + 1))
                continue
            if _is_blocked_html(r.text):
                # CAPTCHA ブロック → さらに待ってリトライ
                time.sleep(10 * (attempt + 1))
                continue
            r.raise_for_status()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f'amazon fetch failed for {url}')


def _parse_yen(text: str) -> int:
    m = re.search(r'[\d,]+', text or '')
    return int(m.group().replace(',', '')) if m else 0


def _parse_rating(text: str) -> float:
    m = re.search(r'(\d+(?:\.\d+)?)', text or '')
    return float(m.group(1)) if m else 0.0


def _parse_int(text: str) -> int:
    m = re.search(r'[\d,]+', text or '')
    return int(m.group().replace(',', '')) if m else 0


def _normalize_card(card) -> Optional[dict]:
    asin = (card.get('data-asin') or '').strip()
    if not asin:
        return None

    title_el = card.find('h2')
    title = title_el.get_text(strip=True) if title_el else ''

    price_el = card.select_one('.a-price .a-offscreen')
    price_jpy = _parse_yen(price_el.get_text() if price_el else '')

    rating_el = card.select_one('span.a-icon-alt')
    rating = _parse_rating(rating_el.get_text() if rating_el else '')

    review_el = card.select_one('a[href*="#customerReviews"] span')
    review_count = _parse_int(review_el.get_text() if review_el else '')

    prime_el = card.select_one('i[aria-label="Amazon Prime"]')
    is_prime = bool(prime_el)

    image_el = card.select_one('img.s-image')
    image_url = image_el.get('src', '') if image_el else ''

    # 中古/新品の判定（タイトルや表示テキスト）
    full_text = f'{title} {card.get_text(" ", strip=True)[:300]}'
    condition = _infer_condition(full_text)

    return {
        'source': 'amazon',
        'name': title,
        'price_jpy': price_jpy,
        'asin': asin,
        'item_url': f'https://www.amazon.co.jp/dp/{asin}',
        'image_url': image_url,
        'rating': rating,
        'review_count': review_count,
        'is_prime': is_prime,
        'condition': condition,
        'shop_name': 'Amazon.co.jp',
        'is_free_shipping': is_prime,  # Prime は実質送料無料
    }


USED_MARKERS = [
    '【中古】', '[中古]', '(中古)', '中古品', '中古：',
    'USED', 'Used',
    '中古商品', '中古コンディション',
]


def _infer_condition(text: str) -> str:
    if not text:
        return 'unknown'
    for m in USED_MARKERS:
        if m in text:
            return 'used'
    return 'new'  # Amazon は明示マーカーなければ新品扱いが妥当（PA-API 廃止後の慣例）


# ---- public --------------------------------------------------------------


def search_by_keyword(
    keyword: str,
    *,
    max_items: int = 20,
    new_only: bool = True,
) -> list[dict]:
    """
    Amazon.co.jp 検索結果を取得。
    new_only=True で「中古」と判定されたカード（タイトルに【中古】等含む）を除外。
    URL 上の rh フィルタは Amazon 側で動作不安定だったため、ローカルフィルタに統一。
    """
    encoded = urllib.parse.quote_plus(keyword)
    url = f'https://www.amazon.co.jp/s?k={encoded}'

    html = _fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.find_all('div', {'data-component-type': 's-search-result'})

    items: list[dict] = []
    seen_asins: set[str] = set()
    for c in cards:
        norm = _normalize_card(c)
        if not norm:
            continue
        if norm['asin'] in seen_asins:
            continue
        seen_asins.add(norm['asin'])
        if norm['price_jpy'] <= 0:
            continue
        if new_only and norm['condition'] == 'used':
            continue
        items.append(norm)
        if len(items) >= max_items:
            break
    return items


def search_by_jan(jan: str, max_items: int = 10) -> list[dict]:
    return search_by_keyword(jan, max_items=max_items, new_only=True)


def cheapest_match(items: list[dict], *, exclude_used: bool = True) -> Optional[dict]:
    valid = [it for it in items if it['price_jpy'] > 0 and (not exclude_used or it.get('condition') != 'used')]
    if not valid:
        return None
    return min(valid, key=lambda it: it['price_jpy'])


if __name__ == '__main__':
    print('▼ Amazon.co.jp Nike Dunk Low（new only）')
    items = search_by_keyword('Nike Dunk Low', max_items=8, new_only=True)
    print(f'  取得 {len(items)} 件')
    for it in items[:8]:
        prime_tag = ' Prime' if it['is_prime'] else ''
        print(f"  ¥{it['price_jpy']:>7,}{prime_tag} | ★{it['rating']} ({it['review_count']}) | "
              f"[{it['condition']}] {it['name'][:55]} | ASIN={it['asin']}")
    cheap = cheapest_match(items)
    if cheap:
        print(f"\n  最安: ¥{cheap['price_jpy']:,} | {cheap['name'][:60]}")
        print(f"  {cheap['item_url']}")
