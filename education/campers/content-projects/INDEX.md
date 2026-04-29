# コンテンツ蓄積基盤 INDEX — 配信ダッシュボード

> Reffort社長の「Claude Code × eBay運営」実践記録を **Campers実名 / 匿名X / Note有料記事** の3軸で配信できる素材として可視化・整理するインデックス。
>
> ⚠️ **本INDEXは素材棚卸しの目的のみ**。配信判断・公開判断・タイミングは全て社長判断。Claude Codeから「記事化しますか？」と提案するのは禁止（`memory/feedback_content_recording.md` / `memory/project_consulting.md` 準拠）。

---

## 部屋全体の地図

```
content-projects/
├─ INDEX.md（このファイル）         ← 入口・配信ダッシュボード
│
├─ by-business-process/             ← 本棚A：業務縦軸 12段階
│   ├─ 00-claude-code-foundation/   ★Claude Code 基盤（メンバー向け導入ガイド）
│   ├─ 01-research/                 リサーチ
│   ├─ 02-listing/                  出品
│   ├─ 03-mukozai-stock-management/ 無在庫管理ツール
│   ├─ 04-uzaiko-stock-management/  有在庫管理ツール
│   ├─ 05-procurement/              仕入管理
│   ├─ 06-trouble-handling/         トラブル対応（要検討）
│   ├─ 07-shipping/                 発送
│   ├─ 08-accounting/               経理・外注報酬
│   ├─ 09-analytics/                分析・KPI
│   ├─ 10-advertising/              広告最適化
│   └─ 11-direct-sales/             ダイレクト販売
│
├─ cross-cutting-skills/            ← 本棚B：業務横断スキル
│   └─ external-integrations/       外部ツール連携・自動化全般
│
├─ applications-beyond-ebay/        ← 展示棚：「Claude Codeはこんなこともできる」（Campers向け参考例のみ）
│
├─ webinar-materials/               ← 作業机1：ウェビナー素材
├─ ai-course-curriculum/            ← 作業机2：AIコース月額カリキュラム
└─ archived-by-theme/               ← 物置：旧テーマ別構造を保管
```

---

## 2軸戦略（再掲）

| 軸 | 対象 | 形態 | 誘導先 |
|---|---|---|---|
| **Axis 1: Campers** | 既存Campersメンバー（約40名・eBayセラー・非エンジニア） | 月次ウェビナー＋専用Chatwork＋AIコース月額追加 | AIコース |
| **Axis 2: 匿名X→Note** | AI×eBay運営に興味ある不特定多数 | 匿名Xアカウント運用→Note有料記事 | Note記事販売（**Campers/コンサルへの誘導は禁止**） |

**直近の山場**: 2026-05-31（日）Campersウェビナー（Axis 1）

**配信時の禁止事項**:
- BayChat関連は **Campers向け参考例のみ**（匿名X／Note不可・社長と特定されるため）
- 匿名X／Note では社長氏名・Reffort社名・スタッフ氏名等の特定要素を全て匿名化

---

## 業務縦軸ビュー（メンバーの実践用）

### 凡例
- **完成度**: 素材がどれだけ揃っているか
  - ◯ 80%以上：今すぐ配信素材化可能
  - △ 50-79%：要点は揃うが肉付け必要
  - ✕ 50%未満：素材薄い・継続蓄積が必要
- **3軸適合度**: ◎ 主力素材／○ 利用可能／△ 加工要／✕ 適合外

