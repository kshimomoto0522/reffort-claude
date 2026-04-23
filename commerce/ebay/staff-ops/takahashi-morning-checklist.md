# 🌅 朝一確認用 — 高橋 Claude Code 導入チェックリスト
> 2026-03-27 朝に確認用

---

## 準備済み（Claudeが完了済み）

| # | 内容 | ファイル |
|---|------|---------|
| ✅ | 全体プラン（権限・ロードマップ・コスト） | `commerce/ebay/staff-ops/takahashi-claude-code-plan.md` |
| ✅ | 権限設定テンプレート（読み取り全開放・編集は3フォルダ限定） | `commerce/ebay/staff-ops/takahashi-settings-template.json` |
| ✅ | 高橋さん専用CLAUDE.md（Claudeの振る舞い設定） | `commerce/ebay/staff-ops/takahashi-CLAUDE.md` |
| ✅ | 高橋さん向けセットアップ手順書（印刷して渡せる形式） | `commerce/ebay/staff-ops/takahashi-setup-guide.md` |

---

## 社長がやること（手順どおり進めてください）

### ① アカウント作成（社長 or 高橋さん本人が実施）

**Claude.ai アカウント:**
1. https://claude.ai → Sign Up
2. メール: `s.takahashi2603@gmail.com`
3. Pro プランを契約（$20/月）

**GitHub アカウント:**
1. https://github.com → Sign up
2. メール: `s.takahashi2603@gmail.com`
3. ユーザー名を決める → 社長に報告

### ② GitHub リポジトリに招待（社長が実施）
1. https://github.com/kshimomoto0522/reffort-claude にアクセス
2. 「Settings」→「Collaborators」→「Add people」
3. 高橋さんのGitHubユーザー名を入力
4. **Write権限**で招待（PRベースで運用するため）

### ③ 高橋さんのPCセットアップ
- `takahashi-setup-guide.md` の手順に沿って進める
- 一緒にやる場合は30分〜1時間あれば完了
- または手順書を渡して自力でやらせてもOK（トレーニングにもなる）

### ④ 権限設定の配置（社長 or 高橋さんが実施）
1. 高橋さんのPC: `reffort/.claude/` フォルダを作成
2. `takahashi-settings-template.json` の中身を `settings.local.json` にコピー
3. `takahashi-CLAUDE.md` を高橋さんのユーザーディレクトリに配置

---

## 決定事項まとめ

| 項目 | 決定 |
|------|------|
| プラン | 社長:Max($100)のまま / 高橋:Pro($20)を新規契約 |
| 月額コスト | +$20（約3,000円）のみ |
| 読み取り範囲 | 全フォルダOK（.envとbaychat-ai除く） |
| 編集範囲 | staff-ops/ + marketing/ + management/ |
| Git運用 | PRベース（高橋→PR作成→社長レビュー→マージ） |
| 同時作業 | 可能（Cowork不要。GitHubで統合） |
| Teamsプラン | 不採用（最低5人必要で割高） |

---

## 高橋さんの作業ロードマップ

```
【今すぐ（Phase 1）】          【1ヶ月後（Phase 2）】
 基本操作を覚える               総務のAI化
 ファイル操作                   Excel整理
 簡単な文書作成                 マニュアル作成
       ↓                            ↓
【2ヶ月後（Phase 3）】         【3ヶ月後（Phase 4）】
 在庫管理アプリ試作              マーケ本格稼働
 経理ツール試作                  SNS・プロモーション
 management/で開発               BayChat/BayPack訴求
```

---

*このファイルは確認後に削除してOKです*
