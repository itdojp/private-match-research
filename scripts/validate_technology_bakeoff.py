#!/usr/bin/env python3
"""Validate Research Issue #4 records, experiment selection, and reproducibility plan."""

from __future__ import annotations

import argparse
import csv
import json
import unicodedata
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

import yaml
from jsonschema import Draft202012Validator


REQUIRED_RECORDS = {
    "secretflow-psi.yaml": "secretflow-psi",
    "rfc9497-circl-voprf.yaml": "rfc9497-circl-voprf",
    "meta-private-id.yaml": "meta-private-id",
    "microsoft-apsi.yaml": "microsoft-apsi",
    "google-private-join-compute.yaml": "google-private-join-compute",
    "mp-spdz.yaml": "mp-spdz",
    "aws-nitro-enclaves.yaml": "aws-nitro-enclaves",
    "gnark-zkp.yaml": "gnark-zkp",
    "aws-c3r.yaml": "aws-c3r",
}

REQUIRED_CATEGORIES = {"PSI", "OPRF", "MPC", "TEE", "ZKP"}
REQUIRED_EXPERIMENTS = {f"EXP-{number:03d}" for number in range(1, 9)}
RESULT_STATUSES = {"pass", "fail", "skip", "unsupported", "timeout", "tool-error"}
PLAN_STATUSES = RESULT_STATUSES | {"not-run"}
REQUIRED_TRACKS = {"TRACK-PSI", "TRACK-VOPRF", "TRACK-TEE"}
REPOSITORY_PATH_ERROR = "repository-path"
RESULT_SOURCE_REVISION_ERROR = "result-source-revision"
DUPLICATE_ID_ERROR = "duplicate-id"

REQUIRED_RECORD_PATHS = (
    "observation.observed_at",
    "observation.last_verified_at",
    "observation.next_review_at",
    "problem_fit.supported_results",
    "problem_fit.party_model",
    "problem_fit.data_profiles",
    "problem_fit.target_use_cases",
    "problem_fit.non_fit",
    "security.security_model",
    "security.cryptographic_assumptions",
    "security.trusted_components",
    "security.input_authenticity",
    "security.omission_resistance",
    "security.replay_and_session_binding",
    "security.metadata_leakage",
    "security.repeated_query_risk",
    "security.known_attacks_or_limitations",
    "engineering.computation_profile",
    "engineering.communication_profile",
    "engineering.operational_complexity",
    "engineering.key_or_setup_requirements",
    "assurance.external_audits",
    "assurance.interoperability",
    "project_health.license",
    "project_health.patent_considerations",
    "project_health.latest_release",
    "project_health.maintenance_status",
    "assessment.limitations_or_unknowns",
    "assessment.recommended_experiments",
    "assessment.private_match_fit",
    "assessment.confidence",
    "sources.primary",
)

REQUIRED_COMPARISON_COLUMNS = (
    "Model and trusted components",
    "Low-entropy identifiers",
    "Input omission / malicious input",
    "Repeated-query risk",
    "Metadata leakage",
    "Result symmetry",
    "Balanced / unbalanced fit",
    "Computation / communication / operational cost",
    "Setup, keys, attestation, deployment",
    "Maintenance / license",
    "External review and interoperability",
    "Experiment decision",
)


def _read_path(record: dict[str, Any], dotted_path: str) -> Any:
    value: Any = record
    for segment in dotted_path.split("."):
        if not isinstance(value, dict) or segment not in value:
            return None
        value = value[segment]
    return value


def _load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_artifacts(
    root: Path,
) -> tuple[dict[str, dict[str, Any]], str, str, dict[str, Any]]:
    records_dir = root / "records" / "technologies"
    records: dict[str, dict[str, Any]] = {}
    if records_dir.exists():
        for path in sorted((*records_dir.glob("*.yaml"), *records_dir.glob("*.yml"))):
            records[path.name] = _load_yaml(path)
    survey_path = root / "technologies" / "README.md"
    adr_path = root / "decisions" / "ADR-0001-first-technology-bakeoff.md"
    matrix_path = root / "benchmarks" / "experiment-matrix.yaml"
    survey = survey_path.read_text(encoding="utf-8") if survey_path.exists() else ""
    adr = adr_path.read_text(encoding="utf-8") if adr_path.exists() else ""
    matrix = _load_yaml(matrix_path) if matrix_path.exists() else {}
    return records, survey, adr, matrix


