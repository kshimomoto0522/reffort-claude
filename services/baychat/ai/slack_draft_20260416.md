# Cowatech向けSlack草案（2026-04-16）
> 送信先: `#baychat-ai導入`（チャンネルID: C09KXK26J8G）
> メンション: @Dang Van Quyet / @Keisuke Shimomoto
> **送信前に必ず社長の承認を得ること**（方針決定を含む依頼のため）

---

## 送信スレッド（新規作成）

### スレッドタイトル（太字で親メッセージ）
```
*AI Replyプロンプト最適化の次のステップ相談*
```

### スレッド内の返信本文

```
@Dang Van Quyet
@Keisuke Shimomoto
クエットさん、いつもありがとうございます。

今回お送りいただいた本番ペイロード（`gpt_api_payload.txt`）を参考に、
オフライン検証用に本番同等のペイロード構造を再現できるツールを構築しました。
検証を12ケースで実施した結果、ある発見があり相談させてください。

【発見】
最後のdeveloperメッセージに入っている「FORCED TEMPLATE」ブロック
（Hello {buyer_name}, ... Best regards, {seller_name} を強制するもの）
を **除去すると、品質が明確に改善する** ことがわかりました。

- FORCED TEMPLATE ON  : 平均 19.5 / 25
- FORCED TEMPLATE OFF : 平均 21.5 / 25（+2.0ポイント改善）

12ケース中 10ケースで改善または同点、1ケースのみ軽微に悪化。
adminプロンプトv2.4には既に「RESPONSE STRUCTURE」で
状況別の署名・挨拶パターンが記述されているため、
強制テンプレートを被せない方がadminプロンプトの判断力を活かせる構造です。

【ご相談】
ただし、BayChatのAI Reply画面には **TO（宛先）・FROM（署名）のプルダウン** があり、
現状これらの値はFORCED TEMPLATEの最下部の
  seller_name: {UIで選ばれた値}
  buyer_name: {UIで選ばれた値}
として渡されていると理解しています。

FORCED TEMPLATEを除去した場合、TO/FROMの値の渡し方を
設計し直す必要があります。以下3案のいずれかを想定しています：

A. adminプロンプトに `{buyerAddress}` `{sellerSignature}` プレースホルダを追加し、
   BayChatからの値を末尾のINPUTSセクションに注入する
   （Seller intent: ..., Tone: ..., Buyer address: ..., Seller signature: ...）

B. FORCED TEMPLATEを「強制」から「ヒント」に書き換える
   （『次のフォーマットを参考にしてよい』という柔らかい指示にする）

C. ベースプロンプトに `Greeting target: {buyerAddress}` `Signature: {sellerSignature}` を注入する

【確認したいこと】
1. 上記3案のうち、BayChat側の実装として
   どれが最も実装しやすい／現実的でしょうか？
2. TO/FROMの「なし」選択時、現状はどのように処理されていますか？
   （空文字列で渡すのか、プレースホルダそのものが消えるのか）
3. 補足情報（description / sellerSetting）が空の場合、
   本番ペイロードの「Create questions/answers ... main content being ...」
   ブロックは挿入されないという理解で合っていますか？

お手すきの際にご確認いただけますと幸いです。
ベトナム語でのご回答でも問題ございません。

よろしくお願いいたします。
```

---

## 承認チェックリスト（送信前に社長に確認）

- [ ] スコア数値（19.5 vs 21.5）の公開可否
- [ ] 3案（A / B / C）の記載内容が社長の意図と一致しているか
- [ ] 「FORCED TEMPLATE除去」を **決定事項として** 伝えるか、
      **検証結果としてシェア** にとどめるか
- [ ] 3つの質問の優先順位（最重要は #1 = 実装難易度の確認）

---

## 送信後タスク

- Cowatechからの返信はこのSlackスレッド内で続ける
- 返信に「方針決定を求める内容」が含まれる場合は社長に報告してから返答
- 返信が技術的な事実確認のみなら自動でお礼＋終了
