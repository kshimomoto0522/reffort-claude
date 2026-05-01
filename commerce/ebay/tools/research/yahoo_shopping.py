"""
Yahoo!ショッピング 検索結果スクレイパー

【方針】
- 公式 V3 itemSearch API（Client ID 必要）は社長の登録待ち。
  Ver.1 は Next.js の `__NEXT_DATA__` を抽出して動かす。
- 検索結果配列パス: props.initialState.bff.searchResults.items.* (動的キー).content.items[]

【取れる項目】
- 商品名 (name) / 価格 (actualPrice / highestPrice / cheapest) / 商品URL (url)
- ストア情報 (dataBeacon に cid: store_id, str_rate: ストア評価, str_rct: レビュー数)
- ポイント / 割引率 / カテゴリID / 送料情報 (isShip / shippingCode)

【レート制限】
- 1 秒に 1 req 程度
- robots.txt 上は /search は許可（Disallow されているのは /my/, /review/contribution/ 等）
"""

import os
import re
import json
import time
import sys
import urllib.parse
from typing import Optional

import requests

sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

DEFAULT_HEADERS = {
    'User-Agent': UA,
    'Accept-Language': 'ja,en-US;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__"[^>]*>(\{.+?\})</script>',
    re.DOTALL,
)

LAST_REQUEST_TIME = [0.0]
MIN_INTERVAL_SEC = 1.2


def _polite_sleep():
    elapsed = time.time() - LAST_REQUEST_TIME[0]
    if elapsed < MIN_INTERVAL_SEC:
        time.sleep(MIN_INTERVAL_SEC - elapsed)
    LAST_REQUEST_TIME[0] = time.time()


def _fetch_html(url: str) -> str:
    _polite_sleep()
    for attempt in range(3):
        try:
            r = requests.get(url, headers=DEFAULT_HEADERS, timeout=20)
            if r.status_code == 200:
                return r.text
            if r.status_code in (429, 503):
                time.sleep(3 * (attempt + 1))
                continue
            r.raise_for_status()
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f'yahoo fetch failed for {url}')


def _parse_next_data(html: str) -> Optional[dict]:
    m = NEXT_DATA_RE.search(html)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def _find_search_items(state: dict) -> list[dict]:
    """
    動的キーが入ったパスから商品配列を取り出す。
    props.initialState.bff.searchResults.items.<dynamic_key>[..].content.items[]
    """
    out: list[dict] = []
    try:
        items_root = state['props']['initialState']['bff']['searchResults']['items']
    except (KeyError, TypeError):
        return out
    if not isinstance(items_root, dict):
        return out
    for _, page_node in items_root.items():
        # page_node はリスト or 単一の dict のどちらかありうる
        if isinstance(page_node, list):
            iterator = page_node
        else:
            iterator = [page_node]
        for entry in iterator:
            if not isinstance(entry, dict):
                continue
            content = entry.get('content') or {}
            arr = content.get('items') if isinstance(content, dict) else None
            if isinstance(arr, list):
                out.extend([it for it in arr if isinstance(it, dict)])
    return out


def _parse_data_beacon(beacon: str) -> dict:
    """
    `_cl_module:rsltlst;...;cid:lowtex;str_rate:4.74;str_rct:13579;tname:NIKE...` のような
    `;` 区切り key:value 文字列を辞書に変換。
    """
    out: dict = {}
    if not beacon or not isinstance(beacon, str):
        return out
    for piece in beacon.split(';'):
        piece = piece.strip()
        if ':' not in piece:
            continue
        k, _, v = piece.partition(':')
        out[k.strip()] = v.strip()
    return out


def _normalize_item(raw: dict) -> dict:
    name = raw.get('name', '') or ''
    actual_price = raw.get('actualPrice') or raw.get('price') or 0
    highest_price = raw.get('highestPrice') or 0
    discount_rate = raw.get('discountRate') or 0
    point = raw.get('point') or 0
    item_url = raw.get('url') or ''
    is_ship = bool(raw.get('isShip'))

    beacon = _parse_data_beacon(raw.get('dataBeacon') or '')
    store_id = beacon.get('cid') or ''
    store_rate = float(beacon.get('str_rate') or 0)
    store_review_count = int(beacon.get('str_rct') or 0)
    jan = beacon.get('jan')
    if jan in ('null', '', 'undefined'):
        jan = None

    images = raw.get('images') or []
    image_url = ''
    if images:
        first = images[0] if isinstance(images, list) else None
        if isinstance(first, dict):
            image_url = first.get('url') or first.get('imageUrl') or ''

    return {
        'source': 'yahoo_shopping',
        'name': name,
        'price_jpy': int(actual_price) if actual_price else 0,
        'highest_price_jpy': int(highest_price) if highest_price else 0,
        'discount_rate_pct': discount_rate,
        'point': point,
        'item_url': item_url,
        'image_url': image_url,
        'is_free_shipping': is_ship,
        'store_id': store_id,
        'store_rate': store_rate,
        'store_review_count': store_review_count,
        'jan': jan,
        'category_ids': raw.get('categoryIds') or [],
        'brand': (raw.get('brand') or {}).get('name') if isinstance(raw.get('brand'), dict) else (raw.get('brand') or ''),
    }


# ---- public --------------------------------------------------------------


def search_by_keyword(
    keyword: str,
    *,
    max_items: int = 30,
    new_only: bool = True,
) -> list[dict]:
    """
    キーワード検索結果を返す。
    new_only=True で新品のみフィルタ（used=2）。
    """
    base = 'https://shopping.yahoo.co.jp/search'
    params = {'p': keyword}
    if new_only:
        params['used'] = '2'
    url = base + '?' + urllib.parse.urlencode(params)

    html = _fetch_html(url)
    state = _parse_next_data(html)
    if not state:
        return []
    raw_items = _find_search_items(state)
    return [_normalize_item(it) for it in raw_items[:max_items]]


def search_by_jan(jan: str, max_items: int = 10) -> list[dict]:
    return search_by_keyword(jan, max_items=max_items, new_only=True)


def cheapest_match(items: list[dict]) -> Optional[dict]:
    valid = [it for it in items if it.get('price_jpy', 0) > 0]
    if not valid:
        return None
    return min(valid, key=lambda it: it['price_jpy'])


if __name__ == '__main__':
    print('▼ Yahoo!ショッピング Nike Dunk Low')
    items = search_by_keyword('Nike Dunk Low', max_items=10)
    print(f'  取得 {len(items)} 件')
    for it in items[:5]:
        flag = '★無料' if it['is_free_shipping'] else ''
        print(f"  ¥{it['price_jpy']:>7,} {flag} | {it['name'][:55]} | {it['store_id']}({it['store_rate']})")
    print('\n▼ 最安')
    cheap = cheapest_match(items)
    if cheap:
        print(f"  ¥{cheap['price_jpy']:,} | {cheap['name'][:60]}")
        print(f"  {cheap['item_url'][:100]}")
