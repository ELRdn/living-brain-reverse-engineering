# Living Brain リバースエンジニアリング 一次調査レポート

> やさしい図解版: https://elrdn.github.io/living-brain-reverse-engineering/

対象: `livingbrain.com` / `docs.livingbrain.com` / `api.livingbrain.com` / `livingbrain.fernmcp.dev` / 公開SDK・CLI・GitHub
手法: REA（受動的Web観測 + 成果物静的解析）+ 一次資料の直接取得 + ベンチマーク一次データによる再計算
調査日: 2026-11-06
状態: **Phase 1（静的証拠の確定）完了 / Phase 2以降は未実施**（理由は `PLAN.md`）

証拠の格付けは REA の規約に従い **観測 / 推測 / 不明** を明示する。
すべての出典URLは `evidence/SOURCES.md` に列挙した。

---

## 0. 要旨

Living Brain は「モデルの外に記憶を置く」という主張どおり、**チャンク検索型RAGではなく「ページ合成（compile）型」の記憶層**である。捕獲（capture）は同期的に受け付けられ、バックグラウンドワーカーが Extract → Route → Patch → Record → Embed/Link の5段でページを書き換える。APIは50パス・60オペレーション・111スキーマで、NestJS系のDTO命名とエラー封筒からバックエンド構成まで推定できる。

ベンチマーク主張は**一部が一次データで厳密に裏付けられ、一部が表面間で矛盾する**。LoCoMoの「1,540問」は公開データセット（1,986問）から敵対的カテゴリ446問を除いた部分集合と**完全一致**し、カテゴリ別内訳（282/321/96/841）も一致した。一方、中央値レイテンシと回答時間はランディングページと公式docsで数値が食い違う（464ms vs 592ms、3.7s vs 11.2s）。

製品としての最重要の未解決点は技術ではなく**信頼の設計**である。プライバシーポリシーはAI訓練利用を**オプトアウト方式**とし、APIは「ソースを削除しても派生ページは残る」と明記する。これは「記憶を外に置く」製品の中心的な約束（可搬性・削除可能性）と緊張関係にある。

---

## 1. 調査対象の同一性

| 項目 | 内容 | 格付け |
|---|---|---|
| 製品 | Living Brain（ChatAndBuild Ltd / ChatChat の記憶基盤） | 観測 |
| 発表 | X投稿 2026-11-04 13:59（@ladyxtel, 4.6M views） | 観測 |
| API | `https://api.livingbrain.com`（OpenAPI 3.1.0, version 1.0.0） | 観測 |
| MCP | `https://livingbrain.fernmcp.dev/livingbrain`（serverInfo version 0.1.0） | 観測 |
| 公開リポジトリ | `ChatAndBuild/livingbrain`（READMEのみ）, `-cli`, `-ts-sdk`, `-python-sdk` | 観測 |
| リポジトリ作成 | 2026-10-26〜10-28、SDK再生成コミットは 2026-11-04（発表当日） | 観測 |

発表当日にSDK/CLIが再生成されている（`SDK regeneration (#1)` 14:10Z、`(#2)` 16:02Z）。投稿は13:59（現地時刻表記）で、**公開成果物はローンチに合わせて整備された**と推測できる。

---

## 2. アーキテクチャの復元

### 2.1 記憶の単位と生成パイプライン（観測）

公式docsが明示する処理系:

```
Capture (同期, 202) → Extract → Route → Patch → Record → Embed & Link (非同期) → Search
ingest source: pending → compiling → completed | failed
```

- **Extract**: 捕獲から事実を抽出
- **Route**: 事実を既存ページの意味的近傍と比較
- **Patch**: 選ばれたページを**全文書き換え**し、既存記述を保持。適合ページがなければ新規作成
- **Record**: 出典リンク付きで新バージョンを保存
- **Embed & Link**: 検索用ベクトル更新 + 近傍ページとの接続判定

設計上の含意（推測を含む）:
- 全文Patch方式のため、1事実あたりの書き込みトークンは「差分」ではなく「ページ全体」に比例する。ページが育つほど捕獲コストが増える構造（**推測**、原価は非公開）
- 各段が独立に失敗し得る。ページ保存後に埋め込みが失敗してもページは残る（観測）
- `originRef` が冪等キー。同一originRefの再送は重複を作らない（観測）

