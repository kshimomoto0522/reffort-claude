# C1 The Novelist's Claude Toolkit - Notion Template Structure

**フラッグシップ商品の中核：Notionテンプレート設計書**

購入者が受け取るNotionテンプレートの完全な構造仕様。制作時のブループリント。

---

## Top-Level Dashboard（ルートページ）

### 構成
```
🏠 Novelist's Claude Toolkit
├── 📊 Project Dashboard
├── 📘 Current Novel
├── 👤 Characters Database
├── 🗺️ Worldbuilding Wiki
├── 📖 Chapters & Scenes
├── 🎯 Plot Thread Tracker
├── 💬 Claude Prompts Library
├── 📚 Research Vault
├── ✏️ Revision Checklist
└── 📖 How to Use This Template
```

### Dashboardに表示するもの
- 現在進行中の小説カード（タイトル、ジャンル、目標文字数、進捗％）
- This Week's Writing Goal
- Recent Claude Sessions（最近使ったプロンプトのログ）
- Quick Actions（「新しい章を追加」「キャラクター追加」「プロンプト検索」）

---

## 📘 Current Novel

### Properties
- Title (text)
- Genre (select: Fantasy, Mystery, Romance, Sci-Fi, Literary, Thriller, Horror, YA, Other)
- Target word count (number)
- Current word count (number)
- Start date (date)
- Target completion date (date)
- Status (select: Outlining, Drafting, Revising, Complete)
- One-line premise (text)
- Elevator pitch (text, 2-3 sentences)
- Theme (text)

### Sub-pages
- Synopsis (long text)
- Outline（3-act / Save the Cat / Hero's Journey を選択可能）
- Character Arcs（キャラクター別のアーク追跡）

---

## 👤 Characters Database

### Properties
- Name (title)
- Role (select: Protagonist, Antagonist, Supporting, Minor)
- Archetype (select)
- Appearance (text)
- Core Want (text)
- Core Need (text)
- Backstory (long text)
- Voice sample (text, 2-3行のサンプル対話)
- Arc summary (long text)
- First appearance (chapter link)
- Claude session links (relation to Prompts)

### 関連プロンプト（Prompts Libraryから参照）
- Character Creation Starter
- Voice Development Sample Dialogue
- Backstory Generation
- Character Arc Planner
- Flaw & Strength Balance

---

## 🗺️ Worldbuilding Wiki

### Sub-databases
- Locations (properties: Name, Type, Description, First appearance, Related characters)
- Factions/Groups
- Magic Systems / Technology (ジャンルによって)
- Cultures / Societies
- Timeline of events

### 関連プロンプト
- World Map Generator
- Culture Builder
- Magic System Consistency Check
- Historical Timeline Generator

---

## 📖 Chapters & Scenes

### Chapters Database
- Properties: Number, Title, POV Character, Word count, Status, Summary, Scene count
- Sub-pages: Full chapter text

### Scenes Database（各Chapterのsub）
- Properties: Scene number, POV, Setting, Characters present, Time of day, Goal, Conflict, Outcome, Word count
- Sub-pages: Scene draft

### 関連プロンプト
- Scene Builder (goal-conflict-outcome)
- Pacing Analyzer
- Sensory Detail Enhancer
- Chapter Opening Generator

---

## 🎯 Plot Thread Tracker

### Properties
- Thread name (title)
- Type (select: Main plot, Subplot, Character arc, Mystery, Romance, etc.)
- Setup chapter (relation)
- Development chapters (relation, multi)
- Payoff chapter (relation)
- Status (select: Setup, Building, Climax, Resolved)
- Related characters (relation)

---

## 💬 Claude Prompts Library（中核）

### 50+ プロンプトを以下の構造で整理

**カテゴリ別フォルダ**：

#### Plot Development (10 prompts)
1. Three-Act Outline Generator
2. Save the Cat Beat Sheet
3. Hero's Journey Adaptation
4. Plot Hole Detector
5. Twist Generator
6. Stakes Escalation Prompt
7. Climax Design Prompt
8. Opening Hook Generator
9. Ending Variations Brainstorm
10. Pacing Adjustment Analyzer

