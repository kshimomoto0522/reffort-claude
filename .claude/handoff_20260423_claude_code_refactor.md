# Claude Code リファクタ 竹案 引き継ぎ（2026-04-23 作成）

> **新セッションでの起動方法**:
> 新セッションを起動したら、最初にこう言ってください:
> ```
> @.claude/handoff_20260423_claude_code_refactor.md を読んで、竹案を実行してください
> ```
> 1行で本ドキュメント全体を引き継いで実行が始まります。

---

## 📋 本ドキュメントの目的

社長からの依頼（2026-04-23）により、Claude Code運用を**Anthropic公式ベストプラクティス準拠**に整える。梅案は前セッションで完了済み。本セッションで**竹案（構造改善・3〜4時間）**を実施する。

---

## 🔴 最優先：着手前に必ず読む「継続ルール」（社長からのフィードバック）

**竹案のどのタスクを始める前も、以下を必ず確認してから動いてください。社長が過去に明言した運用ルールであり、全セッションで前提となります。**

### A. 思考・口調・姿勢の最重要ルール（順不同で最重要）
1. `memory/feedback_tone_and_depth.md` — **敬語厳守・タメ口禁止・指摘される前に徹底的に考え抜く・最初から徹底版を出す**
2. `memory/feedback_proactive_partner.md` — **言いなり禁止・指示の目的を理解し先回り提案・経営を同じ目線で考える存在**
3. `memory/feedback_best_first_thinking.md` — **ハードル/コストで切り捨てず、ゴールから逆算したベストを松竹梅で提示**
4. `memory/feedback_declaration_to_implementation.md` — **「〜します」と宣言したら、その場でhook/task/scriptに落とすまで完了しない**
5. `memory/user_patterns.md` + `memory/user_profile.md` — **社長の思考パターン・プロフィール**

### B. 構造・運用の原則
6. `memory/feedback_claude_md_structure.md` — **CLAUDE.mdは100行以下のコアのみ。参照情報は`.claude/rules/`に分離**
7. `memory/feedback_communication.md` — **無駄なやりとり禁止・確認不足は嘘と同じ**
8. `memory/feedback_content_recording.md` — **AI運用の発見はSNS/Note/コンサル向けに記録**

### C. 「二度とするな」系ミス回避リスト（過去に実害が出た失敗）
9. `memory/feedback_asics_block.md` — ヘッドレスBot検出をIPブロックと誤認する繰り返しミス。無限監視ループ禁止
10. `memory/feedback_scheduled_task_execution.md` — できない処理をスキップして続行絶対禁止。イレギュラーは即中断・報告
11. `memory/feedback_task_activation.md` — 新規タスクは必ずアクティベートテスト→承認→本番プロンプト更新の3ステップ
12. `memory/feedback_security.md` — APIトークンは.env管理必須。コード直書き禁止
13. `memory/feedback_slack_rules.md` — Slack送信前GO厳守・スレッド構造（タイトル→ts→返信）厳守・勝手送信禁止
14. `memory/feedback_chatwork_rules.md` — AI宛てのメンション・返信のみ反応。それ以外スルー
15. `memory/feedback_chatwork_dm_format.md` — 個人DM(426170119)は必ず`[info][title]...[/title]...[/info]`の箱型カード形式
16. `memory/feedback_file_delivery.md` — 「フォルダに作りました」禁止。startコマンドで開くかエクスプローラーで見える状態
17. `memory/feedback_hp_publish_rule.md` — 本番HP変更はプレビュー→OK後に公開。勝手に押さない
18. `memory/feedback_server_deploy.md` — VPS失敗の教訓。事前調査・PaaS優先・社長に手作業させない
19. `memory/feedback_local_test_workflow.md` — ローカルテスト→社長OK→本番push。営業時間中push禁止
20. `memory/feedback_sku_required.md` — 商品言及時は必ず【SKU】タイトル形式
21. `memory/feedback_env_file_handling.md` — 機密情報はClaudeがファイル作成→社長が直接入力。チャット上での入力案内禁止
22. `memory/feedback_scheduled_task_sync.md` — スクリプト変更時はタスクプロンプトも必ず更新
23. `memory/feedback_checkpoint_first_design.md` — 定期タスクは処理より先にチェックポイント保存
24. `memory/feedback_scheduled_task_approval_cache.md` — 新規/改修タスクは「今すぐ実行」で承認焼き込み必須

