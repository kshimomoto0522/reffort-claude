"""
Chatwork【AI】eBay運営グループ メンション自動応答スクリプト
旧 Claude scheduled-task `chatwork-ai-reply` の Windows 移管版（2026-04-29）

- 起動: Windowsタスクスケジューラ `ChatworkAIReply` から毎日10:00
- 既知の制約: 旧版は平日10〜20時の10分ごとだったが、社長判断で1日1回チェックに変更
- 役割: 【AI】eBay運営グループ (room_id 426169912) で REFFORT AI (account_id 11193405) 宛の
        メンション/返信を抽出し、Claude判断で自律返信。改善要望は report_requests.json へ蓄積
- 失敗時: 社長個人DM (room_id 426170119) に箱型カードで失敗通知
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

# ── 文字化け対策 ──
sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / ".env", override=True)

# ── 設定 ──
ANTHROPIC_API_KEY      = os.getenv("ANTHROPIC_API_KEY")
CW_TOKEN               = os.getenv("CHATWORK_API_TOKEN")
ROOM_ID_AI_EBAY        = int(os.getenv("CHATWORK_ROOM_ID_AI_EBAY", "426169912"))
ROOM_ID_PRESIDENT      = int(os.getenv("CHATWORK_ROOM_ID_PRESIDENT", "426170119"))
SELF_ACCOUNT_ID        = int(os.getenv("CHATWORK_SELF_ACCOUNT_ID", "11193405"))
DRY_RUN                = os.getenv("DRY_RUN", "false").lower() == "true"

REPORT_REQUESTS_PATH   = Path("C:/Users/KEISUKE SHIMOMOTO/Desktop/reffort/commerce/ebay/analytics/report_requests.json")
STATE_PATH             = SCRIPT_DIR / "last_processed_id.txt"

JST = timezone(timedelta(hours=9))


# ──────────────────────────────────────────────
# Chatwork API ラッパ
# ──────────────────────────────────────────────
def _cw_request(method: str, path: str, body: dict | None = None) -> dict | list:
    url = f"https://api.chatwork.com/v2/{path.lstrip('/')}"
    data = urllib.parse.urlencode(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-ChatWorkToken", CW_TOKEN)
    with urllib.request.urlopen(req, timeout=30) as res:
        raw = res.read().decode()
        return json.loads(raw) if raw else {}


def cw_list_messages(room_id: int) -> list[dict]:
    """ルームのメッセージ最大100件を取得（force=1で未読でなくても取得）。"""
    return _cw_request("GET", f"rooms/{room_id}/messages?force=1") or []


def cw_post_message(room_id: int, body: str) -> dict:
    """ルームへメッセージ投稿。DRY_RUN時はスキップ。"""
    if DRY_RUN:
        print(f"[DRY_RUN] post to room {room_id}:\n{body[:200]}...\n")
        return {"message_id": "DRY_RUN"}
    return _cw_request("POST", f"rooms/{room_id}/messages", {"body": body})


# ──────────────────────────────────────────────
# 状態管理（最後に処理した message_id）
# ──────────────────────────────────────────────
def load_last_id() -> str | None:
    if STATE_PATH.exists():
        v = STATE_PATH.read_text(encoding="utf-8").strip()
        return v or None
    return None


def save_last_id(message_id: str) -> None:
    STATE_PATH.write_text(message_id, encoding="utf-8")


# ──────────────────────────────────────────────
# メンション抽出
# ──────────────────────────────────────────────
MENTION_PATTERNS = [
    re.compile(rf"\[To:{SELF_ACCOUNT_ID}\]"),
    re.compile(rf"\[rp aid={SELF_ACCOUNT_ID} to=\d+-\d+\]"),
    re.compile(rf"\[piconname:{SELF_ACCOUNT_ID}\]"),
]


def is_mention_to_self(body: str) -> bool:
    return any(p.search(body) for p in MENTION_PATTERNS)


def is_self_message(account_id: int) -> bool:
    return account_id == SELF_ACCOUNT_ID


# ──────────────────────────────────────────────
# Claude 判断
# ──────────────────────────────────────────────
CLASSIFY_AND_REPLY_PROMPT = """あなたは株式会社リフォート（英文名: Reffort, Ltd.・eBay輸出事業）の +REFFORT AI+ として、Chatwork【AI】eBay運営グループでスタッフからの質問・要望に対応するアシスタントです。

スタッフからのメッセージ本文：
---
{message}
---

このメッセージへの対応を以下のJSONフォーマットで返してください。

{{
  "category": "request" | "question" | "ignore",
  "reply": "返信本文（categoryがignoreなら空文字）",
  "request_summary": "改善要望の要約（categoryがrequestのときのみ・それ以外は空文字）"
}}

判定ルール：
- "request" : 週次レポートの仕様変更・項目追加・列追加・データ抽出ロジック等への改善要望
- "question" : eBay運営/レポートの見方/数字の意味/ツール操作などの一般質問
- "ignore" : 雑談・お礼のみ・自分宛でない・既に他のスタッフが対応済みなど（返信不要）

返信本文の制約：
- categoryが "request" のとき：「要望を受け付けました。検討し、対応が可能か確認いたします。」というニュアンスにすること。**「反映します」「次回から対応します」「次回月曜のレポートから反映」とは絶対に言わない**（社長判断が必要なため）
- categoryが "question" のとき：丁寧な日本語で回答。Reffortの事業（eBay輸出/BayChat/BayPack/Campers）の文脈を踏まえる
- 冒頭に [rp aid=送信者ID to=ROOMID-MESSAGEID]さん の形式で返信引用は付けず、シンプルに「{sender_name}さん、」で始める
- 末尾は「引き続きお気づきの点があればこちらにお知らせください！」等の励まし
- メッセージは [info] タグで囲まない（プレーンテキスト）

