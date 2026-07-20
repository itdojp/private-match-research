# PSI, OPRF, MPC, TEE, and ZKP Technology Survey

- Observed: 2026-07-18
- Last verified: 2026-07-18
- Next review: 2026-10-18
- Evidence: E1 public standards, papers, repositories, releases, and vendor documentation
- Local candidate results: not run
- Publication classification: public

## 1. Scope and claim boundary

This survey selects bounded experiments for Private Match. It does not select a production architecture, establish an end-to-end security property, or treat a project, author, or vendor benchmark as a local result.

No local candidate benchmark has been executed. Facts (`F`) are attributed to current primary sources. Inferences (`I`) compare those facts with the proposed Private Match boundary. Decisions (`D`) select experiments only. Hypotheses (`H`) remain untested. Unknowns (`U`) are retained.

The comparison reference is a two-party workflow whose accepted result is limited to `MATCH`, `NO_MATCH`, or `INDETERMINATE`, is identical for both parties, binds the session, parties, policy, and protocol version, and permits later disclosure only after both parties consent. None of the surveyed implementations is assumed to enforce that complete policy without an application wrapper.

The nine files under `records/technologies/` evaluate standards and
implementations by technology category. They are not competitor classifications.
Some projects also appear under `records/competitors/` as product or
building-block market records; that separate record type evaluates buyer,
trigger, and market position. A technology selection or shared project identity
does not create a `direct` competitor designation, and no direct-designation
approval metadata is applicable to these technology records.

## 2. Cross-candidate security and leakage comparison

