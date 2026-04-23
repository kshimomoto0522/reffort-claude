# BayChat AI Reply 設計図

> **バージョン**: v0.2（実データ完全統合版）
> **作成日**: 2026-04-20
> **管理主体**: 株式会社Reffort（Cowatechレビュー体制）
> **マスター言語**: 日本語（技術用語は英日併記）
> **単一参照源**: このフォルダ配下のMarkdown群が AI Reply の唯一の正式設計図。既存の19枚CSV（`cowatech_payloads/spec_sheets/`）は「参考資料」にデモート済み。

---

## 📌 この設計図の目的

**社長・Claude・Cowatech の3者が、同じ情報源で議論・実装・改善を進められる共通言語を作る。**

ゴール状態：
- ✅ AI Replyの全仕様（プロンプト本文・API構造・条件分岐・UI連動・tone別差分・event enum・スキーマ）が書いてある
- ✅ ClaudeがCowatechに仕様質問することがほぼゼロになる
- ✅ Cowatechが実装・更新するときの参照源・運用手順が整っている
- ✅ 既存CSV19枚は「過去の参考資料」にデモート済み

---

## 🗂️ ファイル構成（v0.2・全19ファイル）

```
design-doc/
├── README.md                              ← このファイル（目次・入口）
│
├── 📊 横断ビュー
│   ├── 00_overall_flow.md                 ← 全体処理フロー（Mermaid図）
│   ├── 01_prompt_blocks_overview.md       ← プロンプトブロック俯瞰表
│   ├── 02_ui_injection_matrix.md          ← UI → プロンプト注入マトリクス
│   ├── 04_conditional_logic.md            ← 条件分岐表（完全版）
│
├── 📇 ブロック詳細カード（7枚）
│   └── 03_block_cards/
│       ├── block_00_item_info.md          ← [0] 商品情報JSON
│       ├── block_chat_history.md          ← [1..N] チャット履歴
│       ├── block_n1_description_guide.md  ← [N+1] 補足情報ガイド
│       ├── block_n2_base_prompt.md        ← [N+2] BASE_PROMPT
│       ├── block_n3_output_format.md      ← [N+3] OUTPUT_FORMAT
│       ├── block_n4_admin_prompt.md       ← [N+4] admin_prompt ⭐
│       └── block_n5_forced_template.md    ← [N+5] FORCED_TEMPLATE
│
├── 🔧 運用・管理
│   ├── 05_changelog.md                    ← 変更履歴
│   ├── 07_cowatech_operation.md           ← Cowatech運用ルール
│   ├── 08_migration_plan.md               ← CSV → 設計図の移行計画
│   └── 09_open_questions.md               ← 未解決論点集約
│
├── 🔌 API・テスト・連携
│   ├── 10_api_testing.md                  ← テスト環境完全仕様
│   ├── 12_ebay_api_integration.md         ← eBay API連携仕様（42項目）
│   └── 13_baychat_api_spec.md             ← BayChat → Cowatech I/F仕様
│
├── 🎯 モデル・QA・将来機能
│   ├── 11_model_selection.md              ← モデル選定経緯・次期候補
│   ├── 14_qa_testing.md                   ← QA観点・不具合履歴
│   └── 15_summary_mode.md                 ← 要約モード仕様（将来機能）
│
└── 📖 参照
    └── 06_glossary.md                     ← 用語集・FAQ
```

---

## 🚦 v0.2 完成度

