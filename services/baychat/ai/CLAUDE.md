# BayChat部門 — 部門ドキュメント

> 親ドキュメント: `/reffort/CLAUDE.md` を必ず先に読むこと。
> このフォルダでは「BayChatのサービス運営・AI機能開発・プロンプト改善・Cowatech連携・競合対策」に特化して動く。
> **詳細ファイル一覧: `index.md` を参照。**

---

## サービス概要

| 項目 | 内容 |
|------|------|
| サービス名 | BayChat |
| 種別 | eBayセラー向け顧客対応・CSツール（SaaS） |
| 形態 | Webブラウザアプリ（PC・スマホ対応） |
| 認定 | eBay Compatible Application（公認） |
| 開発 | Cowatech（ベトナム） |
| 特徴 | シンプルイズザベスト。CSに特化。統合ツール化はしない方針 |

---

## AI Reply — 現状要点（最重要開発案件）

- **プロンプト**: v2.4 本番運用中 / **v2.3_baseline_natural3 (iter8)** = cat02 確定版（テスト中）
- **本番モデル候補**: **GPT-4.1-Mini / GPT-4o-Mini**（標準目標3秒近接で達成）。GPT-5-Mini は **2026-05-01 本番除外決定**（余計なことを言う・コントロール困難・推論モデル特性で速度遅い）
- **cat02 完成**: 全15ケース（subset5 + additional10）で社長OK判定済（2026-05-01）。社長フィードバック ABCDEF 全解消・品質100%クリーン
- **Cowatech stg+prd 反映完了**（2026-04-22 23:58）：FORCED_TEMPLATE除去＋プレースホルダ `{sellerAccountEbay}/{buyerAccountEbay}` 注入対応
- **本番反映待ち**: natural3 系の改修を Cowatech に反映依頼するタイミングは社長判断（cat03 まで完了後の一括反映が候補）
- **次セッション冒頭必読**: `handoff_20260501_evening_cat02_complete.md`

👉 **詳細全量: `ai-reply-status.md`**（開発状況・本番ペイロード構造・モデル選定・プロンプト管理・テスト環境・今後の機能）

---

## 進行中・今後のタスク（未完了分）

### 現在進行中（2026-05-01 〜）
- [x] cat02 完成（全15ケース・natural3 / iter8・社長OK判定）
- [x] GPT-5-Mini 本番除外決定（社長判断 2026-05-01）
- [x] 比較HTMLに補足情報入力UI + 再生成APIサーバー実装（result_server.py / port 8765）
- [ ] cat03（配送関連 / 購入後質問）テスト着手 — 次セッション
- [ ] cat03 で APOLOGY トーン込みテスト・5-Mini を念のため最終挙動確認 → 完全除外
- [ ] SpeedPAK 業者対応辞書を admin_prompt に組み込むか・Cowatech 仕様書追加するか判断
- [ ] natural3 系の Cowatech 本番反映タイミング判断
- [ ] testing/payload_builder.py の v2.6 対応は不要（v2.3_baseline 系で完結）

### 次セッション冒頭の確認事項
- `handoff_20260501_evening_cat02_complete.md` を読んで cat02 状態と cat03 着手内容を把握
- cat03 設計（10ケース・single 5 + multi 5）→ 社長レビュー → テスト
- 速度改善（3モデル → 2モデル化 + 並列実行検討）

### 並行継続
- [ ] v2.4での本番運用継続（品質担保済み）
- [ ] eBay API連携（Cowatech対応完了待ち）
- [ ] 無料→有料転換率改善の施策立案
- [ ] AI Replyリリースに合わせたプロモーション計画
- [ ] マーケ担当者との連携・方針決定

---

## BayChat AI Reply 進行時のスタンス（厳守）

memory `feedback_baychat_ai_reply_stance.md` に詳細。要点：

1. **設計図は理解済み前提**で動く（CSV・ペイロード・仕様すべて頭に入っている状態）
2. **Cowatechに聞く前に設計図から答えを出す努力**をする
3. **論点リストを機械的に並べない**（今必要か毎回吟味）
4. **議論の結論を草案に正確に反映**する
5. **経営パートナーとして社長の意図を汲んでクエットさんとやりとりする**

---

## Claudeへの重要ルール（BayChat部門専用）

- AI Replyのプロンプト開発は専用セッションで行う（このCLAUDE.mdは概要のみ）
- ユーザーデータ・売上データを扱う際は必ず社長に確認を取ること
- 機能追加・変更はCowatechへの仕様書作成まで行うこと
- 競合動向は常に意識しながら提案すること
- 「無料ユーザーの有料転換率向上」も重要テーマとして意識すること
- Cowatech連携・Slack送信ルールは `cowatech-rules.md` を厳守

---

## 関連ファイル

- **次セッション冒頭必読**: `handoff_20260423_cowatech_prd_sync.md`（最新）
- **最新プロンプト**: `prompt_admin_v2.6.md` + `.html` + `.json`
- テスト結果: `testing/results/` 配下に最終マージ Excel `test_gpt_gemini_gpt5nano_v2.6_merged_20260422.xlsx`
- 最新ダッシュボード: `testing/results/dashboard_test_gpt_gemini_gpt5nano_v2.6_merged_20260422.html`
- 社長フィードバック用: `testing/results/comparison_20260422_011559.html`
- 合成テストケース: `testing/test_cases/synthetic_40cases_v1.json`
- テストケース生成: `testing/generate_synthetic_cases.py`
- 本番ペイロード解析: `cowatech_payloads/` (gpt_api_payload.txt) + `cowatech_payloads/spec_sheets/` (CSV 19枚)
- 過去ハンドオフ: `handoff_20260416_results.md` / `handoff_20260420_design_doc_project.md` / `handoff_20260420_v0.2_complete.md`

---

*最終更新: 2026-04-24（竹案T3実施 — 419→約130行圧縮・退避5ファイル作成・archive/移動・index.md新設）*
*BayChat AI Reply 進行時は memory `feedback_baychat_ai_reply_stance.md` の5原則を厳守*
*変更があれば随時更新すること*
