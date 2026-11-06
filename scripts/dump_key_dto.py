import json, os

d = r"C:\Users\hiron\Documents\Default Project\living-brain-re\raw"
spec = json.load(open(os.path.join(d, "openapi.json"), encoding="utf-8"))
S = spec["components"]["schemas"]

want = ["BrainPageDto", "BrainPageDtoPageType", "BrainPageDtoStatus", "BrainPageDtoBucket",
        "BrainSearchReqDto", "BrainSearchResultDto", "BrainSearchResultDtoMatchedOn",
        "BrainCaptureReqDto", "BrainCaptureReqDtoKind", "BrainCaptureReqDtoBucket",
        "BrainConnectionDto", "BrainConnectionDtoStrength", "BrainConnectionDtoSource",
        "BrainScoreResDto", "BrainScoreMetricDto", "BrainScoreFactorDto", "BrainScoreFactorDtoTone",
        "BrainGraphNodeDto", "BrainGraphEdgeDto", "BrainChangeEventDto", "BrainChangeEventDtoAction",
        "BrainProfileDirectivesDto", "BrainProfileDto", "BrainIngestSourceDto", "BrainIngestSourceDtoStatus",
        "BrainIndexEntryDto", "BrainStatsResDto", "BrainPageSourceRefDto", "ErrorResDto", "BrainSourceDto"]

for w in want:
    print("=" * 15, w)
    print(json.dumps(S[w], indent=1)[:3500])
