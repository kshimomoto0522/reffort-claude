# コンテンツ蓄積基盤整備 引き継ぎ（2026-04-28 作成）

> **新セッションでの起動方法**:
> 新セッションを起動したら、最初にこう言ってください:
> ```
> @.claude/handoff_20260428_content_infrastructure.md を読んで進めてください
> ```
> 1行で本ドキュメント全体を引き継いで実行が始まります。

---

## 📋 本ドキュメントの目的

社長から2026-04-28に依頼：「コンテンツ蓄積基盤の不備を埋める作業」を**専用セッションで実施**する。本ドキュメントは新セッションへの引継ぎ。

---

## 🔴 最優先：着手前に必ず読む「継続ルール」

**どのタスクを始める前も、以下を必ず確認してから動いてください。社長が過去に明言した運用ルールであり、全セッションで前提となります。**

### A. 思考・口調・姿勢の最重要ルール
1. `memory/feedback_tone_and_depth.md` — 敬語厳守・指摘される前に徹底的に考え抜く
2. `memory/feedback_proactive_partner.md` — 言いなり禁止・指示の目的を理解し先回り提案
3. `memory/feedback_best_first_thinking.md` — ゴールから逆算したベストを松竹梅で提示
4. `memory/feedback_declaration_to_implementation.md` — 宣言したらその場で実装まで完了
5. `memory/user_patterns.md` + `memory/user_profile.md` — 社長の思考パターン・プロフィール

### B. 本タスク特化の前提知識（**必ず先に把握**）
6. **`memory/project_consulting.md`** — 2軸戦略（Campers実名 / 匿名X→Note）
7. **`memory/feedback_content_audience_framing.md`** — 対象者と配信先別の切り分けルール
8. **`memory/project_campers_webinar.md`** — 5/31 Campersウェビナーの位置づけ
9. **`memory/feedback_content_recording.md`** — 既存のコンテンツ記録ルール
10. **`memory/project_spreadsheet_automation_content.md`** — スプレッドシート関連は教材必須テーマ

### C. 既存の content-projects 構造
- `education/campers/content-projects/claude-code-maintenance-case-study/` — 2026-04-23〜24の運用大改修
- `education/campers/content-projects/spreadsheet-automation-case-study/` — 2026-04-28の clasp/Playwright移行
- 各ケーススタディの構造: `README.md` / `outline.md` / `session-logs/` / `assets/`

---

## 🎯 社長の本来の依頼（原文）

> いずれCampers（または外部）に向けて基本的にebayに関してClaude Codeを活用したAI ebay運営のコンサル事業を行うことを前提に、わたしが日々AIを使う中で実践したこと、どのようなことを取り入れたか、どんなことでつまづいたか、やっておくべきこと、やってはいけないこと等をあなたが最終的にコンテンツにまとめられるように日々記録をしていってください

> Campersはebayのコミュニティです。BayChatはもちろんebayのCSツールですがメンバー達は開発の細かいことなどには無関係であり、あくまでまずはebayの運営についてメインでプレゼンを行い、参加者には実践させていきます。
> しかし、Claude Codeではこんなこともできるよ、自分の場合はBayChat等でこんなこともやったよ、だからあなたがClaude Codeを使いこなせばebayだけじゃなく、他に事業があるなら、なくても新しいことに活用できるよという流れと方針です。

> Campersでは毎月ウェビナーを行ったり、専用グループチャットで質問を受け付けたりしますが、それとは別に同じくAI ebay運営についてXアカウントを中心に情報発信を行い、Note等に誘導し有料記事等の販売で収益化を目指したいと考えています。
> 内容は同じではありますが、Xアカウントの方はわたしであることを伏せて活動したいと考えています。SNS運用とNote等の有料コンテンツ化（コミュニティ運営やコンサル等には誘導しない方針）の二軸で進めれるよう考えておいてください。
> しかしまずはCampersから実行します。そして5/31（日）にCampersウェビナーを行いますのでそれに向けて準備を進めていきます。

---

## 📊 現状の自己評価（前セッション最終分析）

