# ブロックカード：[N+5] FORCED_TEMPLATE（🔴 **廃止済み**）

> 🔴 **廃止済み（2026-04-22 Cowatech prd反映）**
> Cowatechにより FORCED_TEMPLATE ブロック生成ロジックが stg+prd の両環境で削除された（2026-04-22 23:58 完了）。
> 挨拶・署名制御は [N+4] admin_prompt の GREETING & SIGNATURE POLICY セクションへ移管。
> 本カードは**履歴・経緯の記録用**として保存。新規の実装・議論は `block_n4_admin_prompt.md` を参照。

---

## 📇 基本情報（廃止時点の記録）

| 項目 | 内容 |
|------|------|
| **ブロックID** | `forced_template` |
| **順序** | [N+5]（最後尾） |
| **role** | `developer` |
| **管理主体** | Cowatech |
| **廃止日** | **2026-04-22 23:58（stg+prd同時反映）** |
| **廃止理由** | 2026-04-16テストで除去により +2.0pt 品質改善を確認。挨拶・署名制御をadmin_prompt側に集約することで柔軟な状況判断が可能になるため |
| **挨拶・署名の代替注入経路** | **[N+4] admin_prompt に `{buyerAccountEbay}` / `{sellerAccountEbay}` プレースホルダを注入する方式に移行** |
| **実物ファイル（参考）** | `SUMMARY_PROMT.csv`（tone別全原文・廃止時点の仕様） + `gpt_api_payload.txt`（実本番・polite版・廃止前の実例） |
| **変更頻度** | ❌ 廃止済み |
| **ON/OFF** | ❌ 常時OFF（ブロック自体が生成されない） |
| **概算トークン** | ~70 tokens（廃止により削減） |

---

## 🎯 このブロックの目的

AIの出力を **`Hello {buyer_name}, ... Best regards, {seller_name}`** 形式に**絶対強制**する。
TO（宛先）/ FROM（署名）プルダウンで選ばれたUI値がここに注入される唯一の経路。

---

## 📐 tone別3バリエーション（完全原文）

### ▼ polite版（丁寧） — `SUMMARY_PROMT.csv`由来

```text
The response MUST ABSOLUTELY adhere to the following format.
  Do not add explanations, markdown, or extra text.

  Hello {buyer_name},
  {output_content}

  Best regards,
   {seller_name}

  Replace the placeholders with actual values.
  seller_name: {{user select in sreen}}
  buyer_name: {{user select in sreen}}

  ABSOLUTELY: Always ensure that the output of the .jpn Language
  and the buyer Language adhere to the above format.
```

**本番実例**（`gpt_api_payload.txt` [13]、seller_name=`rioxxrinaxjapan` / buyer_name=`michkuc_71`）：
```text
The response MUST ABSOLUTELY adhere to the following format.
  Do not add explanations, markdown, or extra text.

  Hello {buyer_name},
  <Break line here>{output_content}<Break line here>
  Best regards,
   {seller_name}

  Replace the placeholders with actual values.
  seller_name: rioxxrinaxjapan
  buyer_name: michkuc_71


  ABSOLUTELY: Always ensure that the output of the .jpn Language
  and the buyer Language adhere to the above format.
```

**⚠️ 差分**：本番のpolite版は仕様書（SUMMARY_PROMT.csv）には無い `<Break line here>` 記述が含まれている。実装と仕様書の**齟齬が存在する**。

### ▼ friendly版（フレンドリー）— `SUMMARY_PROMT.csv`由来

```text
The response MUST ABSOLUTELY adhere to the following format.
  Do not add explanations, markdown, or extra text.

  Hello {buyer_name},
  <Break line here>{output_content}<Break line here>
  Best,
   {seller_name}

  Replace the placeholders with actual values.
  seller_name: rioxxrinaxjapan
  buyer_name: virgimax_pop

  ABSOLUTELY: Always ensure that the output of the .jpn Language
  and the buyer Language adhere to the above format.
```

**⚠️ 問題**：`seller_name: rioxxrinaxjapan` / `buyer_name: virgimax_pop` が**固定値**で仕様書に書かれている。本来UI選択値に動的置換されるべき。仕様書のtypo or 実装時に置換漏れのリスクあり。

### ▼ apologetic版（謝罪）— `SUMMARY_PROMT.csv`由来

