# WRITEUP — Production LLM FAQ Service

> **How to use this template.** Copy this file to `WRITEUP.md` (drop
> the `.template`) and fill in each section with the evidence the
> rubric requires. Keep evidence inline (curl outputs, screenshots,
> log excerpts) — a reviewer should be able to grade your submission
> from this file alone.
>
> **Recommended path:** with `make serve` running in another terminal,
> run `make harvest-evidence` to generate `WRITEUP-draft.md` with §1–§11
> mostly pre-populated. Copy that draft into `WRITEUP.md` and fill in
> the four `<!-- TODO: learner — ... -->` analysis blocks (the
> threshold proposal in §5, the slowest-step analysis in §7, the
> cost-at-scale paragraph in §9, plus the §1 curl using one of YOUR
> new products). The harvester captures pure-evidence sections; the
> writing remains yours.
>
> Aim for ~1,500–3,000 words. Longer is fine if you include images.
> Each `## Deliverable N` section maps to one row of
> [`rubric.md`](rubric.md).

## Setup snapshot

- Python: `python --version`
- Branch / commit: `git rev-parse --short HEAD` (the commit your
  reviewer should clone)
- Test suite: `make test` (paste the final line — should be ≥195
  passing)
- Verify: `make verify` (paste the "Automated: X passed, 0 failed"
  line)

## Substitutions from the proposal

The starter ships with three substitutions vs. the proposal text. If
you used the as-shipped stack (the default), just say so. If you swapped
back to the proposal stack (Redis Stack / Langfuse / Guardrails AI),
explain what you changed and why.

| Layer | Proposal | Starter default | Your choice |
|-------|----------|------------------|--------------|
| Cache | Redis Stack | Chroma collection | _your choice_ |
| Tracing | Langfuse Cloud | Phoenix in-process | _your choice_ |
| Guardrails | Guardrails AI | LLM Guard + LLM judge | _your choice_ |

---

## Deliverable 1 — Vector Database Populated

> **Rubric:** at least 5 new product JSONs in `data/products/` (or proof
> of equivalent ingestion through `data/inbox/`). Output of one `POST
> /query` showing retrieval includes a new product.

- New products added (list filenames or `doc_id`s):
- One curl response showing retrieval includes a new product:

```json
// paste POST /query response with `sources[*].doc_id` matching one of your additions
```

## Deliverable 2 — RAG Pipeline With Structured Output

> **Rubric:** `POST /query` returns a `QueryResponse` with all fields
> populated. RAGAS scores from at least one `make eval` run.

- One representative `POST /query` response showing every field
  (`answer`, `sources`, `confidence`, `model`, `tokens`, `cost_usd`,
  `cached`, `trace_id`, `blocked_by`):

```json
// paste here
```

- RAGAS aggregate metrics from `make eval`:

```
faithfulness:      ?.???
answer_relevancy:  ?.???
context_recall:    ?.???
context_precision: ?.???
```

## Deliverable 3 — LLM Gateway With Tiered Routing

> **Rubric:** at least 4 queries logged showing the `model` field
> varies by classification.

- Four queries with their `model` field showing the split between
  `gpt-4o-mini` and `gpt-4o`:

| Query | model | query_type |
|-------|-------|------------|
| ... | gpt-4o-mini | simple |
| ... | gpt-4o-mini | simple |
| ... | gpt-4o | complex |
| ... | gpt-4o | complex |

(Pull these from `data/cost_log.jsonl` or from `POST /query`
responses.)

## Deliverable 4 — Automated Data Ingestion (File Watcher)

> **Rubric:** two artifacts: a successful ingestion and a quarantined
> failure with `<name>.error.txt`.

- Successful ingestion: drop a valid JSON in `data/inbox/`, then run a
  `POST /query` whose answer cites the new product. Paste both files
  / responses.
- Quarantined failure: drop a malformed JSON, then paste the
  `data/inbox/failed/<name>.error.txt` content.

## Deliverable 5 — Automated Evaluation Suite

> **Rubric:** `make eval` produces the four RAGAS metrics. Propose a
> regression threshold for at least one metric and justify it.

- Aggregate metrics (paste again from D2 if you only ran one eval):

```
// paste
```

- **Proposed regression threshold** for one metric:
  - Metric:
  - Threshold:
  - Justification (one paragraph): _why this threshold? what would
    cause it to be violated? what's the action when it is?_

## Deliverable 6 — Input and Output Guardrails

> **Rubric:** add at least 3 new injection patterns to
> `INJECTION_PATTERNS`, OR add a new sensitive-data type to
> `PII_PATTERNS`/`PII_REDACTIONS`. Show paired curls per pattern: one
> that triggers it (`blocked_by` populated) and one that should not.

- Patterns added (list with one-line description each):
- Paired curl examples per added pattern:

```bash
# Pattern X — should fire
curl -X POST http://localhost:8080/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"<input that should trigger>"}' | jq .blocked_by
# Expected: "prompt_injection: ..." or "pii_redacted: ..."

# Pattern X — should NOT fire
curl -X POST http://localhost:8080/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"<legitimate question>"}' | jq .blocked_by
# Expected: null
```

## Deliverable 7 — Distributed Tracing

> **Rubric:** at least 10 queries in Phoenix, identify the slowest
> step.

- Either a Phoenix screenshot (with one trace expanded) **or** the
  `make show-traces` markdown output for ≥10 queries.
- Slowest step in your traces:
  - Step name:
  - Latency:
  - One sentence on why it's the slowest:

## Deliverable 8 — Cost Monitoring Dashboard

> **Rubric:** `data/cost_log.jsonl` with ≥50 entries. Screenshot of
> `GET /cost-dashboard` plus a 5-line excerpt.

- Total entries: `wc -l data/cost_log.jsonl`
- 5-line excerpt:

```
// paste 5 lines from data/cost_log.jsonl
```

- Screenshot or paste of `GET /cost-dashboard` output:

## Deliverable 9 — Cost Savings Analysis (Tiered vs. Baseline)

> **Rubric:** comparison of actual cost (tiered) vs. single-model
> baseline using `scripts/cost_report.py`. Report absolute savings and
> percentage.

- `scripts/cost_report.py` output:

```
// paste
```

- Absolute savings: $___
- Percentage savings: ___%

---

## Bonus 10 — Semantic Cache

> **Rubric:** six paraphrased queries showing ≥3 cache hits, plus the
> cache contents.

- Six paraphrased queries with their `cached` field per response:
- `chromadb.PersistentClient(path='data/chroma').get_or_create_collection('cache').count()`:
- `.get(limit=10)['metadatas']` excerpt:

## Bonus 11 — Latency Optimization via Streaming

> **Rubric:** `compare_ttft` output for at least 3 queries with TTFT
> improvement percentage.

```
// paste compare_ttft output
```

---

## Lessons learned (optional, exceeds specifications)

> Reflect on which layer was the hardest to extend and what you would
> do differently in a real production system (cost ceilings, auth,
> multi-tenancy, etc.). One or two paragraphs.
