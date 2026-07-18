#!/usr/bin/env python3
"""Validate public Private Match research records and documentation."""

from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import datetime as dt
import json
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator, FormatChecker


class NoDatesSafeLoader(yaml.SafeLoader):
    """Safe YAML loader that leaves ISO dates as strings for JSON Schema."""


for first_char, resolvers in list(NoDatesSafeLoader.yaml_implicit_resolvers.items()):
    NoDatesSafeLoader.yaml_implicit_resolvers[first_char] = [
        entry for entry in resolvers if entry[0] != "tag:yaml.org,2002:timestamp"
    ]


@dataclasses.dataclass(frozen=True)
class Finding:
    severity: str  # error | warning | info
    code: str
    path: str
    message: str


SCHEMA_FILES = {
    "competitor": "competitor-record.schema.json",
    "technology": "technology-record.schema.json",
    "public-use-case-finding": "public-use-case-finding.schema.json",
}

RECORD_ROOT = "records"
EXCLUDED_DIRS = {".git", ".venv", "artifacts", "__pycache__", "node_modules"}
REVIEW_APPROVED = {"approved", "not-required"}
RISKY_PATTERNS = {
    "secure": re.compile(r"\bsecure\b|安全(?:です|である|性を保証)", re.IGNORECASE),
    "proven": re.compile(r"\bproven\b|証明済み|数学的に証明", re.IGNORECASE),
    "zero-leakage": re.compile(r"zero[ -]?leakage|漏えい(?:は)?ゼロ|情報漏えいなし", re.IGNORECASE),
    "anonymous": re.compile(r"\banonymous\b|完全匿名", re.IGNORECASE),
    "compliant": re.compile(r"\bcompliant\b|法令準拠|規制準拠", re.IGNORECASE),
    "world-first": re.compile(r"world(?:'s)? first|世界初", re.IGNORECASE),
    "no-competitor": re.compile(r"no competitors?|競合(?:は)?(?:存在し)?ない", re.IGNORECASE),
    "production-ready": re.compile(r"production[ -]?ready|本番(?:対応|準備完了)", re.IGNORECASE),
}
NEGATING_CONTEXT = re.compile(
    r"\b(?:not|no|does not|do not|cannot|isn't|aren't|without|non-goal)\b|"
    r"(?:ではない|しない|できない|禁止|未対応|非目標|主張しない)",
    re.IGNORECASE,
)
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
RAW_URL_RE = re.compile(r"https://[^\s<>()\]\[\"']+")


def _iter_files(root: Path, suffixes: set[str]) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        yield path


def _relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.load(handle, Loader=NoDatesSafeLoader)


def load_schemas(root: Path) -> dict[str, Draft202012Validator]:
    validators: dict[str, Draft202012Validator] = {}
    for record_type, filename in SCHEMA_FILES.items():
        schema_path = root / "schema" / filename
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validators[record_type] = Draft202012Validator(schema, format_checker=FormatChecker())
    return validators


