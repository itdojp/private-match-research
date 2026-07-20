# Initial Market Map — 2026-07

Observed at: 2026-07-18  
Status: preliminary / public-source scan  
Scope: adjacent products and substitutes for privacy-preserving cross-organization matching and analysis

Structured follow-up: [`competitor-index.md`](competitor-index.md) contains 29
schema-validated records with buyer, user, trigger, output, deployment, pricing,
trust, assurance, source, and review-date fields. The structured records
supersede this preliminary scan when details differ.

## 1. Interpretation boundary

This document does not establish that a direct competitor does or does not exist.

Most products below are classified as `adjacent` because they provide broader data collaboration, analysis, or confidential-computing platforms. Whether they compete directly with Private Match depends on buyer, trigger, implementation effort, output, and pricing.

Statements sourced from vendor pages describe the vendor's published position. Performance and security claims are not treated as independently verified unless an independent source is cited.

## 2. Hyperscale and warehouse-native data clean rooms

### AWS Clean Rooms / Cryptographic Computing for Clean Rooms (C3R)

Classification: `adjacent`

Published facts:

- C3R is an optional capability of AWS Clean Rooms for collaborations using encrypted data.
- A client-side encryption tool prepares data before upload.
- The documented encrypted-query scope is limited, including JOIN and SELECT over protected columns rather than arbitrary encrypted SQL.
- AWS documents residual metadata exposure such as table shape, row count, value-length information, and logging-level information.
- Fingerprint columns use HMAC-based processing; sealed columns use AES-GCM.

Implication:

- AWS offers a credible cloud-native alternative for organizations already operating tabular collaboration workflows on AWS.
- Private Match should not compete as a general SQL clean room.
- A possible differentiation hypothesis is a smaller decision surface, lower setup burden, bilateral session semantics, explicit query budget, and public conformance evidence.

Primary sources:

- https://docs.aws.amazon.com/clean-rooms/latest/userguide/crypto-computing.html
- <https://docs.aws.amazon.com/clean-rooms/latest/userguide/crypto-computing-considerations.html>
- https://github.com/aws/c3r

### Snowflake Data Clean Rooms

Classification: `adjacent`

Published facts:

- Snowflake describes its offering as a native, multi-collaborator data-clean-room environment.
- Collaborators can submit and approve templates and data sources.
- Analyses run inside the clean-room environment; collaborators can receive approved results without directly querying raw data.
- Snowflake documents UI and developer API surfaces and privacy controls including policies and differential privacy.

Implication:

- Snowflake is a strong substitute for existing Snowflake customers needing repeated analytics and governed collaboration.
- Private Match must validate demand for pre-analysis decisions that do not justify warehouse-specific setup.

Primary sources:

- <https://docs.snowflake.com/en/user-guide/cleanrooms/introduction>
- https://docs.snowflake.com/en/user-guide/cleanrooms/overview

### BigQuery Data Clean Rooms

Classification: `adjacent`

Published facts:

- BigQuery Data Clean Rooms use BigQuery sharing infrastructure.
- Contributors share tables, views, or routines while subscribers are restricted by analysis rules and privacy controls.
- Google positions the environment for joining and analyzing sensitive data without directly revealing the underlying data.

Implication:

- BigQuery customers can solve many recurring collaboration problems without a separate protocol product.
- Private Match should focus on bilateral, narrow, policy-bound decisions and avoid becoming a smaller BigQuery clone.

Primary source:

- https://cloud.google.com/bigquery/docs/data-clean-rooms

## 3. Independent PET and secure-collaboration platforms

### InfoSum Secure Data Clean Room

Classification: `adjacent`

Vendor-published position:

- Matching and analysis across datasets without sharing or moving data.
- Decentralized processing and differential-privacy techniques.
- Strong focus on advertising, media, commerce, activation, and measurement workflows.

Unverified / follow-up:

- Precise trust model and cryptographic construction for each product path.
- Query-budget and repeated-query controls.
- Pricing and minimum deployment effort.

Implication:

- “Data does not move” is already an established commercial value proposition.
- Private Match requires a narrower buyer and workflow, not only stronger privacy language.

Primary source:

- <https://www.infosum.com/platform/privacy>
- <https://support.infosum.com/hc/en-us/articles/20230364634258-Introducing-the-InfoSum-Data-Clean-Room>

### Decentriq

Classification: `adjacent`

Vendor-published position:

- Secure collaboration without exposing raw data.
- Use of confidential computing and other PETs; the current site also refers to homomorphic encryption.
- Data clean rooms and audience-oriented collaboration products.

Unverified / follow-up:

- Product-specific threat models and attestation assumptions.
- Deployment and pricing profile for one-off bilateral use.

Implication:

- TEE-backed confidential computing is a practical alternative and must be included in the technology bake-off.

Primary sources:

- https://www.decentriq.com/data-clean-rooms
- https://www.decentriq.com/

### Duality

Classification: `adjacent`

Vendor-published position:

