#!/usr/bin/env python3
"""Generate deterministic synthetic two-party set inputs and a digest manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path
from typing import Sequence


GENERATOR_VERSION = "0.1"


def _identifier(namespace: str, index: int, seed: int) -> str:
    material = f"private-match-synthetic-v1:{seed}:{namespace}:{index}".encode()
    return f"pm-synth-{hashlib.sha256(material).hexdigest()[:24]}"


def build_sets(
    left_size: int,
    right_size: int,
    intersection_size: int,
    seed: int,
    left_duplicate_count: int = 0,
    right_duplicate_count: int = 0,
) -> tuple[list[str], list[str]]:
    """Build shuffled synthetic rows; sizes count distinct values before duplicates."""
    if left_size < 0 or right_size < 0 or intersection_size < 0:
        raise ValueError("set sizes and intersection size must be non-negative")
    if intersection_size > min(left_size, right_size):
        raise ValueError("intersection size cannot exceed either set size")
    if left_duplicate_count < 0 or right_duplicate_count < 0:
        raise ValueError("duplicate counts must be non-negative")
    if left_duplicate_count and left_size == 0:
        raise ValueError("left duplicates require at least one distinct left value")
    if right_duplicate_count and right_size == 0:
        raise ValueError("right duplicates require at least one distinct right value")

    common = [_identifier("common", index, seed) for index in range(intersection_size)]
    left = common + [
        _identifier("left", index, seed)
        for index in range(left_size - intersection_size)
    ]
    right = common + [
        _identifier("right", index, seed)
        for index in range(right_size - intersection_size)
    ]

    left.extend(left[index % left_size] for index in range(left_duplicate_count))
    right.extend(right[index % right_size] for index in range(right_duplicate_count))

    random.Random(seed ^ 0x4C454654).shuffle(left)
    random.Random(seed ^ 0x52494748).shuffle(right)
    return left, right


def _write_csv(path: Path, rows: Sequence[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("id",))
        writer.writerows((value,) for value in rows)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generate_case(
    output_dir: Path,
    case_id: str,
    left_size: int,
    right_size: int,
    intersection_size: int,
    seed: int,
    left_duplicate_count: int = 0,
    right_duplicate_count: int = 0,
) -> dict[str, object]:
    """Write a deterministic case and return the manifest mapping."""
    if not case_id or any(
        character not in "abcdefghijklmnopqrstuvwxyz0123456789-_"
        for character in case_id
    ):
        raise ValueError(
            "case id must use lowercase letters, digits, hyphen, or underscore"
        )

    left, right = build_sets(
        left_size,
        right_size,
        intersection_size,
        seed,
        left_duplicate_count,
        right_duplicate_count,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    left_path = output_dir / f"{case_id}-left.csv"
    right_path = output_dir / f"{case_id}-right.csv"
    manifest_path = output_dir / f"{case_id}-manifest.json"
    _write_csv(left_path, left)
    _write_csv(right_path, right)

    manifest: dict[str, object] = {
        "schema_version": "0.1",
        "generator": f"benchmarks/generate_inputs.py@{GENERATOR_VERSION}",
        "case_id": case_id,
        "seed": seed,
        "identifiers": "synthetic-only",
        "left": {
            "path": left_path.name,
            "rows": len(left),
            "distinct": len(set(left)),
            "duplicates": len(left) - len(set(left)),
            "sha256": _sha256(left_path),
        },
        "right": {
            "path": right_path.name,
            "rows": len(right),
            "distinct": len(set(right)),
            "duplicates": len(right) - len(set(right)),
            "sha256": _sha256(right_path),
        },
        "expected": {
            "byte_exact_distinct_intersection": len(set(left) & set(right)),
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--left-size", type=int, required=True)
    parser.add_argument("--right-size", type=int, required=True)
    parser.add_argument("--intersection-size", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--left-duplicate-count", type=int, default=0)
    parser.add_argument("--right-duplicate-count", type=int, default=0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest = generate_case(
        output_dir=args.output_dir.resolve(),
        case_id=args.case_id,
        left_size=args.left_size,
        right_size=args.right_size,
        intersection_size=args.intersection_size,
        seed=args.seed,
        left_duplicate_count=args.left_duplicate_count,
        right_duplicate_count=args.right_duplicate_count,
    )
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
