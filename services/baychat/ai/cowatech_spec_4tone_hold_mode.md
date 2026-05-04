# BayChat AI Reply — 4トーン化 + 保留モード追加 仕様書

> 宛先: Cowatech 様
> 作成: Reffort 株式会社
> 作成日: 2026-05-04
> 関連: 既存実装（v2.4 系・FORCED_TEMPLATE 除去済み・プレースホルダ `{sellerAccountEbay}/{buyerAccountEbay}` 対応済み・stg + prd 反映済み 2026-04-22）

---

## 1. 概要・目的

現行の AI Reply 機能は 3 トーン（`polite` / `friendly` / `apologetic`）でリプライを生成しています。本改修により、以下 2 つの機能を追加します。

1. **4つ目のトーン `assertive`（主張）の追加**
   - バイヤーからの不当な主張（関税負担拒否、偽物クレーム、配送非のなすりつけ等）に対し、丁寧だが下手に出ず毅然と対応する文体を生成
2. **保留モード（hold_mode）の追加**
   - 「即答せず、後ほど確認の上で連絡する」旨の応答を生成するモード
   - 既存4トーンとは独立した直交軸として動作

これにより、ユーザー（セラー）は **「文体（4トーン）」と「対応スタンス（即答／保留）」を独立して選択** できるようになります。これは BayChat ならではの差別化機能となります。

---

## 2. データモデル変更

### 2.1 tone enum の拡張

| 現行 | 変更後 |
|---|---|
| `polite` / `friendly` / `apologetic`（3個） | `polite` / `friendly` / `apologetic` / **`assertive`**（4個） |

- DB マイグレーション: 既存ユーザの過去 tone 値に影響なし（新規選択肢を追加するのみ）
- 新規ユーザのデフォルト値: 既存通り `polite`

### 2.2 hold_mode フラグの追加

| 項目 | 値 |
|---|---|
| 型 | `boolean` |
| デフォルト | `false`（即答モード） |
| 永続化（ユーザー選好への保存） | **しない**（毎回 `false` から開始） |

理由: 保留はその場限りの一時的な対応選択であり、ユーザー個別のデフォルト設定として保存すべきではないため。

---

## 3. API インターフェース

### 3.1 リクエスト

AI Reply 生成エンドポイントに `hold_mode` パラメータを追加します。

```json
{
  "tone": "polite | friendly | apologetic | assertive",
  "hold_mode": false,
  "...（既存パラメータ）..."
}
```

### 3.2 バリデーション

以下の組み合わせは **API 側で 400 Bad Request を返す**（仕様矛盾）：

```
tone == "assertive" AND hold_mode == true  → 拒否
```

理由: 「毅然と主張する」と「保留する」は意味的に矛盾するため、UI 側でも grayed out とし、バックエンドでも二重防御として弾く設計です。

### 3.3 レスポンス

既存仕様（`{ "jpnLanguage": "...", "buyerLanguage": "..." }`）から変更なし。

---

## 4. admin_prompt の差し替え

### 4.1 差し替え元・先

| 項目 | 内容 |
|---|---|
| 現行（admin 画面登録中） | v2.4 系 |
| 改修後（差し替え） | **`prompt_admin_v2.3_baseline_natural3_assertive.md`**（4 トーン定義込み・本仕様書添付） |

※ 本ファイルの ` ``` ` ブロック内のテキスト全文を admin_prompt として登録。

### 4.2 プレースホルダ

既存仕様と同一（変更なし）：

| プレースホルダ | 値 |
|---|---|
| `{toneSetting}` | `polite` / `friendly` / `apologetic` / `assertive` のいずれか |
| `{sellerSetting}` | UI の補足入力 description（空なら本文字列のまま残す） |
| `{buyerAccountEbay}` | UI 「TO」選択値（既存実装通り） |
| `{sellerAccountEbay}` | UI 「FROM」選択値（既存実装通り） |

### 4.3 hold_mode の処理（重要・新規）

`hold_mode == true` の場合、admin_prompt の **末尾**（developer ロール最後の admin_prompt メッセージ）に **以下のブロックを動的に追加挿入** してください。

#### 挿入位置

既存ペイロード構造（FORCED_TEMPLATE 除去後）：

```
[0]   developer : 商品情報JSON
[1..N] chat history
[N+1] developer : (任意) 補足情報ガイド
[N+2] developer : BASE_PROMPT
[N+3] developer : OUTPUT_FORMAT
[N+4] developer : admin_prompt（toneSetting置換後）
[N+5] developer : ★ HOLD_MODE_BLOCK（hold_mode == true の時だけ挿入）  ← 新規
```

#### 追加挿入する HOLD_MODE_BLOCK の内容（固定文字列）

```
--------------------------------
HOLD MODE — RESPOND WITH A HOLD/CONFIRMATION REPLY
--------------------------------
The seller has chosen to NOT answer the buyer's substantive question yet.

Generate a reply that:
- Acknowledges the buyer's message courteously, in the tone selected via {toneSetting}.
- States that we will check / confirm on our end and follow up.
- Does NOT attempt to answer the substantive question.
- Does NOT make specific promises about timing (no "within 24 hours", no specific dates).
- Stays under 4 sentences.

