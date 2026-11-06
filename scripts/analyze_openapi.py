import json, os, collections

d = r"C:\Users\hiron\Documents\Default Project\living-brain-re\raw"
spec = json.load(open(os.path.join(d, "openapi.json"), encoding="utf-8"))

paths = spec["paths"]
rows = []
methods = collections.Counter()
tags = collections.Counter()
for p, item in paths.items():
    for m, op in item.items():
        if m not in ("get", "post", "put", "patch", "delete", "head", "options"):
            continue
        methods[m] += 1
        for t in op.get("tags", ["(none)"]):
            tags[t] += 1
        params = [x.get("name") for x in op.get("parameters", [])]
        rows.append((m.upper(), p, op.get("operationId"), ",".join(op.get("tags", [])), ",".join(params)))

print("paths:", len(paths), "operations:", len(rows))
print("methods:", dict(methods))
print("tags:", dict(tags))
print()
for r in sorted(rows, key=lambda x: (x[3], x[1])):
    print(" | ".join(str(x) for x in r))

schemas = spec.get("components", {}).get("schemas", {})
print("\nschemas:", len(schemas))
print("enum-bearing schemas:")
for name, s in schemas.items():
    props = s.get("properties") or {}
    enums = {k: v.get("enum") for k, v in props.items() if isinstance(v, dict) and "enum" in v}
    if enums:
        print(" ", name, "->", enums)
