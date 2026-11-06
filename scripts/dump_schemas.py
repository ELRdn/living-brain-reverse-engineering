import json, os

d = r"C:\Users\hiron\Documents\Default Project\living-brain-re\raw"
spec = json.load(open(os.path.join(d, "openapi.json"), encoding="utf-8"))
S = spec["components"]["schemas"]
print("ALL SCHEMAS:", len(S))
print(", ".join(sorted(S)))
print()
want = ["Page", "PageSummary", "SearchRequest", "SearchResponse", "SearchResult", "CaptureRequest",
        "Capture", "Connection", "Score", "ScoreMetric", "ScoreFactor", "Graph", "GraphNode",
        "ChangeEvent", "BrainProfile", "PageVersion", "IngestSource", "PromptIndex", "BucketCounts"]
for w in want:
    cand = [k for k in S if k.lower() == w.lower()]
    for k in cand:
        print("=" * 20, k)
        print(json.dumps(S[k], indent=1)[:4000])
