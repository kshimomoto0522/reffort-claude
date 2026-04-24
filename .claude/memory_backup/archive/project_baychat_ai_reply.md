---
name: BayChat AI Reply プロジェクト状況
description: AI Reply機能の開発進捗・プロンプト・モデル選定・テスト結果
type: project
originSessionId: cad5d328-fbe2-462e-8502-6ca7c9ebaa09
---
# BayChat AI Reply プロジェクト

## 現在のステータス（2026-04-23 朝時点）

### 🆕 Cowatech stg+prd 反映済み（2026-04-22 23:58 完了）
- FORCED_TEMPLATE 除去済み
- プレースホルダ注入対応済み（命名：`{sellerAccountEbay}/{buyerAccountEbay}`）
- UI signature/receiver 選択で動的置換（クエットさん確認済み）
- **ただし admin画面のプロンプトは依然として v2.4**（社長が v2.6 アップロードするまで動作変わらず）

### 🔴 設計図同期問題が顕在化（2026-04-23 朝）
社長指摘：「Cowatech側がコード更新したから設計図も更新必要＋共有・更新管理の方法を考える必要」

**現状のズレ**：
- Cowatech prd：`{sellerAccountEbay}/{buyerAccountEbay}`
- 設計図 v0.2：`{buyer_name}/{seller_name}`（命名不一致）
- 設計図（22ファイル）は Cowatech に**一度も共有していない**

**次セッション判断待ち**：
- 進め方：X（設計図最新化優先）/ Y（Cowatech相談先行）/ Z（全部今日）
- 共有方法：A（GitHub）/ B（Notion）/ C（Google Drive）/ D（Cowatech既存）
- Claude推奨：X + A + クエットさんお礼即返信

---

## 旧ステータス（2026-04-22 深夜時点）

### ✅ 設計図整備プロジェクト v0.2 完成（2026-04-20）
- 22ファイル（`services/baychat/ai/design-doc/` 配下）で AI Reply の全仕様を統合・単一参照源化
- 設計図は「Claudeが理解している前提」で扱う（memory `feedback_baychat_ai_reply_stance.md`）

### ✅ Q1+Q3 仕様確定・Cowatech実装対応中（2026-04-21）
- FORCED_TEMPLATE除去確定（+2.0pt品質改善）
- TO/FROM UI機能は残す・admin_prompt v2.5/v2.6 に移行
- Cowatech：実装対応中（工数8時間で承諾済み）。プレースホルダ名 `{sellerAccountEbay}` `{buyerAccountEbay}` を先行共有
- UI選択反映の動的置換確認質問送信済・返信待ち
- Slack thread_ts: 1776427836.602699

### ✅ GPT-5-Nano 仮決定（2026-04-21 社長判断）
- 18ケーステストで Gemini 23.22 / GPT-4.1-Mini 22.72 / GPT-5-Nano 22.33
- 社長判断：Gemini除外（速度4秒超・コスト高・Cowatech実装要）
- **GPT-5-Nano 採用**：コスト ¥0.04/件（現行1/7）・速度2.8秒・品質差0.4ptはプロンプト改善で埋める戦略
- **admin画面でGPTモデル変更可能が判明** → Cowatech依頼不要
- 設計図 `design-doc/11_model_selection.md` 更新済み

### ✅ admin_prompt v2.6 ドラフト完成（2026-04-22）
- `services/baychat/ai/prompt_admin_v2.6.md`
- 新設3セクション：EMPATHY ENFORCEMENT / MULTILINGUAL HANDLING / COMPLEX CASE HANDLING
- Next step 具体性強化・FINAL CHECK 拡張
- HTML + JSON エクスポート済み（admin画面アップロード用）

### ✅ 合成40ケーステスト完了（2026-04-22）
- 8分類 × 4ステージ × 商品ジャンル多様化で40シナリオ設計
- S2進行中18件（45%）を含む「途中対応」中心
- v2.6 × 3モデル × 40ケース = 120テスト実施
- 購入前バグ（全件 `purchase_completed` 混入）を発見し、9件を `events=[]` で再生成 → 部分再テスト → Excelマージで解決
- **最終結果**：Gemini 19.85 / **GPT-5-Nano 19.05** / GPT-4.1-Mini 18.77
- 18件テストより-3pt — これが「途中対応」を含めた真の実力

