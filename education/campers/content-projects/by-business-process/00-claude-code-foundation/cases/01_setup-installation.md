# Claude Code インストール・初期セットアップ手順

> 対象: Campersメンバー（プログラミング未経験〜半経験）
> 所要時間: 30分〜1時間

---

## このファイルでわかること

- Claude Code を自分のPCにインストールする方法
- Claude Code を初めて起動して、動作確認するまで
- インストール時に詰まりやすいポイント

---

## 前提条件

| 項目 | 推奨 |
|---|---|
| OS | Windows 10/11、または macOS |
| Anthropic Claude プラン | **Claude Max プラン**（社長と同じ。複数セッション対応） |
| Node.js | LTS版（必須・後述） |
| Git | インストール済み（GitHub連携で必要） |

---

## ステップ1：Node.js のインストール

Claude Code は Node.js が必要です。

1. [https://nodejs.org/](https://nodejs.org/) にアクセス
2. **左側の「LTS版」**を選ぶ（緑色の大きいボタン・例：v24.14.1 LTS版）
3. Windowsの場合は「Windows 64-bit Installer」（.msi）をダウンロード
4. インストーラーを実行（全部「次へ」でOK）

**注意**：
- 「最新版」を選ばない（不安定なことがある）
- LTS = Long Term Support（長期サポート版）が業務用途では一択

---

## ステップ2：Claude Code のインストール

ターミナル（Windowsはコマンドプロンプトまたは PowerShell・Macはターミナル）を開いて、以下を実行：

```bash
npm install -g @anthropic-ai/claude-code
```

インストールが終わったら確認：

```bash
claude --version
```

バージョンが表示されればOK。

---

## ステップ3：Claude プラン契約・ログイン

1. [https://claude.ai/](https://claude.ai/) にアクセス
2. **Max プラン**を契約（複数セッション対応・推奨）
3. ターミナルで以下を実行してログイン：

```bash
claude
```

ブラウザが開くので、claude.aiにログイン済みのアカウントで認証します。

---

## ステップ4：作業フォルダの準備

自分の事業用フォルダを作ります。例：

```bash
mkdir my-ebay-business
cd my-ebay-business
```

このフォルダの中で Claude Code を起動：

```bash
claude
```

これで「このフォルダ専用のClaude」として動き出します。

---

## ステップ5：動作確認

Claude Code が起動したら、試しに聞いてみてください：

```
このフォルダの中身を教えて
```

```
今日は何月何日？
```

応答が返ってくればOK。

---

## つまづきやすいポイント

### ポイント1：「commandが見つからない」エラー
- → Node.jsのインストールが正しく終わっていない
- 一度ターミナルを閉じて開き直す（PATHの再読み込み）
- それでもダメなら Node.js を再インストール

### ポイント2：「権限がない」エラー
- → npm のグローバルインストールに管理者権限が必要な場合がある
- Windows: 「管理者として実行」でコマンドプロンプトを開き直す
- Mac: `sudo npm install -g @anthropic-ai/claude-code`

### ポイント3：ログインで詰まる
- → ブラウザが自動で開かない場合がある
- 表示されたURLを手動でブラウザに貼り付け

### ポイント4：複数のPCで使いたい
- → ログイン情報は各PCで個別に行う必要がある
- 作業フォルダはGitHub経由で同期する（後述）

---

## 次のステップ

→ `02_security-rules.md` で APIトークン管理・セキュリティルールを学ぶ

---

*社長の体験談（journey-log.md L18-101 / L118-196）から要点整理*