### D. 進行中プロジェクトの前提
25. `memory/feedback_baychat_ai_reply_stance.md` — BayChat AI Reply 進行時の5原則（設計図理解前提・Cowatech前に自力解決・論点リスト機械消化禁止）

### ロード方法（Claudeへ）
新セッション起動時にMEMORY.md経由で自動ロードされるが、本ハンドオフを読んだ時点で**上記の該当ファイルは意識的に再確認**すること。特にA群（敬語・徹底・先回り・ベストから逆算・宣言は実装）は全てのタスクの前提として常に適用する。

---

## 🎯 前セッションの診断結果サマリー

### 症状（社長からの訴え）
> 「最近あきらかにClaude codeが一度言った通りにやらない、嘘をつく、言い訳をする、遅い、トークン消費が激しい、回答がバカ過ぎます」

### 真因（3本柱）
1. **カスケード・コンテキスト爆発**: 作業フォルダで親4層（ルート→services→baychat→ai）の全CLAUDE.mdが自動ロード。`services/baychat/ai/`で作業時に572行+rules150行+MEMORY.md61行 = 初期段階で5,000〜8,000トークン消費
2. **effort_booster過アグレッシブ** → 前セッションで修正済み
3. **ノイズファイル氾濫** → 前セッションで削除済み

### ベストプラクティス逸脱
- ルートCLAUDE.md 136行（推奨60〜150 ギリギリ）
- 子CLAUDE.md 最大488行（推奨200以下の**2.4倍**）
- 子CLAUDE.md 20ファイル中6ファイルが200行超（30%が逸脱）
- settings.local.json 298行（ワンオフallow列挙）
- memory 47ファイル合計2,385行

出典: [Anthropic公式ベストプラクティス](`C:\Users\KEISUKE SHIMOMOTO\Downloads\claude-code-best-practices.md`) / Boris Cherny Tips

---

## ✅ 前セッション（梅案）完了内容

| # | 作業 | 結果 |
|---|------|------|
| 1 | effort_booster.py COMPLEX_KEYWORDS厳選 | 20+語→16語・日常語削除・次回プロンプトから軽量化 |
| 2 | tools配下ノイズ77個削除 | 約840KB削減・視認性改善 |
| 3 | scrape_data.exe_extracted/ 削除 | 190MB削減 |
| 4 | CLAUDE.md.backup_20260403, error.log, error_adidas.log削除 | 130KB削減 |
| 5 | 空ebay-tools/フォルダ削除 | 再編成置き土産解消 |
| 6 | pyinstxtractor.py削除 | 不要ツール撤去 |
| 7 | .gitignore強化（一時ファイルパターン追加） | 再発防止 |
| 8 | commerce/direct-sales/CLAUDE.md:95 旧パス修正 | デプロイ事故防止 |

---

## 🛡️ 絶対に触らない情報資産リスト（保護対象）

**どのタスクでも以下ファイルは一切変更しない・削除しない**:

