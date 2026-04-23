# ブロックカード：[N+1] 補足情報ガイド

> ✅ **v0.2 完成版**

---

## 📇 基本情報

| 項目 | 内容 |
|------|------|
| **ブロックID** | `description_guide` |
| **順序** | [N+1]（チャット履歴の直後・BASE_PROMPTの前） |
| **role** | `developer` |
| **管理主体** | Cowatech（テンプレ固定） |
| **現行バージョン** | 仕様固定 |
| **実物ファイル** | `SUMMARY_PROMT.csv`「AI guide 生成ルール」行 |
| **変更頻度** | 🟡 低 |
| **ON/OFF** | **条件付き：補足情報（description）が空でない場合のみ注入** |
| **概算トークン** | ~30 tokens |

---

## 🎯 このブロックの目的

セラーが「補足情報」欄に自分の意図を入力したとき、AIに「そのトーンとユーザー入力を元にQ&Aを作成せよ」と指示する。

---

## 📐 現行の原文（`SUMMARY_PROMT.csv` 由来）

```text
Create questions/answers as requested,
with a '{{Tone}}' tone and the main content being: '{{User input in sreen}}'.
```

**⚠️ 注記**：原文に **"sreen" というtypo** が含まれている（本来は "screen"）。Cowatech側の仕様書上でtypoしており、本番実装にそのまま反映されている可能性が高い。

---

## 🎛️ 動的プレースホルダ

| プレースホルダ | 置換元 | 空のときの挙動 |
|--------------|--------|------------|
| `{{Tone}}` | UIトーンプルダウン | 必須UIのため空にならない |
| `{{User input in sreen}}` | UI補足情報欄 | **このブロック自体がスキップされる想定** |

---

## 🔀 条件分岐ロジック

**本番ペイロード（`gpt_api_payload.txt`）の観察結果**：
- 本番実例ではこのブロックは**注入されていない**（descriptionが空だったため）
- admin_prompt 内の `{sellerSetting}` プレースホルダは空文字で置換されている

**→ ロジックの推定**：
```
if (description is not empty):
    inject description_guide block at [N+1]
else:
    skip this block
```

**🔴 未確認**：
- 判定ロジック（空文字？null？trim後？一定文字数以下？）
- これは **Q3** として Cowatech に確認が必要

---

## 🌐 影響範囲

### 直接影響する要素
- AIが補足情報を意識するかどうかの文脈スイッチ
- Q&A生成のスタイル指示

### 間接影響する要素
- admin_prompt の SELLER INTENT セクションと機能重複の可能性
- `{sellerSetting}` が admin_prompt 側でも処理されており、二重管理リスク

### 副作用のリスク
- このブロック存在時／非存在時でAI挙動が変わる可能性（未検証）
- admin_prompt との整合性が取れていないと、補足情報の扱いが不安定

---

## ⚠️ 未解決の論点

| # | 論点 | 重要度 |
|---|-----|------|
| **Q3** | descriptionが空かどうかの判定ロジック（空文字？null？trim後？） | 🔴 高 |
| — | "sreen" typoの修正（仕様書と本番コードの両方） | 🟡 中 |
| — | このブロックと admin_prompt `{sellerSetting}` のロジック重複整理 | 🟡 中 |
| — | 補足情報ON/OFFによるAI挙動の差分検証（未実施） | 🟡 中 |

---

## 🤝 Cowatech合意事項

| 項目 | 合意内容 | 合意日 | 根拠 |
|------|--------|------|------|
| 配置順序 | [N+1]（条件付き注入） | プロジェクト初期 | `SUMMARY_PROMT.csv` |
| 条件 | descriptionが空でない場合のみ | プロジェクト初期 | `gpt_api_payload.txt`（実例で欠落） |

---

## 📚 関連ドキュメント

| ドキュメント | 役割 |
|----------|------|
| `SUMMARY_PROMT.csv` | このブロックの仕様書 |
| `04_conditional_logic.md` | 条件分岐の詳細 |
| `09_open_questions.md` | Q3の詳細 |
| `block_n4_admin_prompt.md` | `{sellerSetting}` の扱いとの重複整理 |
