# 出典一覧（原文URL）

すべて 2026-11-06 に取得。状態は「取得済み（本文を読んだ）」「応答のみ（ステータス/ヘッダのみ）」「未取得（リンク存在のみ）」を区別する。

## A. 製品公式サイト

| # | URL | 内容 | 状態 |
|---|---|---|---|
| A1 | https://livingbrain.com/ | ランディング。92.2% / 464ms / 22.6× / 0% hallucination の主張 | 取得済み |
| A2 | https://livingbrain.com/pricing | 料金。$8/M input, $0.50/M output, Workspace $99/月, レート制限 | 取得済み |
| A3 | https://livingbrain.com/about-us | 会社・チーム・Research Observatory デモ | 取得済み |
| A4 | https://livingbrain.com/privacy-policy | 第8条にAI訓練のオプトアウト規定、保持期間 | 取得済み |
| A5 | https://livingbrain.com/robots.txt | `Content-Signal: ai-train=no`、学習クローラ拒否 | 取得済み |
| A6 | https://livingbrain.com/workspace | アプリ本体（要認証）。REA観測対象 | 取得済み（HTML）+ REA観測 |
| A7 | https://livingbrain.com/stories | ニュースルーム | 未取得 |
| A8 | https://livingbrain.com/contact | 問い合わせ | 未取得 |
| A9 | https://livingbrain.com/terms-of-service | 利用規約（訓練利用の詳細はここ参照と明記） | 未取得 |
| A10 | https://livingbrain.com/.well-known/security.txt | 存在せず（HTMLフォールバック） | 応答のみ |
| A11 | https://livingbrain.com/sitemap.xml | 存在せず（HTMLフォールバック） | 応答のみ |

## B. 公式ドキュメント

| # | URL | 内容 | 状態 |
|---|---|---|---|
| B1 | https://docs.livingbrain.com/ | ドキュメント入口 | 取得済み |
| B2 | https://docs.livingbrain.com/llms.txt | 全ページ索引（AIエージェント向け） | 取得済み |
| B3 | https://docs.livingbrain.com/openapi.json | OpenAPI 3.1 仕様（一次成果物） | 取得済み |
| B4 | https://docs.livingbrain.com/openapi.yaml | 同 YAML | 未取得 |
| B5 | https://docs.livingbrain.com/docs/concepts.md | パイプライン・データモデル定義 | 取得済み |
| B6 | https://docs.livingbrain.com/docs/design-policies.md | MWS/PFS/CRS/RPS の信号 | 取得済み |
| B7 | https://docs.livingbrain.com/docs/search-ranking.md | ハイブリッド検索、0.35床、matchedOn | 取得済み |
| B8 | https://docs.livingbrain.com/docs/benchmarks.md | LoCoMo実行条件、batch f8d531ac、592ms/11.2s | 取得済み |
| B9 | https://docs.livingbrain.com/docs/brain-health.md | Freshness/Readiness/Strain | 取得済み |
| B10 | https://docs.livingbrain.com/docs/pages.md | ページ操作、削除の意味論 | 取得済み |
| B11 | https://docs.livingbrain.com/docs/importing.md | Obsidian/Claude/ChatGPT 取り込み手順 | 取得済み |
| B12 | https://docs.livingbrain.com/mcp.md | MCP接続、60ツール、認証ヘッダ | 取得済み |
| B13 | https://docs.livingbrain.com/docs/capturing.md | 捕獲の詳細 | 未取得 |
| B14 | https://docs.livingbrain.com/docs/search.md | 検索・prompt index | 未取得 |
| B15 | https://docs.livingbrain.com/docs/changes.md | Change feed / webhook | 未取得 |
| B16 | https://docs.livingbrain.com/docs/build.md | 実装パターン | 未取得 |
| B17 | https://docs.livingbrain.com/docs/authentication.md | 認証モデル | 未取得 |
| B18 | https://docs.livingbrain.com/docs/errors.md | エラー封筒・再試行 | 未取得 |
| B19 | https://docs.livingbrain.com/docs/slack.md | Slack連携 | 未取得 |
| B20 | https://docs.livingbrain.com/cli.md | CLI | 未取得 |
| B21 | https://docs.livingbrain.com/sdk/typescript.md | TS SDK | 未取得 |
| B22 | https://docs.livingbrain.com/sdk/python.md | Python SDK | 未取得 |
| B23 | https://docs.livingbrain.com/mcp/sign-in.md | サインイン型MCP | 未取得 |
| B24 | https://docs.livingbrain.com/docs/use-cases/x-support-bot.md | ユースケース（X bot） | 未取得 |
| B25 | https://docs.livingbrain.com/docs/use-cases/coding-agent-memory.md | ユースケース（コーディングエージェント） | 未取得 |

## C. 実サービスへの直接観測

