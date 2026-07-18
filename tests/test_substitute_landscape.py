from __future__ import annotations

import copy
import unittest
from pathlib import Path

from scripts.validate_substitute_landscape import REQUIRED_CLASSES, load_landscape, validate_content


ROOT = Path(__file__).resolve().parents[1]


class SubstituteLandscapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records, cls.survey = load_landscape(ROOT)

    def test_repository_landscape_meets_issue_acceptance(self) -> None:
        self.assertEqual(validate_content(self.records, self.survey), [])
        self.assertGreaterEqual(len(self.records), 5)
        self.assertTrue(set(REQUIRED_CLASSES).issubset(self.records))

    def test_missing_required_class_is_rejected(self) -> None:
        records = dict(self.records)
        missing_filename = next(iter(REQUIRED_CLASSES))
        del records[missing_filename]
        errors = validate_content(records, self.survey)
        self.assertTrue(any("missing required substitute class" in error for error in errors), errors)

    def test_duplicate_identity_is_rejected(self) -> None:
        records = copy.deepcopy(self.records)
        duplicate = copy.deepcopy(next(iter(records.values())))
        records["duplicate.yaml"] = duplicate
        errors = validate_content(records, self.survey)
        self.assertTrue(any("duplicate identity" in error for error in errors), errors)

    def test_missing_disconfirming_tests_is_rejected(self) -> None:
        survey = self.survey.replace("DCT-", "REMOVED-")
        errors = validate_content(self.records, survey)
        self.assertTrue(any("disconfirming tests" in error for error in errors), errors)

    def test_missing_comparison_evidence_is_rejected(self) -> None:
        records = copy.deepcopy(self.records)
        record = next(iter(records.values()))
        del record["market"]["buyer"]
        errors = validate_content(records, self.survey)
        self.assertTrue(any("market.buyer" in error for error in errors), errors)

    def test_missing_comparison_column_is_rejected(self) -> None:
        survey = self.survey.replace("| Class | Setup time |", "| Class | Removed setup |")
        errors = validate_content(self.records, survey)
        self.assertTrue(any("missing column: Setup time" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
