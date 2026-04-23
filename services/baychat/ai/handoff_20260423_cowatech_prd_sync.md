# BayChat AI Reply — 次セッション引き継ぎ（2026-04-23 朝）

> **新セッション冒頭でこのファイルを最初に読むこと。**
> 続いて `memory/feedback_baychat_ai_reply_stance.md` の5原則を読む。

---

## 🎯 現在地サマリー

| 項目 | 状態 |
|------|-----|
| **フォルダ構成** | `services/baychat/ai/` 配下（リファクタ済み） |
| **設計図** | v0.2 完成（22ファイル）だが **Cowatech実装と乖離発生中** |
| **admin_prompt 最新ドラフト** | v2.6（`prompt_admin_v2.6.md`） |
| **仮決定モデル** | GPT-5-Nano（admin画面で社長が直接切替可能） |
| **Cowatech prd 反映状態** | **🆕 FORCED_TEMPLATE除去＋プレースホルダ対応が本番に反映済み（2026-04-22 23:58）** |
| **設計図 ↔ Cowatech共有** | **未実施**（本件の論点） |

---

## 🚨 本セッション（2026-04-23 朝）で判明した重要事実

### クエットさん Slack 返信 2件（thread_ts `1776427836.602699`）

**① 2026-04-22 23:13**:
> 「ご認識通りです。」

→ `{sellerAccountEbay}` `{buyerAccountEbay}` は UI signature/receiver 選択（ID/氏名/担当者名/なし）に応じて動的置換される、の認識で正解。

**② 2026-04-22 23:58**:
> 「対応してstgとprdに反映済みです。」

→ **ステージング（stg）と本番（prd）両方に既に実装反映完了**。

### 実装変更の内容（Cowatech側）
- FORCED_TEMPLATE ブロック生成ロジック削除
- admin_prompt内に `{sellerAccountEbay}/{buyerAccountEbay}` プレースホルダ注入の仕組み追加
- UI の signature/receiver 選択値で動的置換

### 現行動作（今の本番）
- Cowatech インフラは v2.5/v2.6 対応済み
- **ただし admin画面に登録されているプロンプトは依然として v2.4**（プレースホルダなし）
- → 社長が v2.6 を admin にアップロードしない限り、動作は v2.4 のまま
- → 社長がアップロードすれば即 v2.6 + FORCED_TEMPLATE除去 本番稼働

---

## 🔴 社長の重大な指摘（2026-04-23 朝）

> 「Cowatech側がコードを更新したのであれば設計図も更新しないといけません。
> まず設計図を完成させた上でお互いどうやって共有するのか、更新管理するのかを考えないといけません。」

### 現状のズレ

| 領域 | 現状 |
|------|-----|
| Cowatech prd 実装 | FORCED_TEMPLATE除去済み・プレースホルダ `{sellerAccountEbay}/{buyerAccountEbay}` 実装済み |
| Reffort 設計図 v0.2 | プレースホルダ想定名が `{buyer_name}/{seller_name}`（Cowatech命名と違う） |
| Cowatech ↔ 設計図共有 | **一度も共有していない** |

→ このままでは「設計図＝唯一の参照源」は機能しない。

---

## 🚀 新セッション冒頭で最初にやること

### 1. このファイル + 5原則を読む
```
services/baychat/ai/handoff_20260423_cowatech_prd_sync.md  ← このファイル
memory/feedback_baychat_ai_reply_stance.md                  ← 5原則
```

### 2. 社長の判断を確認する（前セッションで3択を提示済み・社長判断待ち）

#### 進め方の3択
| 進め方 | 内容 |
|------|------|
| **X**（Claude推奨） | ステップ1を先行（設計図を最新化）→ 社長と共有方法を議論 → Cowatechに相談 |
| Y | 先にCowatechへ「お礼＋共有方法の相談」をSlack投げる → 返信見てから設計図最新化 |
| Z | ステップ1→2→3を今日全部（お礼Slack+共有方法提案も同時に） |

#### 共有方法の4択
| 案 | 利点 | 課題 |
|---|-----|-----|
| **A**（Claude推奨）: GitHub（`reffort-claude` private repo 共有） | 既存運用（毎日自動バックアップ）・git履歴で変更追跡・PR制可能 | Cowatechへアクセス権限付与必要 |
| B: Notion | 共同編集・コメント容易 | 新規契約・別管理になる |
| C: Google Drive | シンプル | バージョン管理弱い |
| D: Cowatech既存ツール | Cowatech負担ゼロ | Reffortから掌握できない |

