#!/usr/bin/env python3
"""Generate the public competitor index from structured YAML records."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import os
from pathlib import Path
from typing import Any, Iterable

import yaml


CLASS_ORDER = ("direct", "adjacent", "substitute", "building-block", "potential")


def load_records(records_dir: Path) -> list[tuple[Path, dict[str, Any]]]:
    """Load competitor records and reject ambiguous index identities."""
    records: list[tuple[Path, dict[str, Any]]] = []
    identities: dict[tuple[str, str], Path] = {}

    for path in sorted((*records_dir.glob("*.yaml"), *records_dir.glob("*.yml"))):
        with path.open("r", encoding="utf-8") as handle:
            record = yaml.safe_load(handle)
        if not isinstance(record, dict) or record.get("record_type") != "competitor":
            raise ValueError(f"{path}: expected a competitor record")

        try:
            identity = record["identity"]
            key = (str(identity["organization"]), str(identity["product"]))
            record["classification"]["class"]
            record["classification"]["confidence"]
            record["observation"]["last_verified_at"]
            record["observation"]["next_review_at"]
            record["market"]["pricing"]["public"]
        except (KeyError, TypeError) as exc:
            raise ValueError(f"{path}: missing index field {exc}") from exc

        if key in identities:
            raise ValueError(f"{path}: duplicate organization/product also present in {identities[key]}")
        identities[key] = path
        records.append((path, record))

    return records


def _date_text(value: Any) -> str:
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    return str(value)


def _escape_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_index(records: Iterable[tuple[Path, dict[str, Any]]], output_path: Path) -> str:
    rows = list(records)
    counts = collections.Counter(record["classification"]["class"] for _, record in rows)
    latest_verification = max(
        (_date_text(record["observation"]["last_verified_at"]) for _, record in rows),
        default="unknown",
    )

    lines = [
        "# Structured Competitor Index",
        "",
        "This index is generated from the public YAML records under `records/competitors/`.",
        "Regenerate it with `python scripts/generate_competitor_index.py`.",
        "",
        f"- Records: {len(rows)}",
        f"- Latest source verification date: {latest_verification}",
        "- Classification boundary: technology similarity alone does not establish",
        "  direct competition.",
        "- Human decision boundary: no `direct` designation is asserted by this index",
        "  without explicit approval.",
        "",
        "## Classification summary",
        "",
        "| Classification | Records |",
        "| --- | ---: |",
    ]
    lines.extend(f"| `{name}` | {counts[name]} |" for name in CLASS_ORDER)
    lines.extend(
        [
            "",
            "A zero count does not establish that a category has no market participants;",
            "it only describes the current reviewed records.",
            "",
            "## Records",
            "",
            "| Organization | Product | Class | Confidence | Verified | Review | Pricing |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )

    def sort_key(item: tuple[Path, dict[str, Any]]) -> tuple[int, str, str]:
        _, record = item
        classification = record["classification"]["class"]
        return (
            CLASS_ORDER.index(classification) if classification in CLASS_ORDER else len(CLASS_ORDER),
            str(record["identity"]["organization"]).casefold(),
            str(record["identity"]["product"]).casefold(),
        )

    for path, record in sorted(rows, key=sort_key):
        identity = record["identity"]
        classification = record["classification"]
        observation = record["observation"]
        relative_record = Path(os.path.relpath(path, start=output_path.parent))
        product = f"[{_escape_cell(identity['product'])}]({relative_record.as_posix()})"
        pricing = "yes" if record["market"]["pricing"]["public"] else "no / unknown"
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_cell(identity["organization"]),
                    product,
                    f"`{_escape_cell(classification['class'])}`",
                    _escape_cell(classification["confidence"]),
                    _date_text(observation["last_verified_at"]),
                    _date_text(observation["next_review_at"]),
                    pricing,
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Evidence boundary",
            "",
            "Each linked record separates vendor-published facts, research inferences,",
            "hypotheses, and unknowns. A record does not independently validate a vendor's",
            "performance, privacy, security, or compliance claims.",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--records-dir", type=Path, default=Path("records/competitors"))
    parser.add_argument("--output", type=Path, default=Path("landscape/competitor-index.md"))
    parser.add_argument("--minimum-count", type=int, default=25)
    parser.add_argument("--check", action="store_true", help="Fail if the committed index is stale")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    records_dir = args.records_dir if args.records_dir.is_absolute() else root / args.records_dir
    output_path = args.output if args.output.is_absolute() else root / args.output
    records = load_records(records_dir)
    if len(records) < args.minimum_count:
        raise SystemExit(f"competitor-index: expected at least {args.minimum_count} records, found {len(records)}")
    rendered = render_index(records, output_path)

    if args.check:
        current = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
        if current != rendered:
            print(f"competitor-index: stale or missing: {output_path}")
            return 1
        print(f"competitor-index: current records={len(records)} output={output_path}")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    print(f"competitor-index: wrote records={len(records)} output={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
