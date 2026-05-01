# eBay OAuth トークン rotate（取り消し→再発行）手順

**作成日**: 2026-04-29
**所要時間**: 10〜15分
**目的**: GitHub Private リポジトリに流出していた eBay OAuth refresh_token を無効化し、新しいトークンに置き換える

---

## 全体の流れ

```
STEP 1: eBay側で旧トークンを取り消し（無効化）
  ↓
STEP 2: PCで新トークンを発行（自動でファイルに保存される）
  ↓
STEP 3: 動作確認（週次レポートのスクリプトを1回試走）
  ↓
STEP 4: Claudeに「完了しました」と一言
```

---

## 事前準備

- ブラウザ（Chrome等）が使えること
- 社長のeBayセラーアカウント（Rioxx）にログインできるパスワード
- このPC（reffortフォルダがあるPC）が手元にあること

---

## STEP 1: eBay側で旧トークンを取り消す（5分）

### 1-1. eBay にログイン

ブラウザで https://www.ebay.com/mye/myebay/summary を開く。
すでにログインしていない場合はログインする（Rioxxのアカウント）。

### 1-2. アプリ・サイトのアクセス管理画面に移動

URLバーに以下を直接コピペして開く：
```
https://www.ebay.com/mys/auth/recent_activity
```

または、画面右上のアカウントアイコン → **Account settings**（アカウント設定）→ 左メニューの **Site Preferences**（サイト設定）→ 「**Permissions**」または「**Sign in and security**」セクション内の「**Apps and websites you've granted access to**」（連携しているアプリとサイト）。

### 1-3. Reffort のアプリを探して取り消し

連携アプリの一覧が表示される。今回rotateする対象は：
- アプリ名は `Reffort` または `Rioxx` または `[社長が4月に作成したeBay App名]` で表示されているはず
- 説明欄に「Marketing」「Analytics」「Sell APIs」などのスコープ名が書かれている

該当アプリの行にある **「Remove access」** または **「Revoke access」** ボタンをクリック。

確認ダイアログが出たら **「Yes / Confirm」** をクリック。

✅ これで旧 refresh_token は eBay 側で**即無効化**される。

### 1-4. 確認

リストから該当アプリが消えたことを確認。これでSTEP 1完了。

---

## STEP 2: PCで新トークンを発行（5分）

このPC（reffortフォルダがあるPC）で以下を実行する。

### 2-1. PowerShellまたはコマンドプロンプトを開く

スタートメニューで `powershell` と検索 → クリックして開く。

### 2-2. スクリプトを実行

開いた黒い画面に以下をコピペしてEnter：

```
cd "C:\Users\KEISUKE SHIMOMOTO\Desktop\reffort\commerce\ebay\analytics"
python ebay_oauth.py
```

### 2-3. 自動で起きること

スクリプトを実行すると、自動で以下が起きる：

1. **ブラウザが自動で開く**（eBayの認可画面が出る）
2. eBayのログインを求められたらログイン
3. 「**Reffortが以下の権限を要求しています**」画面が出る：
   - View your selling activity（売上閲覧）
   - Manage your marketing activities（広告管理）
   - View your marketing activities（広告閲覧）
4. 一番下の **「Agree（同意する）」** ボタンをクリック
5. ブラウザに「Token saved successfully」または成功メッセージが表示される
6. PowerShell画面に戻ると「✅ refresh_token 取得成功」のような表示

### 2-4. 確認

`ebay_oauth_tokens.json` ファイルが新しい内容で更新される（自動）。
gitignore済みなので、もう GitHub には上がらない。

---

## STEP 3: 動作確認（5分）

新しいトークンで週次レポートのスクリプトが正常動作するかテストする。

PowerShell画面で以下をコピペしてEnter：

```
cd "C:\Users\KEISUKE SHIMOMOTO\Desktop\reffort\commerce\ebay\analytics"
python create_weekly_report_v3.py
```

エラーが出ずに走り切れば成功。
- Excelファイルが生成される（数分かかる）
- 「Traffic API取得 OK」「OK Saved to ...xlsx」のような表示が出る

エラーが出た場合は、エラーメッセージをそのままコピペしてClaude にお送りください。

---

## STEP 4: Claudeに完了報告

「rotate 完了しました」と一言いただければ、Claudeが以下を実行します：

1. Chatwork個人DMに「セキュリティインシデント解決完了」報告
2. memory `feedback_security.md` を「**未対応**→**対応完了 2026-04-29**」に更新
3. （任意）git履歴からの完全削除（git filter-repo）の手順案内

---

## トラブル時の対処

### ❌ 「ブラウザが開かない」
→ 手動でURLを開く。`python ebay_oauth.py` の出力に表示されている `https://auth.ebay.com/oauth2/authorize?...` をブラウザにコピペ。

### ❌ 「Reffortのアプリが連携アプリ一覧に出てこない」
→ STEP 1-3 で別の名前で表示されているかも。表示されている全アプリを確認。判断つかなければ画面のスクリーンショットをClaudeに送る。

### ❌ 「Agree した後にエラー画面が出る」
→ Redirect URI設定の問題。エラーメッセージ全文をClaudeに送る。

### ❌ 「create_weekly_report_v3.py がエラー（401 Unauthorized等）」
→ STEP 2 が失敗している可能性。`python ebay_oauth.py` をもう一度実行。

### ❌ 「STEP 1 でアプリが見つからない／既に削除済み」
→ 想定外。Claudeに「アプリ一覧にReffortが見当たらない」と伝える。

---

## 補足：これは何のトークン？

今回rotateするのは「eBay の Sell系 API（Analytics + Marketing）にアクセスするための鍵」です。
- 流出していた場合の最大リスク：競合に売上数値が漏れる、広告予算を勝手に使われる
- rotate後はその「鍵」が新しいものに置き換わるので、旧鍵は永久に使えない

Cowatech に渡している在庫管理ツール用のトークンとは**別物**なので、今回の作業でCowatech側に影響はありません。

---

*このファイルは作業完了後、Claudeが削除候補として整理します。*
