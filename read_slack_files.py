import json, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = r"C:\Users\KEISUKE SHIMOMOTO\.claude\projects\C--Users-KEISUKE-SHIMOMOTO-Desktop-reffort\f79b493f-939b-4a50-8f0b-4e107052eb00\tool-results\toolu_01DZY8hvrNmDBseW9pC9ejKP.json"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

msgs = json.loads(data[0]["text"])["messages"]

print(f"総メッセージ数: {len(msgs)}")
print("=" * 60)

# ファイル添付があるメッセージを探す
for m in msgs:
    files = m.get("files", [])
    if files:
        print(f"\n[{m['ts']}] ファイル添付:")
        for fi in files:
            print(f"  - {fi.get('name', '?')} | id: {fi.get('id')} | url: {fi.get('url_private_download', fi.get('url_private', ''))}")
