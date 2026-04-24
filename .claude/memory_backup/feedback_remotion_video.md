---
name: Remotion動画制作の失敗教訓
description: BayChat機能紹介動画でRemotionを試みたが砂嵐問題が解決不可能。Cap.soを推奨すること
type: feedback
originSessionId: e12bef15-097d-4f6a-b990-bb92a7f03bdf
---
Remotion + 実画面録画（スクリーンキャプチャ動画素材）の組み合わせは使わない。

**Why:** 実際の画面録画MP4をRemotionのOffthreadVideoで扱うと、Chromiumのデコードアーキテクチャとの相性問題で砂嵐が発生し、ffmpegで再エンコードしても解決しなかった。BayChat商品編集画面の機能紹介動画で試みたが失敗。社長に「切り貼りしただけ」「Claude公式ムービーの要素はゼロ」と指摘され、方針転換。

**How to apply:**
- BayChatや自社ツールの機能紹介動画は **Cap.so**（無料プランあり、Windows対応）を推奨する。録画するだけでブラウザフレーム・クリックアニメーション・自動ズームが自動付与される。
- RemotionはUIを一から作り込むアニメーション（テキスト・グラフィック・データビジュアライゼーション）には有効。実画面録画ベースの機能紹介動画には向いていない。
- 次回「動画作りたい」と言われた時は、まずCap.soを提案すること。