| 要素 | 達成度 | コメント |
|---|---|---|
| 日々記録 | ◯ 90% | journey-log.md に36エントリ・主要トピックは押さえている |
| 実践したこと | ◯ 90% | journey-log.mdに事実は残っている |
| つまづき | △ 70% | 失敗譚もあるがエントリにより粒度バラバラ |
| やっておくべきこと | △ 60% | 「次セッション冒頭で確認」項は機能、横断ベストプラクティスは未整備 |
| やってはいけないこと | △ 60% | feedback memory には溜まっているが教材形式では未整理 |
| **最終的にコンテンツにまとめられる状態** | **✕ 40%** | **ここが一番弱い**。蓄積はあるが取り出しと完成度可視化がない |

### 不足している主な点
1. 「コンテンツ候補」がjourney-log.md内に40件以上散在しているのに**横断検索/集計の仕組みがない**
2. **「コンテンツ完成度」のトラッキングがない**（どのテーマが記事化できる量に達したか分からない）
3. **過去5週間の蓄積（3/11〜4/24）がjourney-log.mdに埋もれたまま** — 既存ケーススタディは直近1週間の2本のみ
4. 記録の粒度がエントリごとにバラバラ
5. 社長が「ネタ出して」と言った時に即出せる窓口が不在

---

## 🚀 やってほしいこと（優先順位順）

### Phase 1（必須・5/31までに完了）

#### 1-A. 過去テーマ別ケーススタディの棚卸し新設
journey-log.md（36エントリ・2148行）から主要テーマを抽出して、テーマ別ケーススタディフォルダを新設する。**最低でも以下のテーマは独立したケーススタディとして整備**：

- `ebay-ad-optimization-case-study/` — eBay広告最適化プロジェクト（PLG/PLP/Offsite・3/26〜継続）
- `baychat-ai-reply-case-study/` — BayChat AI Reply プロンプトv2.2〜v2.6開発・設計図整備プロジェクト
- `asics-stock-tool-case-study/` — ASICS Bot検出格闘・v2.3修正・旧ツール復旧
- `weekly-report-case-study/` — eBay週次レポートv3 構築・GSheets移行
- `direct-sales-case-study/` — ダイレクト販売ツール本番デプロイ（NY顧客向け）
- `shiire-tool-case-study/` — 仕入管理表GAS Fulfillment API移行・clasp化
- `claude-code-setup-case-study/` — Claude Code初期セットアップ・セキュリティ・複数PC環境

**各ケーススタディの構造**（既存2本に倣う）:
```
<theme>-case-study/
  README.md     ← 目的・配信シナリオ案
  outline.md    ← 章構成テンプレート（Campers向け / 匿名X向け / Note向けの3軸）
  session-logs/ ← 当該テーマの過去journey-log該当部分を切り出して保存
  assets/       ← スクリーンショット・図表
```

**重要**: outline.md は `feedback_content_audience_framing.md` の3軸対応構造（Campers/X/Note）で書く。

#### 1-B. 横断 INDEX.md 作成
`education/campers/content-projects/INDEX.md` を新設し、全ケーススタディを以下の形で一覧化：

| ケーススタディ | テーマ | 蓄積素材量 | 完成度 | Campers向け | 匿名X向け | Note向け | 推奨配信 |
|---|---|---|---|---|---|---|---|
| ebay-ad-optimization | eBay広告最適化 | 大 | 80% | ◯ | ◯ | ◯（有料記事3本ぶん） | Campersウェビナー1コーナー＋Note 3本 |
| ... | ... | ... | ... | ... | ... | ... | ... |

完成度は「もう記事化できる」「あと○○の事例があれば書ける」「素材薄い」等を1〜100%で表現。

#### 1-C. 5/31 Campersウェビナー骨子の更新
- 既存草案 `education/consulting/webinar-draft-20260426.md` を確認
- 4/26 ウェビナー実施結果（成功・反省点）を社長から聞く必要があれば質問する（無人実行で進めるなら自分の知る範囲で素案を作り、社長確認に上げる）
- 5/31版の骨子を新規作成（or 4/26版を5/31版に更新）
- INDEX.md と連動させて「この素材を使う」を明示

### Phase 2（5/31以降・余裕があれば）

#### 2-A. journey-log.md 月次抽出の自動化
毎月1日に前月分の【コンテンツ候補】タグを抽出 → `content-projects/_candidates_<月>.md` に集約する仕組み。
- 既存 `biweekly-claude-maintenance` の延長として実装するか
- 独立した `monthly-content-extraction` タスクを作るか
- 設計判断は社長確認

