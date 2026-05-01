"""
為替レート取得モジュール（USD/JPY）

【方針】
- 無料 API（Frankfurter / open.er-api.com）を最優先
- ローカルキャッシュ（30 分）で API 過剰呼び出しを避ける
- ネット失敗時は cache の最終値で継続
- requests を使う（urllib は User-Agent ブロックされる API がある）

【参考】
- Frankfurter: https://www.frankfurter.app/docs/    （ECB 公開データ・無料・無認証）
- open.er-api: https://www.exchangerate-api.com/docs/free （無料・無認証）
"""

import os
import json
import time
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(SCRIPT_DIR, 'cache', 'fx_rate.json')
CACHE_TTL_SEC = 30 * 60  # 30 分


def _read_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {}


def _write_cache(data: dict) -> None:
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def _fetch_from_frankfurter() -> float | None:
    try:
        r = requests.get(
            'https://api.frankfurter.app/latest',
            params={'from': 'USD', 'to': 'JPY'},
            timeout=10,
        )
        r.raise_for_status()
        rate = r.json().get('rates', {}).get('JPY')
        return float(rate) if rate else None
    except Exception:
        return None


def _fetch_from_open_er_api() -> float | None:
    try:
        r = requests.get('https://open.er-api.com/v6/latest/USD', timeout=10)
        r.raise_for_status()
        rate = r.json().get('rates', {}).get('JPY')
        return float(rate) if rate else None
    except Exception:
        return None


def get_usdjpy(force_refresh: bool = False) -> float:
    """
    USD→JPY のレートを返す（円/USD・例: 159.74）。
    キャッシュ→Frankfurter→open.er-api.com の順で試す。
    """
    cache = _read_cache()
    if not force_refresh and cache.get('rate') and (time.time() - cache.get('fetched_at', 0)) < CACHE_TTL_SEC:
        return float(cache['rate'])

    for fetcher in (_fetch_from_frankfurter, _fetch_from_open_er_api):
        rate = fetcher()
        if rate and 50.0 < rate < 500.0:  # サニティチェック
            _write_cache({
                'rate': rate,
                'fetched_at': time.time(),
                'fetched_at_human': time.strftime('%Y-%m-%d %H:%M:%S'),
                'source': fetcher.__name__,
            })
            return rate

    if cache.get('rate'):
        return float(cache['rate'])

    raise RuntimeError(
        '為替レートを取得できませんでした。Frankfurter / open.er-api.com 両方失敗かつキャッシュなし。'
    )


if __name__ == '__main__':
    rate = get_usdjpy(force_refresh=True)
    print(f'USD/JPY = {rate}')
