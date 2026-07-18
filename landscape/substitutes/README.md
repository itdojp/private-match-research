# Non-Cryptographic Substitutes and Manual Workflows

- Observed at: 2026-07-18
- Last verified at: 2026-07-18
- Next review at: 2026-10-18
- Evidence level: E1 for documented public workflows; E0 for Private Match comparisons and disconfirming tests
- Publication classification: public

## 1. Purpose and evidence boundary

This survey asks when an organization can make the same business decision without buying a dedicated privacy-enhancing-technology product. It covers all seven workflow categories required by Research Issue #3.

Facts (`F`) describe current official guidance, product documentation, or service documentation. Inferences (`I`) describe generalized workflows and comparisons. Hypotheses (`H`) define tests that have not been run. Unknowns (`U`) remain explicit.

No interview-derived information is included. Future interview observations remain private until they are anonymized, source-reviewed, and approved through the publication gate. No customer identity, transaction, or internal commercial information is used.

“Evidentiary value” below means the operational record available to a decision-maker; it is not legal evidence and does not establish admissibility, professional assurance, input completeness, or correctness.

## 2. Comparison reference

The Private Match reference in this document is a proposed bounded workflow, not an implemented market claim:

- two parties submit separately held inputs;
- the accepted result is limited to `MATCH`, `NO_MATCH`, or `INDETERMINATE`;
- raw identifiers are intended to stay inside an approved client boundary;
- additional disclosure requires both parties' later consent;
- session binding, query budgets, conformance, operational cost, and procurement time are not yet established.

The comparison therefore tests whether minimum disclosure provides enough incremental value to justify another product, integration, and review path.

## 3. Cross-class comparison

| Class | Setup time | Trust | Disclosure | Output | Cost model | Evidentiary value | When superior |
|---|---|---|---|---|---|---|---|
| NDA + CSV comparison | Unknown; agreement, field mapping, transfer, and review are required | Counterparty staff and designated analysts | Selected row-level identifiers and attributes pass to the counterparty | Match list, exceptions, counts, and working file | Internal labor, counsel or template review, and transfer tooling; standardized amount unknown | Agreement, file versions, formulas, and reviewer notes if retained | Parties already accept direct disclosure and need row-level explanation or ad hoc analysis |
| Trusted third-party matching | Unknown; subscription, authorization, and file-format onboarding vary | Central service operator and its reference dataset | Identifiers pass to the intermediary; report fields return to the requester | Service-defined row-level and aggregate reports | Subscription or service tier; public amount not found in reviewed sources | Submission receipt and operator-generated report within the stated service scope | A recognized intermediary owns the needed reference data or supplies an accountable report |
| Professional diligence engagement | Unknown; scope, data-room preparation, and specialist availability vary | Advisor, engagement team, and source-data providers | Deal documents, assumptions, and questions pass to professionals | Findings, issues, analysis, and scoped report | Engagement-based fees and internal participation; public amount unknown | Scoped professional report and workpapers, subject to engagement limits | Human judgment, negotiation context, or broad multi-domain diligence is required |
| CDP / identity resolution | Unknown initial mapping and ruleset setup; documented jobs run on a platform schedule after configuration | Platform operator, tenant administrators, and configured data sources | Source profiles and matching attributes enter the configured tenant boundary | Unified profiles, links, and resolution summaries | Platform entitlement and usage credits; contractual amount varies | Ruleset configuration, processing history, and unified-profile output | The organization already owns the platform and needs persistent operational profiles rather than a bilateral decision |
| Warehouse sharing + agreement | Unknown agreement and object-design time; access can be immediate after grants are configured | Cloud warehouse, provider administrators, consumer roles, and contractual governance | Consumer can query the rows or views granted by the provider | Read-only data access and arbitrary permitted query results | Existing warehouse plans, consumer compute, administration, and agreement work | Grants, query history, agreement, and reproducible SQL when retained | Counterparties accept controlled row-level access and already share a warehouse platform |
| Internal conflict database + questionnaire | Unknown; usually part of existing intake and review operations | Firm intake staff, conflicts analysts, and internal data custodians | Prospective-client, matter, relationship, and internal client data are available inside the firm | Hit list, review notes, and accept, decline, or escalate decision | Existing staff and system cost; incremental amount may be negligible | Intake form, search record, analyst notes, and approval trail | One firm's internal records and domain judgment are sufficient to decide the matter |
| Sampled or de-identified exchange | Unknown; extract, transformation, risk review, and transfer are required | Data-preparation staff, recipient analysts, and contractual controls | A transformed subset with residual attributes passes to the counterparty | Exploratory statistics, sample findings, and follow-up questions | Internal preparation, review, transfer, and analyst labor | Transformation log, sample definition, and analysis output; generalizability remains limited | Rich exploratory analysis is needed and the parties accept residual disclosure and sampling uncertainty |

