# 08. CSV移行計画

> ✅ **v0.2 完成版**
> このファイルの役割：**既存の19枚CSV** を **単一参照源としての設計図** に段階的に移行する計画を定義。移行先マップ・廃止スケジュール・デモート手順を明確にする。

---

## 🎯 移行の基本方針

| 項目 | 方針 |
|------|------|
| **マスター** | `design-doc/` 配下のMarkdown群 |
| **既存CSV** | `cowatech_payloads/spec_sheets/` は「参考資料」にデモート |
| **移行期間** | 3か月（2026-04-20 〜 2026-07-20） |
| **3か月後** | 参考資料のまま保持 or アーカイブ化を判断 |
| **矛盾時** | 設計図を優先（ただし矛盾を `09_open_questions.md` に記録） |

---

## 📋 CSV19枚の移行先マップ

### 🟢 完全移行済み（設計図に情報を取り込み済み）

| CSVファイル | 内容 | 移行先 | 状態 |
|-----------|------|-------|-----|
| **SUMMARY_PROMT.csv** | 最新プロンプト仕様（一次資料） | `block_n2_base_prompt.md`<br>`block_n3_output_format.md`<br>`block_n5_forced_template.md`<br>`block_chat_history.md`<br>`04_conditional_logic.md` | ✅ 完全転記 |
| **promt_spec_48665.csv** | 詳細版プロンプト仕様 | `block_n2_base_prompt.md`（代替版セクション） | ✅ 完全転記 |
| **admin_setting.csv** | admin補足プロンプト | `block_n4_admin_prompt.md`（参考） | ✅ 記録 |
| **Input_item_info.csv** | eBay API取得パラメータ全42項目 | `12_ebay_api_integration.md` | ✅ 完全転記 |
| **UI.csv** | UI仕様（ベトナム語） | `14_qa_testing.md`（UI設計詳細セクション）<br>`02_ui_injection_matrix.md` | ✅ 主要部分転記 |
| **Feedback.csv** | 10件の不具合記録 | `14_qa_testing.md`（過去の不具合記録） | ✅ 完全転記 |
| **quan_diem_test.csv** | 7項目QAチェックリスト | `14_qa_testing.md`（QAチェックリスト） | ✅ 完全転記 |
| **Compare_models.csv** | モデル比較表 | `11_model_selection.md` | ✅ 完全転記 |
| **test-gpt-model.csv** | モデルテスト結果 | `11_model_selection.md` | ✅ 主要部分転記 |
| **quy_doi_type_chat.csv** | typeChat→event変換 | `block_chat_history.md`<br>`04_conditional_logic.md` | ✅ 完全転記 |
| **Quy_doi_chat.csv** | event簡潔版 | 同上 | ✅ 内容統合（重複のため） |
| **promt_example.csv** | 実例セッション | （省略）本番ペイロードで代替 | ✅ 不採用（代替資料あり） |

### 🟡 部分移行（参考情報として記録）

| CSVファイル | 内容 | 移行先 | 状態 |
|-----------|------|-------|-----|
| **Image_feedback.csv** | 不具合画像の索引 | `14_qa_testing.md`（画像参照） | 🟡 索引のみ |
| **Follow.csv** | フォロー機能仕様（周辺） | 未採用（AI Reply本体と無関係） | 🟡 未採用 |
| **2026-03-19.csv** | 中間スナップショット | `block_n4_admin_prompt.md`（v2.0時代の記録） | 🟡 参考 |

### ⬇️ 廃止候補

| CSVファイル | 内容 | 廃止理由 |
|-----------|------|---------|
| **old_promt_spec.csv** | v1系プロンプト仕様（旧） | 現行v2.4で上書きされた。SUMMARY_PROMT.csvに取り込み済み |
| **promt-update.csv** | v1系更新記録 | 同上 |

### 📄 空・未完成

| CSVファイル | 状態 |
|-----------|-----|
| **AI-update-evd.csv** | 空ファイル。将来用として保持 |

---

## 🗓️ 段階的デモート計画

### フェーズ1：即座に実施（2026-04-20）
- [ ] 設計図を `reffort-claude` リポジトリにコミット
- [ ] `cowatech_payloads/spec_sheets/` に `_README.md` を配置し、「参考資料扱い」を明記
- [ ] Cowatechに設計図の存在と位置付けを通知

### フェーズ2：1か月後（2026-05-20）
- [ ] Cowatechの設計図レビュー完了
- [ ] 移行マップの見直し（漏れ・誤り確認）
- [ ] 移行マップの矛盾・不明点を `09_open_questions.md` に集約
- [ ] Cowatechと「どのCSVを優先的に廃止するか」協議

### フェーズ3：2か月後（2026-06-20）
- [ ] 廃止候補CSVの正式廃止（アーカイブフォルダへ移動）
- [ ] 残CSVの参考資料としての運用フロー確立
- [ ] 新規情報はすべて設計図に記入するルールを徹底

### フェーズ4：3か月後（2026-07-20）
- [ ] 移行完了判定
- [ ] 全CSVの扱い決定：
  - 削除
  - アーカイブ（`cowatech_payloads/_archive/`）
  - 参考資料として維持
- [ ] 移行完了記録を `05_changelog.md` に追記