def validate_yaml_syntax(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _iter_files(root, {".yaml", ".yml"}):
        try:
            load_yaml(path)
        except Exception as exc:
            findings.append(Finding("error", "yaml-parse", _relative(path, root), str(exc)))
    return findings


def _json_path(error: Any) -> str:
    parts = [str(item) for item in error.absolute_path]
    return ".".join(parts) if parts else "$"


def _parse_date(value: Any) -> dt.date | None:
    if not isinstance(value, str):
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def _publication_gate(record: dict[str, Any], path: str) -> list[Finding]:
    findings: list[Finding] = []
    publication = record.get("publication")
    if not isinstance(publication, dict):
        return findings

    required_approved = ["source_check", "freshness_check", "privacy_review", "claims_review"]
    conditional = ["ip_review", "security_review"]
    if record.get("record_type") == "public-use-case-finding":
        required_approved.append("anonymization_review")

    for field in required_approved:
        if publication.get(field) != "approved":
            findings.append(
                Finding(
                    "error",
                    "publication-gate",
                    path,
                    f"publication.{field} must be 'approved' for a public record",
                )
            )
    for field in conditional:
        if publication.get(field) not in REVIEW_APPROVED:
            findings.append(
                Finding(
                    "error",
                    "publication-gate",
                    path,
                    f"publication.{field} must be 'approved' or 'not-required' for a public record",
                )
            )
    return findings


def _date_consistency(record: dict[str, Any], path: str, today: dt.date, stale_policy: str) -> list[Finding]:
    findings: list[Finding] = []
    observation = record.get("observation")
    if not isinstance(observation, dict):
        return findings
    observed = _parse_date(observation.get("observed_at"))
    verified = _parse_date(observation.get("last_verified_at"))
    review = _parse_date(observation.get("next_review_at"))
    if observed and verified and observed > verified:
        findings.append(Finding("error", "date-order", path, "observed_at must not be after last_verified_at"))
    if verified and verified > today:
        findings.append(Finding("error", "future-verification", path, "last_verified_at must not be in the future"))
    if verified and review and review < verified:
        findings.append(Finding("error", "date-order", path, "next_review_at must not be before last_verified_at"))
    if review and review < today:
        severity = "error" if stale_policy == "fail" else "warning"
        findings.append(Finding(severity, "stale-record", path, f"next_review_at {review.isoformat()} is overdue"))
    return findings


def validate_records(
    root: Path, stale_policy: str, today: dt.date | None = None
) -> tuple[list[Finding], list[dict[str, Any]]]:
    today = today or dt.datetime.now(dt.timezone.utc).date()
    validators = load_schemas(root)
    findings: list[Finding] = []
    records: list[dict[str, Any]] = []
    records_root = root / RECORD_ROOT
    if not records_root.exists():
        return findings, records

    for path in _iter_files(records_root, {".yaml", ".yml"}):
        rel = _relative(path, root)
        try:
            raw = load_yaml(path)
        except Exception:
            continue
        if not isinstance(raw, dict):
            findings.append(Finding("error", "record-shape", rel, "record must be a YAML mapping"))
            continue
        record_type = raw.get("record_type")
        validator = validators.get(record_type)
        if validator is None:
            findings.append(Finding("error", "unknown-record-type", rel, f"unsupported record_type: {record_type!r}"))
            continue
        for error in sorted(validator.iter_errors(raw), key=lambda item: list(item.absolute_path)):
            findings.append(Finding("error", "schema", rel, f"{_json_path(error)}: {error.message}"))
        findings.extend(_date_consistency(raw, rel, today, stale_policy))
        findings.extend(_publication_gate(raw, rel))
        records.append(raw)
    return findings, records


def _extract_source_urls(record: Any) -> set[str]:
    urls: set[str] = set()
    if isinstance(record, dict):
        for key, value in record.items():
            if key == "url" and isinstance(value, str):
                urls.add(value)
            elif key in {"canonical_url", "source"} and isinstance(value, str) and value.startswith("https://"):
                urls.add(value)
            else:
                urls.update(_extract_source_urls(value))
    elif isinstance(record, list):
        for value in record:
            if isinstance(value, str) and value.startswith("https://"):
                urls.add(value)
            else:
                urls.update(_extract_source_urls(value))
    return urls


def validate_markdown_links(root: Path) -> tuple[list[Finding], set[str]]:
    findings: list[Finding] = []
    external_urls: set[str] = set()
    for path in _iter_files(root, {".md"}):
        rel = _relative(path, root)
        text = path.read_text(encoding="utf-8")
        for _label, target_raw in MARKDOWN_LINK_RE.findall(text):
            target = target_raw.strip().split()[0].strip("<>")
            if not target:
                findings.append(Finding("error", "markdown-link", rel, "empty Markdown link target"))
                continue
            parsed = urllib.parse.urlparse(target)
            if parsed.scheme in {"http", "https"}:
                if parsed.scheme != "https":
                    findings.append(Finding("warning", "insecure-url", rel, f"non-HTTPS external link: {target}"))
                external_urls.add(target)
            elif parsed.scheme in {"mailto", "tel"} or target.startswith("#"):
                continue
            elif parsed.scheme:
                findings.append(Finding("error", "markdown-link", rel, f"unsupported link scheme: {target}"))
            else:
                local_part = urllib.parse.unquote(target.split("#", 1)[0])
                if not local_part:
                    continue
                candidate = (path.parent / local_part).resolve()
                try:
                    candidate.relative_to(root.resolve())
                except ValueError:
                    findings.append(Finding("error", "markdown-link", rel, f"link escapes repository: {target}"))
                    continue
                if not candidate.exists():
                    findings.append(Finding("error", "broken-local-link", rel, f"missing local target: {target}"))
        external_urls.update(RAW_URL_RE.findall(text))
    return findings, external_urls


def lint_claims(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _iter_files(root, {".md", ".yaml", ".yml"}):
        rel = _relative(path, root)
        text = path.read_text(encoding="utf-8")
        in_fenced_block = False
        in_ignore_block = False
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if "<!-- claim-lint: ignore-start -->" in line:
                in_ignore_block = True
                continue
            if "<!-- claim-lint: ignore-end -->" in line:
                in_ignore_block = False
                continue
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fenced_block = not in_fenced_block
                continue
            if in_ignore_block or in_fenced_block:
                continue
            if NEGATING_CONTEXT.search(line):
                continue
            for code, pattern in RISKY_PATTERNS.items():
                if pattern.search(line):
                    findings.append(
                        Finding(
                            "warning",
                            f"risky-claim-{code}",
                            rel,
                            f"line {line_no}: risky claim wording requires scoped evidence and claims review",
                        )
                    )
    return findings


def collect_record_urls(records: Iterable[dict[str, Any]]) -> set[str]:
    urls: set[str] = set()
    for record in records:
        urls.update(_extract_source_urls(record))
    return urls


def check_url(url: str, timeout: float) -> tuple[str, str]:
    request = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "private-match-research-quality/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return "ok", f"HTTP {response.status}"
    except urllib.error.HTTPError as exc:
        if exc.code in {405, 501}:
            try:
                get_request = urllib.request.Request(
                    url,
                    method="GET",
                    headers={"User-Agent": "private-match-research-quality/0.1", "Range": "bytes=0-0"},
                )
                with urllib.request.urlopen(get_request, timeout=timeout) as response:
                    return "ok", f"HTTP {response.status}"
            except Exception as get_exc:
                exc = get_exc
        if isinstance(exc, urllib.error.HTTPError):
            if exc.code in {404, 410}:
                return "http-failure", f"HTTP {exc.code} (missing or gone)"
            return "http-failure", f"HTTP {exc.code}"
        return "network-failure", str(exc)
    except (urllib.error.URLError, TimeoutError, socket.timeout, ConnectionError) as exc:
        return "network-failure", str(exc)
    except Exception as exc:
        return "network-failure", f"unexpected network error: {exc}"


def check_urls(urls: Iterable[str], timeout: float, policy: str) -> list[Finding]:
    unique = sorted(set(urls))
    findings: list[Finding] = []
    if not unique:
        return findings
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, len(unique))) as executor:
        future_map = {executor.submit(check_url, url, timeout): url for url in unique}
        for future in concurrent.futures.as_completed(future_map):
            url = future_map[future]
            status, detail = future.result()
            if status == "ok":
                continue
            severity = "error" if policy == "fail" and status == "http-failure" else "warning"
            findings.append(Finding(severity, status, url, detail))
    return findings


