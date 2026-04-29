"""共通ユーティリティ（認証・列計算・ブロックコピー・ロガー）"""

import os
import sys
import json
import calendar
from datetime import date, datetime
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

# 認証情報パス（既存週次レポートと同じJSONを流用）
_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parent.parent  # commerce/ebay/
CREDS_PATH = _PROJECT_ROOT / 'analytics' / 'reffort-sheets-fcbca5a4bbc2.json'

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

_gc = None


def get_gc():
    """gspreadクライアントをシングルトンで取得"""
    global _gc
    if _gc is None:
        if not CREDS_PATH.exists():
            raise FileNotFoundError(f'認証JSONが見つかりません: {CREDS_PATH}')
        creds = Credentials.from_service_account_file(str(CREDS_PATH), scopes=SCOPES)
        _gc = gspread.authorize(creds)
    return _gc


def col_letter(col_num: int) -> str:
    """列番号→英字（1=A, 27=AA, 28=AB ...）"""
    if col_num < 1:
        raise ValueError(f'列番号は1以上: {col_num}')
    s = ''
    n = col_num
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def block_start_col(month: int, width: int = 14) -> int:
    """月→ブロック開始列番号（1月=1=A, 2月=15=O, 3月=29=AC）"""
    if not (1 <= month <= 12):
        raise ValueError(f'月は1-12: {month}')
    return 1 + (month - 1) * width


def month_end_str(year: int, month: int) -> str:
    """月末日付を 'YYYY/M/D' 形式で返す（先頭ゼロなし）"""
    last_day = calendar.monthrange(year, month)[1]
    return f'{year}/{month}/{last_day}'


def previous_month(year: int, month: int) -> tuple:
    """前月を返す"""
    if month == 1:
        return year - 1, 12
    return year, month - 1


def parse_yyyymm(s: str) -> tuple:
    """'202603' → (2026, 3)"""
    s = str(s).strip()
    if len(s) != 6 or not s.isdigit():
        raise ValueError(f'YYYYMM形式が不正: {s!r}')
    return int(s[:4]), int(s[4:6])


def ensure_columns(ws, needed_col: int):
    """ワークシートの列数が足りない場合に拡張"""
    if ws.col_count < needed_col:
        add = needed_col - ws.col_count
        ws.add_cols(add)
        return add
    return 0


def get_column_pixel_sizes(ss, sheet_id: int, col_start_idx: int, count: int) -> list:
    """指定シートの列範囲ごとのpixelSize（列幅）を取得。col_start_idxは0-indexed。"""
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{ss.id}'
    params = {
        'fields': 'sheets(properties(sheetId),data(columnMetadata(pixelSize)))',
    }
    resp = ss.client.session.get(url, params=params)
    resp.raise_for_status()
    payload = resp.json()
    for s in payload.get('sheets', []):
        if s['properties']['sheetId'] == sheet_id:
            col_meta = s.get('data', [{}])[0].get('columnMetadata', [])
            return [
                col_meta[i].get('pixelSize') if i < len(col_meta) else None
                for i in range(col_start_idx, col_start_idx + count)
            ]
    return [None] * count


def copy_column_widths(ss, sheet_id: int, src_col_start_idx: int,
                       dst_col_start_idx: int, count: int):
    """ソース列幅 → destination列に適用。col_start_idxは0-indexed。"""
    src_widths = get_column_pixel_sizes(ss, sheet_id, src_col_start_idx, count)
    requests = []
    for offset, pixel_size in enumerate(src_widths):
        if pixel_size is None:
            continue
        dst_idx = dst_col_start_idx + offset
        requests.append({
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': dst_idx,
                    'endIndex': dst_idx + 1,
                },
                'properties': {'pixelSize': pixel_size},
                'fields': 'pixelSize',
            }
        })
    if requests:
        ss.batch_update({'requests': requests})


def copy_format(ss, sheet_id: int,
                src_row_start_idx: int, src_row_end_idx: int,
                src_col_start_idx: int, src_col_end_idx: int,
                dst_row_start_idx: int, dst_row_end_idx: int,
                dst_col_start_idx: int, dst_col_end_idx: int):
    """書式のみコピー（PASTE_FORMAT）。すべて0-indexed・end_idxは exclusive。
    sourceがdestinationより小さい場合、destinationを満たすまでパターンが繰り返される。
    """
    body = {
        'requests': [{
            'copyPaste': {
                'source': {
                    'sheetId': sheet_id,
                    'startRowIndex': src_row_start_idx, 'endRowIndex': src_row_end_idx,
                    'startColumnIndex': src_col_start_idx, 'endColumnIndex': src_col_end_idx,
                },
                'destination': {
                    'sheetId': sheet_id,
                    'startRowIndex': dst_row_start_idx, 'endRowIndex': dst_row_end_idx,
                    'startColumnIndex': dst_col_start_idx, 'endColumnIndex': dst_col_end_idx,
                },
                'pasteType': 'PASTE_FORMAT',
                'pasteOrientation': 'NORMAL',
            }
        }]
    }
    ss.batch_update(body)


def copy_block(ss, sheet_id: int, src_col_start: int, dst_col_start: int,
               width: int = 14, rows: int = 32):
    """指定ブロックを別範囲にバッチコピー（書式・数式・値・結合すべて含む）

    src_col_start, dst_col_start は 1-indexed の列番号
    rows は 1-indexed の行数（0行目から rows-1 行目まで）
    """
    body = {
        'requests': [{
            'copyPaste': {
                'source': {
                    'sheetId': sheet_id,
                    'startRowIndex': 0,
                    'endRowIndex': rows,
                    'startColumnIndex': src_col_start - 1,
                    'endColumnIndex': src_col_start - 1 + width,
                },
                'destination': {
                    'sheetId': sheet_id,
                    'startRowIndex': 0,
                    'endRowIndex': rows,
                    'startColumnIndex': dst_col_start - 1,
                    'endColumnIndex': dst_col_start - 1 + width,
                },
                'pasteType': 'PASTE_NORMAL',
                'pasteOrientation': 'NORMAL',
            }
        }]
    }
    ss.batch_update(body)


def open_invoice_log(log_dir: Path, prefix: str = 'invoice') -> Path:
    """ログファイルパスを返す（書込まれた内容のJSON記録用）"""
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    return log_dir / f'{prefix}_{ts}.json'


def write_log(log_path: Path, payload: dict):
    """ログJSON書出し"""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open('w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)


def floor_to(value, unit: int) -> int:
    """指定単位で切捨て（例: floor_to(36559479, 50000) = 36550000）"""
    return (int(value) // unit) * unit


def fmt_money(n) -> str:
    """カンマ区切り表示"""
    try:
        return f'{int(n):,}'
    except (TypeError, ValueError):
        return str(n)


# stdout がUnicode対応してない時のための調整
def setup_stdout():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


setup_stdout()
