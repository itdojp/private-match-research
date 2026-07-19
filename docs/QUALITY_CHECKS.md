# Research Quality Checks

## Scope and claim boundary

The quality validator checks public research structure, review metadata, link
targets, source availability observations, and risky wording. It does not decide
whether a factual, cryptographic, security, market, privacy, or legal claim is
substantively true.

The required local checks cover:

- YAML syntax across the repository
- structured records under `records/`
- competitor, technology, and public use-case finding JSON Schemas
- observation, verification, and review dates
- classification and confidence vocabulary
- primary-source presence
- publication-gate status
- Markdown local-link existence and external-link structural safety
- risky claim wording

External URL availability is a separate trusted observation mode.

## Supported CI environment

The reviewed lock and CI support boundary is:

- GitHub-hosted `ubuntu-24.04`
- x86_64
- CPython 3.12.13
- the default Python Package Index

The lock is resolved for CPython 3.12.13 on
`x86_64-unknown-linux-gnu`. It may install on another CPython 3.12 patch release,
but other operating systems, architectures, Python implementations, and Python
minor versions are not reviewed CI targets.

## Integrity-locked dependencies

`requirements-dev.in` contains the direct validation tools:

- jsonschema 4.26.0
- PyYAML 6.0.3
- REUSE 6.2.0

`requirements-dev.txt` contains their complete reviewed transitive graph and
allowed distribution hashes. `requirements-build.in` and
`requirements-build.txt` separately lock Poetry Core 2.3.2, which is required to
build the REUSE source distribution without an unpinned isolated build
environment.

Install into a clean environment:

```bash
python -m pip install --require-hashes -r requirements-build.txt
python -m pip install \
  --require-hashes \
  --no-build-isolation \
  -r requirements-dev.txt
```

CI uses only those commands. Exact version pins alone are not treated as an
integrity control.

### Lock renewal and deterministic regeneration

The current locks were generated with uv 0.8.22 and a cutoff that excludes
artifacts uploaded after 2026-07-19 00:00:00 UTC:

```bash
uv pip compile \
  --python-version 3.12.13 \
  --python-platform x86_64-unknown-linux-gnu \
  --exclude-newer 2026-07-19T00:00:00Z \
  --generate-hashes \
  requirements-build.in \
  --output-file requirements-build.txt

uv pip compile \
  --python-version 3.12.13 \
  --python-platform x86_64-unknown-linux-gnu \
  --exclude-newer 2026-07-19T00:00:00Z \
  --generate-hashes \
  requirements-dev.in \
  --output-file requirements-dev.txt
```

A renewal must deliberately update the direct input, cutoff, or resolver version;
review direct and transitive version/license/provenance changes; regenerate twice
and compare byte-for-byte; install into a clean supported environment with
`--require-hashes`; and rerun the complete validation suite. A lock generated for
another platform is not a substitute for a separate reviewed platform lock.

## Workflow trust separation

`.github/workflows/research-quality.yml` runs on pull requests, pushes to `main`,
and manual dispatch. Its validator invocation performs syntax, schema,
publication-gate, local-link, local external-URL structure, and claim validation
only. The local URL check rejects non-HTTPS schemes, userinfo, unapproved ports,
localhost names, and non-public literal IP addresses without resolving hostnames.
The workflow does not pass `--check-urls` and therefore makes no external
requests based on repository URLs.

`.github/workflows/research-url-observation.yml` has no `pull_request` or
`pull_request_target` trigger. It observes URLs only after trusted content is
selected by one of these events:

- push to `main`
- weekly scheduled run
- explicitly initiated `workflow_dispatch`

The CLI adds a second guard: `--check-urls` requires
`--trusted-url-observation` and refuses to run when `GITHUB_EVENT_NAME` is
`pull_request` or any unapproved GitHub event.

Both workflows retain `permissions: contents: read`, pin third-party Actions to
reviewed full commit SHAs, disable persisted checkout credentials, and install
from the same hash locks. Neither workflow publishes or deploys repository
content.

## Commands

Run unit and negative URL-safety tests:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Run required local-only repository validation:

