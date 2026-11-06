import json, os

base = r"C:\Users\hiron\Documents\Default Project\living-brain-re"
pub = json.load(open(os.path.join(base, "raw", "openapi.json"), encoding="utf-8"))
cli = json.load(open(os.path.join(base, "artifacts", "cli", "cli", "livingbrain", "openapi0.json"), encoding="utf-8"))
sa, sb = pub["components"]["schemas"], cli["components"]["schemas"]


def shape(s):
    """Functional shape: property names, types, required, enum values, refs."""
    if not isinstance(s, dict):
        return s
    out = {}
    if "properties" in s:
        out["props"] = {k: shape(v) for k, v in s["properties"].items()}
    for key in ("type", "format", "enum", "required", "items", "$ref", "oneOf", "anyOf", "default"):
        if key in s:
            out[key] = shape(s[key])
    return out


functional = []
doconly = []
for k in sorted(set(sa) & set(sb)):
    if json.dumps(shape(sa[k]), sort_keys=True) == json.dumps(shape(sb[k]), sort_keys=True):
        doconly.append(k)
    else:
        functional.append(k)

print("identical functional shape:", len(doconly))
print("functionally different:", len(functional))
print(functional)
for k in functional[:3]:
    a = json.dumps(shape(sa[k]), sort_keys=True)
    b = json.dumps(shape(sb[k]), sort_keys=True)
    print("\n---", k)
    print("published:", a[:600])
    print("cli      :", b[:600])
