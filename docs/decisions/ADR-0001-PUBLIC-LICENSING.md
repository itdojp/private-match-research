# ADR-0001: Public research repository licensing

- Status: Accepted
- Decision owner: ITDO Inc. / 株式会社アイティードゥ
- Decision date: 2026-07-19
- Human approval: Explicitly approved for this public repository review
- Review date: 2026-10-18

## Context

This public repository contains both narrative research material and executable or
machine-consumable validation artifacts. The repository policy requires explicit
human approval for license and patent strategy changes. That approval was supplied
for this review.

## Decision

- Narrative documentation, research text, tables, diagrams, templates, and
  structured research records use CC BY 4.0.
- Python code, JSON Schemas, validators, tests, fixtures, workflows, build inputs,
  and executable or configuration artifacts use Apache License 2.0.
- `REUSE.toml` is the machine-readable SPDX file mapping. `LICENSES/` contains the
  complete license texts and takes precedence over the summary in `LICENSE.md`.
- Patent-sensitive or trade-secret candidate material remains private or embargoed
  until separate human IP and publication approval is recorded.

## Boundary and impact

This allocation changes licensing metadata only. It does not publish embargoed
material, grant rights to third-party material, or establish vendor claims, market
demand, cryptographic security, legal compliance, privacy properties, production
readiness, or patent clearance. Apache-2.0 patent provisions do not replace the
separate human patent and publication gate.