| Candidate | Model and trusted components | Low-entropy identifiers | Input omission / malicious input | Repeated-query risk | Metadata leakage | Result symmetry | Balanced / unbalanced fit |
|---|---|---|---|---|---|---|---|
| SecretFlow PSI / KKRT | Documented KKRT path is semi-honest; both endpoints, implementation, transport configuration, and host are trusted to follow the selected protocol | OPRF-based PSI avoids a public unkeyed-hash table, but guessed membership can still be tested through authorized runs | No dataset-completeness guarantee; semi-honest mode does not cover arbitrary deviation | Repeated receiver queries can form a membership oracle unless the application owns a query budget | Party identities, roles, endpoints, set/file sizes, timing, traffic shape, output rows, and traces | Configurable `broadcast_result`; the library can disclose intersection rows rather than only the core enum | Documented balanced PSI and repository paths for unbalanced PSI; each protocol must be tested separately |
| RFC 9497 VOPRF via CIRCL | VOPRF makes server key use verifiable to the client under the RFC assumptions; CIRCL and its runtime remain implementation dependencies | Server-keyed evaluation is relevant to low-entropy inputs, but an authenticated online server still needs purpose binding, rate limits, and query budgets | The primitive validates group elements and proofs; it does not attest dataset completeness or business authorization | Authorized clients can enumerate guesses through repeated evaluations without application controls | Client/server identity, suite, batch size, request/response size, timing, and public context | Client learns the VOPRF output; no symmetric match result | Batched client/server evaluations; not a set-intersection implementation by itself |
| Meta Private-ID | Paper describes DDH-based private matching constructions; the exact deployed corruption model and implementation-to-paper correspondence were not independently established | Pseudorandom identifiers replace raw join keys, but guessed input and repeated-run policy remain application concerns | Public material reviewed here does not establish dataset completeness; protocol-specific deviation handling needs reproduction | Repeated matching or streaming batches can accumulate linkability and output information | Party roles, set sizes, universal identifiers, network shape, and downstream share dimensions | Each party maps its own records to pseudorandom identifiers; this is not the proposed shared enum | Large and streaming datasets are paper goals; current balanced/unbalanced cost must be measured |
| Microsoft APSI | Receiver encrypts queries and sender evaluates them using BFV plus an OPRF step; end-to-end malicious-party handling is not claimed from the reviewed README | OPRF hashing protects against direct public hashing, while an authorized receiver can still submit guesses | Query structure is validated against sender parameters, but real-input authenticity and dataset completeness are external | Independent receiver queries create a membership service unless authorization and budgets are added | Public upper set-size bounds, parameters, bin-bundle counts, response sizes, timing, and labels | Receiver obtains match results; not symmetric | Designed for a large sender set and small receiver query set |
| Google Private Join and Compute | Repository states honest-but-curious security; parties and implementation are assumed to follow the protocol | Commutative-encryption matching does not remove output-oracle risk for guessable identifiers | Repository explicitly states inputs are not authenticated and can be changed arbitrarily | Repository warns that related runs can reveal more from cardinality and sum outputs | Set sizes, intersection cardinality, sum, traffic shape, and timing | Client outputs intersection size and sum; no identical minimum enum for both parties | Input-size flags permit different sizes, but current cost profiles are unknown |
| MP-SPDZ | Supports multiple semi-honest and malicious protocol families with different majority and preprocessing assumptions; selected protocol and party threshold determine the model | A circuit can avoid revealing raw values, but low-entropy output-oracle and query-policy controls remain application work | Malicious protocols can detect classes of protocol deviation; they do not prove that a party supplied its complete real dataset | Repetition leaks through the programmed output unless sessions and budgets are implemented around the computation | Parties, circuit/program size, preprocessing, traffic volume, rounds, timing, and outputs | Program-defined; all-party output is possible but not automatic | General computation supports either profile at potentially high circuit and operator cost |
| AWS Nitro Enclaves | Trusts the AWS Nitro system, hypervisor, attestation PKI, reviewed EIF, verifier, and application code; parent controls availability and I/O | Plain identifiers can be processed inside the enclave, but authorized code and repeated-query policy determine enumeration resistance | Attestation identifies measured code/configuration; it does not prove input completeness or data truth | Stateful query-budget enforcement must be designed outside ephemeral enclave memory or through an approved bound store | Parent observes lifecycle, allocated resources, vsock traffic volume/timing, and external network behavior | Application-defined; identical result delivery must be implemented and bound to attestation/session evidence | Application-defined within enclave CPU, memory, storage, and I/O constraints |
| gnark ZKP | Proof system and circuit assumptions vary by backend; setup/proving keys, circuit, compiler, and verifier are trusted according to the selected scheme | A proof can hide a witness, but a public statement or repeated proof policy can still expose guessable claims | A circuit proves only encoded constraints over supplied witnesses; it cannot prove omitted real-world records are absent | Repeated proofs and public inputs can accumulate information unless the statement is bounded | Circuit size, public inputs, proof size, verifier behavior, timing, and setup identifiers | Proof verification can be performed by both parties, but gnark does not perform matching by itself | Circuit-defined; large sets may make proving and witness generation costly |
| AWS C3R | Trusts client endpoints, a shared secret, AWS Clean Rooms workflow, schemas, and configured query controls | HMAC-derived fingerprint columns help avoid public hashing, but shared-key handling and permitted queries remain critical | Client preprocessing does not authenticate a complete dataset; Clean Rooms policy and participant behavior remain external | Repeated permitted SQL can accumulate disclosure unless analysis controls restrict it | Table shape, row counts, value lengths, schema, query shape, logs, and encrypted result sizes | Collaboration and result-receiver configuration determine output ownership | Tabular workflow; not a standalone balanced/unbalanced PSI API |

## 3. Engineering, assurance, and selection comparison

