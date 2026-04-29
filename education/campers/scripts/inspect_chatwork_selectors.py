"""決定版調査：設定ボタン → メニュー項目 → 実際の設定パネルへ進む"""
import sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
SCRIPT_DIR = Path(__file__).parent.resolve()
AUTH_FILE = SCRIPT_DIR / ".chatwork_auth.json"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            storage_state=str(AUTH_FILE),
            viewport={"width": 1400, "height": 900},
            locale="ja-JP",
        )
        page = context.new_page()
        rid = "178951974"
        page.goto(f"https://www.chatwork.com/#!rid{rid}")
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(6)
        page.wait_for_selector('[data-testid="room-header_room-settings-button"]', timeout=15000)

        # Step1: 歯車アイコン
        print("Step1: 歯車")
        page.click('[data-testid="room-header_room-settings-button"]')
        time.sleep(2)

        # Step2: メニュー項目「グループチャットの設定」
        print("Step2: グループチャットの設定 メニュー項目をクリック")
        try:
            page.click('[data-testid="room-header_room-settings_room-settings-menu"]', timeout=5000)
        except Exception as e:
            print(f"  fail: {e}")
        time.sleep(3)

        sc2 = SCRIPT_DIR / "_step2_settings_open.png"
        page.screenshot(path=str(sc2), full_page=True)
        html2 = SCRIPT_DIR / "_step2_settings_open.html"
        html2.write_text(page.content(), encoding="utf-8")
        print(f"  📸 {sc2.name} html={html2.stat().st_size:,}")

        # Step3: 「権限」タブをクリック（text）
        print("\nStep3: 権限タブクリック")
        try:
            page.click('button:has-text("権限")', timeout=5000)
        except Exception as e:
            print(f"  fail: {e}")
        time.sleep(2)
        sc3 = SCRIPT_DIR / "_step3_permission_tab.png"
        page.screenshot(path=str(sc3), full_page=True)
        html3 = SCRIPT_DIR / "_step3_permission_tab.html"
        html3.write_text(page.content(), encoding="utf-8")
        print(f"  📸 {sc3.name}")

        # data-testid で関連UIを探す
        print("\n--- visible data-testid (settings/permission/admin系のみ) ---")
        ts = page.evaluate("""() => {
            const els = document.querySelectorAll('[data-testid]');
            const out = {};
            for (const el of els) {
                const dt = el.getAttribute('data-testid');
                const v = el.offsetWidth > 0 && el.offsetHeight > 0;
                if (v && (dt.includes('setting') || dt.includes('admin') || dt.includes('permission') || dt.includes('tab') || dt.includes('toggle') || dt.includes('switch') || dt.includes('group'))) {
                    out[dt] = (el.innerText || el.getAttribute('aria-label') || '').slice(0, 60);
                }
            }
            return out;
        }""")
        for k, v in ts.items():
            print(f"  [{k}] '{v}'")

        # 「権限」「メッセージ送信」等を再検索（panel内）
        print("\n--- KEYWORD HITS in panel ---")
        for kw in ["権限", "メッセージ送信", "参加者一覧", "閲覧", "メンバー以外", "管理者", "編集権限", "操作権限", "保存"]:
            results = page.evaluate(f"""() => {{
                const kw = {kw!r};
                const all = document.querySelectorAll('*');
                const hits = [];
                for (const el of all) {{
                    if (el.children.length === 0) {{
                        const t = (el.innerText || el.textContent || '').trim();
                        if (t.includes(kw) && t.length < 80) {{
                            const rect = el.getBoundingClientRect();
                            const visible = rect.width > 0 && rect.height > 0;
                            const tag = el.tagName.toLowerCase();
                            const id = el.id || '';
                            const dt = el.getAttribute('data-testid') || '';
                            const aria = el.getAttribute('aria-label') || '';
                            hits.push({{ tag, id, dt, aria, text: t, visible }});
                        }}
                    }}
                }}
                return hits.filter(h => h.visible).slice(0, 12);
            }}""")
            if results:
                print(f"\n  [{kw}] {len(results)}件")
                for r in results[:8]:
                    print(f"    <{r['tag']} id='{r['id']}' dt='{r['dt']}' aria='{r['aria']}'> '{r['text'][:60]}'")

        # checkbox/input を全部
        print("\n--- input[type=checkbox] visible ---")
        cbs = page.evaluate("""() => {
            const els = document.querySelectorAll('input[type="checkbox"], [role="switch"]');
            return Array.from(els).filter(e => {
                const r = e.getBoundingClientRect();
                return r.width > 0 && r.height > 0;
            }).map(e => {
                const dt = e.getAttribute('data-testid') || '';
                const id = e.id || '';
                const checked = e.checked;
                const ariaChecked = e.getAttribute('aria-checked');
                // 親をたどってラベル文字列を取る
                let parent = e.parentElement;
                let label = '';
                for (let i = 0; i < 5 && parent; i++) {
                    const t = parent.innerText || '';
                    if (t.length > 0 && t.length < 200) { label = t.slice(0, 100); break; }
                    parent = parent.parentElement;
                }
                return { dt, id, checked, ariaChecked, label };
            });
        }""")
        for cb in cbs:
            print(f"  dt='{cb['dt']}' id='{cb['id']}' checked={cb['checked']} aria={cb['ariaChecked']} label='{cb['label']}'")

        browser.close()


if __name__ == "__main__":
    main()