#### 2-B. エントリ書式テンプレートの確定
journey-log.md の新規エントリ書式を統一（数値Before/After ／ 判断 ／ 学び ／ コンテンツ候補・配信形態案）。
- 既存4/24エントリ・4/28エントリが良い見本
- セッション終了時の追記時に必ずこのフォーマットを使うルール化
- ルール化は `memory/feedback_journey_log_format.md`（新設）に保存

#### 2-C. 匿名X→Note（Axis 2）の準備
- Axis 2 用の content-projects/ 配下サブツリー（例: `_axis2_anonymous/`）作成検討
- 匿名性確保のための語彙置換ルール（社長名・Reffort社名・スタッフ名・Chatworkルームid 等を伏せる）
- 着手は Axis 1（Campers）が一巡してから

---

## 🚫 やってはいけないこと

1. **配信判断・公開判断を勝手にすること** — 全て社長判断。Claudeから「記事化しますか？」と提案するのは禁止
2. **匿名X用素材から Campers/コンサルへの誘導を組み込むこと** — Axis 2 → Axis 1 誘導は社長の明示禁止事項
3. **BayChat内部の機密（プロンプト・設計図・Cowatech情報・スタッフ氏名）を匿名X/Note向け素材に含めること**
4. **過去エントリの本文を書き換えること** — journey-log.md の過去エントリは時系列史実。**新エントリの追記のみ**
5. **既存の運用中ファイルを動かすこと**（例: `memory/MEMORY.md` を勝手に大きく再構成）— 必要時のみ最小編集
6. **本タスクの最中に他の依頼を勝手に拡張実装すること** — 社長から別件の指示が来たら都度確認

---

## 📝 完了の定義

- ✅ 7テーマ以上のケーススタディフォルダが整備済み（README/outline/session-logs/assets）
- ✅ INDEX.md が完成し、3軸（Campers/X/Note）の完成度可視化がされている
- ✅ 5/31 ウェビナー骨子が最新版になっている
- ✅ 各ケーススタディの session-logs/ に**journey-log.md からの該当エントリの切り出し**が入っている（リンクではなく独立コピー、後から要約・再編集する素材として）
- ✅ MEMORY.md インデックスに新規作成memoryへのリンクが追加されている
- ✅ 本セッション終了時に journey-log.md に「2026-04-XX コンテンツ蓄積基盤整備セッション」エントリが追記されている

---

## 🔧 進め方の推奨

1. **まずINDEX.mdの素案を先に作る**（社長に方向性確認が早い）
2. journey-log.md を全部読み、テーマごとに素材を分類
3. テーマ別ケーススタディを並行で立ち上げ（README/outline は雛形でOK・session-logs に過去journey-logの該当部分をコピー）
4. INDEX.md を実データで埋める
5. 5/31骨子を更新
6. 完了報告 → journey-log 追記 → 引継ぎ完了

**作業中は社長から質問が飛んでくる前提で、進捗を毎所要時間ごとに簡潔に報告する**（前セッションで社長が「あと何分とか自分で言ってる割に放置」と指摘済み）。能動的にポーリング・更新する姿勢で進める。

---

## 📂 関連ファイル一覧

### 必読
- `CLAUDE.md`（ルート）
- `memory/MEMORY.md` → 関連 memory 全部
- `education/consulting/journey-log.md` — 全2148行・36エントリ
- `education/campers/CLAUDE.md` — Campers部門ルール
- `education/consulting/CLAUDE.md` — コンサル部門ルール

### 既存 content-projects（参考雛形として）
- `education/campers/content-projects/claude-code-maintenance-case-study/`
- `education/campers/content-projects/spreadsheet-automation-case-study/`

### 既存ウェビナー資料
- `education/consulting/webinar-draft-20260426.md`（4/26ウェビナー草案）

### 関連ツール仕様（必要時参照）
- `commerce/ebay/tools/gas-shiire-tool-spec.md`
- `commerce/ebay/analytics/CLAUDE.md`
- `services/baychat/ai/` 配下の handoff series

---

*作成: 2026-04-28（コンテンツ蓄積基盤整備引継ぎ）*
