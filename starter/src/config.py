"""Application settings loaded from environment variables."""

from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env into os.environ early so libraries that read environment
# variables directly — RAGAS's internal OpenAI() client, the openai
# SDK's base-URL discovery, anything bypassing Settings — see the
# project's keys without needing a manual `set -a; source .env` step.
# pydantic-settings populates Settings from .env but does NOT export
# back to the environment, so callers that don't go through Settings
# would otherwise be blind to the .env values.
#
# override=False (the default) — already-set env vars win, so the
# explicit `set -a; source .env` workflow keeps working during the
# transition.
load_dotenv()


class Settings(BaseSettings):
    """Central configuration — all values come from .env or the environment."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # API keys
    openai_api_key: str = ""
    # Empty string means "use the SDK default (https://api.openai.com/v1)".
    # Set to https://openai.vocareum.com/v1 when running with a Vocareum key.
    openai_base_url: str = ""

    # Chroma — embedded persistent store (no Docker). Files are written
    # under this path; safe to delete and reload via `make load-data`.
    chroma_path: str = "data/chroma"

    # Tracing — "phoenix" runs an embedded Arize Phoenix UI at the host/port
    # below. "none" disables tracing entirely (useful for tests and CI).
    tracing_backend: Literal["phoenix", "none"] = "phoenix"

    # Phoenix (used when tracing_backend == "phoenix")
    phoenix_embedded: bool = True
    phoenix_host: str = "0.0.0.0"
    phoenix_port: int = 6006
    phoenix_working_dir: str = "data/phoenix"
    phoenix_project_name: str = "llm-ops-capstone"

    # Models
    model_complex: str = "gpt-4o"
    model_simple: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # Application
    confidence_threshold: float = 0.7
    cost_log_path: str = "data/cost_log.jsonl"

    # Guardrails — output-side
    # FactualConsistency NLI scanner's minimum entailment score.
    #
    # **Dormant under the current default scanner.** The live `/query`
    # route uses the LLM-judge scanner at
    # `src.guardrails.llm_judge.output_guards` (FPR=0.00, TPR=1.00 on
    # the golden cohort — see
    # docs/verifications/2026-04-30-llm-judge-vs-nli-comparison.md).
    # This setting only takes effect if the operator manually swaps the
    # `check_hallucination` import in `src/gateway/routes.py` back to
    # `src.guardrails.llm_guard.output_guards`. Kept in `Settings`
    # because REQ-018 / PR #27 introduced it as a documented config
    # surface; removing it would break any operator who pinned a value
    # in their `.env`.
    #
    # Historical context: the value `0.05` was empirically tuned on
    # 2026-04-29 via `make tune-factuality`. NLI on paragraph-level RAG
    # output has structurally high false-positive rates (40% FPR at
    # this threshold). That's why the default scanner was swapped — see
    # docs/verifications/2026-04-29-factuality-threshold-tuning.md for
    # the original calibration data.
    guardrails_factuality_min_score: float = 0.05


settings = Settings()
