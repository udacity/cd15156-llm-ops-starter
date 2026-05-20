"""CLI: tiered-routing vs single-model-baseline cost comparison.

Reads the JSONL cost log, computes what every request would have cost on
the baseline model (default: ``gpt-4o``), and reports absolute + percentage
savings from the tiered routing.
"""

import argparse
import sys
from pathlib import Path

from src.cost.tracker import load_log
from src.models import TokenUsage
from src.pricing import compute_cost


def baseline_cost(records: list[dict], baseline_model: str) -> float:
    """Recompute the cost as if every request had hit ``baseline_model``."""
    total = 0.0
    for r in records:
        total += compute_cost(
            baseline_model,
            TokenUsage(
                prompt_tokens=r["prompt_tokens"],
                completion_tokens=r["completion_tokens"],
            ),
        )
    return total


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare tiered-routing cost against a single-model baseline."
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=None,
        help="Cost log JSONL path (default: settings.cost_log_path).",
    )
    parser.add_argument(
        "--baseline",
        default="gpt-4o",
        help="Model to use as the baseline (default: gpt-4o).",
    )
    args = parser.parse_args(argv)

    records = load_log(args.log)
    if not records:
        print("No records in cost log. Run some queries first.")
        return 0

    actual = sum(r["cost_usd"] for r in records)
    baseline = baseline_cost(records, args.baseline)
    savings = baseline - actual
    pct = (savings / baseline * 100) if baseline > 0 else 0.0

    print(f"Records:           {len(records)}")
    print(f"Actual cost:       ${actual:.4f}")
    print(f"Baseline ({args.baseline}): ${baseline:.4f}")
    print(f"Savings:           ${savings:.4f} ({pct:.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