| ファイル | 状態 | 備考 |
|---------|-----|-----|
| README.md | ✅ 完成版 | v0.2 |
| 00_overall_flow.md | ✅ 完成版 | Mermaid図＋非エンジニア解説 |
| 01_prompt_blocks_overview.md | ✅ 完成版 | 7ブロック俯瞰表 |
| 02_ui_injection_matrix.md | ✅ 完成版 | UI → プロンプト注入表 |
| 03_block_cards/block_00_item_info.md | ✅ 完成版 | 実データ転記 |
| 03_block_cards/block_chat_history.md | ✅ 完成版 | event enum完全リスト |
| 03_block_cards/block_n1_description_guide.md | ✅ 完成版 | 原文＋条件分岐 |
| 03_block_cards/block_n2_base_prompt.md | ✅ 完成版 | 単純版＋詳細版両方転記 |
| 03_block_cards/block_n3_output_format.md | ✅ 完成版 | schema完全定義 |
| 03_block_cards/block_n4_admin_prompt.md | ✅ 完成版 | v2.4構造・バージョン履歴 |
| 03_block_cards/block_n5_forced_template.md | ✅ 完成版 | tone別3バリエーション完全転記 |
| 04_conditional_logic.md | ✅ 完成版 | 全条件分岐・全パラメータ |
| 05_changelog.md | ✅ 完成版 | v0.2変更記録 |
| 06_glossary.md | ✅ 完成版 | 用語集・FAQ・略語集 |
| 07_cowatech_operation.md | ✅ 完成版 | 運用ルール |
| 08_migration_plan.md | ✅ 完成版 | CSV19枚移行マップ |
| 09_open_questions.md | ✅ 完成版 | Q1-Q24の論点集約 |
| 10_api_testing.md | ✅ 完成版 | testing/完全ドキュメント |
| 11_model_selection.md | ✅ 完成版 | モデル選定経緯 |
| 12_ebay_api_integration.md | ✅ 完成版 | eBay API 42項目 |
| 13_baychat_api_spec.md | ✅ 完成版 | BayChat→Cowatech I/F |
| 14_qa_testing.md | ✅ 完成版 | QA観点・不具合履歴 |
| 15_summary_mode.md | ✅ 完成版 | 要約モード仕様（ドラフト段階） |

---

## 📖 読む順番（目的別）

### 🤝 Cowatech：初回に読むもの（30分）

このフォルダに初めてアクセスした方は、以下の順で読んでください。
この4ファイルだけで、AI Reply の全体像と Reffort ⇔ Cowatech の連携ルールが把握できます。

1. `README.md`（このファイル）
2. `00_overall_flow.md`（AI Reply の全体処理フロー・図解あり）
3. `01_prompt_blocks_overview.md`（プロンプトを構成する7ブロックの俯瞰表）
4. `07_cowatech_operation.md`（Reffort との連携・更新・Slack運用ルール）

### 🤝 Cowatech：実装・更新時に参照するもの

BayChat本体の実装・修正に入るときは、以下を併せて確認してください。

- 該当するブロックカード（`03_block_cards/` 配下の7ファイルから1つ選択）
- `09_open_questions.md`（現在Reffortが抱えている未解決論点）
- `13_baychat_api_spec.md`（BayChat⇔OpenAI API の I/F仕様）
- `05_changelog.md`（直近の変更履歴）

### 🤝 Cowatech：困ったとき

- `06_glossary.md`（用語集・FAQ）
- Slack `#baychat-ai導入` で質問してください（`07_cowatech_operation.md` のSlack運用ルール参照）

---

### 🔹 初見で全体像を把握したい（Reffort内向け）
1. `README.md`（このファイル）
2. `00_overall_flow.md`（全体フロー図）
3. `01_prompt_blocks_overview.md`（7ブロック俯瞰）

**所要時間：10分**

### 🔹 admin_prompt を編集したい（社長の日常作業）
1. `03_block_cards/block_n4_admin_prompt.md`（最重要）
2. `services/baychat/ai/prompt_admin_v2.4.md`（実物）
3. `14_qa_testing.md`（デグレチェック）

### 🔹 Cowatech に新機能を依頼したい
1. `07_cowatech_operation.md`（運用フロー）
2. 該当するブロックカード（`03_block_cards/`）
3. `09_open_questions.md`（既存論点確認）

### 🔹 テストを実行したい
1. `10_api_testing.md`（完全ガイド）
2. `11_model_selection.md`（モデル選定）

