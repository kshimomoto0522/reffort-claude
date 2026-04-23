# 00. 全体処理フロー

> このファイルの役割：**BayChat画面でセラーが「AIで返信を生成」ボタンを押してから、AIの返信がセラー画面に表示されるまでの全工程**を視覚化する。

---

## 🗺️ 全体フロー（Mermaid図）

```mermaid
flowchart TD
    Start([セラー: BayChat画面でバイヤーメッセージを開く]) --> UIOp[セラー: UI操作<br/>・TO/FROM選択<br/>・トーン選択（polite/friendly/apologetic）<br/>・補足情報の入力（任意）]
    UIOp --> Click([セラー: 「AIで返信を生成」ボタンクリック])

    Click --> Assemble[BayChatサーバー:<br/>ペイロード組み立て開始]

    Assemble --> B0["[0] 商品情報JSON<br/>role=developer<br/>ItemID経由でDBから取得"]
    B0 --> Chat["[1..N] チャット履歴<br/>role=user/assistant/system<br/>DBのメッセージ・event履歴"]
    Chat --> DescCheck{descriptionが<br/>空でない？}
    DescCheck -- Yes --> BN1["[N+1] 補足情報ガイド<br/>role=developer<br/>『Create questions/answers...』"]
    DescCheck -- No --> SkipBN1[ブロック[N+1]は注入しない]
    BN1 --> BN2
    SkipBN1 --> BN2

    BN2["[N+2] BASE_PROMPT<br/>role=developer<br/>PLATFORM COMPLIANCE<br/>（Cowatech固定）"]
    BN2 --> BN3["[N+3] OUTPUT_FORMAT<br/>role=developer<br/>JSON strict指定<br/>（Cowatech固定）"]
    BN3 --> BN4["[N+4] admin_prompt<br/>role=developer<br/>社長がadmin画面で編集<br/>{sellerSetting}/{toneSetting}置換"]
    BN4 --> BN5["[N+5] FORCED_TEMPLATE<br/>role=developer<br/>tone別3バリエーション<br/>seller_name/buyer_name注入"]

    BN5 --> Send[BayChatサーバー:<br/>OpenAI Responses APIへ送信<br/>model=gpt-4.1-mini<br/>temperature=0.2<br/>response_format=json_schema strict<br/>name=multi_language_reply]

    Send --> OpenAI[(OpenAI API)]

    OpenAI --> Resp[レスポンス受信<br/>JSON: jpnLanguage + buyerLanguage]

    Resp --> Post[BayChatサーバー:<br/>後処理<br/>・jpnLanguageを日本語タブに<br/>・buyerLanguageを返信タブに<br/>・セラー編集待ち状態へ]

    Post --> Show([セラー画面: 2タブで返信候補を表示])

    classDef uiClass fill:#9D4EDD,stroke:#333,color:#fff
    classDef blockClass fill:#C77DFF,stroke:#333,color:#fff
    classDef logicClass fill:#E0AAFF,stroke:#333,color:#000
    classDef sendClass fill:#7209B7,stroke:#333,color:#fff
    classDef apiClass fill:#240046,stroke:#333,color:#fff

    class Start,UIOp,Click,Show uiClass
    class B0,Chat,BN1,BN2,BN3,BN4,BN5 blockClass
    class Assemble,Post,DescCheck,SkipBN1 logicClass
    class Send sendClass
    class OpenAI apiClass
```

---

## 📝 フロー解説（非エンジニア向け）

### ステップ1：セラーがUI操作する
BayChat画面でバイヤーとのチャットを開き、以下を選ぶ：
- **TO**：返信の宛先（バイヤーID / バイヤー氏名 / なし）
- **FROM**：署名（セラーID / セラー氏名 / 担当者名 / なし）
- **トーン**：polite（丁寧）/ friendly（フレンドリー）/ apologetic（謝罪）
- **補足情報**：AIに伝えたい意図（任意）

### ステップ2：「AIで返信を生成」ボタンを押す
BayChatサーバーが、AIへの送信データ（**ペイロード**）を組み立て始める。

### ステップ3：ペイロード組み立て（ブロック順に積み上げ）
7つのブロックが **必ずこの順序** で積み上げられる：
1. **[0] 商品情報JSON** — AIに「どの商品についてのやり取りか」を教える
2. **[1..N] チャット履歴** — バイヤーとセラーの過去のやり取りと、発生したイベント（注文・返品リクエスト等）
3. **[N+1] 補足情報ガイド** ← **「descriptionが空でない場合のみ」注入される**
4. **[N+2] BASE_PROMPT** — eBayコンプライアンス制約（変更不可）
5. **[N+3] OUTPUT_FORMAT** — JSONで返すよう強制
6. **[N+4] admin_prompt** — 社長がadmin画面で編集できる最重要プロンプト
7. **[N+5] FORCED_TEMPLATE** — 「Hello ... Best regards ...」を強制（tone別3バリエーション）

### ステップ4：OpenAI APIに送信
以下の設定で送信：
- モデル：`gpt-4.1-mini`（次期候補：Gemini 2.5 Flash）
- temperature：0.2（安定性重視）
- response_format：json_schema strict（JSON以外の返答を拒否）
- schema名：`multi_language_reply`

### ステップ5：レスポンス受信と後処理
AIが返すJSON：
```json
{
  "jpnLanguage": "（日本語訳）",
  "buyerLanguage": "（バイヤーへの返信英文）"
}
```
BayChatサーバーが2タブに振り分けて表示 → セラーが編集・送信。

---

## ⚙️ 重要な技術パラメータ（v0.1時点）

| パラメータ | 値 | 意味 | 変更時の注意 |
|---------|-----|-----|-----------|
| `model` | `gpt-4.1-mini-2025-04-14` | 使用AIモデル | Gemini 2.5 Flashへの変更検討中（Cowatech実装待ち） |
| `temperature` | `0.2` | 出力の安定性（低いほど一貫） | 0.0-1.0。上げると創造的、下げると機械的 |
| `response_format.type` | `json_schema` | JSON形式を強制 | `text`に変えるとJSON以外も許可（非推奨） |
| `response_format.strict` | `true` | schemaと完全一致を強制 | `false`にするとextra fieldsを許可 |
| `response_format.name` | `multi_language_reply` | schema名（後処理で使用） | Cowatech後処理と連動するため変更厳禁 |

---

## 🔁 各ステップの所要時間（2026-04時点の計測）

| 区間 | 時間 | 備考 |
|------|-----|-----|
| ステップ1〜2（UI操作） | セラー依存 | — |
| ステップ3（ペイロード組み立て） | ~100ms | BayChat内部処理 |
| ステップ4〜5（API往復） | **1〜10秒以上** | ⚠️ 現行GPT-4.1-Miniは遅いケースあり。Gemini 2.5 Flashは1〜2秒 |
| ステップ5（後処理〜表示） | ~100ms | — |

**→ 体感待ち時間の大半はAI生成時間。モデル選定が体感改善の本丸。**

---

## 🚨 このフロー図を更新するタイミング

以下のいずれかが発生したら即座に更新する：

- [ ] プロンプトブロックの追加・削除
- [ ] ブロックの順序変更
- [ ] 条件分岐ロジックの変更（descriptionチェック以外の条件が追加される等）
- [ ] AIモデル・APIパラメータの変更
- [ ] 後処理ロジックの変更
- [ ] UI操作項目の追加・変更

**更新時は `05_changelog.md` にも記録する。**