| ファイル | 場所 | サイズ | 理由 |
|---------|------|--------|------|
| journey-log.md | education/consulting/ | 123KB・毎日更新 | 日々のジャーニー蓄積 |
| decisions_log.md | memory/ | 182行 | 経営判断ログ |
| decision-log.md | management/monetization-portfolio/ | - | 収益化判断 |
| user_patterns.md | memory/ | 114行 | 社長の思考パターン |
| user_profile.md | memory/ | 61行 | 社長プロフィール |
| weekly_history.json | commerce/ebay/analytics/ | - | 週次レポート履歴 |
| weekly_history_backup_20260326.json | commerce/ebay/analytics/ | - | 履歴バックアップ |
| webinar_20260426.pptx/pdf | education/consulting/ | - | ウェビナー成果物 |
| design-doc/ 全体 | services/baychat/ai/ | - | AI Reply設計図v0.2 |
| handoff_*.md 全て | services/baychat/ai/ 等 | - | セッション引き継ぎ履歴 |
| memory/ 配下47ファイル全て | - | 2,385行 | フィードバック・プロジェクト記録 |

---

## 🛠️ 竹案タスク一覧（チェックボックス付き）

**原則**: 各タスクごとに `git commit` で区切り、社長がいつでも `git log` で戻せる状態を維持。

### □ タスク1: ルートCLAUDE.md圧縮（136行→80行以下）
**ファイル**: `CLAUDE.md`
**方針**: `.claude/rules/` と重複している記述・自明な記述を削除
**削除候補**:
- 「Claudeへの期待役割」5項目（user_profile.mdと重複）
- 「Effort Level運用」詳細（設定で完結しており説明不要）
- 「セッション終了時チェックリスト」は簡潔化（5行程度に）
- 「自動タスク管理ルール」は表のみに圧縮

**保持すべき**:
- 社長プロフィール（短縮版）
- 重要ルール（本番データ確認・APIレート制限・日本語コメント）
- セッション終了チェックリスト（journey-log更新・memory保存）
- 自動タスク一覧（表形式）

### □ タスク2: commerce/ebay/analytics/CLAUDE.md（488行→200行）
**ファイル**: `commerce/ebay/analytics/CLAUDE.md`
**方針**: 広告戦略等の詳細を別ファイルに退避（**内容は失わない**）
**退避先新規作成**:
- `commerce/ebay/analytics/ad-strategy.md`（広告戦略詳細）
- `commerce/ebay/analytics/suppliers.md`（仕入先詳細・HIROUN含む）
- `commerce/ebay/analytics/tools-list.md`（使用ツール・スプレッドシート一覧）

**CLAUDE.mdに残す**:
- 事業概要（要点のみ表）
- スタッフ体制（名前・役割名のみ）
- 各退避ファイルへのポインタ

### □ タスク3: services/baychat/ai/CLAUDE.md（419行→200行）
**ファイル**: `services/baychat/ai/CLAUDE.md`
**方針**: 機能詳細・ユーザー数トレンドを別ファイルに退避
**退避先新規作成**:
- `services/baychat/ai/features-spec.md`（主要機能詳細）
- `services/baychat/ai/user-growth.md`（ユーザー数・売上トレンド）

**CLAUDE.mdに残す**:
- サービス概要（要点のみ）
- AI Reply プロジェクトの現状サマリー
- 各退避ファイルへのポインタ
- design-doc/ への導線

### □ タスク4: commerce/ebay/tools/CLAUDE.md（296行→200行）
**方針**: 「日本語パス問題」等の解決済み履歴を削除。詳細マニュアルを別ファイルに
**退避先**:
- `commerce/ebay/tools/development-history.md`（解決済み履歴・経緯）
**CLAUDE.mdに残す**: 現行ツール一覧・開発優先順位・コード更新手順（2026-04-22実証済み手順）

### □ タスク5: management/monetization-portfolio/CLAUDE.md（249行→150行）
**方針**: 長い事業分析記述を別ファイル化
**退避先**: `management/monetization-portfolio/portfolio-analysis.md`

### □ タスク6: settings.local.json のワイルドカード化（298行→60-80行）
**ファイル**: `.claude/settings.local.json`
**方針**: ワンオフコマンドをワイルドカードに統合
**統合パターン例**:
- `Bash(py :*)` ← py系全部
- `Bash(python :*)` ← python系全部
- `Bash(python3 :*)` ← python3系全部
- `Bash(powershell :*)` ← powershell系全部
- `Bash(schtasks :*)` ← schtasks系全部
- `Bash(curl :*)` ← curl系全部
- `Bash(gh :*)` ← gh系全部
- `Bash(npm :*) / Bash(npx :*) / Bash(node :*)` ← Node.js系
- `WebFetch(domain:*)` は個別維持（セキュリティ上）

