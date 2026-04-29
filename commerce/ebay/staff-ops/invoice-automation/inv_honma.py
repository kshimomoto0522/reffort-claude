"""本間請求書ロジック

毎月10,000円固定（1月特例の11,000円のような場合は社長が手動で上書き）。
前月ブロックを新月ブロックにコピーし、件名月・日付・単価のみ書き換える。
"""

from inv_common import (
    get_gc, col_letter, block_start_col, month_end_str,
    ensure_columns, copy_block, copy_column_widths, fmt_money,
)


def plan_honma(year: int, month: int, config: dict) -> dict:
    """書込プランを生成（書込はしない）"""
    layout = config['invoice_layout']
    honma = config['honma']

    src_month = month - 1
    if src_month < 1:
        raise ValueError(f'1月の請求書は前月（前年12月）が必要なため、現状未対応')
    src_col = block_start_col(src_month, layout['block_width'])
    dst_col = block_start_col(month, layout['block_width'])

    subject_col = dst_col + layout['offsets']['subject_col']
    date_col = dst_col + layout['offsets']['date_col']
    unit_col = dst_col + layout['offsets']['unit_col']

    return {
        'staff': '本間',
        'sheet': config['invoice_sheets']['honma'],
        'src_block': f'{col_letter(src_col)}:{col_letter(src_col + layout["block_width"] - 1)}',
        'dst_block': f'{col_letter(dst_col)}:{col_letter(dst_col + layout["block_width"] - 1)}',
        'src_col': src_col,
        'dst_col': dst_col,
        'cells': {
            f'{col_letter(subject_col)}{layout["rows"]["subject"]}': honma['subject_template'].format(month=month),
            f'{col_letter(date_col)}{layout["rows"]["date"]}': month_end_str(year, month),
            f'{col_letter(unit_col)}{layout["rows"]["item"]}': honma['unit_price'],
        },
        'needed_col_count': dst_col + layout['block_width'] - 1,
    }


def print_plan(plan: dict):
    print(f"\n--- {plan['staff']}請求書 ---")
    print(f"  シート: {plan['sheet']}")
    print(f"  コピー: {plan['src_block']} → {plan['dst_block']}")
    print(f"  必要列数: {plan['needed_col_count']}")
    print(f"  書込:")
    for cell, val in plan['cells'].items():
        if isinstance(val, int):
            print(f"    {cell} = {fmt_money(val)}")
        else:
            print(f"    {cell} = {val!r}")


def apply_honma(year: int, month: int, config: dict) -> dict:
    """実書込"""
    plan = plan_honma(year, month, config)
    layout = config['invoice_layout']

    gc = get_gc()
    ss = gc.open_by_key(config['spreadsheets']['keishi'])
    ws = ss.worksheet(plan['sheet'])

    # 1. 列拡張
    ensure_columns(ws, plan['needed_col_count'])

    # 2. ブロックコピー（書式・数式・値・結合）
    copy_block(ss, ws.id,
               src_col_start=plan['src_col'],
               dst_col_start=plan['dst_col'],
               width=layout['block_width'],
               rows=layout['copy_rows'])

    # 3. 列幅コピー（copyPasteは列幅をコピーしないので別途）
    copy_column_widths(ss, ws.id,
                       src_col_start_idx=plan['src_col'] - 1,
                       dst_col_start_idx=plan['dst_col'] - 1,
                       count=layout['block_width'])

    # 4. 件名・日付・単価の上書き
    updates = [{'range': cell, 'values': [[val]]} for cell, val in plan['cells'].items()]
    ws.batch_update(updates, value_input_option='USER_ENTERED')

    return {'plan': plan, 'status': 'applied'}
