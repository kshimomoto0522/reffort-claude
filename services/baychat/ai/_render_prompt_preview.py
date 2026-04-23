# -*- coding: utf-8 -*-
"""
adminプロンプト v2.6 を社長レビュー用HTMLに変換するスクリプト。

出力:
  prompt_admin_v2.6.html        — 社長がブラウザで読むためのプレビュー
  prompt_admin_v2.6.json        — admin画面にアップロードするためのJSON
"""
import os
import re
import json
import sys
import io
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).parent
MD_FILE = BASE_DIR / "prompt_admin_v2.6.md"
OLD_MD_FILE = BASE_DIR / "prompt_admin_v2.5.md"
HTML_OUT = BASE_DIR / "prompt_admin_v2.6.html"
JSON_OUT = BASE_DIR / "prompt_admin_v2.6.json"


def extract_prompt_body(md_text):
    """```〜```で囲まれたプロンプト本文を取り出す"""
    m = re.search(r"```\n(.*?)```", md_text, re.DOTALL)
    return m.group(1).strip() if m else ""


def generate_html(md_text, version="2.6", old_version="2.5"):
    """Markdownを整形HTMLに変換（既存スタイルに準拠・紫ベース）"""
    try:
        import markdown
        html_body = markdown.markdown(
            md_text, extensions=['tables', 'fenced_code', 'nl2br', 'toc']
        )
    except ImportError:
        # fallback
        html_body = f"<pre>{md_text}</pre>"

    css = """
<style>
  * { box-sizing: border-box; }
  body {
    font-family: 'Yu Gothic UI', 'Segoe UI', -apple-system, sans-serif;
    max-width: 1000px;
    margin: 0 auto;
    padding: 0 32px 60px;
    line-height: 1.75;
    color: #2d2d2d;
    background: #fafafa;
  }
  .hero {
    background: linear-gradient(135deg, #5a189a 0%, #9d4edd 100%);
    color: white;
    padding: 32px 40px;
    margin: 0 -32px 32px;
    border-radius: 0 0 12px 12px;
    text-align: center;
  }
  .hero h1 { margin: 0 0 8px; font-size: 26px; font-weight: 600; }
  .hero .sub { opacity: 0.9; font-size: 14px; }

  .review-box {
    background: white;
    border: 2px solid #c77dff;
    border-radius: 10px;
    padding: 20px 28px;
    margin-bottom: 32px;
  }
  .review-box h2 {
    margin: 0 0 12px;
    color: #5a189a;
    border: none;
    padding: 0;
    font-size: 16px;
  }
  .review-box ol { margin: 0; padding-left: 22px; }
  .review-box li { margin-bottom: 6px; }

  h1 {
    color: #5a189a;
    border-bottom: 3px solid #9d4edd;
    padding-bottom: 10px;
    margin-top: 40px;
  }
  h2 {
    color: #5a189a;
    border-left: 5px solid #9d4edd;
    padding-left: 14px;
    margin-top: 36px;
    font-size: 22px;
  }
  h3 { color: #3c096c; margin-top: 28px; }
  h4 { color: #3c096c; margin-top: 24px; }
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
    border-radius: 6px;
    overflow: hidden;
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
    font-family: Consolas, 'Courier New', monospace;
    font-size: 0.92em;
  }
  pre {
    background: #2d1a45;
    color: #e0d5ef;
    padding: 18px 22px;
    border-radius: 8px;
    overflow-x: auto;
    line-height: 1.55;
    font-size: 13px;
  }
  pre code { background: transparent; color: inherit; padding: 0; }
  ul, ol { padding-left: 28px; }
  li { margin: 4px 0; }
  a {
    color: #7b2cbf;
    text-decoration: none;
    border-bottom: 1px dotted #9d4edd;
  }
  hr {
    border: none;
    border-top: 2px dashed #c77dff;
    margin: 32px 0;
  }
  .nav {
    background: linear-gradient(135deg, #7b2cbf 0%, #9d4edd 100%);
    color: white;
    padding: 12px 20px;
    margin: -32px -32px 24px;
    font-size: 13px;
    text-align: center;
  }
  .nav a { color: white; margin: 0 12px; border-bottom: 1px dotted white; }
  .nav .version-badge {
    display: inline-block;
    background: white;
    color: #5a189a;
    padding: 2px 10px;
    border-radius: 12px;
    font-weight: 700;
    margin: 0 12px;
  }
</style>
"""

    nav = f"""
<div class="nav">
  🧪 <span class="version-badge">v{version}</span>
  <span>前版: v{old_version}</span>
  <span>|</span>
  <a href="javascript:window.print()">印刷</a>
</div>
"""

    review_box = """
<div class="review-box">
  <h2>📋 社長レビューのポイント</h2>
  <ol>
    <li><strong>v2.5 からの変更点</strong>（次セクション）を読む — 何を改善したか</li>
    <li><strong>登録用プロンプト本文</strong>（黒い背景のコードブロック）を読む</li>
    <li>特に新規セクション: <code>EMPATHY ENFORCEMENT</code> / <code>MULTILINGUAL HANDLING</code> / <code>COMPLEX CASE HANDLING</code> の具体例が自然か</li>
    <li>問題なければ JSON ファイル（<code>prompt_admin_v2.6.json</code>）を admin 画面にアップロード</li>
  </ol>
</div>
"""

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>AI Reply adminプロンプト v{version}</title>
{css}
</head>
<body>
{nav}
<div class="hero">
  <h1>🧪 AI Reply adminプロンプト v{version}</h1>
  <div class="sub">v{old_version} からの改善版 — 社長レビュー用プレビュー</div>
</div>
{review_box}
{html_body}
</body>
</html>"""


def generate_admin_json(md_text, version="2.6"):
    """admin画面アップロード用のJSON出力"""
    prompt_body = extract_prompt_body(md_text)

    # 変更点セクションを抜き出し（レビュー履歴として残す）
    changelog_match = re.search(
        r"## v[\d\.]+ からの変更点\n\n(.*?)\n\n---",
        md_text, re.DOTALL
    )
    changelog = changelog_match.group(1).strip() if changelog_match else ""

    purpose_match = re.search(
        r"## 🎯 v[\d\.]+ の目的\n\n(.*?)\n\n---",
        md_text, re.DOTALL
    )
    purpose = purpose_match.group(1).strip() if purpose_match else ""

    return {
        "version": version,
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "prompt_body": prompt_body,
        "purpose": purpose,
        "changelog": changelog,
        "model_target": "gpt-5-nano",
        "notes": "FORCED_TEMPLATE除去済（2026-04-22 Cowatech prd反映）+ "
                 "{buyerAccountEbay}/{sellerAccountEbay}プレースホルダで挨拶・署名制御。"
                 "v2.5の弱点（return/complex/多言語）を改善。"
    }


def main():
    md_text = MD_FILE.read_text(encoding="utf-8")

    # HTML出力
    html = generate_html(md_text, version="2.6", old_version="2.5")
    HTML_OUT.write_text(html, encoding="utf-8")
    print(f"[OK] HTML: {HTML_OUT}")

    # JSON出力
    admin_json = generate_admin_json(md_text, version="2.6")
    JSON_OUT.write_text(
        json.dumps(admin_json, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"[OK] JSON: {JSON_OUT}")
    print(f"     プロンプト本文長: {len(admin_json['prompt_body'])} 文字")


if __name__ == "__main__":
    main()
