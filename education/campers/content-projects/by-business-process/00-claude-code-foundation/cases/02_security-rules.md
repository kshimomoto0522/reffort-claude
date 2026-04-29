# セキュリティルール — APIトークン管理・社長が試行錯誤して確立した運用

> 対象: Campersメンバー
> 所要時間: 20〜30分の理解＋随時

---

## このファイルでわかること

- APIトークンの正しい管理方法（.envファイル）
- やってはいけない危険な行為
- 社長が実際にやらかして学んだ教訓

---

## なぜセキュリティが最初に来るか

Claude Codeは強力です。eBay APIキー、Chatwork APIキー、各種サービスのトークン … これらが揃って初めて業務AI化ができます。

しかし**そのトークンが漏れたら**：
- eBayアカウントが乗っ取られる
- 顧客データが盗まれる
- スタッフ宛Chatworkで偽メッセージが送られる
- 不正課金される

「便利さ」と「危険さ」は表裏一体。最初に**正しい管理方法**を身につけてから業務AI化に進みます。

---

## ルール1：APIトークンは必ず .env で管理する

### やってはいけないこと

❌ **コード内に直接書く**:
```python
EBAY_API_KEY = "abc123xyz789..."   # ← 絶対NG
```

❌ **CLAUDE.md などのMarkdownに書く**:
```markdown
私のAPIキーは abc123xyz789 です  ← ← 絶対NG
```

❌ **GitHubに直接プッシュする**:
- パブリックリポジトリは即座に世界中のbotに発見される
- プライベートでも、運営側からアクセス可能

### 正しい方法：.envファイル

プロジェクトフォルダのトップに `.env` という名前のファイルを作って、そこにトークンを書きます：

```
EBAY_APP_ID=your_app_id_here
EBAY_CERT_ID=your_cert_id_here
CHATWORK_API_TOKEN=your_token_here
```

そして `.gitignore` に `.env` を必ず追加（GitHubに上がらないようにする）：

```
.env
.env.*
```

コードからは環境変数として読み込みます：

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("EBAY_APP_ID")
```

---

## ルール2：Claude Code には .env の中身を見せない

Claude Code は便利ですが、**.envファイルの中身をチャットに出力させてはいけません**。

### 何が問題か
- チャットログがAnthropic側に送信される（学習に使われない契約だが、ログには残る）
- スクリーンショットを誰かに送ったときに漏れる
- セッション履歴を共有したときに漏れる

### 社長と Claude のルール
- Claude が `.env` ファイルの**中身を表示する行為は禁止**
- 値が必要な時は、**社長が直接ファイルに書き込む**（Claudeはテンプレを作るだけ）
- Claudeは「.envを開きました」「項目を追加しました」と宣言するが、**値は見ない／見せない**

これは社長が実際に体験して、Claude Codeの設定（settings.local.json の deny ルール）に焼き込んでいます。

---

## ルール3：本番の顧客データ・注文データは扱う前に必ず確認

eBayの本番注文データやBayChatの本番DBを扱う作業は、**社長が明示的に許可してから**着手します。

ヒヤリハットの例：
- テスト用と思って本番DBに書き込み → データ消失
- 「全件削除して」と指示 → 本当に全件消えた
- 「このメッセージを送って」 → スタッフ全員に意図しないSlack送信

**Claude Code は強力すぎる**ため、確認なしで動くと不可逆な事故が起きます。

---

## ルール4：settings.local.json の権限管理

Claude Code はコマンド実行権限を `settings.local.json` で管理します。
このファイルに「ALLOW」されているコマンドはユーザー確認なしで実行されます。

### ベストプラクティス
- ワイルドカード（`Bash(*)`等）は使わない
- 個別コマンドを必要に応じて追加
- 怪しいコマンドはallowリストから削除（特に rm, sudo, curl等の外部送信）
- 定期的に棚卸しする（社長は隔週メンテで実施）

---

## ルール5：GitHubバックアップは Private リポジトリで

社長の事業フォルダは GitHub に毎日深夜0時に自動バックアップされています。

- リポジトリは**必ずPrivate**（Publicにすると世界中に公開）
- バックアップ先：[https://github.com/kshimomoto0522/reffort-claude](https://github.com/kshimomoto0522/reffort-claude)（社長の例）
- メンバーも自分のGitHubアカウントで Private リポジトリを作成すべし

---

## 社長が試行錯誤して学んだこと

### 失敗1：APIトークンを設定ファイルに直書き
- → 早期に発見できたので被害ゼロ
- → 即座に .env 管理へ移行
- → settings.local.json から該当行を削除

### 失敗2：Claude Code に .env の中身を読ませた
- → セッションログにトークンが残る可能性に気付いた
- → settings.local.json で .env の Read を deny に設定

### 失敗3：本番Slackに意図せず送信
- → 「このメッセージ送信して」を Claude が即実行
- → 以降「送信前に必ずGOを確認する」ルールを徹底

これらは Reffort で実際に起きた事例で、それぞれ運用ルール化されました。

---

## 次のステップ

→ `03_claude-md-template.md` で、自分用のCLAUDE.mdを作る

---

*社長の体験談（journey-log.md L452-491 ほか）から要点整理*
*関連 memory: feedback_security.md / feedback_env_file_handling.md*
