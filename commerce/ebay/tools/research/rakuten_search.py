"""
楽天市場 検索結果スクレイパー

【方針】
- 公式 Web Service API（Application ID 必要）は社長の登録待ち。
  Ver.1 は HTML スクレイピングで動かす（robots.txt は /search/ を許可）。
- 検索ページに埋め込まれた `__INITIAL_STATE__` JSON を抽出してパースする
  （HTML 構造変更に対する耐性: タグ依存より高い）。
- 楽天 ID（Application ID）が後で取得できたら API クライアントに差し替える前提。

【取れる項目】
- 商品名 / 価格（円・税込）/ 商品URL / 送料設定 / ショップ名 / レビュー数 / 在庫
- ジャンル ID リスト（カテゴリ判定の補助）

【レート制限】
- 1 秒に 1 req 程度（公式 API ガイド準拠）
- リトライは指数バックオフ
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

INITIAL_STATE_START_RE = re.compile(r'__INITIAL_STATE__\s*=\s*\{')


def _extract_initial_state_json(html: str) -> str | None:
    """
    `__INITIAL_STATE__ = {...};` の JSON を波括弧バランスで正確に取り出す。
    （`</script>` で anchor せず、文字列リテラル内のエスケープも考慮する）
    """
    m = INITIAL_STATE_START_RE.search(html)
    if not m:
        return None
    start = m.end() - 1  # `{` の位置
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(html)):
        c = html[i]
        if in_str:
            if escape:
                escape = False
            elif c == '\\':
                escape = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return html[start:i + 1]
    return None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LAST_REQUEST_TIME = [0.0]
MIN_INTERVAL_SEC = 1.2


def _polite_sleep():
    elapsed = time.time() - LAST_REQUEST_TIME[0]
    if elapsed < MIN_INTERVAL_SEC:
        time.sleep(MIN_INTERVAL_SEC - elapsed)
    LAST_REQUEST_TIME[0] = time.time()


def _fetch_html(url: str) -> str:
    """1.2秒以上の間隔で安全に HTML 取得。"""
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
    raise RuntimeError(f'rakuten fetch failed for {url}')


def _parse_initial_state(html: str) -> Optional[dict]:
    raw = _extract_initial_state_json(html)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _extract_items(state: dict) -> list[dict]:
    """state.data.ichibaSearch.items を素直に取り出す。構造変化時はパスを更新。"""
    try:
        return state['state']['data']['ichibaSearch']['items'] or []
    except (KeyError, TypeError):
        return []


def _normalize_item(raw: dict) -> dict:
    """検索結果1件を統一フォーマットに正規化。"""
    name = raw.get('name', '') or ''
    price_jpy = raw.get('price') or 0  # int 円
    shop = raw.get('shop') or {}
    shop_name = ''
    shop_url = ''
    if isinstance(shop, dict):
        shop_name = shop.get('name') or shop.get('shopName') or ''
        shop_url = shop.get('url') or ''
    review_count = raw.get('reviewCount') or 0
    review_average = raw.get('reviewAverage') or 0.0
    is_sold_out = bool(raw.get('isSoldOut'))

    # 商品 URL: redirect_rpp が来るので、productUrl / originalItemUrl があればそちら優先
    item_url = (
        raw.get('originalItemUrl')
        or raw.get('productUrl')
        or raw.get('itemUrl')
        or raw.get('url')
        or ''
    )

    # 送料設定: shipping = {'cost': ..., 'isPostageInclusive': bool, 'description': ...}
    shipping = raw.get('shipping') or {}
    is_free_shipping = bool(shipping.get('isPostageInclusive')) or shipping.get('cost') == 0

    images = raw.get('images') or raw.get('thumbnailImages') or raw.get('mediumImageUrls') or []
    image_url = ''
    if images:
        first = images[0]
        if isinstance(first, dict):
            image_url = first.get('imageUrl') or first.get('url') or ''
        elif isinstance(first, str):
            image_url = first

    # 新品/中古ステータス推定（タイトルベース・楽天は明示フィールドなし）
    full_text = f'{name} {raw.get("subtitle") or ""}'
    condition = _infer_condition(full_text)

    return {
        'source': 'rakuten',
        'name': name,
        'price_jpy': int(price_jpy),
        'shop_name': shop_name,
        'shop_url': shop_url,
        'item_url': item_url,
        'item_code': raw.get('code') or '',
        'is_free_shipping': is_free_shipping,
        'is_sold_out': is_sold_out,
        'condition': condition,  # 'new' / 'used' / 'unknown'
        'review_count': review_count,
        'review_average': review_average,
        'image_url': image_url,
        'genre_ids': raw.get('genreIdList') or [],
        'brand': raw.get('brand') or '',
        'subtitle': raw.get('subtitle') or '',
        'has_price_range': bool(raw.get('hasPriceRange')),
    }


# 中古を示す日本語マーカー（タイトル先頭/中身どちらでも反応）
USED_MARKERS = [
    '【中古】', '[中古]', '(中古)', '中古品', '中古美品',
    'USED', 'used', 'Used',
    'ジャンク', '訳あり', '訳アリ',
    '展示品', '展示処分', 'B級品',
    '未使用品',  # 未使用と書かれていても「中古扱いの未使用品」のことが多い
]

# 新品を示す日本語マーカー（あれば信頼度上がる）
NEW_MARKERS = [
    '【新品】', '[新品]', '(新品)', '新品未開封', '新品未使用',
    '正規品', '日本正規品', '国内正規品',
    'ブランド新品', 'NEW', '新品 ', '新品・',
]


def _infer_condition(text: str) -> str:
    """タイトル文字列から新品/中古/不明を推定。"""
    if not text:
        return 'unknown'
    for m in USED_MARKERS:
        if m in text:
            return 'used'
    for m in NEW_MARKERS:
        if m in text:
            return 'new'
    return 'unknown'


# ---- public --------------------------------------------------------------


def search_by_keyword(
    keyword: str,
    *,
    max_items: int = 30,
    sort: str = 'standard',
    in_stock_only: bool = True,
    new_only: bool = True,
) -> list[dict]:
    """
    キーワード検索結果をカード一覧として返す。
    sort: standard / +affiliateRate / -updateTimestamp / +itemPrice / -itemPrice / -reviewCount
    new_only=True で「中古」と判定された商品を除外する。
    """
    # 楽天は %20 ではなく + 区切りを期待する。quote_plus を使う。
    base = f'https://search.rakuten.co.jp/search/mall/{urllib.parse.quote_plus(keyword)}/'
    params = []
    if sort and sort != 'standard':
        params.append(f's={urllib.parse.quote(sort)}')
    if in_stock_only:
        params.append('f=2')  # 在庫あり
    if params:
        base += '?' + '&'.join(params)

    html = _fetch_html(base)
    state = _parse_initial_state(html)
    if not state:
        return []
    raw_items = _extract_items(state)
    items = [_normalize_item(it) for it in raw_items[:max_items]]
    if new_only:
        items = [it for it in items if it.get('condition') != 'used']
    return items


def search_by_jan(jan: str, max_items: int = 10) -> list[dict]:
    """JAN コードで楽天市場を検索（キーワード扱い）。"""
    return search_by_keyword(jan, max_items=max_items, in_stock_only=True)


def cheapest_match(items: list[dict], *, exclude_used: bool = True) -> Optional[dict]:
    """価格範囲ありの商品（hasPriceRange）と売り切れと中古を除外して最安値を返す。"""
    valid = [
        it for it in items
        if it['price_jpy'] > 0 and not it['has_price_range'] and not it.get('is_sold_out')
        and (not exclude_used or it.get('condition') != 'used')
    ]
    if not valid:
        return None
    return min(valid, key=lambda it: it['price_jpy'])


if __name__ == '__main__':
    print('▼ Nike Dunk Low キーワード検索 (in_stock_only=False で確認)')
    # デバッグ: 直接 HTML を取って構造確認
    base_url = f'https://search.rakuten.co.jp/search/mall/{urllib.parse.quote_plus("Nike Dunk Low")}/'
    print(f'  url: {base_url}')
    html = _fetch_html(base_url)
    print(f'  html len: {len(html)}')
    state = _parse_initial_state(html)
    print(f'  state parsed: {state is not None}')
    if state:
        raw_items = _extract_items(state)
        print(f'  raw items: {len(raw_items)}')
        if raw_items:
            print(f'  first item keys: {list(raw_items[0].keys())[:15]}')

    items = search_by_keyword('Nike Dunk Low', max_items=10, in_stock_only=False)
    print(f'  取得 {len(items)} 件')
    for it in items[:5]:
        print(f"  ¥{it['price_jpy']:>7,} | {it['name'][:55]} | {it['shop_name']}")

    print('\n▼ 最安値')
    cheapest = cheapest_match(items)
    if cheapest:
        print(f"  ¥{cheapest['price_jpy']:,} | {cheapest['name'][:60]}")
        print(f"  {cheapest['item_url'][:100]}")