### 2.2 データモデル（観測 / OpenAPI 111スキーマ）

主要エンティティ:

| 実体 | 主要フィールド | 備考 |
|---|---|---|
| Brain | id, name, description, briefSettings | subject単位で隔離 |
| Page | id, **tenantId**, subjectId, brainId, pageType, bucket, bucketSource, slug, title, summary, body, entities[], sources[], backlinks[], version, pinned, archived, status, lastCompiledAt, lastReferencedAt | `body`はMarkdown |
| Connection | pageAId/BId, similarity, strength, reasoning, source(auto/manual), ackedAt | モデル生成の理由文を持つ |
| IngestSource | kind, status, metadata, bucket | pending/compiling/completed/failed |
| ChangeEvent | action, changeSummary, pageSlug | 外部同期用フィード |
| Score | freshness, readiness, strain（各0-100, factors付き） | |

列挙型（仕様に固定）:
- `pageType`: source / topic / entity / project / decision / brief
- `status`: active / deprecated / stale / contested / archived
- `bucket`: inbox / notes / ideas / projects
- `capture.kind`: note / file / url / transcript / chat_turn / integration
- `strength`: weak / medium / strong
- `matchedOn`: semantic / keyword / both

**`tenantId` が全DTOに露出**している。これはB2B2C（1テナント内に複数subject）を前提とした多層分離モデルで、APIキー＝テナント、`x-subject-id`＝エンドユーザーという二段認証だと読める（観測＋推測）。

### 2.3 4つのスコアリング政策（観測: 名称と信号 / 不明: 重み）

docs は「設計政策」として4つを公開している。

| 記号 | 名称 | 決めること | 公開されている信号 |
|---|---|---|---|
| MWS | Memory Worthiness Score | その事実をページに維持するか | 耐久性, 影響, 再出現, 新規性, 将来利用, 抽出信頼度, 自分/プロジェクト関連性 / 不適素材で減点 |
| PFS | Placement Fit Score | どのページに置くか | 意味一致, 語一致, 共有实体, 関係判定, 時間整合, グラフ近接, ルーティング履歴 / **1位と2位の差（gap）**で place/review/new を決定 |
| CRS | Connection Resonance Score | 何とリンクするか | 近接, 関係意味, 証拠強度, 時間関連, グラフ証拠, 実効有用性, 補完性 / 重複・陳腐化で減点 |
| RPS | Re-entry Priority Score | いつ再浮上させるか | タスク適合, 接続強度, 緊急度, 未完了コミットメント, 再出現, 影響, 親和性, 新情報 / 疲労で減点 |

**重要**: 「重みは非公開」「APIはスコアを返さない」と明記されている（観測）。したがってこれは**再現可能なアルゴリズムではなく、説明可能な意思決定フレーム**である。第三者検証はブラックボックス実験になる。

PFSの「top-2 gap → review」は、記憶システムの典型的失敗である**誤マージ**（2社の類似事実が混ざる）に対する明示的な安全弁で、設計思想上の要点（観測）。

### 2.4 検索（観測）

- セマンティック（cosine）＋キーワード（title/summary/body）のハイブリッド
- `topK` 既定5、`minSimilarity` 既定**0.35**（キーワード一致は下限未満でも返す）
- 埋め込み対象は **title / summary / body冒頭のみ**。長い本文の後半はベクトル検索で到達できない（設計上の既知の限界）
- 返るのは `similarity`（ベクトル値のみ）で、**合成ランクは非公開**
- `matchedOn` で根拠種別を開示

これは「検索品質の監査可能性」を一部手放す設計だ。ランク関数が非公開なため、順位の妥当性は人手評価でしか検証できない（推測）。

### 2.5 Brain health（観測）

Freshness / Readiness / Strain の3指標。**`getPage` が `lastReferencedAt` を更新し、それがスコアに効く**と明記。つまり「読まれたこと」が健全性に算入される。これは利用ログと品質指標の混同であり、エージェントが自動で読むほどスコアが上がる構造（観測された仕様 + 設計上の批判は推測）。

### 2.6 基盤（観測）