This OVERRIDES "HARD RULE (3) NO FUTURE PROMISES" for this single turn —
saying "we will follow up" or "we will get back to you" is REQUIRED, not
forbidden, when HOLD MODE is active.

Tone-specific guidance for HOLD MODE:
  POLITE:    "Thank you for your message. Let me confirm this on our end
              and get back to you shortly."
  FRIENDLY:  "Thanks for reaching out! Let me check on this and I'll
              follow up soon."
  APOLOGY:   "Thank you for your patience. We are looking into this and
              will follow up with you as soon as we have an update."

(ASSERTIVE + HOLD is rejected at the API layer and will not occur here.)
```

#### Cowatech 実装上の注意

- このブロックは **固定文字列**（環境変数化や DB 化は不要）
- `hold_mode == false` のときは挿入しない（既存挙動と完全に同じ）
- `{toneSetting}` プレースホルダはこのブロック内に含まれていますが、既存の admin_prompt 置換ロジックでそのまま置換されます（特別処理不要）

---

## 5. UI 機能要件（最小限）

UI の見た目・配置は Cowatech 様の判断にお任せします。ただし以下の機能要件は満たしてください。

### 5.1 トーン選択
- 4 択（`polite` / `friendly` / `apologetic` / `assertive`）から1つ選択
- 日本語表示: 丁寧 / フレンドリー / 謝罪 / **主張**
- デフォルト: ユーザー選好で保存された値（新規ユーザは `polite`）

### 5.2 保留モード切替
- ON / OFF の 2 値（boolean トグル等、形式は任意）
- 日本語ラベル例: 「保留モード（即答せず確認中の旨を返す）」
- **デフォルト: 常に OFF**（ユーザー選好として保存しない）

### 5.3 排他制御
- トーンが `assertive` に切り替えられた時、保留モードは **強制的に OFF** にし、UI 上で **選択不可（grayed out / disabled）** とする
- 保留モード ON の状態でトーンを `assertive` に切り替えた場合も、保留モードを自動 OFF にする

---

## 6. テスト観点

Cowatech 様の QA で以下を確認していただきたい項目です。

| # | 観点 | 期待挙動 |
|---|---|---|
| 1 | tone=`assertive` でリプライ生成 | 4 つ目の admin_prompt 内 ASSERTIVE 定義に従い、謝罪語を含まない毅然な英文 + 日本語訳が返る |
| 2 | hold_mode=`true` で各トーン（polite/friendly/apologetic）でリプライ生成 | バイヤーの実質的な質問に答えず、確認の上連絡する旨の応答が生成される |
| 3 | tone=`assertive` + hold_mode=`true` で API 呼び出し | 400 Bad Request が返る |
| 4 | hold_mode=`false`（既存挙動） | 改修前と完全に同一の応答が返る（後方互換性） |
| 5 | UI: トーンを assertive に切り替え | 保留モードが OFF になり、grayed out 表示 |
| 6 | UI: 保留モード ON のままトーンを assertive に切り替え | 保留モードが自動 OFF になる |

---

## 7. 後方互換性・デフォルト挙動

| 項目 | 内容 |
|---|---|
| 既存ユーザの保存済みトーン値（polite/friendly/apologetic）| 影響なし・そのまま動作 |
| `hold_mode` 未指定でリクエストが来た場合 | `false` として扱う |
| 既存の admin_prompt（v2.4 系）登録のままの場合 | 新版に差し替えるまで `assertive` は admin_prompt 側に未定義のため、生成品質低下の可能性あり → **admin 画面で natural3_assertive 版に差し替え必須** |

---

## 8. 添付ファイル

| ファイル名 | 内容 |
|---|---|
| `prompt_admin_v2.3_baseline_natural3_assertive.md` | 新版 admin_prompt 本文（` ``` ` ブロック内を admin 画面に登録） |
| `prompt_admin_v2.3_baseline_natural3_for_cowatech.txt` | 4 トーン版 admin_prompt のクリーン版テキスト（ヘッダ等を除いた本文のみ・参考） |

※ admin_prompt 本文に `assertive` トーン定義を含む `prompt_admin_v2.3_baseline_natural3_assertive.md` を後日改めて Slack で送付します。

---

## 9. 実装順序の推奨

1. tone enum 拡張 + hold_mode カラム追加（DB マイグレーション）
2. API バリデーション追加（assertive + hold_mode = true を弾く）
3. ペイロード組み立てロジックに HOLD_MODE_BLOCK 動的挿入処理を追加
4. UI: tone 4 択 + 保留トグル + 排他制御
5. stg で動作確認
6. admin 画面で新版 admin_prompt（natural3_assertive）に差し替え
7. prd 反映

---

## 10. 工数・見積依頼

本仕様の実装にかかる工数とコストの見積を Slack スレッドにて頂戴できますと幸いです。

不明点・仕様確認が必要な箇所があれば、Slack thread にてご連絡ください。

以上、よろしくお願いいたします。

Reffort 株式会社