---

## ⚠️ 重複・矛盾の解消方針

### CSVの重複構造

```
SUMMARY_PROMT.csv（最新・一次資料）
  ├─ promt_spec_48665.csv（詳細版）
  ├─ 2026-03-19.csv（中間版）
  ├─ old_promt_spec.csv（旧版・廃止候補）
  └─ promt-update.csv（v1系・廃止候補）

quy_doi_type_chat.csv（詳細版）
  └─ Quy_doi_chat.csv（簡潔版）
```

### 解消方針

| 種類 | 対応 |
|------|------|
| **最新版 vs 旧版** | 最新版をマスターに、旧版は廃止 |
| **詳細版 vs 簡潔版** | 詳細版をマスターに、簡潔版は廃止 |
| **同内容の2ファイル** | 設計図に統合後、両方廃止候補 |

### 既知の矛盾

| 矛盾点 | 旧 | 新 | 方針 |
|-------|---|---|------|
| output field名 | `japanese`/`reply`（2026-03-19.csv, promt-update.csv） | `jpnLanguage`/`buyerLanguage` | **新（camelCase）採用** |
| FORCED_TEMPLATE | CSVに固定値（`rioxxrinaxjapan`等） | UI動的値 | **UI動的値採用** |
| `<Break line here>` 記述 | SUMMARY_PROMT.csv polite版に無い | 本番実装にある | **本番実装採用（要確認）** |

---

## 🏷️ 参考資料ディレクトリの再整理案

### 現状
```
services/baychat/ai/cowatech_payloads/
├── gpt_api_payload.txt        ← 本番ペイロード（一次資料）
├── baychat_api_payload.txt    ← BayChat→Cowatech（一次資料）
└── spec_sheets/                ← 19枚CSV
    ├── (全19枚混在)
```

### 提案する再整理
```
services/baychat/ai/cowatech_payloads/
├── _README.md                  ← 参考資料扱い明記
├── gpt_api_payload.txt         ← 維持（本番実データ）
├── baychat_api_payload.txt     ← 維持（リクエスト実例）
└── spec_sheets/
    ├── _README.md              ← 各CSVの扱い明記
    ├── _active/                ← 参考として残す
    │   ├── SUMMARY_PROMT.csv
    │   ├── promt_spec_48665.csv
    │   ├── Input_item_info.csv
    │   ├── UI.csv
    │   ├── Feedback.csv
    │   ├── quan_diem_test.csv
    │   ├── Compare_models.csv
    │   ├── test-gpt-model.csv
    │   ├── admin_setting.csv
    │   ├── quy_doi_type_chat.csv
    │   ├── Image_feedback.csv
    │   ├── promt_example.csv
    │   └── Follow.csv
    └── _archive/               ← 廃止候補（フェーズ3で移動）
        ├── old_promt_spec.csv
        ├── promt-update.csv
        ├── Quy_doi_chat.csv（重複）
        ├── 2026-03-19.csv（中間スナップ）
        └── AI-update-evd.csv（空）
```

**ただし再整理の実施はCowatechとの合意後**。CSVへのリンクがCowatech側のコードに埋まっている可能性があり、勝手に移動すると依存が壊れる。

---

## 📝 Cowatech向けサマリー

Cowatechに設計図を共有する際に使えるサマリー文（案）：

```markdown
## BayChat AI Reply 統合設計図の運用開始について

2026-04-20 付で、AI Reply の単一参照源として統合設計図を導入します。

### 概要
- 保管場所：reffort-claude リポジトリ `services/baychat/ai/design-doc/`
- マスター：本設計図（Markdown + GitHub）
- 参考資料：既存の19枚CSV（`cowatech_payloads/spec_sheets/`）は「参考資料」にデモート

### 今後の運用
- プロンプト・条件分岐・UI連動などAI Reply関連の仕様は、すべて設計図が正
- 矛盾があれば設計図を優先
- Cowatech側での変更・追加は、まず設計図への記録 → Slack相談 → 実装の順で
- 既存CSVは3か月（2026-07-20まで）は参考資料として残す

### レビュー依頼
添付設計図をご確認いただき、以下について回答いただけますと幸いです：
1. 技術的な誤り・不足
2. 未解決論点（`09_open_questions.md`）への回答
3. 運用ルール（`07_cowatech_operation.md`）への合意

よろしくお願いします。
```

---

## ⚠️ 未解決の論点

| # | 論点 | 重要度 |
|---|-----|------|
| — | CSV廃止がCowatech実装に与える影響の確認 | 🔴 高 |
| — | `cowatech_payloads/spec_sheets/` ディレクトリ再整理のCowatech合意 | 🟡 中 |
| — | CSVへのリンクを持つコード・ドキュメントの棚卸し | 🟡 中 |
| — | 新CSVが今後生まれないことの保証（Cowatech運用徹底） | 🟡 中 |

---

## 📚 関連ドキュメント

| ドキュメント | 役割 |
|----------|------|
| `07_cowatech_operation.md` | 運用ルール（これと密接に連携） |
| `05_changelog.md` | 移行進捗の記録 |
| `09_open_questions.md` | 未解決論点 |
| 各 `block_*.md` | 移行先の詳細 |