### 🚫 Cowatech に今後聞かない論点（設計図から答え出せる/優先度低）
- Q4（履歴件数上限）: 品質改善に直結しない
- Q5（schema名参照）: 要約モード実装時で十分
- **Q6（Gemini実装ロードマップ）: 実質不要**（GPT内切替はadmin画面で可能・Gemini採用しない方針）
- Q7（whoPaysShipping欠損）: 別案件として切り出し
- Q8（自動メッセージ区別）: ✅ 解決済み
- Q9（CSVコード依存）: 3か月計画内で確認

### 🔜 明日（2026-04-23予定）のフロー
1. 社長が `comparison_20260422_011559.html` でケース別フィードバックを書き JSON 出力
2. Claude がフィードバックを v2.7 に反映
3. v2.7 vs v2.6 で40ケース再テスト → 改善幅検証
4. 合格なら admin画面に v2.7 登録 + GPT-5-Nano 切替

### 🚫 Cowatech に今後聞かない論点（設計図から答え出せる/優先度低）
- Q4（履歴件数上限）: 品質改善に直結しない・今は不要
- Q5（schema名参照）: 要約モード実装時で十分
- Q6（Gemini実装ロードマップ）: FORCED_TEMPLATE除去完了後で十分
- Q7（whoPaysShipping欠損）: 別案件として切り出し
- Q8（自動メッセージ区別）: **CLAUDE.md に「本番では自動メッセージはAIに渡らない」と記載あり＝既に解決済み**
- Q9（CSVコード依存）: 3か月計画の中で確認

### テスト環境・モデル・プロンプトの現状
- テスト環境：動作中（社内のみ）・DB接続完了・大量テスト可能
- 本番ペイロード再現インフラ: `testing/payload_builder.py`（2026-04-16）で本番同構造テスト可能
- 使用モデル（本番）：GPT-4.1-Mini Standard（`gpt-4.1-mini-2025-04-14`）
- 次期モデル：Gemini 2.5 Flash（Cowatech実装待ち）
- プロンプト：v2.4（本番運用中）→ v2.5 ドラフト作成中

### テスト環境・モデル・プロンプトの現状（据え置き）
- テスト環境：動作中（社内のみ）・DB接続完了・大量テスト可能
- 本番ペイロード再現インフラ: `testing/payload_builder.py`（2026-04-16）で本番同構造テスト可能
- 使用モデル（本番）：GPT-4.1-Mini Standard（`gpt-4.1-mini-2025-04-14`）
- 次期モデル：要再検討（Gemini 2.5 Flashは速度外れ値あり。GPT-5-Mini最有力）
- プロンプト：v2.4（2026-04-15作成）で本番運用継続
- **大発見（2026-04-16）**: FORCED TEMPLATE除去で平均スコア19.5→21.5（+2.0pt）改善。ただし本番適用判断は設計図整備後に保留

### Cowatech返信の扱い（保留中）
- 4/16にFORCED TEMPLATE除去の技術確認4件送信 → クエットさんから「2/3/4はBayChat画面で確認できるのでは？」と返信
- 4/20に手元資料でQ2・Q4は自力解決、残Q1・Q3に絞った返信草案作成済みだが**送信保留**
- 設計図整備プロジェクト立ち上げ後、文脈を再検討してから送信するか、大きな相談の一部に組み込むか判断

---

## モデル選定結論（2026-03-19）

**採用方針: Gemini 2.5 Flash（Google）**

| モデル | 速度 | 品質 | 1ユーザー月額（5回/日×30日） |
|--------|------|------|--------------------------|
| GPT-4.1-Mini（現在） | 10秒以上 | 良好 | 約¥24 |
| GPT-4.1-Nano | 速い | 日本語品質に課題 | 約¥6 |
| GPT-5-Mini Standard | 18秒 | 非常に高い | 約¥36 |
| GPT-5-Mini Priority | 10秒 | 非常に高い | 約¥131 |
| Claude 3.5 Haiku | 速い | 高い | 約¥90 |
| **Gemini 2.5 Flash** | **1〜2秒** | **GPT-5相当** | **約¥15** |

→ コストを下げながら品質を上げられる唯一の選択肢としてGemini 2.5 Flashに決定。