## 4. Estimated disclosure by stage

The disclosure entries in this section are inferences from the documented workflows. They are not measurements of a specific deployment.

| Class | Stage 0: scope | Stage 1: input preparation | Stage 2: transfer or processing | Stage 3: result and retention |
|---|---|---|---|---|
| NDA + CSV comparison | Party identities, purpose, proposed fields, and intended recipients | Each party's selected rows and normalization logic are visible internally | Selected identifiers and attributes become available to the receiving counterparty or joint analyst | Match rows, nonmatches, formulas, copies, and notes may persist according to the agreement and operations |
| Trusted third-party matching | Subscriber identity, purpose, authorization, and requested report | Requester prepares service-defined identifiers and file format | The intermediary receives identifiers and compares them with its reference records | The requester receives defined row-level or aggregate reports; the intermediary may retain submitted data under its service terms |
| Professional diligence engagement | Parties, deal context, questions, scope, and advisor mandate | Source parties prepare documents, extracts, assumptions, and explanations | Engagement professionals review broad source material and request clarification | Findings and reports are distributed to agreed recipients; workpaper retention depends on the engagement |
| CDP / identity resolution | Tenant, sources, schemas, ruleset purpose, and administrator roles | Source profiles are mapped to platform objects and matching attributes | Platform rules link records and reconcile values inside the configured tenant | Unified profiles, links, summaries, and processing history remain available to authorized tenant users |
| Warehouse sharing + agreement | Provider, consumer, purpose, object list, roles, and agreement terms | Provider builds tables or views and grants selected objects | Consumer roles can query the granted rows or view results | Query outputs and logs may persist in consumer and provider environments according to configuration |
| Internal conflict database + questionnaire | Prospective client or matter identity and intake purpose | Intake staff collect names, relationships, affiliates, and matter context | Search and human review expose hits and internal context to authorized firm staff | Decision, escalation, notes, and limited external communication follow firm policy |
| Sampled or de-identified exchange | Parties, purpose, sampling rule, fields, recipients, and transformation plan | Source staff see the full extract while selecting rows and modifying identifiers or attributes | Recipient obtains the transformed sample and remaining quasi-identifiers | Analyses, copies, and follow-up extracts may accumulate; residual linkage and sampling error remain possible |

## 5. Substitute class records

<!-- substitute:nda-csv -->
### SUB-NDA-CSV — Mutual NDA followed by spreadsheet or CSV comparison