```bash
python scripts/validate_research.py \
  --root . \
  --report-dir artifacts \
  --stale-policy warn
```

Run trusted external URL observation only after the repository content and event
are trusted:

```bash
python scripts/validate_research.py \
  --root . \
  --report-dir artifacts \
  --stale-policy warn \
  --check-urls \
  --trusted-url-observation \
  --url-policy warn \
  --url-timeout 5
```

Generated reports:

- `artifacts/research-quality-report.json`
- `artifacts/research-quality-report.md`

Reports contain status, HTTP status or bounded error detail, and source URL. They
do not contain response bodies. URL userinfo is removed before a URL is written
to a finding.

## URL destination safety

Trusted observation applies all of the following before the initial request and
every redirect request:

- HTTPS is mandatory;
- URL userinfo is forbidden;
- only port 443 is approved;
- hostnames are IDNA-normalized and trailing root dots are removed before
  localhost and literal-address checks;
- `localhost`, scoped addresses, and missing/invalid hosts are rejected;
- literal and DNS-resolved loopback, private, link-local, multicast, reserved,
  unspecified, and otherwise non-global IP addresses are rejected;
- a hostname is rejected if any usable DNS answer is non-public;
- validated public addresses are used directly for the connection while the
  original hostname is retained for TLS and HTTP, preventing an unvalidated
  second DNS lookup;
- environment HTTP proxies are disabled for the observer;
- redirects are handled manually and capped at 5;
- each request timeout is capped at 15 seconds and CI uses 5 seconds;
- a bounded GET fallback for servers that reject HEAD reads at most 64 KiB;
- response bodies are never included in reports.

Unsafe destination, excessive redirect, and oversized response findings are
always errors. `--url-policy warn` can make ordinary HTTP availability failures
warnings, but it cannot downgrade a destination-safety failure.

Unit tests inject mocked DNS and HTTP behavior. Tests never connect to loopback,
RFC1918, link-local, cloud metadata, or any other internal address.

## Finding policy

### Errors

The validator exits non-zero for:

- invalid YAML or JSON Schema usage
- unknown record types
- missing or invalid required research metadata
- invalid or escaping local links
- incomplete public publication gate
- inconsistent or future verification dates
- unsafe external URL structure or literal destination
- unsafe external URL destination
- redirect limit or response-size limit violations

### Warnings

The initial policy emits warnings for:

- overdue `next_review_at`
- ordinary external HTTP failure when URL policy is `warn`
- DNS, TLS, timeout, and other network failure
- risky claim wording

An availability failure does not prove that a source or product no longer exists.
Researchers must review and update `source_status` when evidence is superseded or
unavailable.

## Publication gate

Structured records under `records/` are public artifacts. Before merge:

- `source_check`, `freshness_check`, `privacy_review`, `claims_review`, and
  `reproducibility_review` must be `approved`;
- `ip_review` and `security_review` must be `approved` or `not-required`;
- public use-case findings also require `anonymization_review: approved`.

Templates are syntax checked but are not treated as published findings.
Patent-sensitive or trade-secret candidates stay private or embargoed until a
separate human IP and publication approval.

## Risky claim lint

The linter highlights a maintained vocabulary of high-risk assurance and market
claims. The vocabulary is shown below for documentation only:

<!-- claim-lint: ignore-start -->
- secure
- proven
- zero leakage
- anonymous
- compliant
- world first
- no competitor
- production ready
<!-- claim-lint: ignore-end -->

A warning requires human claims review and narrower wording or supporting
evidence. Negated statements are ignored where the bounded context detector
recognizes them. HTTP/HTTPS URL tokens, fenced code blocks, and explicit
documentation-ignore blocks are excluded; those exclusions must not suppress
substantive claims.

## Record locations

Use:

```text
records/competitors/
records/substitutes/
records/technologies/
records/use-cases/
```

Record validation is selected by `record_type`, not only by directory.

## Non-goals

The checks do not:

- verify vendor claims;
- verify market demand;
- establish cryptographic security;
- establish legal compliance;
- establish privacy properties;
- establish production readiness;
- decide competitor classification from technology similarity;
- publish private customer evidence.