**重要**: deny配列（env読み取り禁止・force push禁止等）は**一切変更しない**

### □ タスク7: memory/ 重複統合
**方針**: 冗長なfeedbackを統合。内容は失わず、重複箇所のみ排除
**統合候補**:
- `feedback_baychat_ai_reply_stance.md` (99行) → `decisions_log.md` へ吸収（2026-04-20 のBayChat関連エントリと重複）
- `feedback_communication.md` (131行) の古い2026-03月インシデント記述 → 簡潔化（Hooksで機械防止済みのものは削除可）
- `project_asics_tool.md` (119行) → ASICSツール作業が一段落したら `project_archive/` 新設して移動
- `MEMORY.md` の index を整理（統合後のファイル名に合わせる）

**やってはいけないこと**:
- ファイル内容の**意味を変える**統合（単純マージのみOK）
- 「冗長」と感じても情報資産（decisions_log.md・user_*.md）の本体を削らない

### □ タスク8: commerce/direct-sales/data/backup_*/ のgit除去
**方針**: git追跡済みバックアップをリポジトリから除去（ローカル残す選択可）
**手順**: `git rm -r --cached commerce/direct-sales/data/backup_*/` でコミット

### □ タスク9: 追跡済みGAS中間物のgit除去
**対象**: `commerce/ebay/tools/` の追跡済み中間物
- `_gas_b64.txt`, `_gas_b64_0.txt` 〜 `_gas_b64_4.txt`
- `_inject.js`
- `gas_b64_temp.txt`
- `gas_shiire_b64.txt`
- `gas_shiire_content.json`

**手順**: `git rm --cached <files>` でリポジトリから除外。ローカルは.gitignoreで守られる

### □ タスク10: 全部門に `archive/` フォルダを新設（持続可能性の柱①）
**目的**: 完了済み・古い情報は削除せず `archive/` へ退避。Claudeは原則archive/を読まない（明示的指示時のみ）
**対象フォルダ**（新規作成）:
- `commerce/ebay/analytics/archive/`
- `commerce/ebay/tools/archive/`
- `services/baychat/ai/archive/`
- `services/baychat/product/archive/`
- `services/baychat/marketing/archive/`
- `management/monetization-portfolio/archive/`
- `education/consulting/archive/`

**各archive/ 直下に `README.md` を配置**:
```markdown
# archive/ 配下のルール
- ここに置かれたファイルはClaudeが通常のセッションで参照しません
- 完了済みプロジェクト・古いバージョン・過去ログの保存場所
- 削除はしない。情報資産として保全
- 必要な時は社長が明示的に「archive/○○.md を読んで」と指示
```

**CLAUDE.md（ルート）に以下1行追加**:
```
## archive/ は読まない
全フォルダの `archive/` 配下は、社長から明示的に指示されない限りClaudeは読み込まない。
```

### □ タスク11: `biweekly-claude-maintenance` 隔週メンテナンス新設（持続可能性の柱②）
**目的**: 隔週で「肥大化監視＋Claude Code最新情報取り込み＋改善提案」を自動送信。受動監視ではなく能動進化へ。
**スクリプト作成場所**: `management/md-audit/biweekly_maintenance.py`（新規）
**スケジュール**: **第1・第3月曜 10:00**
**タスク名**: `biweekly-claude-maintenance`
**アクティベートテスト必須**（feedback_task_activation.md 準拠）

