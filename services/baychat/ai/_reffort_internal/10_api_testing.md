# 10. API・テスト環境仕様

> ✅ **v0.2 完成版**
> このファイルの役割：**AI Replyの本番同等テスト環境** を完全ドキュメント化する。Claude/Cowatech/社長が同じ理解でテスト実行・結果解釈できる状態を作る。

---

## 🎯 テスト環境の全体像

```
┌──────────────────────────────────────────────┐
│  services/baychat/ai/testing/                         │
│  ┌────────────────────────────────────────┐  │
│  │  1. extract_cases.py                   │  │
│  │     STG DBからテストケース抽出          │  │
│  │          ↓                              │  │
│  │  2. test_cases/*.json（50件規模）       │  │
│  │          ↓                              │  │
│  │  3. payload_builder.py                 │  │
│  │     本番と同構造のmessages組立           │  │
│  │          ↓                              │  │
│  │  4. batch_test.py                      │  │
│  │     マルチモデル×プロンプト版テスト     │  │
│  │          ↓                              │  │
│  │  5. ai_judge.py                        │  │
│  │     5項目×5点自動採点                  │  │
│  │          ↓                              │  │
│  │  6. results/*.xlsx / *.html            │  │
│  │     Excel+HTMLで結果可視化             │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

---

## 📁 ディレクトリ構成（完全版）

```
services/baychat/ai/testing/
├── __pycache__/                    # Pythonキャッシュ
├── test_cases/                     # 抽出テストケース
│   └── extracted_YYYYMMDD_HHMMSS.json
├── results/                        # テスト結果
│   ├── test_*.xlsx                 # 採点結果Excel
│   ├── comparison_*.html           # HTML比較レポート
│   └── run_log_*.txt               # 実行ログ
│
├── payload_builder.py              # 本番同等ペイロード組立
├── batch_test.py                   # メインエンジン
├── ai_judge.py                     # AI審判（5項目×5点）
├── db_connect.py                   # SSH+MariaDB接続
├── extract_cases.py                # STG DB抽出
│
├── render_reply_comparison.py      # HTML：返信比較
├── render_summary_view.py          # HTML：集計サマリ
│
├── _inspect_views.py               # 補助：HTMLビュー確認
├── _speed_analysis.py              # 補助：速度分析
├── _summarize_5models.py           # 補助：5モデル比較
└── _summarize_results.py           # 補助：結果集計
```

---

## 🔧 主要スクリプト詳細

### 1. payload_builder.py — 本番同等ペイロード組立

**何をするか**：Cowatech本番APIペイロードを完全再現。8ブロック構造で messages を組立。

**主要関数**：
```python
payload_builder.build_payload(
    messages,                      # chat history配列
    tone="polite",                 # polite/friendly/apologetic
    description="",                # {sellerSetting}置換用
    include_forced_template=True   # 本番=True
)
```

**組立順序**：
```
[0]   developer : 商品情報JSON
[1..] user/assistant/system : チャット履歴
[N+1] developer : description_guide（descriptionあれば）
[N+2] developer : BASE_PROMPT
[N+3] developer : OUTPUT_FORMAT
[N+4] developer : admin_prompt（{sellerSetting}/{toneSetting}置換後）
[N+5] developer : FORCED_TEMPLATE（include_forced_template=True時）
```

---

### 2. batch_test.py — メインエンジン

**何をするか**：テストケース×モデル×プロンプト版の全組み合わせで API呼び出し → AI採点 → Excel出力。

**全フラグ一覧**：

| フラグ | 内容 | 例 |
|-------|-----|---|
| `--models` | モデル指定（複数可） | `--models gpt gemini claude` |
| `--prompt-versions` | プロンプト版（複数可） | `--prompt-versions 2.3 2.4` |
| `--cases` | テストケースJSONパス | `--cases testing/test_cases/extracted_*.json` |
| `--judge` | AI審判（openai/claude/gemini） | `--judge claude` |
| `--no-judge` | 採点スキップ | — |
| `--limit` | ケース数制限 | `--limit 10` |
| `--production-payload` | **本番モード**（FORCED_TEMPLATE有効） | — |
| `--no-forced-template` | FORCED_TEMPLATE除外 | — |
| `--tone` | 固定tone | `--tone friendly` |
| `--seller-name` | セラー名（テンプレ内） | `--seller-name myshop` |
| `--description` | sellerSetting（admin指示文） | `--description "Be concise"` |

**推奨実行例（本番同等モード）**：
```bash
cd services/baychat/ai/testing
python batch_test.py \
  --models gpt gemini \
  --prompt-versions 2.3 2.4 \
  --production-payload \
  --cases test_cases/extracted_20260415_182039.json \
  --judge claude \
  --limit 30
