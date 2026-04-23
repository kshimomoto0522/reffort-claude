import urllib.request
import json
import os
from dotenv import load_dotenv

# .envファイルから機密情報を読み込む
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'commerce', 'ebay', 'analytics', '.env'))

TOKEN = os.getenv('SLACK_BOT_TOKEN')
CHANNEL = "C09KXK26J8G"
THREAD_TS = "1773665481.840449"  # "Claude Codeを活用した開発" スレッド

def api(method, data):
    req = urllib.request.Request(
        f"https://slack.com/api/{method}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())

result = api("chat.postMessage", {
    "channel": CHANNEL,
    "thread_ts": THREAD_TS,
    "text": "<@U047VJD3895> <@U04HGPBABQU> <@U048ZRU4KLG>\n\nはじめまして。Claude Codeです。\n今後、BayChatのAI Reply開発を進めるにあたり、プロンプトの作成・改善はこちらで担当し、必要に応じてコードや仕様の確認をこのチャンネルでお願いすることがあります。\nどうぞよろしくお願いします。"
})

print("OK!" if result["ok"] else f"Error: {result.get('error')}")
