"""Run guardrail patterns against the live `/query` endpoint and print a §6-ready table.

Reads `INJECTION_PATTERNS` and `PII_PATTERNS` at call time from
`src.guardrails.input_guards` (so additions take effect on the next run
without reinstalling), then for each pattern POSTs the matching `Fire`
and `No-fire` questions from `data/guardrails-examples.md` to
`http://localhost:8080/query`. The output is a single markdown table
sized for direct paste into `WRITEUP.template.md` §6.

Usage:
    make serve             # in another terminal
    make demo-guardrails   # prints the markdown table

Patterns without a matching example in the file render as a `(no
example — see guardrails-examples.md)` row so the learner knows where
to add one.
"""

import re
import sys
from pathlib import Path

import httpx

EXAMPLES_PATH = Path("data/guardrails-examples.md")
HEALTH_URL = "http://localhost:8080/health"
QUERY_URL = "http://localhost:8080/query"


def _parse_examples(text: str) -> dict[str, dict[str, str]]:
    """Map regex source string → {label, fire, nofire}.

    The parser walks the file line by line, tracking the most recent
    `### Label` header and accumulating the three required field lines
    (`Regex (source)`, `Fire`, `No-fire`). When all three are present an
    entry is recorded keyed by the regex source string.
    """
    field_re = {
        "regex": re.compile(r"\s*-\s*\*\*Regex \(source\):\*\*\s*`(.+?)`\s*$"),
        "fire": re.compile(r"\s*-\s*\*\*Fire:\*\*\s*`(.+?)`\s*$"),
        "nofire": re.compile(r"\s*-\s*\*\*No-fire:\*\*\s*`(.+?)`\s*$"),
    }
    header_re = re.compile(r"^#{2,4}\s+(.+?)\s*$")

    examples: dict[str, dict[str, str]] = {}
    label = ""
    pending: dict[str, str] = {}
    in_fence = False

    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if m := header_re.match(line):
            label = m.group(1)
            pending = {}
            continue
        for key, pat in field_re.items():
            if m := pat.match(line):
                pending[key] = m.group(1)
                break
        if {"regex", "fire", "nofire"} <= pending.keys():
            examples[pending["regex"]] = {
                "label": label,
                "fire": pending["fire"],
                "nofire": pending["nofire"],
            }
            pending = {}
    return examples


def _preflight() -> None:
    """Verify `/health` is reachable; exit with a clear message otherwise."""
    try:
        httpx.get(HEALTH_URL, timeout=5.0).raise_for_status()
    except Exception as exc:  # noqa: BLE001 — surface every failure mode the same way
        print(
            f"Could not reach {HEALTH_URL}. Start the server in another "
            f"terminal with `make serve` and try again. ({exc.__class__.__name__})",
            file=sys.stderr,
        )
        sys.exit(1)


def _call_query(question: str) -> str:
    """POST one question and return its `blocked_by` (or `null` / error tag)."""
    try:
        r = httpx.post(QUERY_URL, json={"question": question}, timeout=60.0)
        r.raise_for_status()
        return r.json().get("blocked_by") or "null"
    except httpx.HTTPStatusError as exc:
        return f"HTTP {exc.response.status_code}"
    except httpx.RequestError as exc:
        return f"ERROR {exc.__class__.__name__}"


def _md_escape(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ").strip()


def _render_table(rows: list[dict[str, str]]) -> str:
    header = (
        "| Type | Pattern | Fire question | Fire `blocked_by` | "
        "No-fire question | No-fire `blocked_by` |"
    )
    sep = "|------|---------|---------------|-------------------|------------------|----------------------|"
    lines = [header, sep]
    for r in rows:
        lines.append(
            f"| {r['type']} | {_md_escape(r['label'])} "
            f"| {_md_escape(r['fire_q'])} | `{_md_escape(r['fire_resp'])}` "
            f"| {_md_escape(r['nofire_q'])} | `{_md_escape(r['nofire_resp'])}` |"
        )
    return "\n".join(lines)


def _row_for(kind: str, regex_src: str, fallback_label: str, examples: dict) -> dict[str, str]:
    ex = examples.get(regex_src)
    if not ex:
        return {
            "type": kind,
            "label": fallback_label,
            "fire_q": "(no example — see guardrails-examples.md)",
            "fire_resp": "—",
            "nofire_q": "—",
            "nofire_resp": "—",
        }
    print(f"  -> {kind}: {ex['label']}", file=sys.stderr)
    return {
        "type": kind,
        "label": ex["label"],
        "fire_q": ex["fire"],
        "fire_resp": _call_query(ex["fire"]),
        "nofire_q": ex["nofire"],
        "nofire_resp": _call_query(ex["nofire"]),
    }


def main() -> int:
    _preflight()

    # Imported inside main() so each invocation re-evaluates the module —
    # any new pattern a learner adds to input_guards.py is picked up
    # without reinstalling or restarting anything.
    from src.guardrails.input_guards import INJECTION_PATTERNS, PII_PATTERNS

    if not EXAMPLES_PATH.exists():
        print(f"Examples file not found: {EXAMPLES_PATH}", file=sys.stderr)
        return 1

    examples = _parse_examples(EXAMPLES_PATH.read_text())
    print(
        f"Demoing {len(INJECTION_PATTERNS)} injection + {len(PII_PATTERNS)} PII "
        f"patterns against {QUERY_URL} ...",
        file=sys.stderr,
    )

    rows: list[dict[str, str]] = []
    for pattern in INJECTION_PATTERNS:
        rows.append(_row_for("injection", pattern.pattern, pattern.pattern, examples))
    for kind, pattern in PII_PATTERNS.items():
        rows.append(_row_for("pii", pattern.pattern, kind, examples))

    print(_render_table(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