### 🔹 Cowatech に質問したい
1. `09_open_questions.md`（未解決論点）
2. 該当するブロックカード
3. `07_cowatech_operation.md`（Slack運用ルール）

---

## 🎯 社長への最短アクセス

| 疑問 | 開くファイル |
|------|-----------|
| AI Replyの仕組みは？ | `00_overall_flow.md` |
| 7つのブロックとは？ | `01_prompt_blocks_overview.md` |
| 社長が触れるのはどこ？ | `block_n4_admin_prompt.md` |
| UI操作はどこに反映される？ | `02_ui_injection_matrix.md` |
| 今Cowatechに聞きたいことは？ | `09_open_questions.md` |
| 今の品質スコアは？ | `block_n4_admin_prompt.md` → 品質ベンチマーク |
| Gemini切替はいつ？ | `11_model_selection.md` |

---

## 🛠️ 更新ルール（要点）

### 変更時の必須アクション
1. 該当ファイルを編集
2. `05_changelog.md` に記録（いつ・誰が・なぜ・何を・影響範囲）
3. 関連ドキュメントのリンク・クロスリファレンス更新
4. HTMLビューを再生成（`python _render_html.py`）

### 運用フェーズ別（`07_cowatech_operation.md`）
- **〜1か月**：直編集
- **1〜3か月**：PR＆レビュー
- **3か月〜**：PR＆月次同期

---

## 🌐 HTMLプレビュー

社長が読みやすいように、全Markdownを整形HTMLに変換している：

- **トップ（推奨）**: `_html_preview/dashboard.html` — 社長ダッシュボード
- **目次**: `_html_preview/index.html` — 全ページ一覧

**生成コマンド**：
```bash
cd services/baychat/ai/design-doc
python _render_html.py
```

---

## 🔴 現在の最重要論点（v0.2時点）

**Cowatech確認待ちの高優先度論点（9件）**：

| # | 内容 |
|---|------|
| Q1 | FORCED_TEMPLATE除去時のTO/FROM注入経路 |
| Q3 | description・TO/FROMの「空/なし」判定ロジック |
| Q4 | チャット履歴の件数・トークン上限 |
| Q5 | multi_language_reply schema名の参照有無 |
| Q6 | Gemini 2.5 Flash実装ロードマップ |
| Q7 | whoPaysShipping欠損の原因 |
| Q8 | 自動メッセージ/手動返信の区別ロジック |
| Q9 | 既存CSVのコード依存の有無 |

詳細：`09_open_questions.md`

---

## 📞 関連ドキュメント（設計図外）

| ドキュメント | 役割 |
|----------|------|
| `services/baychat/ai/CLAUDE.md` | BayChat部門の日常運営ルール |
| `services/baychat/ai/prompt_admin_v2.4.md` | 現行admin_promptの実物 |
| `services/baychat/ai/cowatech_payloads/gpt_api_payload.txt` | 本番ペイロード一次資料 |
| `services/baychat/ai/cowatech_payloads/baychat_api_payload.txt` | BayChatリクエスト一次資料 |
| `services/baychat/ai/cowatech_payloads/spec_sheets/` | 既存CSV19枚（参考資料） |
| `services/baychat/ai/handoff_20260420_design_doc_project.md` | 本プロジェクトの背景 |
| `services/baychat/ai/testing/` | 本番同等テスト環境 |

---

## 🗓️ バージョン履歴

| バージョン | 日付 | 主な変更 |
|----------|-----|--------|
| v0.1 | 2026-04-20 | 叩き台（骨格・admin_promptサンプル完成） |
| **v0.2** | **2026-04-20** | **実データ完全統合（5エージェント並列調査・全ブロックカード完成・新規7ファイル追加）** |
| v1.0（予定） | — | Cowatechレビュー完了版 |

詳細：`05_changelog.md`

---

*この設計図は「作ること」が目的ではなく、「3者が意思疎通でき、継続管理できる基盤」が目的。形式より実用性を優先する。*
