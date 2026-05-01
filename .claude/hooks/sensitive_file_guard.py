#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PreToolUse hook (Write|Edit): 機密ファイル名を作成しようとしたら .gitignore 状況を確認して警告。

【目的】
- 4/29発覚: ebay_oauth_tokens.json が4/23から流出していた
- 5/1検出: cache/ebay_app_token.json も同パターン（github_backup.pyの最終防衛線で止めた）
- 本フックは「ファイル作成時点」で警告 → push直前の検出よりさらに早く気づける

【動作】
1. Write/Edit の対象ファイル名をチェック
2. 機密ファイル名パターン（token/credentials/secret/api_key/.pem 等）にマッチ
3. .gitignore で除外されているか確認
4. 除外されていなければ stderr に警告（exit code 0: ブロックせず続行）
   推奨gitignoreパターンを提示

【ブロックしない理由】
- 機密キャッシュ自体は必要（OAuth refresh_token保存等）
- ブロックすると正当なツール開発が止まる
- 「警告 → Claudeが.gitignore追加してから書く」運用にする

設計: github_backup.py の検出ロジックと一貫させる（拡張子除外・パターン同一）
"""

import io
import json
import os
import re
import sys
from pathlib import Path

# Windowsコンソール文字化け対策
try:
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

# ─── github_backup.py と同じ判定ロジック ────────────────
SENSITIVE_NAME_PATTERNS = [
    re.compile(r"(^|/)\.env(?:\.|$)"),
    re.compile(r"\.env\.[A-Za-z0-9_-]+$"),
    re.compile(r"(credentials|secret|token|private_key|apikey|api_key|access_key)", re.IGNORECASE),
    re.compile(r"\.(pem|key|p12|pfx)$"),
]

# コード/ドキュメント拡張子は機密実体を含まないため除外（ファイル名に "token" を含むだけ）
NON_SENSITIVE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".md", ".rst", ".txt",
    ".html", ".htm", ".css", ".scss",
    ".gs", ".gas",
    ".bat", ".sh", ".ps1",
}


def is_sensitive_filename(path: str) -> bool:
    """ファイル名が機密パターンにマッチするか（拡張子フィルタ後）。"""
    # 拡張子取得
    ext = ""
    base = path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    if "." in base:
        ext = "." + base.rsplit(".", 1)[-1].lower()
    if ext in NON_SENSITIVE_EXTENSIONS:
        return False
    # 機密パターン照合
    norm = path.replace("\\", "/")
    return any(p.search(norm) for p in SENSITIVE_NAME_PATTERNS)


def is_covered_by_gitignore(path: str, gitignore_lines: list[str]) -> bool:
    """対象パスが既存 .gitignore パターンでカバーされているかの簡易判定。

    完全な gitignore パーサではなく「パス末尾のbase nameやパターン断片の包含」で判定。
    誤検出（カバーされてないのに「カバー済み」判定）を避けるため、保守的に判定する。
    """
    norm = path.replace("\\", "/")
    base = norm.rsplit("/", 1)[-1].lower()
    norm_lower = norm.lower()

    for raw in gitignore_lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # `**/foo.json` `*.env` `credentials*.json` 等
        # gitignore のグロブを正規表現に変換（簡易版）
        # 1. ** → .*
        # 2. *  → [^/]*
        # 3. ?  → .
        # 4. .  → \.
        # まずアンカー処理（先頭 / は repository root 固定）
        anchored = line.startswith("/")
        if anchored:
            line = line.lstrip("/")
        # 正規表現変換
        regex = re.escape(line)
        regex = regex.replace(r"\*\*", ".*")
        regex = regex.replace(r"\*", r"[^/]*")
        regex = regex.replace(r"\?", ".")
        # マッチング
        if anchored:
            pattern = re.compile(r"^" + regex + r"(/|$)")
        else:
            # フルパス／basename どちらかにマッチすればカバー
            pattern = re.compile(r"(^|/)" + regex + r"(/|$)")
        if pattern.search(norm_lower) or pattern.search(base):
            return True
    return False


def suggest_gitignore_pattern(path: str) -> str:
    """機密ファイルに対する推奨 gitignore パターンを生成。"""
    norm = path.replace("\\", "/")
    base = norm.rsplit("/", 1)[-1]
    # cache配下なら **/cache/<base name パターン>
    if "/cache/" in norm:
        # 例: cache/ebay_app_token.json → **/cache/*token*.json
        m = re.search(r"(token|credentials|secret|api_key|apikey|access_key|private_key|oauth)", base, re.IGNORECASE)
        if m:
            keyword = m.group(1).lower()
            ext = base.rsplit(".", 1)[-1] if "." in base else "*"
            return f"**/cache/*{keyword}*.{ext}"
    # 通常: **/<basename>
    return f"**/{base}"


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    if not is_sensitive_filename(file_path):
        sys.exit(0)

    # .gitignore 読み込み（プロジェクトルート想定）
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    gitignore_path = Path(project_dir) / ".gitignore" if project_dir else Path(".gitignore")
    gitignore_lines: list[str] = []
    if gitignore_path.exists():
        try:
            gitignore_lines = gitignore_path.read_text(encoding="utf-8").splitlines()
        except Exception:
            gitignore_lines = []

    if is_covered_by_gitignore(file_path, gitignore_lines):
        # 既にカバー済 → 黙って通す
        sys.exit(0)

    # 警告（ブロックしない）
    suggested = suggest_gitignore_pattern(file_path)
    msg = (
        "\n=============================================================\n"
        "⚠️  機密ファイル候補の作成を検知（PreToolUse hook）\n"
        "=============================================================\n"
        f"対象パス: {file_path}\n"
        "判定: ファイル名に token/credentials/secret 等のパターン含む\n"
        "現状: .gitignore で除外されていない可能性あり\n"
        "\n"
        "推奨アクション:\n"
        f"  1. .gitignore に以下を追加:  {suggested}\n"
        "  2. 既に commit されたファイルがあれば git rm --cached も検討\n"
        "  3. 中身が真に機密なら（例: 動的生成のtokenキャッシュ）→ 必ず除外\n"
        "  4. 中身が機密でない（例: ガイド.md / token取得ロジック.py）→ このまま作業継続OK\n"
        "\n"
        "本フックはブロックしません。Claude側で判断のうえ、必要なら .gitignore を先に更新してから\n"
        "再度 Write/Edit してください。最終防衛線として github_backup.py が push 前にも検出します。\n"
        "=============================================================\n"
    )
    sys.stderr.write(msg)
    # exit 0: 警告のみ・ブロックなし（Claudeに判断させる）
    sys.exit(0)


if __name__ == "__main__":
    main()