#### Character (12 prompts)
1. Protagonist Starter (Want + Need + Flaw)
2. Antagonist Design (Motivation + Method)
3. Supporting Cast Balancer
4. Character Voice Sample Generator
5. Dialogue Diagnostic (does it fit the character?)
6. Backstory Deep Dive
7. Character Arc Tracker
8. Relationship Dynamic Mapper
9. Archetype Fresh Spin
10. Flaw to Growth Converter
11. Physical Description Variety
12. Name Generator by Genre

#### Dialogue (8 prompts)
1. Dialogue Draft from Scene Purpose
2. Subtext Injector
3. Voice Consistency Check
4. Tension Amplifier
5. Info Dump Breaker
6. Argument Structure Builder
7. Silence & Action Beat Integrator
8. Dialect/Speech Pattern Designer

#### Scene Writing (10 prompts)
1. Scene Purpose Definer
2. POV Depth Enhancer
3. Sensory Detail Layer
4. Action Sequence Clarifier
5. Emotional Beat Insertion
6. Scene Transition Smoother
7. Setting Description Generator
8. Flashback Integration
9. Internal Monologue Calibrator
10. Scene Cut Analyzer

#### Worldbuilding (6 prompts)
1. Culture Designer
2. Magic/Tech System Rules
3. Political Structure Generator
4. Religion/Belief System Creator
5. Geography-to-Culture Connection
6. Historical Event Generator

#### Revision & Editing (4 prompts)
1. Chapter-level Diagnostic
2. Line Editing Pass
3. Voice Consistency Check
4. Filler Word Eliminator

### 各プロンプトの構造

```
---
Prompt Name: [例] Three-Act Outline Generator
Category: Plot Development
When to use: [説明]
Works best with: Claude Opus / Sonnet
---

[プロンプト本体]

[Output example]

[Variations / tweaks]
```

---

## 📚 Research Vault

小説のリサーチ資料置き場
- Reference articles (URL + summary)
- Research sessions with Claude (Perplexity連携のNotion import)
- Image references
- Historical facts
- Expert notes

---

## ✏️ Revision Checklist

### Pass 1: Structural
- [ ] Each chapter has clear purpose
- [ ] Plot threads all resolve or have intentional dangle
- [ ] Character arcs complete
- [ ] Pacing chart balanced

### Pass 2: Scene-level
- [ ] Every scene has goal-conflict-outcome
- [ ] POV consistency
- [ ] Sensory details sufficient

### Pass 3: Line-level
- [ ] Voice consistency
- [ ] Dialogue tags minimized
- [ ] Filter words removed
- [ ] Passive voice audited

### Pass 4: Polish
- [ ] Opening hook
- [ ] Closing line
- [ ] First chapter vs last chapter tonal check

---

## 📖 How to Use This Template

### Quick Start (10 min)
1. Duplicate template to your Notion
2. Fill in Current Novel (title, genre, premise)
3. Add your main character to Characters Database
4. Pick one prompt from Plot Development
5. Run it with Claude
6. Paste output back to your dashboard

### Typical Workflow
（詳細なワークフロー図を含む）

---

## 制作工数見積もり

- Notion template構築：約8-12時間（社長＋Claude Codeの組み合わせ）
- Prompts執筆＆テスト：約15-20時間
- Sample outputs生成：約5-8時間
- PDF Guide執筆：約10-15時間
- カバー画像制作：約5-8時間（Canva）

**合計：約43-63時間**

これを4-6週間で完成させる前提で、週あたり10-15時間の作業量。
うち**社長の作業は週1-2時間**（承認・最終調整のみ）。

---

## 次のアクション

社長承認後：
1. Notionテンプレートの実装着手
2. 50プロンプトの第1段目（Plot 10本）から執筆
3. 並行してサンプルアウトプット生成
4. 毎週金曜に進捗と試作を社長に提出

---

*2026-04-19 Claude Code設計。C1フラッグシップの完全仕様書*
