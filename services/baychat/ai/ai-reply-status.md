# AI Reply 開発状況（最重要開発案件）

> 親: `services/baychat/ai/CLAUDE.md` から「必要時ロード」として参照される詳細ファイル。
> 設計図は `design-doc/` 配下（22ファイル・v0.2・単一参照源）。
> BayChat AI Reply 進行時は memory `feedback_baychat_ai_reply_stance.md` の5原則を厳守。

---

## 現状（2026-04-20 夜時点）

- **設計図**: `services/baychat/ai/design-doc/` 22ファイル・v0.2完成（AI Reply全仕様の単一参照源・HTMLプレビュー `_html_preview/dashboard.html`）
- **テスト環境**: 動作中（社内のみ）・DB接続完了・大量テスト可能
- **使用AIモデル（本番）**: GPT-4.1-Mini Standard（`gpt-4.1-mini-2025-04-14`）
- **次期モデル候補**: Gemini 2.5 Flash（2026-03-19 採用方針決定・Cowatech実装待ち）
- **プロンプト**: **v2.4 本番運用中 / v2.5 ドラフト作成済み**（`prompt_admin_v2.5.md` — FORCED_TEMPLATE除去前提・GREETING & SIGNATURE POLICY新設）
- **本番ペイロード再現インフラ**: `testing/payload_builder.py`で本番同構造テスト可能
- **FORCED_TEMPLATE除去検証**: 12ケース平均スコア **19.5→21.5（+2.0pt）** 改善を確認
- **Cowatech相談中**: Q1+Q3（FORCED_TEMPLATE除去・TO/FROM再設計）を Slack thread_ts: 1776427836.602699 で送信済 — Cowatech実装対応中
- **残タスク**: eBay API連携（Cowatech対応完了待ち）

---

## 🆕 2026-04-22 更新

- **次期仮決定モデル**: **GPT-5-Nano**（admin画面で社長が直接切替可能・Cowatech依頼不要）
- **優先度最低**: Gemini 2.5 Flash（速度4秒超で体感NG・Cowatech実装要・コスト高で除外）
- **最新プロンプト**: **v2.6 ドラフト**（`prompt_admin_v2.6.md` — EMPATHY/MULTILINGUAL/COMPLEX CASE 新設）
- **Cowatechプレースホルダ先行共有**: `{sellerAccountEbay}` `{buyerAccountEbay}`
- **合成40ケーステスト（2026-04-22）実施**: v2.6 で Gemini 19.85 / GPT-5-Nano 19.05 / GPT-4.1-Mini 18.77（18件より-3ptで「途中対応」の真の難易度判明）

---

## 🆕🆕 2026-04-23 朝 更新（最新）

- **Cowatech stg+prd 反映完了**（2026-04-22 23:58）：FORCED_TEMPLATE除去＋プレースホルダ `{sellerAccountEbay}/{buyerAccountEbay}` 注入対応。UI動的置換もクエットさん確認済
- **ただし admin画面のプロンプトは依然v2.4**（社長が v2.6 アップロードするまで動作変わらず）
- **🔴 設計図同期問題が顕在化**：社長指摘「Cowatech側がコード更新したから設計図も更新必要＋共有・更新管理の方法を考える必要」
- **現状のズレ**：Cowatech命名 `{sellerAccountEbay}/{buyerAccountEbay}` vs 設計図想定 `{buyer_name}/{seller_name}`。設計図22ファイルはCowatechに未共有
- **次セッション判断待ち**：進め方X/Y/Z・共有方法A/B/C/D・お礼Slack返信タイミング
- **次セッション冒頭必読**: `services/baychat/ai/handoff_20260423_cowatech_prd_sync.md`

---

## 本番ペイロード構造（2026-04-16 完全解明）

Cowatechから入手した`gpt_api_payload.txt`と仕様スプレッドシート19シートを解析：

