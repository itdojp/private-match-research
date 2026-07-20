"""Shared fail-closed checks for direct-competitor designation approval."""

from __future__ import annotations

import datetime as dt
import re
from typing import Any


DIRECT_DESIGNATION_APPROVAL_ERROR = "direct-designation-approval"
DIRECT_DESIGNATION_AUTHORITY = "authorized-itdo-human"

# Accept only a repository-scoped GitHub reference to a concrete review or
# comment. The automated check validates structure and scope; a human reviewer
# still has to verify the referenced author's authority and approval scope.
DIRECT_DESIGNATION_EVIDENCE_RE = re.compile(
    r"https://github\.com/itdojp/private-match-research/"
    r"(?:"
    r"pull/[1-9][0-9]*#(?:"
    r"pullrequestreview-[1-9][0-9]*|"
    r"discussion_r[1-9][0-9]*|"
    r"issuecomment-[1-9][0-9]*"
    r")|"
    r"issues/[1-9][0-9]*#issuecomment-[1-9][0-9]*"
    r")"
)


def _approval_date(value: Any) -> dt.date | None:
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value
    ):
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def direct_designation_approval_errors(
    record: dict[str, Any], *, today: dt.date | None = None
) -> list[str]:
    """Return stable semantic errors for a competitor classification approval."""
    classification = record.get("classification")
    if not isinstance(classification, dict):
        return []

    classification_class = classification.get("class")
    has_approval = "direct_designation_approval" in classification
    approval = classification.get("direct_designation_approval")

    if classification_class != "direct":
        if has_approval:
            return [
                "classification.direct_designation_approval is forbidden unless "
                "classification.class is 'direct'"
            ]
        return []

    if not isinstance(approval, dict):
        return [
            "classification.direct_designation_approval must be a record-scoped "
            "approval object for a 'direct' classification"
        ]

    errors: list[str] = []
    allowed_fields = {"status", "authority", "approved_at", "evidence_url"}
    extra_fields = sorted(set(approval) - allowed_fields)
    if extra_fields:
        errors.append(
            "classification.direct_designation_approval contains unsupported "
            f"field(s): {', '.join(extra_fields)}"
        )
    if approval.get("status") != "approved":
        errors.append(
            "classification.direct_designation_approval.status must be 'approved'"
        )
    if approval.get("authority") != DIRECT_DESIGNATION_AUTHORITY:
        errors.append(
            "classification.direct_designation_approval.authority must be "
            f"'{DIRECT_DESIGNATION_AUTHORITY}'"
        )

    approved_at = _approval_date(approval.get("approved_at"))
    if approved_at is None:
        errors.append(
            "classification.direct_designation_approval.approved_at must be a valid "
            "YYYY-MM-DD date"
        )
    elif approved_at > (today or dt.datetime.now(dt.timezone.utc).date()):
        errors.append(
            "classification.direct_designation_approval.approved_at must not be in "
            "the future"
        )

    evidence_url = approval.get("evidence_url")
    if (
        not isinstance(evidence_url, str)
        or DIRECT_DESIGNATION_EVIDENCE_RE.fullmatch(evidence_url) is None
    ):
        errors.append(
            "classification.direct_designation_approval.evidence_url must identify "
            "a concrete review or comment in itdojp/private-match-research"
        )
    return errors
