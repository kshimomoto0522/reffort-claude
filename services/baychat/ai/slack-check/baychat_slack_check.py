"""
BayChat Slack #baychat-ai導入 監視・自律返信スクリプト
旧 Claude scheduled-task `baychat-slack-hourly-check` の Windows 移管版（2026-04-29）

- 起動: Windowsタスクスケジューラ `BayChatSlackCheck` から30分ごと（社長判断で頻度UP）
- 役割: BayChat関連Slackチャンネル `#baychat-ai導入` (C09KXK26J8G) で
        Claude Code Bot (U0AM647TMNH) 宛のメンションを抽出 → Claude判断で
        ① 技術的な事実確認 → 自律返信＋社長DM通知
        ② 社長判断要 → 社長DMに報告し返信は保留
        ③ 判断迷う → 社長側に倒す（②と同じ）
- チェックポイント先行更新ルール（旧SKILL.mdルール）：
        履歴取得 → 最新ts即保存 → 差分処理（処理失敗で詰まらない）
- 失敗時: 社長個人DM (room_id 426170119) に箱型カードで失敗通知

⚠️ SLACK_BOT_TOKEN は社長が Slack App を作成して発行する必要あり。
   発行手順は ../slack-check/SLACK_BOT_SETUP.md 参照。
"""

import os
import sys
import json
import re
import traceback
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

import anthropic
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / ".env", override=True)

# ── 設定 ──
ANTHROPIC_API_KEY      = os.getenv("ANTHROPIC_API_KEY")
SLACK_BOT_TOKEN        = os.getenv("SLACK_BOT_TOKEN", "")
CW_TOKEN               = os.getenv("CHATWORK_API_TOKEN")
CHANNEL_ID             = os.getenv("SLACK_CHANNEL_ID", "C09KXK26J8G")
BOT_USER_ID            = os.getenv("SLACK_BOT_USER_ID", "U0AM647TMNH")
QUYET_USER_ID          = os.getenv("SLACK_QUYET_USER_ID", "U04HGPBABQU")
ANOTHER_USER_ID        = os.getenv("SLACK_ANOTHER_USER_ID", "U048ZRU4KLG")
ROOM_ID_PRESIDENT      = int(os.getenv("CHATWORK_ROOM_ID_PRESIDENT", "426170119"))
DRY_RUN                = os.getenv("DRY_RUN", "false").lower() == "true"

# 旧来のチェックポイントファイル（既存パスを踏襲）
CHECKPOINT_PATH        = Path("C:/Users/KEISUKE SHIMOMOTO/Desktop/reffort/services/baychat/ai/slack_last_checked.txt")

JST = timezone(timedelta(hours=9))


