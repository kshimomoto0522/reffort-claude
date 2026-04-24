---
name: Claude Code運用の持続可能性ルール（4点セット＋隔週メンテ）
description: Claude Codeの肥大化を防ぎ最新情報を取り込むための運用ルール。archive・biweekly-maintenance・index.md・/隔週メンテナンス＋Progressive Disclosure＋コンテンツ素材化
type: feedback
originSessionId: 895e94b1-5256-4fcc-b9c4-8dd3ada2f186
---
# Claude Code運用の持続可能性ルール

2026-04-23〜24のリファクタで確立した、Claude Codeを永続的に最高パフォーマンスで動かすための運用ルール。

## 持続可能性4点セット（全て揃って初めて機能する）

### ① archive/ フォルダで完了情報を退避
- 全部門に `archive/` 配下を新設
- 完了プロジェクト・古いバージョン・過去ログは**削除せず**ここへ退避
- Claudeは archive/ を**原則読まない**（明示指示時のみ）
- 情報資産保全とコンテキスト軽量化を両立
- ルートCLAUDE.md に「archive/ は読まない」宣言を明記

### ② biweekly-claude-maintenance 隔週タスク
- **第1・第3月曜 10:00** 自動実行
- スクリプト: `management/md-audit/biweekly_maintenance.py`
- 機能:
  1. 現状計測（全CLAUDE.md・memory・settings等の行数推移・前回比付き）
  2. 5層の最新情報調査: 公式・Boris Cherny・GitHub Trending・コミュニティ事例・事業側変化
  3. 松竹梅改善提案
  4. Chatwork個人DM(426170119)に `[info][title]📊 隔週Claude Codeメンテナンス[/title]...[/info]` 形式で通知
  5. `management/md-audit/reports/YYYY-MM-DD.md` にログ蓄積

### ③ 各部門 index.md で退避ファイル一覧を管理
- 各部門に `index.md` を配置
- 「常時ロード」「必要時ロード」「archive/参照なし」の3層で可視化
- 新規退避が発生した時、更新すべきは index.md 1ファイルだけ → 探索コスト常に一定

### ④ `/隔週メンテナンス` スラッシュコマンド
- `.claude/commands/隔週メンテナンス.md` 配置
- 挙動: Chatwork DM読み込み → 提案再提示 → 社長判断 → 実行 → 結果再送信
- Claude Code 1コマンドで改善サイクルが回る半自動フロー
- 実行過程は全て `education/campers/content-projects/claude-code-maintenance-case-study/session-logs/YYYY-MM-DD.md` に蓄積

## Progressive Disclosure 実装ルール（Anthropic公式・Boris Cherny準拠）

- **CLAUDE.md は各ファイル200行以下**（推奨60〜150行・HumanLayerは60行）
- CLAUDE.mdに全部書かず「**どこに書いてあるか**」だけ書く
- 詳細は退避先ファイル（ad-strategy.md・suppliers.md・features-spec.md等）で必要時ロード
- `.claude/rules/` への外部化を徹底
- 200行超過は即分割 or archive/ 移動

## effort_booster.py チューニングルール

- `OPT_IN_KEYWORDS`（社長明示）: 「しっかり」「ちゃんと」「じっくり」「徹底的」「ベストで」「!max」「ultrathink」等 → 残す
- `COMPLEX_KEYWORDS`（2個以上ヒットで自動ブースト）: **日常語NG・専門語OK**
  - ✅OK: アーキテクチャ・リファクタリング・ボトルネック・トレードオフ・戦略的・中長期・経営判断・マイグレーション・複雑度
  - ❌NG: 分析・検証・判断・バグ・エラー・方針・比較・改善・なぜ・原因（2026-04-23に削除済み）
- 社長が本当に深思考を要する時は OPT_IN で明示することでカバー可能

## 全作業のコンテンツ素材化

- 診断・改善・失敗・復活の全過程を `education/campers/content-projects/claude-code-maintenance-case-study/session-logs/YYYY-MM-DD.md` に蓄積
- 7章構成の執筆骨子テンプレート（`outline.md`）を使用
- 配信計画・記事公開・X投稿・動画制作等は**社長判断で別途実施**（勝手に公開しない）
- `feedback_content_recording.md` の原則と整合

## 肥大化の兆候（早期発見のチェックリスト）

以下が現れたら即メンテ:

1. 「Claudeが一度言ったことを守らない」「指示を忘れる」
2. 「回答が浅い・バカ」「嘘をつく（確認せず報告）」
3. レスポンスが遅い・トークン消費が激しい
4. 単純な指示でも extended thinking が長時間回る
5. git status に大量の `??` が出る
6. `ls` / `grep` のたびに Claude が正本でない中間ファイルにヒットして混乱

→ これらが出たら **/隔週メンテナンス** を即実行、または 4点セットが欠けていないか確認

## なぜこのルールが必要か

**Why:** 2026-04-23、社長から「Claude Codeが遅く・浅く・嘘をつく」と強い不満表明。3エージェント並列診断で肥大化が真因と特定。「再編成前から蓄積された肥大化」が臨界点を超えていた。受動的な監視では Claude Code の進化に追随できない → 隔週で能動的に最新情報を取り込む仕組みが必要と判断。

**How to apply:**
- 新規CLAUDE.md追加時は200行以下を厳守。超過したら即分割 or archive/
- 古い情報は削除せず archive/ へ（情報資産は失わない）
- 隔週メンテで受け取った提案は新セッションで `/隔週メンテナンス` で実行
- 4点セットのいずれかが欠けると持続しない → セットで運用
- 全作業は `session-logs/` に蓄積（コンテンツ素材）。ただし公開判断は社長のみ
