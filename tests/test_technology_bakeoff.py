from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from benchmarks.generate_inputs import build_sets, generate_case
from scripts.validate_technology_bakeoff import (
    DUPLICATE_ID_ERROR,
    REPOSITORY_PATH_ERROR,
    RESULT_SOURCE_REVISION_ERROR,
    load_artifacts,
    resolve_repo_file,
    validate_content,
)


ROOT = Path(__file__).resolve().parents[1]
HEX_64 = "0" * 64
PSI_REVISION = "d7682707035d6b3e04cc09b8bfef629140641432"
VOPRF_REVISION = "v1.6.4"
TEE_REVISION = "cli-v1.4.5+nsm-v0.5.2"


class TechnologyBakeoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records, cls.survey, cls.adr, cls.matrix = load_artifacts(ROOT)

    def valid_result(
        self,
        *,
        experiment_id: str = "EXP-001",
        track_id: str = "TRACK-PSI",
        status: str = "pass",
        source_revision: str = PSI_REVISION,
    ) -> dict[str, object]:
        return {
            "schema_version": "0.1",
            "experiment_id": experiment_id,
            "track_id": track_id,
            "result_origin": "local",
            "status": status,
            "executed_at": "2026-07-18T00:00:00Z",
            "source_revision": source_revision,
            "environment": {"os": "synthetic schema fixture"},
            "commands": [{"argv": ["candidate", "--synthetic"], "exit_code": 0}],
            "evidence": {
                "stdout_sha256": HEX_64,
                "stderr_sha256": HEX_64,
                "input_artifacts": {"input-manifest.json": HEX_64},
                "output_artifacts": {"result.json": HEX_64} if status == "pass" else {},
            },
            "measurements": {},
            "observations": ["synthetic schema fixture only"],
            "limitations": ["not a candidate execution"],
        }

    def result_schema_errors(self, result: dict[str, object]) -> list[object]:
        schema = json.loads(
            (ROOT / "benchmarks" / "result.schema.json").read_text(encoding="utf-8")
        )
        return list(Draft202012Validator(schema).iter_errors(result))

    def validate_result(
        self,
        result: dict[str, object],
        *,
        matrix: dict[str, object] | None = None,
    ) -> list[str]:
        candidate_matrix = copy.deepcopy(matrix if matrix is not None else self.matrix)
        experiment = next(
            item
            for item in candidate_matrix["experiments"]
            if item["id"] == result["experiment_id"]
        )
        experiment["execution_status"] = result["status"]
        with tempfile.TemporaryDirectory(
            prefix=".codex-test-bakeoff-result-", dir=ROOT / "benchmarks"
        ) as result_dir:
            result_path = Path(result_dir) / "result.json"
            result_path.write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            experiment["result"] = str(result_path.relative_to(ROOT))
            return validate_content(
                ROOT,
                self.records,
                self.survey,
                self.adr,
                candidate_matrix,
            )

    def test_repository_bakeoff_meets_issue_acceptance(self) -> None:
        self.assertEqual(
            validate_content(ROOT, self.records, self.survey, self.adr, self.matrix),
            [],
        )
        self.assertGreaterEqual(len(self.records), 5)

    def test_current_eight_experiments_remain_not_run(self) -> None:
        expected_requirements = {
            "EXP-001": "small balanced sets",
            "EXP-002": "large balanced sets",
            "EXP-003": "highly unbalanced sets",
            "EXP-004": "duplicate and normalization edge cases",
            "EXP-005": "no-match, one-match, and small-intersection cases",
            "EXP-006": "repeated adaptive query attempts",
            "EXP-007": "tampered messages and replay",
            "EXP-008": "packet capture and raw-data egress observation",
        }
        self.assertEqual(
            {
                experiment["id"]: experiment["requirement"]
                for experiment in self.matrix["experiments"]
            },
            expected_requirements,
        )
        self.assertTrue(
            all(
                experiment["execution_status"] == "not-run"
                for experiment in self.matrix["experiments"]
            )
        )

    def test_missing_required_category_is_rejected(self) -> None:
        records = {
            filename: record
            for filename, record in copy.deepcopy(self.records).items()
            if record["identity"]["category"] != "TEE"
        }
        errors = validate_content(ROOT, records, self.survey, self.adr, self.matrix)
        self.assertTrue(
            any("missing required technology categories" in error for error in errors),
            errors,
        )

    def test_duplicate_technology_identity_is_rejected(self) -> None:
        records = copy.deepcopy(self.records)
        records["duplicate.yaml"] = copy.deepcopy(next(iter(records.values())))
        errors = validate_content(ROOT, records, self.survey, self.adr, self.matrix)
        self.assertTrue(
            any("duplicate technology identity" in error for error in errors), errors
        )

    def test_missing_required_experiment_is_rejected(self) -> None:
        matrix = copy.deepcopy(self.matrix)
        matrix["experiments"] = [
            item for item in matrix["experiments"] if item["id"] != "EXP-008"
        ]
        errors = validate_content(ROOT, self.records, self.survey, self.adr, matrix)
        self.assertTrue(
            any("experiment matrix IDs" in error for error in errors), errors
        )

    def test_duplicate_experiment_id_is_rejected_even_when_all_required_exist(
        self,
    ) -> None:
        matrix = copy.deepcopy(self.matrix)
        matrix["experiments"].append(copy.deepcopy(matrix["experiments"][0]))

        errors = validate_content(ROOT, self.records, self.survey, self.adr, matrix)

        self.assertTrue(
            any(DUPLICATE_ID_ERROR in error and "EXP-001" in error for error in errors),
            errors,
        )

    def test_duplicate_selected_track_id_is_rejected(self) -> None:
        matrix = copy.deepcopy(self.matrix)
        matrix["selected_tracks"].append(copy.deepcopy(matrix["selected_tracks"][0]))

        errors = validate_content(ROOT, self.records, self.survey, self.adr, matrix)

        self.assertTrue(
            any(
                DUPLICATE_ID_ERROR in error and "TRACK-PSI" in error for error in errors
            ),
            errors,
        )

    def test_unique_track_and_experiment_ids_pass(self) -> None:
        errors = validate_content(
            ROOT,
            self.records,
            self.survey,
            self.adr,
            self.matrix,
        )

        self.assertFalse(any(DUPLICATE_ID_ERROR in error for error in errors), errors)

    def test_missing_and_duplicate_experiment_errors_are_both_retained(self) -> None:
        matrix = copy.deepcopy(self.matrix)
        matrix["experiments"] = [
            experiment
            for experiment in matrix["experiments"]
            if experiment["id"] != "EXP-008"
        ]
        matrix["experiments"].append(copy.deepcopy(matrix["experiments"][0]))

        errors = validate_content(ROOT, self.records, self.survey, self.adr, matrix)

        self.assertTrue(any(DUPLICATE_ID_ERROR in error for error in errors), errors)
        self.assertTrue(
            any("experiment matrix IDs" in error for error in errors), errors
        )

    def test_missing_tee_selection_is_rejected(self) -> None:
        adr = self.adr.replace("<!-- selection:tee -->", "<!-- removed -->")
        errors = validate_content(ROOT, self.records, self.survey, adr, self.matrix)
        self.assertTrue(
            any("TEE reproduction selection" in error for error in errors), errors
        )

    def test_executed_status_without_result_is_rejected(self) -> None:
        matrix = copy.deepcopy(self.matrix)
        matrix["experiments"][0]["execution_status"] = "pass"
        errors = validate_content(ROOT, self.records, self.survey, self.adr, matrix)
        self.assertTrue(
            any("executed status requires" in error for error in errors), errors
        )

    def test_executed_status_with_invalid_result_is_rejected(self) -> None:
        matrix = copy.deepcopy(self.matrix)
        experiment = matrix["experiments"][0]
        experiment["execution_status"] = "pass"
        with tempfile.TemporaryDirectory(
            prefix=".codex-test-bakeoff-", dir=ROOT / "benchmarks"
        ) as result_dir:
            result_path = Path(result_dir) / "invalid-result.json"
            result_path.write_text("{}\n", encoding="utf-8")
            experiment["result"] = str(result_path.relative_to(ROOT))
            errors = validate_content(ROOT, self.records, self.survey, self.adr, matrix)
        self.assertTrue(
            any("result does not conform" in error for error in errors), errors
        )

    def test_generator_is_deterministic_and_records_duplicates(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix=".codex-test-bakeoff-", dir=ROOT
        ) as first_dir:
            with tempfile.TemporaryDirectory(
                prefix=".codex-test-bakeoff-", dir=ROOT
            ) as second_dir:
                first = generate_case(Path(first_dir), "case-a", 100, 80, 5, 42, 3, 2)
                second = generate_case(Path(second_dir), "case-a", 100, 80, 5, 42, 3, 2)
        self.assertEqual(first, second)
        self.assertEqual(first["left"]["rows"], 103)
        self.assertEqual(first["left"]["duplicates"], 3)
        self.assertEqual(first["right"]["rows"], 82)
        self.assertEqual(first["right"]["duplicates"], 2)
        self.assertEqual(first["expected"]["byte_exact_distinct_intersection"], 5)

    def test_generator_manifest_digests_match_fixture_bytes(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix=".codex-test-bakeoff-", dir=ROOT
        ) as output_dir:
            output_path = Path(output_dir)
            manifest = generate_case(output_path, "digest-case", 7, 5, 2, 41)
            committed_manifest = json.loads(
                (output_path / "digest-case-manifest.json").read_text(encoding="utf-8")
            )

            self.assertEqual(committed_manifest, manifest)
            for side in ("left", "right"):
                path = output_path / manifest[side]["path"]
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(manifest[side]["sha256"], digest)

    def test_generator_rejects_impossible_intersection(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            build_sets(3, 4, 5, 1)

    def test_result_schema_rejects_empty_input_artifacts(self) -> None:
        result = self.valid_result()
        result["evidence"]["input_artifacts"] = {}

        self.assertTrue(self.result_schema_errors(result))

    def test_result_schema_accepts_pass_with_input_digest(self) -> None:
        self.assertEqual(self.result_schema_errors(self.valid_result()), [])

    def test_result_schema_accepts_fail_with_input_digest(self) -> None:
        result = self.valid_result(status="fail")

        self.assertEqual(self.result_schema_errors(result), [])

    def test_result_schema_accepts_skip_or_unsupported_with_plan_digest(self) -> None:
        for status in ("skip", "unsupported"):
            with self.subTest(status=status):
                result = self.valid_result(status=status)
                result["evidence"]["input_artifacts"] = {
                    "experiment-matrix.yaml": HEX_64
                }
                result["limitations"] = [
                    "no experiment input was generated; plan digest retained"
                ]
                self.assertEqual(self.result_schema_errors(result), [])

    def test_result_schema_rejects_invalid_input_digest(self) -> None:
        result = self.valid_result()
        result["evidence"]["input_artifacts"] = {"input.json": "not-a-sha256"}

        self.assertTrue(self.result_schema_errors(result))

    def test_result_schema_rejects_output_digest_without_input_digest(self) -> None:
        result = self.valid_result()
        result["evidence"]["input_artifacts"] = {}

        self.assertTrue(self.result_schema_errors(result))

    def test_result_schema_requires_output_digest_for_pass(self) -> None:
        result = self.valid_result()
        result["evidence"]["output_artifacts"] = {}

        self.assertTrue(self.result_schema_errors(result))

    def test_result_revision_exact_selected_pin_passes(self) -> None:
        errors = self.validate_result(self.valid_result())

        self.assertFalse(
            any(RESULT_SOURCE_REVISION_ERROR in error for error in errors), errors
        )

    def test_exact_tag_and_composite_selected_pins_pass(self) -> None:
        for track_id, revision in (
            ("TRACK-VOPRF", VOPRF_REVISION),
            ("TRACK-TEE", TEE_REVISION),
        ):
            with self.subTest(track_id=track_id):
                result = self.valid_result(
                    experiment_id="EXP-003",
                    track_id=track_id,
                    source_revision=revision,
                )
                errors = self.validate_result(result)
                self.assertFalse(
                    any(RESULT_SOURCE_REVISION_ERROR in error for error in errors),
                    errors,
                )

    def test_arbitrary_seven_character_result_revision_fails(self) -> None:
        result = self.valid_result(source_revision="abcdef0")

        errors = self.validate_result(result)

        self.assertTrue(
            any(RESULT_SOURCE_REVISION_ERROR in error for error in errors), errors
        )

    def test_another_track_revision_fails(self) -> None:
        result = self.valid_result(source_revision=VOPRF_REVISION)

        errors = self.validate_result(result)

        self.assertTrue(
            any(RESULT_SOURCE_REVISION_ERROR in error for error in errors), errors
        )

    def test_commit_sha_cannot_replace_tag_pin(self) -> None:
        result = self.valid_result(
            experiment_id="EXP-003",
            track_id="TRACK-VOPRF",
            source_revision=PSI_REVISION,
        )

        errors = self.validate_result(result)

        self.assertTrue(
            any(RESULT_SOURCE_REVISION_ERROR in error for error in errors), errors
        )

    def test_composite_tee_revision_partial_match_fails(self) -> None:
        result = self.valid_result(
            experiment_id="EXP-003",
            track_id="TRACK-TEE",
            source_revision="cli-v1.4.5",
        )

        errors = self.validate_result(result)

        self.assertTrue(
            any(RESULT_SOURCE_REVISION_ERROR in error for error in errors), errors
        )

    def test_matrix_pin_change_rejects_old_result_revision(self) -> None:
        matrix = copy.deepcopy(self.matrix)
        matrix["selected_tracks"][0]["source_revision"] = "reviewed-next-pin"

        errors = self.validate_result(self.valid_result(), matrix=matrix)

        self.assertTrue(
            any(RESULT_SOURCE_REVISION_ERROR in error for error in errors), errors
        )

    def test_valid_technology_record_path_resolves(self) -> None:
        path = resolve_repo_file(
            ROOT,
            "records/technologies/secretflow-psi.yaml",
            "records/technologies",
        )

        self.assertEqual(
            path, (ROOT / "records/technologies/secretflow-psi.yaml").resolve()
        )

    def test_absolute_repository_path_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "absolute paths"):
            resolve_repo_file(
                ROOT,
                str((ROOT / "records/technologies/secretflow-psi.yaml").resolve()),
                "records/technologies",
            )

    def test_parent_repository_path_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "parent path segments"):
            resolve_repo_file(
                ROOT,
                "../secretflow-psi.yaml",
                "records/technologies",
            )

    def test_normalized_nested_parent_escape_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "parent path segments"):
            resolve_repo_file(
                ROOT,
                "records/technologies/nested/../../../outside.yaml",
                "records/technologies",
            )

    def test_symlink_to_outside_repository_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix=".codex-test-bakeoff-root-", dir=ROOT
        ) as repository_dir:
            with tempfile.TemporaryDirectory(
                prefix=".codex-test-bakeoff-outside-", dir=ROOT
            ) as outside_dir:
                repository_root = Path(repository_dir)
                records_dir = repository_root / "records" / "technologies"
                records_dir.mkdir(parents=True)
                outside_file = Path(outside_dir) / "outside.yaml"
                outside_file.write_text("record_type: technology\n", encoding="utf-8")
                (records_dir / "escape.yaml").symlink_to(outside_file)

                with self.assertRaisesRegex(ValueError, "escapes the repository"):
                    resolve_repo_file(
                        repository_root,
                        "records/technologies/escape.yaml",
                        "records/technologies",
                    )

    def test_directory_repository_path_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "regular file"):
            resolve_repo_file(
                ROOT,
                "records/technologies",
                "records/technologies",
            )

    def test_missing_repository_path_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "regular file"):
            resolve_repo_file(
                ROOT,
                "records/technologies/missing.yaml",
                "records/technologies",
            )

    def test_selected_track_path_escape_is_rejected_by_validator(self) -> None:
        matrix = copy.deepcopy(self.matrix)
        matrix["selected_tracks"][0]["record"] = "../outside.yaml"

        errors = validate_content(ROOT, self.records, self.survey, self.adr, matrix)

        self.assertTrue(
            any(
                REPOSITORY_PATH_ERROR in error and "TRACK-PSI" in error
                for error in errors
            ),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