### Cowatechへの依頼状況（Gemini移行）
- 2026-03-19：クエットさんへSlackでGemini 2.5 Flash実装の確認メッセージを送信済み
  （※ 社長のGOなしに勝手に送信してしまったミスあり）
- **返信なし（2026-03-20時点）**
- 返信があった場合：内容を社長に報告してから次のアクションを決める

---

## プロンプト管理

| バージョン | 状況 |
|-----------|------|
| v2.3 | **GPT APIテスト済み・本番テスト待ち**（2026-03-30） |
| v2.2 | adminに登録中（v2.3テスト後に差し替え予定） |
| v2.1 | 旧版 |
| v2.0 | 旧版（参照不要） |
| v1.0 | 旧版（参照不要） |

### プロンプト構成（2つに分離）
- **ベースプロンプト**：Cowatech管理。出力形式（JSON）・eBayコンプライアンスのみ。ほぼ変えない
- **adminプロンプト**：社長がadmin画面で自由に変更可能。CS品質・トーン・会話フロー等

### プロンプトファイルの場所
`C:\Users\KEISUKE SHIMOMOTO\Desktop\reffort\services\baychat\ai\prompt_admin_v2.3.md`

### プロンプト設計方針（社長の明確な指示 2026-03-21）
- **ルールで縛るのではなくAIの判断力に委ねる方針**
- 細かいルールを積み重ねるとAIは柔軟性を失う
- 特定シナリオごとの具体ルールは追加しない
- 代わりに「どういう姿勢で返信すべきか」を教える
- 例：「具体的な日程を言え」→ ✗ 特定ルール / 「バイヤーの立場に立って安心させろ」→ ✓ 姿勢

### 仕様メモ（Cowatechより確認済み）
- TO/FROM設定：BayChatのTO/FROM設定と連動している（YES確認）
- 署名（Best regards,）：トーン別に変わる仕様。詳細仕様シート → https://docs.google.com/spreadsheets/d/1eXuElyXIK6q-2CwHwTyYbdElT_IOM2iT_WTbS5FVuvs/edit?gid=1122266780#gid=1122266780&range=B13:E14
- `{{ admin setting }}`：社長のadmin画面で設定するプロンプト部分

---

## テストスクリプト

| スクリプト | 用途 |
|-----------|------|
| `run_all_tests.py` | 全ケース一括実行（v2.1対応・新旧JSON両形式対応） |
| `compare_models.py` | 2モデル比較・速度計測・コストシミュレーション |

### テストデータ（ローカル）
- `gpt_request.json` + `gpt_request_2.json` 〜 `gpt_request_10.json`（10ケース）
- **本番環境のデータ**（2026-03-21 差し替え完了）

### テストスクリプト追加（2026-03-21）
- `test_prompt_quick.py`：プロンプト修正時のクイックテスト用。GPT APIで即座にテストできる

---

## オフラインテスト環境（2026-04-14構築）

### アーキテクチャ
```
STG MariaDB ──SSH tunnel──→ VPS(163.44.112.53) ──→ Claude Code
  → データ抽出 → バッチ実行エンジン → AI自動採点 → Excelレポート
```

### スクリプト構成（services/baychat/ai/testing/）
| ファイル | 役割 |
|---------|------|
| `db_connect.py` | SSHトンネル + MariaDB接続ユーティリティ |
| `extract_cases.py` | DBからテストケース抽出（--explore / --extract） |
| `ai_judge.py` | AI審判（5項目×5点、25点満点） |
| `batch_test.py` | メインエンジン（モデル×プロンプト一括テスト→Excel出力） |

### DB接続情報
- STG Host: .envの `BAYCHAT_STG_DB_HOST` に設定済み（AWS RDS）
- VPS踏み台: 163.44.112.53（ConoHa VPS・SSHキー認証）
- ユーザー: readonly_claude
- **IPホワイトリスト登録待ち**（クエットさんへ確認済み 4/14）
- データ範囲: ひとまず下元さんのデータのみ（クエットさん提案）

### 動作確認結果（2026-04-14）
- 既存テストケース1件でGPT vs Gemini比較テスト成功
- GPT-4.1-Mini: 3.5秒 / ¥0.205
- Gemini 2.5 Flash: 1.9秒 / ¥0.043（速度2倍・コスト5分の1）

---

## 今後のタスク（優先順）

