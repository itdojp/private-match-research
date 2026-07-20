#!/usr/bin/env python3
"""Generate the public competitor index from structured YAML records."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import os
import unicodedata
from pathlib import Path
from typing import Any, Iterable

import yaml

if __package__:
    from scripts.direct_designation import direct_designation_approval_errors
else:
    from direct_designation import (  # type: ignore[import-not-found]
        direct_designation_approval_errors,
    )


CLASS_ORDER = ("direct", "adjacent", "substitute", "building-block", "potential")

# Encode syntax-significant characters as HTML character references. CommonMark
# renders the original character while the generated source cannot open a link,
# table column, inline HTML tag, emphasis span, or code span from identity data.
_MARKDOWN_INLINE_ENTITIES = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\\": "&#92;",
    "|": "&#124;",
    "[": "&#91;",
    "]": "&#93;",
    "*": "&#42;",
    "_": "&#95;",
    "`": "&#96;",
    "~": "&#126;",
}


def _require_direct_designation_approval(path: Path, record: dict[str, Any]) -> None:
    errors = direct_designation_approval_errors(record)
    if errors:
        raise ValueError(f"{path}: direct designation approval: {'; '.join(errors)}")


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

        _require_direct_designation_approval(path, record)

        if key in identities:
            raise ValueError(
                f"{path}: duplicate organization/product also present in {identities[key]}"
            )
        identities[key] = path
        records.append((path, record))

    return records


def _date_text(value: Any) -> str:
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    return str(value)


def _normalize_inline_text(value: Any) -> str:
    """Normalize non-rendering code points without silently deleting input."""
    text = str(value).replace("\r\n", "\n").replace("\r", "\n")
    normalized: list[str] = []
    for character in text:
        category = unicodedata.category(character)
        if category in {"Cc", "Zl", "Zp"}:
            normalized.append(" ")
        elif category == "Cs":
            normalized.append("\N{REPLACEMENT CHARACTER}")
        else:
            normalized.append(character)
    return "".join(normalized)


def _escape_table_cell(value: Any) -> str:
    """Render identity text as literal content inside one Markdown table cell."""
    normalized = _normalize_inline_text(value)
    return "".join(
        _MARKDOWN_INLINE_ENTITIES.get(character, character) for character in normalized
    )


def _escape_link_label(value: Any) -> str:
    """Render identity text without permitting it to terminate a Markdown link label."""
    normalized = _normalize_inline_text(value)
    return "".join(
        _MARKDOWN_INLINE_ENTITIES.get(character, character) for character in normalized
    )


def render_index(
    records: Iterable[tuple[Path, dict[str, Any]]], output_path: Path
) -> str:
    rows = list(records)
    for path, record in rows:
        _require_direct_designation_approval(path, record)
    counts = collections.Counter(
        record["classification"]["class"] for _, record in rows
    )
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
        "- Human decision boundary: a `direct` record is rendered only with its own",
        "  `authorized-itdo-human` approval and concrete GitHub evidence reference.",
        "  Automation checks the reference structure, not the human author's authority",
        "  or the substantive scope of the approval.",
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
            CLASS_ORDER.index(classification)
            if classification in CLASS_ORDER
            else len(CLASS_ORDER),
            str(record["identity"]["organization"]).casefold(),
            str(record["identity"]["product"]).casefold(),
        )

    for path, record in sorted(rows, key=sort_key):
        identity = record["identity"]
        classification = record["classification"]
        observation = record["observation"]
        relative_record = Path(os.path.relpath(path, start=output_path.parent))
        product = (
            f"[{_escape_link_label(identity['product'])}]({relative_record.as_posix()})"
        )
        pricing = "yes" if record["market"]["pricing"]["public"] else "no / unknown"
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_table_cell(identity["organization"]),
                    product,
                    f"`{_escape_table_cell(classification['class'])}`",
                    _escape_table_cell(classification["confidence"]),
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
    parser.add_argument(
        "--output", type=Path, default=Path("landscape/competitor-index.md")
    )
    parser.add_argument("--minimum-count", type=int, default=25)
    parser.add_argument(
        "--check", action="store_true", help="Fail if the committed index is stale"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    records_dir = (
        args.records_dir if args.records_dir.is_absolute() else root / args.records_dir
    )
    output_path = args.output if args.output.is_absolute() else root / args.output
    records = load_records(records_dir)
    if len(records) < args.minimum_count:
        raise SystemExit(
            f"competitor-index: expected at least {args.minimum_count} records, found {len(records)}"
        )
    rendered = render_index(records, output_path)

    if args.check:
        current = (
            output_path.read_text(encoding="utf-8") if output_path.exists() else ""
        )
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
