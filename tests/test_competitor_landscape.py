from __future__ import annotations

import copy
import datetime as dt
import html
import json
import re
import tempfile
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from scripts.generate_competitor_index import load_records, main, render_index
from scripts.validate_research import load_yaml, validate_markdown_links


ROOT = Path(__file__).resolve().parents[1]
RECORDS_DIR = ROOT / "records" / "competitors"


def index_record(organization: str, product: str) -> dict:
    return {
        "record_type": "competitor",
        "identity": {"organization": organization, "product": product},
        "observation": {
            "last_verified_at": "2026-07-18",
            "next_review_at": "2026-10-18",
        },
        "classification": {"class": "adjacent", "confidence": "medium"},
        "market": {"pricing": {"public": False}},
    }


def render_identity(organization: str, product: str) -> tuple[str, list[str]]:
    record_path = Path("records/competitors/special.yaml")
    output_path = Path("landscape/competitor-index.md")
    rendered = render_index(
        [(record_path, index_record(organization, product))], output_path
    )
    target = "../records/competitors/special.yaml"
    row = next(line for line in rendered.splitlines() if f"]({target})" in line)
    cells = [
        cell.strip() for cell in row.removeprefix("|").removesuffix("|").split("|")
    ]
    return row, cells


def parse_product_link(cell: str) -> tuple[str, str]:
    match = re.fullmatch(r"\[([^\[\]]+)\]\(([^)\r\n]+)\)", cell)
    if match is None:
        raise AssertionError(f"invalid product link: {cell!r}")
    return html.unescape(match.group(1)), match.group(2)


