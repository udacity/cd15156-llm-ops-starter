# Capstone Rubric — Production LLM FAQ Service

This rubric grades the deliverables defined in [`INSTRUCTIONS.md`](INSTRUCTIONS.md).
Each row covers one deliverable. The **Meets Specifications** column is the
bar to pass; the optional **Exceeds Specifications** column describes
stretch work that distinguishes a stand-out submission.

## How to Use This Rubric

- **To pass the project**, every row in [Required Deliverables (1–9)](#required-deliverables) must reach **Meets Specifications**, plus the [Writeup](#writeup-quality) and [Workspace Hygiene](#workspace-hygiene) rows.
- **For a stand-out submission**, complete at least one of the two [Bonus Deliverables (10–11)](#bonus-deliverables) at **Meets Specifications** and any one row at **Exceeds Specifications**.
- A reviewer should be able to verify each criterion using the artifacts in your `WRITEUP.md` (screenshots, log excerpts, code snippets) plus a fresh clone of your repository.
- "Reasonable" thresholds (e.g., RAGAS faithfulness ≥0.7) are starting points; if your evidence shows the threshold should be different, justify it in the writeup and the reviewer will accept your justification.

## Required Deliverables

### 1. Vector Database Populated

| | Meets Specifications |
|---|---|
| **Criterion** | The Chroma collection contains the seed corpus plus the learner's additions. Retrieval returns relevant chunks for both seed and new products. |
| **Evidence required** | At least 5 new product JSONs in `data/products/` (or proof of equivalent ingestion through `data/inbox/`). Output of one `POST /query` showing retrieval includes a new product. |

| | Exceeds Specifications |
|---|---|
| **Stretch** | Documents the chunking choice (one chunk per product vs. a multi-chunk-per-product alternative) and shows retrieval differences between the two strategies on at least three queries. |

### 2. RAG Pipeline With Structured Output

| | Meets Specifications |
|---|---|
| **Criterion** | `POST /query` returns a `QueryResponse` JSON with `answer`, `sources` (with `doc_id` + `chunk_text` + `similarity_score`), `confidence`, `model`, `tokens`, `cost_usd`, `cached`, `trace_id`, and `blocked_by` populated as specified by `src/models.py::QueryResponse`. |
| **Evidence required** | Curl output (or screenshot) of one query showing all fields. RAGAS scores from at least one `make eval` run. |

| | Exceeds Specifications |
|---|---|
| **Stretch** | Tunes `top_k` to two non-default values (e.g., 3 and 10), reports per-metric RAGAS deltas, and recommends a value with a justification grounded in the data. |

### 3. LLM Gateway With Tiered Routing

| | Meets Specifications |
|---|---|
| **Criterion** | The classifier in `src/gateway/classifier.py` routes between at least two model tiers; demonstrably some queries hit `gpt-4o-mini` and others hit `gpt-4o` (or whatever pair is configured in `.env`). |
| **Evidence required** | At least 4 queries logged showing the `model` field varies by classification. `prompts/classifier.j2` is unmodified or modified with a justification. |

| | Exceeds Specifications |
|---|---|
| **Stretch** | Adds a third tier (e.g., a budget tier) by extending `src/pricing.py::MODEL_PRICING` and updating the classifier prompt to route to it. Shows a query routed to each of the three tiers. |

### 4. Automated Data Ingestion (File Watcher)

| | Meets Specifications |
|---|---|
| **Criterion** | A new product JSON dropped into `data/inbox/` while `make watch` runs is ingested (chunked, embedded, upserted to Chroma) and becomes queryable. A malformed JSON is quarantined to `data/inbox/failed/` with a sibling `.error.txt`. |
| **Evidence required** | Two artifacts: a successful ingestion (the new product appears in a subsequent `POST /query` result) and a quarantined file (`<name>.error.txt` content). |

### 5. Automated Evaluation Suite

| | Meets Specifications |
|---|---|
| **Criterion** | `make eval` runs without error against `data/golden_test_set.csv` and produces the four RAGAS metrics (`faithfulness`, `answer_relevancy`, `context_recall`, `context_precision`). The learner proposes a regression threshold for at least one metric and justifies it. |
| **Evidence required** | The aggregate metrics table from one full eval run. The proposed threshold and a one-paragraph justification in the writeup. |

| | Exceeds Specifications |
|---|---|
| **Stretch** | Adds at least one more golden-set row (representative of a real customer question), re-runs the eval, and discusses score change. |

### 6. Input and Output Guardrails

| | Meets Specifications |
|---|---|
| **Criterion** | The learner adds at least 3 new injection patterns to `INJECTION_PATTERNS` in `src/guardrails/input_guards.py`, OR adds a new PII type to `PII_PATTERNS` and `PII_REDACTIONS`. New patterns demonstrably block hostile input while letting legitimate questions pass. |
| **Evidence required** | Two paired curl examples per added pattern: one that triggers the new guardrail (response has `blocked_by`) and one that should not (response is a normal answer). |

| | Exceeds Specifications |
|---|---|
| **Stretch** | Compares the **three** input-guard configurations on the same 5 hostile inputs: (a) regex alone (`src/guardrails/input_guards.py`), (b) LLM Guard alone (DeBERTa + Presidio, by stripping the regex pre-filter from `src/guardrails/llm_guard/input_guards.py`), and (c) the layered default (regex pre-filter then DeBERTa fall-through). Report false-positive / false-negative rates and discuss when each layer earns its keep. |

### 7. Distributed Tracing

| | Meets Specifications |
|---|---|
| **Criterion** | Phoenix traces include at least 10 queries from the learner's session, with the full RAG pipeline visible (retrieval, generation, latency per step, token counts). |
| **Evidence required** | Either a screenshot of the Phoenix dashboard at http://localhost:6006 showing a representative trace expanded with the spans labeled, **or** the markdown output of `make show-traces` for environments where port 6006 isn't reachable. The learner identifies which step is the slowest and quantifies it. |

| | Exceeds Specifications |
|---|---|
| **Stretch** | Proposes a remediation for the slowest step (e.g., parallel retrieval, model swap, prompt compression) and estimates the latency improvement. |

### 8. Cost Monitoring Dashboard

| | Meets Specifications |
|---|---|
| **Criterion** | The cost log at `data/cost_log.jsonl` contains at least 50 entries from the learner's runs. `GET /cost-dashboard` renders without error and shows per-model cost. |
| **Evidence required** | Screenshot of the cost dashboard with non-trivial numbers, plus a 5-line excerpt from `cost_log.jsonl` showing the entry shape. |

### 9. Cost Savings Analysis (Tiered vs. Baseline)

| | Meets Specifications |
|---|---|
| **Criterion** | Using `scripts/cost_report.py`, the learner compares actual cost (tiered routing) against a single-model baseline (e.g., `gpt-4o` for everything) over the same 50-query log. Reports absolute savings and a percentage. |
| **Evidence required** | The `cost_report.py` output captured in the writeup. |

| | Exceeds Specifications |
|---|---|
| **Stretch** | Models a higher-volume scenario (e.g., 10,000 queries/day at the same tier mix) and projects monthly savings. Discusses what would change at scale. |

## Bonus Deliverables

### 10. Semantic Cache (Bonus)

| | Meets Specifications |
|---|---|
| **Criterion** | The semantic cache is engaged by the HTTP route (default behavior in `src/gateway/routes.py`). The learner runs paraphrased queries and observes cache hits via the `cached: true` flag in the response. Reports hit rate at the default similarity threshold. |
| **Evidence required** | Six paraphrased queries showing at least three cache hits, plus the cache contents listed via `chromadb.PersistentClient(path='data/chroma').get_or_create_collection('cache').count()` and `.get(limit=10)['metadatas']`. |

| | Exceeds Specifications |
|---|---|
| **Stretch** | Sweeps the similarity threshold (e.g., 0.85, 0.90, 0.95) and reports hit-rate vs. answer-quality tradeoff with concrete examples of false-positive cache hits at low thresholds. |

### 11. Latency Optimization via Streaming (Bonus)

| | Meets Specifications |
|---|---|
| **Criterion** | `POST /query/stream` streams Server-Sent Events token-by-token. The learner uses `compare_ttft` from `src/optimization/streaming.py` to measure blocking vs. streaming time-to-first-token. |
| **Evidence required** | The `compare_ttft` output for at least 3 queries, including the percentage TTFT improvement. |

| | Exceeds Specifications |
|---|---|
| **Stretch** | Discusses when streaming is *not* worth the extra plumbing (short answers, batch contexts, programmatic consumers) and gives a concrete example. |

## Writeup Quality

| | Meets Specifications |
|---|---|
| **Criterion** | `WRITEUP.md` exists at the project root. It covers all 9 required deliverables in order, with evidence per the criteria above. It is readable cold by someone familiar with the project proposal but not the learner's specific work. |
| **Evidence required** | The writeup itself. ~1,500–3,000 words is typical; longer if including images. |

| | Exceeds Specifications |
|---|---|
| **Stretch** | Includes a "Lessons Learned" section reflecting on which layer was the hardest to extend and what they would do differently in a real production system (cost ceilings, auth, multi-tenancy). |

## Workspace Hygiene

| | Meets Specifications |
|---|---|
| **Criterion** | The repository is clean and the project still runs: (a) no real secrets committed (`.env` not tracked); (b) `make test` passes (≥195 tests); (c) `make verify` reports no failed automated checks; (d) the README's Quick Start sequence still works on a fresh clone. |
| **Evidence required** | The `make test` and `make verify` outputs in the writeup. |

## Pass/Fail Decision Reference

A submission **passes** when every required row (1–9) plus Writeup Quality and Workspace Hygiene reach Meets Specifications.

A submission is **stand-out** when, in addition to passing, at least one bonus deliverable (10 or 11) reaches Meets Specifications and at least one row reaches Exceeds Specifications.

A submission **fails** if any required row falls short. A reviewer must give specific, actionable feedback on which row failed and why, citing the criterion text above.
