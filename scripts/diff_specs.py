import json, os

base = r"C:\Users\hiron\Documents\Default Project\living-brain-re"
pub = json.load(open(os.path.join(base, "raw", "openapi.json"), encoding="utf-8"))
cli = json.load(open(os.path.join(base, "artifacts", "cli", "cli", "livingbrain", "openapi0.json"), encoding="utf-8"))


def ops(spec):
    out = {}
    for p, item in spec["paths"].items():
        for m, op in item.items():
            if m in ("get", "post", "put", "patch", "delete"):
                out[op.get("operationId")] = (m.upper(), p)
    return out


a, b = ops(pub), ops(cli)
print("published ops:", len(a), "cli-embedded ops:", len(b))
print("only in published:", sorted(set(a) - set(b)))
print("only in cli:", sorted(set(b) - set(a)))
diff = [k for k in set(a) & set(b) if a[k] != b[k]]
print("changed path/method:", [(k, a[k], b[k]) for k in diff])

sa = pub.get("components", {}).get("schemas", {})
sb = cli.get("components", {}).get("schemas", {})
print("schemas published:", len(sa), "cli:", len(sb))
print("schema only published:", sorted(set(sa) - set(sb))[:20])
print("schema only cli:", sorted(set(sb) - set(sa))[:20])

changed = []
for k in set(sa) & set(sb):
    if json.dumps(sa[k], sort_keys=True) != json.dumps(sb[k], sort_keys=True):
        changed.append(k)
print("schemas differing:", len(changed))
print(sorted(changed)[:40])
print("published servers:", pub.get("servers"), "cli servers:", cli.get("servers"))
