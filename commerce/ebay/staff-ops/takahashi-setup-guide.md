# 【高橋さん向け】Claude Code セットアップ手順書

> この手順書に沿って、1つずつ進めてください。
> わからないことがあったら社長に聞いてOKです。

---

## ステップ1: Claude.ai のアカウントを作る

1. ブラウザで https://claude.ai を開く
2. 「Sign Up」（新規登録）をクリック
3. **メールアドレス**: `s.takahashi2603@gmail.com` で登録
4. パスワードを設定（自分で決めてOK）
5. メールに届く確認リンクをクリック

## ステップ2: Claude Pro を契約する

1. claude.ai にログイン
2. 左下の「Upgrade」→「Pro」を選択
3. **$20/月**（約3,000円）のプランを選ぶ
4. 支払い情報を入力

※ 支払いについては社長に確認してください

## ステップ3: GitHub のアカウントを作る

1. ブラウザで https://github.com を開く
2. 「Sign up」をクリック
3. **メールアドレス**: `s.takahashi2603@gmail.com` で登録
4. ユーザー名を決める（例: `s-takahashi2603`）
5. パスワードを設定
6. メールに届く確認リンクをクリック

→ 作成できたら社長にユーザー名を伝えてください。社長がリポジトリに招待します。

## ステップ4: 必要なソフトをインストール

以下3つをダウンロード＆インストールしてください。
すべて無料で、「次へ」「Next」を押していけばOKです。

### ① Node.js
- https://nodejs.org にアクセス
- **LTS版（左の緑のボタン）** をダウンロード
- インストーラーを実行 → 全部「Next」でOK

### ② Git
- https://git-scm.com にアクセス
- 「Download for Windows」をクリック
- インストーラーを実行 → 全部デフォルト設定でOK

### ③ VS Code（テキストエディタ）
- https://code.visualstudio.com にアクセス
- 「Download for Windows」をクリック
- インストーラーを実行

## ステップ5: Claude Code をインストール

1. VS Code を開く
2. 上のメニューから「ターミナル」→「新しいターミナル」を選ぶ
3. 下に黒い画面（ターミナル）が出るので、以下を入力してEnter:

```
npm install -g @anthropic-ai/claude-code
```

4. しばらく待つ（数分かかることもある）
5. 「added X packages」と出たらOK

## ステップ6: Git の初期設定

ターミナルで以下を1行ずつ入力してEnter:

```
git config --global user.name "Sae Takahashi"
git config --global user.email "s.takahashi2603@gmail.com"
```

## ステップ7: リポジトリをクローン（ダウンロード）

※ 社長がGitHubで招待してからこのステップに進んでください

ターミナルで以下を入力:

```
cd ~/Desktop
git clone https://github.com/kshimomoto0522/reffort-claude.git reffort
```

→ デスクトップに「reffort」フォルダが作られます

## ステップ8: 権限設定ファイルを配置

1. reffort フォルダの中に `.claude` フォルダを作る
2. `commerce/ebay/staff-ops/takahashi-settings-template.json` の中身をコピー
3. `.claude/settings.local.json` という名前で保存

※ このステップは社長と一緒にやるか、社長が事前に設定してください

## ステップ9: Claude Code を起動してみる

ターミナルで:

```
cd ~/Desktop/reffort
claude
```

→ ブラウザが開くので、ステップ1で作ったclaude.aiアカウントでログイン
→ 「Hello!」と入力してみて、返事が返ってくればセットアップ完了！

---

## 最初にやってみること（練習）

セットアップが終わったら、以下を試してみてください:

### 練習1: 質問してみる
Claude Code で以下を入力:
```
株式会社リフォートについて、CLAUDE.mdを読んで教えて
```

### 練習2: ファイルを作ってみる
```
staff-ops/ フォルダに「test.md」というファイルを作って、
「テストです」と書いてください
```

### 練習3: Git を試す
```
今の変更をgit commitして
```

---

## 困ったときチェックリスト

| 症状 | やること |
|------|---------|
| npm が見つからない | Node.js をもう一度インストール。PCを再起動 |
| git が見つからない | Git をもう一度インストール。PCを再起動 |
| claude が見つからない | ステップ5をもう一度やる |
| ログインできない | claude.ai のパスワードを確認。リセットも可 |
| clone できない | 社長にGitHub招待を確認 |

**何をやってもダメなときは、エラーメッセージのスクリーンショットを社長に送ってください。**

---

*作成: 2026-03-26*
