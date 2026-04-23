# 高橋紗英 Claude Code 導入プラン

> 作成日: 2026-03-25 / 更新: 2026-03-26
> 作成者: Claude Code（社長の指示により準備）
> 目的: 高橋さんが自分のPCでClaude Codeを使い、段階的にAI活用スキルを身につける

---

## 1. 環境構成の全体像

```
【社長のPC — Max $100/月】              【高橋さんのPC — Pro $20/月】
reffort/ (フルアクセス)                  reffort/ (読み取り広く・編集は限定)
├── CLAUDE.md ←共有（読める）            ├── CLAUDE.md ←読めるが編集不可
├── ebay-analytics/ ←社長専用            ├── staff-ops/ ←メイン作業場
├── baychat-ai/ ←社長専用                ├── marketing/ ←マーケ作業場
├── baychat-product/ ←読み取りOK         ├── management/ ←経理アプリ等の開発場
├── .env（APIキー）←非共有              ├── .env なし（機密アクセス不要）
│                                       │
└── GitHub (Private repo) ──共有────→   └── GitHub clone
         ↑                                    ↓
    git pull で確認 ←──── Pull Request ←── git commit
```

**ポイント**:
- 同じGitHubリポジトリを共有するが、高橋さんは編集できるフォルダが限定される
- 社長のPC環境には一切触れない（完全に独立）
- **同時並行で作業可能**（社長はebay-analytics、高橋さんはstaff-opsなど）

---

## 2. サブスクリプション

| | **社長（現在）** | **高橋さん（新規）** |
|---|---|---|
| **プラン** | Max 5x | **Pro** |
| **月額** | $100 | **$20（約3,000円）** |
| **アカウント** | 社長のメール | s.takahashi2603@gmail.com |

**なぜTeamsプランではないか**: Teamsは最低5人必要（$125〜/月）。2人なら個別契約の方が安く、社長のMax枠も維持できる。

---

## 3. セットアップ手順

### Step 1: Claude.aiアカウント作成
1. https://claude.ai にアクセス
2. `s.takahashi2603@gmail.com` でアカウント作成
3. Claude Pro ($20/月) を契約

### Step 2: GitHubアカウント作成
1. https://github.com にアクセス
2. 同じメールアドレスでアカウント作成
3. 社長が `reffort-claude` リポジトリに **Write権限** で招待
   （Write権限が必要 = pushはできるが、PRベースで運用することで管理）

### Step 3: 高橋さんのPCに必要なものをインストール
1. **Node.js** — https://nodejs.org からLTS版をダウンロード・インストール
2. **Git** — https://git-scm.com からダウンロード・インストール
3. **VS Code** — https://code.visualstudio.com からダウンロード・インストール

### Step 4: Claude Code インストール
```bash
# 高橋さんのPCのターミナル（VS Codeのターミナルでも可）で実行
npm install -g @anthropic-ai/claude-code
```

### Step 5: リポジトリをクローン
```bash
cd ~/Desktop
git clone https://github.com/kshimomoto0522/reffort-claude.git reffort
```

### Step 6: 権限設定ファイルを配置
`takahashi-settings-template.json` の中身を高橋さんのPC上の
`reffort/.claude/settings.local.json` にコピー

### Step 7: 高橋さん専用CLAUDE.mdを配置
`takahashi-CLAUDE.md` を高橋さんのPC上の
`~/.claude/CLAUDE.md`（ユーザーレベル設定）にコピー

### Step 8: 初回ログイン・動作確認
```bash
cd ~/Desktop/reffort
claude
```
→ ブラウザが開くのでClaude.aiアカウント（高橋さんのメール）でログイン

---

## 4. 権限設計

### 読み取り（Read）— 全フォルダOK
高橋さんはリポジトリ内のほぼすべてのファイルを**読める**。
BayChat/BayPackの概要・機能・UIを理解した上で作業できる。

**ただし以下は読めない:**
- `.env`ファイル（APIキー・トークン等の機密情報）
- `services/baychat/ai/`（AI Replyプロンプト — 開発中の機密）

### 編集（Edit/Write）— 3フォルダのみ

| フォルダ | 用途 |
|----------|------|
| `commerce/ebay/staff-ops/` | 総務・マニュアル・手順書・雑務全般 |
| `services/baychat/marketing/` | BayChat/BayPackのSNS・プロモーション・競合分析 |
| `management/` | 経理アプリ・在庫管理アプリ・管理ツール開発 |

### プログラム実行 — OK
Python・Node.jsのスクリプト実行を許可（アプリ開発のため）

### Git操作

| 操作 | 許可 | 説明 |
|------|------|------|
| commit | ○ | 作業の記録 |
| pull | ○ | 最新の状態を取得 |
| push | △ | PRベースで運用（後述） |

---

## 5. 社長が高橋さんの作業を確認する方法

### 方法①: Pull Request（おすすめ）
高橋さんが作業完了 → PRを作成 → 社長がGitHub上で変更内容を確認 → OKならマージ

```
高橋: git checkout -b takahashi/inventory-app   ← 作業ブランチ作成
高橋: （作業する）
高橋: git commit -m "在庫管理アプリの初版作成"
高橋: git push origin takahashi/inventory-app
高橋: GitHub上でPull Requestを作成

社長: GitHub上でPRを確認 → 変更箇所が色付きで見える → OKならマージ
```

