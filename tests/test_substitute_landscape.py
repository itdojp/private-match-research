from __future__ import annotations

import copy
import io
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import scripts.validate_substitute_landscape as substitute_validator
from scripts.validate_substitute_landscape import (
    REQUIRED_CLASSES,
    load_landscape,
    main,
    validate_content,
)


ROOT = Path(__file__).resolve().parents[1]


class SubstituteLandscapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records, cls.survey, cls.load_errors = load_landscape(ROOT)

    def fixture_root(
        self,
        *,
        record_names: tuple[str, ...] = (),
        include_survey: bool = True,
    ) -> Path:
        temporary_directory = tempfile.TemporaryDirectory(
            dir=ROOT,
            prefix=".test-substitute-landscape-",
        )
        self.addCleanup(temporary_directory.cleanup)
        root = Path(temporary_directory.name)
        records_dir = root / "records" / "substitutes"
        records_dir.mkdir(parents=True)
        for name in record_names:
            shutil.copy2(ROOT / "records" / "substitutes" / name, records_dir / name)
        if include_survey:
            survey_dir = root / "landscape" / "substitutes"
            survey_dir.mkdir(parents=True)
            shutil.copy2(
                ROOT / "landscape" / "substitutes" / "README.md",
                survey_dir / "README.md",
            )
        return root

    def test_repository_landscape_meets_issue_acceptance(self) -> None:
        self.assertEqual(self.load_errors, [])
        self.assertEqual(
            validate_content(self.records, self.survey, self.load_errors), []
        )
        self.assertGreaterEqual(len(self.records), 5)
        self.assertTrue(set(REQUIRED_CLASSES).issubset(self.records))

    def test_missing_required_class_is_rejected(self) -> None:
        records = dict(self.records)
        missing_filename = next(
            (name for name in REQUIRED_CLASSES if name in records), None
        )
        if missing_filename is None:
            self.skipTest("required substitute fixtures are absent from the baseline")
        del records[missing_filename]
        errors = validate_content(records, self.survey, [])
        self.assertTrue(
            any("missing required substitute class" in error for error in errors),
            errors,
        )

    def test_duplicate_identity_is_rejected(self) -> None:
        records = copy.deepcopy(self.records)
        duplicate = copy.deepcopy(next(iter(records.values())))
        records["duplicate.yaml"] = duplicate
        errors = validate_content(records, self.survey, [])
        self.assertTrue(any("duplicate identity" in error for error in errors), errors)

    def test_missing_disconfirming_tests_is_rejected(self) -> None:
        survey = self.survey.replace("DCT-", "REMOVED-")
        errors = validate_content(self.records, survey, [])
        self.assertTrue(any("disconfirming tests" in error for error in errors), errors)

    def test_missing_comparison_evidence_is_rejected(self) -> None:
        records = copy.deepcopy(self.records)
        record = next(iter(records.values()))
        del record["market"]["buyer"]
        errors = validate_content(records, self.survey, [])
        self.assertTrue(any("market.buyer" in error for error in errors), errors)

    def test_missing_comparison_column_is_rejected(self) -> None:
        survey = self.survey.replace(
            "| Class | Setup time |", "| Class | Removed setup |"
        )
        errors = validate_content(self.records, survey, [])
        self.assertTrue(
            any("missing column: Setup time" in error for error in errors), errors
        )

    def test_malformed_yaml_is_a_structured_filename_error_without_mapping_duplicate(
        self,
    ) -> None:
        root = self.fixture_root()
        malformed_path = root / "records" / "substitutes" / "malformed.yaml"
        malformed_path.write_text(
            "secret: SHOULD-NOT-APPEAR\nidentity: [unterminated\n",
            encoding="utf-8",
        )

        records, survey, load_errors = load_landscape(root)
        errors = validate_content(records, survey, load_errors)

        expected_prefix = "records/substitutes/malformed.yaml: YAML parse error:"
        self.assertTrue(
            any(error.startswith(expected_prefix) for error in errors), errors
        )
        self.assertFalse(
            any(
                "malformed.yaml: record must be a YAML mapping" in error
                for error in errors
            ),
            errors,
        )
        self.assertFalse(any("SHOULD-NOT-APPEAR" in error for error in errors), errors)

    def test_record_read_error_is_structured(self) -> None:
        root = self.fixture_root(record_names=("nda-csv-comparison.yaml",))
        target = root / "records" / "substitutes" / "nda-csv-comparison.yaml"
        original_read_utf8 = substitute_validator._read_utf8

        def fail_target(path: Path) -> str:
            if path == target:
                raise OSError(13, "permission denied")
            return original_read_utf8(path)

        with mock.patch(
            "scripts.validate_substitute_landscape._read_utf8", side_effect=fail_target
        ):
            records, _, load_errors = load_landscape(root)

        self.assertNotIn(target.name, records)
        self.assertTrue(
            any(
                error.startswith(
                    "records/substitutes/nda-csv-comparison.yaml: file read error:"
                )
                and "errno 13" in error
                for error in load_errors
            ),
            load_errors,
        )
        self.assertFalse(any("permission denied" in error for error in load_errors))

    def test_invalid_utf8_is_a_structured_error(self) -> None:
        root = self.fixture_root()
        invalid_path = root / "records" / "substitutes" / "invalid-utf8.yaml"
        invalid_path.write_bytes(b"identity: \xff\n")

        records, _, load_errors = load_landscape(root)

        self.assertNotIn(invalid_path.name, records)
        self.assertTrue(
            any(
                error.startswith(
                    "records/substitutes/invalid-utf8.yaml: text decode error:"
                )
                for error in load_errors
            ),
            load_errors,
        )
        self.assertFalse(any("input/output error" in error for error in load_errors))

    def test_survey_read_error_is_structured(self) -> None:
        root = self.fixture_root()
        survey_path = root / "landscape" / "substitutes" / "README.md"
        original_read_utf8 = substitute_validator._read_utf8

        def fail_survey(path: Path) -> str:
            if path == survey_path:
                raise OSError(5, "input/output error")
            return original_read_utf8(path)

        with mock.patch(
            "scripts.validate_substitute_landscape._read_utf8", side_effect=fail_survey
        ):
            _, survey, load_errors = load_landscape(root)

        self.assertEqual(survey, "")
        self.assertTrue(
            any(
                error.startswith(
                    "landscape/substitutes/README.md: file read error: OSError (errno 5)"
                )
                for error in load_errors
            ),
            load_errors,
        )

    def test_parse_failure_does_not_stop_other_record_validation(self) -> None:
        valid_name = "nda-csv-comparison.yaml"
        root = self.fixture_root(record_names=(valid_name,))
        malformed_path = root / "records" / "substitutes" / "malformed.yaml"
        malformed_path.write_text("identity: [unterminated\n", encoding="utf-8")

        records, survey, load_errors = load_landscape(root)
        del records[valid_name]["market"]["buyer"]
        errors = validate_content(records, survey, load_errors)

        self.assertIn(valid_name, records)
        self.assertTrue(
            any("malformed.yaml: YAML parse error:" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any(
                f"{valid_name}: missing comparison evidence at market.buyer" in error
                for error in errors
            ),
            errors,
        )

    def test_multiple_load_errors_are_all_reported(self) -> None:
        root = self.fixture_root()
        (root / "records" / "substitutes" / "malformed.yaml").write_text(
            "identity: [unterminated\n",
            encoding="utf-8",
        )
        (root / "records" / "substitutes" / "invalid-utf8.yaml").write_bytes(
            b"identity: \xff\n"
        )

        _, _, load_errors = load_landscape(root)

        self.assertEqual(len(load_errors), 2, load_errors)
        self.assertTrue(
            any("malformed.yaml: YAML parse error:" in error for error in load_errors)
        )
        self.assertTrue(
            any(
                "invalid-utf8.yaml: text decode error:" in error
                for error in load_errors
            )
        )

    def test_cli_returns_one_and_prints_each_load_error_without_traceback(self) -> None:
        root = self.fixture_root()
        (root / "records" / "substitutes" / "malformed.yaml").write_text(
            "identity: [unterminated\n",
            encoding="utf-8",
        )
        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(["--root", str(root)])

        self.assertEqual(exit_code, 1)
        self.assertIn(
            "substitute-landscape: error: records/substitutes/malformed.yaml: YAML parse error:",
            stdout.getvalue(),
        )
        self.assertNotIn("Traceback", stdout.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_missing_baseline_fixtures_skip_negative_test_without_key_error(
        self,
    ) -> None:
        case = SubstituteLandscapeTests("test_missing_required_class_is_rejected")
        case.records = {}
        case.survey = self.survey
        result = unittest.TestResult()

        case.run(result)

        self.assertEqual(result.errors, [])
        self.assertEqual(result.failures, [])
        self.assertEqual(len(result.skipped), 1)

    def test_acceptance_validation_still_detects_missing_required_records(self) -> None:
        errors = validate_content({}, self.survey, [])

        self.assertTrue(
            any("missing required substitute class" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
