# Troubleshooting: Hints and Common Pitfalls

Skim this page **before you start**. Most learners hit at least one of
these. Then come back to it per task: each task in
[`INSTRUCTIONS.md §6`](INSTRUCTIONS.md#6-your-tasks) links to the
specific items below that tend to bite on that task.

Nothing here is a code bug in the starter. These are the operational
surprises that show up when you run a real LLM stack, plus how to tell
"working as designed" apart from "actually broken."

## Contents

- [Setup and budget](#setup-and-budget)
- [Per-task gotchas](#per-task-gotchas)
- [Dev and testing](#dev-and-testing)

---

## Setup and budget

### Vocareum returns Insufficient budget available

`BadRequestError: Insufficient budget available. Reason: Exceeded
budget 10 > X.X`. Your Vocareum API key has a $10 lifetime cap and
you've consumed it. This is **not** a code bug — the proxy returns a
400 before any tokens are billed, so the failed call costs you nothing.
Contact course support for a top-up. While you wait, you can continue
any work that doesn't make LLM calls (writing your WRITEUP, running
`make test`, examining traces already in Phoenix). Reduce future burn
by treating `make eval-topk-sweep` (~$0.10) as a once-per-submission
deliverable and not running `make eval` (~$0.03) in a loop while
iterating.

### First LLM Guard call hangs for several minutes

The library downloads ~400 MB of HuggingFace transformer models
(DeBERTa for injection, Presidio NER for PII, BanTopics zero-shot, NLI
for factuality) on first use. Pre-cache them with
`make install-guardrails-models`.

## Per-task gotchas

### make load-data complains about an empty Chroma

Chroma runs in-process via `chromadb.PersistentClient`. If
`data/chroma/` is missing or unwritable, `make load-data` fails. Delete
the directory and re-run to reset.

### make eval prints TimeoutError lines

`make eval` / `make eval-topk-sweep` prints `TimeoutError` lines. The
Vocareum OpenAI proxy is shared, and tail latencies of 30–60 s for a
single request are common under the parallelism RAGAS uses. RAGAS
retries each timed-out call transparently, so a noisy log with dozens
of `TimeoutError` warnings still produces complete metrics — one
example-solutions run logged ~43 timeouts during the top-k sweep and
still emitted a clean comparison table. Watch the final summary, not
the intermediate warnings.

On the Workspace (GPU) every cell of the sweep should come back with a
real number, including `context_precision` at `top_k=10`. For this
30-product catalog it lands in roughly the 0.72–0.78 band, so a value
there is the healthy result, not an error. A `NaN` is not the expected
result and does not mean the metric is zero. It means a judge call
never returned even after retries, usually because the pipeline was
slow enough to starve its time budget (heavy proxy contention, or
running the local guard and embedding models on CPU instead of the
GPU). If you hit one, re-run that single `top_k` with
`EVAL_MAX_WORKERS=1` and it should fill in.

### The classifier falls back to complex on bad JSON

That's the safer (more capable, more expensive) default. If your
routing decisions look skewed toward `gpt-4o`, check whether the
classifier is actually returning JSON.

### Brand names flagged as pii_redacted person

Asking about something like the Selkirk AMPED S2 returns a normal
answer **and** `blocked_by: "pii_redacted: person"` in the same
response. This is annotation, not a block — the request flowed through,
the answer is real, and you should treat the response as successful.
Presidio's NER model flags single capitalized tokens that match
person-name distributions; brand names like "Selkirk", "Joola", and
"Diadem" hit this pattern. The `/query` route calls `_annotate_pii`
(not `_safe_response`) for PII detections, so the original answer is
preserved. If the annotation becomes noisy in your own deployment, you
can either drop `PERSON` from Presidio's entity list for product
domains or add a brand-name allowlist to `Anonymize`'s vault — both
follow-up exercises beyond the core curriculum.

### Phoenix dashboard is not reachable in your browser

Some learner workspaces don't expose port 6006. You can still satisfy
rubric §7: run `make show-traces` to get the same trace data as a
markdown export. Include the markdown in your writeup instead of a
screenshot.

### Phoenix UI shows no traces or an empty default project

The app registers spans under the **`llm-ops-capstone`** project, not
`default`. Use the project picker in the top-left of the Phoenix
dashboard to switch. If you also see stale projects like
`udacity-llm-ops` or a typo'd `llm-ops-captone` in the dropdown, those
are remnants from prior runs persisted in `data/phoenix/` and can be
ignored — your current traces are in `llm-ops-capstone`.

### Phoenix UI binds to all interfaces by default

Phoenix binds to `0.0.0.0:6006` by default. Fine on a single-user GCP
container, but on a multi-tenant or internet-reachable host, override
`PHOENIX_HOST=127.0.0.1` (or put it behind an authenticating reverse
proxy) before exposing the box.

### Cost-log file grows large

Each query is a JSON line. After a 50-query run you'll have ~12 KB of
log; that's normal. Don't delete the log between Task 8 and Task 9 —
they share it.

## Dev and testing

### Tests assume the conftest mocks all external SDKs

Don't import any external SDK at module-import time outside `src/` —
`tests/conftest.py` patches the constructors of `chromadb`, `openai`,
`phoenix`, and `llm_guard` scanners before any test runs.

### Forward-dependency rule

Don't add an `import` from a "later" package to an "earlier" one. The
fitness function in `tests/integration/test_dependency_graph.py` will
fail.
