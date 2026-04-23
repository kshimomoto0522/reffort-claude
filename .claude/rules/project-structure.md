# プロジェクト構成

3事業階層（物販・サービス・教育/コンサル）＋ 経営横断機能の4トップレベル構成。

```
/reffort/
  CLAUDE.md                            ← 全社コアルール
  .claude/rules/                       ← 会社概要・事業・ロードマップ・技術等

  /commerce/                           【物販】
    /ebay/                             eBay輸出（コア事業）
      /analytics/                      週次レポート・KPI
      /tools/                          在庫管理・スクレイピング・リサーチ
      /staff-ops/                      スタッフ指示・マニュアル
    /direct-sales/                     NYダイレクト販売（Render公開）

  /services/                           【SaaS】
    /baychat/                          CS自動化
      /ai/                             AI Reply
      /product/                        UI/UX・Cowatech仕様書
      /marketing/                      SNS・Webマーケ
    /baypack/                          米国返品代行
      /invoice/                        共同運営費の請求書自動化

  /education/                          【コンサル・教育】
    /campers/                          Campersスクール
    /consulting/                       将来のコンサル事業（journey-log.md）

  /management/                         【全事業横断】
    /dashboards/                       売上ダッシュボード
    /x-digest/                         X情報ダイジェスト
    /monetization-portfolio/           収益化設計
```

## CLAUDE.mdのカスケード

Claudeは作業時のカレントディレクトリから親方向にCLAUDE.mdを遡って読み込む。
例：`services/baychat/ai/` で作業 → `/CLAUDE.md → /services/CLAUDE.md → /services/baychat/CLAUDE.md → /services/baychat/ai/CLAUDE.md` の4層が自動ロード。階層構造そのものが指示の階層になるため、**固有情報は最も深い層にだけ置き、中間層はポインタにする**のが原則。

## 配置ルール

- 特定事業の分析・ツール・マーケは**その事業配下**に配置する（例：eBay広告の分析は `commerce/ebay/analytics/`）
- 全事業を横断する経営判断・情報は `management/` 配下に配置する
- 新規事業ユニットを追加する場合は、その層に**固有ルールがある時だけ** CLAUDE.md を作成する（中間層の空ポインタは避ける）
