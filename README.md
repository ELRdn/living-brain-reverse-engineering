# Living Brain — Reverse Engineering & Verification

> **やさしい図解版 → https://elrdn.github.io/living-brain-reverse-engineering/**

An evidence-led teardown of [Living Brain](https://livingbrain.com/) — a "memory outside the model" layer for AI agents — plus a replication plan for its benchmark claims.

> Status: **Phase 1 (static evidence) complete.** Dynamic verification is pending an API key. See [`PLAN.md`](PLAN.md) §8.

## What this repo answers

| Question | Answer | Evidence |
|---|---|---|
| What is it, architecturally? | A page-compiling memory layer, not chunk RAG. `Capture → Extract → Route → Patch → Record → Embed/Link` | [`REPORT.md`](REPORT.md) §2.1 |
| How big is the public surface? | 50 paths / 60 operations / 111 schemas; 60 MCP tools | `raw/openapi.json`, `raw/mcp-tools.json` |
| Is "92.2% on LoCoMo" verifiable? | The 1,540-question set is LoCoMo minus 446 adversarial questions — confirmed against the public dataset | [`REPORT.md`](REPORT.md) §3.1 |
| Are the marketing numbers consistent? | No. 464 ms vs 592 ms retrieval; 3.7 s vs 11.2 s answer | [`REPORT.md`](REPORT.md) §3.2 |
| What stack is behind it? | NestJS/Express + Google Cloud LB; Next.js/Turbopack + Cloudflare; Fern-generated SDK/CLI/MCP | [`REPORT.md`](REPORT.md) §2.6 |
| How many MCP surfaces? | Two: a Fern-generated API-key server (60 tools) and a hand-built OAuth server (12 tools, 7 resources, MCP Apps UI) | [`REPORT.md`](REPORT.md) §2.7 |
| What are the trust risks? | AI-training opt-out by default, derived pages survive source deletion, asymmetric robots policy | [`REPORT.md`](REPORT.md) §5 |

## Contents

```
REPORT.md                     Findings, with observed / inferred / unknown labels
PLAN.md                       Redesigned plan, gap analysis, decisions required
evidence/SOURCES.md           Every source URL, with fetch status
evidence/rea-evidence-bundle.json   REA evidence bundle (1 record, 67 KB)
raw/openapi.json              OpenAPI 3.1 spec (136 KB)
raw/mcp-tools.json            MCP tools/list response (60 tools)
raw/locomo10.json             LoCoMo dataset used for the 1,986 → 1,540 check
scripts/                      Re-runnable verification code
```

## Reproduce the checks

```bash
# LoCoMo is third-party data and is not redistributed here.
curl -L -o raw/locomo10.json \
  https://raw.githubusercontent.com/snap-research/locomo/main/data/locomo10.json

python scripts/check_locomo.py        # 1,986 QA → 1,540 after removing category 5
python scripts/analyze_openapi.py     # path/operation/schema inventory
python scripts/parse_mcp.py           # MCP tool inventory
python scripts/dump_key_dto.py        # core data model
python scripts/diff_specs.py          # published spec vs CLI-embedded spec
python scripts/diff_specs_shape.py    # functional-shape comparison
```

Only the LoCoMo download needs network access; everything else runs offline.

## Method

- **Static**: OpenAPI spec, docs (`llms.txt` index), MCP `tools/list`, public SDK/CLI sources, npm metadata, GitHub history.
- **Runtime**: REA passive CDP inspection of `livingbrain.com/workspace` (`ev_c190b54a6e2ec4662c6ea65df9844ecf8e65fddae689815b5f52776a8fc69ab6`) — 37 scripts, PostHog/Mixpanel, IndexedDB inventory. No JavaScript was evaluated and no page was mutated.
- **Benchmark**: recomputation against `snap-research/locomo` primary data.

Every claim in `REPORT.md` carries one of three labels: **観測 (observed)**, **推測 (inferred)**, **不明 (unknown)**.

## Scope and ethics

Read-only. No cross-tenant probing, no load testing, no destructive calls. One unauthenticated request each to the API and MCP endpoints, to observe the public error envelope and tool inventory.

## License

Code: MIT. Documents: CC BY 4.0. Third-party datasets (LoCoMo) are **not** redistributed; cite the original repository.