1. **STG DB接続完了**（IPホワイトリスト登録待ち → テーブル構造調査 → テストケース抽出）
2. **GPT vs Gemini 大規模比較テスト**（DB抽出ケース数百件 + AI採点）
3. **プロンプトv2.3の本番テスト**（v2.2の補足無視・保留表現問題を修正済み）
4. **保留モードの仕様設計**（トーンとは別軸の対応モード）
5. **eBay API連携**（Cowatech対応完了待ち）
6. **本番リリース**（プロンプト完成＋API連携完了後）

---

## 重要なやりとりルール（このセッションで明確化）
- Slackへのメッセージ送信は**必ず社長のGOを取ってから**行う
- 草案を提示→「GO」をもらう→送信、のフローを厳守
- 返信が来たら社長に報告し、次のアクションもGOを取る
- スケジュールタスクもGOなしで作成しない

---

## 更新ログ

| 日付 | 内容 |
|------|------|
| 2026-03-19 | プロジェクトメモリ新規作成。モデル選定完了・Gemini 2.5 Flash採用方針決定 |
| 2026-03-20 | テストデータがステージング環境のものと判明・本番データ提供を依頼。仕様メモ追記。Slack送信ルール明文化 |
| 2026-03-21 | 本番テストデータ10件受領・差し替え完了。Anthropic APIキー取得。3モデル比較テスト実施（Gemini無料枠上限到達・Claude JSONエラー）。プロンプトv2.2作成→GPT APIで6回テスト→本番テスト成功。設計方針「ルールで縛らずAIの判断力に委ねる」を明文化。「プロンプト修正はGPT APIでテストしてから提出する」運用を確立。保留モードのアイデアが出た（次のタスク） |
| 2026-03-30 | v2.2本番テストで2問題発覚（補足あり→補足のみ出力、補足なし→保留表現）。v2.3で修正：SELLER INTENTに2段階思考導入・保留禁止を「決定vs約束」で再定義・品質基準に返品例追加・FINAL CHECK追加。GPT APIで12回以上テスト。補足あり問題は完全解決、保留表現は大幅改善（完全排除はGPT-4.1-Miniのモデル特性の限界） |
| 2026-04-14 | オフラインテスト環境フレームワーク構築完了（db_connect/extract_cases/ai_judge/batch_test）。STG DB接続情報を.envに設定。Gemini API課金設定完了。GPT vs Gemini動作確認テスト成功。IPホワイトリスト登録待ち |
| 2026-04-15 | 5モデル×12ケース=60実行バッチ完了（GPT-4.1-Mini/GPT-5-Mini/GPT-5-Nano/GPT-4.1-Nano/Gemini 2.5 Flash、平均20.5/25、合計¥8.54）。HTMLレポートに会話履歴タイムライン・日本語併記・ケース別勝者バッジを実装。重大バグ発見: extract_cases.pyがSELLER_UIDハードコードで他セラー会話のロール判定を誤っていた → sellerId列とsenderId列が別物と判明 → 会話ごとに動的検出する方式に修正。vipuv_81ハードコードも動的置換。プロンプトv2.4作成（復唱禁止・挨拶対応・URL対応・テンプレート緩和）。3モデル（GPT-5-Mini/GPT-4.1-Nano/GPT-5-Nano）に絞り込んで v2.4 で再バッチ。引き継ぎドキュメント`/services/baychat/ai/handoff_20260415_to_20260416.md`作成。Cowatechへ仕様開示依頼送信済（処理フロー・実装詳細・ロギング）。 |
| 2026-04-16 | Cowatechから本番ペイロード（`gpt_api_payload.txt` 21KB）と仕様スプレッドシート（19シート分をCSV化）を入手。本番構造を完全解明（4 developer blocks＋chat history、temperature=0.2、json_schema strict、`gpt-4.1-mini-2025-04-14`）。`testing/payload_builder.py`新設（tone別FORCED TEMPLATE含む）、`batch_test.py`に`--production-payload`フラグ追加。12ケース比較実施: FORCED TEMPLATE **ON=19.5/25 vs OFF=21.5/25（+2.0pt）**。v2.4のRESPONSE STRUCTUREが状況判断を内包しているため、強制テンプレ除去が品質を上げる。TO/FROM選択機能との整合設計が次課題（3案まとめて`slack_draft_20260416.md`に保存、社長承認後に送信予定）。成果ドキュメント: `services/baychat/ai/handoff_20260416_results.md` |
| 2026-04-19 | クエットさんから4/16の技術確認に返信「2/3/4はBayChat画面を開くと検証できると思いますが、できませんでしょうか？」 |
| 2026-04-20 | 社長の指摘で手元資料を再読、Q2（TO/FROM値はFORCED TEMPLATEのみに注入）・Q4（description空ならtoneブロック挿入なし）を自力解決。残Q1・Q3の返信草案作成（送信保留）。**大きな方針転換**：社長が料理の比喩（マニュアルを作る前に調味料・機器設定が狂っている）で根本問題を提起→プロンプト微修正ループを停止し「設計図整備プロジェクト」立ち上げ。次セッション引き継ぎドキュメント`services/baychat/ai/handoff_20260420_design_doc_project.md`作成。論点A（フォーマット）・B（ツール）・C（Cowatech役割分担）が議論対象 |
| 2026-04-20 夜 | **設計図 v0.2 完成**（22ファイル・CSV19枚/本番ペイロード/全プロンプトバージョン/testing環境を統合・単一参照源化）。5エージェント並列調査を活用。Q1（TO/FROM UI機能の設計）と Q3（空/なし判定）を社長と議論し仕様確定→Cowatech送信済（thread_ts:1776427836.602699・認識確認と工数見積もり依頼）。社長の複数指摘で失敗を学習：①情報過多 ②議論結論を草案に反映し忘れ ③設計図活用漏れ。→ 新規memory: **feedback_baychat_ai_reply_stance.md**（5原則：設計図は理解済み前提・Cowatech前に自力解決・論点リスト機械消化禁止・議論結論を草案に正確反映・経営パートナースタンス）を作成。Q4-Q9は吟味の結果「今は聞かない」方針。次：admin_prompt v2.5 ドラフト作成、クエットさん返信待ち |
| 2026-04-21 | クエットさん「別設定で対応可能・工数8時間」→ 社長「既存admin_promptで実行できるように」指示→承諾。プレースホルダ `{sellerAccountEbay}` `{buyerAccountEbay}` 先行共有。UI選択反映の動的置換質問を送信（社長GOあり）。3件サンプルテスト→18件本格テスト実施で GPT-5-Nano 仮決定（品質22.33・速度2.8秒・コスト¥0.04）。Gemini は4秒超で体感NG・Cowatech実装要・コスト高で優先度最低に降格。**admin画面でGPTモデル変更可能が判明**→Cowatech依頼不要（Q6実質不要）。設計図 `11_model_selection.md` 更新 |
| 2026-04-22 | **admin_prompt v2.6 ドラフト完成**（EMPATHY ENFORCEMENT / MULTILINGUAL HANDLING / COMPLEX CASE HANDLING 新設）。社長指摘「テストが完結・お礼ばかりで途中対応不足」→ **合成40シナリオ設計**（A〜H × S1〜S4・商品ジャンル多様化：カメラ・時計・トレカ・楽器・着物・フィギュア・ゲーム・アパレル等）→ `generate_synthetic_cases.py` で生成。v2.6 × 3モデル × 40ケース本格テスト → Gemini 19.85 / GPT-5-Nano 19.05 / GPT-4.1-Mini 18.77。18件より-3pt で真の実力判明。**購入前バグ発見**（全件に purchase_completed 混入）→ 9件を events=[] で再生成・部分再テスト・Excelマージで解決。次：社長が comparison HTML でケース別フィードバック→v2.7 改善サイクル。ハンドオフ `handoff_20260422_v2.6_test_complete.md` 作成 |
| 2026-04-23 朝 | **Cowatech stg+prd 反映完了の報告受信**（FORCED_TEMPLATE除去＋プレースホルダ `{sellerAccountEbay}/{buyerAccountEbay}` 注入）。UI動的置換もクエットさん確認済。**ただし admin画面は依然v2.4**（アップロードしない限り動作変わらず）。社長指摘：「コード更新したら設計図も更新必要＋共有・更新管理の方法を考える必要」→ 設計図v0.2（22ファイル）とCowatech prd実装の命名不一致＋未共有問題が顕在化。次セッション判断待ち：進め方X/Y/Z・共有方法A/B/C/D。ハンドオフ `handoff_20260423_cowatech_prd_sync.md` 作成 |