#### 機能（5層調査＋松竹梅提案）
1. **現状計測（前回比付き）**
   - 全プロジェクト配下の `*.md` 行数走査（archive/除外）
   - settings.local.json の allow 行数
   - memory/ のファイル数・合計行数
   - hooks の動作ログサマリー（effort_booster.log の発火件数等）
   - 前回レポートとの差分（増減）
   - 3段階分類（🟢正常 ≤200行 / 🟡警告 201-300行 / 🔴超過 301行以上）

2. **5層の最新情報調査**（WebSearch/WebFetchで自動取得）
   - **層1: 公式** — `code.claude.com/docs` / Anthropic Changelog の直近2週間更新
   - **層2: 開発者Tips** — Boris Cherny（Claude Code開発者）の直近のX投稿・ブログ
   - **層3: 高評価実例** — shanraisshan/claude-code-best-practice 等 GitHub Trending の更新
   - **層4: コミュニティ事例** — HumanLayer Blog / Level Up Coding / Medium の Claude Code 関連記事
   - **層5: 事業側変化** — eBay API / BayChat Cowatech側の変更 / Gemini・GPT モデルの新版情報

3. **改善提案（松竹梅）** — 調査で得た情報をこのプロジェクトに適用可能な形で整理、工数・効果・リスク明記

4. **Chatwork個人DM(426170119)へ送信** — feedback_chatwork_dm_format.md 準拠の `[info][title]...[/title]...[/info]` 箱型カード形式

5. **実行ログ保存**
   - `management/md-audit/audit_log.csv` に推移記録
   - `management/md-audit/reports/YYYY-MM-DD.md` に詳細レポート保存

#### Chatwork通知テンプレ（参考）
```
[info][title]📊 隔週Claude Codeメンテナンス（YYYY-MM-DD）[/title]
【現状】前回比
・ルートCLAUDE.md: 80行（±0）🟢
・analytics/CLAUDE.md: 205行（+5）🟡
・settings.local.json: 65行（+3）🟢
・memory: 32ファイル（+1）🟢

【最新動向（過去2週間）】
・Anthropic公式: ○○○
・Boris Cherny: ○○○
・GitHub Trending: ○○○
・コミュニティ: ○○○
・事業側: ○○○

【今回の提案（松竹梅）】
🥇 推奨: ○○○（工数1h・効果大）
🥈 次案: ○○○（工数3h・効果中）
🥉 後で: ○○○（工数30min・効果小）

新セッションで「/隔週メンテナンス」→ 判断→実行
[/info]
```

### □ タスク12: 各部門に `index.md` 新設（持続可能性の柱③）
**目的**: 各フォルダ配下の退避ファイル一覧を明示。Claudeも社長も「何がどこにあるか」即把握
**配置例**: `commerce/ebay/analytics/index.md`
```markdown
# commerce/ebay/analytics/ ファイル一覧

## 常時ロード
- `CLAUDE.md` ... 事業概要・運用ルール（毎セッション自動ロード）

## 必要時ロード（退避ファイル）
- `ad-strategy.md` ... 広告戦略詳細（PLG/PLP/Offsite）
- `suppliers.md` ... 仕入先情報（HIROUN・メイン20サイト等）
- `tools-list.md` ... 使用ツール・スプレッドシート一覧

## 参照なし（archive/）
- `archive/` 配下は参照しない（明示指示時のみ）
```

**新規配置先**:
- `commerce/ebay/analytics/index.md`
- `commerce/ebay/tools/index.md`
- `services/baychat/ai/index.md`
- `services/baychat/product/index.md`
- `management/monetization-portfolio/index.md`

各 CLAUDE.md の冒頭に **`詳細ファイル一覧: index.md を参照`** の一行を追加。

**効果**: 新規退避が発生した時、追加で更新すべきは `index.md` 1ファイルだけ。探索コストが常に一定に保たれる。

### □ タスク13: `/隔週メンテナンス` スラッシュコマンド作成（持続可能性の柱④）
**目的**: 隔週タスクのChatwork通知を受けて、社長がClaude Codeで1コマンド実行するだけで改善サイクルを回せる半自動フロー
**配置**: `.claude/commands/隔週メンテナンス.md`（新規）

