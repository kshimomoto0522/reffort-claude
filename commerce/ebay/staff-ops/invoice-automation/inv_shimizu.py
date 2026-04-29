"""清水請求書ロジック

仕入管理表「報酬管理」シートのB列で当月の「X月」ラベルを探し、
その上に位置する「小計（円）」行のAH列値を当月単価として反映。
"""

from inv_common import (
    get_gc, col_letter, block_start_col, month_end_str,
    ensure_columns, copy_block, copy_column_widths, fmt_money,
)


def _find_subtotal_row_for_month(ws_shiire, month: int) -> tuple:
    """報酬管理シートで当月の「小計（円）」行番号を返す。
    返り値: (subtotal_row, debug_info)
    """
    b_col = ws_shiire.col_values(2)  # B列
    target = f'{month}月'
    label_row = None
    for i, v in enumerate(b_col):
        if isinstance(v, str) and v.strip() == target:
            label_row = i + 1
            break
    if label_row is None:
        raise ValueError(
            f'仕入管理表/報酬管理シートのB列に「{target}」が見つかりません。'
            f'当月の月名行（例：「3月」）が存在することを確認してください。'
        )

    # 月名行（X月のヘッダー）から下方向に「小計（円）」を探す
    # 構造：B{label_row}='3月' → B{label_row+1}=曜日行 → B{label_row+2..}=各種データ → B{?}='小計（円）'
    subtotal_row = None
    for i in range(label_row, min(label_row + 15, len(b_col))):
        v = b_col[i] if i < len(b_col) else ''
        if isinstance(v, str) and '小計' in v:
            subtotal_row = i + 1
            break
    if subtotal_row is None:
        raise ValueError(
            f'「{target}」(B{label_row})の下15行以内に「小計（円）」行が見つかりません。'
        )

    return subtotal_row, {
        'month_label_row': label_row,
        'subtotal_row': subtotal_row,
    }


def plan_shimizu(year: int, month: int, config: dict) -> dict:
    """書込プラン生成（仕入管理表からの単価取得を含む）"""
    gc = get_gc()
    ss_shi = gc.open_by_key(config['spreadsheets']['shiire'])
    ws_shi = ss_shi.worksheet(config['shimizu']['shiire_sheet'])

    subtotal_row, debug = _find_subtotal_row_for_month(ws_shi, month)
    amount_col = config['shimizu']['shiire_amount_col']
    cell_addr = f'{amount_col}{subtotal_row}'

    raw = ws_shi.acell(cell_addr, value_render_option='UNFORMATTED_VALUE').value
    if raw in (None, ''):
        raise ValueError(f'仕入管理表 {cell_addr} が空です')
    try:
        unit_price = int(float(raw))
    except (TypeError, ValueError):
        # 文字列ならカンマ除去して再試行
        s = str(raw).replace(',', '').replace('¥', '').replace('円', '').strip()
        unit_price = int(float(s))

    layout = config['invoice_layout']
    shimizu = config['shimizu']

    src_month = month - 1
    src_col = block_start_col(src_month, layout['block_width'])
    dst_col = block_start_col(month, layout['block_width'])

    subject_col = dst_col + layout['offsets']['subject_col']
    date_col = dst_col + layout['offsets']['date_col']
    unit_col = dst_col + layout['offsets']['unit_col']

    return {
        'staff': '清水',
        'sheet': config['invoice_sheets']['shimizu'],
        'src_block': f'{col_letter(src_col)}:{col_letter(src_col + layout["block_width"] - 1)}',
        'dst_block': f'{col_letter(dst_col)}:{col_letter(dst_col + layout["block_width"] - 1)}',
        'src_col': src_col,
        'dst_col': dst_col,
        'shiire_subtotal_cell': cell_addr,
        'shiire_debug': debug,
        'unit_price': unit_price,
        'cells': {
            f'{col_letter(subject_col)}{layout["rows"]["subject"]}': shimizu['subject_template'].format(month=month),
            f'{col_letter(date_col)}{layout["rows"]["date"]}': month_end_str(year, month),
            f'{col_letter(unit_col)}{layout["rows"]["item"]}': unit_price,
        },
        'needed_col_count': dst_col + layout['block_width'] - 1,
    }


def print_plan(plan: dict):
    print(f"\n--- {plan['staff']}請求書 ---")
    print(f"  シート: {plan['sheet']}")
    print(f"  コピー: {plan['src_block']} → {plan['dst_block']}")
    print(f"  必要列数: {plan['needed_col_count']}")
    print(f"  仕入管理表: {plan['shiire_subtotal_cell']} = {fmt_money(plan['unit_price'])}円 "
          f"(月名行 B{plan['shiire_debug']['month_label_row']})")
    print(f"  書込:")
    for cell, val in plan['cells'].items():
        if isinstance(val, int):
            print(f"    {cell} = {fmt_money(val)}")
        else:
            print(f"    {cell} = {val!r}")


def apply_shimizu(year: int, month: int, config: dict) -> dict:
    plan = plan_shimizu(year, month, config)
    layout = config['invoice_layout']

    gc = get_gc()
    ss = gc.open_by_key(config['spreadsheets']['keishi'])
    ws = ss.worksheet(plan['sheet'])

    ensure_columns(ws, plan['needed_col_count'])
    copy_block(ss, ws.id,
               src_col_start=plan['src_col'],
               dst_col_start=plan['dst_col'],
               width=layout['block_width'],
               rows=layout['copy_rows'])
    copy_column_widths(ss, ws.id,
                       src_col_start_idx=plan['src_col'] - 1,
                       dst_col_start_idx=plan['dst_col'] - 1,
                       count=layout['block_width'])

    updates = [{'range': cell, 'values': [[val]]} for cell, val in plan['cells'].items()]
    ws.batch_update(updates, value_input_option='USER_ENTERED')

    return {'plan': plan, 'status': 'applied'}
