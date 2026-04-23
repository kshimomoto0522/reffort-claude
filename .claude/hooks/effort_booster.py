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
COMPLEX_KEYWORDS = [
    # 設計・構造系
    "設計", "アーキテクチャ", "構造", "リファクタ", "リファクタリング",
    # 根本原因系
    "根本", "原因", "なぜ", "ボトルネック", "本質",
    # 戦略・判断系
    "戦略", "判断", "意思決定", "選択肢", "方針", "ロードマップ",
    # デバッグ系
    "バグ", "デバッグ", "動かない", "エラー", "failing",
    # 最適化系
    "最適化", "チューニング", "効率化", "改善案",
    # 比較系
    "比較", "メリットデメリット", "どちらが良い", "ベスト", "最善",
    # 経営系
    "経営", "事業", "戦略的",
    # 分析系
    "分析", "精査", "検証", "洗い出し",
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
