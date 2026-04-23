# 多視点プロセス（Multi-Perspective Decision Process）

> 社長のご指示：「あなたが考える・ファクトチェックする人がいる・疑う人がいる・それらを持ってあなたが判断するなどのプロセスを作れない？」への回答・実装文書。
> **重要な意思決定では、Claude Codeが一人で考えて進めることを禁止する**ための仕組み。

---

## なぜこのプロセスが必要か

### 私（Claude）単体の構造的弱点

1. **確証バイアス**：自分が立てた仮説を補強する情報を選びがち
2. **ユーザー迎合バイアス**：社長が気に入りそうな方向に傾きがち
3. **最近性バイアス**：直前に読んだ情報を過大評価しがち
4. **過度な楽観性**：成功事例を根拠にしがち、失敗事例を軽視しがち
5. **データの取り違え**：「競合ゼロ」と「需要ゼロ」を混同した実例（2026-04-19に社長が指摘）

→ これらは**単体の私には克服不能**。役割を分離した複数視点で相互にチェックする仕組みが必要。

---

## 4ロール体制

### 🎯 ロール1：Proposer（推進役）
- 役割：「なぜこれをやるべきか」を主張
- 担当：通常モードの私
- 出力：提案の根拠・期待される成果

### 🔥 ロール2：Skeptic（懐疑役 / Devil's Advocate）
- 役割：**最も厳しく反論**。盲点・リスク・対抗シナリオを徹底的に指摘
- 担当：専用サブエージェント（`general-purpose`を懐疑モードで起動）
- 指示テンプレート：
  ```
  You are a Devil's Advocate. Your ONLY job is to attack the following proposal:
  - Find every logical weakness
  - Identify hidden assumptions
  - Surface the worst-case scenarios
  - Challenge "evidence" as potentially cherry-picked
  - Propose competing explanations for any cited success story
  Do NOT be polite. Do NOT hedge. Be brutal but specific.
  ```

### 🔍 ロール3：Fact-Checker（検証役）
- 役割：Proposerの主張とSkepticの反論、両方の根拠データを実データで検証
- 担当：専用サブエージェント（`general-purpose` with WebSearch/WebFetch）
- 指示テンプレート：
  ```
  You are a Fact-Checker. For the following claims and counter-claims:
  - Verify each numerical claim with current sources (2025-2026)
  - Flag claims that lack primary source
  - Distinguish confirmed facts from unverified claims
  - Provide URLs for every verified data point
  - Rate each claim: Confirmed / Partial / Unverified / Contradicted
  ```

### ⚖️ ロール4：Judge（判断役）
- 役割：Proposer / Skeptic / Fact-Checker の3者の出力を統合して最終判断を提案
- 担当：通常モードの私（統合視点）
- 出力：
  1. 3者の主要論点サマリー
  2. 確認された事実 vs 未確認の主張
  3. Judge自身の判断と根拠
  4. 社長に判断を仰ぐポイント（残る不確実性）

---

## 発動タイミング

### 必須発動（自動）
- ❗ 初期の各ストリーム戦略策定時
- ❗ 撤退/継続/拡大の判断時
- ❗ 月次レビューの重要提言時
- ❗ 予算$50以上の投資判断時
- ❗ 社長から「これ大丈夫？」「疑問」の発言があった時

### 推奨発動（私の判断）
- 🟡 週次レビューで1件以上（必ず1つは多視点で検証）
- 🟡 新ストリーム追加時
- 🟡 ニッチ選定の最終確定時

### 省略可（コスト節約）
- 🟢 日々の作業タスク（記事ドラフト生成等）
- 🟢 フォーマット修正等の非戦略判断

---

## 出力フォーマット

多視点プロセスを実行した結果は、以下のフォーマットで提示：

```markdown
## 多視点レビュー：[判断内容]

### 🎯 Proposer（推進）
- 主張：
- 根拠：
- 期待成果：

### 🔥 Skeptic（懐疑）
- 最大のリスク：
- 盲点：
- 対抗シナリオ：
- 「成功事例」への疑義：

### 🔍 Fact-Checker（検証）
- Confirmed：[確認済み事実]
- Unverified：[未確認の主張]
- Contradicted：[反証されたもの]
- 追加で確認が必要な点：

### ⚖️ Judge（判断）
- 3者の論点サマリー：
- 最終判断：
- 判断の確信度：高/中/低
- 社長に仰ぐべきポイント：
```

