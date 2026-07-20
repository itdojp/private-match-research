# ADR-0001: Select the First Technology Bake-off Tracks

- Status: proposed experiment selection
- Date: 2026-07-18
- Decision scope: public research reproduction only
- Local candidate results: not run
- Production architecture: not selected

## Context

Private Match requires an identical minimum result for two parties while preserving explicit trust, leakage, session, replay, and query-budget boundaries. Issue #4 requires at least one cryptographic and one TEE reproduction selection without converting a research experiment into a product architecture decision.

The survey found materially different models:

- PSI implementations can compute intersections but often return rows to one receiver or both parties.
- VOPRF standardizes a keyed client/server primitive but not a complete set protocol or symmetric result.
- general MPC can encode broader functions at higher configuration and operational cost;
- TEEs move trust into measured code, hardware, attestation, and a verifier;
- ZKP can support a bounded claim but does not independently supply set matching, input completeness, or query policy.

## Decision

<!-- selection:cryptographic -->
### D-001 — Select SecretFlow PSI and RFC 9497/CIRCL for cryptographic reproduction

1. Pin SecretFlow PSI commit `d7682707035d6b3e04cc09b8bfef629140641432` and start with documented `PROTOCOL_KKRT` under its explicit semi-honest assumption.
2. Pin Cloudflare CIRCL `v1.6.4` and reproduce RFC 9497 VOPRF vectors as a separate primitive track.
3. Do not treat either upstream output as the Private Match core result. Record the wrapper logic and compare outputs at both endpoints.
4. Do not copy upstream benchmark numbers into local result fields.

Rationale: SecretFlow exercises an end-to-end set path with public source and benchmark procedures; RFC 9497/CIRCL provides a standardized primitive boundary for testing low-entropy input controls and proof/key validation. Keeping them separate prevents the VOPRF primitive from being mislabeled as a complete PSI protocol.

<!-- selection:tee -->
### D-002 — Select AWS Nitro Enclaves for an attested TEE reproduction

Pin Nitro CLI `v1.4.5` and NSM API `v0.5.2`. The prototype must run outside debug mode, validate the AWS Nitro attestation chain and a fresh nonce, bind expected PCR policy, accept only synthetic inputs, return only the enumerated result plus a bound receipt, and measure parent-visible vsock/network/artifact metadata.

Execution requires prior human approval of the paid AWS environment, cost ceiling, region, account boundary, instance type, retention, and teardown. Selection does not authorize resource creation.

Rationale: Nitro Enclaves has current public documentation, attestation semantics, maintained open-source tooling, and explicit I/O constraints. It provides a practical trust-model contrast to the cryptographic track. It does not prove application correctness, input completeness, endpoint protection, or side-channel resistance.

### D-003 — Keep ZKP as a supporting mechanism

Evaluate gnark later only for a bounded public statement with a defined witness, public input, setup model, and verifier binding. Do not implement whole-set matching in a circuit for the first bake-off and do not claim that a proof establishes real-world dataset completeness.

### D-004 — Execute the smallest falsifiable experiment first

The next bounded experiment is `EXP-001` and the 0/1/3 variants of `EXP-005` on SecretFlow KKRT:

- 1,000 distinct synthetic identifiers per party;
- intersections of 100 for the baseline and 0, 1, and 3 for sparse cases;
- five repetitions after one warm-up;
- explicit `broadcast_result` setting;
- per-party wall time, peak memory, byte counts, outputs, and digests;
- packet/stdout/stderr/temporary/output inspection for raw synthetic identifiers;
- no customer data, cloud resource, production dependency, or market claim.

Stop after this bounded run. Do not continue automatically to the million-row or paid TEE cases. Review failures, output semantics, privilege requirements, and evidence completeness first.

## Rejected from the first bounded experiment

| Alternative | Decision | Reason | Reconsider when |
|---|---|---|---|
| Meta Private-ID | Defer | Universal-ID and downstream-share semantics exceed the minimum result; current implementation assumptions need reproduction | Downstream private compute becomes a validated requirement |
| Microsoft APSI | Defer | Optimized for an asymmetric receiver query and receiver-owned results rather than the first balanced symmetric case | `EXP-003` is authorized and an unbalanced membership workflow is required |
| Google Private Join and Compute | Reject for core experiment | Cardinality and sum exceed the allowed core output; repository documents honest-but-curious and repeated-output limitations | A separately approved aggregate-output profile exists |
| MP-SPDZ | Defer | General MPC requires a defined circuit, protocol, preprocessing, and party model before cost is comparable | The minimum function and active-security comparison are specified |
| gnark as default matching | Reject | It is a proof framework, not a set-matching policy; circuitizing the full match is unbounded for this issue | A narrow supporting statement and verifier consumer are defined |
| AWS C3R | Defer as adjacent reference | Requires an AWS Clean Rooms collaboration and produces a governed SQL workflow rather than a standalone minimum-result protocol | Managed clean-room setup is the comparison question |
| SecretFlow RR22 or other protocol switch | Defer | Changing protocol changes assumptions and comparison scope | KKRT evidence is complete and a separately reviewed follow-up identifies the next model |
| TEE debug-mode result | Reject | AWS documents zero-valued PCRs in debug-mode attestation | Non-debug attestation can be verified under an approved environment |

## Consequences

### Positive

- Covers a purpose-built PSI path, a standards-based VOPRF primitive, and an attested TEE path.
- Makes semi-honest, hardware, application, and verifier trust explicit.
- Measures policy gaps, metadata, raw egress, result ownership, and failure semantics rather than speed alone.
- Uses deterministic synthetic inputs and evidence digests.

### Negative and residual risk

- SecretFlow's documented container procedure grants broad privileges and host networking; the first run must use a disposable host with no credentials or private data.
- VOPRF does not provide set semantics, symmetry, authentication, or query-budget state.
- Nitro execution incurs AWS service cost and depends on AWS Nitro hardware, hypervisor, PKI, parent lifecycle, and approved operational controls.
- The selected tracks do not establish malicious-party security, dataset authenticity, completeness, legal sufficiency, endpoint safety, or side-channel resistance.
- License observations do not constitute patent clearance or final product-license approval.

## Evidence required to revisit this ADR

- Result records conforming to `benchmarks/result.schema.json` for the bounded run.
- Complete failure, skip, unsupported, timeout, and tool-error evidence.
- Input/output/stdout/stderr digests and environment pins.
- A per-party output and result-symmetry comparison.
- Packet and artifact observations with explicit unobserved-channel limits.
- Human approval before any paid TEE execution or production PET selection.

## Alternatives remain open

This ADR is an experiment-selection record. It is superseded by evidence, not by silent fallback. A candidate failure may justify a new experiment decision; it does not automatically promote another candidate or select a production architecture.
