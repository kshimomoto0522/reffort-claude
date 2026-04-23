# BayChat AI Reply 設計図

> **管理主体**: 株式会社Reffort（Cowatech共同レビュー）
> **目的**: Reffort と Cowatech が同じ情報を見て AI Reply の実装・改善・テストを進めるための **単一参照源**

---

## 🤝 Cowatech：初回に読むもの（30分）

この4ファイルだけで、AI Reply の全体像と Reffort ⇔ Cowatech の連携ルールが把握できます。

1. `README.md`（このファイル）
2. `00_overall_flow.md`（AI Reply の処理フロー・図解あり）
3. `01_prompt_blocks_overview.md`（プロンプトを構成する7ブロックの俯瞰）
4. `07_cowatech_operation.md`（Reffort との連携・更新・Slack運用ルール）

## 🤝 Cowatech：実装・更新時に参照するもの

- 該当ブロックカード（`03_block_cards/` 配下の7枚から1つ選択）
- `09_open_questions.md`（未解決論点）
- `13_baychat_api_spec.md`（BayChat ↔ OpenAI API の I/F仕様）
- `05_changelog.md`（直近の変更履歴）

困ったら：`06_glossary.md`（用語集・FAQ）→ Slack `#baychat-ai導入` で質問

**ブラウザで読みたい場合**：`_html_preview/index.html` をブラウザで開くと、見やすいHTML版で全ファイルを閲覧・ナビゲーションできます。GitHubで見る場合は .md をそのままクリックしてください。

---

## 🗂️ ファイル構成

```
design-doc/
├── README.md                              このファイル
│
├── 🗺 全体像
│   ├── 00_overall_flow.md                 処理フロー図
│   ├── 01_prompt_blocks_overview.md       7ブロック俯瞰
│   ├── 02_ui_injection_matrix.md          UI → プロンプト注入表
│   └── 04_conditional_logic.md            条件分岐・プレースホルダ置換
│
├── 📇 ブロック詳細（7枚）
│   └── 03_block_cards/
│       ├── block_00_item_info.md              [0] 商品情報JSON
│       ├── block_chat_history.md              [1..N] チャット履歴
│       ├── block_n1_description_guide.md      [N+1] 補足情報ガイド
│       ├── block_n2_base_prompt.md            [N+2] BASE_PROMPT
│       ├── block_n3_output_format.md          [N+3] OUTPUT_FORMAT
│       ├── block_n4_admin_prompt.md       ⭐  [N+4] admin_prompt（Reffort領域）
│       └── block_n5_forced_template.md    🔴  [N+5] FORCED_TEMPLATE（廃止済み）
│
├── 🔌 API・連携
│   ├── 12_ebay_api_integration.md         eBay API 42項目
│   └── 13_baychat_api_spec.md             BayChat → OpenAI API I/F
│
├── 🔧 運用・管理
│   ├── 05_changelog.md                    変更履歴
│   ├── 07_cowatech_operation.md           Cowatech運用ルール
│   └── 09_open_questions.md               未解決論点
│
└── 📖 参照
    └── 06_glossary.md                     用語集・FAQ
```

**設計図外（Cowatech非公開・Reffort内部記録）**：
`services/baychat/ai/_reffort_internal/` にテスト環境仕様・モデル選定経緯・QA記録・将来機能案などを分離

---

## 🔄 更新ルール（シンプル版）

### Cowatech が実装を更新したとき
1. Cowatech が Slack `#baychat-ai導入` の該当議題スレッドで変更内容を共有
2. Reffort（下元＋Claude）が該当する設計図を更新
3. GitHub に push（毎日0時に自動バックアップ）
4. Cowatech は GitHub で常に最新を参照できる

### Reffort が設計図を先行更新したとき
1. Reffort が該当ファイルを編集 → GitHub push
2. Slack で Cowatech に変更内容を告知
3. 必要に応じて Cowatech がレビュー・実装

### 変更記録
- 変更のたびに `05_changelog.md` の先頭に追記（いつ・誰が・なぜ・何を・影響範囲）

---

## 📞 連絡先・関連情報

| 項目 | 内容 |
|------|------|
| Slackチャンネル | `#baychat-ai導入`（チャンネルID: C09KXK26J8G） |
| Cowatech担当 | Dang Van Quyet（クエットさん）`<@U04HGPBABQU>` |
| Reffort担当 | Keisuke Shimomoto（下元）`<@U048ZRU4KLG>` |
| GitHubリポジトリ | https://github.com/kshimomoto0522/reffort-claude（Private） |
| 設計図パス | `services/baychat/ai/design-doc/` |

---

*この設計図は「3者（Reffort・Claude・Cowatech）が同じ情報で意思疎通するための共通言語」。形式より実用性を優先。*
