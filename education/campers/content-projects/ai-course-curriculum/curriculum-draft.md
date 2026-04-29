# Campers AIコース 月額カリキュラム（v0.1 枠組み）

> Campersメンバー向けの**月額追加 AIコース**のカリキュラム設計。
> 単発講座ではなく、メンバーが**自分の業務をAI化していく過程を伴走する**継続的なコース。
>
> ⚠️ **本ファイルは枠組みドラフト**。料金・開始時期・具体的な運営フォーマットは社長判断待ち。

---

## コースのコンセプト

### 核心メッセージ
**「あなたが自分の業務をAI化できる状態になるまで、伴走します」**

### 背景
- Campersメンバーは eBay輸出継続者・全員プログラミング未経験
- 関税で売上ダメージ・新しい打ち手が見つからない状態
- 「Claude Code でAI化する」という新しいスキルを身につけることで：
  - 業務効率化（時間短縮・コスト削減）
  - スキルアップ（AI活用が新しい収入源にもなる可能性）
  - Campers 残留動機（「保険」ではなく「成長の場」へ）

### 狙う行動変容
- 「Claude Code は何だか難しそう」→「自分でも使える・自分の業務に活かせる」
- 単発で諦めるのではなく、**継続的に運用しながら改善できる**状態
- メンバー同士で事例共有・教え合いができる**コミュニティ機能**

---

## カリキュラム構成（全6単元・月1単元想定）

### Unit 1: Claude Code 導入と土台作り（1ヶ月目）

**目的**: Claude Code を自分のPCで動かし、自分の事業情報を反映した CLAUDE.md を整備する

**内容**:
- Claude Code とは何か・ChatGPT との違い
- インストール・初期セットアップ
- セキュリティルール（APIトークン.env管理）
- CLAUDE.md テンプレートを使った自分用設定
- セッション・メモリの仕組み

**成果物**:
- 自分のPCで Claude Code が動いている
- 自分の事業情報を反映した CLAUDE.md ができている
- journey-log.md を毎日書く習慣ができている

**素材**:
- `by-business-process/00-claude-code-foundation/`（README＋7ファイル全部）

---

### Unit 2: 業務棚卸しと最初の1個を選ぶ（1ヶ月目後半〜2ヶ月目）

**目的**: 自分の業務プロセスを11業務段階に当てはめ、最も効果のある「最初の1個」を選ぶ

**内容**:
- eBay運営の11業務段階の理解
- 自分の業務を当てはめる（業務棚卸しワークシート）
- ボトルネック特定（時間・コスト・ミス頻度）
- AI化優先度の付け方
- 「最初の1個」選定基準（毎日／定型／効果測定可能／失敗ダメージ小）

**成果物**:
- 自分の業務プロセス全体が可視化されている
- AI化優先度トップ3が決まっている
- 最初の1個（具体的なツール／自動化）が決まっている

**素材**:
- `by-business-process/00-claude-code-foundation/cases/03_claude-md-template.md`（業務プロセス優先度表）
- `INDEX.md`（業務縦軸ビュー）
- `by-business-process/01〜11/`（各業務段階のREADME）

---

### Unit 3: スプレッドシート活用（2〜3ヶ月目）

**目的**: ほぼ全員が使うスプレッドシートを Claude Code で操作できるようになる

**内容**:
- スプレッドシート自動化3型ルーティング（型A：GAS / 型B：Sheets API / 型C：Playwright）
- 型判定フローチャート
- 型A：GAS + clasp の実装
- 型B：Service Account + gspread の実装
- 型C：Playwright + cookie session の実装

**成果物**:
- 自分の業務スプレッドシートに自動メニュー or 自動更新が組み込まれている
- 失敗時に通知される仕組みが組み込まれている

**素材**:
- `cross-cutting-skills/external-integrations/cases/spreadsheet-automation.md`
- `by-business-process/05-procurement/cases/shiire-tool.md`（実例）

---

### Unit 4: API連携と外部ツール統合（3〜4ヶ月目）

**目的**: eBay API・Chatwork API 等を自分で叩いて業務統合できる

**内容**:
- eBay API（GetOrders / Marketing / Fulfillment）の概要
- OAuth2 認証の理解
- Chatwork / Slack / LINE Notify 等のチャット連携
- スケジュールタスク運用
- 失敗時通知の仕組み

**成果物**:
- 自分の業務で eBay API + Chatwork 等の連携が動いている
- 毎日／毎週の自動レポートが Chatwork等に届いている

