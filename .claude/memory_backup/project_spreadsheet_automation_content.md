---
name: スプレッドシート操作はAIコース教材の必須テーマ
description: スプレッドシート自動化(GAS/clasp/Sheets API/Playwright)はCampers AIコース・コンサル教材の必須コンテンツ。記録蓄積先と扱い方針
type: project
originSessionId: 723d0162-a26f-4a70-85ec-18691aeb1a1d
---
# スプレッドシート操作はAIコース教材の必須テーマ

社長明言（2026-04-28）: 「CampersのAIコースのコンテンツでスプレッドシートを操作することは絶対に必要な情報」。

**Why:**
- eBay運営に限らず、ほぼ全ての中小事業者は業務をスプレッドシートに集約している
- 「AIにスプレッドシート任せたい」は受講生の最大ニーズ
- やり方を間違えるとすぐ詰む（Monaco editor手作業、Chrome MCP既知バグ等）ため、Reffortの実体験は希少価値が高い

**How to apply:**
- スプレッドシート操作・GAS開発・clasp運用・Sheets API・Playwright UI操作 等の作業をした時は、必ず以下にも反映：
  1. **session-log として実体験を保存**: `education/campers/content-projects/spreadsheet-automation-case-study/session-logs/YYYY-MM-DD_<topic>.md`
  2. **共通ルールはmemory化**: `memory/feedback_spreadsheet_automation_patterns.md`（3型ルーティング）に追記
  3. **journey-log.md にも当日エントリ追記**（CLAUDE.md セッション終了ルール準拠）
- 失敗・遠回り・既知バグへの対処も生のまま残す（受講生に「実運用での落とし穴」を伝えるため最も価値が高い素材）
- 社長が判断するまで配信物として公開はしない（`feedback_hp_publish_rule.md` 同精神）
- 「これは記事化しますか？」と提案するのは禁止（社長負担増・本人判断時に勝手に進めない）

**蓄積場所サマリー:**
- ケーススタディ全体: `education/campers/content-projects/spreadsheet-automation-case-study/`
  - `README.md` — 目的・配信シナリオ
  - `outline.md` — 章構成テンプレート（記事/動画/教材化時の骨子）
  - `session-logs/` — 各実装サイクルの生記録
  - `assets/` — スクリーンショット・図表
- 関連 memory: `feedback_spreadsheet_automation_patterns.md` / `feedback_chrome_mcp_unattended.md`
- 関連 spec: `commerce/ebay/tools/gas-shiire-tool-spec.md`

**蓄積対象（型別）:**
- 型A（GAS/clasp）: 仕入管理表・将来追加するGASプロジェクトの実装と運用
- 型B（Sheets API/Service Account）: 週次レポートの GSheets書込・在庫管理ツールのシート更新
- 型C（Playwright/cookie）: Campersメンバー削除の権限OFF/ON UI操作

**配信タイミング判断:**
- 配信は社長判断のみ。Claude Codeから「記事化しますか？」と提案しない。
- 蓄積物は「ネタ帳」であり、社長が記事/動画/スクール教材に落とし込む際の素材。