#### コマンド実行時の挙動
1. **直前のChatwork個人DM読み込み**
   - `mcp__chatwork__list_room_messages` で room_id 426170119 の直近1週間を取得
   - `📊 隔週Claude Codeメンテナンス` タイトルの最新メッセージを抽出
2. **提案の再提示** — Chatworkで送った松竹梅提案をセッション内で再表示、社長に「どれを採用しますか？」と判断を仰ぐ
3. **実行** — 社長が選んだ案を実行（複数選択可）。過程は全てログに残す（コンテンツ素材）
4. **結果通知** — 実行完了後、Chatwork個人DMに「実行完了・変更点サマリー」を再送信（議事録化）

#### ファイル内容の骨組み（`.claude/commands/隔週メンテナンス.md`）
```markdown
---
description: 隔週Claude Codeメンテナンスの半自動実行。Chatwork個人DMの最新提案を読み、社長判断の上で実行する。
---

# 隔週Claude Codeメンテナンス 実行

以下の手順で実行してください：

1. Chatwork個人DM(room_id: 426170119)から直近の `📊 隔週Claude Codeメンテナンス` メッセージを読み込む
2. そのメッセージに含まれる松竹梅提案をセッションに再提示
3. 社長に「どれを採用しますか？」と確認（複数選択可）
4. 選ばれた案を実行
5. 実行完了後、Chatwork個人DMに結果通知（[info][title]...[/title]...[/info]形式）を送信

**重要**: 実行過程の全記録は `education/campers/content-projects/claude-code-maintenance-case-study/session-logs/YYYY-MM-DD.md` にも保存する（Campersコンテンツ素材として蓄積）。
```

### □ タスク15: `daily-github-backup` 拡張＋memory自動同期（管理方法統一の完成）
**目的**: 2026-04-24 社長指示「管理方法は統一」を完遂。memoryフォルダのスナップショットを `.claude/memory_backup/` に毎日自動同期し、GitHub一元バックアップを確立する。
**背景**: 2026-04-24時点で `.claude/memory_backup/` への初回コピー＋コミットは完了済み。ただし「自動同期」は未実装。手動同期が必要な状態を自動化する。

#### 実施内容
1. **`daily-github-backup` スクリプトを拡張**
   - 現状対応範囲: reffortフォルダ全体（CLAUDE.md系中心）
   - 拡張内容: スクリプト冒頭で以下を実行してから git add/commit/push
     ```python
     import shutil
     from pathlib import Path
     SRC = Path.home() / ".claude/projects/C--Users-KEISUKE-SHIMOMOTO-Desktop-reffort/memory"
     DST = Path(__file__).parent.parent / ".claude/memory_backup"
     DST.mkdir(parents=True, exist_ok=True)
     # 削除対応のため DST を一旦クリアしてから同期
     for f in DST.glob("*.md"):
         f.unlink()
     for f in SRC.glob("*.md"):
         shutil.copy2(f, DST / f.name)
     ```
2. **scheduled-tasks MCP の `daily-github-backup` プロンプトも更新**
   - 実行前の memory同期処理を明示
   - feedback_scheduled_task_sync.md 準拠（スクリプト変更時はタスクプロンプトも必ず更新）
3. **アクティベートテスト必須**（feedback_task_activation.md 準拠）
   - 「今すぐ実行」で memory同期→git add→commit→push まで通ることを確認
   - 差分が出た場合のみコミット（変更がない日はスキップ）
4. **CLAUDE.md（ルート）の「自動タスク一覧」を更新**
   - `daily-github-backup` の対象範囲を「reffortフォルダ＋memory同期」に書き換え

#### 検証基準
- memoryに新規ファイル追加→翌日深夜0時に自動で memory_backup に反映＆GitHub push
- memoryファイル削除→翌日深夜0時に memory_backup からも削除反映＆push
- スマホClaudeアプリから最新のmemory内容が参照できる