| # | 業務段階 | 主要事例 | 完成度 | Campers | 匿名X | Note | コメント |
|---|---|---|:-:|:-:|:-:|:-:|---|
| 00 | **Claude Code 基盤** ★ | 7ファイル整備済み | ◯ 90% | ◎ | ◎ | ◎ | **メンバー向け導入の最重要資料** |
| 01 | リサーチ | （5/31向けに事例作成予定） | ✕ 30% | ◎ | ○ | ○ | 蓄積待ち |
| 02 | 出品 | （5/31向けに出品ツール作成予定） | ✕ 30% | ◎ | ○ | ○ | 蓄積待ち |
| 03 | 無在庫管理ツール | 在庫管理ツール（ASICS／フリマ拡張） | △ 75% | ◎ | ◎ | ◎ | **Bot検出失敗譚は読み物として価値高** |
| 04 | 有在庫管理ツール | （社長スプレッドシート→ツール化予定） | ✕ 30% | ◎ | ○ | ○ | 蓄積待ち |
| 05 | 仕入管理 | 仕入管理表GAS（Fulfillment API・clasp） | ◯ 85% | ◎ | ◎ | ◎ | **OAuth2/GAS/clasp 3本記事化可能** |
| 06 | トラブル対応 | （要検討・蓄積待ち） | ✕ 20% | △ | △ | △ | AI化優位性が見えるか要判断 |
| 07 | 発送 | 仕入管理表と連携 | △ 60% | ◎ | ○ | ○ | 05と一体化で成立 |
| 08 | 経理・外注報酬 | 月次請求書スキル | △ 70% | ◎ | ○ | ○ | 領収書管理・会計連携で完成度UP |
| 09 | 分析・KPI | eBay週次レポートv3 | ◯ 90% | ◎ | ◎ | ◎ | **「92.7%売上ゼロ」は衝撃の数字** |
| 10 | 広告最適化 | eBay広告最適化（帰属103%・広告税） | ◯ 80% | ◎ | ◎ | ◎ | **「広告税」エピソードは普遍的** |
| 11 | ダイレクト販売 | direct-sales（Render） | △ 65% | ○ | △ | ○ | 直取応用の参考例 |

### 横断スキル

| 棚 | 主要事例 | 完成度 | Campers | 匿名X | Note |
|---|---|:-:|:-:|:-:|:-:|
| external-integrations | スプレッドシート3型／Chatwork MCP／スクレイピング戦略 | ◯ 85% | ◎ | ◎ | ◎ |

### 展示棚（Campers向け参考例専用）

| 棚 | 主要事例 | Campers | 匿名X | Note |
|---|---|:-:|:-:|:-:|
| applications-beyond-ebay | BayChat AI Reply（自社SaaS開発） | ◎ | **❌** | **❌** |

---

## 配信フォーマット別ビュー（社長が「次に何を出す？」のとき即引く）

### 5/31 Campersウェビナー候補（Axis 1）

