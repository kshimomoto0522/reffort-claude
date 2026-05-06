# /education コマンド

Education部門への依頼を Education Lead エージェント経由で処理する。
Phase 1（2026-05-06〜）テスト運用中。

---

## 引数

`/education <依頼内容>` の形で起動。

例：
- `/education 5/31ウェビナーの台本ドラフトを仕上げて`
- `/education AIコースの30日カリキュラムを叩き台で作って`
- `/education 今日やったこと全部 journey-log.md に追記しておいて`
- `/education 隔週メンテのsession-logを教材化できる切り口で整理`

---

## 実行手順

### Step 1: PM/COO（メイン会話）が依頼を受付

社長から `/education <依頼内容>` で起動された時、PM/COOは以下を実行：

1. 依頼内容が **Education部門の管轄か** を確認（管轄外なら `.claude/pm_role.md` の振分け表に従う）
2. 「これはEducation部門の案件として進めます」と社長に宣言
3. 依頼を以下の項目で整理してEducation Leadに渡す準備：
   - **目的**: 何を達成するか
   - **期限**: いつまでに（明示なければ「次回隔週メンテまで」）
   - **成功条件**: 何ができたら完了か
   - **承認ゲート**: 社長承認が必要なポイント（`.claude/org_chart.md` 参照）
   - **既存資産**: 関連 memory / handoff / content-projects のパス

### Step 2: Education Lead エージェントを Agent ツールで起動

```
Agent(
  subagent_type: "education-lead",
  description: "Education Lead 委任",
  prompt: <Step 1で整理したパッケージ>
)
```

Education Lead は内部で配下 Specialist（webinar-architect / course-curator / content-recorder）に振り分ける。

### Step 3: 成果を受け取り社長へ報告

Education Lead からの返答を受けて、PM/COO（メイン会話）が社長に報告：

1. 成果物の場所・概要
2. **社長承認待ちのドラフト箇所を必ず明示**（org_chart.md の承認ゲートに従う）
3. 関連 commit hash
4. 次に必要なアクション

報告は `feedback_chatwork.md` 準拠（重要案件は Chatwork個人DMにも箱型カードで送信）。

---

## 承認ゲート（PM/COOが必ず守る）

`.claude/org_chart.md` の Education部門承認ゲート表に従う。要点：

**自走OK（社長確認なしで進めて良い）**:
- 骨子・スライド・教材のドラフト
- journey-log・session-log 更新
- content-projects 内部整理

**社長承認必須（必ず止めて社長に投げる）**:
- ウェビナー本番台本確定
- コース受講者向け公開コンテンツ
- Campersコミュニティ告知
- Note・X 発信
- 配信スケジュール変更

---

## やってはいけないこと

- ✕ Education Lead を経由せずPM直接やる（組織化の意味なし・形骸化）
- ✕ Education部門外（Commerce / Services 等）の依頼を `/education` で受ける
- ✕ 専門用語を素人向けに噛み砕かず社長に報告
- ✕ 社長承認必須案件を「ドラフトです」と明示せず仕上げる
- ✕ Cowatech / 外注スタッフへ直接連絡（PM経由で社長承認後）

---

## Phase 1 期間中（2026-05-06〜）の運用感レビュー

隔週メンテで以下を計測：
- `/education` の起動回数（直近2週間）
- Specialist 振分け頻度（webinar-architect / course-curator / content-recorder）
- 社長承認介入回数
- PM直轄でやった方が速かったケース（あれば次回隔週メンテで方針見直し）

→ Phase 2（Commerce部門立ち上げ）の判断材料に使用。
