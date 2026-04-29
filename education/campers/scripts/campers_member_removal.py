"""
Campersメンバー削除（Playwright版）— Chrome MCP不要・無人実行可能。

実行：
    python campers_member_removal.py             # 本番
    python campers_member_removal.py --dry-run   # 削除を実際にはせず手順だけ確認

処理：
    1. removal-queue.jsonを読み、status=pending かつ removal_date <= today を抽出
    2. 各対象について：
       a) 対象部屋のメンバーリスト取得（API）
       b) 権限OFF（Playwright UI操作）— 質問・共有 → ツール質問
       c) API削除
       d) 権限ON（Playwright UI操作）
       e) 全体連絡は権限変更なしで API削除
    3. queue更新（completed）
    4. Chatwork個人DM(426170119)に箱型カード報告

絶対厳守ルール（feedback_scheduled_tasks.md準拠）：
    ・権限OFF成功確認まで削除を絶対実行しない
    ・各ステップ成否確認・失敗時は中断
    ・中断時は権限を必ず元に戻す
    ・成功・失敗どちらでも社長DMに報告
    ・対象者以外を絶対削除しない（除外ID集合の安全装置）
    ・「APIでできないからスキップ」は絶対許可しない
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright, TimeoutError as PWTimeout

sys.stdout.reconfigure(encoding="utf-8")

# ── パス・定数 ────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parents[2]
QUEUE_FILE = SCRIPT_DIR.parent / "removal-queue.json"
AUTH_FILE = SCRIPT_DIR / ".chatwork_auth.json"

load_dotenv(PROJECT_ROOT / "commerce" / "ebay" / "analytics" / ".env")
CW_TOKEN = os.getenv("CW_TOKEN")
PRESIDENT_DM = "426170119"

# 部屋設定
ROOMS_WITH_TOGGLE = [
    ("178951974", "Campers 質問・共有チャット"),
    ("213457923", "Campers ツール質問チャット"),
]
ROOM_ANNOUNCE = ("167902309", "Campers【全体連絡チャット】")

# 権限トグルラベル（OFFにする2つ）
TOGGLE_LABELS = [
    "チャットの参加者一覧を表示する",
    "メッセージ送信を許可する",
]


# ── Chatwork API ──────────────────────────────────────────────
def _api(url: str, *, method: str = "GET", body: dict | None = None) -> dict:
    data = urllib.parse.urlencode(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-ChatWorkToken", CW_TOKEN)
    with urllib.request.urlopen(req, timeout=20) as r:
        text = r.read().decode("utf-8")
    return json.loads(text) if text else {}


def list_room_members(room_id: str) -> list[dict]:
    return _api(f"https://api.chatwork.com/v2/rooms/{room_id}/members")


def update_room_members(room_id: str, admin_ids: list[int], member_ids: list[int], readonly_ids: list[int]) -> dict:
    return _api(
        f"https://api.chatwork.com/v2/rooms/{room_id}/members",
        method="PUT",
        body={
            "members_admin_ids": ",".join(map(str, admin_ids)),
            "members_member_ids": ",".join(map(str, member_ids)),
            "members_readonly_ids": ",".join(map(str, readonly_ids)),
        },
    )


def post_dm(body: str) -> bool:
    try:
        _api(
            f"https://api.chatwork.com/v2/rooms/{PRESIDENT_DM}/messages",
            method="POST",
            body={"body": body},
        )
        return True
    except Exception as e:
        print(f"  ⚠️ DM送信失敗: {e}")
        return False


def remove_member_via_api(room_id: str, target_id: int) -> dict:
    """対象IDだけ除外して再送信。安全装置：対象以外の人数差は0以上、admin0人禁止、対象が消えていることを確認。"""
    before = list_room_members(room_id)
    before_in = any(m["account_id"] == target_id for m in before)
    if not before_in:
        return {"status": "skip_not_in", "before_total": len(before)}

    admin_ids = [m["account_id"] for m in before if m["role"] == "admin" and m["account_id"] != target_id]
    member_ids = [m["account_id"] for m in before if m["role"] == "member" and m["account_id"] != target_id]
    readonly_ids = [m["account_id"] for m in before if m["role"] == "readonly" and m["account_id"] != target_id]

    if len(admin_ids) < 1:
        raise RuntimeError(f"安全装置：admin 0人になる（room={room_id}）")
    # 対象以外を1人も巻き込まないこと
    expected_after = len(before) - 1
    submitted_total = len(admin_ids) + len(member_ids) + len(readonly_ids)
    if submitted_total != expected_after:
        raise RuntimeError(
            f"安全装置：送信総数mismatch room={room_id} before={len(before)} 期待={expected_after} 送信={submitted_total}"
        )

    update_room_members(room_id, admin_ids, member_ids, readonly_ids)
    after = list_room_members(room_id)
    still_in = any(m["account_id"] == target_id for m in after)
    return {
        "status": "ok" if not still_in else "still_in_after",
        "before_total": len(before),
        "after_total": len(after),
        "still_in_after": still_in,
    }


# ── Playwright 権限トグル操作 ──────────────────────────────────────
def open_settings_dialog(page: Page) -> None:
    """歯車 → メニュー → グループチャットの設定 ダイアログを開く"""
    page.wait_for_selector('[data-testid="room-header_room-settings-button"]', timeout=20000)
    page.click('[data-testid="room-header_room-settings-button"]')
    page.wait_for_selector(
        '[data-testid="room-header_room-settings_room-settings-menu"]',
        timeout=5000,
    )
    page.click('[data-testid="room-header_room-settings_room-settings-menu"]')
    page.wait_for_selector('[data-testid="room-setting-dialog_save-button"]', timeout=10000)


def click_permission_tab(page: Page) -> None:
    page.click('button:has-text("権限")', timeout=5000)
    # トグルラベルが現れるまで待つ
    page.wait_for_selector(f'label:has-text("{TOGGLE_LABELS[0]}")', timeout=5000)


def get_toggle_states(page: Page) -> dict[str, bool]:
    """現在のチェックボックス状態を辞書で返す"""
    return page.evaluate("""
        () => {
            const labels = ["チャットの参加者一覧を表示する", "メッセージ送信を許可する"];
            const result = {};
            for (const lbl of labels) {
                const ls = Array.from(document.querySelectorAll('label'))
                    .filter(l => l.innerText.includes(lbl));
                if (ls.length === 0) { result[lbl] = null; continue; }
                const cb = ls[0].querySelector('input[type="checkbox"]');
                result[lbl] = cb ? cb.checked : null;
            }
            return result;
        }
    """)


def set_toggle(page: Page, label: str, want: bool) -> bool:
    """ラベルでcheckbox特定し want に合わせる。成功でTrue。"""
    states = get_toggle_states(page)
    cur = states.get(label)
    if cur is None:
        raise RuntimeError(f"トグルが見つからない: {label}")
    if cur == want:
        return True
    # ラベルクリックで切り替え
    page.click(f'label:has-text("{label}")', timeout=3000)
    time.sleep(0.5)
    after = get_toggle_states(page).get(label)
    return after == want


def save_dialog(page: Page) -> None:
    page.click('[data-testid="room-setting-dialog_save-button"]', timeout=5000)
    time.sleep(1.5)
    # ダイアログが残っている場合はEscapeで閉じる
    try:
        save_btn = page.query_selector('[data-testid="room-setting-dialog_save-button"]')
        if save_btn and save_btn.is_visible():
            page.keyboard.press("Escape")
            time.sleep(0.5)
    except Exception:
        pass
    # backdropが消えるまで最大8秒待つ
    try:
        page.wait_for_selector('[data-testid="backdrop"]', state="detached", timeout=8000)
    except PWTimeout:
        # それでも残るならもう一度Escape
        try:
            page.keyboard.press("Escape")
            time.sleep(1)
        except Exception:
            pass


def open_room(page: Page, room_id: str) -> None:
    page.goto(f"https://www.chatwork.com/#!rid{room_id}")
    page.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(5)
    if "login" in page.url.lower():
        raise RuntimeError("ログイン切れ。setup_chatwork_auth.pyを再実行してください。")


def set_all_toggles(page: Page, room_id: str, want: bool, label: str, *, verify: bool = True) -> dict:
    """部屋を開いて2トグルを want に設定し保存。verify=Trueなら再オープンで実反映を確認。"""
    open_room(page, room_id)
    open_settings_dialog(page)
    click_permission_tab(page)

    before = get_toggle_states(page)
    results = {}
    for lbl in TOGGLE_LABELS:
        ok = set_toggle(page, lbl, want)
        results[lbl] = ok
        if not ok:
            return {"ok": False, "before": before, "after": get_toggle_states(page), "details": results, "verified": False}

    # 保存直前のDOM状態を確認
    pre_save = get_toggle_states(page)
    save_dialog(page)

    if not verify:
        return {"ok": all(pre_save.get(lbl) == want for lbl in TOGGLE_LABELS), "before": before, "pre_save": pre_save, "details": results, "verified": False}

    # 再オープンして永続化を確認
    open_room(page, room_id)
    open_settings_dialog(page)
    click_permission_tab(page)
    after = get_toggle_states(page)
    persisted = all(after.get(lbl) == want for lbl in TOGGLE_LABELS)
    # 確認後ダイアログを閉じる
    try:
        page.keyboard.press("Escape")
        time.sleep(0.5)
        page.wait_for_selector('[data-testid="backdrop"]', state="detached", timeout=5000)
    except Exception:
        pass
    return {"ok": persisted, "before": before, "after": after, "details": results, "verified": True}


# ── Queue ────────────────────────────────────────────────────
def load_queue() -> list[dict]:
    with open(QUEUE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_queue(q: list[dict]) -> None:
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(q, f, ensure_ascii=False, indent=2)
        f.write("\n")


def pending_today(q: list[dict]) -> list[dict]:
    today = date.today().isoformat()
    return [
        e for e in q
        if e.get("status") == "pending" and e.get("removal_date", "9999-12-31") <= today
    ]


# ── メインフロー ────────────────────────────────────────────────
def process_target(page: Page, entry: dict, dry_run: bool) -> dict:
    """1名処理：権限OFF→API削除→権限ON×2部屋＋全体連絡API削除"""
    name = entry["name"]
    target_id = int(entry["account_id"])
    log = {"name": name, "account_id": target_id, "rooms": [], "status": "in_progress"}

    # Pre-check: 対象が3部屋に在籍しているか
    print(f"\n■ 処理開始: {name}（{target_id}）")
    pre = {}
    for rid, label in ROOMS_WITH_TOGGLE + [ROOM_ANNOUNCE]:
        members = list_room_members(rid)
        in_room = any(m["account_id"] == target_id for m in members)
        pre[rid] = in_room
        print(f"  [{rid}] {label}: {'在籍' if in_room else '在籍なし'}")
    log["pre_membership"] = pre

    if not any(pre.values()):
        log["status"] = "skip_not_in_any_room"
        return log

    # 各 toggle 部屋を順に処理
    for rid, label in ROOMS_WITH_TOGGLE:
        room_log = {"room_id": rid, "label": label, "in_room_before": pre[rid]}
        if not pre[rid]:
            room_log["status"] = "skip_not_in"
            log["rooms"].append(room_log)
            continue

        # 権限OFF
        print(f"\n  ▶ {label} 権限OFF")
        try:
            off_result = set_all_toggles(page, rid, want=False, label=label)
            room_log["off_result"] = {k: (v if not isinstance(v, dict) else v) for k, v in off_result.items()}
        except Exception as e:
            room_log["status"] = "abort_off_failed"
            room_log["error"] = f"権限OFF例外: {e}\n{traceback.format_exc()}"
            log["rooms"].append(room_log)
            log["status"] = "aborted"
            return log

        if not off_result["ok"]:
            room_log["status"] = "abort_off_failed"
            log["rooms"].append(room_log)
            log["status"] = "aborted"
            return log

        # API削除
        if dry_run:
            print(f"  ▶ [DRY-RUN] 削除APIスキップ")
            room_log["delete"] = {"status": "dry_run"}
        else:
            print(f"  ▶ {label} API削除")
            try:
                d = remove_member_via_api(rid, target_id)
                room_log["delete"] = d
                if d.get("still_in_after"):
                    raise RuntimeError("削除後も在籍したまま")
            except Exception as e:
                room_log["delete"] = {"status": "error", "error": str(e)}
                # 必ず権限を戻す
                print(f"  ⚠️ 削除エラー → 権限復元してから中断")
                try:
                    on_result = set_all_toggles(page, rid, want=True, label=label)
                    room_log["on_result_after_error"] = on_result
                except Exception as ee:
                    room_log["on_result_after_error_exception"] = str(ee)
                log["rooms"].append(room_log)
                log["status"] = "aborted"
                return log

        # 権限ON
        print(f"  ▶ {label} 権限ON復元")
        try:
            on_result = set_all_toggles(page, rid, want=True, label=label)
            room_log["on_result"] = on_result
        except Exception as e:
            room_log["status"] = "abort_on_failed"
            room_log["on_error"] = str(e)
            log["rooms"].append(room_log)
            log["status"] = "aborted_after_delete"  # 削除済みで権限復元失敗
            return log

        if not on_result["ok"]:
            room_log["status"] = "abort_on_failed"
            log["rooms"].append(room_log)
            log["status"] = "aborted_after_delete"
            return log

        room_log["status"] = "ok"
        log["rooms"].append(room_log)

    # 全体連絡（toggle不要）
    rid, label = ROOM_ANNOUNCE
    room_log = {"room_id": rid, "label": label, "in_room_before": pre[rid]}
    if pre[rid]:
        if dry_run:
            print(f"\n  ▶ [DRY-RUN] {label} 削除スキップ")
            room_log["delete"] = {"status": "dry_run"}
        else:
            print(f"\n  ▶ {label} API削除（toggle不要）")
            try:
                d = remove_member_via_api(rid, target_id)
                room_log["delete"] = d
            except Exception as e:
                room_log["delete"] = {"status": "error", "error": str(e)}
                log["rooms"].append(room_log)
                log["status"] = "aborted_announce_failed"
                return log
        room_log["status"] = "ok"
    else:
        room_log["status"] = "skip_not_in"
    log["rooms"].append(room_log)

    log["status"] = "completed"
    return log


def build_report(target_logs: list[dict], dry_run: bool) -> str:
    """箱型カードDM本文を構築"""
    today_str = date.today().strftime("%Y-%m-%d")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    head = "🧪 Campersメンバー削除 DRY-RUN" if dry_run else "✅ Campersメンバー削除 完了報告"

    # 全成功 / 一部失敗 判定
    all_completed = all(t["status"] == "completed" for t in target_logs) if target_logs else True
    if not target_logs:
        return f"[info][title]{head}｜{today_str}[/title]処理対象なし（pending+期日到来分なし）[/info]"

    if not all_completed:
        head = "⚠️ Campersメンバー削除 中断報告"

    lines = [f"[info][title]{head}｜{today_str}[/title]"]
    lines.append(f"実行日時: {now_str}")
    if dry_run:
        lines.append("⚠️ DRY-RUN（API削除なし／権限トグル動作確認のみ）")
    lines.append("")

    for t in target_logs:
        lines.append(f"■ {t['name']}（{t['account_id']}）— {t['status']}")
        for r in t.get("rooms", []):
            mark = "✅" if r["status"] == "ok" else ("➖" if r["status"].startswith("skip") else "❌")
            line = f"  {mark} {r.get('label','')}: {r['status']}"
            if "delete" in r:
                d = r["delete"]
                if d.get("status") == "ok":
                    line += f" / 削除OK ({d.get('before_total','?')}→{d.get('after_total','?')})"
                elif d.get("status") == "dry_run":
                    line += " / DRY-RUN"
                elif d.get("status") == "skip_not_in":
                    line += " / 在籍なし"
                else:
                    line += f" / {d.get('status')}"
            lines.append(line)
        lines.append("")

    lines.append("[/info]")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--headed", action="store_true", help="ブラウザを表示")
    args = parser.parse_args()

    if not CW_TOKEN:
        print("❌ CW_TOKEN なし（commerce/ebay/analytics/.env）")
        sys.exit(1)
    if not AUTH_FILE.exists():
        msg = "[info][title]❌ Campersメンバー削除 起動失敗[/title]Playwright認証ファイル(.chatwork_auth.json)が見つかりません。setup_chatwork_auth.py を実行して再ログインしてください。[/info]"
        post_dm(msg)
        print("❌ AUTH_FILE なし")
        sys.exit(1)

    queue = load_queue()
    targets = pending_today(queue)
    print(f"処理対象: {len(targets)}件")
    if not targets:
        post_dm(build_report([], args.dry_run))
        return

    target_logs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed, slow_mo=100)
        context = browser.new_context(
            storage_state=str(AUTH_FILE),
            viewport={"width": 1400, "height": 900},
            locale="ja-JP",
        )
        page = context.new_page()

        try:
            for t in targets:
                log = process_target(page, t, dry_run=args.dry_run)
                target_logs.append(log)
                # 成功時のみqueue更新
                if log["status"] == "completed" and not args.dry_run:
                    for e in queue:
                        if e.get("account_id") == t["account_id"] and e.get("removal_date") == t.get("removal_date"):
                            e["status"] = "completed"
                            e["completed_date"] = date.today().isoformat()
                    save_queue(queue)
        finally:
            try:
                browser.close()
            except Exception:
                pass

    # 詳細ログをファイルにも保存（デバッグ用）
    log_path = SCRIPT_DIR / f"_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_path.write_text(json.dumps(target_logs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n📝 ログ保存: {log_path}")

    body = build_report(target_logs, args.dry_run)
    if post_dm(body):
        print("📨 DM報告完了")
    else:
        print("⚠️ DM報告失敗")


if __name__ == "__main__":
    main()
