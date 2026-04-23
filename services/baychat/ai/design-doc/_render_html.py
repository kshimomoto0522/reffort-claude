# -*- coding: utf-8 -*-
"""
design-doc/ 配下の .md を全てHTMLに変換するスクリプト。
社長レビュー用。BayChat UI設計原則（紫ベース・シンプル・読みやすさ）に準拠。
"""
import os
import markdown
from pathlib import Path

BASE_DIR = Path(__file__).parent
HTML_DIR = BASE_DIR / "_html_preview"
HTML_DIR.mkdir(exist_ok=True)

CSS = """
<style>
  body {
    font-family: 'Yu Gothic UI', 'Segoe UI', -apple-system, sans-serif;
    max-width: 960px;
    margin: 0 auto;
    padding: 32px 40px;
    line-height: 1.75;
    color: #2d2d2d;
    background: #fafafa;
  }
  h1 {
    color: #5a189a;
    border-bottom: 3px solid #9d4edd;
    padding-bottom: 12px;
    margin-top: 0;
  }
  h2 {
    color: #5a189a;
    border-left: 5px solid #9d4edd;
    padding-left: 14px;
    margin-top: 36px;
  }
  h3 {
    color: #3c096c;
    margin-top: 28px;
  }
  h4 {
    color: #3c096c;
    margin-top: 24px;
  }
  blockquote {
    border-left: 4px solid #c77dff;
    background: #f3e8ff;
    margin: 16px 0;
    padding: 12px 20px;
    color: #3c096c;
    border-radius: 4px;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
    background: white;
    font-size: 14px;
  }
  th {
    background: #9d4edd;
    color: white;
    padding: 10px 12px;
    text-align: left;
    border: 1px solid #7b2cbf;
  }
  td {
    padding: 10px 12px;
    border: 1px solid #e0d5ef;
    vertical-align: top;
  }
  tr:nth-child(even) td { background: #faf5ff; }
  code {
    background: #f0e6fa;
    color: #5a189a;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 0.92em;
  }
  pre {
    background: #2d1a45;
    color: #e0d5ef;
    padding: 16px 20px;
    border-radius: 6px;
    overflow-x: auto;
    line-height: 1.5;
  }
  pre code {
    background: transparent;
    color: inherit;
    padding: 0;
  }
  a {
    color: #7b2cbf;
    text-decoration: none;
    border-bottom: 1px dotted #9d4edd;
  }
  a:hover {
    color: #5a189a;
    border-bottom: 1px solid #5a189a;
  }
  hr {
    border: none;
    border-top: 2px dashed #c77dff;
    margin: 32px 0;
  }
  ul, ol { padding-left: 28px; }
  li { margin: 4px 0; }
  .toc-card {
    background: white;
    border: 2px solid #c77dff;
    border-radius: 8px;
    padding: 20px 28px;
    margin: 20px 0;
  }
  .toc-card h2 { margin-top: 0; border: none; padding-left: 0; }
  .status-complete { color: #2d6a4f; font-weight: bold; }
  .status-draft { color: #9a6700; font-weight: bold; }
  .nav {
    background: linear-gradient(135deg, #7b2cbf 0%, #9d4edd 100%);
    color: white;
    padding: 12px 20px;
    margin: -32px -40px 24px -40px;
    font-size: 14px;
  }
  .nav a { color: white; margin-right: 16px; border-bottom: 1px dotted white; }
  .nav a:hover { color: #f3e8ff; border-bottom: 1px solid #f3e8ff; }
  mark { background: #fff3cd; padding: 2px 4px; border-radius: 3px; }
</style>
"""

