#!/usr/bin/env python3
"""Validate Issue #3 substitute coverage and comparison artifacts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml


REQUIRED_CLASSES = {
    "nda-csv-comparison.yaml": "nda-csv",
    "studenttracker-trusted-matching.yaml": "trusted-third-party",
    "deloitte-due-diligence.yaml": "professional-diligence",
    "salesforce-identity-resolution.yaml": "cdp-identity",
    "snowflake-contractual-data-sharing.yaml": "warehouse-contract",
    "internal-conflict-check.yaml": "manual-conflict",
    "sampled-deidentified-exchange.yaml": "sampled-disclosure",
}

REQUIRED_COMPARISON_COLUMNS = (
    "Setup time",
    "Trust",
    "Disclosure",
    "Output",
    "Cost model",
    "Evidentiary value",
    "When superior",
)

REQUIRED_PATHS = (
    "market.buyer",
    "market.user",
    "market.trigger",
    "market.pricing.model",
    "market.deployment_lead_time",
    "product.outputs",
    "product.workflow",
    "product.prerequisites",
    "product.data_movement",
    "privacy_and_security.trust_model",
    "privacy_and_security.raw_data_access",
    "privacy_and_security.audit_and_assurance",
    "assessment.strengths",
    "assessment.limitations_or_unknowns",
    "assessment.implications_for_private_match",
    "assessment.claim_types.facts",
    "assessment.claim_types.inferences",
    "assessment.claim_types.hypotheses",
    "sources.primary",
)


def _read_path(record: dict[str, Any], dotted_path: str) -> Any:
    value: Any = record
    for segment in dotted_path.split("."):
        if not isinstance(value, dict) or segment not in value:
            return None
        value = value[segment]
    return value


def load_landscape(root: Path) -> tuple[dict[str, dict[str, Any]], str]:
    records_dir = root / "records" / "substitutes"
    records: dict[str, dict[str, Any]] = {}
    if records_dir.exists():
        for path in sorted((*records_dir.glob("*.yaml"), *records_dir.glob("*.yml"))):
            with path.open("r", encoding="utf-8") as handle:
                parsed = yaml.safe_load(handle)
            records[path.name] = parsed
    survey_path = root / "landscape" / "substitutes" / "README.md"
    survey = survey_path.read_text(encoding="utf-8") if survey_path.exists() else ""
    return records, survey


def validate_content(records: dict[str, dict[str, Any]], survey: str) -> list[str]:
    errors: list[str] = []
    if len(records) < 5:
        errors.append(f"expected at least 5 substitute records, found {len(records)}")

    for filename, class_id in REQUIRED_CLASSES.items():
        if filename not in records:
            errors.append(f"missing required substitute class {class_id}: {filename}")
        if f"<!-- substitute:{class_id} -->" not in survey:
            errors.append(f"survey missing class marker: {class_id}")

    identities: dict[tuple[str, str], str] = {}
    for filename, record in records.items():
        if not isinstance(record, dict):
            errors.append(f"{filename}: record must be a YAML mapping")
            continue
        if record.get("record_type") != "competitor":
            errors.append(f"{filename}: record_type must be competitor")
        if _read_path(record, "classification.class") != "substitute":
            errors.append(f"{filename}: classification.class must be substitute")

        organization = _read_path(record, "identity.organization")
        product = _read_path(record, "identity.product")
        if organization and product:
            key = (str(organization), str(product))
            if key in identities:
                errors.append(f"{filename}: duplicate identity also present in {identities[key]}")
            identities[key] = filename

        for dotted_path in REQUIRED_PATHS:
            value = _read_path(record, dotted_path)
            if value is None or value == "" or value == []:
                errors.append(f"{filename}: missing comparison evidence at {dotted_path}")

    for column in REQUIRED_COMPARISON_COLUMNS:
        if f"| {column} " not in survey and f"| {column} |" not in survey:
            errors.append(f"survey comparison table missing column: {column}")

    disconfirming_tests = set(re.findall(r"\bDCT-[0-9]{3}\b", survey))
    if len(disconfirming_tests) < 3:
        errors.append(f"expected at least 3 disconfirming tests, found {len(disconfirming_tests)}")
    if "No interview-derived information is included" not in survey:
        errors.append("survey must state the interview/publication boundary")
    if "not legal evidence" not in survey:
        errors.append("survey must scope the evidentiary-value comparison")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    records, survey = load_landscape(root)
    errors = validate_content(records, survey)
    if errors:
        for error in errors:
            print(f"substitute-landscape: error: {error}")
        return 1
    disconfirming_test_count = len(set(re.findall(r"\bDCT-[0-9]{3}\b", survey)))
    print(
        "substitute-landscape: "
        f"records={len(records)} classes={len(REQUIRED_CLASSES)} "
        f"disconfirming_tests={disconfirming_test_count} errors=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
