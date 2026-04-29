---
name: ファイル作成後は即座に開く
description: ファイルを作成・生成したら「フォルダに作りました」ではなく、その場で開くかエクスプローラーで見つけられるようにする
type: feedback
originSessionId: cad5d328-fbe2-462e-8502-6ca7c9ebaa09
---
ファイルを作成したら、社長に探させず即座にアクセスできるようにする。

**Why:** 「フォルダの中に作りました」と言われても、エクスプローラーでフォルダを開いて探しに行く手間がかかる。社長はプログラマーではないので、パスを見てもすぐにたどり着けないことがある。

**How to apply:**
- ファイル生成後は `start ""` コマンドでファイルを直接開く（PPTX→PowerPoint、PDF→デフォルトビューアー、HTML→ブラウザ、**.md→既定エディタ**、.py→既定エディタ、.json→既定エディタ、.xlsx→Excel、.txt→メモ帳 など **全ファイル種別が対象**）
- もしくはフォルダを `start "" "フォルダパス"` で開いてファイルが見える状態にする
- 「Chatworkに送って」と言われていない限り、まずローカルで開く
- パスだけ伝えて終わりにしない

### ⚠️ 頻出NGパターン（2026-04-15 再注意）
以下の言い回しは **全てルール違反** と判断する。使わない。
- 「`xxx.md` に保存しました」「ファイルに書き出しました」「〇〇フォルダに作成しました」で終わる
- コード内容をチャットに貼り付けて「必要なら開きます」と受け身になる
- 「パスは〇〇です」だけ伝える

### ✅ 正しい流れ（例外なし）
1. Write / Edit でファイル作成
2. **同じターン内で** `start "" "絶対パス"` を実行して開く（`.claude/hooks/file_auto_open.py` が自動補助）
3. ユーザーには「開きました。要点は〜」と**開いたことを先に宣言**してから説明に入る
4. どんなに小さい変更でも、社長が見る可能性があるファイルは全て開く

### 🔧 機械化バックアップ（2026-04-25）
- `.claude/hooks/file_auto_open.py`（PostToolUse / `Write|Edit`）：`.env*` `.md` `.html` `.txt` `.csv` `.xlsx` `.pptx` `.pdf` を自動オープン。`.md` は HTML プレビュー化して開く。除外：`.claude/` `archive/` `memory/` 配下、`CLAUDE.md` `index.md` `README.md` 等
- `.claude/hooks/action_guard_stop.py`（Stop / 警告のみ）：応答中の NG フレーズ（「ダブルクリック」「開いて確認してください」「探してください」等）を検出して警告
- 詳細：`.claude/rules/honesty_and_self_completion.md`（誠実性 > 自己完結 > 言葉遣い の優先順位）

**適用範囲**: 全部門・全タスク。.md / .py / .json / .xlsx / .pptx / .pdf / .html / .txt 等ファイル種別を問わない。

### 📄 .md ファイルは必ず整形HTMLに変換して開く（2026-04-15 追加）
社長はプログラマーではないため、`#` `|` `*` などマークダウン記号のままでは読みづらい。**.mdを社長に見せる時は必ずHTMLに変換してブラウザで開く**。

**手順（定型）:**
```python
import markdown
with open('path/to/file.md', 'r', encoding='utf-8') as f:
    md_text = f.read()
html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
# CSS付きHTMLに埋め込んで保存
with open('path/to/file.html', 'w', encoding='utf-8') as f:
    f.write(styled_html)
# start "" で開く
```

**CSSテンプレート**: 見出しに青ライン / 表に枠線 / コードに薄グレー背景 / フォントは日本語対応（Yu Gothic UI / Segoe UI）。

**例外**: 社長自身が「生の.mdで見たい」と明示した場合のみ、素のまま開く。

### 📱 AI出力JSON・テスト結果は必ずUIレンダリング（2026-04-15 追加・最重要）
社長は非エンジニア。`{"summary": {...}}` のような生JSONやPython構造を見せるのは**絶対NG**。テスト・プロンプト開発・機能説明で出力を見せる時は、**常にセラーが実画面で見るUIに近い形にHTML/ブラウザレンダリング**する。

**該当するケース:**
- AI Reply・要約モード等のJSON出力サンプル
- バッチテスト結果（モデル比較など）
- プロンプトに含まれるJSON Schema例

**定型ツール:**
- `services/baychat/ai/testing/render_summary_view.py` : 要約モード用レンダラー
- 今後機能が増えるたびに専用レンダラーを追加する

**禁止パターン:**
- チャット本文にJSONコードブロックを貼ってレビューを求める
- 「この形式でいいですか」とJSONスキーマだけ見せて確認を取る
- .md内のサンプル出力をJSONのまま表示して開く（必ずHTMLプレビュー化）

**正しいフロー:**
1. JSON出力の仕様を決める
2. **即座にHTMLレンダラーを書く**（新機能ごとに1ファイル）
3. サンプルJSONを流して `start "" "preview.html"` で開く
4. 社長はレンダリング済み画面で確認・フィードバック
5. テスト実行時もレンダリング済みHTMLを全ケース分自動生成
