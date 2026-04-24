---
name: ダイレクト販売ツール
description: direct-sales注文管理ツールの開発状況・デプロイ先・技術構成・課題
type: project
---

## ダイレクト販売オーダー管理ツール

Node.js + Express製のWebアプリ。バイヤー向け注文・セラー向け管理を一体化。

### デプロイ先
- **本番URL**: https://reffort-direct-sales.onrender.com
- **ホスティング**: Render Starter ($7/month)
- **永続ディスク**: /opt/render/project/src/data にマウント（1GB, $0.25/月）※2026-04-10追加
- **GitHubリポジトリ**: https://github.com/kshimomoto0522/reffort-direct-sales (Private)
- **GitHubにプッシュすると自動デプロイされる**（masterブランチ）
- **stagingブランチ**もGitHubに存在（将来Renderテスト環境用、現在未使用）

### テスト環境（2026-04-10決定）
- **ローカル環境方式**（Renderテスト環境は不採用、$7/月を節約）
- 同期：`node sync-from-prod.js` で本番→ローカルにデータ一方通行コピー
- 起動：`node server.js` → http://localhost:3000
- 運用フロー：修正→ローカル確認→社長OK→指定タイミングで本番push
- **営業時間中の本番push禁止**（バイヤー利用中の事故防止）

### データ保護
- **seed/フォルダ**: 初回起動時にdata/が空ならseed/からコピーする仕組み（server.js内）
- **デプロイでデータは消えない**（永続ディスク + seed保険）
- data/フォルダはgit管理に含まれているが、永続ディスクがマウントされるため実行時は上書きされない

### 技術構成
- バックエンド: Node.js + Express (server.js)
- フロントエンド: Vanilla JS (public/app.js, index.html, style.css)
- データ保存: JSONファイル (data/*.json)
- Google Sheets API連携（商品マスタ）
- ポート: `process.env.PORT || 3000`

### データファイル
- products.json: 商品マスタ（3モデル・82バリアント）
- orders.json: 注文データ
- purchases.json: 仕入記録（フラット形式: {sku, size, quantity, sizeType} × items配列）
- purchaseInstructions.json: 仕入指示
- settings.json: 拠点設定（5拠点：山田・瓦田・日佐・筑紫野・城南）+ sectionPasswords
- shipments.json: 出荷データ（paid: true/false で支払状態管理）
- coupons.json: クーポン管理（84件）
- deliveries.json: 納品済データ

### 実装済み機能（2026-04-13時点）
- バイヤー向け注文フロー（商品選択→サイズ→カート→注文）
- セラートップメニュー（仕入・オーダー管理・発送管理・商品登録・クーポン管理・詳細設定・収支管理）
- 管理者編集モード（Current Orders・拠点数量の増減）— **発送済み差引後の数量を表示**
- 仕入指示・仕入完了フロー（バッチ単位）
- **未指示計算（加算方式）**: `assigned = purchased + pending_instructed`。`calcInstructedItems`はpendingバッチのみカウント
- 新規オーダー通知（30秒ポーリング）
- クーポン管理機能（管理者がアカウント登録→仕入担当者が発行→使用状況追跡）
- **ページ別パスワード設定**（詳細設定→ページ別パスワード。拠点管理以外の全ページ）
- **パスワード不要ページ**: order, shipping, product, coupon（NO_PASSWORD_ROLES + autoLogin）
- **SKU統一表示順**（productsマスタ基準で全セクション固定）
- 商品画像: ASICS Scene7サーバー（SB_FR_GLB優先、SR_FR_GLBフォールバック）
- **発送済みをCurrent Ordersから自動差引**（calcRemaining使用）
- **仕入済から発送分差引**（拠点別の正確な倉庫在庫表示）
- **バイヤーCurrent Orders**: マイナス数量は非表示（セラー側は表示）
- **バイヤーPast Orders**: 未払い/支払済みバッジ表示、DHL追跡リンク（英語サイト）
- **発送履歴**: 支払済みトグルボタン、足数・合計販売金額表示、追跡番号編集、発送まとめ
- **仕入ページ**: JPサイズ(cm)のみ表示（仕入担当向け）
- **仕入バッチ個別削除**: 仕入ページ・オーダー管理の両方から削除可能
- **仕入日次サイクル制御**: JST 0時リセット。当日完了済み→翌日まで次の仕入非表示（completedAtトラッキング）
- **テーブル全体にゼブラストライプ適用**

### 注意事項（学んだ教訓）
- **purchases のデータ形式**: フラット `{sku, size, quantity, sizeType}` × items配列。マップ形式 `{sizes:{...}}` は使わない
- **bashのcurlで日本語POSTすると文字化け**: 必ずNode.jsスクリプト経由でUTF-8安全に送信
- **パスワードは社長が設定済み、勝手に変更しない**
- **calcRemainingでprice等のメタ情報が消える**: 差引後に必ずprice補完処理を入れる
- **shipments.orderNumbersが注文IDと不一致の場合がある**: order statusに依存せず、calcRemainingで数量ベースで差引する設計
- **未指示計算はmax方式ではなくadd方式**: max(instructed, purchased)だと2回目以降の指示が吸収される。purchased + pending_instructedが正解
- **completedAt管理が重要**: バッチ削除でinstruction.statusが変わると日次サイクルが崩れる。completedAtタイムスタンプで制御

### ローカル状態（2026-04-13）
- 本番データ同期済み（sync-from-prod.js実行済み）
- 次セッションで修正・機能アップデート作業予定
- ローカルサーバーは未起動

### 🔧 新商品追加の標準手順（2026-04-16ルール化）
**必ず `commerce/direct-sales/CLAUDE.md` の「新商品追加の標準手順」を参照してから作業すること。**
キーポイント:
1. スプレッドシートI列に社長入力の**販売価格(USD)**が入っていることが多い → **必ず確認してから登録**
2. C/D/F/H列（SKU・カラー・性別・画像URL）はClaudeが埋める
3. カラー・性別はChrome-in-Chrome MCPでスクレイピング（JS SPA対応）
4. 画像URLは `SB_FR_GLB`（1足正面画像）で統一、403時は `SR_FR_GLB` フォールバック（verify-and-fix-images.js）
5. 並び順変更は `public/app.js` の `MODEL_PRIORITY_LIST` を更新
6. テンプレートスクリプト: `fill-sheet-new-models.js` + `register-new-models.js` + `verify-and-fix-images.js` + `register-to-prod.js`
7. **販売価格は絶対に推測しない**。社長入力値を反映する
8. **⚠️ 本番反映は2段階必要**:
   - コード変更 → `git subtree push --prefix=direct-sales render-ds master`
   - 商品データ → `node register-to-prod.js`（本番APIに直接POST）
   - **永続ディスクの仕様により、git pushだけでは商品データは本番反映されない！**

**Why:** NYバイヤー向けダイレクト販売の注文・仕入・発送を一元管理するため
**How to apply:** コード変更はローカルでテスト → 社長OK → git subtree push で本番デプロイ。VPSは使わない。
新商品追加時は `commerce/direct-sales/CLAUDE.md` の手順を必ず読んでから作業。
