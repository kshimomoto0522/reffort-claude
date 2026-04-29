---
name: コンサル事業ビジョン（2軸戦略）
description: Campers + 匿名X→Noteの2軸でコンテンツ展開。日々の実践をコンテンツ化する前提で記録
type: project
originSessionId: 723d0162-a26f-4a70-85ec-18691aeb1a1d
---
# コンサル事業ビジョン（2軸戦略）

## 全体像

下元氏が「Claude Code × eBay運営」を実践していく過程そのものをコンテンツ化し、**2軸**で展開する。

### Axis 1：Campers（実名・有料コミュニティ）
- **対象**: eBayセラー（既存Campers約40名 + 新規eBay始めたい層）
- **形態**: 月次ウェビナー + 専用グループチャットでQ&A + AIコース（月額追加）
- **直近イベント**: 2026-05-31（日）Campersウェビナー
- **収益化**: 既存月会費 + AIコース月額追加

### Axis 2：匿名X → Note（有料記事販売）
- **対象**: AI×eBay運営に興味ある不特定多数（外部）
- **形態**: 匿名X運用で情報発信 → Note等の有料記事に誘導 → 記事販売で収益化
- **重要方針**:
  - **Xアカウントは社長個人を伏せて運用**（匿名/ペルソナ）
  - **Note等の有料コンテンツに誘導**
  - **コミュニティ運営・コンサル事業（つまりCampers）には誘導しない**
  - Axis 1 と Axis 2 は完全に分離する設計

### 共通方針
- 内容のベース素材は**同じ**（日々のClaude Code × eBay実践記録）
- 配信形態・口調・誘導先のみ Axis ごとに調整する
- BayChat・BayPackはReffort自社サービスのためカリキュラムには含めない（事例として「参考例」程度の言及はあり）

## 優先順位
1. **まずCampers（Axis 1）から実行**
2. 5/31ウェビナーが直近の山場
3. Axis 2（匿名X→Note）はAxis 1運用が回ってから本格立ち上げ

## ターゲット理解（重要）
- **Campersメンバーは非エンジニアのeBayセラー**
- API・コード・MCP等の細かい技術論は苦手 → eBay運営のメリット中心で語る
- 「自分の場合はBayChatでこんなこともやったよ」と参考例として挿入する程度
- 狙う行動変容：「Claude Codeを使いこなせば eBay以外にも、別事業や新規事業にも応用できる」と気づいてもらう

## 記録場所（2026-04-29 構造刷新）
- `/reffort/education/consulting/CLAUDE.md` — 事業コンセプト・カリキュラム構想
- `/reffort/education/consulting/journey-log.md` — 日々の実践・学習の時系列原本（2148行・36エントリ・**書き換えない**・追記のみ）
- `/reffort/education/campers/content-projects/INDEX.md` — **配信ダッシュボード**（業務縦軸ビュー＋配信フォーマット別取り出し窓口）
- `/reffort/education/campers/content-projects/by-business-process/` — 業務プロセス縦軸 12段階（00〜11）
  - 00-claude-code-foundation/（Claude Code基盤・メンバー向け導入ガイド）
  - 01-research / 02-listing / 03-mukozai-stock-management / 04-uzaiko-stock-management
  - 05-procurement / 06-trouble-handling / 07-shipping / 08-accounting
  - 09-analytics / 10-advertising / 11-direct-sales
- `/reffort/education/campers/content-projects/cross-cutting-skills/` — 業務横断スキル
  - external-integrations/（スプレッドシート3型／Chatwork MCP／スクレイピング戦略）
- `/reffort/education/campers/content-projects/applications-beyond-ebay/` — 「Claude Codeはこんなこともできる」展示棚（**Campers向け参考例専用・匿名X/Note不可**）
- `/reffort/education/campers/content-projects/webinar-materials/` — 5/31ウェビナー骨子
- `/reffort/education/campers/content-projects/ai-course-curriculum/` — AIコース月額カリキュラム
- `/reffort/education/campers/content-projects/archived-by-theme/` — 旧テーマ別構造（claude-code-maintenance／spreadsheet-automation）保管

## Claudeへの指示
- 各部門での実践セッション中に「コンテンツになるネタ」を見つけたら journey-log.md に**【コンテンツ候補】**タグで追記
- 大きなテーマは独立した content-projects/<theme>-case-study/ として独立蓄積
- 社長から「ネタ出して」と言われたら content-projects/ + journey-log.md のタグ一覧から即抽出できる状態を維持
- 配信判断・公開判断・タイミングは**全て社長判断**。Claudeから「記事化しますか？」と提案するのは禁止
- 失敗・試行錯誤・遠回りも正直に記録（リアルなコンテンツになる）
- Axis 1（Campers実名）とAxis 2（匿名X→Note）の境界を意識：技術詳細やBayChat内部の話は Axis 2 の方が向くなど、配信先によって素材選別が変わる
