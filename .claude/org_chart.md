# Reffort AIエージェント組織図

> 2026-05-06 隔週メンテで策定。Phase 1 = Education部門のみテスト運用中。
> 全体構想（5部門フルスタック）は段階導入。**現在進行中の部門に🟢、未稼働は⚪**。

---

## 組織図（全体構想・3階層 × 5部門）

```
                ┌─────────────────────┐
                │   社長 (CEO・最終判断)   │
                └──────────┬──────────┘
                           │ 単一窓口で報告
                ┌──────────▼──────────┐
                │  Claude PM/COO（私）   │
                │  → .claude/pm_role.md │
                └──────────┬──────────┘
       ┌────────┬─────────┼─────────┬────────┐
       ▼        ▼         ▼         ▼        ▼
   Commerce  Services 🟢Education Operations Marketing
   ⚪Lead    ⚪Lead    🟢Lead     ⚪Lead    ⚪Lead

   (eBay事業) (BayChat (Campers   (社内自動化 (対外発信)
              BayPack)  コンサル)   セキュリ)
```

**🟢 = Phase 1で稼働中** / **⚪ = Phase 2-3で順次立ち上げ予定**

---

## Phase 1：Education部門の構成（2026-05-06〜稼働）

```
Education Lead
  → .claude/agents/education-lead.md
        │
        ├─ Webinar-Architect（5/31ウェビナー最優先）
        │   → .claude/agents/webinar-architect.md
        │
        ├─ Course-Curator（6月コンサル開始向け教材）
        │   → .claude/agents/course-curator.md
        │
        ├─ Content-Recorder（journey-log・session-log・content-projects）
        │   → .claude/agents/content-recorder.md
        │
        └─ Campers-Operator（暫定：Operations部門立ち上げまでEducation配下）
            → 既存タスク CampersMemberRemoval（Windowsタスク）
```

呼び出し方:
- `/education <依頼内容>` で Education Lead が受付・Specialist振分け
- メイン会話のPM/COOが直接 Specialist を Agent ツールで呼ぶことも可

---

## 承認ゲート（Education部門用）

| カテゴリ | 自走OK | 社長承認必須 |
|---|---|---|
| 骨子ドラフト・スライド草稿 | ✅ | — |
| 教材コンテンツのドラフト | ✅ | — |
| journey-log・session-log 更新 | ✅ | — |
| content-projects 内部整理 | ✅ | — |
| **ウェビナー本番台本確定** | — | ❌ 社長OKまで「ドラフト」 |
| **コース受講者向け公開コンテンツ** | — | ❌ 社長承認後配布 |
| **Campersコミュニティ告知** | — | ❌ 社長承認後送信 |
| **Note・X 発信** | — | ❌ 2軸戦略ルール準拠（feedback_content_audience_framing.md） |
| **配信スケジュール変更** | — | ❌ 社長判断 |

---

## 部門間連携ルール

- Education部門の作業がEducation外（commerce/services/etc）に影響する時は、PM/COOへエスカレーション
- 例: ウェビナーで eBay 機能を扱う → Commerce部門立ち上げまではPMが直接対応
- Cowatech連絡は Services部門立ち上げまでPM直轄

---

## 段階導入（再掲・ロードマップ）

| Phase | 期間 | 範囲 | 状態 |
|---|---|---|---|
| Phase 1 | 2026-05-06〜 | Education部門のみ + PM/COO | **🟢 稼働中** |
| Phase 2 | 5/31ウェビナー後〜 | Commerce 部門追加（eBay事業） | ⚪ 計画中 |
| Phase 3 | 6月以降 | Services（BayChat/BayPack）+ Operations 部門追加 | ⚪ 計画中 |
| Phase 4 | 9月以降 | Marketing 部門追加・KPI最適化・全社化 | ⚪ 計画中 |

---

## 隔週メンテでの定常レビュー項目

第1・第3月曜の隔週メンテで以下を計測：
- 各エージェントの起動回数（直近2週間）
- 社長の承認介入回数
- Specialist 増減・統合・廃止候補
- 部門 Lead 経由 vs PM 直轄 の所要時間比較

→ Operations部門立ち上げ後は Memory-Curator がこの計測を担当。それまでは隔週メンテ Slash Command 内で都度計測。

---

*最終更新: 2026-05-06 午後（隔週メンテで Phase 1 立ち上げ）*
