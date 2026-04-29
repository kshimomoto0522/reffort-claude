#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostToolUse hook: 社長向けファイルをWrite/Edit直後に自動オープン。

旧 env_auto_open.py を汎用化したもの。
feedback_env_file_handling.md / feedback_file_delivery.md / feedback_proactive_partner.md
の機械的バックボーン。

対象拡張子（社長が見る/編集する可能性のあるファイル）:
  .env / .env.*    : 値入力用
  .md              : ドキュメント（HTMLレンダリング後オープン）
  .html            : 直接ブラウザで開く
  .txt / .csv      : テキスト/データ
  .xlsx / .xlsm    : 表計算
  .pptx            : スライド
  .pdf             : 文書

対象外（コード/設定/内部ファイル）:
  .py / .json / .yml / .toml / .sh など
  + 以下のディレクトリ配下は全種類除外:
    .claude/, archive/, memory/, node_modules/, .git/, __pycache__/
  + ファイル名 CLAUDE.md / index.md（設定/ナビ系で頻繁に編集される）
"""
import json
import sys
import os
import re
from pathlib import Path

# stderrをUTF-8強制 (Claude Code側がUTF-8で読むため)
try:
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass


ENV_BASENAME_RE = re.compile(r"^\.env(\..+)?$")
PRESIDENT_FACING_EXTS = {".md", ".html", ".htm", ".txt", ".csv", ".xlsx", ".xlsm", ".pptx", ".pdf"}
EXCLUDE_DIR_NAMES = {".claude", "archive", "memory", "node_modules", ".git", "__pycache__"}
EXCLUDE_BASENAMES_LOWER = {"claude.md", "index.md", "readme.md", "memory.md"}


def is_excluded_path(p: Path) -> bool:
    parts_lower = {part.lower() for part in p.parts}
    if EXCLUDE_DIR_NAMES & parts_lower:
        return True
    if p.name.lower() in EXCLUDE_BASENAMES_LOWER:
        return True
    return False


def render_md_to_html(md_path: Path) -> Path | None:
    """同じディレクトリに `<basename>.preview.html` を生成して返す。失敗時はNone。"""
    try:
        import markdown
    except Exception:
        return None
    try:
        text = md_path.read_text(encoding="utf-8")
        body = markdown.markdown(text, extensions=["tables", "fenced_code", "toc"])
        css = (
            "body{font-family:'Yu Gothic UI','Segoe UI',sans-serif;max-width:920px;"
            "margin:32px auto;padding:0 24px;color:#1a1a1a;line-height:1.7;}"
            "h1,h2,h3{border-bottom:2px solid #2563eb;padding-bottom:6px;}"
            "h2{margin-top:32px;}h3{border-bottom-color:#94a3b8;}"
            "table{border-collapse:collapse;margin:12px 0;}"
            "th,td{border:1px solid #cbd5e1;padding:6px 12px;}"
            "th{background:#f1f5f9;}"
            "code{background:#f3f4f6;padding:2px 6px;border-radius:4px;font-size:0.92em;}"
            "pre{background:#f3f4f6;padding:12px;border-radius:6px;overflow:auto;}"
            "pre code{background:transparent;padding:0;}"
            "blockquote{border-left:4px solid #94a3b8;color:#475569;margin:0;padding:0 16px;}"
            "a{color:#2563eb;}"
        )
        html = (
            f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'>"
            f"<title>{md_path.name}</title><style>{css}</style></head>"
            f"<body>{body}</body></html>"
        )
        out = md_path.with_suffix(".preview.html")
        out.write_text(html, encoding="utf-8")
        return out
    except Exception:
        return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    tool_input = data.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    p = Path(file_path)
    if not p.exists():
        sys.exit(0)

    basename = p.name
    suffix = p.suffix.lower()

    # .env 系判定（拡張子ではなくbasenameで判定）
    is_env = bool(ENV_BASENAME_RE.match(basename))

    if is_env:
        # .envは除外パスチェックをスキップ（どこにあっても開く）
        target = p
    else:
        # 除外パスチェック
        if is_excluded_path(p):
            sys.exit(0)
        # 拡張子チェック
        if suffix not in PRESIDENT_FACING_EXTS:
            sys.exit(0)

        # .md は HTMLレンダリングして開く
        if suffix == ".md":
            html_path = render_md_to_html(p)
            if html_path is not None:
                target = html_path
            else:
                # マークダウン変換失敗時は生.mdを開く（フォールバック）
                target = p
        else:
            target = p

    # 既定アプリで開く
    try:
        os.startfile(str(target))  # type: ignore[attr-defined]
        kind = ".env(値入力用)" if is_env else f"{suffix}({'HTMLプレビュー' if suffix == '.md' and target != p else '直接'})"
        print(
            f"[file_auto_open] Opened: {target} [{kind}]\n"
            f"[file_auto_open] REMINDER: 社長に「{target.name} を開きました」と必ず先に宣言してから次に進むこと。",
            file=sys.stderr,
        )
    except Exception as e:
        print(
            f"[file_auto_open] Failed to open {target}: {e}\n"
            f"[file_auto_open] 手動で `start \"\" \"{target}\"` を実行してください。",
            file=sys.stderr,
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
