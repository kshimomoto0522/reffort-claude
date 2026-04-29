# Slack Bot セットアップ手順（社長作業）

baychat-slack-check スクリプトを動かすには Slack Bot Token (`xoxb-...`) が必要です。
Anthropic 経由のSlack MCPはOAuthでトークンが取れないため、別途 Slack App を作成して Bot を発行します。

所要時間：約10分

---

## STEP 1: Slack App を作成

1. https://api.slack.com/apps にアクセス
2. 「Create New App」→「From scratch」を選択
3. App Name: `Reffort BayChat Bot`（なんでもOK）
4. Workspace: Reffort のワークスペースを選択
5. 「Create App」

## STEP 2: Bot Token Scopes を設定

1. 左メニュー「OAuth & Permissions」を開く
2. 下にスクロールして「Scopes」→「Bot Token Scopes」へ
3. 「Add an OAuth Scope」で以下7個を**全部**追加：
   - `channels:history` — チャンネルメッセージ取得
   - `channels:read` — チャンネル情報取得
   - `chat:write` — メッセージ投稿
   - `users:read` — ユーザー情報取得
   - `groups:history` — プライベートチャンネル対応
   - `groups:read` — プライベートチャンネル情報
   - `chat:write.public` — Bot未参加でも投稿可（任意）

## STEP 3: Workspace にインストール

1. 「OAuth & Permissions」ページ上部の「Install to <Workspace>」をクリック
2. 権限確認画面で「許可」をクリック
3. 上に表示される「Bot User OAuth Token」（`xoxb-...` で始まる）をコピー

## STEP 4: トークンを .env に貼り付け

ファイル：`C:/Users/KEISUKE SHIMOMOTO/Desktop/reffort/services/baychat/ai/slack-check/.env`

```
SLACK_BOT_TOKEN=xoxb-（ここにペースト）
```

## STEP 5: Bot をチャンネルに招待

Slackで `#baychat-ai導入` チャンネルを開き、メッセージ欄に：
```
/invite @Reffort BayChat Bot
```

入力して送信。Botが入室したら準備完了。

## STEP 6: 動作確認

社長は何もしなくてOK。Claudeに「Slack Botセットアップ完了しました」と一言送れば、Claudeが下記を順に実行します：
1. DRY_RUN モードでテスト実行
2. 結果を社長に確認
3. DRY_RUN=false に切替えて本番化
4. Windows Task Scheduler 起動

---

## 注意事項

- `xoxb-...` トークンは絶対に他者と共有しない（漏洩したら STEP 1 で revoke→再発行）
- App は今後 Reffort 専用の他用途にも使い回せる（例：今後別チャンネル監視を追加する等）
- スコープ追加時は再インストール（STEP 3）が必要
