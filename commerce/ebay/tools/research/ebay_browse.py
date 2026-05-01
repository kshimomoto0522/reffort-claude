"""
eBay Browse API クライアント

【目的】
無在庫リサーチ用に「eBay USで売れている / 売れそうな商品」を発見する。

Browse API は eBay のパブリック商品検索 API。
- /item_summary/search   ... キーワード/カテゴリ検索
- /item/{itemId}          ... 商品詳細（重量・GTIN・MPN・出品者）

【売れている度の推定】
Browse API は「過去販売実績」を直接返さない（それは Marketplace Insights API・要申請）。
代わりに本ツールでは複合シグナルで売れ筋らしさを推定する：
  1. 同一キーワードでの出品者数の多さ（多 = 安定需要）
  2. 商品の listingMarketplaceId、location、shipsTo
  3. 価格帯の中央値（外れ値除外）
  4. fieldgroups=EXTENDED の watchCount（一部商品で取れる）

【Marketplace】
EBAY_US（Reffort のメイン販路）。

【参考】
- https://developer.ebay.com/api-docs/buy/browse/resources/item_summary/methods/search
- https://developer.ebay.com/api-docs/buy/static/api-browse.html
"""

import os
import sys
import json
import time
from typing import Optional

import requests

sys.stdout.reconfigure(encoding='utf-8')

from ebay_app_token import get_app_token

API_BASE = 'https://api.ebay.com/buy/browse/v1'
MARKETPLACE = 'EBAY_US'
DEFAULT_LIMIT = 50


class EbayBrowse:
    """eBay Browse API クライアント。"""

    def __init__(self, marketplace: str = MARKETPLACE):
        self.marketplace = marketplace

    def _headers(self) -> dict:
        return {
            'Authorization': f'Bearer {get_app_token()}',
            'X-EBAY-C-MARKETPLACE-ID': self.marketplace,
            # 米国買い手コンテキスト（米国に発送可能な商品優先）
            'X-EBAY-C-ENDUSERCTX': 'contextualLocation=country=US,zip=10001',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
        }

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        url = API_BASE + path
        r = requests.get(url, params=params, headers=self._headers(), timeout=30)
        if r.status_code != 200:
            raise RuntimeError(
                f'eBay API HTTPError {r.status_code} on {path}\n'
                f'params={params}\n'
                f'body={r.text[:1000]}'
            )
        return r.json()

    def search(
        self,
        q: Optional[str] = None,
        category_ids: Optional[str] = None,
        filters: Optional[list[str]] = None,
        sort: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
        fieldgroups: str = 'EXTENDED,MATCHING_ITEMS',
    ) -> dict:
        """
        item_summary/search を叩く。
        filters は filter クエリの文字列リスト（カンマ連結される）。
        例: ['buyingOptions:{FIXED_PRICE}', 'conditionIds:{1000}', 'price:[10..500]', 'priceCurrency:USD']
        """
        params: dict = {'limit': str(limit), 'offset': str(offset)}
        if q:
            params['q'] = q
        if category_ids:
            params['category_ids'] = category_ids
        if filters:
            params['filter'] = ','.join(filters)
        if sort:
            params['sort'] = sort
        if fieldgroups:
            params['fieldgroups'] = fieldgroups
        return self._get('/item_summary/search', params)

    def get_item(self, item_id: str, fieldgroups: str = 'PRODUCT,COMPACT') -> dict:
        """商品詳細を取得（重量・GTIN・MPN・seller 詳細など）。"""
        path = f'/item/{requests.utils.quote(item_id, safe="")}'
        return self._get(path, {'fieldgroups': fieldgroups})


# ---- 高レベル便利関数 -----------------------------------------------------


def search_us_marketplace(
    keyword: str,
    *,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    condition_new: bool = True,
    fixed_price_only: bool = True,
    sort: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    seller_country: Optional[str] = None,
) -> list[dict]:
    """
    キーワードで EBAY_US を検索し、ItemSummary のリストを返す。
    seller_country='JP' で日本セラーのみ抽出（=ライバルセラー観測）。
    seller_country='US' で米国セラーのみ。
    """
    filters = []
    if condition_new:
        filters.append('conditionIds:{1000|1500}')  # New + New other
    if fixed_price_only:
        filters.append('buyingOptions:{FIXED_PRICE}')
    if min_price is not None or max_price is not None:
        lo = '' if min_price is None else f'{min_price:.0f}'
        hi = '' if max_price is None else f'{max_price:.0f}'
        filters.append(f'price:[{lo}..{hi}]')
        filters.append('priceCurrency:USD')
    if seller_country:
        # itemLocationCountry はISO 2文字コード（JP, US 等）
        filters.append(f'itemLocationCountry:{seller_country}')

    client = EbayBrowse()
    res = client.search(q=keyword, filters=filters, sort=sort, limit=limit, offset=offset)
    return res.get('itemSummaries', []) or []


