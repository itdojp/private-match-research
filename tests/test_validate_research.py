from __future__ import annotations

import copy
import datetime as dt
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.validate_research import (
    lint_claims,
    load_schemas,
    load_yaml,
    validate_records,
)


ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_DIRECT_EVIDENCE_URL = (
    "https://github.com/itdojp/private-match-research/"
    "pull/999999#discussion_r999999999"
)


def direct_designation_approval() -> dict:
    """Return synthetic structure only; this is not evidence of human approval."""
    return {
        "status": "approved",
        "authority": "authorized-itdo-human",
        "approved_at": "2026-07-20",
        "evidence_url": SYNTHETIC_DIRECT_EVIDENCE_URL,
    }


def competitor_record() -> dict:
    return {
        "schema_version": "0.1",
        "record_type": "competitor",
        "identity": {
            "organization": "Example Corp",
            "product": "Example Clean Room",
            "canonical_url": "https://example.com/product",
            "country_or_region": "Global",
        },
        "observation": {
            "observed_at": "2026-07-01",
            "last_verified_at": "2026-07-18",
            "next_review_at": "2026-10-18",
            "source_status": "current",
        },
        "classification": {
            "class": "adjacent",
            "confidence": "medium",
            "rationale": "Broader workflow with a different primary output.",
        },
        "market": {
            "buyer": ["Data partnership leader"],
            "user": ["Data analyst"],
            "trigger": ["Cross-organization analysis"],
            "jobs_to_be_done": ["Analyze overlapping populations"],
            "current_alternatives": ["NDA and spreadsheet exchange"],
            "pricing": {"public": False, "model": "unknown", "amount": "", "source": ""},
            "deployment_lead_time": "unknown",
        },
        "product": {
            "inputs": ["Customer identifiers"],
            "outputs": ["Aggregate query result"],
            "workflow": ["Configure collaboration"],
            "deployment": ["Cloud service"],
            "prerequisites": ["Cloud account"],
            "data_movement": "controlled environment",
            "data_retention": "unknown",
        },
        "privacy_and_security": {
            "published_technologies": ["Policy-controlled clean room"],
            "trust_model": "vendor-operated service",
            "attacker_model": "unknown",
            "raw_data_access": "documented restrictions",
            "metadata_leakage": ["Input size may be observable"],
            "repeated_query_controls": "policy dependent",
            "minimum_aggregation_controls": "configurable",
            "audit_and_assurance": ["Official documentation"],
        },
        "assessment": {
            "strengths": ["Broad analytics"],
            "limitations_or_unknowns": ["Public pricing unavailable"],
            "implications_for_private_match": ["Differentiate on setup time and minimum output"],
            "claim_types": {
                "facts": ["The product is documented by its vendor."],
                "inferences": ["The workflow appears broader than Private Match."],
                "hypotheses": ["A narrow preflight may reduce setup time."],
            },
        },
        "sources": {
            "primary": [
                {
                    "url": "https://example.com/product",
                    "title": "Product documentation",
                    "publisher": "Example Corp",
                    "published_at": None,
                    "accessed_at": "2026-07-18",
                }
            ],
            "secondary": [],
        },
        "publication": {
            "classification": "public",
            "source_check": "approved",
            "freshness_check": "approved",
            "ip_review": "not-required",
            "security_review": "not-required",
            "privacy_review": "approved",
            "claims_review": "approved",
            "reproducibility_review": "approved",
        },
    }