def render_markdown(findings: list[Finding], records_count: int, checked_urls: int) -> str:
    counts = {name: sum(1 for item in findings if item.severity == name) for name in ("error", "warning", "info")}
    lines = [
        "# Research Quality Report",
        "",
        f"- generated_at: {dt.datetime.now(dt.timezone.utc).isoformat()}",
        f"- structured_records: {records_count}",
        f"- external_urls_checked: {checked_urls}",
        f"- errors: {counts['error']}",
        f"- warnings: {counts['warning']}",
        f"- info: {counts['info']}",
        "",
    ]
    if not findings:
        lines.append("No findings.")
        return "\n".join(lines) + "\n"
    lines.extend(["| Severity | Code | Path / URL | Message |", "|---|---|---|---|"])
    for item in sorted(findings, key=lambda x: (x.severity != "error", x.severity != "warning", x.path, x.code, x.message)):
        message = item.message.replace("|", "\\|").replace("\n", " ")
        path = item.path.replace("|", "\\|")
        lines.append(f"| {item.severity} | `{item.code}` | `{path}` | {message} |")
    return "\n".join(lines) + "\n"


def write_reports(report_dir: Path, findings: list[Finding], records_count: int, checked_urls: int) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "structured_records": records_count,
        "external_urls_checked": checked_urls,
        "summary": {
            "errors": sum(1 for item in findings if item.severity == "error"),
            "warnings": sum(1 for item in findings if item.severity == "warning"),
            "info": sum(1 for item in findings if item.severity == "info"),
        },
        "findings": [dataclasses.asdict(item) for item in findings],
    }
    (report_dir / "research-quality-report.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (report_dir / "research-quality-report.md").write_text(
        render_markdown(findings, records_count, checked_urls), encoding="utf-8"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--report-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--stale-policy", choices=("warn", "fail"), default="warn")
    parser.add_argument("--check-urls", action="store_true")
    parser.add_argument("--url-policy", choices=("warn", "fail"), default="warn")
    parser.add_argument("--url-timeout", type=float, default=5.0)
    parser.add_argument("--today", help="Override current UTC date for tests (YYYY-MM-DD)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    report_dir = args.report_dir if args.report_dir.is_absolute() else root / args.report_dir
    today = dt.date.fromisoformat(args.today) if args.today else dt.datetime.now(dt.timezone.utc).date()

    findings: list[Finding] = []
    findings.extend(validate_yaml_syntax(root))
    record_findings, records = validate_records(root, args.stale_policy, today=today)
    findings.extend(record_findings)
    markdown_findings, markdown_urls = validate_markdown_links(root)
    findings.extend(markdown_findings)
    findings.extend(lint_claims(root))

    urls = collect_record_urls(records) | markdown_urls
    checked_urls = 0
    if args.check_urls:
        checked_urls = len(urls)
        findings.extend(check_urls(urls, args.url_timeout, args.url_policy))

    write_reports(report_dir, findings, len(records), checked_urls)

    errors = sum(1 for item in findings if item.severity == "error")
    warnings = sum(1 for item in findings if item.severity == "warning")
    print(f"research-quality: records={len(records)} errors={errors} warnings={warnings} report={report_dir}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