def market_overview(
    keyword: str,
    *,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sample_size: int = 100,
) -> dict:
    """
    キーワードの「米国マーケット全体」のスナップショットを返す。
    Browse API 1 リクエスト（最大 200 件）で「競合の厚み・価格分布・ユニークセラー数」を計算。

    返り値: {
      'total_listed': int,        # eBay 全体の出品総数（推定）
      'sampled': int,             # 取得サンプル数
      'unique_sellers': int,      # 出品セラーのユニーク数
      'jp_seller_count': int,     # 日本セラー数
      'us_seller_count': int,     # 米国セラー数
      'price_min_usd': float,
      'price_median_usd': float,
      'price_max_usd': float,
      'price_p25_usd': float,
      'price_p75_usd': float,
      'top_sellers': [(username, count), ...],   # 出品多い順 上位 5 名
    }
    """
    filters = ['conditionIds:{1000|1500}', 'buyingOptions:{FIXED_PRICE}']
    if min_price is not None or max_price is not None:
        lo = '' if min_price is None else f'{min_price:.0f}'
        hi = '' if max_price is None else f'{max_price:.0f}'
        filters.append(f'price:[{lo}..{hi}]')
        filters.append('priceCurrency:USD')

    client = EbayBrowse()
    res = client.search(q=keyword, filters=filters, limit=min(sample_size, 200))
    items = res.get('itemSummaries', []) or []
    total_listed = int(res.get('total', 0) or 0)

    if not items:
        return {
            'total_listed': total_listed,
            'sampled': 0,
            'unique_sellers': 0,
            'jp_seller_count': 0,
            'us_seller_count': 0,
            'price_min_usd': 0.0,
            'price_median_usd': 0.0,
            'price_max_usd': 0.0,
            'price_p25_usd': 0.0,
            'price_p75_usd': 0.0,
            'top_sellers': [],
        }

    prices = []
    seller_counts: dict[str, int] = {}
    jp_count = 0
    us_count = 0
    for it in items:
        price = (it.get('price') or {}).get('value')
        try:
            price_f = float(price) if price else 0.0
        except (TypeError, ValueError):
            price_f = 0.0
        if price_f > 0:
            prices.append(price_f)
        seller = (it.get('seller') or {}).get('username') or ''
        if seller:
            seller_counts[seller] = seller_counts.get(seller, 0) + 1
        country = (it.get('itemLocation') or {}).get('country') or ''
        if country == 'JP':
            jp_count += 1
        elif country == 'US':
            us_count += 1

    prices.sort()
    n = len(prices)

    def percentile(p: float) -> float:
        if not prices:
            return 0.0
        idx = max(0, min(n - 1, int(p * (n - 1))))
        return prices[idx]

    top_sellers = sorted(seller_counts.items(), key=lambda kv: -kv[1])[:5]

    return {
        'total_listed': total_listed,
        'sampled': n,
        'unique_sellers': len(seller_counts),
        'jp_seller_count': jp_count,
        'us_seller_count': us_count,
        'price_min_usd': prices[0] if prices else 0.0,
        'price_median_usd': percentile(0.5),
        'price_max_usd': prices[-1] if prices else 0.0,
        'price_p25_usd': percentile(0.25),
        'price_p75_usd': percentile(0.75),
        'top_sellers': top_sellers,
    }


if __name__ == '__main__':
    # 動作確認
    print('▼ Nike Dunk Low（米国マーケット）検索')
    items = search_us_marketplace(
        'Nike Dunk Low',
        min_price=80,
        max_price=300,
        condition_new=True,
        fixed_price_only=True,
        limit=5,
    )
    print(f'取得件数: {len(items)}')
    for it in items:
        title = it.get('title', '')
        price = it.get('price', {}).get('value', '')
        currency = it.get('price', {}).get('currency', '')
        seller = it.get('seller', {}).get('username', '')
        feedback = it.get('seller', {}).get('feedbackPercentage', '')
        loc = it.get('itemLocation', {}).get('country', '')
        url = it.get('itemWebUrl', '')[:80]
        print(f'  {currency} {price} | [{loc}] {title[:55]} | {seller}({feedback}%)')

    print('\n▼ 同じ検索で日本セラー（itemLocationCountry=JP）')
    items_jp = search_us_marketplace(
        'Nike Dunk Low',
        min_price=80,
        max_price=300,
        condition_new=True,
        fixed_price_only=True,
        seller_country='JP',
        limit=5,
    )
    print(f'取得件数: {len(items_jp)}')
    for it in items_jp:
        title = it.get('title', '')
        price = it.get('price', {}).get('value', '')
        seller = it.get('seller', {}).get('username', '')
        loc = it.get('itemLocation', {}).get('country', '')
        print(f'  USD {price} | [{loc}] {title[:55]} | {seller}')