```text
The response MUST ABSOLUTELY adhere to the following format.
  Do not add explanations, markdown, or extra text.

  Hello {buyer_name},
  <Break line here>{output_content}<Break line here>
  {greeting},
   {seller_name}

  Replace the placeholders with actual values.
  seller_name: kapital_japan
  buyer_name: phu_8417
  greeting: If the buyer's message seems angry, replace it with 'Sincerely';
            otherwise, replace it with 'Kind regards'

  ABSOLUTELY: Always ensure that the output of the .jpn Language
  and the buyer Language adhere to the above format.
```

**⚠️ 問題**：
- `seller_name: kapital_japan` / `buyer_name: phu_8417` も**固定値**（本来UI値のはず）
- `{greeting}` の判定は **AIが行う**（「buyerが怒っていれば Sincerely、そうでなければ Kind regards」）

---

## 🎛️ 動的プレースホルダ

| プレースホルダ | 置換元 | 置換タイミング | 空のときの挙動 |
|--------------|--------|------------|------------|
| `{buyer_name}` | UI「TO」プルダウン | ペイロード組立時（BayChat側） | 🔴 不明（Cowatech確認要・Q3） |
| `{seller_name}` | UI「FROM」プルダウン | ペイロード組立時（BayChat側） | 🔴 不明（Cowatech確認要・Q3） |
| `{output_content}` | AIが生成する本文 | AI生成時 | AIが本文を埋める |
| `{greeting}` | 条件分岐（apologeticのみ） | AI生成時 | 怒り判定で `Sincerely` or `Kind regards` を選択 |

### UI値の注入ポイント（polite版の例）

1. 冒頭 `Hello {buyer_name},`
2. 末尾 `Best regards, {seller_name}`
3. 末尾注意書き `seller_name: xxx` / `buyer_name: xxx`

**→ 同一の値が3箇所に登場する**。BayChat側でいずれも同じ値に置換する必要あり。

---

## 🧪 品質検証結果（2026-04-16）

### FORCED_TEMPLATE ON vs OFF の12ケーステスト

| モード | 平均スコア | コスト合計 |
|-------|--------|--------|
| ON（現行本番） | 19.5 / 25 | ¥3.02 |
| **OFF（除去）** | **21.5 / 25** | ¥2.85 |
| 差分 | **+2.0pt** | -¥0.17 |

### ケース別結果

| 結果 | ケース数 |
|------|--------|
| 改善 | 10ケース |
| 同点 | 0ケース |
| 悪化 | 1ケース（prettypoodle1234：税関トラブル返品） |

### なぜOFFの方が良いか
- admin_prompt v2.4 は「状況判断で挨拶・結句を柔軟にせよ」と指示
- FORCED_TEMPLATEは状況無視で形式強制 → 短い御礼メッセージにも重い形式を被せて不自然
- v2.4 は「状況適応できる設計」なので、FORCED_TEMPLATE除去で本来の力を発揮

### 唯一の悪化ケース（prettypoodle1234）の意味
- カテゴリ：cancel（税関トラブル→返品→返金待ち）
- ON版：FORCED_TEMPLATE の署名があることで丁寧さスコア向上（+3pt）
- OFF版：署名が自然判断に任され、簡略化されて減点
- **→ TO/FROM値の動的注入経路をOFF版にも設計する必要がある（Q1）**

---

## 🌐 影響範囲

### 直接影響する要素
- AI出力の冒頭挨拶・結句・署名
- TO/FROM UI値の反映
- tone選択の最終効果

### 間接影響する要素

#### admin_prompt v2.4 との競合
admin_prompt v2.4 のルール：
> "Force a rigid 'Hello {buyer_name}, ... Best regards, {seller_name}' template when the situation does not call for it. For casual short exchanges, a lighter opening and closing is appropriate."

FORCED_TEMPLATE のルール：
> "The response MUST ABSOLUTELY adhere to the following format."

→ **2つのdeveloperブロックが矛盾する命令を出している**

### 副作用のリスク
- このブロックを除去すると、TO/FROMのUI値をAIに渡す経路が消える（最大のリスク）
- friendly/apologetic版のサンプル固定値（`rioxxrinaxjapan`等）が置換漏れしていると literal として送信される

---

## 🔀 TO/FROM問題の解決案3つ（`handoff_20260416_results.md` 由来）

