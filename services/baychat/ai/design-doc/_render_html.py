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
  <a href="README.html">🏠 一覧</a>
  <a href="block_00_item_info.html">[0] 商品情報</a>
  <a href="block_chat_history.html">[1..N] チャット履歴</a>
  <a href="block_n1_description_guide.html">[N+1] 補足情報</a>
  <a href="block_n2_base_prompt.html">[N+2] BASE</a>
  <a href="block_n3_output_format.html">[N+3] OUTPUT</a>
  <a href="block_n4_admin_prompt.html">[N+4] ⭐admin_prompt</a>
  <a href="block_n5_forced_template.html">[N+5] 廃止</a>
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

# 変換対象（2026-04-23 シンプル化：08/10/11/14/15を_reffort_internal/へ移動したため除外）
targets = [
    ("README.md", "AI Reply プロンプト構成"),
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

# README.html が入口なので index.html は作成しない
print(f"\n全{len(list(HTML_DIR.glob('*.html')))}ファイル生成完了: {HTML_DIR}")
