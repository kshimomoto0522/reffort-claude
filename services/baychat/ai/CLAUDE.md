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

- **プロンプト**: v2.4 本番運用中 / **v2.3_baseline_natural5_lean (iter11)** = 最新テスト版・**原則ベース抜本書き直し**（10原則+5HARD RULES・280行）
- **本番モデル候補**: **GPT-4.1-Mini / GPT-4o-Mini**（標準目標3秒近接で達成）。GPT-5-Mini は **2026-05-01 本番除外決定**（余計なことを言う・コントロール困難・推論モデル特性で速度遅い）
- **cat02 完成**: 全15ケース（subset5 + additional10）で社長OK判定済（2026-05-01）。社長フィードバック ABCDEF 全解消・品質100%クリーン
- **cat03 社長指摘 6ケース全クリア**（natural5_lean iter11c）: 03_01確定形・03_03投げやり解消・03_04状況確認先行・03_06フォーマット完備・03_07eBay公式振り解消・03_10cancel+repurchase案内
- **Cowatech stg+prd 反映完了**（2026-04-22 23:58）：FORCED_TEMPLATE除去＋プレースホルダ `{sellerAccountEbay}/{buyerAccountEbay}` 注入対応
- **本番反映待ち**: natural5_lean の改修を Cowatech に反映依頼するタイミングは社長判断
- **🔥 次セッション冒頭必読**: `handoff_20260505_natural5_lean_complete.md`
- **⚠️ プロンプト改修前必読**: `_reffort_internal/prompt_construction_rules.md`（永続メタルール・レシピ積み上げ再発防止）

👉 **詳細全量: `ai-reply-status.md`**（開発状況・本番ペイロード構造・モデル選定・プロンプト管理・テスト環境・今後の機能）

---

## 進行中・今後のタスク（未完了分）

### 現在進行中（2026-05-05 〜）
- [x] cat02 完成（全15ケース・natural3 / iter8・社長OK判定）
- [x] GPT-5-Mini 本番除外決定（社長判断 2026-05-01）
- [x] cat03 13ケース JSON 設計完了（single 5 + multi 5 + ASSERTIVE 3）
- [x] 4つ目のトーン ASSERTIVE 追加（admin_prompt natural3_assertive / iter9）
- [x] batch_test.py ThreadPoolExecutor 並列化実装（速度ほぼ半減・質影響なし）
- [x] cat03 ASSERTIVE 3ケース × POLITE/ASSERTIVE 対比走行（Round A）完了
- [x] 保留モード（hold_mode）必要性検証 → 不要判断（補足入力で代替可能）
- [x] Cowatech 仕様書（ASSERTIVE 追加のみ）作成・PDF送付（`cowatech_spec_assertive_tone_addition.pdf`）
- [x] 会社名表記の根本修正（13ファイル「株式会社Reffort」→「株式会社リフォート（Reffort, Ltd.）」）
- [ ] **次セッション ①**: cat03 残ケース（cat03_01〜10）テスト走行（POLITE/FRIENDLY/APOLOGY）
- [ ] **次セッション ②**: 要約モードの仕様検討
- [ ] Cowatech 主張トーン実装完了待ち（工数・コスト見積を Slack で受領後）
- [ ] natural3_assertive の Reffort 側 admin 画面登録タイミング判断
- [⏸ 保留] SpeedPAK 業者対応辞書（cat03 完了後再着手・社長Q1〜Q4回答待ち）
- [⏸ 保留] hold_mode v2 検討（reflect 型再設計 + 20ケース追検証）
- [⏸ 保留] 補足欄プリセットボタン（実運用テスト中に必要性を再検討）

### 次セッション冒頭の確認事項
- `handoff_20260505_assertive_complete.md` を読んで ASSERTIVE 追加完了状態と次セッション内容を把握
- cat03 残ケーステスト + 要約モード仕様検討を 2セッション並行で進める

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
