from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from benchmarks.generate_inputs import build_sets, generate_case
from scripts.validate_technology_bakeoff import load_artifacts, validate_content


ROOT = Path(__file__).resolve().parents[1]
HEX_64 = "0" * 64


class TechnologyBakeoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records, cls.survey, cls.adr, cls.matrix = load_artifacts(ROOT)

    def test_repository_bakeoff_meets_issue_acceptance(self) -> None:
        self.assertEqual(
            validate_content(ROOT, self.records, self.survey, self.adr, self.matrix),
            [],
        )
        self.assertGreaterEqual(len(self.records), 5)

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
            prefix=".codex-test-bakeoff-", dir=ROOT
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

    def test_generator_rejects_impossible_intersection(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            build_sets(3, 4, 5, 1)

    def test_result_schema_requires_output_digest_for_pass(self) -> None:
        schema = json.loads((ROOT / "benchmarks" / "result.schema.json").read_text())
        validator = Draft202012Validator(schema)
        result = {
            "schema_version": "0.1",
            "experiment_id": "EXP-001",
            "track_id": "TRACK-PSI",
            "result_origin": "local",
            "status": "pass",
            "executed_at": "2026-07-18T00:00:00Z",
            "source_revision": "d768270",
            "environment": {"os": "synthetic test"},
            "commands": [{"argv": ["candidate", "--synthetic"], "exit_code": 0}],
            "evidence": {
                "stdout_sha256": HEX_64,
                "stderr_sha256": HEX_64,
                "input_artifacts": {"left.csv": HEX_64},
                "output_artifacts": {"result.json": HEX_64},
            },
            "measurements": {},
            "observations": ["synthetic schema fixture only"],
            "limitations": ["not a candidate execution"],
        }
        self.assertEqual(list(validator.iter_errors(result)), [])
        result["evidence"]["output_artifacts"] = {}
        self.assertTrue(list(validator.iter_errors(result)))


if __name__ == "__main__":
    unittest.main()
