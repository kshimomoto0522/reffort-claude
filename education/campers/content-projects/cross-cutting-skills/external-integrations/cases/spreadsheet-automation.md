# スプレッドシート自動化3型ルーティング

> 業務段階横断（全業務でスプレッドシートを使う前提）
> 状況: 社長運用継続中（3型すべて稼働中）
> 元素材: 旧 spreadsheet-automation-case-study（archived-by-theme/ に保存）

---

## 何をやったか（目的・背景）

eBay運営に限らず、**ほぼ全ての中小事業者は業務をスプレッドシートに集約**している。

しかし「AIにスプレッドシートを任せる」のやり方は1つではない。**3つの型**があり、用途で使い分けが必要。社長は3型すべてを実践し、それぞれの落とし穴を体験した。

---

## 3型ルーティング（最重要）

### 型A：シート上で動くロジック（Apps Script + clasp）

**いつ使う**:
- シートを開いた瞬間メニュー表示
- 行追加トリガー
- 時間トリガーで API叩いて自動入力

**適例**:
- 仕入管理表（毎朝 eBay APIから新規オーダーを取得→反映）

**ツール**:
- Google Apps Script（GAS）
- clasp（Google公式 CLI・ローカル開発・自動デプロイ）

**社長の運用例**:
- `commerce/ebay/tools/gas/shiire/`（仕入管理表）

---

### 型B：外部からシートを読み書き（Sheets API + Service Account）

**いつ使う**:
- Pythonの朝バッチで集計→シートに書込
- 在庫管理ツールがシート更新
- 外部システムとの連携

**適例**:
- 週次レポート（Pythonで Excel生成＋Sheets書込→ Chatworkに配信）

**ツール**:
- Google Sheets API
- Service Account（人間アカウントとは別の機械アカウント）
- gspread / google-api-python-client（Pythonライブラリ）

**社長の運用例**:
- 週次レポートv3 の GSheets書込

---

### 型C：シートのUI操作（Playwright + cookieセッション・最終手段）

**いつ使う**:
- 管理画面でしか操作不可のUI設定
- GASエディタ自体を触る
- API公開がない権限管理

**適例**:
- Campersグループの権限OFF/ON操作

**ツール**:
- Playwright（ブラウザ自動操作）
- storage_state（cookie保存・継続セッション）
- Windowsタスクスケジューラ（Claude scheduled-task ではなく直接起動）

**社長の運用例**:
- Campersメンバー削除（権限OFF→API削除→ON×2部屋＋全体連絡API削除）

---

## 3型の判定フローチャート（記事化時に図示）

```
やりたいこと
  ↓
シート内のロジックを動かしたい？
  ├─ Yes → 型A（GAS + clasp）
  └─ No
       ↓
       外部からシートを読書きしたい？
        ├─ Yes → 型B（Sheets API + Service Account）
        └─ No
            ↓
            APIで操作できないUI操作が必要？
             ├─ Yes → 型C（Playwright + cookie）
             └─ No → そもそもスプレッドシート不要
```

---

## つまづいたこと（失敗・遠回り）

### 失敗1：型を間違える
- 型Aで済むのに Playwright で Monaco editor を操作 → bot検知・遠回り
- 型Bで済むのに GAS を新規作成 → GAS制約（実行時間6分・同時実行制限）に詰まる
- 型Cが必要なのに API で無理やり片付けようとする → 仕様外で動かない
- 教訓：**最初に型判定を正しくする**

### 失敗2：Anthropic Issue（Chrome MCP）
- Claude in Chrome MCP を無人実行で使うと per-origin permission 問題で停止
- Anthropic Issue [#30356](https://github.com/anthropics/claude-code/issues/30356) / [#47180](https://github.com/anthropics/claude-code/issues/47180)
- 対策：**Playwright + Windowsタスクスケジューラ直接起動**に切り替え

### 失敗3：Monaco editor 手動 Ctrl+V 運用の限界
- GAS のエディタに手動でコードをペーストする運用
- ペースト漏れ・古いコード残存・差分管理不可
- 対策：**clasp 必須**

### 失敗4：Claude scheduled-task の per-task 承認キャッシュ不安定性
- 「Run now の常に許可」が UI に出ない現象（2026-04-24社長観測）
- 無人タスクで毎回承認待ちになるリスク
- 対策：**Chrome 操作が必要なタスクは Windowsタスクスケジューラ直接起動**

---

## 学んだこと（教訓）

- **3型を見極めることが最重要**：間違えると遠回り
- **GAS は clasp で管理**：Monaco editor 手動運用は破綻
- **Service Account は機械アカウント**：人間ログイン切れの心配なし
- **Playwright は cookie session で安定**：毎回ログインさせない
- **Chrome 操作の無人タスクは Claude 経由を捨てる**：Windowsタスクスケジューラ直接

---

## メンバーへの含意（応用ポイント） ★

### あなたの業務でもこの3型は使う
- 在庫管理表（型A or 型B）
- 仕入管理表（型A）
- 売上ダッシュボード（型B）
- 顧客リスト（型A or 型B）
- 経費集計表（型B）

### 必要な前提
- Google アカウント（個人 or 業務用）
- Python or Node.js の最低限の理解
- Claude Code が動く環境（00-claude-code-foundation/ 整備済み）

### 最初の1個を作る手順
1. 自分の業務スプレッドシートを1つ選ぶ
2. やりたいことを言語化（「毎朝 ○○ を自動更新したい」等）
3. 上記の型判定フローチャートで A/B/C を判定
4. Claude Code に「型○で実装して」と依頼
5. テスト → 1週間運用 → 改善

### やってはいけないこと
- ❌ 型を間違える（最重要）
- ❌ Monaco editor 手動運用（型A の場合は clasp 導入）
- ❌ Chrome MCP の無人実行（型C は Playwright + Windowsタスク直接）
- ❌ Service Account の JSON キーを GitHub にプッシュ

---

## 配信先別の使い分け

| 配信先 | 適合度 | 注意点 |
|---|---|---|
| Campers ◎ | ◎ | 全員がスプレッドシートを使うため最も刺さる |
| 匿名X | ◎ | 「3型ルーティング」は普遍的価値・独立した記事化可能 |
| Note有料 | ◎ | 有料記事3本構成（型A実装／型B実装／型C実装） |

---

## 関連

- 既存の旧 case-study（保存）: `archived-by-theme/spreadsheet-automation-case-study/`
- 関連 memory: `feedback_spreadsheet_automation_patterns.md` / `feedback_chrome_mcp_unattended.md`
- 関連 spec: `commerce/ebay/tools/gas-shiire-tool-spec.md`
- 関連 Claude Code 基盤: `by-business-process/00-claude-code-foundation/`

---

*作成: 2026-04-29（コンテンツ蓄積基盤整備セッション）*
*社長運用継続中（3型すべて稼働中）*
