# 02. UI → プロンプト注入マトリクス

> このファイルの役割：**BayChat画面のUI操作が、AIに送られるプロンプトのどこに差し込まれるか**を一覧で見える化する。
> 「UIの〇〇を変えると、プロンプトの□□が変わって、AIの返信が△△になる」を1枚で把握するためのもの。

---

## 🎛️ UI操作項目の全リスト

| UI項目 | 場所 | 取りうる値 | 必須/任意 |
|-------|-----|---------|---------|
| TO（宛先） | AI Reply生成画面 | バイヤーID / バイヤー氏名 / なし | 任意 |
| FROM（署名） | AI Reply生成画面 | セラーID / セラー氏名 / 担当者名 / なし | 任意 |
| トーン | AI Reply生成画面 | polite（丁寧）/ friendly（フレンドリー）/ apologetic（謝罪） | 必須 |
| 補足情報 | AI Reply生成画面 | 自由入力テキスト | 任意 |
| 「AIで返信を生成」ボタン | AI Reply生成画面 | クリックのみ | — |

※上記は2026-04-20時点のUI。将来TO/FROM機能は再設計検討中（`handoff_20260416_results.md`参照）。

---

## 🎯 注入マトリクス（UI項目 × プロンプトブロック）

| UI項目 | 注入先ブロック | 注入箇所（プロンプト内の位置） | 置換プレースホルダ | 条件 |
|-------|-------------|---------------------------|---------------|------|
| **TO（宛先）** | [N+5] FORCED_TEMPLATE | 冒頭 `Hello {buyer_name},`<br/>末尾 `buyer_name: ...`の行 | `{buyer_name}` | 常時注入 |
| **FROM（署名）** | [N+5] FORCED_TEMPLATE | 末尾 `{seller_name}` 行<br/>末尾 `seller_name: ...`の行 | `{seller_name}` | 常時注入 |
| **トーン** | [N+4] admin_prompt | INPUTSセクションの `Tone: {toneSetting}` | `{toneSetting}` | 常時注入 |
| **トーン** | [N+5] FORCED_TEMPLATE | tone別に3バリエーションから選択<br/>（polite/friendly/apologetic） | テンプレート全体切替 | 常時注入 |
| **補足情報** | [N+4] admin_prompt | SELLER INTENTセクション `Seller intent ({sellerSetting})`<br/>INPUTSセクション `Seller intent: {sellerSetting}` | `{sellerSetting}` | 常時注入 |
| **補足情報** | [N+1] 補足情報ガイド | ブロック全体 | `{{Tone}}` / `{{User input in sreen}}` | **descriptionが空でない場合のみ** |

---

## 📍 具体例：返品リクエストへの返信を生成する場合

### セラーがUIで設定した値
- TO: `michkuc_71`（バイヤーID）
- FROM: `rioxxrinaxjapan`（セラーID）
- トーン: `polite`
- 補足情報: （空）

### 実際にAIに送られるペイロード（抜粋）

#### [N+4] admin_prompt の末尾

```
--------------------------------
INPUTS
--------------------------------
- Seller intent: {sellerSetting}   ← ここは補足情報が空なので空文字に置換
- Tone: polite                      ← ここにトーン値が注入
```

#### [N+5] FORCED_TEMPLATE（polite版）

```
The response MUST ABSOLUTELY adhere to the following format.
  Do not add explanations, markdown, or extra text.

  Hello michkuc_71,                 ← buyer_name が注入
  {output_content}                   ← AIが生成した本文がここに入る

  Best regards,
   rioxxrinaxjapan                   ← seller_name が注入

  Replace the placeholders with actual values.
  seller_name: rioxxrinaxjapan       ← 念押しの再注入
  buyer_name: michkuc_71              ← 念押しの再注入
```

---

## 🔄 tone別の差分（[N+5] FORCED_TEMPLATE）

トーン選択によって FORCED_TEMPLATE の内容が大きく変わる。以下は公式仕様（`SUMMARY_PROMT.csv`より）：

| 要素 | polite（丁寧） | friendly（フレンドリー） | apologetic（謝罪） |
|------|-------------|-------------------|----------------|
| 冒頭挨拶 | `Hello {buyer_name},` | `Hello {buyer_name},` | `Hello {buyer_name},` |
| 本文前後の改行 | なし | `<Break line here>` 明示 | `<Break line here>` 明示 |
| 結句 | `Best regards,` | `Best,` | `{greeting},`（条件分岐） |
| `{greeting}`の中身 | — | — | 怒っている → `Sincerely`<br/>それ以外 → `Kind regards` |

**→ トーンを変えると、AIが出力する結句・改行の扱いまで変わる。**

---

## ⚠️ 注入時の注意点

### 1. 同じプレースホルダが複数箇所に出る
`{buyer_name}` と `{seller_name}` は [N+5] FORCED_TEMPLATE の **冒頭・本文・末尾注意書き** の3箇所に登場。
- **すべて同じ値に置換される**ことをBayChat側で保証する必要あり
- 置換漏れがあると literal `{buyer_name}` がAIへのプロンプトに残り、AIが混乱する

### 2. 補足情報が空のときの扱い
`{sellerSetting}` が空の場合の admin_prompt の挙動：
- `Seller intent: {sellerSetting}` → `Seller intent: ` となる（空文字連結）
- admin_prompt v2.4 は「If not provided: the buyer's request IS the direction.」で空を許容するロジックを持つ
- **空を明示的に"not provided"として扱う別実装にしたい場合は要Cowatech協議**

### 3. descriptionチェックのロジック不明
`[N+1] 補足情報ガイド` を注入するかどうかの判定は：
- 「空文字列ならスキップ」？
- 「nullならスキップ」？
- 「trim後に空ならスキップ」？
- 「一定文字数以下ならスキップ」？
→ **Cowatechに確認が必要（Q3）**

### 4. TO/FROM「なし」選択時の挙動が不明
UIで「なし」を選んだ場合：
- [N+5] で `Hello ,` のようになる？
- それとも挨拶行自体がスキップされる？
- それとも `{buyer_name}` がそのまま残る？
→ **Cowatechに確認が必要**

---

## 🚨 このマトリクスを更新するタイミング

- UI項目の追加・削除・変更
- プレースホルダの追加・変更
- 注入先ブロックの変更
- 条件分岐の追加
- tone別バリエーションの追加（新しいトーン追加時）

**更新時は `05_changelog.md` と対応するブロックカード（`03_block_cards/`）も同時更新すること。**