**主軸として使う**:
1. **00-claude-code-foundation/**（メンバー向け導入の入口）
2. **03-mukozai-stock-management/**（リサーチ系の代表例）
3. **05-procurement/**（仕入管理AI化の代表例）
4. **09-analytics/**（数字を見ることのインパクト）
5. **10-advertising/**（「広告税」エピソードで意識変革）
6. **cross-cutting-skills/external-integrations/**（業務横断の基礎技術）

**参考例として軽く触れる**:
7. **applications-beyond-ebay/**（「自社サービスでもこんなことやった」）
8. **08-accounting/**（スタッフいる人向け）
9. **11-direct-sales/**（直取応用）

**当日デモするなら**:
- 09-analytics の週次レポートの実物
- 03-mukozai-stock-management の在庫追跡画面

詳細は `webinar-materials/20260531-draft.md` を参照。

### 匿名X 単発・スレッド候補（Axis 2）

**バズ狙いの単発投稿**:
- 「全出品の92.7%が売上ゼロだった」（09-analytics）
- 「数年放置していた『広告税』に気付いた話」（10-advertising）
- 「帰属率103%という異常を発見」（10-advertising）

**スレッド形式**:
- スプレッドシート自動化3型（cross-cutting-skills/external-integrations）
- Bot検出との戦い（03-mukozai-stock-management）

### Note有料記事候補（Axis 2）

**今すぐ書ける**:
- 「AIにスプレッドシートを編集させる3つの方法」（cross-cutting-skills）
- 「eBay週次レポートを完全自動化する実装ガイド」（09-analytics）
- 「Trading API → Fulfillment API 移行ガイド」（05-procurement）

**素材揃い次第**:
- 「在庫管理ツールでBot検出と戦った話」（03-mukozai-stock-management）
- 「広告最適化の階層型運用」（10-advertising）

---

## 「やっておくべきこと／やってはいけないこと」横断ビュー

メンバー向けの最重要素材。コンテンツ化する際の核心。

**詳細**: `by-business-process/00-claude-code-foundation/cases/05_dos-and-donts.md` 参照。

主要項目：
- DO: APIトークンは即.env管理 / journey-log を毎日書く / 失敗を正直に記録 / 隔週メンテ
- DON'T: APIトークン直書き / 確認なしで全件処理 / CLAUDE.md肥大化放置 / 「動いているはず」報告

---

## 各事例ファイルの構造（テンプレート）

メンバーがどの事例を見ても同じ構造で読めるように統一：

```
1. 何をやったか（目的・背景）
2. 取り組みのプロセス（時系列の要点）
3. つまづいたこと（失敗・遠回り）
4. 学んだこと（教訓）
5. メンバーへの含意（応用ポイント） ★最重要
6. 数値 Before/After
7. 配信先別の使い分け（Campers / 匿名X / Note）
8. 元素材（journey-log.md 行範囲・関連ファイル）
```

★の「メンバーへの含意」が**「事例＝テンプレ」ではなく「事例＝方法論の例示」**として機能する核心です。

---

## 運用ルール

### 新規セッションでコンテンツ素材になる発見をしたとき
1. journey-log.md にエントリ追記（既存ルール）
2. 該当業務段階の `cases/` に新規ファイル作成 or 既存更新
3. 大きなテーマで該当業務段階が無ければ新設を社長提案
4. 本INDEX.md の「業務縦軸ビュー」を更新

### 配信判断
- 全て社長判断
- Claudeから「記事化しますか？」提案禁止
- 「ネタ出して」と言われたら本INDEX.md から即抽出

### Axis 2（匿名X→Note）素材切り出し時の禁止事項
- 社長氏名・Reffort社名・スタッフ名・Chatworkルームid 等の匿名化必須
- BayChat内部の機密情報を一切出さない
- BayChat事例自体を匿名X／Noteで使わない（社長と特定される）
- Campers/コンサル事業への誘導を組み込まない

---

## メンバー向けサイト化（将来計画）

社長指示（2026-04-29）：
> 「メンバー達がいつでもアクセスして見れるサイトを作る必要があります。質問する前にまずはコンテンツとして見て最低限自分で実行してもらうものです」

→ 本フォルダの内容を**メンバー向け閲覧サイト**として公開する将来計画あり。
候補（後日方針決定）: Notion公開ページ／Note マガジン／reffort.co.jp サブドメイン／専用Web。

現時点では**コンテンツの中身を正しい構造で蓄積する**ことに集中。

---

## 関連ファイル

- 時系列史実の原本: `education/consulting/journey-log.md`（2148行・36エントリ・書き換えない）
- 4/26ウェビナー草案: `education/consulting/webinar-draft-20260426.md`
- 5/31ウェビナー骨子: `webinar-materials/20260531-draft.md`
- AIコースカリキュラム: `ai-course-curriculum/curriculum-draft.md`
- 関連 memory:
  - `memory/project_consulting.md` — 2軸戦略の方針
  - `memory/feedback_content_audience_framing.md` — 配信先別フレーミングルール
  - `memory/feedback_content_recording.md` — コンテンツ記録ルール
  - `memory/project_campers_webinar.md` — 5/31ウェビナー位置づけ
  - `memory/project_spreadsheet_automation_content.md` — スプレッドシート自動化はAIコース必須

---

*作成: 2026-04-29（コンテンツ蓄積基盤整備セッション）*
*更新: 各業務段階の新規事例追加時・配信完了時*
