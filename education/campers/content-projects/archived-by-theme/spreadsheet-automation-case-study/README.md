# スプレッドシート自動化ケーススタディ

> **本プロジェクトの目的**: AIで業務を回すeBayセラー（および中小事業者）にとって、**スプレッドシート操作の自動化は必須スキル**。本ケーススタディは2026-04-28のClaude Code運用大改修（Anthropic既知バグへの対処＋clasp導入）の全過程を、**Campers受講生・将来のコンサル受講者向けコンテンツ素材として蓄積**する骨組みプロジェクト。
>
> ⚠️ **配信計画・記事公開・動画制作・チャネル別タイミング等は社長判断で別途実施**。本プロジェクトは「素材蓄積のみ」を目的とし、勝手に公開・配信しない（`memory/feedback_hp_publish_rule.md` / `memory/feedback_slack_rules.md` の精神準拠）。

---

## なぜ「スプレッドシート操作」が AIコース教材として絶対必要か

eBay運営に限らず、ほぼ全ての中小事業者は以下のいずれか／全部に依存している：

- 在庫管理表
- 仕入管理表
- 売上ダッシュボード
- 顧客リスト
- 経費集計表

これらを「AIに任せる」と一口に言っても、**やり方を間違えると詰む**。受講生が最も挫折しやすいのもここ。本ケーススタディは「実際に詰まった具体例 + 抜け道」で構成する。

---

## 本プロジェクトの構造

```
spreadsheet-automation-case-study/
  README.md                                 ← 本ファイル（目的・方針）
  outline.md                                ← 章構成テンプレート（受講生向け教材化の骨子）
  session-logs/                             ← 各実装サイクルのセッションログ
    2026-04-28_chrome-bypass-and-clasp-migration.md  ← 初回（Playwright移行＋clasp導入）
  assets/                                   ← スクリーンショット・before/after図表
```

---

## 蓄積方針

1. **3型ルーティングの実例を蓄積**:
   - 型A（GASロジック・clasp）: 仕入管理表の clasp 移行
   - 型B（外部読書・Sheets API）: 週次レポートのGSheets書込
   - 型C（UI操作・Playwright）: Campersメンバー削除の権限OFF/ON
   - 各型を「いつ選ぶ」「具体実装」「失敗例」セットで残す

2. **失敗・回避策・既知バグの実体験を残す**:
   - Anthropic Issue [#30356](https://github.com/anthropics/claude-code/issues/30356) / [#47180](https://github.com/anthropics/claude-code/issues/47180)（Chrome MCP の per-origin permission問題）
   - Claude scheduled-task の per-task 承認キャッシュ不安定性
   - Monaco editor 手動Ctrl+V運用の限界
   - これらを生のまま残す（受講生に「実運用での落とし穴」を伝えるため）

3. **素材 ≠ 配信物**:
   - ここに溜まったものを**そのまま公開**することはない
   - 社長が記事・動画・スクール教材に落とし込む際の「ネタ帳」

---

## 想定されるコンテンツ化シナリオ（社長判断で選択）

- **Note記事**: 「AIにスプレッドシートを編集させる3つの方法 — eBay運営で実践した具体例」
- **YouTube動画**: 「AIに仕入管理表を任せる：Apps Script / clasp / Sheets API の使い分け」
- **X スレッド**: 「Claude Code の Chrome MCP が無人実行で詰まる問題、回避策まとめ」
- **Campersスクール教材**: 「あなたの業務スプレッドシートをAIに任せる前に知るべきこと」
- **コンサル教材**: 「中小事業者向けスプレッドシートAI化ロードマップ」
- **書籍**: 「AIで業務を回す実践書」（将来）

---

## 関連 memory / 仕様

- スプレッドシート自動化3型ルーティング: `memory/feedback_spreadsheet_automation_patterns.md`
- Chrome操作の無人タスクはClaude経由を捨てる: `memory/feedback_chrome_mcp_unattended.md`
- 仕入管理表GAS仕様: `commerce/ebay/tools/gas-shiire-tool-spec.md`
- Campersメンバー削除（Playwright版）: `education/campers/scripts/README.md`
- コンテンツ記録原則: `memory/feedback_content_recording.md`
