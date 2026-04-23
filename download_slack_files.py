import urllib.request, os, io, sys
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# .envファイルから機密情報を読み込む
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'commerce', 'ebay', 'analytics', '.env'))

TOKEN = os.getenv('SLACK_BOT_TOKEN')
DEST = r"C:\Users\KEISUKE SHIMOMOTO\Desktop\reffort\services\baychat\ai"

files = {
    "gpt_request_7.json":  "https://files.slack.com/files-pri/T0483GR42P8-F0AMHG2691C/download/gpt_request_7.json",
    "gpt_request_8.json":  "https://files.slack.com/files-pri/T0483GR42P8-F0ANDRRLXMW/download/gpt_request_8.json",
    "gpt_request_9.json":  "https://files.slack.com/files-pri/T0483GR42P8-F0AMYF0G3SM/download/gpt_request_9.json",
    "gpt_request_10.json": "https://files.slack.com/files-pri/T0483GR42P8-F0AM44JFF0F/download/gpt_request_10.json",
}

for name, url in files.items():
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
    data = urllib.request.urlopen(req).read()
    path = os.path.join(DEST, name)
    with open(path, "wb") as f:
        f.write(data)
    print(f"✓ {name} ({len(data)} bytes)")
