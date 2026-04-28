---
name: API調査は根本を掘る（回避策の前に）
description: 自社の他プロダクトで実現できている機能は、必ず何らかのAPI経路があるので、既存コードに固執せず根本APIを調べること
type: feedback
originSessionId: 56271ff7-ea79-4c37-b6d5-0b01b13015d1
---
# API調査は安易な回避策の前に根本を見る

自社の別プロダクト（例: BayChat）で実現できている機能については、
**必ずAPI側に直接取得する手段がある**と前提して動く。既存実装が使っている
古いAPIに固執して回避策を積むと、結果的に大回りになる。

**Why:** 2026-04-24 仕入管理表GASの発送期限バグで、Trading APIに `ShipByDate` が
返らない事実から「JP祝日テーブル手動保持＋GetItem呼び出しで DispatchTimeMax 取得＋
営業日計算」という回避策を社長に提案してしまった。社長が「BayChatでも反映できている」
「日本時間基準の議論をしたことがある」と指摘し、そこで初めて Sell Fulfillment API
(REST) を調査 → 答えが1発で判明（`lineItems[].lineItemFulfillmentInstructions.shipByDate`
を直接返す）。**既存プロダクトの動作が最強の仕様書**であり、回避策を考える前に
「他でできているならどうやっているか」を1本目の質問にする。

**How to apply:**
- 「Trading API では〜」と既存実装の縛りで考え始めたら一旦止まる
- 自社の他プロダクトでその機能が動いているか社長に確認
- 動いているなら REST/新API の可能性を先に調査（eBayなら Sell Fulfillment / Sell Inventory /
  Sell Analytics 等）
- 祝日テーブルや手動計算などの「アナログ対応」は API不達時の最終フォールバックに
  留める
- 調査の初手ヒントを外した場合は素直に認めて軌道修正する（社長は「調査が甘い」と
  はっきり言うタイプ）