| # | URL / エンドポイント | 内容 | 状態 |
|---|---|---|---|
| C1 | `GET https://api.livingbrain.com/v1/brains` | 無効キーで401。`X-Powered-By: Express`, `GCLB` cookie, エラー封筒を取得 | 応答のみ（1回） |
| C2 | `POST https://livingbrain.fernmcp.dev/livingbrain` (`initialize`) | serverInfo: livingbrain 0.1.0, protocol 2025-06-18, defaultBaseUrl | 応答のみ（1回） |
| C3 | 同 (`tools/list`) | 60ツールの完全な一覧とスキーマ | 取得済み（`raw/mcp-tools.json`） |
| C4 | `https://livingbrain.com/workspace` via CDP | REA Evidence `ev_c190b54a...`（37スクリプト、PostHog/Mixpanel、IndexedDB） | 取得済み |

## D. 公開コード・パッケージ

| # | URL | 内容 | 状態 |
|---|---|---|---|
| D1 | https://github.com/ChatAndBuild/livingbrain | README（主張の再掲、team-reported の注記あり） | 取得済み（clone） |
| D2 | https://github.com/ChatAndBuild/livingbrain-cli | Rust製CLI。Fern生成 + `custom.rs` | 取得済み（clone） |
| D3 | https://github.com/ChatAndBuild/livingbrain-ts-sdk | TypeScript SDK（Fern生成、879ファイル） | 取得済み（clone） |
| D4 | https://github.com/ChatAndBuild/livingbrain-python-sdk | Python SDK | 取得済み（clone） |
| D5 | https://github.com/ChatAndBuild/livingbrain-cli/releases/tag/v0.2.4 | バイナリ配布（Windows/macOS/Linux） | 取得済み（メタデータ） |
| D6 | https://registry.npmjs.org/@living-brain/sdk | npmメタデータ（0.3.1, 公開 2026-11-04T14:45Z, SLSA provenance付き） | 取得済み |
| D7 | https://pypi.org/pypi/livingbrain/json | PyPI（404。CLIはPyPI配布ではない） | 応答のみ |
| D8 | https://github.com/ChatAndBuild | 組織の公開リポジトリ一覧（21件） | 取得済み |

## E. ベンチマーク一次資料

| # | URL | 内容 | 状態 |
|---|---|---|---|
| E1 | https://snap-research.github.io/locomo/ | LoCoMo 公式サイト | 未取得 |
| E2 | https://github.com/snap-research/locomo | 公式リポジトリ | 取得済み |
| E3 | https://raw.githubusercontent.com/snap-research/locomo/main/README.MD | 10会話・注釈仕様・50→10会話への縮小の経緯 | 取得済み |
| E4 | https://raw.githubusercontent.com/snap-research/locomo/main/data/locomo10.json | 実データ。1,986問・カテゴリ内訳を実測 | 取得済み |
| E5 | https://arxiv.org/abs/2402.17753 | LoCoMo 論文（README記載のarXiv ID） | 未取得 |
| E6 | https://arxiv.org/abs/2410.10813 | LongMemEval（ICLR 2025）。500問・5能力 | 取得済み |
| E7 | https://arxiv.org/abs/2504.19413 | Mem0 論文。LoCoMo比較の先行研究 | 取得済み |
| E8 | https://github.com/xiaowu0162/LongMemEval | LongMemEval 公式リポジトリ | 取得済み（目録のみ） |

## F. 発表・第三者の言及

| # | URL | 内容 | 状態 |
|---|---|---|---|
| F1 | https://x.com/ladyxtel/status/2117980022250316282 | 発表投稿（2026-11-04 13:59, 4.6M views, 931 reposts） | 取得済み |
| F2 | https://x.com/yourlivingbrain | 製品公式X | 未取得 |
| F3 | https://claude.com/customers/chatandbuild | Anthropic 導入事例（ランディングからリンク） | 未取得 |
| F4 | https://cloud.google.com/customers/chatandbuild | Google Cloud 導入事例（同上） | 未取得 |
| F5 | https://www.linkedin.com/posts/openai-for-startups_at-twitter-christel-buchanan-helped-provide-activity-7406832106598866944-YbO5/ | OpenAI for Startups 投稿（同上） | 未取得 |
| F6 | https://www.nvidia.com/en-sg/startups/ | NVIDIA Inception（同上） | 未取得 |
| F7 | https://discord.gg/chatandbuild | コミュニティ | 未取得 |
| F8 | https://chatchat.com/ | 親プロダクト | 未取得 |

## G. 未検証だが重要な情報源（Phase 2 で追加）

- Wayback Machine: `https://web.archive.org/web/2026*/livingbrain.com/*`（主張の時系列変化）
- `https://livingbrain.com/stories`（プレスリリース・資金調達）
- `https://www.crunchbase.com/`（ChatAndBuild の資金・投資家）
- Hacker News / Reddit / Discord の実ユーザー報告
- 競合の一次資料: Mem0 (`docs.mem0.ai`)、Zep (`getzep.com`)、Letta (`letta.com`)、Supermemory (`supermemory.ai`)
- OpenAI / Anthropic の公式メモリ仕様（比較対象の一次仕様）
