"""
駿河屋（suruga-ya.jp）検索結果取得

【方針】
- リサーチ Agent C（2026-05-01）の検証で requests + UA で 200 OK 取得確認
- Cloudflare 配下だが GET は通過（`__cf_bm` Cookie 発行のみ）
- robots.txt は `Allow: /` で検索系明示 OK（AI 訓練のみ NG）
- フィギュア・ゲーム・トレカ・本・コレクター系で強い

【取れる情報】
- 商品 ID・タイトル・新品価格・中古価格・定価・画像 URL・在庫
- 詳細ページから JAN コード（13 桁）抽出可能 → eBay 突合キー
"""

import os
import re
import sys
import time
import urllib.parse
from typing import Optional

import requests

sys.stdout.reconfigure(encoding='utf-8')

UA = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
)
SESSION = requests.Session()
SESSION.headers.update({'User-Agent': UA, 'Accept-Language': 'ja,en;q=0.9'})

LAST_REQUEST_TIME = [0.0]
MIN_INTERVAL_SEC = 2.0  # Cloudflare 配慮で 2 秒間隔


def _polite_sleep():
    elapsed = time.time() - LAST_REQUEST_TIME[0]
    if elapsed < MIN_INTERVAL_SEC:
        time.sleep(MIN_INTERVAL_SEC - elapsed)
    LAST_REQUEST_TIME[0] = time.time()


def _fetch(url: str) -> Optional[str]:
    _polite_sleep()
    for attempt in range(3):
        try:
            r = SESSION.get(url, allow_redirects=True, timeout=30)
            if r.status_code == 200:
                return r.text
            if r.status_code in (429, 503):
                time.sleep(5 * (attempt + 1))
                continue
            r.raise_for_status()
        except requests.RequestException:
            if attempt == 2:
                return None
            time.sleep(3 * (attempt + 1))
    return None


def _parse_block(block: str) -> Optional[dict]:
    """1 商品ブロック (`item_box` タグの中身) から商品情報を抽出。"""
    pid_m = re.search(r'/product/detail/(\w+)', block)
    if not pid_m:
        return None
    pid = pid_m.group(1)

    title_m = re.search(r'<h3 class="product-name">([^<]+)</h3>', block)
    title = title_m.group(1).strip() if title_m else ''

    img_m = re.search(r'<img[^>]+src="(https://www\.suruga-ya\.jp/database/photo\.php\?[^"]+)"', block)
    image_url = img_m.group(1) if img_m else ''

    teika_m = re.search(r'定価[^\d]{0,5}([\d,]+)', block)
    list_price = int(teika_m.group(1).replace(',', '')) if teika_m else 0

    # 駿河屋実 HTML：
    #   新品 = `icon_mp_brown` + 「マケプレ」 + `<strong>￥1,430</strong>`
    #   中古 = `中古：` + `<strong>￥2,000</strong>`
    new_m = re.search(
        r'icon_mp_brown[\s\S]{0,400}?<strong[^>]*>￥([\d,]+)\s*</strong>',
        block,
    )
    used_m = re.search(
        r'中古[：:][\s\S]{0,400}?<strong[^>]*>￥([\d,]+)\s*</strong>',
        block,
    )
    new_price = int(new_m.group(1).replace(',', '')) if new_m else 0
    used_price = int(used_m.group(1).replace(',', '')) if used_m else 0

    # 「マケプレ」見出しがマケ品（中古業者出品）の場合もあるので、新品は明示テキストで再確認
    is_marketplace_new = (
        bool(new_m) and ('マケプレ' in block[:max(2000, new_m.end())])
    )

    sold_out = '品切' in block[:5000]

    if new_price > 0:
        condition = 'new'  # マケプレは新品扱いが多いが、実態は出品者次第
        price = new_price
    elif used_price > 0:
        condition = 'used'
        price = used_price
    else:
        condition = 'unknown'
        price = 0

    return {
        'source': 'surugaya',
        'item_id': pid,
        'name': title,
        'price_jpy': price,
        'new_price_jpy': new_price,
        'used_price_jpy': used_price,
        'list_price_jpy': list_price,
        'item_url': f'https://www.suruga-ya.jp/product/detail/{pid}',
        'image_url': image_url,
        'condition': condition,
        'is_sold_out': sold_out,
        'shop_name': '駿河屋',
        'is_free_shipping': False,
    }


def search_by_keyword(
    keyword: str,
    *,
    max_items: int = 20,
    new_only: bool = True,
) -> list[dict]:
    """駿河屋を検索して商品リストを返す。"""
    encoded = urllib.parse.quote(keyword)
    url = f'https://www.suruga-ya.jp/search?search_word={encoded}'
    html = _fetch(url)
    if not html:
        return []

    blocks = re.split(r'<div class="item_box', html)[1:]
    out: list[dict] = []
    for b in blocks:
        item = _parse_block(b)
        if not item:
            continue
        if item['price_jpy'] <= 0:
            continue
        if new_only and item['condition'] != 'new':
            continue
        if item['is_sold_out']:
            continue
        out.append(item)
        if len(out) >= max_items:
            break
    return out


def search_by_jan(jan: str, max_items: int = 10) -> list[dict]:
    return search_by_keyword(jan, max_items=max_items, new_only=True)


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
    print('▼ 駿河屋 ポケモンカード Japanese SAR')
    items = search_by_keyword('ポケモンカード SAR', max_items=10, new_only=True)
    print(f'  取得 {len(items)} 件')
    for it in items[:8]:
        print(f"  ¥{it['price_jpy']:>7,} [{it['condition']}] {it['name'][:55]}")
    cheap = cheapest_match(items)
    if cheap:
        print(f'\n  最安: ¥{cheap["price_jpy"]:,} | {cheap["name"][:60]}')
        print(f'  {cheap["item_url"]}')