#### 関連メモリ
`memory/feedback_management_unification.md`（2026-04-24新規・3層管理原則）

---

### □ タスク14: Campersコンテンツ素材の骨組み作成（配信スケジュールは対象外）
**目的**: 「Claude Code失敗→診断→復活→永続メンテ」の記録を生徒向けコンテンツ素材として蓄積する骨組み作り。**社長判断により配信カレンダー・実行スケジュール・配信チャネル別タイミング等は本タスクの対象外（別途社長判断）。**

#### 実施内容（骨組み＋初期素材のみ）
1. **フォルダ新設**: `education/campers/content-projects/claude-code-maintenance-case-study/`

2. **配置するファイル**（全て骨組みテンプレとして作成・中身は段階的に蓄積）
   - `README.md` — 本プロジェクトの目的・社長方針（**「配信タイミングは社長判断・本プロジェクトは素材蓄積のみ」を明記**）
   - `outline.md` — 7章構成の執筆骨子テンプレート
   - `session-logs/` — 各メンテサイクルのセッションログ保存フォルダ
     - `2026-04-23_initial-diagnosis.md` — **本日のセッションを第一素材として保存**（3エージェント調査結果・診断数字・削除ファイルリスト・社長との対話要点・梅案/竹案設計の全過程）
   - `assets/` — スクリーンショット・before/after図表の保存先

3. **7章構成（outline.md の内容）**
   - 第1章: 症状の自覚（社長本人の言葉＋セルフチェック表）
   - 第2章: 診断プロセス（3エージェント並列ワークフロー）
   - 第3章: 真因特定（肥大化・hook・ノイズのファクト）
   - 第4章: 即効解毒（梅案5項目）
   - 第5章: 構造改善（竹案・Progressive Disclosure実装）
   - 第6章: 永続仕組み（archive/・隔週メンテ・index.md・/隔週メンテナンスコマンド）
   - 第7章: 受講生への提言

4. **隔週メンテ・スラッシュコマンド実行の全記録も本フォルダに自動蓄積**（タスク13で配置済み）

**⚠️ 重要**: 本タスクは「素材の器を作り、第一素材を入れる」ところまで。配信スケジュール・記事執筆・動画制作・チャネル別タイミングは社長判断で別途。勝手に記事公開やX投稿等はしない（feedback_hp_publish_rule.md・feedback_slack_rules.md の精神準拠）。

---

## 🔄 持続可能性の4点セット（タスク10-14の意義）

竹案タスク10-12は、社長の本質的な懸念「退避ファイルが増え続けて破綻しないか」への答えです。

| 仕組み | 効果 |
|--------|------|
| archive/ | 完了情報を「削除せず Claude から見えない位置」に退避。情報資産保全×コンテキスト軽量化 |
| biweekly-claude-maintenance | 肥大化監視＋Claude Code最新情報を能動取り込み。隔週でChatworkへ提案 |
| index.md | 退避ファイルが増えても「どこに何があるか」が1ファイルで把握できる |
| /隔週メンテナンス | Chatwork通知→Claude Code 1コマンドで改善サイクル回せる半自動フロー |

**この4点セットを竹案と同時に実装することで、今後10年間肥大化を防ぎながら、Claude Code側の進化も取り込み続ける運用基盤が完成します。さらに全実行記録はCampersコンテンツ素材として蓄積されます（タスク14）。**

---

## 📏 検証基準（竹案完了の定義）

実施後に以下が全て満たされていればOK:

- [ ] ルートCLAUDE.md が **80行以下**
- [ ] 全ての子CLAUDE.mdが **200行以下**
- [ ] settings.local.json allow が **80行以下**
- [ ] memory ファイル数が **35以下**に減少（情報は退避先に保全）
- [ ] 情報資産リスト（保護対象）が一切変更されていない（`git diff` で確認）
- [ ] 退避先ファイル（ad-strategy.md等）が全て作成されている
- [ ] `git status` がクリーン、または意図的な変更のみ