| Candidate | Computation / communication / operational cost | Setup, keys, attestation, deployment | Maintenance / license | External review and interoperability | Experiment decision |
|---|---|---|---|---|---|
| SecretFlow PSI | Project documentation presents ECDH, KKRT, and RR22 trade-offs; upstream timing tables are not local evidence | Bazel, C++ toolchain, two parties, protocol configs, container/network setup, input/output mounts | Active repository; Apache-2.0; release file lists `v0.5.0beta`, with no latest GitHub release endpoint observed | Protocol papers and tests are linked; no cross-implementation result was reviewed | **Selected** for the first end-to-end cryptographic track using KKRT at a pinned commit |
| RFC 9497 VOPRF via CIRCL | Two-message batched primitive; application PSI and result derivation add separate cost | Server key, client-known VOPRF public key, suite/context choice, CIRCL Go module | RFC published December 2023; CIRCL `v1.6.4`; BSD-3-Clause | RFC test vectors and standard ciphersuites support primitive conformance, not application interoperability | **Selected** for primitive/vector reproduction and low-entropy control analysis |
| Meta Private-ID | Paper and repository publish implementations for joins, identifiers, and downstream shares; local cost unknown | Rust nightly in the reviewed README, multiple binaries and role-specific files, optional network/TLS configuration | `v0.0.22` published 2024-08-28; Apache-2.0; default-branch commit observed 2024-10-18 | ePrint papers exist; current independent implementation audit and interop evidence unknown | Rejected from the first bounded run because output semantics and operational surface exceed the minimum-result experiment |
| Microsoft APSI | HE parameters, OPRF, cuckoo hashing, and query powers create nontrivial computation and response artifacts | C++, Microsoft SEAL/BFV parameters, sender database, OPRF key, ZeroMQ or custom channel | `v0.11.0` published 2023-04-17; MIT; default-branch commit observed 2023-12-30 | ePrint 2021/1116 and repository tests; interop with another APSI implementation not reviewed | Rejected from the first run; retain for a later highly unbalanced receiver-only comparison |
| Google Private Join and Compute | Produces intersection cardinality and sum using a dedicated protocol; upstream examples are not local results | Bazel, two processes, commutative-encryption and Paillier material, network endpoint | No GitHub release observed; Apache-2.0; default-branch commit observed 2026-03-09 | Repository documents an honest-but-curious model and explicit leakage caveats; no protocol standard | Rejected because output exceeds the core enum and the first experiment does not need a sum |
| MP-SPDZ | Cost depends on circuit domain, protocol, preprocessing, majority, and network; generality increases comparison scope | Compiler/VM, certificates, parties, preprocessing, protocol-specific binaries, program and I/O design | `v0.4.3` published 2026-07-06; primary license states BSD-3-Clause with bundled-component notices | Many papers and protocols; repository says implementation has not undergone the review expected for critical deployment | Rejected from the first run; retain as the general malicious/active comparison after the minimum function is encoded |
| AWS Nitro Enclaves | Application cost plus enclave allocation, vsock copies, attestation verification, and parent service costs | Supported paid EC2 parent, Nitro CLI, EIF, PCR policy, NSM attestation, nonce verifier, vsock I/O, teardown | Nitro CLI `v1.4.5` and NSM API `v0.5.2`; Apache-2.0 components | AWS documents attestation format and root; no comparison with an independent TEE attestation path was run | **Selected** for an attested TEE reproduction after explicit environment and cost approval |
| gnark ZKP | Circuit compilation, witness generation, proving, proof transfer, and verification; costs depend on backend and circuit | Go, chosen curve and proving system, setup/proving/verifying material, circuit and witness schema | `v0.15.0` published 2026-05-13; Apache-2.0; active repository | Repository lists multiple scoped audits and warns that constant-time and side-channel resistance are not guaranteed | Rejected as the default matcher; retained only for a later supporting-proof question with a bounded public statement |
| AWS C3R | Client preprocessing plus Clean Rooms query cost; encrypted-column restrictions shape the computation | Java CLI/SDK, schema, shared secret, AWS Clean Rooms collaboration, analysis controls | C3R `3.0.5` published 2025-01-07; Apache-2.0; active default branch observed | Official security guidance documents client and metadata boundaries; designed for AWS Clean Rooms rather than cross-implementation PSI | Rejected from the first run as an adjacent managed-workflow reference |

An observed OSS license is not a patent clearance or final product-license decision. Patent status, transitive-license obligations, export controls, and deployment-specific terms remain unknown until qualified review.

## 4. Candidate records

<!-- technology:secretflow-psi -->
### SecretFlow PSI

