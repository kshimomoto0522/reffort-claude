---
name: 高橋紗英 Claude Code導入プロジェクト
description: 高橋さんへのClaude Code環境共有・段階的AI活用の計画と進捗
type: project
originSessionId: 0d7c28b6-6829-45d7-9b15-ae3dcb635117
---
## 概要
社長が高橋さんにClaude Codeを使った業務を段階的に任せる計画。2026-03-25に準備開始。

**Why:** 高橋さんは総務・マーケ担当だが、現状は具体的な指示待ち状態。Claude Codeを活用させることで自律的に動ける体制を作り、将来的にはマーケティング・プロモーションのメイン担当にしたい。

**How to apply:**
- 高橋さんに関する作業依頼があった場合、このプロジェクトの文脈を踏まえて対応する
- 権限設定・セキュリティルールを尊重する
- 段階的なロードマップ（Phase1〜4）に沿って進める

## 作成済みファイル
- `commerce/ebay/staff-ops/takahashi-claude-code-plan.md` — 全体プラン（社長確認用）
- `commerce/ebay/staff-ops/takahashi-settings-template.json` — 権限設定テンプレート（2026-04-15 effortLevel:high追加）
- `commerce/ebay/staff-ops/takahashi-CLAUDE.md` — 高橋さん専用のCLAUDE.md（2026-04-15 Effort Level運用追記）
- `commerce/ebay/staff-ops/takahashi-setup-guide.md` — 高橋さん向けセットアップ手順書
- `commerce/ebay/staff-ops/takahashi-effort-level-setup.md` — Effort Level設定ガイド（Claude-to-Claude伝達用・2026-04-15）

## ステータス（2026-03-26）
- [x] 導入プラン作成
- [x] 権限設定テンプレート作成（v2: 読み取り全開放・management/追加）
- [x] 高橋さん専用CLAUDE.md作成（v2: 作業範囲拡大）
- [x] セットアップ手順書作成
- [ ] 社長の最終承認
- [ ] Claude Proアカウント契約（s.takahashi2603@gmail.com）
- [ ] GitHubアカウント作成→リポジトリ招待
- [ ] 高橋さんのPC環境セットアップ
- [ ] 初回レクチャー実施

## 権限設計（2026-03-26更新）
- **読み取り**: 全フォルダOK（.envとbaychat-ai/を除く）
- **編集可能**: staff-ops/, marketing/, management/ の3フォルダ
- **目的別**:
  - staff-ops/ → 総務・マニュアル・雑務全般
  - marketing/ → BayChat/BayPackのマーケ・プロモーション
  - management/ → 在庫管理アプリ・経理ツールの開発
- **Git**: PRベースで社長がレビュー→マージ
- **プログラム実行**: Python/Node.js OK（アプリ開発のため）

## Phase計画
1. **Phase 1（1〜2週間）**: 基礎トレーニング（質問の仕方・ファイル操作）
2. **Phase 2（2〜4週間）**: 総務・事務作業のAI化（Excel整理・アナログ資料デジタル化）
3. **Phase 3（1〜2ヶ月後）**: 在庫管理アプリ化・経理ツール試作
4. **Phase 4（2〜3ヶ月後）**: マーケティング本格稼働

## コスト
- Claude Pro: $20/月（約3,000円）— まずはこれでスタート
- GitHub/VS Code/Git: 無料

## 重要な決定事項（2026-03-26）
- Teamsプランは使わない（最低5人必要で割高）→ 個別契約が最適
- Coworkは不要（GitHubベースの同時並行作業で十分）
- 社長のMax環境はそのまま維持
- 高橋さんはBayChat/BayPackの情報を読んで理解した上で作業する

## Effort Level運用方針（2026-04-15追加）
- **Pro契約を踏まえた保守的設計**：デフォルトHigh固定、自動ブーストはデフォルトOFF
- **Max相当の発動は `ultrathink` 明示指定時のみ**（社長の方針通り）
- ヒアリング次第でオプトイン語（しっかり・ちゃんと・もっと）の自動発動を追加可能
- 伝達方式：`takahashi-effort-level-setup.md` を高橋さんのClaude Codeに渡すことで自動セットアップ
- 社長の環境（Max契約・フル自動ブースト）とは別系統で運用
