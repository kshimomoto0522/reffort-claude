"""
Yahoo!フリマ（旧 PayPayフリマ）検索結果取得

【方針】
- 公式に近い内部 JSON API `https://paypayfleamarket.yahoo.co.jp/api/v1/search` が
  認証ヘッダなし（UA + Referer のみ）で動作
- リサーチ Agent（2026-05-01）の検証で 200 OK・50 件/ページ・149,999 件総数まで確認
- 商品オブジェクトに condition (new/used) と itemStatus (ON_SALE/SOLD) が直接入る

【取れる情報】
- 商品 ID・タイトル・価格（円）・状態（new/used）・出品中ステータス・サムネ・出品者 ID

【規約対策】
- ログイン状態でアクセスしない
- 1 req / 2 秒間隔
- 並列禁止
"""

import os
import sys
import time
import urllib.parse
from typing import Optional

import requests

sys.stdout.reconfigure(encoding='utf-8')

API_URL = 'https://paypayfleamarket.yahoo.co.jp/api/v1/search'

DEFAULT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    ),
    'Referer': 'https://paypayfleamarket.yahoo.co.jp/',
    'Accept': 'application/json',
}

LAST_REQUEST_TIME = [0.0]
MIN_INTERVAL_SEC = 2.0


def _polite_sleep():
    elapsed = time.time() - LAST_REQUEST_TIME[0]
    if elapsed < MIN_INTERVAL_SEC:
        time.sleep(MIN_INTERVAL_SEC - elapsed)
    LAST_REQUEST_TIME[0] = time.time()


def _normalize_item(raw: dict) -> dict:
    """API 応答 1 件 → 統一フォーマットに正規化。"""
    item_id = raw.get('id') or raw.get('itemId') or ''
    name = raw.get('title') or raw.get('name') or ''
    price = raw.get('price') or 0
    condition = raw.get('condition') or 'unknown'  # 'new' / 'used' / 'unknown'
    status = raw.get('itemStatus') or raw.get('status') or ''
    is_sold = (status or '').upper() in ('SOLD', 'ITEM_STATUS_SOLD_OUT')
    thumbnail = raw.get('thumbnailImageUrl') or raw.get('imageUrl') or ''
    seller_id = raw.get('sellerId') or raw.get('seller', {}).get('id') if isinstance(raw.get('seller'), dict) else raw.get('sellerId', '')

    return {
        'source': 'yahoo_furima',
        'name': name,
        'price_jpy': int(price) if price else 0,
        'item_url': f'https://paypayfleamarket.yahoo.co.jp/item/{item_id}' if item_id else '',
        'item_id': item_id,
        'image_url': thumbnail,
        'condition': condition,
        'is_sold_out': is_sold,
        'seller_id': seller_id,
        'shop_name': f'フリマ:{seller_id}' if seller_id else 'Yahoo!フリマ',
        'is_free_shipping': False,  # 詳細ページに行かないと不明
    }


def search_by_keyword(
    keyword: str,
    *,
    max_items: int = 30,
    new_only: bool = True,
    on_sale_only: bool = True,
) -> list[dict]:
    """
    キーワード検索結果を返す（販売中のみ、新品のみがデフォルト）。
    """
    _polite_sleep()
    out: list[dict] = []
    page = 1
    while len(out) < max_items and page <= 5:
        params = {'query': keyword, 'page': page}
        try:
            r = requests.get(API_URL, params=params, headers=DEFAULT_HEADERS, timeout=15)
            r.raise_for_status()
            data = r.json()
        except (requests.RequestException, ValueError):
            break

        items = data.get('items') or []
        if not items:
            break

        for raw in items:
            n = _normalize_item(raw)
            if on_sale_only and n['is_sold_out']:
                continue
            if new_only and n['condition'] != 'new':
                continue
            if n['price_jpy'] <= 0:
                continue
            out.append(n)
            if len(out) >= max_items:
                break

        page += 1
        if page <= 5:
            time.sleep(2.0)
    return out


def search_by_jan(jan: str, max_items: int = 10) -> list[dict]:
    return search_by_keyword(jan, max_items=max_items, new_only=True, on_sale_only=True)


def cheapest_match(items: list[dict], *, exclude_used: bool = True) -> Optional[dict]:
    valid = [
        it for it in items
        if it['price_jpy'] > 0 and not it.get('is_sold_out')
        and (not exclude_used or it.get('condition') != 'used')
    ]
    if not valid:
        return None
    return min(valid, key=lambda it: it['price_jpy'])


if __name__ == '__main__':
    print('▼ Yahoo!フリマ Onitsuka Tiger Mexico 66（新品・販売中）')
    items = search_by_keyword('Onitsuka Tiger Mexico 66', max_items=10, new_only=True)
    print(f'  取得 {len(items)} 件')
    for it in items[:6]:
        print(f"  ¥{it['price_jpy']:>7,} [{it['condition']}] {it['name'][:55]}")
    cheap = cheapest_match(items)
    if cheap:
        print(f'\n  最安: ¥{cheap["price_jpy"]:,} | {cheap["name"][:60]}')
        print(f'  {cheap["item_url"]}')