| 案 | 方法 | 利点 | 課題 | 実装難度 |
|----|------|------|------|--------|
| **A** | admin_promptに `{buyerAddress}` `{sellerSignature}` を追加、末尾INPUTSで注入 | admin_prompt側で柔軟ハンドリング可能 | Cowatech側でプレースホルダ追加実装 | 中 |
| **B** | FORCED_TEMPLATEを「強制」→「参考ヒント」に書き換え | Cowatech変更最小 | AIが無視する可能性大。+2.0pt改善が失われるリスク | 低 |
| **C** | BASE_PROMPTに `Greeting target: {buyerAddress}, Signature: {sellerSignature}` を注入 | admin_promptと分離 | BASE_PROMPT=Cowatech管理のため変更必要 | 中 |

**現在の推奨**：**案A**（admin_prompt側でコントロール・+2.0pt 改善を維持）

---

## 📜 バージョン履歴

| Ver | 日付 | 主な変更 | きっかけ |
|-----|-----|--------|------|
| v1 | プロジェクト初期 | tone別3バリエーション確立 | ペイロード設計 |
| 検証中 | 2026-04-16 | 除去で+2.0pt改善確認 | admin_prompt v2.4との整合性検証 |
| **廃止** | **2026-04-22 23:58** | **stg+prd同時反映で完全削除** | **Cowatech実装完了（Slack thread_ts `1776427836.602699` クエットさん返信）** |

---

## ✅ 解決済み論点（廃止時点で決着）

| # | 論点 | 解決内容 |
|---|-----|------|
| ~~Q1~~ | ~~FORCED_TEMPLATE除去時のTO/FROM値の代替注入経路~~ | ✅ **2026-04-22 解決**：admin_promptに `{buyerAccountEbay}` / `{sellerAccountEbay}` を注入する方式でCowatech実装完了 |
| ~~Q3~~ | ~~TO/FROM「なし」選択時の挙動~~ | ✅ **2026-04-22 解決**：UI選択値（ID/氏名/担当者名/なし）がそのまま動的置換される。「なし」選択時は空文字で置換され、admin_promptの「WHEN A PLACEHOLDER IS EMPTY」ルールで挨拶・署名が省略される |
| ~~Q5~~ | ~~除去時のBayChat側の副作用~~ | ✅ **2026-04-22 解決**：Cowatech側で除去に伴う副作用も対応済み（stg+prd両環境で動作確認） |
| ~~—~~ | ~~friendly/apologetic版の固定値（rioxxrinaxjapan等）の置換漏れ~~ | ✅ ブロック自体廃止により解消 |
| ~~—~~ | ~~`<Break line here>` 記述の仕様書⇔本番齟齬~~ | ✅ ブロック自体廃止により解消 |
| ~~—~~ | ~~`{greeting}` の怒り判定をAIに任せる信頼性~~ | ✅ admin_prompt側の EMPATHY ENFORCEMENT / TONE GUIDELINES で AI判断を明示化（v2.6） |

---

## 🤝 Cowatech合意事項（廃止時点の記録）

| 項目 | 合意内容 | 合意日 | 根拠 |
|------|--------|------|------|
| 配置順序 | [N+5] 最後尾 | プロジェクト初期 | `gpt_api_payload.txt` |
| tone別選択 | polite/friendly/apologetic の3種から1つ注入 | プロジェクト初期 | `SUMMARY_PROMT.csv` |
| プレースホルダ置換 | BayChat側で実施 | 2026-03-21 | Slack履歴 |
| 🆕 **ブロック廃止** | **stg+prd両環境で FORCED_TEMPLATE 生成ロジック削除** | **2026-04-22 23:58** | **Slack thread_ts `1776427836.602699` クエットさん返信「対応してstgとprdに反映済み」** |

---

## 📚 関連ドキュメント

| ドキュメント | 役割 |
|----------|------|
| `SUMMARY_PROMT.csv` | tone別3バリエーションの仕様書 |
| `gpt_api_payload.txt` | 本番実装（polite版）の実物 |
| `handoff_20260416_results.md` | +2.0pt改善検証の詳細 |
| `slack_draft_20260416.md` | Cowatech向け相談草案（未送信） |
| `09_open_questions.md` | Q1の詳細・選択肢比較 |
| `block_n4_admin_prompt.md` | 競合関係の分析 |
