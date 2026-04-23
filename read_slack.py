import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = r"C:\Users\KEISUKE SHIMOMOTO\.claude\projects\C--Users-KEISUKE-SHIMOMOTO-Desktop-reffort\f79b493f-939b-4a50-8f0b-4e107052eb00\tool-results\toolu_01QLrCDa9YrHDncMsLvzF6wQ.json"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

msgs = json.loads(data[0]["text"])["messages"]

print(f"総メッセージ数: {len(msgs)}")
print("=" * 60)
# 最新10件を表示
for m in msgs[-10:]:
    user = m.get("user", m.get("bot_id", "?"))
    text = m.get("text", "")[:400]
    ts = m.get("ts", "")
    print(f"[{ts}] {user}:\n{text}\n")