### 方法②: 社長のClaude Codeで確認
```
社長: git pull                     ← 高橋さんの変更を取得
社長: git log --author="takahashi" ← 高橋さんの作業履歴を表示
社長: git diff main..takahashi/xxx ← 差分を確認
```

### 方法③: GitHub（ブラウザ）で確認
- https://github.com/kshimomoto0522/reffort-claude にアクセス
- 「Pull Requests」タブで高橋さんの変更リクエストを確認
- 「Commits」で誰がいつ何を変更したか履歴が見える

---

## 6. 段階的な活用ロードマップ

### Phase 1: 基礎トレーニング（1〜2週間）
**作業場**: `commerce/ebay/staff-ops/`

| やること | 具体例 |
|----------|--------|
| Claude Codeの基本操作 | 質問の仕方・ファイル操作を覚える |
| 文書作成 | 報告書・メール下書き・議事録 |
| BayChat/BayPackの理解 | CLAUDE.mdやbaychat-product/を読んで事業を把握 |
| 手順書作成 | staff-ops/内で業務マニュアルの草案 |

### Phase 2: 総務・事務作業のAI化（2〜4週間）
**作業場**: `commerce/ebay/staff-ops/` + `management/`

| やること | 具体例 |
|----------|--------|
| アナログ資料のデジタル化 | 紙・Excel管理の情報を整理・構造化 |
| Excelデータの整理・集計 | 在庫表のクリーニング・フォーマット統一 |
| 経理関係の効率化提案 | 現状フローを整理→改善案をClaude Codeと作成 |
| Chatwork定型報告 | テンプレート化・半自動化 |

### Phase 3: アプリ開発（1〜2ヶ月後）
**作業場**: `management/`

| やること | 具体例 |
|----------|--------|
| 在庫管理アプリの試作 | スプレッドシート → Webアプリ化 |
| 経理ツールの試作 | 請求書管理・売上集計の簡易ツール |
| 要件定義・設計 | 社長と相談しながらClaude Codeで設計 |
| プロトタイプ → PRレビュー | 社長が方向性を確認 |

### Phase 4: マーケティング本格稼働（2〜3ヶ月後）
**作業場**: `services/baychat/marketing/`

| やること | 具体例 |
|----------|--------|
| SNS投稿の企画・下書き | BayChat/BayPackのプロモーション |
| 競合分析レポート | Web検索 → 分析 → レポート |
| LP・バナーのコピーライティング | Claude Codeで原稿作成 |
| データ分析 | SNS反応の分析→改善提案 |

---

## 7. セキュリティルール（高橋さん向け）

1. **APIキー・パスワードは絶対にClaudeに教えない**
2. **個人情報・顧客情報はClaudeに入力しない**
3. **作業はPull Requestベース**で社長のレビューを通す
4. **わからないことは社長に聞く**（Claudeが提案しても判断に迷ったら確認）
5. **Claudeの出力を鵜呑みにしない**（必ず内容を確認してから使う）

---

## 8. 社長がやること（チェックリスト）

### アカウント関連
- [ ] claude.ai で高橋さん用アカウント作成（s.takahashi2603@gmail.com）
- [ ] Claude Proプラン契約 ($20/月)
- [ ] GitHub で高橋さん用アカウント作成（同メール）
- [ ] reffort-claude リポジトリにWrite権限で招待

### 高橋さんのPC環境
- [ ] Node.js インストール
- [ ] Git インストール
- [ ] VS Code インストール
- [ ] Claude Code インストール（`npm install -g @anthropic-ai/claude-code`）
- [ ] リポジトリをクローン
- [ ] settings.local.json を配置（権限設定）
- [ ] 高橋専用CLAUDE.mdを配置

### 運用開始
- [ ] 基本操作のレクチャー（30分〜1時間）
- [ ] 最初の練習課題を出す
- [ ] PRベースの作業フローを教える

---

## 9. 想定コスト

| 項目 | 月額 | 備考 |
|------|------|------|
| Claude Pro（高橋さん分） | $20（約3,000円） | まずはこれで十分 |
| GitHub（Private repo） | $0 | 既存リポジトリを共有 |
| VS Code / Git / Node.js | $0 | すべて無料 |
| **合計** | **約3,000円/月** | |

---

## 10. 同時並行作業のイメージ

```
社長のPC（Claude Max）              高橋さんのPC（Claude Pro）
━━━━━━━━━━━━━━━━━━              ━━━━━━━━━━━━━━━━━━━━
ebay-analytics/ で                 staff-ops/ で
週次レポートの改善中                 業務マニュアル作成中
       ↓ 同時に作業OK ↓                    ↓
baychat-ai/ で                     marketing/ で
AI Replyプロンプト改善中             SNS投稿の下書き作成中
       ↓                                   ↓
   git push                          Pull Request
       ↓                                   ↓
   GitHub に統合 ←──────────────── 社長がレビュー → マージ
```

**Coworkは不要。** それぞれのPCでClaude Codeを独立して使い、GitHubで統合する方式。

---

*社長の承認後に実行に移します。*
*関連ファイル: takahashi-settings-template.json / takahashi-CLAUDE.md*