- **F — documented basis:** The UK Intellectual Property Office publishes one-way and mutual NDA examples for discussions with potential collaborators. The UK Information Commissioner's Office describes data-sharing agreements as a way to state purpose, data stages, roles, and responsibilities. These sources do not prescribe a CSV-matching method.
- **I — buyer and trigger:** A partnership, sales, diligence, or operations owner needs an overlap answer and both organizations are willing to disclose selected identifiers under agreed controls.
- **I — participants:** Business owners, counsel or policy reviewers, data preparers, transfer administrators, and analysts.
- **I — workflow:** Agree purpose and recipients; define fields and normalization; exchange selected files; compare in spreadsheet, SQL, or a script; review exceptions; retain or delete working material under the parties' process.
- **U — elapsed time:** No standardized duration was found. Agreement negotiation, data mapping, approvals, and exception review are variable.
- **I — output and failure modes:** The workflow can return exact matching rows, counts, and explanations. Failures include inconsistent normalization, stale extracts, duplicate rows, formula or join errors, uncontrolled copies, and incomplete party inputs.
- **I — why accepted:** It uses familiar tools, permits flexible follow-up, and can be adequate for a one-off low-volume decision.
- **I — when superior:** It is superior when direct disclosure is already acceptable, exact rows are required immediately, and the incremental value of a minimum result is low.
- **H — purchase-unnecessary condition:** A separate product is unnecessary when the parties already have an approved exchange process and can reach the decision within the required time and disclosure tolerance.
- **Primary sources:** [UK IPO NDA guidance](https://www.gov.uk/government/publications/non-disclosure-agreements); [ICO data-sharing agreements](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-sharing/data-sharing-a-code-of-practice/data-sharing-agreements/).

<!-- substitute:trusted-third-party -->
### SUB-TTP — Trusted third-party batch matching

- **F — documented basis:** National Student Clearinghouse StudentTracker accepts batch submissions, publishes a 250,000-record file limit, and returns student-level and aggregate reports. Its implementation guidance describes file submission and states that submitted student records are stored for later reporting.
- **I — buyer and trigger:** An education organization needs outcomes matched against a reference dataset that it does not own.
- **I — participants:** Subscriber administrator, data preparer, intermediary operator, reference-data contributors, and report users.
- **I — workflow:** Establish service access; prepare the prescribed file; submit it to the intermediary; the intermediary matches against its reference records; retrieve and interpret the service-defined report.
- **U — elapsed time:** Onboarding and report turnaround were not established from the reviewed public pages.
- **I — output and failure modes:** Outputs can include row-level and aggregate outcomes. Failures include formatting errors, incomplete reference coverage, stale source records, ambiguous identity data, unauthorized submission, or a report that does not answer the business question.
- **I — why accepted:** The intermediary supplies a reference dataset, established submission format, and operator-generated report that neither party can create alone.
- **I — when superior:** It is superior when the central service maintains the broader reference data needed for the question, or procurement requires a recognized operator rather than a peer-to-peer result.
- **H — purchase-unnecessary condition:** Private Match is unnecessary when the decision depends on external reference data available through the intermediary's service but not through the proposed peer-to-peer workflow.
- **Primary sources:** [StudentTracker service description](https://www.studentclearinghouse.org/solutions/ed-insights/studenttracker/); [StudentTracker implementation guidance](https://help.studentclearinghouse.org/sths/knowledge-base/implementing-your-service/).

<!-- substitute:professional-diligence -->
### SUB-PRO — Law-firm, audit-firm, consulting, or due-diligence engagement

- **F — documented basis:** Deloitte publishes acquisition, vendor, commercial, operational, and IT diligence services and describes analysis of issues that inform investment decisions. The page is vendor material; no independent assessment of quality or duration was reviewed.
- **I — buyer and trigger:** A corporate development, investment, finance, or deal leader needs a decision supported by multi-domain analysis and professional judgment.
- **I — participants:** Buyer and seller teams, engagement lead, financial, commercial, operational, technical, or legal specialists, and data-room administrators.
- **I — workflow:** Define scope and questions; execute an engagement; collect documents and management explanations; perform analysis; discuss exceptions; issue a scoped report and follow-up requests.
- **U — elapsed time:** Public standardized duration and price were not found; both depend on scope and access to information.
- **I — output and failure modes:** Output can include findings, risks, assumptions, and workpapers. Failures include incomplete scope, withheld data, late access, subjective judgment, inconsistent methods, unresolved exceptions, and a report delivered after the decision window.
- **I — why accepted:** Human specialists can interpret context, challenge management, integrate qualitative evidence, and support negotiation beyond a match result.
- **I — when superior:** It is superior when the decision requires explanations, valuation, domain judgment, or an accountable engagement record rather than a minimum binary result.
- **H — purchase-unnecessary condition:** A dedicated preflight product is unnecessary when diligence is already commissioned and the relevant overlap can be answered within that engagement without material additional disclosure.
- **Primary source:** [Deloitte acquisition and vendor diligence services](https://www.deloitte.com/cbc/en/services/financial-advisory/services/acquisition-and-vendor-diligence-services.html).

<!-- substitute:cdp-identity -->
### SUB-CDP — Customer-data-platform identity resolution

- **F — documented basis:** Salesforce documents Data Cloud identity resolution as processing source profiles into unified profiles through match and reconciliation rules. The documentation states that usage consumes credits and that processing frequency varies by data source after configuration.
- **I — buyer and trigger:** A marketing, customer-data, or service-data owner needs persistent profile unification across systems under one organizational tenant.
- **I — participants:** Data Cloud architect, tenant administrator, source-system owners, data stewards, and profile users.
- **I — workflow:** Map source schemas to platform objects; configure exact or fuzzy match rules and reconciliation; run the ruleset; inspect resolution summaries; use unified profiles in downstream analysis or activation.
- **U — elapsed time:** Initial mapping, connector, quality review, and rule-tuning time are unknown. The documented processing schedule does not measure end-to-end implementation time.
- **I — output and failure modes:** Output includes unified profiles, source links, and consolidation summaries. Failures include overly broad or narrow match rules, inconsistent source data, wrong reconciliation precedence, delayed sources, duplicate profiles, and credit consumption beyond expectations.
- **I — why accepted:** Organizations may already operate the platform, need reusable profiles, and value integration with downstream customer workflows.
- **I — when superior:** It is superior for persistent first-party identity resolution where rich profiles and operational activation are intended outputs.
- **H — purchase-unnecessary condition:** Private Match is unnecessary when all relevant data is already controlled by one organization and its existing identity platform can answer the decision.
- **Primary sources:** [Salesforce identity resolution overview](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution.htm&language=en_US&type=5); [Salesforce service-data ruleset guide](https://help.salesforce.com/s/articleView?id=data.c360_a_unify_data_dc4service.htm&language=en_US&type=5).

<!-- substitute:warehouse-contract -->
### SUB-WH — Existing warehouse query with contractual controls

- **F — documented basis:** Snowflake documents provider-created shares that grant selected read-only objects to consumer accounts without copying data between accounts in the ordinary same-platform path. The ICO describes data-sharing agreements as documenting purpose, parties, data stages, roles, and responsibilities; this is cited only as a public example of governance documentation, not as legal advice.
- **I — buyer and trigger:** A data partnership or analytics owner needs repeated access to agreed rows or views and both parties already use a compatible warehouse environment.
- **I — participants:** Provider administrator, consumer administrator, data owner, agreement reviewers, and consumer analysts.
- **I — workflow:** Agree purpose and use boundaries; create restricted tables or views; grant them to the consumer account; query through consumer compute; monitor grants and query history; revoke access when appropriate.
- **U — elapsed time:** Snowflake states access is available immediately after a consumer is added to a configured share, but agreement, account, view-design, and review time are unknown.
- **I — output and failure modes:** Consumers can obtain arbitrary query results permitted by grants. Failures include overbroad grants, incorrect view filtering, unexpected downstream copies, cross-region replication requirements, missing consumer accounts, and contractual terms that do not prevent technical misuse.
- **I — why accepted:** Existing warehouse roles, SQL, logs, and live data access reduce application integration and support repeated questions.
- **I — when superior:** It is superior when row-level or flexible query access is acceptable and both parties already have the necessary warehouse and governance capability.
- **H — purchase-unnecessary condition:** Private Match is unnecessary when a restricted view exposes an acceptable dataset and a minimum result would only delay the analysis users already need.
- **Primary sources:** [Snowflake data-sharing overview](https://docs.snowflake.com/en/user-guide/data-sharing-intro); [Snowflake provider configuration](https://docs.snowflake.com/en/user-guide/data-sharing-provider); [ICO data-sharing agreements](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-sharing/data-sharing-a-code-of-practice/data-sharing-agreements/).

<!-- substitute:manual-conflict -->
### SUB-CONFLICT — Manual conflict database and intake questionnaire

- **F — documented basis:** The Solicitors Regulation Authority publishes guidance on conflicts involving current and prospective clients. Intapp publishes a conflicts product for new-business acceptance and optional compliance handoff. Neither source establishes one universal manual process.
- **I — buyer and trigger:** A professional-services risk or intake leader receives a prospective client, matter, engagement, or relationship that requires internal clearance.
- **I — participants:** Requesting professional, intake staff, conflicts analyst, compliance reviewer, and internal client/matter data custodians.
- **I — workflow:** Collect names, affiliates, matter type, adverse parties, and relationships through a questionnaire; search an internal database; review possible hits and context; request clarification; accept, decline, or escalate under firm policy.
- **U — elapsed time:** No general duration was found; it depends on database quality, naming complexity, staffing, and escalation.
- **I — output and failure modes:** Output can include a hit list, rationale, notes, and a decision. Failures include aliases, spelling differences, incomplete intake, stale matter data, omitted relationships, excessive false hits, confidentiality limits, and inconsistent human review.
- **I — why accepted:** The firm retains domain context, existing records, accountable reviewers, and the ability to explain a decision.
- **I — when superior:** It is superior when one firm's internal data is sufficient, the review needs contextual judgment, or the actual conflicting identity must be handled immediately.
- **H — purchase-unnecessary condition:** Private Match is unnecessary when internal intake already resolves the material question without obtaining a hidden set from another organization.
- **Primary sources:** [SRA conflicts guidance](https://rules.sra.org.uk/solicitors/guidance/conflicts-interest/); [Intapp Conflicts](https://www.intapp.com/product/intapp-conflicts/).

<!-- substitute:sampled-disclosure -->
### SUB-SAMPLE — Bilateral disclosure using sampling or de-identification

- **F — documented basis:** NIST SP 800-188 describes de-identification models, governance, and the need to evaluate residual disclosure risks before release. The NIST publication explicitly recognizes multiple data-sharing models rather than one universal method.
- **I — buyer and trigger:** A partnership, research, diligence, or analytics owner needs richer exploratory evidence than a minimum match result and accepts a transformed subset.
- **I — participants:** Source-data owner, data-preparation and disclosure reviewers, transfer administrator, recipient analyst, and business decision-maker.
- **I — workflow:** Define purpose, fields, sample, and transformation; extract selected records; remove or generalize identifiers and attributes; review residual risk; transfer the sample; analyze results; request follow-up if the sample is insufficient.
- **U — elapsed time:** No general duration or cost was found; it depends on data sensitivity, transformation method, sample design, and review.
- **I — output and failure modes:** Output can include exploratory statistics and row-level transformed data. Failures include biased samples, rare-attribute linkage, remaining quasi-identifiers, over-transformation, insufficient coverage, uncontrolled copies, and conclusions that do not generalize to the full dataset.
- **I — why accepted:** Familiar analytics tools can examine richer attributes, stakeholders can inspect rows, and a sample can be cheaper than a new integration for a one-off question.
- **I — when superior:** It is superior when residual disclosure is acceptable, rich feature exploration is necessary, and sampling limitations are understood.
- **H — purchase-unnecessary condition:** Private Match is unnecessary when a reviewed transformed sample answers the business question at acceptable cost, time, and residual risk.
- **Primary sources:** [NIST SP 800-188](https://csrc.nist.gov/pubs/sp/800/188/final); [NISTIR 8053 publication page](https://www.nist.gov/publications/de-identification-personal-information).

## 6. Why organizations may accept the current workaround

The following are inferences to validate, not customer findings:

1. Existing tools and contracts have already passed internal procurement and access review.
2. Operators need exact identities, explanations, documents, or editable rows rather than a minimum result.
3. Human judgment and an accountable reviewer matter more than technical minimization.
4. A one-off, low-volume decision does not justify integration, vendor review, or another operational dependency.
5. The substitute owns a necessary reference dataset, identity graph, professional expertise, or transaction context.
6. Existing logs, reports, workpapers, or intake records fit the organization's current decision and audit process.
7. Direct disclosure is within the parties' risk tolerance, making a privacy-minimizing computation unnecessary.

## 7. Disconfirming tests for the Private Preflight hypothesis

These tests are unexecuted E0 hypotheses. They do not represent interview results or product decisions.

### DCT-001 — Existing-workflow sufficiency

- **Hypothesis challenged:** Organizations need a new bilateral preflight product.
- **Test:** In future anonymized discovery, map whether the decision was completed using an internal conflict system, warehouse, CDP, intermediary, or existing diligence engagement without creating a new cross-party computation.
- **Disconfirming observation:** Target decisions are routinely completed within the required time, disclosure tolerance, and cost using an existing workflow.
- **Implication if observed:** Do not treat privacy-preserving computation as an independent purchase reason for that segment.

### DCT-002 — End-to-end time advantage

- **Hypothesis challenged:** Minimum disclosure materially shortens the decision.
- **Test:** Compare elapsed time from request to accepted decision, including agreement, procurement, identity normalization, data preparation, integration, exceptions, and follow-up.
- **Disconfirming observation:** The proposed Private Match path is not faster than NDA plus file exchange, restricted warehouse access, or a current intermediary.
- **Implication if observed:** A setup-time value proposition is unsupported for the tested workflow.

### DCT-003 — Minimum-output sufficiency

- **Hypothesis challenged:** `MATCH`, `NO_MATCH`, or `INDETERMINATE` is sufficient before disclosure.
- **Test:** Record the first output required to make the actual decision, without asking respondents to accept the proposed vocabulary.
- **Disconfirming observation:** Users require matching identities, reason codes, amounts, provenance, or source documents before they can decide.
- **Implication if observed:** A minimum result adds a step without replacing the existing disclosure or diligence workflow.

### DCT-004 — Accountable-intermediary preference

- **Hypothesis challenged:** A symmetric protocol result is more valuable than a trusted intermediary or professional report.
- **Test:** Compare which record the decision owner and governance reviewers will accept: a protocol receipt, an operator report, a professional diligence report, or internal analyst workpapers.
- **Disconfirming observation:** The organization requires a recognized intermediary, advisor, or internal accountable reviewer and will not act on the protocol result alone.
- **Implication if observed:** Product value must include an accepted accountability model rather than cryptographic execution alone.

### DCT-005 — Data-quality bottleneck

- **Hypothesis challenged:** Privacy is the primary blocker to the overlap decision.
- **Test:** Measure time and unresolved cases attributable to missing identifiers, aliases, normalization, stale records, input omission, and reference-data coverage before evaluating computation time.
- **Disconfirming observation:** Data preparation and input completeness dominate elapsed time or decision error, while disclosure is already acceptable.
- **Implication if observed:** Identity and data-quality work should precede or replace a Private Match product experiment for that segment.

## 8. Decisions and unknowns

### Decisions in this research artifact

- Document all seven required substitute categories.
- Treat substitute advantages as first-class findings rather than exceptions.
- Keep all Private Match comparisons and disconfirming tests at E0 until external evidence is reviewed and publishable.
- Do not make legal, regulatory, product-priority, or go/no-go conclusions.

### Unknowns for follow-up

- Actual elapsed time and total cost of each workflow in target organizations.
- Whether buyers accept direct identifier disclosure under their current governance.
- Which operational record is accepted for each decision.
- Frequency, dataset sizes, exception rates, and identity-quality burden.
- Whether a minimum symmetric output changes the decision or merely adds a preliminary step.
- Whether target users require a trusted intermediary, professional judgment, or row-level explanation.

## 9. Publication check

- Source check: official regulator, government, vendor, service, and standards documentation only.
- Freshness check: all URLs observed on 2026-07-18; changeable records scheduled for 2026-10-18 review.
- IP check: short paraphrases only; no third-party code, templates, or long passages copied.
- Security check: no vulnerability, exploit, internal topology, or operational secret is included.
- Privacy check: no customer, interview, transaction, personal, or private repository data is included.
- Claims check: vendor capabilities are attributed; comparisons are labeled as inference; tests are labeled as unexecuted hypotheses.
