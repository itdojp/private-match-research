from __future__ import annotations

import copy
import datetime as dt
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.generate_competitor_index import load_records, main, render_index
from scripts.validate_research import load_yaml


ROOT = Path(__file__).resolve().parents[1]
RECORDS_DIR = ROOT / "records" / "competitors"


def index_record(organization: str, product: str) -> dict:
    return {
        "record_type": "competitor",
        "identity": {"organization": organization, "product": product},
        "observation": {"last_verified_at": "2026-07-18", "next_review_at": "2026-10-18"},
        "classification": {"class": "adjacent", "confidence": "medium"},
        "market": {"pricing": {"public": False}},
    }


class CompetitorLandscapeTests(unittest.TestCase):
    def test_landscape_meets_issue_acceptance_floor(self) -> None:
        paths = sorted(RECORDS_DIR.glob("*.yaml"))
        self.assertGreaterEqual(len(paths), 25)
        records = [load_yaml(path) for path in paths]
        self.assertGreaterEqual(sum(record["classification"]["class"] == "substitute" for record in records), 5)
        for record in records:
            with self.subTest(record=record["identity"]["product"]):
                self.assertTrue(record["sources"]["primary"])
                self.assertTrue(record["market"]["buyer"])
                self.assertTrue(record["market"]["user"])
                self.assertTrue(record["market"]["trigger"])
                self.assertTrue(record["product"]["outputs"])
                verified_at = dt.date.fromisoformat(record["observation"]["last_verified_at"])
                next_review_at = dt.date.fromisoformat(record["observation"]["next_review_at"])
                self.assertGreater(next_review_at, verified_at)
                self.assertTrue(record["assessment"]["claim_types"]["facts"])
                self.assertTrue(record["assessment"]["claim_types"]["inferences"])
                self.assertTrue(record["assessment"]["claim_types"]["hypotheses"])
                self.assertEqual(record["publication"]["reproducibility_review"], "approved")
                for source in record["sources"]["primary"]:
                    self.assertTrue(source["url"].startswith("https://"))
                    self.assertTrue(source["title"])
                    self.assertTrue(source["publisher"])
                    self.assertIn("published_at", source)
                    self.assertEqual(source["accessed_at"], "2026-07-18")

    def test_index_generation_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            records_dir = root / "records" / "competitors"
            records_dir.mkdir(parents=True)
            for name, record in (("b.yaml", index_record("Beta", "Two")), ("a.yaml", index_record("Alpha", "One"))):
                (records_dir / name).write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
            output = root / "landscape" / "competitor-index.md"
            records = load_records(records_dir)
            first = render_index(records, output)
            second = render_index(load_records(records_dir), output)
            self.assertEqual(first, second)
            self.assertLess(first.index("Alpha"), first.index("Beta"))

    def test_duplicate_identity_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            records_dir = Path(tmp)
            record = index_record("Alpha", "One")
            (records_dir / "one.yaml").write_text(yaml.safe_dump(record), encoding="utf-8")
            duplicate = copy.deepcopy(record)
            (records_dir / "two.yaml").write_text(yaml.safe_dump(duplicate), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate organization/product"):
                load_records(records_dir)

    def test_check_mode_detects_stale_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            records_dir = root / "records" / "competitors"
            records_dir.mkdir(parents=True)
            (records_dir / "one.yaml").write_text(yaml.safe_dump(index_record("Alpha", "One")), encoding="utf-8")
            output = root / "landscape" / "competitor-index.md"
            output.parent.mkdir(parents=True)
            output.write_text("stale\n", encoding="utf-8")
            result = main(["--root", str(root), "--minimum-count", "1", "--check"])
            self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