def technology_record() -> dict:
    return {
        "schema_version": "0.1",
        "record_type": "technology",
        "identity": {
            "name": "Example VOPRF",
            "category": "OPRF",
            "implementation_or_standard": "Example implementation",
            "canonical_url": "https://example.com/voprf",
        },
        "observation": {
            "observed_at": "2026-07-01",
            "last_verified_at": "2026-07-18",
            "next_review_at": "2026-10-18",
            "maturity": "experimental",
        },
        "problem_fit": {
            "supported_results": ["membership"],
            "party_model": ["client-server"],
            "data_profiles": ["low-entropy-identifiers"],
            "target_use_cases": ["Private identifier tokenization"],
            "non_fit": ["General computation"],
        },
        "security": {
            "security_model": "semi-honest",
            "cryptographic_assumptions": ["Discrete logarithm assumption"],
            "trusted_components": [],
            "collusion_threshold": "unknown",
            "input_authenticity": "external control required",
            "omission_resistance": "external control required",
            "replay_and_session_binding": "application protocol required",
            "metadata_leakage": ["Request timing"],
            "repeated_query_risk": ["Requires rate and query controls"],
            "known_attacks_or_limitations": ["Endpoint compromise is out of scope"],
        },
        "engineering": {
            "languages": ["Rust"],
            "platforms": ["Linux"],
            "deployment_models": ["client-server"],
            "computation_profile": "unknown",
            "communication_profile": "unknown",
            "artifact_size_profile": "unknown",
            "operational_complexity": "medium",
            "key_or_setup_requirements": ["Server key"],
        },
        "assurance": {
            "standards": [],
            "papers": [],
            "formal_analysis": [],
            "external_audits": [],
            "test_vectors": [],
            "interoperability": [],
        },
        "project_health": {
            "license": "Apache-2.0",
            "patent_considerations": "review required",
            "latest_release": "unknown",
            "maintenance_status": "active",
            "bus_factor": "unknown",
            "security_reporting": "documented",
        },
        "assessment": {
            "strengths": ["Protects client input from the server under its security model"],
            "limitations_or_unknowns": ["Malicious security not established"],
            "recommended_experiments": ["Tokenization correctness and replay tests"],
            "private_match_fit": "candidate for bounded experiment",
            "confidence": "low",
        },
        "sources": {"primary": ["https://example.com/voprf"], "secondary": []},
        "publication": {
            "classification": "public",
            "source_check": "approved",
            "freshness_check": "approved",
            "ip_review": "approved",
            "security_review": "approved",
            "privacy_review": "approved",
            "claims_review": "approved",
            "reproducibility_review": "approved",
        },
    }


def public_finding_record() -> dict:
    return {
        "schema_version": "0.1",
        "record_type": "public-use-case-finding",
        "identity": {"id": "H1-FINDING-001", "title": "Anonymized workflow finding", "domain": "professional services"},
        "observation": {
            "observed_at": "2026-07-01",
            "last_verified_at": "2026-07-18",
            "next_review_at": "2026-10-18",
            "source_status": "current",
        },
        "study": {
            "evidence_level": "E2",
            "method": ["Anonymized interviews"],
            "sample_size": 5,
            "population": ["Process owners"],
            "anonymization": "Aggregated with identifiers removed.",
        },
        "finding": {
            "buyer": ["Risk leader"],
            "user": ["Workflow operator"],
            "trigger": ["New engagement"],
            "current_workflow": ["Internal database and manual review"],
            "minimum_useful_output": ["Potential conflict requiring manual review"],
            "unacceptable_disclosures": ["Unmatched identities"],
            "disconfirming_findings": ["Some organizations require immediate identity disclosure"],
            "limitations": ["Small non-random sample"],
        },
        "claim_types": {
            "facts": ["Five relevant interviews were completed."],
            "inferences": ["A preflight may be useful before identity reveal."],
            "hypotheses": ["A paid workflow requires further validation."],
        },
        "sources": {
            "primary": [
                {
                    "url": "https://example.com/methodology",
                    "title": "Public methodology note",
                    "publisher": "ITDO Inc.",
                    "published_at": "2026-07-18",
                    "accessed_at": "2026-07-18",
                }
            ],
            "secondary": [],
        },
        "publication": {
            "classification": "public",
            "source_check": "approved",
            "freshness_check": "approved",
            "ip_review": "not-required",
            "security_review": "not-required",
            "privacy_review": "approved",
            "claims_review": "approved",
            "reproducibility_review": "approved",
            "anonymization_review": "approved",
        },
    }


