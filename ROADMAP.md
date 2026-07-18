# Research Roadmap

Updated: 2026-07-18

## Milestone R0 — Research foundation

Goal: establish a reproducible and publication-safe research system.

- [x] repository purpose and boundaries
- [x] research method and evidence levels
- [x] market / technology / use-case templates
- [x] preliminary market map from primary vendor sources
- [ ] source registry and automated URL-status checks
- [ ] citation and claim linting rules
- [ ] contribution guide
- [ ] review cadence and stale-record reporting

Exit criteria:

- every published record has observation date, primary source, confidence, and fact/inference separation
- publication checks are defined
- stale product information can be detected

## Milestone R1 — Competitive landscape

Goal: identify direct, adjacent, substitute, and building-block alternatives.

Target coverage:

- hyperscale / warehouse clean rooms
- independent PET platforms
- Japan providers
- conflict-checking and trusted-third-party substitutes
- manual NDA / consultancy workflows
- privacy-first matching products
- open-source components

Exit criteria:

- at least 25 structured records
- buyer, trigger, output, deployment effort, and public pricing captured where available
- at least 5 non-cryptographic substitutes included
- direct-competitor classification reviewed separately from technology similarity

## Milestone R2 — Use-case evidence

Goal: validate whether narrow pre-disclosure decisions have independent economic value.

Priority hypotheses:

1. conflict / relationship overlap preflight
2. partnership and M&A customer-overlap preflight
3. confidential recruiting match

Exit criteria:

- buyer, user, trigger, current workaround, required output, and procurement path defined
- at least two hypotheses reach customer evidence level E2
- disconfirming evidence and no-go criteria recorded
- public findings are anonymized and approved through the publication gate

## Milestone R3 — PET technology bake-off

Goal: compare practical approaches under the actual Private Match threat and data profiles.

Candidate classes:

- PSI / PSI cardinality
- OPRF / VOPRF
- MPC / 2PC
- TEE / confidential computing
- ZKP for selected claims
- FHE as a comparison path

Required comparison dimensions:

- security and trust model
- low-entropy identifier handling
- malicious-input resistance
- repeated-query leakage
- balanced and unbalanced set performance
- communication and deployment cost
- maintenance, license, audit, and interoperability

Exit criteria:

- at least one cryptographic and one TEE approach reproduced
- raw-input egress measured
- packet and metadata observations recorded
- no silent fallback or mock path in benchmark results
- a public ADR recommends the next protocol experiment without claiming product readiness

## Milestone R4 — Research-to-protocol handoff

Goal: turn validated findings into bounded protocol requirements.

Outputs to `private-match-protocol`:

- actors, assets, adversaries, trust boundaries
- required result and prohibited disclosure
- set-size and intersection thresholds
- query-budget policy
- normalization and identity-resolution assumptions
- failure semantics
- candidate protocol and alternatives

Exit criteria:

- every protocol requirement links to research evidence or an explicit policy decision
- unresolved market and technical assumptions remain visible
- product-specific confidential details are not copied into public repositories

## Milestone R5 — Continuous review

Goal: keep the public research accurate as products, standards, and implementations change.

- quarterly competitor re-verification
- monthly check for major PET standard and project releases
- correction log
- archived / superseded record handling
- evidence-level changes from pilots and customer discovery
