# -*- coding: utf-8 -*-
"""
Claude Code Effort Auto-Booster Hook
====================================
目的：
  - ベースラインはHigh（settings.local.jsonで設定済み）
  - 複雑なタスクと判定した場合、そのターンだけ「ultrathink」を注入してMax相当に引き上げる

判定ロジック：
  1. オプトアウト語が入っていればブーストしない（「軽く」「さっと」など）
  2. 明示オプトイン語があれば即ブースト（「じっくり」「!max」「ultrathink」など）
  3. 複雑タスク判定キーワードが2つ以上含まれれば自動ブースト

トリガーされた場合、UserPromptSubmitフックの標準出力に "ultrathink" を出力することで、
Claudeのプロンプトに追加コンテキストとして注入される（= 最大思考予算が割り当てられる）。
"""
import sys
import io
import json
from datetime import datetime
from pathlib import Path

# Windows環境でも日本語プロンプトを正しく読むためUTF-8固定
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ------------------------------------------------------------
# キーワード定義
# ------------------------------------------------------------

# 明示オプトアウト（社長はこれ系の言葉は使わないため空で運用。必要になれば追加）
OPT_OUT_KEYWORDS: list[str] = []

# 明示オプトイン（これらが含まれる時は必ずブースト）
# 社長の実発言パターンに合わせた品質強調語を中心に
OPT_IN_KEYWORDS = [
    "!max", "ultrathink",
    # 強調語（社長が頻繁に使う）
    "しっかり", "ちゃんと", "もっと",
    # 深度指定語
    "じっくり", "深く考え", "徹底的",
    # ベスト系
    "ベストを考え", "ベストから", "ベストで", "最善",
]

# 複雑タスク判定キーワード（2個以上マッチで自動ブースト）
# 2026-04-23厳選版：
#   旧版は「分析・検証・判断・バグ・エラー・方針・比較」など日常語を含み、
#   社長が普通に話すだけで誤爆ブースト（トークン倍増・レイテンシ増）が頻発していた。
#   真に深思考が必要な「専門語・構造語」のみに絞る。
#   社長が明示的にじっくり考えて欲しい時は OPT_IN_KEYWORDS（しっかり/ちゃんと/ultrathink等）で起動。
COMPLEX_KEYWORDS = [
    # 設計・構造系（真のアーキテクチャ判断）
    "アーキテクチャ", "リファクタリング", "データフロー", "依存関係",
    # 根本原因系（深掘りが必要な場面）
    "根本原因", "本質的", "ボトルネック", "トレードオフ",
    # 戦略・経営系（長期視点）
    "戦略的", "中長期", "経営判断", "全体最適",
    # 複雑実装系
    "マイグレーション", "移行計画", "段階的実装", "複雑度",
]

LOG_PATH = Path(__file__).parent / "effort_booster.log"


def should_boost(prompt: str) -> tuple[bool, str]:
    """
    ブーストすべきかを判定し、(判定結果, 理由) を返す
    """
    p_lower = prompt.lower()

    # オプトアウトが最優先
    for kw in OPT_OUT_KEYWORDS:
        if kw.lower() in p_lower:
            return False, f"opt-out: {kw}"

    # オプトイン
    for kw in OPT_IN_KEYWORDS:
        if kw.lower() in p_lower:
            return True, f"opt-in: {kw}"

    # 複雑タスクキーワード2個以上で自動ブースト
    hits = [kw for kw in COMPLEX_KEYWORDS if kw in prompt]
    if len(hits) >= 2:
        return True, f"auto: {', '.join(hits[:5])}"

    return False, f"skip (hits={len(hits)})"


def log(message: str) -> None:
    """簡易ログ（デバッグ用・失敗しても無視）"""
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} {message}\n")
    except Exception:
        pass


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        log(f"parse error: {e}")
        sys.exit(0)

    prompt = payload.get("prompt", "") or ""
    boost, reason = should_boost(prompt)
    log(f"boost={boost} reason={reason} len={len(prompt)}")

    if boost:
        # フックの標準出力はプロンプトに追加コンテキストとして結合される
        # "ultrathink" キーワードを注入することでMax相当の思考予算を割り当てる
        print("ultrathink")

    sys.exit(0)


if __name__ == "__main__":
    main()