```
[0] 商品情報JSON（developer）
[1..N] チャット履歴（user/assistant交互）
[N+1] description guide（descriptionが空でない場合のみ）
[N+2] BASE_PROMPT（developer）
[N+3] OUTPUT_FORMAT（developer）
[N+4] admin prompt（developer）← 社長がadmin画面で設定
[N+5] FORCED TEMPLATE（developer）← tone別にHello/Best regards等を強制
```

- temperature=0.2 / json_schema strict / response_format: `multi_language_reply`

---

## オフラインテスト環境（services/baychat/ai/testing/）

| ファイル | 役割 |
|---------|------|
| `payload_builder.py` | 本番と同構造でAPI messagesを組立（4 developer blocks＋chat history） |
| `batch_test.py` | メインエンジン（`--production-payload`で本番再現モード） |
| `ai_judge.py` | AI審判（5項目×5点、25点満点） |
| `db_connect.py` | SSHトンネル＋MariaDB接続 |
| `extract_cases.py` | DBからテストケース抽出 |

---

## モデル選定結論（2026-03-19）

**採用方針: Gemini 2.5 Flash（Google）**

| 比較項目 | GPT-4.1-Mini（現在） | Gemini 2.5 Flash（次期） |
|----------|---------------------|------------------------|
| 生成速度 | 10秒以上かかる場合あり | 1〜2秒（圧倒的に速い） |
| 品質 | 良好 | GPT-5相当（Pro級） |
| 1ユーザー月額（5回/日×30日） | 約¥24 | 約¥15 |
| 実装 | OpenAI（現在対応済み） | Cowatechへ確認・依頼が必要 |

### 結論の根拠

- GPT-5-Mini Priority でテスト → 速度10秒でNG
- Gemini 2.5 Flash は GPT-5 級の品質・速度1〜2秒・コストはGPT-4.1-Miniより安い
- 1ユーザーあたり約¥15/月（AI Reply オプション ¥2,200 に対してコストは問題なし）
- **コストを下げながら品質を上げられる唯一の選択肢**

※2026-04-22 以降は Gemini 2.5 Flash 優先度を下げ、GPT-5-Nano を次期仮決定（速度体感NG問題のため）。

---

## 選択可能なAIモデル一覧（2026-03-19時点）

### OpenAIモデル

| モデル | プラン | Input | Output | 備考 |
|--------|--------|-------|--------|------|
| GPT-5 | Standard | $1.25 | $10.00 | 最高品質・最高コスト |
| GPT-5 | Priority | $2.50 | $20.00 | |
| GPT-5-Mini | Standard | $0.25 | $2.00 | 速度18秒でNG（テスト済み） |
| GPT-5-Mini | Priority | $0.45 | $3.60 | 速度10秒でNG（テスト済み） |
| GPT-5-Nano | Standard | $0.05 | $0.40 | |
| **GPT-4.1-Mini** | **Standard** | **$0.40** | **$1.60** | **← 現在使用中** |
| GPT-4.1-Mini | Priority | $0.70 | $2.80 | |
| GPT-4.1-Nano | Standard | $0.10 | $0.40 | 日本語品質に課題あり（テスト済み） |
| GPT-4.1-Nano | Priority | $0.20 | $0.80 | |
| o4-Mini | Standard | $1.10 | $4.40 | |
| o4-Mini | Priority | $2.00 | $8.00 | |
| GPT-4o-Mini | Standard | $0.15 | $0.60 | 旧モデル |
| GPT-4o-Mini | Priority | $0.25 | $1.00 | 旧モデル |

### Googleモデル（Cowatech実装確認が必要）

| モデル | Input | Output | 備考 |
|--------|-------|--------|------|
| **Gemini 2.5 Flash** | **$0.075** | **$0.30** | Pro級品質・速度1〜2秒 |
| Gemini 2.0 Flash | $0.10 | $0.40 | 速い・安い・品質良好 |
| Gemini 2.5 Pro | $1.25 | $10.00 | 最高品質・コスト高 |

