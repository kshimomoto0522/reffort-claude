"""
X（Twitter）情報収集・要約 → Chatwork自動報告スクリプト
毎日9:40にスケジュールタスクから実行される
"""

import os
import sys
import tweepy
import anthropic
import urllib.request
import urllib.parse
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Windows環境での文字化け対策
sys.stdout.reconfigure(encoding="utf-8")

# .envファイルを読み込む（絶対パスで確実に読み込む）
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(_env_path, override=True)

# ── 設定 ──────────────────────────────────────
X_CONSUMER_KEY        = os.getenv("X_CONSUMER_KEY")
X_CONSUMER_SECRET     = os.getenv("X_CONSUMER_SECRET")
X_ACCESS_TOKEN        = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")
X_BEARER_TOKEN        = os.getenv("X_BEARER_TOKEN")
ANTHROPIC_API_KEY     = os.getenv("ANTHROPIC_API_KEY")
CW_TOKEN              = os.getenv("CHATWORK_API_TOKEN")
CW_ROOM_ID            = os.getenv("CHATWORK_ROOM_ID")

# 取得する投稿数（1回あたり最大100件）
MAX_RESULTS = 50

# バズ判定のしきい値（いいね数）
BUZZ_THRESHOLD = 10


def fetch_home_timeline():
    """フォロー中アカウントの最新投稿を取得する"""
    # OAuth 1.0a クライアントを作成
    client = tweepy.Client(
        bearer_token=X_BEARER_TOKEN,
        consumer_key=X_CONSUMER_KEY,
        consumer_secret=X_CONSUMER_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True
    )

    # 自分のユーザーIDを取得
    me = client.get_me()
    user_id = me.data.id

    # 日本時間で昨日の範囲を指定
    jst = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst)
    start_of_today = now_jst.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_yesterday = start_of_today - timedelta(days=1)

    # ホームタイムラインを取得
    tweets = client.get_home_timeline(
        max_results=MAX_RESULTS,
        start_time=start_of_yesterday.astimezone(timezone.utc),
        end_time=start_of_today.astimezone(timezone.utc),
        tweet_fields=["created_at", "public_metrics", "author_id", "text"],
        user_fields=["name", "username"],
        expansions=["author_id"]
    )

    if not tweets.data:
        return []

    # ユーザー情報をマッピング（author_id → name/username）
    users = {}
    if tweets.includes and "users" in tweets.includes:
        for user in tweets.includes["users"]:
            users[user.id] = {"name": user.name, "username": user.username}

    # 投稿リストを整形
    results = []
    for tweet in tweets.data:
        metrics = tweet.public_metrics or {}
        like_count = metrics.get("like_count", 0)
        rt_count   = metrics.get("retweet_count", 0)
        author     = users.get(tweet.author_id, {})

        results.append({
            "text":     tweet.text,
            "author":   author.get("name", "不明"),
            "username": author.get("username", ""),
            "likes":    like_count,
            "retweets": rt_count,
            "url":      f"https://x.com/{author.get('username', '')}/status/{tweet.id}"
        })

    # いいね数の多い順に並べる
    results.sort(key=lambda x: x["likes"], reverse=True)
    return results


def summarize_with_claude(tweets):
    """Claudeで投稿を要約・重要度判定する"""
    if not tweets:
        return "昨日のフォロー中アカウントに投稿はありませんでした。"

    # バズっている投稿を優先（しきい値以上 or 上位10件）
    buzz_posts = [t for t in tweets if t["likes"] >= BUZZ_THRESHOLD]
    top_posts  = tweets[:10]  # 最低でも上位10件は含める
    # 重複を除いてマージ
    seen = set()
    combined = []
    for t in buzz_posts + top_posts:
        if t["url"] not in seen:
            seen.add(t["url"])
            combined.append(t)

    # Claudeに渡すテキストを構築
    posts_text = ""
    for i, t in enumerate(combined, 1):
        posts_text += (
            f"\n【{i}】@{t['username']}（{t['author']}）"
            f" ❤️{t['likes']} 🔁{t['retweets']}\n"
            f"{t['text']}\n"
            f"URL: {t['url']}\n"
        )

    prompt = f"""
あなたはeBayセラー向けSaaSを運営する経営者の情報アシスタントです。
以下はX（Twitter）でフォロー中のアカウントの昨日の投稿です。

経営者のプロフィール：
- eBay輸出事業とSaaS（BayChat・BayPack）を運営
- Claude Code・AI活用・事業自動化に強い関心あり
- SNSやAI系の最新情報を事業に活かしたい

---
{posts_text}
---

以下の形式で日本語でまとめてください：

## 🔥 今日のハイライト（3件まで）
最も重要・バズっている投稿を選び、なぜ注目すべきかを1〜2行で解説。

## 📌 注目トピック（カテゴリ別）
投稿をカテゴリ（Claude/AI全般/eBay・EC/ビジネス/その他）に分けて要点を箇条書き。

## 💡 事業への活用ヒント
これらの情報をReffortの事業（eBay・BayChat・BayPack）に活かせるアイデアを1〜3個提案。

## ❓ 深掘りしたい？
社長がもし興味を持ったら一緒に調べたいトピックを1〜2個提示。
"""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def send_to_chatwork(message_body):
    """Chatworkの個人DM（下元 敬介）にメッセージを送信する"""
    jst = timezone(timedelta(hours=9))
    today = datetime.now(jst).strftime("%Y年%m月%d日")

    full_message = f"""[info][title]📱 X情報ダイジェスト｜{today}[/title]{message_body}[/info]"""

    data = urllib.parse.urlencode({"body": full_message}).encode()
    req  = urllib.request.Request(
        f"https://api.chatwork.com/v2/rooms/{CW_ROOM_ID}/messages",
        data=data,
        method="POST"
    )
    req.add_header("X-ChatWorkToken", CW_TOKEN)

    with urllib.request.urlopen(req) as res:
        result = json.loads(res.read().decode())
        print(f"✅ Chatwork送信完了 message_id: {result.get('message_id')}")


def main():
    print("=== X情報ダイジェスト 開始 ===")

    print("📥 Xから投稿を取得中...")
    tweets = fetch_home_timeline()
    print(f"  → {len(tweets)}件取得")

    print("🤖 Claudeで要約中...")
    summary = summarize_with_claude(tweets)

    print("📨 Chatworkに送信中...")
    send_to_chatwork(summary)

    print("=== 完了 ===")


if __name__ == "__main__":
    main()