def _has_prefix(values: Any, prefix: str) -> bool:
    return isinstance(values, list) and any(
        isinstance(value, str) and value.startswith(prefix) for value in values
    )


def _duplicate_ids(items: list[Any]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str):
            continue
        if item_id in seen:
            duplicates.add(item_id)
        seen.add(item_id)
    return sorted(duplicates)


def resolve_repo_file(root: Path, candidate: str, allowed_prefix: str) -> Path:
    """Resolve a repository-relative regular file without allowing path escape."""
    if not isinstance(candidate, str) or not candidate:
        raise ValueError("path must be a non-empty relative POSIX path")

    candidate_path = PurePosixPath(candidate)
    if candidate_path.is_absolute() or PureWindowsPath(candidate).is_absolute():
        raise ValueError("absolute paths are not allowed")
    if "\\" in candidate:
        raise ValueError("path must use POSIX separators")
    if ".." in candidate_path.parts:
        raise ValueError("parent path segments are not allowed")

    prefix_path = PurePosixPath(allowed_prefix)
    if candidate_path.parts[: len(prefix_path.parts)] != prefix_path.parts:
        raise ValueError(f"path must be under {prefix_path.as_posix()}/")

    resolved_root = root.resolve()
    resolved = resolved_root.joinpath(*candidate_path.parts).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError("resolved path escapes the repository") from error
    if not resolved.is_file():
        raise ValueError("path must resolve to an existing regular file")
    return resolved


def _validate_edge_fixtures(root: Path) -> list[str]:
    errors: list[str] = []
    fixture_dir = root / "benchmarks" / "fixtures"

    def read_ids(path: Path) -> list[str]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return [row["id"] for row in csv.DictReader(handle)]

    try:
        left = read_ids(fixture_dir / "normalization-edge-left.csv")
        right = read_ids(fixture_dir / "normalization-edge-right.csv")
    except (FileNotFoundError, KeyError) as error:
        return [f"normalization fixtures are unavailable or malformed: {error}"]

    exact = len(set(left) & set(right))

    def normalize(value: str) -> str:
        return unicodedata.normalize("NFKC", value.strip()).casefold()

    normalized = len(
        {normalize(value) for value in left} & {normalize(value) for value in right}
    )
    if exact != 1:
        errors.append(f"byte-exact edge fixture intersection must be 1, found {exact}")
    if normalized != 4:
        errors.append(
            f"trim-casefold-NFKC edge fixture intersection must be 4, found {normalized}"
        )
    return errors


def _load_result_validator(
    root: Path,
) -> tuple[Draft202012Validator | None, list[str]]:
    try:
        path = resolve_repo_file(
            root,
            "benchmarks/result.schema.json",
            "benchmarks",
        )
    except ValueError as error:
        return None, [f"{REPOSITORY_PATH_ERROR}: benchmark result schema: {error}"]
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except (json.JSONDecodeError, ValueError, TypeError) as error:
        return None, [f"invalid benchmark result schema: {error}"]
    return Draft202012Validator(schema), []


def _validate_result_file(
    root: Path,
    result_path: str,
    validator: Draft202012Validator,
    experiment_id: str,
    status: str,
    applicable_tracks: Any,
    selected_tracks: dict[str, dict[str, Any]],
) -> list[str]:
    try:
        path = resolve_repo_file(root, result_path, "benchmarks")
    except ValueError as error:
        return [f"{experiment_id}: {REPOSITORY_PATH_ERROR}: result file: {error}"]

    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"{experiment_id}: result file is not readable JSON: {error}"]

    errors = []
    for error in sorted(
        validator.iter_errors(result),
        key=lambda item: tuple(str(segment) for segment in item.path),
    ):
        location = ".".join(str(segment) for segment in error.path) or "<root>"
        errors.append(
            f"{experiment_id}: result does not conform at {location}: {error.message}"
        )
    if isinstance(result, dict):
        if result.get("experiment_id") != experiment_id:
            errors.append(
                f"{experiment_id}: result experiment_id does not match the matrix"
            )
        if result.get("status") != status:
            errors.append(f"{experiment_id}: result status does not match the matrix")
        tracks = applicable_tracks if isinstance(applicable_tracks, list) else []
        track_id = result.get("track_id")
        if track_id not in tracks:
            errors.append(f"{experiment_id}: result track_id is not applicable")
        selected_track = (
            selected_tracks.get(track_id) if isinstance(track_id, str) else None
        )
        if selected_track is not None:
            expected_revision = selected_track.get("source_revision")
            if result.get("source_revision") != expected_revision:
                errors.append(
                    f"{experiment_id}: {RESULT_SOURCE_REVISION_ERROR}: "
                    f"source_revision must exactly match the {track_id} selected-track pin"
                )
    return errors