### Anthropic（Claude）モデル（Cowatech実装確認が必要）

| モデル | Input | Output | 備考 |
|--------|-------|--------|------|
| Claude 3.5 Haiku | $0.80 | $4.00 | 速い・高品質だがコストはGPT-4.1-Miniより高い |
| Claude 3.7 Sonnet | $3.00 | $15.00 | 最高品質・コスト高 |

### 速度問題への対応方針（2026-03-19 更新）

- GPT-4.1-Mini Standardで生成に10秒以上かかる場合がある（速度問題）
- **最優先対応**: Gemini 2.5 Flash への切り替え（速度・品質・コストすべて改善）
- 切り替えにはCowatechでのGoogle AI API実装が必要 → クエットさんへ確認依頼
- 現状維持の場合の次善策: ストリーミング表示（文字を逐次表示→体感待ち時間を大幅削減）

---

## プロンプト管理構成

| 種別 | 管理者 | 変更頻度 | 内容 |
|---|---|---|---|
| ベースプロンプト | Cowatech | ほぼ変えない | 出力形式（JSON）・eBayコンプライアンスのみ |
| adminプロンプト | 下元さん（admin画面） | 自由にいつでも | CS品質全般・トーン・会話フロー・補足情報統合 |

### 最新プロンプトファイル

- `prompt_admin_v2.6.md` ← **最新ドラフト（2026-04-22 EMPATHY/MULTILINGUAL/COMPLEX CASE新設・合成40ケーステスト実施済み・社長フィードバック待ち）**
- `prompt_admin_v2.6.html` ← 社長レビュー用HTMLプレビュー
- `prompt_admin_v2.6.json` ← admin画面アップロード用
- `prompt_admin_v2.5.md` ← v2.5 ドラフト（FORCED_TEMPLATE除去前提・GREETING & SIGNATURE POLICY新設）
- `prompt_admin_v2.4.md` ← 本番運用中（2026-04-15 復唱禁止・挨拶対応・URL対応・テンプレート緩和）
- `prompt_admin_v2.3.md` ← 旧版（GPT APIテスト済み）
- `prompt_admin_v2.2.md` ← 旧版
- `prompt_admin_v2.1.md` ← 旧版
- `prompt_admin_v1.md` ← 旧版（参照不要）

### プロンプト開発ルール（2026-03-21 確立）

- **修正したらGPT APIでテストしてから社長に提出する**（`test_prompt_quick.py`を使用）
- ルールで縛るのではなくAIの判断力に委ねる設計方針
- 特定シナリオごとの具体ルールは追加しない
- 品質基準の例は「シナリオ別ルール」ではなく「期待レベルの提示」として使う

---

## AI Reply 改善サイクル（継続ループ）

```
① Claudeがプロンプトを改善・テスト
       ↓
② 社長が実際にテストして評価
       ↓
③「もっとこうしたい」をClaudeに伝える
       ↓
④ ①に戻る（継続ループ）
```

---

## テストデータ取得状況

- 2026-03-19：クエットさんからgpt_request_1〜10.json（10ケース）を受領・ローカルに保存済み
- **⚠️ ただしステージング環境のデータ**：自動メッセージ（セラー側）が含まれており正確なテスト不可
- 本番ではセラーの自動メッセージはAIに渡らない仕組み（Cowatech確認済み）
- 2026-03-20：**本番環境のテストデータを再依頼済み**（クエットさんへSlack送信・社長GOあり）
- 本番データ到着後に全テストを再実施する予定

---

## 今後実装したいAI機能（優先順）

1. **AI Reply**（最優先・プロンプト完成次第リリース）
   - バイヤーへの返信文を自動生成
2. **要約・状況整理機能**（次のフェーズ）
   - バイヤーの長文メッセージを要約
   - 「何を求めているか」を整理
   - 「どんな対応が必要か」を提示
   - セラーの意思を確認して返信文に落とし込む