NAV = """
<div class="nav">
  🏠 <a href="dashboard.html">ダッシュボード</a>
  📖 <a href="index.html">目次</a>
  <a href="README.html">README</a>
  <a href="00_overall_flow.html">全体フロー</a>
  <a href="01_prompt_blocks_overview.html">ブロック俯瞰</a>
  <a href="02_ui_injection_matrix.html">UI注入</a>
  <a href="block_n4_admin_prompt.html">⭐admin_prompt</a>
  <a href="04_conditional_logic.html">条件分岐</a>
  <a href="09_open_questions.html">未解決論点</a>
  <a href="10_api_testing.html">テスト環境</a>
  <a href="06_glossary.html">用語集</a>
</div>
"""

MERMAID_SCRIPT = """
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: false, theme: 'default', securityLevel: 'loose' });
  document.querySelectorAll('pre > code.language-mermaid').forEach((el, i) => {
    const div = document.createElement('div');
    div.className = 'mermaid';
    div.textContent = el.textContent;
    el.parentElement.replaceWith(div);
  });
  mermaid.run();
</script>
<style>
  .mermaid { background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0d5ef; margin: 20px 0; text-align: center; }
</style>
"""

def md_to_html(md_text, title):
    html_body = markdown.markdown(
        md_text,
        extensions=['tables', 'fenced_code', 'nl2br', 'toc']
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{title} | BayChat AI Reply 設計図</title>
{CSS}
</head>
<body>
{NAV}
{html_body}
{MERMAID_SCRIPT}
</body>
</html>"""

# 変換対象
targets = [
    ("README.md", "README"),
    ("00_overall_flow.md", "全体フロー"),
    ("01_prompt_blocks_overview.md", "プロンプトブロック俯瞰"),
    ("02_ui_injection_matrix.md", "UI注入マトリクス"),
    ("04_conditional_logic.md", "条件分岐表"),
    ("05_changelog.md", "変更履歴"),
    ("06_glossary.md", "用語集・FAQ"),
    ("07_cowatech_operation.md", "Cowatech運用ルール"),
    ("08_migration_plan.md", "CSV移行計画"),
    ("09_open_questions.md", "未解決論点集約"),
    ("10_api_testing.md", "API・テスト環境仕様"),
    ("11_model_selection.md", "モデル選定"),
    ("12_ebay_api_integration.md", "eBay API連携仕様"),
    ("13_baychat_api_spec.md", "BayChat API仕様"),
    ("14_qa_testing.md", "QA観点・不具合履歴"),
    ("15_summary_mode.md", "要約モード仕様"),
]

for md_file, title in targets:
    md_path = BASE_DIR / md_file
    if not md_path.exists():
        print(f"SKIP: {md_file}")
        continue
    html_text = md_to_html(md_path.read_text(encoding='utf-8'), title)
    html_path = HTML_DIR / md_file.replace('.md', '.html')
    html_path.write_text(html_text, encoding='utf-8')
    print(f"OK: {html_path.name}")

# block_cards の変換
card_dir = BASE_DIR / "03_block_cards"
for md_path in card_dir.glob("block_*.md"):
    html_text = md_to_html(md_path.read_text(encoding='utf-8'), md_path.stem)
    html_path = HTML_DIR / (md_path.stem + ".html")
    html_path.write_text(html_text, encoding='utf-8')
    print(f"OK: {html_path.name}")

# index.html（トップページ）
index_md = """# BayChat AI Reply 設計図 v0.2（実データ完全統合版）

> 📌 **社長用に最適化された入口：[🏠 ダッシュボード](dashboard.html)**
> **このページは全19ファイルの目次です。**

---

## 🏠 まずはここから

**[🏠 社長ダッシュボード](dashboard.html)** — 5分で全体像を把握できるサマリー画面

---

## 📚 ドキュメント一覧（19ファイル・全て完成版）

### 🗺️ 横断ビュー

| # | ドキュメント | 内容 |
|---|----------|------|
| 1 | [README](README.html) | 目次・使い方 |
| 2 | [00 全体フロー](00_overall_flow.html) | UI→AI→返信表示までの全工程（Mermaid図+解説） |
| 3 | [01 ブロック俯瞰表](01_prompt_blocks_overview.html) | 7ブロックを一枚で俯瞰 |
| 4 | [02 UI注入マトリクス](02_ui_injection_matrix.html) | UI操作→プロンプト注入先の対応表 |
| 5 | [04 条件分岐表](04_conditional_logic.html) | ON/OFF・置換の全条件・APIパラメータ |

### 📇 ブロック詳細カード（7枚）

| # | ブロック | カード |
|---|-------|------|
| [0] | 商品情報JSON | [block_00_item_info](block_00_item_info.html) |
| [1..N] | チャット履歴 | [block_chat_history](block_chat_history.html) |
| [N+1] | 補足情報ガイド | [block_n1_description_guide](block_n1_description_guide.html) |
| [N+2] | BASE_PROMPT | [block_n2_base_prompt](block_n2_base_prompt.html) |
| [N+3] | OUTPUT_FORMAT | [block_n3_output_format](block_n3_output_format.html) |
| **[N+4]** | **admin_prompt** ⭐ | **[block_n4_admin_prompt](block_n4_admin_prompt.html)** |
| [N+5] | FORCED_TEMPLATE | [block_n5_forced_template](block_n5_forced_template.html) |

### 🔧 運用・管理

| # | ドキュメント | 内容 |
|---|----------|------|
| 05 | [変更履歴](05_changelog.html) | 変更を時系列で記録 |
| 07 | [Cowatech運用ルール](07_cowatech_operation.html) | 設計図の管理・更新・レビューフロー |
| 08 | [CSV移行計画](08_migration_plan.html) | 19枚CSVの移行マップ・廃止スケジュール |
| 09 | [未解決論点集約](09_open_questions.html) | Q1-Q24の全論点・Cowatech質問パッケージ |

### 🔌 API・テスト・連携

| # | ドキュメント | 内容 |
|---|----------|------|
| 10 | [API・テスト環境仕様](10_api_testing.html) | testing/配下の完全ドキュメント |
| 12 | [eBay API連携仕様](12_ebay_api_integration.html) | 取得パラメータ42項目・採用状況 |
| 13 | [BayChat API仕様](13_baychat_api_spec.html) | BayChat→Cowatech I/F仕様 |

### 🎯 モデル・QA・将来機能

| # | ドキュメント | 内容 |
|---|----------|------|
| 11 | [モデル選定](11_model_selection.html) | 現行・次期候補・却下モデル |
| 14 | [QA観点・不具合履歴](14_qa_testing.html) | QAチェックリスト7項目・10件不具合記録 |
| 15 | [要約モード仕様](15_summary_mode.html) | 将来機能のドラフト仕様 |

### 📖 参照

| # | ドキュメント | 内容 |
|---|----------|------|
| 06 | [用語集・FAQ](06_glossary.html) | 日英対応100件・FAQ15問・略語集 |

---

## 🚨 Cowatech確認待ちの高優先度論点（9件）

| # | 論点 |
|---|-----|
| Q1 | FORCED_TEMPLATE除去時のTO/FROM注入経路 |
| Q3 | description・TO/FROMの「空/なし」判定ロジック |
| Q4 | チャット履歴の件数・トークン上限 |
| Q5 | multi_language_reply schema名の参照有無 |
| Q6 | Gemini 2.5 Flash実装ロードマップ |
| Q7 | whoPaysShipping欠損の原因 |
| Q8 | 自動メッセージ/手動返信の区別ロジック |
| Q9 | 既存CSVのコード依存の有無 |

詳細：[09 未解決論点集約](09_open_questions.html)
"""
index_html = md_to_html(index_md, "目次")
(HTML_DIR / "index.html").write_text(index_html, encoding='utf-8')
print(f"OK: index.html")
print(f"\n全{len(list(HTML_DIR.glob('*.html')))}ファイル生成完了: {HTML_DIR}")