- **F:** The official project contains PSI/PIR code, a PSI v2 API, build/test instructions, protocol configurations, and a benchmark guide. Its documentation describes ECDH and KKRT paths as semi-honest and shows `broadcast_result` as an explicit setting.
- **I:** KKRT is a bounded first reproduction because it exercises an end-to-end set path locally, but its upstream output and semi-honest assumptions do not satisfy the full Private Match policy.
- **U:** Current local build cost, exact dependency graph, transport behavior, raw-egress surfaces, and tamper/replay handling have not been measured.
- **Sources:** [repository](https://github.com/secretflow/psi), [protocol documentation](https://secretflow.readthedocs.io/en/stable/user_guide/psi.html), [PSI v2 benchmark guide](https://github.com/secretflow/psi/blob/main/docs/user_guide/psi_v2_benchmark.md), [security policy](https://github.com/secretflow/psi/blob/main/SECURITY.md).

<!-- technology:rfc9497-circl-voprf -->
### RFC 9497 VOPRF through Cloudflare CIRCL

- **F:** RFC 9497 specifies OPRF, VOPRF, and POPRF variants, error handling, ciphersuites, security considerations, and test vectors. CIRCL publishes an RFC-compatible Go `oprf` package.
- **I:** A server-keyed VOPRF is a relevant preprocessing experiment for low-entropy identifiers because it avoids direct substitution with a public hash, but authentication and bounded online evaluation remain mandatory.
- **U:** An end-to-end set protocol, symmetric result, application transcript binding, authorization, rate limit, and authoritative query budget are not supplied by the primitive.
- **Sources:** [RFC 9497](https://datatracker.ietf.org/doc/rfc9497/), [CIRCL repository](https://github.com/cloudflare/circl), [CIRCL `oprf` package](https://pkg.go.dev/github.com/cloudflare/circl/oprf), [CIRCL v1.6.4](https://github.com/cloudflare/circl/releases/tag/v1.6.4).

<!-- technology:meta-private-id -->
### Meta Private-ID

- **F:** The official repository publishes Rust implementations for multiple private matching and downstream-sharing variants. The cited paper describes DDH-based private matching constructions.
- **I:** Universal-identifier and downstream-share outputs are useful adjacent evidence but do not directly test the proposed identical enum result.
- **U:** Current dependency compatibility, end-to-end corruption model for each binary, external implementation audit, and current balanced/unbalanced performance are unknown.
- **Sources:** [repository](https://github.com/facebookresearch/Private-ID), [Private Matching for Compute paper](https://eprint.iacr.org/2020/599), [v0.0.22 release](https://github.com/facebookresearch/Private-ID/releases/tag/v0.0.22).

<!-- technology:microsoft-apsi -->
### Microsoft APSI

- **F:** APSI publishes unlabeled and labeled asymmetric PSI using BFV homomorphic encryption, an OPRF phase, cuckoo hashing, and explicit sender/receiver roles. Public upper set-size bounds are not hidden.
- **I:** It is a strong later candidate for a large stable reference set and small receiver query, but receiver-only item/label output is not the first symmetric-result experiment.
- **U:** Current active maintenance cadence, application query budgets, malicious-party coverage, and cross-implementation interoperability are unknown.
- **Sources:** [repository and design README](https://github.com/microsoft/APSI), [protocol paper](https://eprint.iacr.org/2021/1116), [v0.11.0 release](https://github.com/microsoft/APSI/releases/tag/v0.11.0).

<!-- technology:google-private-join-compute -->
### Google Private Join and Compute

- **F:** The repository computes intersection cardinality and an associated-value sum, states an honest-but-curious model, states inputs are not authenticated, and warns about small-output and repeated-run leakage.
- **I:** Its explicit caveats are valuable negative-test requirements, while its result exceeds the proposed core output.
- **U:** Current release packaging, external review of the current default revision, and comparable local cost are unknown.
- **Sources:** [repository and caveats](https://github.com/google/private-join-and-compute), [USENIX 2022 leakage study linked by the project](https://www.usenix.org/conference/usenixsecurity22/presentation/guo).

<!-- technology:mp-spdz -->
### MP-SPDZ

- **F:** MP-SPDZ implements many MPC protocols across honest/dishonest majority and semi-honest/malicious models, provides a high-level program compiler, and publishes a benchmark-oriented workflow.
- **I:** It can encode a minimum-result function and compare active versus passive models, but its configuration space is too broad for the first narrow run.
- **U:** Circuit design, preprocessing volume, normalization, session policy, current external audit coverage, and the cheapest applicable protocol are unknown.
- **Sources:** [repository](https://github.com/data61/MP-SPDZ), [v0.4.3 release](https://github.com/data61/MP-SPDZ/releases/tag/v0.4.3), [framework paper](https://eprint.iacr.org/2020/521), [license](https://github.com/data61/MP-SPDZ/blob/master/License.txt).

<!-- technology:aws-nitro-enclaves -->
### AWS Nitro Enclaves

- **F:** AWS documents isolated enclave CPU/memory, no direct external network or persistent storage, vsock-only parent communication, and signed attestation documents containing PCR measurements. Debug mode produces zero-valued PCRs that are unsuitable for cryptographic attestation.
- **I:** A measured enclave can test a simple minimum-result application and parent-visible metadata without first designing a new cryptographic set protocol.
- **U:** Application correctness, endpoint protection, side channels, rollback/query-budget persistence, exact EC2 cost, and independent TEE comparison remain unverified.
- **Sources:** [Nitro Enclaves overview](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html), [attestation](https://docs.aws.amazon.com/enclaves/latest/user/set-up-attestation.html), [root verification](https://docs.aws.amazon.com/enclaves/latest/user/verify-root.html), [Nitro CLI](https://github.com/aws/aws-nitro-enclaves-cli), [NSM API](https://github.com/aws/aws-nitro-enclaves-nsm-api).

<!-- technology:gnark-zkp -->
### gnark as a supporting proof mechanism

- **F:** gnark publishes Go APIs for circuit definition, proving, and verification with multiple proof systems and curves. The repository lists scoped audits and explicitly disclaims constant-time and side-channel guarantees.
- **I:** ZKP is better evaluated later for a bounded statement such as conformance to a committed transformation or policy input, not as the default set-matching engine.
- **U:** The supporting statement, circuit size, setup model, proof-system choice, verifier binding, and value relative to signed receipts remain undecided.
- **Sources:** [repository](https://github.com/Consensys/gnark), [documentation](https://docs.gnark.consensys.io/), [v0.15.0 release](https://github.com/Consensys/gnark/releases/tag/v0.15.0), [audit list](https://github.com/Consensys/gnark#audits).

<!-- technology:aws-c3r -->
### AWS Cryptographic Computing for Clean Rooms

- **F:** C3R publishes a client and SDK for AWS Clean Rooms, uses schemas to transform protected columns, and documents HMAC-based fingerprint columns, AES-GCM sealed columns, and residual metadata boundaries.
- **I:** C3R is an adjacent operational reference for client-side preprocessing and managed query controls rather than a first standalone Private Match protocol.
- **U:** Comparable one-off setup cost, query-budget behavior for the proposed decision, and symmetry of an accepted result are unknown.
- **Sources:** [repository](https://github.com/aws/c3r), [C3R overview](https://docs.aws.amazon.com/clean-rooms/latest/userguide/crypto-computing.html), [guidelines](https://docs.aws.amazon.com/clean-rooms/latest/userguide/crypto-computing-guidelines.html), [3.0.5 release](https://github.com/aws/c3r/releases/tag/3.0.5).

## 5. Cross-cutting findings

### Facts

- None of the reviewed candidate APIs is documented as enforcing the full Private Match core result, symmetry, consent, replay, and query-budget policy as one unit.
- Input completeness is not established merely by using PSI, VOPRF, MPC, TEE, or ZKP.
- Small outputs and repeated related runs can reveal information even when raw inputs are not returned.
- Candidate trust models differ materially and must not be hidden behind one generic PET adapter claim.

### Inferences

- The first experiment should compare policy gaps as well as runtime cost.
- A low-entropy path needs server-keyed evaluation plus application authentication, purpose/session binding, rate limits, and authoritative query-budget state.
- Result symmetry must be observed at both endpoints; a receiver-only intersection is not equivalent to the core result.
- TEE attestation changes the trusted-computing base rather than eliminating trust.

### Unknowns

- Which candidate can meet the result policy with the least additional trusted code and operator burden.
- Whether the first cryptographic and TEE runs reject all malformed and replay cases through public hooks.
- Actual local computation, communication, memory, disk, metadata, and raw-egress observations.
- Patent and production-license conclusions.

## 6. Decision handoff

[`ADR-0001-first-technology-bakeoff.md`](../decisions/ADR-0001-first-technology-bakeoff.md) selects SecretFlow KKRT, RFC 9497/CIRCL VOPRF, and AWS Nitro Enclaves for reproduction. [`../benchmarks/README.md`](../benchmarks/README.md) defines the eight required experiments and evidence boundary.

The decision is reversible. A failed, unsupported, timed-out, or tool-error result remains evidence and does not authorize a fallback or production selection.
