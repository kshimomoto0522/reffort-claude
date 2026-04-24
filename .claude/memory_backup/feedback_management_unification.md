---
name: 管理方法統一ルール（全重要ファイルをreffortへ集約）
description: memoryやスクリプトなど全重要ファイルをreffort/配下に集約しgit+GitHubで一元管理する原則ルール
type: feedback
originSessionId: 895e94b1-5256-4fcc-b9c4-8dd3ada2f186
---
# 管理方法統一ルール

2026-04-24 社長指示「基本的に管理方法は統一して」により確立。全ての重要ファイルは reffort/ 配下に集約し、バックアップ漏れゼロ・スマホ参照可能・PC故障時も復旧可能な状態を常に維持する。

## 原則（3層管理）

### 層1: reffort/ 配下のgit管理
- プロジェクトソース・スクリプト・設定ファイル
- 各部門CLAUDE.md・design-doc・handoff等
- **memoryスナップショット** (`.claude/memory_backup/`) ← 2026-04-24新設
- journey-log.md・weekly_history.json 等の実践記録

### 層2: 毎日深夜0時のGitHub自動バックアップ
- `daily-github-backup` タスクで reffort 全体を対象
- 2026-04-24以降は memory_backup も自動対象に拡張予定（竹案タスク15で自動同期化）
- コミット＆push まで自動

### 層3: リモートリポジトリ（Private）
- `github.com/kshimomoto0522/reffort-claude`
- スマホClaudeアプリからも参照可能（外出先・PC故障時も内容アクセス可）

## 絶対に守ること

1. **重要ファイルを reffort/ 配下以外に置かない**
   - 唯一の例外: Claude Code の memoryフォルダ（`~/.claude/projects/.../memory/`）。これは Claude Code 仕様で物理的に動かせないため、スナップショットを `.claude/memory_backup/` に同期する運用で統一
2. **新しいツール・スクリプト追加時は reffort/ 配下の適切な場所へ**
   - ダイレクト販売: `commerce/direct-sales/`
   - eBayツール: `commerce/ebay/tools/`
   - 経営横断: `management/`
   - 教育・コンサル: `education/`
3. **reffort 以外の場所にファイルを作る必要がある場合は必ず社長に確認**
4. **新しいmemoryを追加/更新したら `.claude/memory_backup/` への同期も意識**（自動化は竹案タスク15で完了予定）

## Why

2026-04-24、memoryフォルダが reffortの git管理外にあり GitHubバックアップされていないことが判明。社長指示で即統一。

統一する価値：
- バックアップ漏れゼロ（「reffortにあるもの＝バックアップ済み」）
- スマホから全情報参照可能（外出先・打ち合わせ中も確認可）
- PC故障時も復旧可能
- 運用ルールが単純化（考えることが減る）
- 将来のスタッフ・Claude新セッションも迷わない

## How to apply

- 毎日深夜0時の `daily-github-backup` が memory_backup も含めて push する仕組みに拡張（竹案タスク15）
- 新しいツール追加時は、「reffort配下のどこが適切か」を思考してから社長に提案
- memoryに記録したら `.claude/memory_backup/` への同期も意識（自動化済みなら自動反映）
- 「reffortに入っていれば確実に守られる」を全ての運用の前提とする