| 層 | 証拠 |
|---|---|
| API | `X-Powered-By: Express`、`Set-Cookie: GCLB=...`、`Via: 1.1 google` → Node/Express系 + Google Cloud Load Balancer |
| エラー封筒 | `{statusCode, timestamp, path, message, body:{message,error,statusCode}}` → NestJS系の例外フィルタ + 独自ラップ |
| DTO命名 | `BrainPageDto`, `BrainCaptureReqDtoKind` → NestJS + Swagger生成 |
| マーケ/Workspace | Next.js（Turbopackチャンク）、Cloudflare、`x-nextjs-prerender` |
| 計測 | PostHog（`/ingest/array/phc_...` にリバースプロキシ）＋ Mixpanel（IndexedDB: `mixpanelBrowserDb`） |
| フォント | `ChatSans`（自社ブランド書体、woff2 8ウェイト） |
| SDK/CLI/MCP | すべて **Fern** 生成（`fern shield` バッジ、`openapi0.json` 埋め込み、`fern_cli_sdk`） |

REA実行時観測: `ev_c190b54a6e2ec4662c6ea65df9844ecf8e65fddae689815b5f52776a8fc69ab6`
（`https://livingbrain.com/workspace`、スクリプト37件、localStorage 2キー、IndexedDB 2件。`completeness: policy_filtered`、network/consoleはアタッチ前のため空）

### 2.7 MCPサーバは**2つ**ある（観測）

**(a) APIキー型: `https://livingbrain.fernmcp.dev/livingbrain`**
- `initialize` と `tools/list` が**無認証で応答**（レート制限の範囲内で1回ずつ実行）
- 60ツール（OpenAPIの60オペレーションと1:1、Fern生成）
- `serverInfo.instructions` に生成物由来の記述矛盾: 「accepts either an API key (x-api-key header) or an API key (x-subject-id header)」→ **subject-idをAPIキーと誤記**（自動生成ドキュメントの品質指標）
- ツール説明は「abbreviated」で、完全スキーマは `_meta.openapi/operationId` 経由で参照させる設計

**(b) サインイン型: `https://api.livingbrain.com/mcp`（OAuth）**
- ChatGPT / Claude のコネクタとして使う想定。APIキー不要
- ツール名が `living_brain_*` 系（12ツール）で、Fern生成側とは**別実装**
- OAuthスコープで露出が変わる: `livingbrain:list` / `manage` / `search` / `read` / `capture`
- MCPリソース: `livingbrain://brains/{brainId}/index`, `.../pages/{slug}`, `.../profile`
- **MCP Apps のUIリソース**: `ui://living-brain/v3/setup.html`, `v1/search.html`, `v5/graph.html`, `livingbrain://ui/brain-model/{chunk}`
  → バージョン番号が資源ごとに異なる = 反復開発の痕跡（推測）
- 設計上の配慮: 「brainIdはアクセス可能なbrainが1つのときのみ省略可」

**60ツール＝60プラットフォームではない**。ランディングは「60+ AI Platforms」、docsは「Browse all 60 tools」と書いており、数字の出所が異なる（観測。混同か意図的圧縮かは不明）。

### 2.8 認証・分離・権限（観測）

- 必須ヘッダ: `x-api-key` + `x-subject-id`（UUID必須）
- APIキーは**組織スコープ**で、発行されたメンバーのロールを継承（Owner / Admin / Developer / Viewer）
- subjectは「ホスト定義」。つまり顧客アプリのエンドユーザーIDをそのまま流す設計
- 分離の実装: 他subjectのbrainは **404**（403ではない）。「存在するが自分のものではない」と「存在しない」を区別しない設計で、**他ユーザーのbrainを探る攻撃面を塞いでいる**（docs明記）
- 無効キー時の応答: HTTP 401、`{"statusCode":401,...,"message":"Invalid API key"}`（実測）

### 2.9 生成物のドリフト（観測）

CLIリポジトリに埋め込まれた `openapi0.json` と、公開中の `openapi.json` を機械比較した。

| 項目 | CLI埋め込み版 | 公開版 |
|---|---|---|
| オペレーション数 | 60 | 60 |
| パス/メソッドの差分 | なし | なし |
| operationId | `slack_startOAuth` | `slack_startOauth`（大小文字） |
| スキーマ数 | 72 | 111（enumを独立スキーマ化） |
| 機能差 | `originRef: string`（非null） | `originRef: string \| null` |

