---
name: スプレッドシート自動化の3型ルーティング
description: GAS内ロジック=clasp / 外部Python=Sheets API / UI操作=Playwrightの使い分け。Monaco編集の手動Ctrl+V運用は廃止
type: feedback
originSessionId: 723d0162-a26f-4a70-85ec-18691aeb1a1d
---
# スプレッドシート自動化の3型ルーティング

スプレッドシート関連の自動化案件は3つの型に分けて、最適なツールを即決できるようにする。

**Why:**
- 2026-04-28まで仕入管理表のコード更新を「Monaco editorに手動Ctrl+V」で運用していたが、Claude in Chrome経由は失敗多発（Chrome側の保護で）、社長による手動操作が必須でボトルネック化
- 解決策（clasp）が**既に手元にインストール済み**だったが活用されていなかった（npm install -g clasp済・3.3.0）
- 「Chrome操作で詰まる」案件の多くは型Aで、clasp に切り替えれば即解決する

**How to apply:**

新規スプレッドシート自動化を求められたら、まずどの型かを即判定する：

| 型 | やりたいこと | 推奨ツール | セットアップ |
|---|---|---|---|
| **A. GAS内でロジックを書く・走らせる** | シートを開いた瞬間にメニュー表示／行追加トリガー／GAS自身がeBay等のAPIを叩いてシートに反映／時間トリガーで自動実行 | **`clasp`**（公式CLI）でローカルマスター管理 + GASトリガー | `clasp login`（1回）→ 各GASに `clasp clone <scriptId>` |
| **B. 外部からシートを読み書きする** | Pythonの朝バッチで集計→シートに書込／在庫管理ツールがシートからSKU読込・更新 | **Google Sheets API + Service Account**（既設・`commerce/ebay/analytics/.env` の `GOOGLE_SHEETS_CREDENTIALS`） | service account JSONを共有・スプレッドシートを「サービスアカウントメール」に共有 |
| **C. シートのUI操作が要る** | スプレッドシート画面でしか実現不可なUI操作（条件付き書式の動的調整、ピボット作成 等） | **Playwright**（`storage_state` cookie永続化） | `setup_chatwork_auth.py` 同等の認証スクリプト+ Windowsタスク |

**型Aの実装パターン（clasp版・推奨）:**
- フォルダ構造: `<base>/gas/<project>/`（例: `commerce/ebay/tools/gas/shiire/`）
- 必須ファイル: `.clasp.json`（scriptId）/ `appsscript.json`（マニフェスト）/ `*.js`（コード）
- 更新: `cd <base>/gas/<project>/ && clasp push`
- 取得: `clasp pull` または `clasp clone <scriptId>`（新規プロジェクト紐付け時）
- Chromeブラウザ・Monaco editor・手動Ctrl+V は **完全に不要**

**禁止事項:**
- 型Aの案件で Playwright + Monaco editor 操作を提案・実装すること（bot検知・Monacoの不安定さで遠回り）
- 旧 `gas_copy.html` + `serve_gas.py` + `update_gas_copy.py` + base64 中継のような Monaco貼付け補助ファイルを新規作成すること（clasp で完全代替済み）

**clasp に絞り込むべき判断ポイント:**
- 「シート上で動くロジックを書きたい」→ 即 clasp（型A）
- 「外からデータを入れたい」→ 即 service account（型B）。GAS書く必要なし
- 上記どちらも当てはまらないUI操作は最後の手段で Playwright

**現在運用中のGASプロジェクト（型A）:**
- 仕入管理表: `commerce/ebay/tools/gas/shiire/` → 本番GAS `1EGuRaF3Hj1Uhayek4jCIgGQcxzKEJxLaqZmqfsgZbRph_RYUNZRgCNNf`（毎朝9:45自動実行）
