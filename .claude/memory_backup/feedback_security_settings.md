---
name: セキュリティ設定の考え方
description: settings.local.jsonのセキュリティ設定方針。deny設定・トークン管理・.envブロックの判断基準
type: feedback
---

## セキュリティは「やり直せるか？」で判断する

- やり直せる操作（ファイル編集・検索・分析）→ Always allowでOK
- やり直せない操作（git push --force、git reset --hard）→ deny設定で禁止
- 外に出る操作（メッセージ送信・API呼び出し）→ 毎回確認

## deny設定済み（2026-03-26）
- `git push --force` / `-f`（全パターン）
- `git reset --hard`（全パターン）
- `Read(**/.env)` / `Read(**/.env.*)`

## トークン管理ルール
- curlでAPIを直接叩く許可を出すと、settings.local.jsonにトークンが丸ごと記録される
- MCP経由（mcp__chatwork__、mcp__slack__）ならトークンが見えないので安全
- 今後APIを叩く必要がある場合は、curlではなくMCPまたはPythonスクリプト（.envから読む）経由で行う

## .envブロックの理由（社長の洞察）
- 社長自身が「読んで」と指示する分には問題ない
- 問題は外部からの指示（プロンプトインジェクション）でClaudeが.envを読まされ、外部に送信させられるリスク
- .envの直接読み取りをブロックすることで、仮に騙されても読めない状態にした

**Why:** settings.local.jsonにAPIトークンが丸出しで記録されていた問題が発覚。.envに隠しても許可設定側に残る落とし穴
**How to apply:** 新しいAPI連携を設定するときは必ずMCPまたは.env経由。curlで直接トークンを渡す許可は出さない