class ResearchValidationTests(unittest.TestCase):
    def schema_errors(self, record: dict) -> list:
        validator = load_schemas(ROOT)[record["record_type"]]
        return list(validator.iter_errors(record))

    def direct_approval_findings(
        self, record: dict, *, today: dt.date = dt.date(2026, 7, 20)
    ) -> list:
        with tempfile.TemporaryDirectory(
            prefix=".codex-test-direct-approval-", dir=ROOT
        ) as tmp:
            repo = Path(tmp)
            shutil.copytree(ROOT / "schema", repo / "schema")
            records = repo / "records" / "competitors"
            records.mkdir(parents=True)
            (records / "synthetic.yaml").write_text(
                yaml.safe_dump(record, sort_keys=False), encoding="utf-8"
            )
            findings, _parsed = validate_records(repo, "warn", today=today)
        return [item for item in findings if item.code == "direct-designation-approval"]

    def test_custom_yaml_loader_does_not_change_safe_loader_dates(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix=".codex-test-yaml-loader-", dir=ROOT
        ) as tmp:
            path = Path(tmp) / "date.yaml"
            path.write_text("observed_at: 2026-07-18\n", encoding="utf-8")

            custom = load_yaml(path)
            standard = yaml.safe_load(path.read_text(encoding="utf-8"))

        self.assertEqual(custom["observed_at"], "2026-07-18")
        self.assertIsInstance(custom["observed_at"], str)
        self.assertEqual(standard["observed_at"], dt.date(2026, 7, 18))
        self.assertIsInstance(standard["observed_at"], dt.date)

    def test_schemas_are_valid(self) -> None:
        validators = load_schemas(ROOT)
        self.assertEqual(set(validators), {"competitor", "technology", "public-use-case-finding"})

    def test_valid_records_pass_schema(self) -> None:
        validators = load_schemas(ROOT)
        for record in (competitor_record(), technology_record(), public_finding_record()):
            errors = list(validators[record["record_type"]].iter_errors(record))
            self.assertEqual(errors, [], [error.message for error in errors])

    def test_invalid_records_fail_for_expected_reason(self) -> None:
        validators = load_schemas(ROOT)
        cases = []
        missing_primary = competitor_record()
        missing_primary["sources"]["primary"] = []
        cases.append((missing_primary, "should be non-empty"))
        invalid_class = competitor_record()
        invalid_class["classification"]["class"] = "monopoly"
        cases.append((invalid_class, "is not one of"))
        missing_date = technology_record()
        del missing_date["observation"]["observed_at"]
        cases.append((missing_date, "is a required property"))
        missing_reproducibility_review = public_finding_record()
        del missing_reproducibility_review["publication"][
            "reproducibility_review"
        ]
        cases.append((missing_reproducibility_review, "is a required property"))

        for record, message in cases:
            errors = list(validators[record["record_type"]].iter_errors(record))
            self.assertTrue(errors)
            self.assertTrue(any(message in error.message for error in errors), [error.message for error in errors])

    def test_direct_without_approval_fails_schema_and_semantic_validation(self) -> None:
        record = competitor_record()
        record["classification"]["class"] = "direct"
        self.assertTrue(self.schema_errors(record))
        self.assertTrue(self.direct_approval_findings(record))

    def test_claims_review_alone_does_not_approve_direct_designation(self) -> None:
        record = competitor_record()
        record["classification"]["class"] = "direct"
        self.assertEqual(record["publication"]["claims_review"], "approved")
        findings = self.direct_approval_findings(record)
        self.assertTrue(findings)
        self.assertIn("record-scoped approval object", findings[0].message)

    def test_pending_direct_approval_fails_schema_and_semantic_validation(self) -> None:
        record = competitor_record()
        record["classification"]["class"] = "direct"
        approval = direct_designation_approval()
        approval["status"] = "pending"
        record["classification"]["direct_designation_approval"] = approval
        self.assertTrue(self.schema_errors(record))
        self.assertTrue(
            any("status" in item.message for item in self.direct_approval_findings(record))
        )

    def test_wrong_direct_approval_authority_fails_validation(self) -> None:
        record = competitor_record()
        record["classification"]["class"] = "direct"
        approval = direct_designation_approval()
        approval["authority"] = "research-agent"
        record["classification"]["direct_designation_approval"] = approval
        self.assertTrue(self.schema_errors(record))
        self.assertTrue(
            any(
                "authority" in item.message
                for item in self.direct_approval_findings(record)
            )
        )

    def test_direct_evidence_without_fragment_fails_validation(self) -> None:
        record = competitor_record()
        record["classification"]["class"] = "direct"
        approval = direct_designation_approval()
        approval["evidence_url"] = (
            "https://github.com/itdojp/private-match-research/pull/999999"
        )
        record["classification"]["direct_designation_approval"] = approval
        self.assertTrue(self.schema_errors(record))
        self.assertTrue(
            any(
                "evidence_url" in item.message
                for item in self.direct_approval_findings(record)
            )
        )

    def test_direct_evidence_from_another_repository_fails_validation(self) -> None:
        record = competitor_record()
        record["classification"]["class"] = "direct"
        approval = direct_designation_approval()
        approval["evidence_url"] = (
            "https://github.com/itdojp/private-match-strategy/"
            "pull/999999#discussion_r999999999"
        )
        record["classification"]["direct_designation_approval"] = approval
        self.assertTrue(self.schema_errors(record))
        self.assertTrue(
            any(
                "evidence_url" in item.message
                for item in self.direct_approval_findings(record)
            )
        )

    def test_future_direct_approval_date_fails_semantic_validation(self) -> None:
        record = competitor_record()
        record["classification"]["class"] = "direct"
        approval = direct_designation_approval()
        approval["approved_at"] = "2026-07-21"
        record["classification"]["direct_designation_approval"] = approval
        self.assertEqual(self.schema_errors(record), [])
        self.assertTrue(
            any("future" in item.message for item in self.direct_approval_findings(record))
        )

    def test_invalid_direct_approval_date_fails_schema_and_semantics(self) -> None:
        record = competitor_record()
        record["classification"]["class"] = "direct"
        approval = direct_designation_approval()
        approval["approved_at"] = "2026-02-30"
        record["classification"]["direct_designation_approval"] = approval
        self.assertTrue(self.schema_errors(record))
        self.assertTrue(
            any(
                "valid YYYY-MM-DD" in item.message
                for item in self.direct_approval_findings(record)
            )
        )

    def test_non_direct_record_cannot_carry_direct_approval(self) -> None:
        record = competitor_record()
        record["classification"]["direct_designation_approval"] = (
            direct_designation_approval()
        )
        self.assertTrue(self.schema_errors(record))
        self.assertTrue(
            any(
                "forbidden" in item.message
                for item in self.direct_approval_findings(record)
            )
        )

    def test_valid_synthetic_direct_approval_passes_schema_and_semantics(self) -> None:
        record = competitor_record()
        record["classification"]["class"] = "direct"
        record["classification"]["direct_designation_approval"] = (
            direct_designation_approval()
        )
        self.assertEqual(self.schema_errors(record), [])
        self.assertEqual(self.direct_approval_findings(record), [])

    def test_record_validation_reports_stale_and_gate_errors(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix=".codex-test-record-validation-", dir=ROOT
        ) as tmp:
            repo = Path(tmp)
            shutil.copytree(ROOT / "schema", repo / "schema")
            records = repo / "records" / "competitors"
            records.mkdir(parents=True)
            record = copy.deepcopy(competitor_record())
            record["observation"]["next_review_at"] = "2026-07-01"
            record["publication"]["reproducibility_review"] = "pending"
            (records / "stale.yaml").write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
            findings, parsed = validate_records(repo, "warn", today=dt.date(2026, 7, 18))
            self.assertEqual(len(parsed), 1)
            self.assertTrue(any(item.code == "stale-record" and item.severity == "warning" for item in findings))
            self.assertTrue(
                any(
                    item.code == "publication-gate"
                    and item.severity == "error"
                    and "reproducibility_review" in item.message
                    for item in findings
                )
            )

    def test_claim_lint_ignores_documentation_and_fenced_examples(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix=".codex-test-claim-lint-", dir=ROOT
        ) as tmp:
            repo = Path(tmp)
            (repo / "doc.md").write_text(
                """# Claims\n\n<!-- claim-lint: ignore-start -->\n- secure\n<!-- claim-lint: ignore-end -->\n\n```text\nproduction ready\n```\n\nSource: https://secure.example.com/proven-result\n\nThis product is secure.\n""",
                encoding="utf-8",
            )
            (repo / "record.yaml").write_text(
                "source: https://secure.example.com/proven-result\n",
                encoding="utf-8",
            )
            findings = lint_claims(repo)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].code, "risky-claim-secure")


if __name__ == "__main__":
    unittest.main()