```

---

### 3. ai_judge.py — AI審判

**評価項目（5項目 × 5点 = 25点満点）**：

| # | 項目 | 5点 | 3点 | 1点 |
|---|------|---|---|---|
| 1 | Accuracy（正確性） | 完全に正確・ポリシー準拠 | 大部分正確だが細節に誤り | 誤情報・有害 |
| 2 | Tone（トーン） | 完全にプロ＆共感的 | 共感やや不足 | 無礼・冷淡・不適切 |
| 3 | Completeness（完全性） | 全質問・懸念に対応 | 主要点は答えるが細節漏落 | 主要質問を見落とし |
| 4 | Action Clarity（アクション明確性） | 次のステップが明確 | ガイダンスあるが曖昧 | 次のステップ不明 |
| 5 | Naturalness（自然さ） | 人間のCSのように自然 | 多少AI的だが許容範囲 | テンプレ感強い |

**審判の出力形式**：
```json
{
  "accuracy": 4,
  "tone": 5,
  "completeness": 3,
  "action_clarity": 4,
  "naturalness": 4,
  "total": 20,
  "critical_issues": ["should mention return shipping label"],
  "improvements": ["add timeline for resolution"],
  "summary_ja": "返信は正確で親切だが、返品手続きの具体的なステップが不足している。"
}
```

---

### 4. db_connect.py — SSH+MariaDB接続

**接続フロー**：
1. SSH秘密鍵（`~/.ssh/id_ed25519_vps_baychat`）ロード
2. VPS踏み台にトンネル接続：`ssh -L 127.0.0.1:13306:RDSホスト:3306`
3. localhost:13306 → VPS → RDS への通路確立
4. pymysql で接続（実はRDS）

**必須.env変数**：
| 変数名 | 用途 |
|-------|-----|
| `BAYCHAT_STG_DB_HOST` | RDSホスト |
| `BAYCHAT_STG_DB_PORT` | 3306（またはカスタム） |
| `BAYCHAT_STG_DB_USER` | DBユーザー |
| `BAYCHAT_STG_DB_PASSWORD` | DBパスワード |
| `VPS_HOST` | VPS固定IP（`.env.vps`に記載） |

**使用例**：
```python
with get_tunnel_and_connection(database="baychat_stg") as (tunnel, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM view_chat_ebay LIMIT 5")
    rows = cursor.fetchall()
```

---

### 5. extract_cases.py — テストケース抽出

**何をするか**：STG DB `view_chat_ebay` から「最新メッセージ＝バイヤー発信＝セラーが返信する番」の会話を50件抽出。

**カテゴリ分類ロジック**（キーワード優先度順）：
| 優先度 | カテゴリ | キーワード例 |
|-------|--------|------------|
| 1 | cancel | "cancel", "placed by mistake", "by accident" |
| 2 | return | "return", "refund", "send it back", "RMA" |
| 3 | claim | "damaged", "broken", "wrong", "not as described" |
| 4 | tracking | "tracking", "shipment", "when will", "delivery", "customs" |
| 5 | discount | "discount", "offer", "negotiate", "best price" |
| 6 | general | 上記に該当しないもの |

**実行例**：
```bash
python extract_cases.py                    # 50件バランス抽出
python extract_cases.py --limit 100        # 100件に変更
python extract_cases.py --per-category 8   # カテゴリあたり8件（計48件）
```

**出力**：`test_cases/extracted_YYYYMMDD_HHMMSS.json`

**妥当性フィルター**：
- バイヤーメッセージ最低60文字（挨拶・感謝のみ除外）
- 単純応答（Thank you / OK / Got it）は meaningful=False → スキップ
- 複雑すぎる会話（20メッセージ超）スキップ

---

## 📄 テストケースJSONフォーマット

```json
[
  {
    "id": "rafrra69_64efacd9",        // seller_hash + uuid
    "category": "cancel",              // 6カテゴリ
    "buyer_ebay": "rafrra69",          // バイヤーeID
    "buyer_message": "Yo quiero mi reembolso...",  // LATESTメッセージ
    "num_messages": 32,                // 会話メッセージ総数
    "has_seller_history": true,        // セラー過去返信あり
    "input": [                         // OpenAI messages形式
      {"role": "developer", "content": "{\"Title\": \"...\", ...}"},
      {"role": "system", "content": "event: [日時] purchase_completed"},
      ...
    ]
  }
]
```

---

## 📊 Excel結果フォーマット

### シート1：スコアサマリー

| カラム | 内容 |
|-------|------|
| ケース | テストケースID |
| モデル | 使用モデル名 |
| プロンプト | バージョン |
| 正確性〜自然さ | 5項目スコア |
| 合計(/25) | 合計スコア（条件付き書式） |
| 応答時間(秒) | レイテンシ |
| コスト(¥) | 円換算コスト |
| サマリー | 審判の1行コメント |

**条件付き書式**：
- 20点以上 = 🟢 緑
- 15〜20 = 🟡 黄
- 15未満 = 🔴 赤

### シート2：詳細
- AI返信テキスト（日本語・英語）
- 採点理由
- critical_issues
- improvements

### シート3：集計
- モデル別・プロンプト版別の平均スコア比較

---

## 🧪 過去テスト履歴（results/）

### 重要なテスト結果
| ファイル | 概要 | スコア |
|---------|------|-------|
| `test_gpt_v2.4_prodON_20260416_173251.xlsx` | 本番モード（FORCED_TEMPLATE有効） | **19.5/25** |
| `test_gpt_v2.4_prodOFF_20260416_173615.xlsx` | FORCED_TEMPLATE除去 | **21.5/25 (+2.0pt)** |
| `test_gpt5mini_gpt41nano_gpt5nano_v2.4_20260415_211256.xlsx` | v2.4 3モデル比較 | — |
| `test_gpt_gpt5mini_gpt5nano_gpt41nano_gemini_v2.3_20260415_190920.xlsx` | v2.3 5モデル比較 | — |

---

## 📂 gpt_request_1〜10.json

**重要**：`services/baychat/ai/gpt_request_*.json` は **2026-03時点のステージング環境データ**。  
- セラー自動メッセージが含まれる（本番ではセラー自動メッセージはAIに渡らない仕様）
- 2026-03-20 に本番データを再依頼済み、到着待ち（CLAUDE.md参照）

**サイズ・内容**：
| ファイル | サイズ | メッセージ数 | 内容 |
|---------|-------|-----------|------|
| gpt_request_2.json | 12 KB | 8 | キャンセル→住所確認→解決 |
| gpt_request_3.json | 12 KB | 6 | 返品（サイズ合わず） |
| gpt_request_5.json | 11 KB | 5 | 発送日問い合わせ |
| gpt_request_9.json | 15 KB | 28 | 最長の会話 |

---

## 🔧 補助スクリプト

| スクリプト | 用途 |
|----------|------|
| `compare_cases.py` | 複数プロンプト版で同じケース実行・比較 |
| `compare_models.py` | GPT / Gemini / Claude を同一条件で比較（APIキー未設定モデルはスキップ） |
| `run_all_tests.py` | gpt_request_*.json を固定プロンプト版で全実行 |
| `render_reply_comparison.py` | ExcelからHTML比較レポート生成 |
| `render_summary_view.py` | スコア集計をHTML棒グラフ化 |
| `_speed_analysis.py` | レスポンス速度分析 |
| `_summarize_results.py` | 結果集計 |

---

## ⚠️ 注意事項

- **DBスキーマ変更時**：`extract_cases.py` の SQL を要修正
- **API仕様変更時**：`payload_builder.py` を要修正
- **新モデル追加時**：`batch_test.py` の モデル分岐を要追加
- **審判プロンプト変更時**：過去の採点結果との比較不可に

---

## 📚 関連ドキュメント

| ドキュメント | 役割 |
|----------|------|
| `00_overall_flow.md` | 本番実装との対応 |
| `11_model_selection.md` | モデル選定経緯 |
| `13_baychat_api_spec.md` | 本番API仕様 |
| `05_changelog.md` | テスト実行履歴記録 |
