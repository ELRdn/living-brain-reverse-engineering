import json, collections, os

d = r"C:\Users\hiron\Documents\Default Project\living-brain-re\raw"
data = json.load(open(os.path.join(d, "locomo10.json"), encoding="utf-8"))
print("conversations:", len(data))
cats = collections.Counter()
total = 0
for sample in data:
    for qa in sample.get("qa", []):
        total += 1
        cats[qa.get("category")] += 1
print("total QA:", total)
for k, v in sorted(cats.items(), key=lambda x: str(x[0])):
    print("  category", k, ":", v)
print("excluding adversarial (5):", total - cats.get(5, 0))
print("excluding 5 and 2:", total - cats.get(5, 0) - cats.get(2, 0))

# token size estimate of conversations
sizes = []
for sample in data:
    n = 0
    conv = sample["conversation"]
    for k, v in conv.items():
        if isinstance(v, list):
            for turn in v:
                n += len(str(turn.get("text", "")))
    sizes.append(n)
print("chars per conversation:", sizes)