# ──────────────────────────────────────────────
# Slack Web API ラッパ
# ──────────────────────────────────────────────
def _slack_request(method: str, params: dict | None = None, json_body: dict | None = None) -> dict:
    url = f"https://slack.com/api/{method}"
    if json_body is not None:
        data = json.dumps(json_body).encode()
        headers = {
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
        }
        req = urllib.request.Request(url, data=data, method="POST", headers=headers)
    else:
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, method="GET")
        req.add_header("Authorization", f"Bearer {SLACK_BOT_TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as res:
        body = json.loads(res.read().decode())
    if not body.get("ok"):
        raise RuntimeError(f"Slack API error on {method}: {body.get('error')}")
    return body


def slack_get_history(channel_id: str, limit: int = 30) -> list[dict]:
    res = _slack_request("conversations.history", {"channel": channel_id, "limit": limit})
    return res.get("messages", [])


def slack_get_thread_replies(channel_id: str, thread_ts: str) -> list[dict]:
    res = _slack_request("conversations.replies", {"channel": channel_id, "ts": thread_ts})
    return res.get("messages", [])


def slack_post_reply(channel_id: str, thread_ts: str, text: str) -> dict:
    if DRY_RUN:
        print(f"[DRY_RUN] reply to thread {thread_ts}:\n{text[:200]}...\n")
        return {"ok": True, "ts": "DRY_RUN"}
    return _slack_request("chat.postMessage", json_body={
        "channel": channel_id,
        "thread_ts": thread_ts,
        "text": text,
    })


# ──────────────────────────────────────────────
# Chatwork API（社長DM通知用）
# ──────────────────────────────────────────────
def cw_post_president(body: str) -> dict:
    if DRY_RUN:
        print(f"[DRY_RUN] DM to president:\n{body[:200]}...\n")
        return {"message_id": "DRY_RUN"}
    url = f"https://api.chatwork.com/v2/rooms/{ROOM_ID_PRESIDENT}/messages"
    data = urllib.parse.urlencode({"body": body}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("X-ChatWorkToken", CW_TOKEN)
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.loads(res.read().decode())


# ──────────────────────────────────────────────
# チェックポイント管理（先行更新ルール）
# ──────────────────────────────────────────────
def load_prev_ts() -> str:
    if CHECKPOINT_PATH.exists():
        v = CHECKPOINT_PATH.read_text(encoding="utf-8").strip()
        return v or "0"
    return "0"


def save_checkpoint(ts: str) -> None:
    CHECKPOINT_PATH.write_text(ts, encoding="utf-8")


# ──────────────────────────────────────────────
# 判定ヘルパ
# ──────────────────────────────────────────────
def is_mention_to_self(text: str) -> bool:
    return f"<@{BOT_USER_ID}>" in (text or "")


# ──────────────────────────────────────────────
# Claude 判断
# ──────────────────────────────────────────────
CLASSIFY_AND_REPLY_PROMPT = """あなたは株式会社ReffortのClaude Code（自分のSlack ID: {bot_id}）として、Slackチャンネル #baychat-ai導入 でCowatech（ベトナム開発会社）のクエットさん（{quyet_id}）と協業しています。

このスレッドの最新メッセージへの対応を判断してください。

【スレッド履歴（古い順）】
---
{thread_history}
---

【最新の自分宛メンションメッセージ】（自分=Claude Code 宛て）
---
{latest_msg}
---

以下のJSONフォーマットで返してください。

{{
  "category": "auto_reply" | "president_check" | "ignore",
  "reply": "Slackスレッドへの返信本文（categoryがauto_replyのときのみ）",
  "president_summary": "社長への報告サマリー（auto_reply/president_check 共通で必須・箱型カード本文）"
}}

判定ルール：
- "auto_reply" : 技術的回答・事実確認の返答・お礼・了解等、社長判断不要なもの
- "president_check" : 仕様変更・契約・予算・社外発信等、社長判断が必要なもの。返信は保留して社長DMにのみ報告
- "ignore" : 自分宛でない/雑談のみ/既に他者が対応済みなど（返信不要・社長報告も不要）

返信本文(reply)の制約（auto_replyの場合）：
- 冒頭に Cowatech メンバーへのメンションを必ず付ける: <@{quyet_id}> <@{another_id}>
- 日本語で丁寧に
- 技術的な内容は簡潔・正確に
- 質問への回答が確定していない場合は「確認します」と書き、決して推測で答えない

president_summary の構成：
- 1行目に状況の要約
- 続けて「やったこと」「これから必要な判断」を箇条書き
- 最後に Slack スレッドリンクの場所（実際のリンク生成は呼び出し側で付与）

JSON以外の説明文・前置き・コードブロック記号は付けず、純粋なJSONのみを返してください。
"""


def claude_judge(thread_history: str, latest_msg: str) -> dict:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = CLASSIFY_AND_REPLY_PROMPT.format(
        bot_id=BOT_USER_ID,
        quyet_id=QUYET_USER_ID,
        another_id=ANOTHER_USER_ID,
        thread_history=thread_history[:6000],
        latest_msg=latest_msg[:3000],
    )
    res = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = res.content[0].text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE)
    return json.loads(text)


# ──────────────────────────────────────────────
# 失敗通知
# ──────────────────────────────────────────────
def notify_failure(step: str, err: BaseException) -> None:
    try:
        if not CW_TOKEN:
            return
        now = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
        body = (
            f"[info][title]⚠️ baychat-slack-check 失敗通知｜{now}[/title]"
            f"■ 失敗ステップ: {step}\n"
            f"■ 例外: {type(err).__name__}\n"
            f"■ 内容: {str(err)[:600]}\n"
            f"■ 起動経路: Windowsタスクスケジューラ BayChatSlackCheck\n"
            f"■ チェックポイント: 先行更新済み（次回は新地点から再開）\n"
            f"対応: 社長確認をお願いします。[/info]"
        )
        cw_post_president(body)
    except Exception:
        traceback.print_exc()


# ──────────────────────────────────────────────
# メインフロー
# ──────────────────────────────────────────────
def main() -> int:
    print(f"=== baychat-slack-check 開始 (DRY_RUN={DRY_RUN}) ===")

    if not SLACK_BOT_TOKEN:
        print("⚠️ SLACK_BOT_TOKEN が未設定。.env を確認してください。")
        notify_failure("init: SLACK_BOT_TOKEN missing", RuntimeError("SLACK_BOT_TOKEN missing"))
        return 2

    step = "init"
    try:
        step = "load_prev_ts"
        prev_ts = load_prev_ts()
        print(f"  prev_ts: {prev_ts}")

        step = "slack_get_history"
        messages = slack_get_history(CHANNEL_ID, limit=30)
        print(f"  retrieved {len(messages)} top-level messages")

        # 最大tsを算出（top-level + thread latest_reply）
        step = "compute_latest_ts"
        latest_ts_candidates = [prev_ts]
        for m in messages:
            latest_ts_candidates.append(m.get("ts", "0"))
            if m.get("latest_reply"):
                latest_ts_candidates.append(m.get("latest_reply"))
        latest_checkpoint_ts = max(latest_ts_candidates, key=lambda x: float(x or 0))
        print(f"  latest_checkpoint_ts: {latest_checkpoint_ts}")

        # ★チェックポイント先行更新★
        step = "save_checkpoint_first"
        save_checkpoint(latest_checkpoint_ts)
        print(f"  ✅ checkpoint saved BEFORE processing (重要)")

        # 差分スキャン
        step = "scan_mentions"
        prev_f = float(prev_ts or 0)
        mentions: list[tuple[str, dict]] = []  # (thread_ts, mention_msg)
        for m in messages:
            top_ts = m.get("ts", "0")
            top_user = m.get("user")
            top_text = m.get("text", "")
            # トップレベル新着 + メンション
            if float(top_ts) > prev_f and top_user != BOT_USER_ID and is_mention_to_self(top_text):
                mentions.append((top_ts, m))
            # スレッド内
            if m.get("reply_count", 0) > 0 and m.get("latest_reply") and float(m["latest_reply"]) > prev_f:
                try:
                    replies = slack_get_thread_replies(CHANNEL_ID, m["ts"])
                except Exception as te:
                    print(f"    !! thread fetch failed for {m['ts']}: {te}")
                    continue
                for r in replies:
                    r_ts = r.get("ts", "0")
                    r_user = r.get("user")
                    r_text = r.get("text", "")
                    if float(r_ts) > prev_f and r_user != BOT_USER_ID and is_mention_to_self(r_text):
                        mentions.append((m["ts"], r))

        print(f"  → {len(mentions)} mention(s) to me")

        if not mentions:
            print("=== 完了 (新着なし) ===")
            return 0

        step = "process_mentions"
        replied_count = 0
        president_reported_count = 0

        for thread_ts, mention_msg in mentions:
            mid_ts = mention_msg.get("ts")
            mtext = mention_msg.get("text", "")
            print(f"  → mention at {mid_ts}: {mtext[:80]}...")

            # スレッド全履歴を組み立てる
            try:
                thread_msgs = slack_get_thread_replies(CHANNEL_ID, thread_ts)
            except Exception as te:
                print(f"    !! thread fetch failed: {te}")
                continue
            history_lines = []
            for tm in thread_msgs:
                u = tm.get("user", "?")
                t = tm.get("text", "")
                history_lines.append(f"<@{u}>: {t}")
            history_text = "\n".join(history_lines)

            try:
                judge = claude_judge(history_text, mtext)
            except Exception as je:
                print(f"    !! Claude判断失敗: {je}")
                notify_failure(f"claude_judge (ts {mid_ts})", je)
                continue

            category = judge.get("category", "ignore")
            reply = (judge.get("reply") or "").strip()
            president_summary = (judge.get("president_summary") or "").strip()

            # スレッドリンク生成（Slackパーマリンク形式は手元で組み立て）
            permalink = f"https://app.slack.com/client/T0483GR42P8/{CHANNEL_ID}/thread/{CHANNEL_ID}-{thread_ts}"

            if category == "ignore":
                print(f"    → ignore")
                continue

            if category == "auto_reply" and reply:
                slack_post_reply(CHANNEL_ID, thread_ts, reply)
                replied_count += 1
                print(f"    → auto_reply posted")

            if president_summary:
                now = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
                category_label = "自律返信済み" if category == "auto_reply" else "社長判断要"
                cw_body = (
                    f"[info][title]【BayChat Slack】{category_label}｜{now}[/title]"
                    f"{president_summary}\n"
                    f"\nスレッド: {permalink}[/info]"
                )
                cw_post_president(cw_body)
                president_reported_count += 1
                print(f"    → president DM posted ({category_label})")

        print(f"=== 完了: 自律返信 {replied_count} 件 / 社長DM {president_reported_count} 件 ===")
        return 0

    except BaseException as e:
        traceback.print_exc()
        notify_failure(step, e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
