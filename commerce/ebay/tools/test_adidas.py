# -*- coding: utf-8 -*-
"""Adidas在庫APIテストスクリプト"""
import requests
import json

product_id = 'IH9052'
url = f'https://www.adidas.jp/api/products/{product_id}/availability'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ja-JP,ja;q=0.9',
    'Referer': 'https://www.adidas.jp/',
    'Origin': 'https://www.adidas.jp',
}

r = requests.get(url, headers=headers, timeout=15)
print(f'ステータス: {r.status_code}')
print(f'レスポンス長: {len(r.text)} 文字')
print(f'エンコーディング: {r.encoding}')
print(f'先頭200文字: {r.text[:200]}')

if r.text.strip():
    data = json.loads(r.text)
    print(f'\n商品ID: {data.get("id")}')
    variations = data.get('variation_list', [])
    print(f'バリエーション数: {len(variations)}')
    print('\nサイズ別在庫:')
    in_stock = 0
    for v in variations:
        status_str = v.get('availability_status', '')
        is_in = status_str == 'IN_STOCK'
        if is_in:
            in_stock += 1
        mark = '○' if is_in else '×'
        print(f'  {v.get("size",""):8s} | {mark} {status_str:15s} | {v.get("availability",0)}個')
    print(f'\n在庫あり: {in_stock}件 / 全{len(variations)}件')