→ **機能差はほぼなく、null許容とenum抽出の生成規則差**。CLIは公開仕様より1世代前の記述を持つ（低リスクのドリフト）。

---

## 3. ベンチマーク主張の検証

### 3.1 LoCoMo: 部分集合の特定に成功（観測）

公開データ `locomo10.json` を取得し、カテゴリを集計した結果:

| カテゴリ | 公式データ件数 | Living Brain docs の件数 | 一致 |
|---|---|---|---|
| multi-hop (cat 1) | 282 | 282 | ✓ |
| temporal (cat 2) | 321 | 321 | ✓ |
| open-domain (cat 3) | 96 | 96 | ✓ |
| single-hop (cat 4) | 841 | 841 | ✓ |
| adversarial (cat 5) | 446 | **記載なし（除外）** | — |
| 合計 | **1,986** | **1,540** | 1,986 − 446 = 1,540 ✓ |

**結論（観測）**: Living Brain の「1,540問」は LoCoMo 全問ではなく、**敵対的（回答不能）カテゴリを除いた部分集合**。これは Mem0 の評価プロトコルと同じ除外規則であり、比較可能性の土台は揃っている。

> 注: 本調査では**独立再現は実施しない**（依頼者判断）。以下は公開値の内部整合性と、一次データによる分母の検証までである。

カテゴリ別正答率から全体を再計算:
`(0.947×321 + 0.94×282 + 0.927×841 + 0.74×96) / 1540 = 1,419.7 / 1,540 = 92.19%`
→ 公称 92.2% と整合（観測）。内部整合性は高い。

ただし以下は**比較の限界**（観測に基づく推測）:
- 回答モデルは GPT-5。Mem0論文の回答モデル（GPT-4o系）と異なるため、92.2% vs 66.9% を直接並べることはできない
- 「judged accuracy」の判定者・プロンプト・再現手順は非公開。**回答者と判定者が同一モデル系列**だと self-preference bias が入る（推測。判定モデルは非公開）
- 敵対的質問の除外は、記憶システムの「知らないと言う能力」を測らない。LongMemEvalの abstention 能力とは別物

### 3.2 表面間の数値矛盾（観測）

| 指標 | ランディング (`livingbrain.com`) | 公式docs (`/docs/benchmarks`) |
|---|---|---|
| LoCoMo 中央値retrieval | **464 ms** | **592 ms** |
| 中央値answer時間 | **3.7 s** | **11.2 s** |
| コンテキスト | 9.4K vs 26K（2.8×） | 同値 |
| 正答数 | 92.2% | 1,420/1,540（=92.2%） |

同一ベンチ（batch `f8d531ac`, 2026-11-01）を指しながら数値が異なる。**版の取り違え、または測定条件の再定義**が起きている（推測）。マーケ側の数値が良い方向にだけ動いている点は、統制された再測定ではなく更新漏れの可能性が高い。

### 3.3 LongMemEval の主張（観測 + 推測）

- 「22.6× fewer tokens（5.1K vs 116K）」「95% lower cost」「**0% hallucinations**」
- 22.6× は 116/5.1 = 22.75 で算術的に整合（観測）
- LongMemEval は5能力（情報抽出・マルチセッション推論・時間推論・知識更新・**棄権**）を測るベンチで、公式問題数は500（一次資料で確認）
- **「0% hallucinations」は指標として定義されていない**。棄権（abstention）問題を除外すれば0%は構成上ほぼ自明になる（推測。除外の有無は非公開）
- したがってこの数値は**反証不能な主張**に近く、購買判断の根拠には使えない（評価）

### 3.4 「#1 on LoCoMo」の意味（観測 + 推測）

ランディングには「Ranked #1 on LoCoMo **in our internal comparisons**」「Rankings apply to the systems and configurations tested」と注記がある。つまり**比較集合は非公開**で、外部リーダーボードではない。表現自体は誠実だが、見出しだけが独走する構造（評価）。

---

## 4. 主張と証拠のギャップ一覧