- Privacy-preserving queries, collaborative AI, and federated analytics across distributed data.
- Use of multiple PETs, including FHE-based technology through OpenFHE.
- Governance and collaboration-management capabilities for regulated industries.

Unverified / follow-up:

- Product-specific security model, query leakage, performance under Private Match data profiles, and commercial terms.

Implication:

- General encrypted analytics and cross-domain collaboration are established categories.
- Private Match should remain a decision product with explicit output minimization rather than a general encrypted-query platform.

Primary sources:

- <https://dualitytech.com/>
- <https://dualitytech.com/wp-content/uploads/2023/06/pagerFinCrime_v10.pdf>
- <https://dualitytech.com/wp-content/uploads/2024/01/Installation-Guide-v3.1-AWS-Market-Place_support.pdf>

## 4. Japan market

### Acompany AutoPrivacy DataCleanRoom / SGX-EIM

Classification: `adjacent`

Vendor-published facts and claims:

- AutoPrivacy describes protected ID matching without sharing raw data or data-processing information between parties.
- SGX-EIM uses Intel SGX and was reported by Acompany as processing a 10-million-by-10-million ID matching and cross-tabulation workload in approximately 11 seconds in its stated test conditions.

Boundary:

- The performance number is a vendor-published result, not an independent benchmark.

Implication:

- Japanese organizations already have access to TEE-based protected ID matching and compliance-oriented data-clean-room offerings.
- Competing as a generic domestic confidential-ID-matching platform is weak without a narrower workflow advantage.

Primary sources:

- https://service.acompany.tech/datacleanroom/function/
- https://www.acompany.tech/news/24-0209-2

### NTT DOCOMO BUSINESS 析秘 / 析秘TEE

Classification: `adjacent` and `substitute`

Published facts:

- 析秘TEE began commercial provision on 2025-07-31.
- The service uses a TEE-based isolated execution environment and an approval workflow for agreed data processing.
- NTT distinguishes it from its existing MPC-based 析秘 service.
- The 2025 launch material published both per-use and monthly pricing models, including an initial fee.

Implication:

- A Japanese enterprise can purchase confidential processing with workflow approval from a major provider.
- Private Match must validate whether lower-cost, lower-preparation, standardized preflight decisions form a separate buying category.

Primary sources:

- https://www.ntt.com/about-us/press-releases/news/article/2025/0730.html
- https://www.ntt.com/business/services/secihi.html

### EAGLYS

Classification: `adjacent`

Vendor-published position:

- Confidential-computing and AI solutions for cross-company data use.
- ALCHEMISTA targets materials informatics and cross-company optimization while data remains protected.
- EAGLYS announced a 2026 proof-of-concept with Tomoegawa and Hitachi High-Tech using confidential AI for cross-company manufacturing-condition optimization.

Implication:

- Domain-specific confidential collaboration is commercially active in Japan.
- Private Match should use domain templates, but initial domains should avoid competing with established industrial AI platforms.

Primary sources:

- https://eaglys.co.jp/
- https://eaglys.co.jp/solution/alchemista/
- https://eaglys.co.jp/resource/news/260319

## 5. Preliminary conclusions

### Facts

- General-purpose and warehouse-native data clean rooms are mature commercial categories.
- Confidential computing, MPC, FHE, differential privacy, and client-side cryptographic preprocessing are already used or marketed in commercial offerings.
- Protected ID matching is offered in Japan by established vendors.
- The structured index includes three dedicated privacy-first matching
  candidates—ZERONEAR, Heyoosh Engine, and Voxhu—reviewed from official sources
  on 2026-07-20; none is designated as a direct competitor.

### Inferences

- “Uses ZKP/PET” and “does not share raw data” are insufficient differentiation on their own.
- A smaller pre-disclosure decision product could be differentiated by setup time, constrained output, bilateral consent, query budgets, public verifier/client surfaces, and assurance evidence.
- The likely competitive set includes manual NDA-and-consulting workflows, not only software platforms.

### Hypotheses to test

- `H-MKT-001`: Some bilateral decisions need only YES/NO or a coarse band and do not justify a full data-clean-room engagement.
- `H-MKT-002`: Legal, M&A, sales-alliance, or audit teams can sponsor a preflight purchase without first building a data-platform project.
- `H-MKT-003`: Public protocol and assurance artifacts materially reduce trust and procurement friction.
- `H-MKT-004`: One-off or low-frequency pricing can be viable below enterprise clean-room price and effort thresholds.

## 6. Next research actions

1. Review and refresh the
   [structured competitor index](competitor-index.md) on each record's
   `next_review_at` date.
2. Obtain human review before assigning any material `direct` classification.
3. Add independent reproduction evidence when a product or OSS implementation
   is exercised; retain vendor-only labels until then.
4. Interview target users for H1 conflict preflight and H2 customer-overlap preflight.
5. Conduct a technology bake-off including at least one PSI/OPRF approach and one TEE approach.