def validate_content(
    root: Path,
    records: dict[str, dict[str, Any]],
    survey: str,
    adr: str,
    matrix: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if len(records) < 5:
        errors.append(f"expected at least 5 technology records, found {len(records)}")

    for filename, marker in REQUIRED_RECORDS.items():
        if filename not in records:
            errors.append(f"missing surveyed technology record: {filename}")
        if f"<!-- technology:{marker} -->" not in survey:
            errors.append(f"survey missing technology marker: {marker}")

    identities: dict[str, str] = {}
    categories: set[str] = set()
    for filename, record in records.items():
        if not isinstance(record, dict):
            errors.append(f"{filename}: record must be a YAML mapping")
            continue
        if record.get("record_type") != "technology":
            errors.append(f"{filename}: record_type must be technology")
        name = _read_path(record, "identity.name")
        if isinstance(name, str) and name:
            if name in identities:
                errors.append(
                    f"{filename}: duplicate technology identity also present in {identities[name]}"
                )
            identities[name] = filename
        category = _read_path(record, "identity.category")
        if isinstance(category, str):
            categories.add(category)
        for dotted_path in REQUIRED_RECORD_PATHS:
            value = _read_path(record, dotted_path)
            if value is None or value == "" or value == []:
                errors.append(
                    f"{filename}: missing evaluation evidence at {dotted_path}"
                )
        if not _has_prefix(_read_path(record, "assessment.strengths"), "F —"):
            errors.append(f"{filename}: assessment.strengths must contain an F — fact")
        if not _has_prefix(
            _read_path(record, "assessment.limitations_or_unknowns"), "U —"
        ):
            errors.append(f"{filename}: limitations must contain a U — unknown")
        if not _has_prefix(
            _read_path(record, "assessment.recommended_experiments"), "H —"
        ):
            errors.append(
                f"{filename}: recommended experiments must contain an H — hypothesis"
            )
        fit = _read_path(record, "assessment.private_match_fit")
        if not isinstance(fit, str) or not fit.startswith("I —"):
            errors.append(
                f"{filename}: private_match_fit must contain an I — inference"
            )

    missing_categories = REQUIRED_CATEGORIES - categories
    if missing_categories:
        errors.append(
            f"missing required technology categories: {sorted(missing_categories)}"
        )

    for column in REQUIRED_COMPARISON_COLUMNS:
        if f"| {column} " not in survey and f"| {column} |" not in survey:
            errors.append(f"survey comparison table missing column: {column}")
    if "No local candidate benchmark has been executed" not in survey:
        errors.append(
            "survey must state that no local candidate benchmark was executed"
        )

    if "<!-- selection:cryptographic -->" not in adr:
        errors.append("ADR must mark the cryptographic reproduction selection")
    if "<!-- selection:tee -->" not in adr:
        errors.append("ADR must mark the TEE reproduction selection")
    if "Production architecture: not selected" not in adr:
        errors.append("ADR must state the production-architecture boundary")
    if "D-004 — Execute the smallest falsifiable experiment first" not in adr:
        errors.append("ADR must recommend a bounded next experiment")
    if "Rejected from the first bounded experiment" not in adr:
        errors.append("ADR must record rejected or deferred alternatives")

    if not isinstance(matrix, dict):
        errors.append("experiment matrix must be a YAML mapping")
        return errors
    boundary = matrix.get("execution_boundary", {})
    if boundary.get("vendor_results_are_local_results") is not False:
        errors.append("matrix must distinguish vendor results from local results")
    if boundary.get("production_architecture_decision") is not False:
        errors.append("matrix must not select a production architecture")
    if boundary.get("data_classification") != "synthetic-only":
        errors.append("matrix must require synthetic-only data")

    result_validator, result_schema_errors = _load_result_validator(root)
    errors.extend(result_schema_errors)

    tracks = matrix.get("selected_tracks", [])
    if not isinstance(tracks, list):
        errors.append("selected_tracks must be an array")
        tracks = []
    duplicate_track_ids = _duplicate_ids(tracks)
    if duplicate_track_ids:
        errors.append(
            f"{DUPLICATE_ID_ERROR}: duplicate selected track IDs: {duplicate_track_ids}"
        )
    track_ids = {
        track.get("id")
        for track in tracks
        if isinstance(track, dict) and isinstance(track.get("id"), str)
    }
    selected_tracks: dict[str, dict[str, Any]] = {}
    for track in tracks:
        if not isinstance(track, dict):
            continue
        track_id = track.get("id")
        if isinstance(track_id, str) and track_id not in selected_tracks:
            selected_tracks[track_id] = track
    if not REQUIRED_TRACKS.issubset(track_ids):
        errors.append(f"missing selected tracks: {sorted(REQUIRED_TRACKS - track_ids)}")
    classes = {track.get("class") for track in tracks if isinstance(track, dict)}
    if "cryptographic" not in classes or "tee" not in classes:
        errors.append("at least one cryptographic and one TEE track must be selected")
    for track in tracks:
        if not isinstance(track, dict):
            errors.append("each selected track must be a mapping")
            continue
        record_path = track.get("record")
        try:
            resolve_repo_file(root, record_path, "records/technologies")
        except ValueError as error:
            errors.append(
                f"{track.get('id', 'unknown track')}: {REPOSITORY_PATH_ERROR}: "
                f"selected record: {error}"
            )
        if not track.get("source_revision"):
            errors.append(
                f"{track.get('id', 'unknown track')}: source revision is required"
            )
        if not track.get("environment_authorization"):
            errors.append(
                f"{track.get('id', 'unknown track')}: environment authorization is required"
            )

    experiments = matrix.get("experiments", [])
    if not isinstance(experiments, list):
        errors.append("experiments must be an array")
        experiments = []
    duplicate_experiment_ids = _duplicate_ids(experiments)
    if duplicate_experiment_ids:
        errors.append(
            f"{DUPLICATE_ID_ERROR}: duplicate experiment IDs: {duplicate_experiment_ids}"
        )
    experiment_ids = {
        experiment.get("id")
        for experiment in experiments
        if isinstance(experiment, dict) and isinstance(experiment.get("id"), str)
    }
    if experiment_ids != REQUIRED_EXPERIMENTS:
        errors.append(
            f"experiment matrix IDs must be {sorted(REQUIRED_EXPERIMENTS)}, found {sorted(str(value) for value in experiment_ids)}"
        )
    for experiment in experiments:
        if not isinstance(experiment, dict):
            errors.append("each experiment must be a mapping")
            continue
        experiment_id = experiment.get("id", "unknown experiment")
        status = experiment.get("execution_status")
        if status not in PLAN_STATUSES:
            errors.append(f"{experiment_id}: invalid execution status {status!r}")
        if not experiment.get("requirement"):
            errors.append(f"{experiment_id}: requirement is required")
        if not experiment.get("applicable_tracks"):
            errors.append(f"{experiment_id}: applicable tracks are required")

        inputs = experiment.get("inputs")
        if isinstance(inputs, dict):
            for field, allowed_prefix in (
                ("generator", "benchmarks"),
                ("left_fixture", "benchmarks/fixtures"),
                ("right_fixture", "benchmarks/fixtures"),
            ):
                if field not in inputs:
                    continue
                try:
                    resolve_repo_file(root, inputs[field], allowed_prefix)
                except ValueError as error:
                    errors.append(
                        f"{experiment_id}: {REPOSITORY_PATH_ERROR}: {field}: {error}"
                    )
        if status in RESULT_STATUSES:
            result_path = experiment.get("result")
            if not isinstance(result_path, str):
                errors.append(
                    f"{experiment_id}: executed status requires a committed result path"
                )
            elif result_validator is not None:
                errors.extend(
                    _validate_result_file(
                        root,
                        result_path,
                        result_validator,
                        experiment_id,
                        status,
                        experiment.get("applicable_tracks", []),
                        selected_tracks,
                    )
                )

    errors.extend(_validate_edge_fixtures(root))
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    records, survey, adr, matrix = load_artifacts(root)
    errors = validate_content(root, records, survey, adr, matrix)
    if errors:
        for error in errors:
            print(f"technology-bakeoff: error: {error}")
        return 1
    categories = {
        _read_path(record, "identity.category") for record in records.values()
    }
    print(
        "technology-bakeoff: "
        f"records={len(records)} categories={len(categories)} "
        f"tracks={len(matrix['selected_tracks'])} experiments={len(matrix['experiments'])} errors=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