**素材**:
- `cross-cutting-skills/external-integrations/cases/chatwork-mcp.md`
- `by-business-process/09-analytics/cases/weekly-report.md`（実例）

---

### Unit 5: 自動化スクリプト・自分専用ツール開発（4〜5ヶ月目）

**目的**: 自分の業務に最適化された専用ツールを自分で作って運用する

**内容**:
- 業務AI化の本格的な実装
- スクレイピング（必要な人のみ）
- 直取販売サイト等のWebアプリ（必要な人のみ）
- スタッフ運用フィードバックの取り入れ方
- 失敗・遠回りの記録と改善

**成果物**:
- 自分専用の業務ツールが2〜3個完成・運用中
- スタッフがいる人はスタッフが使える状態
- メンテナンスサイクルが確立

**素材**:
- `by-business-process/03-mukozai-stock-management/cases/stock-management-tool.md`
- `by-business-process/11-direct-sales/cases/direct-sales.md`
- `cross-cutting-skills/external-integrations/cases/scraping-strategy.md`

---

### Unit 6: 運用維持と次のステップ（6ヶ月目以降）

**目的**: AI運用を継続的に発展させ、新しい業務領域に展開できる

**内容**:
- 隔週メンテナンスの実施
- CLAUDE.md / memory の肥大化対策
- 新しい業務領域への展開
- メンバー同士の事例共有
- 「AI活用スキル」を新しい収入源にする可能性

**成果物**:
- 隔週メンテが運用に組み込まれている
- 月次でAI活用の成果を振り返れる
- メンバー同士で教え合える状態

**素材**:
- `by-business-process/00-claude-code-foundation/cases/06_maintenance-cycle.md`
- `archived-by-theme/claude-code-maintenance-case-study/`（社長の運用大改修事例）

---

## 運営フォーマット（社長判断）

### 候補1：月次ライブセッション + Chatwork 質問対応
- 月1回の Zoom／Google Meet ライブ（Unit内容を講義＋ワーク）
- 月内は Chatwork で質問対応
- メンバー同士の事例共有

### 候補2：録画講義 + 個別相談
- Unit ごとに録画講義（後から見返せる）
- 月1回の個別相談（30〜60分）
- Chatwork で随時質問

### 候補3：ハイブリッド
- 録画講義（基礎）
- 月1回ライブ（応用・質疑）
- Chatwork で随時質問
- 個別相談はオプション（追加料金）

---

## 料金設計（社長判断）

参考：
- Campers 既存月会費：約 ¥10,000/月
- AIコース月額追加（仮）：¥5,000〜¥20,000/月（社長判断）
- 個別相談オプション（仮）：¥10,000/回

---

## 開始時期（社長判断）

- 5/31 ウェビナーで案内
- 6月開始 or 7月開始
- 最初は10〜20名の少人数からスタート（運営回しながら改善）

---

## 配布素材

### 必須
- CLAUDE.md テンプレート
- 業務棚卸しワークシート
- 11業務段階の早見表
- 隔週メンテチェックリスト

### あれば良い
- スプレッドシート自動化3型の判定フローチャート
- 各Unit のスライド（PDF）
- メンバー専用 Chatwork ルーム

---

## メンバー成果の測定

- 月次：journey-log.md の蓄積量
- 月次：AI化した業務の数
- 月次：自動化による時間短縮（自己申告）
- 6ヶ月後：自分専用ツール完成数

---

## このコースで「金を巻き取る」感を出さないために

社長明言（2026-04-29）：
> 「金を巻き取ろうなんて思っていませんが、わたしが今 Claude Code であらゆることを AI化し人生が変わったことをメンバー達に教えることであらたな収入を作り、Campers脱退抑止に繋げたいと考えているわけです」

- 押し売り感を出さない
- 「払いたい」と感じてもらえる中身が前提
- 払えない人にも基礎情報は無料で提供（00-claude-code-foundation/ は無料公開検討）
- メンバーが成果を出せたら積極的に共有・他メンバーへの励みに

---

## 関連

- 5/31ウェビナー骨子: `webinar-materials/20260531-draft.md`
- INDEX: `INDEX.md`
- 関連 memory: `project_consulting.md` / `project_campers_webinar.md`

---

*作成: 2026-04-29（v0.1 枠組み）*
*更新: 料金・開始時期・運営フォーマット決定時*
