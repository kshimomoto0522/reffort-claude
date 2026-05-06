# 🚨 次セッション冒頭で必ず読むファイル一覧

> ルート `CLAUDE.md` から分離（2026-05-06）。セッション開始時にここを必ず開いて進行中タスクを把握する。
> 古くなった項目は削除し、表の上のもの（最新）から処理する。

---

## 🔥🔥 進行中（最重要）

- **🆕 5/31 Campersウェビナー残タスク整理（ドラフト・Education Lead作成）**: `education/campers/content-projects/webinar-materials/handoff_20260506_remaining_tasks_to_531_DRAFT.md`
  - 5/13〜5/19 隔週メンテで社長判断必須の8項目（料金・開始時期・運営フォーマット等）を整理
  - 第1週から course-curator / content-recorder 起動推奨・第2週から webinar-architect 本格起動
- **🆕 Phase 1 エージェント組織立ち上げ（Education部門のみ稼働中）**: `.claude/org_chart.md` + `.claude/pm_role.md` + `.claude/agents/`
  - 次セッションから `/education <依頼内容>` でEducation Lead起動可能
  - PM/COO（メイン会話のClaude）→ Education Lead → 3 Specialists の3階層構造
- **ASICS v8+補正版 本番稼働中（210秒試行・1047対応・3論点修正反映）**: `commerce/ebay/tools/handoff_20260506_v8plus_deploy.md`
  - v9並列化中止・v8ベースに3論点修正＋待機210秒短縮＋EndItem 1047成功扱い・5/6 13:47ビルド・S02754自動クリア確認済
  - 1周完走後にBot検出頻度をレビュー
- **🆕 BayChat 発送追跡 API 統合（OC返信待ちで凍結中）**: `services/baychat/ai/handoff_20260506_shipment_api_investigation.md`
  - 方針確定：層A(BayChat既存DB→構造化SHIPMENT BLOCK) + 層B(FedEx/DHL公開API + Orange Connex非公開API) + バックグラウンド同期+キャッシュ
  - Orange Connex 担当者宛て依頼メッセージ社長から送信済 → 返信後に層B仕様書を全面書き直し
  - 既存ドラフト `cowatech_spec_ebay_shipment_data_integration.md` は **凍結（旧Fulfillment API前提）**・流用不可
  - Quantity 修正（A）は完了：設計図訂正済み
- **BayChat AI Reply natural5_lean (iter11) 完成・原則ベース抜本書き直し**: `services/baychat/ai/handoff_20260505_natural5_lean_complete.md`
  - 10原則+5HARD RULESに圧縮・660→280行/-63%・cat03社長指摘6ケース全クリア
  - プロンプト構成永続メタルール `_reffort_internal/prompt_construction_rules.md` 新設
  - 残タスク（OC返信待ちと並行可）：①cat03_05保証書欠品 ②cat03 FRIENDLY/ASSERTIVEスコア低下

## 🔥 完了済み（参考・参照のみ）

- **ASICS 並列化中止経緯**: `commerce/ebay/tools/handoff_20260505_evening_parallel_v9.md` + `memory/project_asics_parallel_v9.md`
  - DECODOコスト過大・AdsPower共有問題で中止・v9コード残置・将来モバイルSIM案で再開可能
- **ASICS在庫管理ツール v8 完成**: `commerce/ebay/tools/handoff_20260505_asics_v8_complete.md`
  - v8+補正版のベース・GAS削除予約連携稼働中・adidasツールはv8+補正の知見適用予定
- **BayChat AI Reply ASSERTIVE 追加完了（旧）**: `services/baychat/ai/handoff_20260505_assertive_complete.md`
  - 朝の引継ぎ・iter9時点・上書き済み
- **BayChat AI Reply cat02 完成・cat03 引継ぎ（旧）**: `services/baychat/ai/handoff_20260501_evening_cat02_complete.md`
  - iter1〜8自走改善で品質100%クリーン・GPT-5-Mini本番除外決定・補足情報UI/再生成APIサーバー実装済
- **eBay リサーチツール Ver.1.5 完成**: `commerce/ebay/tools/research/handoff_20260501_v15.md`
  - 5サイト並列+12カテゴリ+evidence score 7シグナル+赤字除外ゲート・社長判断待ちAPI 3件
- **コンテンツ基盤整備 完了引継ぎ**: `.claude/handoff_20260429_content_infrastructure_complete.md`
  - 業務縦軸構造に根本刷新完了・5/31ウェビナー骨子v0.1＋AIコースカリキュラムv0.1完成

## 📌 戦略・ダッシュボード

- **配信ダッシュボード**: `education/campers/content-projects/INDEX.md`（全体の取り出し窓口・最初に開く）
- **2軸戦略コンテンツ前提**: `memory/project_consulting.md` + `memory/feedback_content_audience_framing.md`
  - BayChat は Campers のみ・Note/X 完全禁止
- **直近イベント**: 2026-05-31（日）Campersウェビナー（`memory/project_campers_webinar.md`）
- **竹案リファクタ T1-T15 全完了**（梅案 `eef37ab` → 竹案 `ea044c9`）
  - 各部門 `index.md` → `.claude/rules/project-structure.md` の順で把握

## 🆕 新機能（4/24以降稼働中）

- 隔週自動メンテ: `biweekly-claude-maintenance`（第1・第3月曜10時・肥大化監視＋Chatwork個人DM通知）
- 半自動改善: `/隔週メンテナンス` スラッシュコマンド
- memory 3層統合: `memory/` → `.claude/memory_backup/` → GitHub（DailyGithubBackup 0:05自動同期）
- Campers削除: Windowsタスク `CampersMemberRemoval`（Playwright版・毎日5:00・Chrome MCP不要）
- 仕入管理表GAS: `commerce/ebay/tools/gas/shiire/` clasp管理（Monaco貼付け廃止）

## 🛠 BayChat AI Reply作業時の必読

- `services/baychat/ai/handoff_20260423_cowatech_prd_sync.md`
- `memory/feedback_baychat_ai_reply_stance.md`

---

*最終更新: 2026-05-06 午後（v9並列化中止・v8+補正版本番投入・210秒試行・1047対応・S02754自動クリア確認済／隔週メンテで本ファイル新設）*