class CompetitorLandscapeTests(unittest.TestCase):
    def test_landscape_meets_issue_acceptance_floor(self) -> None:
        paths = sorted(RECORDS_DIR.glob("*.yaml"))
        self.assertGreaterEqual(len(paths), 25)
        records = [load_yaml(path) for path in paths]
        self.assertGreaterEqual(
            sum(
                record["classification"]["class"] == "substitute" for record in records
            ),
            5,
        )
        for record in records:
            with self.subTest(record=record["identity"]["product"]):
                self.assertTrue(record["sources"]["primary"])
                self.assertTrue(record["market"]["buyer"])
                self.assertTrue(record["market"]["user"])
                self.assertTrue(record["market"]["trigger"])
                self.assertTrue(record["product"]["outputs"])
                verified_at = dt.date.fromisoformat(
                    record["observation"]["last_verified_at"]
                )
                next_review_at = dt.date.fromisoformat(
                    record["observation"]["next_review_at"]
                )
                self.assertGreater(next_review_at, verified_at)
                self.assertTrue(record["assessment"]["claim_types"]["facts"])
                self.assertTrue(record["assessment"]["claim_types"]["inferences"])
                self.assertTrue(record["assessment"]["claim_types"]["hypotheses"])
                self.assertEqual(
                    record["publication"]["reproducibility_review"], "approved"
                )
                for source in record["sources"]["primary"]:
                    self.assertTrue(source["url"].startswith("https://"))
                    self.assertTrue(source["title"])
                    self.assertTrue(source["publisher"])
                    self.assertIn("published_at", source)
                    self.assertEqual(
                        source["accessed_at"], record["observation"]["last_verified_at"]
                    )

    def test_landscape_covers_privacy_first_matching_products_conservatively(
        self,
    ) -> None:
        records = [load_yaml(path) for path in sorted(RECORDS_DIR.glob("*.yaml"))]
        by_product = {record["identity"]["product"]: record for record in records}
        expected = {"ZERONEAR", "Heyoosh Engine", "Voxhu"}
        self.assertTrue(expected <= by_product.keys())
        for product in expected:
            with self.subTest(product=product):
                record = by_product[product]
                self.assertIn(
                    record["classification"]["class"], {"adjacent", "potential"}
                )
                self.assertIn(record["classification"]["confidence"], {"low", "medium"})
                self.assertNotEqual(record["classification"]["class"], "direct")
                self.assertTrue(record["assessment"]["limitations_or_unknowns"])
                self.assertIn(
                    "published material only",
                    " ".join(record["privacy_and_security"]["audit_and_assurance"]),
                )

    def test_index_generation_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            records_dir = root / "records" / "competitors"
            records_dir.mkdir(parents=True)
            for name, record in (
                ("b.yaml", index_record("Beta", "Two")),
                ("a.yaml", index_record("Alpha", "One")),
            ):
                (records_dir / name).write_text(
                    yaml.safe_dump(record, sort_keys=False), encoding="utf-8"
                )
            output = root / "landscape" / "competitor-index.md"
            records = load_records(records_dir)
            first = render_index(records, output)
            second = render_index(load_records(records_dir), output)
            self.assertEqual(first, second)
            self.assertLess(first.index("Alpha"), first.index("Beta"))

    def test_product_closing_bracket_cannot_close_link_label(self) -> None:
        _row, cells = render_identity("Organization", "Product]name")
        label, _target = parse_product_link(cells[1])
        self.assertEqual(label, "Product]name")
        self.assertIn("Product&#93;name", cells[1])

    def test_product_opening_bracket_is_literal_link_label_text(self) -> None:
        _row, cells = render_identity("Organization", "Product[name")
        label, _target = parse_product_link(cells[1])
        self.assertEqual(label, "Product[name")
        self.assertIn("Product&#91;name", cells[1])

    def test_product_backslash_is_literal_link_label_text(self) -> None:
        _row, cells = render_identity("Organization", r"Product\name")
        label, _target = parse_product_link(cells[1])
        self.assertEqual(label, r"Product\name")
        self.assertIn("Product&#92;name", cells[1])

    def test_identity_pipes_do_not_create_table_columns(self) -> None:
        _row, cells = render_identity("Org|unit", "Product|edition")
        self.assertEqual(len(cells), 7)
        self.assertEqual(html.unescape(cells[0]), "Org|unit")
        label, _target = parse_product_link(cells[1])
        self.assertEqual(label, "Product|edition")

    def test_lf_is_normalized_to_an_inline_space(self) -> None:
        row, cells = render_identity("Org\nunit", "Product\nname")
        self.assertNotIn("\n", row)
        self.assertEqual(html.unescape(cells[0]), "Org unit")
        self.assertEqual(parse_product_link(cells[1])[0], "Product name")

    def test_cr_is_normalized_to_an_inline_space(self) -> None:
        row, cells = render_identity("Org\runit", "Product\rname")
        self.assertNotIn("\r", row)
        self.assertEqual(html.unescape(cells[0]), "Org unit")
        self.assertEqual(parse_product_link(cells[1])[0], "Product name")

    def test_crlf_is_normalized_to_one_inline_space(self) -> None:
        row, cells = render_identity("Org\r\nunit", "Product\r\nname")
        self.assertNotIn("\r", row)
        self.assertNotIn("\n", row)
        self.assertEqual(html.unescape(cells[0]), "Org unit")
        self.assertEqual(parse_product_link(cells[1])[0], "Product name")

    def test_other_inline_control_characters_are_normalized(self) -> None:
        _row, cells = render_identity("Org\tunit", "Product\x7fname")
        self.assertEqual(html.unescape(cells[0]), "Org unit")
        self.assertEqual(parse_product_link(cells[1])[0], "Product name")

    def test_unpaired_surrogate_is_replaced_with_visible_marker(self) -> None:
        row, cells = render_identity("Organization", "Product\ud800name")
        self.assertEqual(
            parse_product_link(cells[1])[0], "Product\N{REPLACEMENT CHARACTER}name"
        )
        row.encode("utf-8")

    def test_special_identity_generation_is_deterministic(self) -> None:
        identity = ("Org|[unit]\\\r\n", "Product|[edition]\\\r\n")
        first = render_identity(*identity)[0]
        second = render_identity(*identity)[0]
        self.assertEqual(first, second)

    def test_special_identity_strings_remain_schema_valid(self) -> None:
        source = load_yaml(RECORDS_DIR / "acompany-autoprivacy-dcr.yaml")
        source["identity"]["organization"] = "Org|[unit]\\\r\n"
        source["identity"]["product"] = "Product|[edition]\\\r\n"
        schema = json.loads(
            (ROOT / "schema" / "competitor-record.schema.json").read_text(
                encoding="utf-8"
            )
        )
        Draft202012Validator(schema).validate(source)

    def test_special_identity_preserves_seven_table_columns(self) -> None:
        _row, cells = render_identity("Org|[unit]\\\r\n", "Product|[edition]\\\r\n")
        self.assertEqual(len(cells), 7)

    def test_product_link_target_remains_the_record_path(self) -> None:
        _row, cells = render_identity("Organization", "Product|[edition]\\\r\n")
        _label, target = parse_product_link(cells[1])
        self.assertEqual(target, "../records/competitors/special.yaml")

    def test_product_cannot_inject_another_link_html_or_inline_markup(self) -> None:
        product = "Name](https://attacker.example)[<script>*_`~"
        row, cells = render_identity("Organization", product)
        label, target = parse_product_link(cells[1])
        self.assertEqual(label, product)
        self.assertEqual(target, "../records/competitors/special.yaml")
        self.assertEqual(row.count("](../records/competitors/special.yaml)"), 1)
        self.assertNotIn("<script>", row)
        self.assertNotIn("](", cells[1].split("](../records", 1)[0])

    def test_generated_special_identity_local_link_is_validated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record_path = root / "records" / "competitors" / "special.yaml"
            record_path.parent.mkdir(parents=True)
            record_path.write_text("record_type: competitor\n", encoding="utf-8")
            output = root / "landscape" / "competitor-index.md"
            output.parent.mkdir(parents=True)
            rendered = render_index(
                [
                    (
                        record_path,
                        index_record("Org|[unit]\\\r\n", "Product|[edition]\\\r\n"),
                    )
                ],
                output,
            )
            output.write_text(rendered, encoding="utf-8")
            findings, _urls = validate_markdown_links(root)
            self.assertEqual(findings, [])

            record_path.unlink()
            missing_findings, _urls = validate_markdown_links(root)
            self.assertTrue(
                any(item.code == "broken-local-link" for item in missing_findings)
            )

    def test_duplicate_identity_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            records_dir = Path(tmp)
            record = index_record("Alpha", "One")
            (records_dir / "one.yaml").write_text(
                yaml.safe_dump(record), encoding="utf-8"
            )
            duplicate = copy.deepcopy(record)
            (records_dir / "two.yaml").write_text(
                yaml.safe_dump(duplicate), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "duplicate organization/product"):
                load_records(records_dir)

    def test_check_mode_detects_stale_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            records_dir = root / "records" / "competitors"
            records_dir.mkdir(parents=True)
            (records_dir / "one.yaml").write_text(
                yaml.safe_dump(index_record("Alpha", "One")), encoding="utf-8"
            )
            output = root / "landscape" / "competitor-index.md"
            output.parent.mkdir(parents=True)
            output.write_text("stale\n", encoding="utf-8")
            result = main(["--root", str(root), "--minimum-count", "1", "--check"])
            self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
