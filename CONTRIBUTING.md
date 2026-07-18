# Contributing

## Before contributing

Read:

- `README.md`
- `docs/RESEARCH_METHOD.md`
- `GOVERNANCE.md`
- `AGENTS.md`

Contributions must be suitable for a public repository.

## Contribution types

### Source correction

Use when a product, standard, license, release, or company status has changed.

Include:

- old statement
- corrected statement
- canonical source
- observation date
- impact on prior analysis

### New competitor or substitute record

Use `templates/competitor-record.yaml`.

A record must include:

- classification rationale
- buyer, user, and trigger where known
- primary source
- facts, inferences, hypotheses, and unknowns
- confidence
- review dates

### New technology record

Use `templates/technology-record.yaml`.

Do not recommend a technology based only on benchmark speed or cryptographic branding. Record the security model, residual leakage, trust assumptions, maintenance, licensing, and operational cost.

### Use-case finding

Raw customer discovery belongs in the private strategy repository. Only anonymized, aggregated, reviewed findings may be contributed here.

## Pull requests

Keep each pull request focused on one issue or one coherent correction.

The pull request should contain:

- linked issue
- goal and scope
- sources
- claim classification
- validation
- publication-boundary check
- known limitations

## Source quality

Preferred sources:

1. standards and regulators
2. peer-reviewed or author-published papers
3. official technical documentation
4. official source repositories and releases
5. official case studies and announcements

Marketing claims must be labeled as vendor-published claims.

## Copyright and quotations

- Paraphrase rather than copying long passages.
- Preserve source links and attribution.
- Do not upload third-party reports, screenshots, datasets, or paywalled material without permission.
- Confirm license compatibility before adding code or datasets.

## Security and privacy

Do not disclose vulnerabilities, customer details, internal infrastructure, private repository content, unpublished inventions, or personal information in an issue or pull request.

## Review outcome

A contribution may be rejected even if factually correct when it:

- belongs in a private repository
- creates avoidable security or privacy risk
- lacks sufficient sourcing
- overstates the evidence
- expands the project beyond the current research scope