---

## 🚦 実施手順（新セッション初手）

### Step 1: 現状スナップショット
```bash
cd "C:/Users/KEISUKE SHIMOMOTO/Desktop/reffort"
git status
git log --oneline -5
```
未コミット変更があれば社長に「梅案の結果をコミットしますか？」と確認してからコミット

### Step 2: タスク1から順次実施
1タスクごとに:
1. 変更前の行数を記録（`wc -l <file>`）
2. 退避先ファイル作成 → CLAUDE.md圧縮
3. 検証（行数確認・ポインタが正しく張れているか）
4. git commit（メッセージ例: `竹案T1: ルートCLAUDE.md圧縮 136→72行`）
5. 社長に簡潔報告（before/after数字）

### Step 3: 全タスク完了後、最終検証
- コンテキスト計測: ルートCLAUDE.md + rules/ + MEMORY.md の合計行数
- before/after 表を作成して社長に報告

### Step 4: CLAUDE.mdに「次に読むファイル」更新
現状の「🚨 次セッション冒頭で必ず読むファイル」セクションを今の状況に合わせて更新

---

## ⚠️ 重要な制約条件

### 社長のfeedback(memory参照)
- **feedback_tone_and_depth.md**: 敬語厳守・徹底的に考え抜く・最初から徹底版
- **feedback_proactive_partner.md**: 言いなり禁止・先回り提案
- **feedback_best_first_thinking.md**: ベストから逆算・松竹梅提示
- **feedback_declaration_to_implementation.md**: 宣言は実装とセット
- **feedback_claude_md_structure.md**: CLAUDE.md は100行以下のコアルールのみ

### 作業原則
- **情報は失わない**: 圧縮は「削除」ではなく「別ファイルへの退避」
- **1タスクずつコミット**: 各タスク完了時にgit commit
- **社長確認を挟む**: タスク2・タスク6・タスク7・タスク11 のような影響大の作業は**実施前に草案を見せてGOを取る**
- **疑問があれば聞く**: 勝手に進めず社長に確認（feedback_claude_md_structure.md 参照）
- **継続ルール（最優先セクション）は全タスクで常時適用**: 敬語厳守・徹底・先回り・ベストから逆算・宣言は実装・SKU付き言及 等は例外なく守る
- **ミスをしたら**: 言い訳せず短く謝罪→即修正→memoryに「二度としないミス」として記録追加
- **全作業はコンテンツ素材として扱う**: feedback_content_recording.md 準拠。診断・改善・失敗・復活の全過程を `education/campers/content-projects/` 配下に蓄積（タスク14で仕組み化）。**ただし配信タイミング・記事公開・X投稿等は社長判断で別途実施、勝手に公開しない**

---

## 📚 参照ドキュメント

- ベストプラクティス: `C:\Users\KEISUKE SHIMOMOTO\Downloads\claude-code-best-practices.md`
- 前セッションの詳細ログ: 現セッションの会話履歴（このhandoff作成時点）
- プロジェクト構造: `.claude/rules/project-structure.md`

---

## 🎁 期待効果（竹案完了時）

| 指標 | 現状 | 竹案後 | 削減率 |
|------|------|--------|-------|
| 初期コンテキスト消費 | 5,000-8,000トークン | 2,500-4,000 | **約50%減** |
| ルートCLAUDE.md | 136行 | 80行以下 | 40%減 |
| 最大子CLAUDE.md | 488行 | 200行以下 | 60%減 |
| settings.local.json | 298行 | 60-80行 | 75%減 |
| Claudeのレイテンシ | 重い | 軽い | 30-40%改善 |
| 社長の体感 | 「遅い・バカ」 | 「元のパフォーマンス回復」 | - |

---

**本ハンドオフは前セッションの引き継ぎです。ご質問があればこのドキュメント全体を理解した上でお答えします。**
