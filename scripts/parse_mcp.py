import json, os

d = r"C:\Users\hiron\Documents\Default Project\living-brain-re\raw"
raw = open(os.path.join(d, "mcp-tools-raw.txt"), encoding="utf-8-sig").read()
data = [l[6:] for l in raw.splitlines() if l.startswith("data: ")]
obj = json.loads(data[0])
tools = obj["result"]["tools"]
print("tool count:", len(tools))
json.dump(obj, open(os.path.join(d, "mcp-tools.json"), "w", encoding="utf-8"), indent=1)
for t in tools:
    print(t["name"], "|", (t.get("description") or "")[:90].replace("\n", " "))