JSON以外の説明文・前置き・コードブロック記号は一切付けず、純粋なJSONのみを返してください。
"""


def claude_judge(message_body: str, sender_name: str) -> dict:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = CLASSIFY_AND_REPLY_PROMPT.format(
        message=message_body,
        sender_name=sender_name,
    )
    res = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    text = res.content[0].text.strip()
    # 余計なコードブロック対策
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE)
    return json.loads(text)


# ──────────────────────────────────────────────
# 改善要望ストア
# ──────────────────────────────────────────────
def append_request_record(sender_name: str, summary: str) -> None:
    REPORT_REQUESTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if REPORT_REQUESTS_PATH.exists():
        data = json.loads(REPORT_REQUESTS_PATH.read_text(encoding="utf-8") or "[]")
    else:
        data = []
    data.append({
        "date": datetime.now(JST).strftime("%Y-%m-%d"),
        "from": sender_name,
        "request": summary,
        "status": "pending",
        "result": "",
    })
    REPORT_REQUESTS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ──────────────────────────────────────────────
# 失敗通知
# ──────────────────────────────────────────────
def notify_failure(step: str, err: BaseException) -> None:
    try:
        if not CW_TOKEN:
            return
        now = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
        body = (
            f"[info][title]⚠️ chatwork-ai-reply 失敗通知｜{now}[/title]"
            f"■ 失敗ステップ: {step}\n"
            f"■ 例外: {type(err).__name__}\n"
            f"■ 内容: {str(err)[:600]}\n"
            f"■ 起動経路: Windowsタスクスケジューラ ChatworkAIReply\n"
            f"対応: 社長確認をお願いします。[/info]"
        )
        cw_post_message(ROOM_ID_PRESIDENT, body)
    except Exception:
        traceback.print_exc()


# ──────────────────────────────────────────────
# メインフロー
# ──────────────────────────────────────────────
def main() -> int:
    print(f"=== chatwork-ai-reply 開始 (DRY_RUN={DRY_RUN}) ===")

    step = "init"
    try:
        step = "load_last_id"
        last_id = load_last_id()
        print(f"  last_processed_id: {last_id}")

        step = "list_messages"
        messages = cw_list_messages(ROOM_ID_AI_EBAY)
        print(f"  retrieved {len(messages)} messages")

        # ChatworkAPIの並びは古い→新しい順。最後が最新。
        # 初回起動 (last_id=None) のときは「処理せずに最新message_idだけ記録」して空打ち防止
        if last_id is None:
            if messages:
                save_last_id(messages[-1]["message_id"])
                print(f"  initial run: bookmarked latest message_id={messages[-1]['message_id']} (no processing)")
            return 0

        step = "filter_new_messages"
        new_messages = []
        seen_last = False
        for m in messages:
            if seen_last:
                new_messages.append(m)
            elif m["message_id"] == last_id:
                seen_last = True
        # last_id がリスト内に無い（古すぎて押し出された等）→ 全件処理は危険なので最新のみブックマーク
        if not seen_last:
            print(f"  ⚠️ last_id={last_id} not found in current 100 messages window; rebookmarking only")
            if messages:
                save_last_id(messages[-1]["message_id"])
            return 0

        print(f"  new messages since last run: {len(new_messages)}")

        step = "process_each"
        # 最新のmessage_idを処理開始前に先行保存（チェックポイント先行更新）
        if messages:
            save_last_id(messages[-1]["message_id"])

        replied_count = 0
        request_count = 0
        for m in new_messages:
            account_id = m["account"]["account_id"]
            sender_name = m["account"]["name"]
            body = m["body"]
            mid = m["message_id"]

            if is_self_message(account_id):
                continue
            if not is_mention_to_self(body):
                continue

            # メンション部分を取り除いた本文をClaudeに渡す
            clean_body = re.sub(r"\[(?:To|rp|piconname)[^\]]+\]", "", body).strip()
            if not clean_body:
                continue

            print(f"  → mention from {sender_name} (msg {mid}): {clean_body[:80]}...")

            try:
                judge = claude_judge(clean_body, sender_name)
            except Exception as je:
                print(f"    !! Claude判断失敗: {je}")
                notify_failure(f"claude_judge (msg {mid})", je)
                continue

            category = judge.get("category", "ignore")
            reply = judge.get("reply", "").strip()
            request_summary = judge.get("request_summary", "").strip()

            if category == "ignore" or not reply:
                print(f"    → ignore")
                continue

            if category == "request" and request_summary:
                append_request_record(sender_name, request_summary)
                request_count += 1
                print(f"    → request recorded: {request_summary[:50]}")

            # 返信投稿
            reply_with_quote = (
                f"[AI返信]\n"
                f"[rp aid={account_id} to={ROOM_ID_AI_EBAY}-{mid}]\n"
                f"{reply}"
            )
            cw_post_message(ROOM_ID_AI_EBAY, reply_with_quote)
            replied_count += 1
            print(f"    → posted ({category})")

        print(f"=== 完了: 返信 {replied_count} 件 / 改善要望 {request_count} 件 ===")
        return 0

    except BaseException as e:
        traceback.print_exc()
        notify_failure(step, e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