| 主張 | 証拠の状態 | 判定 |
|---|---|---|
| 92.2% on LoCoMo | 一次データで部分集合・内訳・算術を再現 | **支持**（比較可能性に留保） |
| 464ms retrieval | docsは592ms | **矛盾** |
| 3.7s answer | docsは11.2s | **矛盾** |
| 22.6× fewer tokens | 算術整合、基準は116K full-context | 支持（自己申告） |
| 0% hallucinations | 指標定義なし、棄権除外の可能性 | **反証不能** |
| 60+ AI Platforms | 60はMCPツール数と一致 | **要検証**（混同の疑い） |
| "persistent and self-learning" | self-learning の定義・機構は非公開 | 不明 |
| "interoperable" | MCP/API/SDK/CLIで実装されている | **支持**（観測） |
| "memory outside the model" | ページを外部DBに保持し検索時に注入 | **支持**（観測） |

---

## 5. 設計上の重要所見（専門家向け）

1. **削除の連鎖が切れている（観測）**: 公式docsは明記する —「Deleting a source leaves any pages already derived from it in place — delete those separately if you want them gone.」出典を消しても知識は残る。GDPR Art.17（消去権）と「記憶」製品の相性問題が、仕様として現れている。ページ単位の永久削除（`permanent: "true"` 必須）はあるが、**出典から派生ページへの連鎖削除は提供されていない**。
2. **訓練利用がオプトアウト式（観測）**: プライバシーポリシー第8条は「you may opt out of having your personal data used for AI model training at any time」。既定は利用可。記憶＝最も機微な文脈の集積であることを踏まえると、これは導入時の主要なデューデリジェンス項目。
3. **自社コンテンツはAI学習を拒否（観測）**: `robots.txt` は `Content-Signal: ai-train=no` とし、GPTBot/ClaudeBot/Google-Extended等をDisallow。プロダクトの入力側と出力側で立場が非対称。
4. **健全性スコアが利用ログと結合（観測）**: `lastReferencedAt` が Freshness に寄与。品質指標として解釈するには注意が必要。
5. **全文Patch（観測）**: 長期運用でのトークン原価はページサイズに比例。`$8/M input` の従量課金と組み合わせると、**記憶が育つほど単価が上がる**構造になり得る（推測）。
6. **検索の到達範囲が本文冒頭に限定（観測）**: 長文ページの後半は意味検索で拾えない。設計上のトレードオフが明示されている点は評価できる。
7. **監査可能性の設計（観測）**: `matchedOn`、`reasoning`（接続理由）、`factors`（スコア要因）、ChangeEvent を返す。ブラックボックスにしすぎない配慮がある。
8. **チャット分類器が全ターン課金（観測）**: 「Send every turn. The classifier is the point」と明記。会話量に比例してLLM分類コストが発生する設計で、料金表の「Automatic chat-turn classification: charged by measured model tokens」と整合する。**会話プロダクトでは捕獲コストが利用量に線形に効く**（推測: 単価は非公開）。

---

## 6. 未解決の問い（**本調査では未検証**。APIキーを用いた動的検証が必要）

以下は仕様からは答えが出ず、実サービスへの実験が必要な項目。依頼者判断により Phase 2 は実施していないため、**すべて「不明」**として残す。

- 1捕獲あたりの実コストとレイテンシ分布（公開値は中央値のみ）
- 同一内容の再捕獲・矛盾する追記・同時書き込みでの PFS/CRS の実際の挙動
- `export/markdown` の忠実性（再取り込みで同一グラフが再現するか）
- subject分離の実装強度（他subjectのページが検索・グラフに漏れないか）
- MCP経由のプロンプトインジェクション耐性（捕獲内容が指示として解釈されないか）
- Webhook署名・リトライ・順序保証
- 料金表の「requests」の定義（1ツール呼び出し＝1リクエストか）
- 競合（Mem0 / Zep / Letta / Supermemory / OpenAI memory / Anthropic memory）との同一条件比較

---

## 7. 成果物

- `raw/openapi.json` — OpenAPI 3.1 仕様（50パス / 60オペレーション / 111スキーマ）
- `raw/mcp-tools.json` — MCP `tools/list` の生レスポンス（60ツール）
- `raw/locomo10.json` — LoCoMo 公式データ（検証用）
- `evidence/rea-evidence-bundle.json` — REA Evidence バンドル（1レコード）
- `scripts/analyze_openapi.py`, `scripts/dump_key_dto.py`, `scripts/parse_mcp.py`, `scripts/check_locomo.py` — 再実行可能な検証コード