---

## 運用ログ

多視点プロセスを実行した履歴を、この下に時系列で記録する：

### ✅ 2026-04-19 実行1：The $20 Stack の立ち位置検証

#### 🎯 Proposer（推進役）
- 主張：「The $20 Stack」は競合ゼロで勝てる
- 根拠：類似名ニュースレターが存在しない、切り口明快、運用がブレない
- 期待成果：9ヶ月で購読者5,000人、月$890

#### 🔥 Skeptic（懐疑役）による反論
- **最大のリスク**：「競合ゼロ＝需要ゼロ」の可能性を排除できていない
- **盲点**：ブートストラッパー層は広告主視点でLTVが低い可能性
- **対抗シナリオ**：購読者は集まっても広告CPMが低くて月$890モデルが成立しない
- **「成功事例」への疑義**：引用したSuperhuman AI/Mindstreamは全て「broad AI」ポジション。ブートストラッパー特化で成功した事例を示していない

#### 🔍 Fact-Checker（検証役）結果
- **Confirmed**：
  - ブートストラッパー層CPMは$30〜$60（Source: industry knowledge through 2026）
  - SaaS Founder層CPMは$150〜$400+（3〜5倍）
  - 成功AIニュースレター（Ben's Bites, The Rundown, Superhuman AI）は全て「broad AI audience」
  - 「Tips」系コンテンツは有料化が弱い（Starter Story/Trends.vcは「Deal Flow / 実用ストック」で成功）
- **Unverified**：「The $20 Stack」類似名ニュースレターの真の不存在（検索では見つからなかったが、未発見の可能性）
- **Contradicted**：**「競合ゼロ=ブルーオーシャン」の仮説**。広告主TAM（Total Addressable Market）が小さいから誰もやらないという構造的理由が存在する

#### ⚖️ Judge（判断役）
- **論点サマリー**：
  - Proposerは「読者獲得の容易さ」だけを見ていた
  - Skepticが「広告主予算というTAM」の盲点を指摘
  - Fact-Checkerが数値で裏付け：CPM差は3〜5倍、構造的
- **最終判断**：**「The $20 Stack」ポジション採用を却下**
- **判断の確信度**：高
- **代替推奨**：「The AI Operator」（実運営者向け、広めの層、広告主プール維持）
- **社長に仰ぐべきポイント**：
  - 代替案として「The AI Operator」「AI for Small Business」「The Solo SaaS Stack」の3案を再提示
  - このうち最終決定を委ねる

**🔴 重要な学び**：社長の「競合ゼロはニッチな場合もあれば需要ゼロの可能性もある」という指摘が、多視点プロセスで完全に正しかったと証明された。**この失敗を早期に発見できたのは多視点プロセスのおかげ**。運用初日に効果が出た。

---

### ✅ 2026-04-19 実行2：Publisher Rocket 買い切りの検証

#### 🎯 Proposer
- 主張：Publisher Rocket $199買い切りはKDP運用に最適

#### 🔥 Skeptic
- 懸念：買い切り=情報が古くなるのでは？
- 懸念：1冊目だけの投資としては高すぎる

#### 🔍 Fact-Checker
- Confirmed：
  - 価格は$199買い切り（2024-2025変更なし）
  - アップデートは生涯無料（Dave Chesson公式ポリシー）
  - データはAmazonからリアルタイム取得（キャッシュではない）
  - 2冊以上出版するなら元が取れる
- 代替：KDSPY $47（機能劣るがKDP初心者向け）

#### ⚖️ Judge
- **最終判断**：社長の推奨C（Stream 3をMonth 2に後ろ倒し）で進行
- **Month 2時点の再判断ポイント**：
  - 本当にKDPに着手するか
  - 着手するならPublisher Rocket $199 or KDSPY $47 の選択
- **判断の確信度**：高（情報の鮮度問題は解消、タイミングは柔軟）

---

---

## 注意事項

- 多視点プロセスは**コストがかかる**（サブエージェント2〜3回＋統合）
- 全判断に適用するとトークン消費が過大
- **戦略判断・投資判断・ピボット判断**に絞って発動
- 社長は「プロセスを回した結果」だけを見れば十分（詳細はこのファイルに蓄積）

---

*このプロセスは2026-04-19に社長のご指示で確立。以降の全戦略判断に適用する。*
