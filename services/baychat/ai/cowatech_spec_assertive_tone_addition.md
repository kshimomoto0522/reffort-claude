# BayChat AI Reply — 4トーン化（主張トーン追加）仕様書

> 宛先: Cowatech 様
> 作成: 株式会社リフォート（Reffort, Ltd.）
> 作成日: 2026-05-05
> 関連: 既存実装（v2.4 系・FORCED_TEMPLATE 除去済み・プレースホルダ `{sellerAccountEbay}/{buyerAccountEbay}` 対応済み・stg + prd 反映済み 2026-04-22）

---

## 1. 概要・目的

現行の AI Reply 機能は 3 トーン（`polite` / `friendly` / `apologetic`）でリプライを生成しています。本改修により、**4つ目のトーン `assertive`（主張）** を追加します。

### 追加トーンの想定用途

バイヤーからの不当な主張（関税負担拒否、偽物クレーム、配送非のなすりつけ等）に対し、**丁寧だが下手に出ず毅然と対応する**文体で生成するためのトーンです。

既存3トーン（POLITE / FRIENDLY / APOLOGY）では、いずれも謝罪表現が混ざる傾向があり、「セラー側に非がない不当な主張」に対して下手に出てしまうケースがありました。これを補完するためのトーン追加です。

---

## 2. Cowatech 様への実装依頼スコープ

本仕様書で実装をお願いするのは以下 2 点のみです。

| # | 領域 | 概要 |
|---|---|---|
| (1) | データモデル | tone enum に `assertive` を追加（章 3） |
| (2) | API バリデーション | tone パラメータの受入値を 4 値に拡張（章 4） |

### 本仕様の対象外（Reffort 側で対応）

- **admin_prompt 本文の更新**: admin_prompt は Reffort 側で随時管理・差し替えを行います。Cowatech 様への登録依頼は不要です。新トーン定義（`assertive`）も Reffort 側で admin_prompt に追加した上で、admin 画面から登録します。
- **UI の見た目・配置**: 別途 Reffort 側で要件をお伝えします。

---

## 3. データモデル変更

### 3.1 tone enum の拡張

| 現行 | 変更後 |
|---|---|
| `polite` / `friendly` / `apologetic`（3個） | `polite` / `friendly` / `apologetic` / **`assertive`**（4個） |

- DB マイグレーション: 既存ユーザの過去 tone 値に影響なし（新規選択肢を追加するのみ）
- 新規ユーザのデフォルト値: 既存通り `polite`

---

## 4. API インターフェース

### 4.1 リクエスト

AI Reply 生成エンドポイントの `tone` パラメータの受入値を 4 値に拡張します。

```json
{
  "tone": "polite | friendly | apologetic | assertive",
  "...（既存パラメータ）..."
}
```

### 4.2 バリデーション

`tone` パラメータが上記 4 値以外の場合、既存挙動と同じく 400 Bad Request を返してください（既存仕様と同じ挙動・新規追加の検証ロジックなし）。

### 4.3 レスポンス

既存仕様（`{ "jpnLanguage": "...", "buyerLanguage": "..." }`）から変更なし。

---

## 5. テスト観点（QA）

| # | 観点 | 期待挙動 |
|---|---|---|
| 1 | tone=`assertive` でリプライ生成 | リクエストは正常受理され、admin_prompt 内 ASSERTIVE 定義に従った英文 + 日本語訳が返る |
| 2 | tone=`polite` / `friendly` / `apologetic`（既存3トーン） | 改修前と完全に同一の応答が返る（後方互換性） |
| 3 | tone に未定義値（例: `aggressive`）を指定 | 400 Bad Request（既存挙動と同じ） |

---

## 6. 後方互換性・デフォルト挙動

| 項目 | 内容 |
|---|---|
| 既存ユーザの保存済みトーン値（polite/friendly/apologetic）| 影響なし・そのまま動作 |
| 既存 stg / prd デプロイへの影響 | 改修反映後も既存3トーンで呼び出せば改修前と完全同一の応答 |
| admin_prompt の差し替えタイミング | Reffort 側で別途実施（admin 画面から登録）。Cowatech 様の API 改修と同時に実施しなくても問題なし |

---

## 7. 実装順序の推奨

1. tone enum 拡張（DB マイグレーション）
2. API バリデーション拡張（4 値受入）
3. stg で動作確認（章 5 のテスト観点）
4. prd 反映

---

## 8. 工数・見積依頼

本仕様の実装にかかる工数とコストの見積を Slack スレッドにて頂戴できますと幸いです。

不明点・仕様確認が必要な箇所があれば、Slack thread にてご連絡ください。

以上、よろしくお願いいたします。

株式会社リフォート（Reffort, Ltd.）
代表取締役　下元 敬介
