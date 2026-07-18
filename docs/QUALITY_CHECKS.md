# Research Quality Checks

## Scope

The quality validator checks public research artifacts without deciding whether a cryptographic, security, market, or legal claim is substantively true.

## Required checks

The command validates:

- YAML syntax across the repository
- structured records under `records/`
- competitor, technology, and public use-case finding schemas
- required observation and review dates
- competitor classification and confidence vocabulary
- at least one primary source per structured record
- public publication-gate status
- date ordering and overdue review dates
- Markdown local-link existence and external-link syntax
- risky claim wording
- optional external URL availability

## Commands

Install the validation dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

## Dependency integrity policy (v0.1)

`requirements-dev.txt` uses exact versions for the two direct validation dependencies but does not use pip hash checking in v0.1. A reviewed `--require-hashes` lock must include every transitive dependency and every artifact for each supported Python/platform combination. The project has not yet defined that support matrix or a reviewed lock-update procedure; committing a lock generated for one developer environment would provide incomplete reproducibility for the documented local and GitHub Actions workflows.

The current compensating boundaries are a GitHub-hosted ephemeral runner, read-only `contents` permission, immutable action commit pins, disabled checkout credential persistence, and no publication, deployment, private-repository, or secret requirement in this workflow. These boundaries limit repository impact but do not establish package integrity.

Residual risks remain explicit: transitive dependency versions and downloaded package bytes are not locked, dependency resolution may change without a direct-version change, and compromise of a package, publisher, or index could execute code in CI. Before expanding the workflow's permissions or treating its output as release evidence, define the supported Python/platform matrix, review and pin the complete transitive graph, record hashes for all permitted artifacts, install with `pip --require-hashes`, and document lock renewal and provenance review.

Run unit tests:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

Run required repository validation:

```bash
python scripts/validate_research.py \
  --root . \
  --report-dir artifacts \
  --stale-policy warn
```

Run external URL observation:

```bash
python scripts/validate_research.py \
  --root . \
  --report-dir artifacts \
  --stale-policy warn \
  --check-urls \
  --url-policy warn
```

Generated reports:

- `artifacts/research-quality-report.json`
- `artifacts/research-quality-report.md`

## Policy

### CI errors

The validator exits non-zero for:

- invalid YAML
- unknown record types
- JSON Schema violations
- missing observation date
- invalid competitor classification or confidence
- missing primary source
- invalid or escaping local links
- incomplete public publication gate
- inconsistent or future verification dates

### CI warnings

The initial policy emits warnings for:

- overdue `next_review_at`
- external HTTP failure
- temporary network or DNS failure
- non-HTTPS external links
- risky claim wording

This makes source staleness and network instability visible without making normal pull requests depend on a reliable external network. The stale or URL policy can be changed to `fail` through an explicit reviewed decision.

## Publication gate

Structured records under `records/` are public artifacts. Before merge:

- `source_check`, `freshness_check`, `privacy_review`, and `claims_review` must be `approved`
- `ip_review` and `security_review` must be `approved` or `not-required`
- public use-case findings also require `anonymization_review: approved`

Templates are YAML-parse checked but are not treated as publishable records.

## URL status

The URL checker reports:

- `http-failure` for HTTP errors, including missing or gone resources
- `network-failure` for timeout, DNS, TLS, connection, or temporary network errors

A URL failure does not prove that a product or source no longer exists. Researchers must review and update `source_status` when evidence is superseded or unavailable.

## Risky claim lint

The linter highlights a maintained vocabulary of high-risk assurance and market claims. The vocabulary is shown below for documentation only:

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

A warning requires human claims review and narrower wording or supporting evidence. Negated statements such as `not production ready` are ignored where the simple context detector recognizes them. Fenced code blocks and explicit `claim-lint` documentation blocks are excluded from linting; those exclusions must not be used to suppress substantive claims.

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

- prove vendor claims
- establish cryptographic security
- establish legal compliance
- decide competitor classification from technology similarity
- promote a market hypothesis
- publish private customer evidence
