"""月次請求書 半自動化 メインCLI

使い方:
  python run.py --month 202603              # ドライラン（書込なし）
  python run.py --month 202603 --apply      # 実書込
  python run.py --month 202603 --targets honma,shimizu  # 一部のみ
  python run.py                             # 引数省略 → 前月分

書込前に必ずドライランを通して社長確認を取る運用。
"""

import argparse
import sys
from datetime import date
from pathlib import Path

import yaml

from inv_common import parse_yyyymm, previous_month, open_invoice_log, write_log
import inv_honma
import inv_shimizu
import inv_sasaki


THIS_DIR = Path(__file__).resolve().parent


def load_config():
    with (THIS_DIR / 'config.yml').open(encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description='月次請求書 半自動化')
    parser.add_argument('--month', help='YYYYMM形式（省略時は前月）')
    parser.add_argument('--apply', action='store_true', help='実書込（指定無しはドライラン）')
    parser.add_argument('--targets', default='all',
                        help='honma,shimizu,sasaki カンマ区切り（デフォルト: all）')
    args = parser.parse_args()

    if args.month:
        year, month = parse_yyyymm(args.month)
    else:
        today = date.today()
        year, month = previous_month(today.year, today.month)
        print(f'※ --month 省略のため前月を採用: {year}年{month}月')

    targets = ['honma', 'shimizu', 'sasaki'] if args.targets == 'all' \
              else [t.strip() for t in args.targets.split(',') if t.strip()]

    mode = 'APPLY（実書込）' if args.apply else 'DRY-RUN（ドライラン）'
    print('=' * 70)
    print(f'月次請求書 半自動化 / {year}年{month}月 / {mode}')
    print(f'対象: {", ".join(targets)}')
    print('=' * 70)

    config = load_config()

    log_dir = THIS_DIR / config['defaults']['log_dir']
    log_path = open_invoice_log(log_dir, prefix=f'{year}{month:02d}_{"apply" if args.apply else "dry"}')
    log_payload = {
        'year': year, 'month': month, 'mode': mode, 'targets': targets,
        'plans': {}, 'results': {},
    }

    handlers = {
        'honma':   (inv_honma.plan_honma,     inv_honma.print_plan,     inv_honma.apply_honma),
        'shimizu': (inv_shimizu.plan_shimizu, inv_shimizu.print_plan,   inv_shimizu.apply_shimizu),
        'sasaki':  (inv_sasaki.plan_sasaki,   inv_sasaki.print_plan,    inv_sasaki.apply_sasaki),
    }

    has_error = False
    for t in targets:
        if t not in handlers:
            print(f'\n⚠️  未知のターゲット: {t}')
            continue
        plan_fn, print_fn, apply_fn = handlers[t]
        try:
            plan = plan_fn(year, month, config)
            print_fn(plan)
            log_payload['plans'][t] = {k: (v if not callable(v) else str(v)) for k, v in plan.items() if k != 'details'}
            log_payload['plans'][t]['_detail_count'] = len(plan.get('details', [])) if isinstance(plan.get('details'), list) else None

            if args.apply:
                print(f'\n  → 書込中（{t}）...')
                result = apply_fn(year, month, config)
                log_payload['results'][t] = {k: v for k, v in result.items() if k != 'plan'}
                print(f'  ✅ 書込完了（{t}）')
        except Exception as e:
            has_error = True
            print(f'\n❌ {t} でエラー: {e}')
            import traceback
            traceback.print_exc()
            log_payload['results'][t] = {'status': 'error', 'message': str(e)}

    write_log(log_path, log_payload)
    print(f'\n📝 ログ: {log_path}')

    if has_error:
        print('\n⚠️  一部のターゲットでエラーが発生しました。ログを確認してください。')
        sys.exit(1)

    if not args.apply:
        print('\n' + '=' * 70)
        print('※ ドライランのため書込は実行していません。')
        print('  内容を確認のうえ、社長OK後に --apply を付けて再実行してください。')
        print('=' * 70)


if __name__ == '__main__':
    main()