#### クエットさんへのお礼返信
- 「ご認識通りの確認と本番反映ご対応ありがとうございます」
- Claude推奨：**即返信**（独立したお礼なのでどの進め方でも干渉しない）

---

## 📋 次セッションのタスク（社長判断後に実行）

### ステップ1：設計図の最新化（Claude作業・15-20分）

Cowatech prd実装の正式名に合わせて設計図を更新：

| 更新対象 | 変更内容 |
|---------|--------|
| `design-doc/03_block_cards/block_n4_admin_prompt.md` | プレースホルダ正式名を `{sellerAccountEbay}/{buyerAccountEbay}` に修正 |
| `design-doc/03_block_cards/block_n5_forced_template.md` | ステータス「**廃止済み（prd反映 2026-04-22）**」に変更 |
| `design-doc/04_conditional_logic.md` | 置換マトリクスをCowatech実装の正式命名に更新 |
| `design-doc/09_open_questions.md` | Q1/Q3 を「✅ 解決済み」に移動 |
| `design-doc/05_changelog.md` | 2026-04-22 Cowatech prd反映を記録 |
| `design-doc/01_prompt_blocks_overview.md` | FORCED_TEMPLATE行を「廃止」に |
| `prompt_admin_v2.6.md` | プレースホルダ名を Cowatech命名に統一 |
| HTML再生成 | `_html_preview/` と `prompt_admin_v2.6.html/.json` |

### ステップ2：共有・更新管理ルール策定（社長と議論）
- 共有場所（A/B/C/D）
- 更新フロー（誰がいつどう更新するか）
- 変更通知の方法
- Cowatechへの初回共有方法

### ステップ3：Cowatechと共有合意 → 初回同期
- Cowatechへの共有実施
- レビュー依頼
- 合意後、運用ルール本格稼働

---

## 📂 主要ファイル

### プロンプト
- `prompt_admin_v2.4.md` — 本番運用中
- `prompt_admin_v2.5.md` — v2.5 ドラフト
- `prompt_admin_v2.6.md` — 最新ドラフト（EMPATHY/MULTILINGUAL/COMPLEX CASE新設）
- `prompt_admin_v2.6.html` / `.json` — 社長レビュー用・admin画面アップロード用

### テスト環境（`testing/`）
- `generate_synthetic_cases.py` — 合成40シナリオ生成
- `regenerate_prepurchase.py` — 購入前バグ修正
- `payload_builder.py` — v2.5/v2.6 対応済み
- `batch_test.py` — prompt_version 渡し対応済み
- `render_v25_dashboard.py` — 社長向けダッシュボード
- `render_reply_comparison.py` — ケース別比較レポート（feedback textarea付き）

### テスト結果（最新）
- `results/test_gpt_gemini_gpt5nano_v2.6_merged_20260422.xlsx` — 40ケース最終マージ版
- `results/dashboard_test_gpt_gemini_gpt5nano_v2.6_merged_20260422.html`
- `results/comparison_20260422_011559.html` — **社長フィードバック作業用（ブラウザで開いている可能性）**

### 設計図（`design-doc/`）
- 22ファイル・v0.2完成（ただしCowatech prd反映前）
- **次セッションで最新化必要**

---

## ⚠️ 守ること（5原則・`feedback_baychat_ai_reply_stance.md`）

1. 設計図は理解済み前提で動く
2. Cowatechに聞く前に設計図から答えを出す
3. 論点リストを機械的に並べない
4. 議論の結論を草案に正確反映する
5. 経営パートナーとして社長の意図を汲む

---

## 📞 連絡先

- クエットさん（Cowatech）: `U04HGPBABQU`
- 社長: `U048ZRU4KLG`
- Slackチャンネル: `#baychat-ai導入` (C09KXK26J8G)
- スレッド: thread_ts `1776427836.602699`

---

## 📝 Claude への補足

### 社長のケース別フィードバック作業の状況
- `comparison_20260422_011559.html` で textarea に記入する作業が進行中の可能性
- 完了していれば JSON ダウンロード → v2.7 改善サイクルへ
- ただし本件（設計図共有）と並行で進められる

### 優先順位
1. 🔴 最優先：設計図とCowatech prdの乖離を解消（設計図最新化＋共有ルール確立）
2. 🟡 次：社長フィードバックを v2.7 に反映
3. 🟢 並行：お礼Slack返信

---

*作成: 2026-04-23 朝*
*目的: 新セッションで社長の判断（進め方X/Y/Z・共有方法A/B/C/D）を確認し、設計図とCowatech実装の同期＋共有ルール確立を完遂するため*
