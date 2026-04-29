# 外部ツール／サービス連携・自動化全般

> 業務段階を横断する**全業務に共通の土台技術**を集める棚です。
> どの業務段階（リサーチ・出品・在庫・仕入・経理・分析・広告 等）でも結局これらの技術が必要になります。

---

## なぜ「横断スキル」として独立させるか

業務AI化を進めると、必ずどこかで以下にぶつかります：

- スプレッドシート（Excel / Google Sheets）の操作
- Chatwork / Slack 等のチャットツール連携
- API（eBay / Google / その他）の認証と利用
- スクレイピング（公式APIがないサイトから情報取得）
- ファイル・メール・通知の自動連携

これらは**業務段階のどれにも入らない**が、**全業務段階で使う**。だから独立させて整理します。

---

## このフォルダの中身

| ファイル | テーマ |
|---|---|
| `cases/spreadsheet-automation.md` | スプレッドシート自動化3型（GAS／clasp／Sheets API／Playwright） |
| `cases/chatwork-mcp.md` | Chatwork MCP 連携（自動配信・通知） |
| `cases/scraping-strategy.md` | スクレイピング戦略（Bot検出回避・Playwright・stealth） |
| （今後追加） | API認証管理（OAuth2 / Service Account / トークン管理） |
| （今後追加） | スケジュールタスク運用 |

---

## メンバーが最初に試すべきこと

### 自分がどの「型」を使うべきか見極める

| やりたいこと | 推奨される型 |
|---|---|
| シート上で自動メニュー・トリガー処理 | 型A：GAS（Apps Script）+ clasp |
| 外部Pythonスクリプトからシート読書 | 型B：Sheets API + Service Account |
| 管理画面のUI操作・スクレイピング | 型C：Playwright + cookie session |

詳細は `cases/spreadsheet-automation.md` の3型ルーティング参照。

---

## つまづきやすい共通の落とし穴

### 認証情報管理
- APIキー・トークン・OAuth2 リフレッシュトークン … 種類が多い
- 全て .env で管理（00-claude-code-foundation/cases/02_security-rules.md 参照）

### 認証期限切れ
- OAuth2 リフレッシュトークンは数ヶ月で切れる場合あり
- 失敗時に通知される仕組みを最初に組み込む

### 並列処理の罠
- API レート制限・Bot検出・コスト爆発の原因になる
- 直列で安定させてから並列化を検討

### 「動いているはず」報告
- スケジュールタスクは「実行されている」と「正しく動作している」が別
- 必ずテスト実行＋結果確認＋通知を仕込む

---

## 関連

- セキュリティ: `by-business-process/00-claude-code-foundation/cases/02_security-rules.md`
- 業務段階別の実例: `by-business-process/03〜10/`
- 関連 memory: `feedback_spreadsheet_automation_patterns.md` / `feedback_chrome_mcp_unattended.md`

---

*更新: 各事例ファイル作成・社長運用継続による発見追加*
