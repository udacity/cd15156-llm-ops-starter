# Capstone Rubric — Production LLM FAQ Service

This rubric grades the deliverables defined in [`INSTRUCTIONS.md`](INSTRUCTIONS.md). Each row covers one deliverable and lists the submission requirements that must be present in `WRITEUP.md` for the row to pass.

## How to Use This Rubric

- **To pass the project**, every row below (1–9) must be satisfied. A reviewer should be able to verify each criterion using the artifacts in your `WRITEUP.md` (screenshots, log excerpts, code snippets) plus a fresh clone of your repository.
- **For a stand-out submission**, complete one or more of the ideas in [Suggestions to Stand Out](#suggestions-to-stand-out) in addition to the required rows.
- "Reasonable" thresholds (e.g., RAGAS faithfulness ≥0.7) are starting points; if your evidence shows the threshold should be different, justify it in the writeup and the reviewer will accept your justification.

## Retrieval Layer

### 1. Vector store populated with chunked, embedded product documents

**Criterion.** Build and populate a vector store of chunked, embedded product documents that supports relevance retrieval.

**Submission Requirements.** At least 5 new product JSON files appear under `data/products/`, or a quarantine/ingestion log under `data/inbox/` shows 5 successful inbox ingests of new products. Each new product validates against the schema in `src/ingestion/watcher.py::REQUIRED_FIELDS`. One `POST /query` curl output is included whose `sources[].doc_id` matches at least one of the new products.

## Generation and Routing

### 2. RAG pipeline with structured output and a tuned retrieval depth

**Criterion.** Operationalize a retrieval-augmented generation pipeline and tune retrieval depth against measured quality.

**Submission Requirements.** The output of `make eval-topk-sweep` (or an equivalent manual sweep) appears in `WRITEUP.md` and reports the four RAGAS metrics — `faithfulness`, `answer_relevancy`, `context_recall`, `context_precision` — at `top_k = 3`, `top_k = 5`, and `top_k = 10`. A recommended `top_k` value is named, and the justification cites at least two per-metric deltas from the sweep table. One `POST /query` curl output (or screenshot) is included where the response is a `QueryResponse` JSON containing `answer`, `sources`, `confidence`, `model`, `tokens`, `cost_usd`, `cached`, `trace_id`, and `blocked_by`, and `sources` contains at least one element with `doc_id`, `chunk_text`, and `similarity_score`.

### 3. Tiered model routing via the LLM gateway

**Criterion.** Route requests to tiered models through a gateway that balances cost and answer quality.

**Submission Requirements.** Three or more `POST /query` outputs are included that cover at least one simple-fact question and one complex / multi-product question. The `model` field differs across the captured outputs (e.g., `gpt-4o-mini` for simple, `gpt-4o` for complex), matching the tier mapping configured in `.env`. A short note in `WRITEUP.md` identifies which classification each query received.

## Data, Quality, and Safety

### 4. Automated data ingestion with quarantine for malformed inputs

**Criterion.** Automate knowledge-base ingestion so new product data becomes queryable without manual reprocessing, and route malformed inputs to a quarantine path.

**Submission Requirements.** At least 3 valid product JSONs are dropped into `data/inbox/` while `make serve` (or `make watch`) is running, and `WRITEUP.md` includes a `POST /query` curl output where `sources` references one of those products. At least 1 deliberately malformed JSON is dropped, and the writeup shows the resulting file path under `data/inbox/failed/` and the content of the sibling `.error.txt`.

### 5. Automated evaluation suite with a data-driven regression threshold

**Criterion.** Measure retrieval and generation quality with an automated evaluation suite and define data-driven regression thresholds.

**Submission Requirements.** The aggregate metrics table from one `make eval` run is captured in `WRITEUP.md`, including all four RAGAS metrics: `faithfulness`, `answer_relevancy`, `context_recall`, `context_precision`. The writeup names which of the four metrics scored lowest on this run and proposes a plausible cause grounded in the dataset or the pipeline (e.g., chunking, retrieval coverage, prompt). A regression threshold is proposed for at least one named metric (e.g., "faithfulness ≥ 0.75"). The threshold justification names the metric, cites at least one descriptive statistic from the eval run (median, percentile, or range), and states the action triggered on threshold violation.

### 6. Input and output guardrails

**Criterion.** Enforce input and output guardrails that block prompt injection, redact sensitive data, and surface hallucinations.

**Submission Requirements.** At least 3 new patterns are added to `INJECTION_PATTERNS` in `src/guardrails/input_guards.py`, or a new sensitive-data type is added to `PII_PATTERNS` and `PII_REDACTIONS` in the same module. For each added pattern, the submission includes one `POST /query` whose response sets `blocked_by` to the new pattern, and one `POST /query` on a legitimate question whose response has `blocked_by` null.

## Observability and Cost

### 7. Distributed tracing of the request pipeline

**Criterion.** Instrument the request pipeline with distributed tracing that exposes per-step latency and token usage.

**Submission Requirements.** At least 10 `POST /query` requests are issued, and `WRITEUP.md` includes either (a) a screenshot of one Phoenix trace at http://localhost:6006 in the `llm-ops-capstone` project with retrieval, classification, and generation spans visible and labeled, or (b) the markdown output of `make show-traces` for the same trace. The writeup names the slowest pipeline step for that trace and quantifies it as a fraction of total request latency.

### 8. Cost monitoring, per-tier summary, and savings vs. a single-model baseline

**Criterion.** Monitor per-request token usage and cost across models, and quantify savings from tiered routing against a single-model baseline.

**Submission Requirements.** `data/cost_log.jsonl` contains at least 50 entries; a 5-line excerpt is included in `WRITEUP.md` to show the entry shape, and a screenshot of `GET /cost-dashboard` is included showing per-model cost. The writeup contains a per-tier summary that names, for each model tier, the number of queries that hit it and the average per-query cost in dollars. `scripts/cost_report.py` (or `make cost-report`) is run against the same log; its output appears in the writeup with both absolute savings and a percentage relative to a named single-model baseline (e.g., `gpt-4o` for every request).

## Submission Quality

### 9. Documented implementation, evidence, and reproducible repository

**Criterion.** Document the implementation, evidence, and tradeoffs in a clean, reproducible repository.

**Submission Requirements.** `WRITEUP.md` exists at the project root and contains a section for each of the 9 required deliverables in numeric order. Each section contains a summary paragraph and the evidence named in the corresponding criterion above (curl outputs, screenshots, metric tables, or log excerpts). The submission includes captured output from `make test` (≥195 tests passing) and `make verify` (0 failed). `.env` is absent from the repository, and no API keys appear in committed files.

## Suggestions to Stand Out

These ideas aren't separately graded, but a submission that picks one or two of them up — and writes them up alongside the required deliverables — reads as a stand-out project.

- **Add a third routing tier.** Extend `src/pricing.py::MODEL_PRICING` with a budget tier and update `prompts/classifier.j2` so the classifier routes to it; show one query landing on each of the three tiers.
- **Engage the semantic cache.** Run 6 paraphrased questions about the same product and confirm at least 3 hit the cache (`cached: true`); inspect the cache collection via `chromadb.PersistentClient(path='data/chroma').get_or_create_collection('cache').get(limit=10)`. Sweep the similarity threshold (e.g., 0.85, 0.90, 0.95) and discuss the hit-rate vs. answer-quality tradeoff with a false-positive example.
- **Optimize first-token latency via streaming.** Use `compare_ttft` from `src/optimization/streaming.py` on at least 3 uncached questions, report the per-question and averaged TTFT improvement, and discuss when streaming is not worth the plumbing.
- **Project costs at scale.** Model a higher-volume scenario (e.g., 10,000 queries/day at the observed tier mix) and discuss what would change at scale (rate limits, cache pressure, eval cadence, on-call cost ceilings).
