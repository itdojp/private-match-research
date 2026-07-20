# Governance

## Maintainer

This repository is maintained by 株式会社アイティードゥ (`itdojp`).

## Repository responsibility

This repository is the public system of record for publishable research about Private Match.

It is not the system of record for:

- product source code
- customer discovery records
- pricing and sales strategy
- unpublished inventions
- vulnerability handling
- assurance evidence for a specific private product build

Those responsibilities belong to the related private or public repositories described in `README.md`.

## Change categories

### Research fact update

Examples:

- product capability changed
- company or project status changed
- new standard or paper published
- license or release status changed

Requirements:

- primary source
- observed date
- distinction between vendor claim and independently verified result

### Analysis update

Examples:

- competitor classification
- market implication
- technology-fit assessment

Requirements:

- supporting facts
- explicit inference label
- confidence level
- alternative interpretations when material
- for a material `direct` competitor designation, record-scoped approval from an
  authorized human with a concrete public review reference; general claims
  review does not substitute for that decision

### Decision record

A public decision record may explain why a technology or scope was selected or rejected. It must not disclose private commercial strategy or unpublished inventions.

## Publication gate

Material originating from private repositories must not be mirrored automatically.

Publication uses a one-way review process:

```text
private draft
  -> source and freshness review
  -> IP review
  -> security review
  -> privacy review
  -> claims review
  -> explicit public pull request
```

Public repositories must receive selected files as new public commits. Do not publish private Git history through subtree, mirror, or filter-branch workflows.

## Security information

Do not open a public issue for:

- an exploitable vulnerability
- internal infrastructure details
- private product source findings
- customer-specific weaknesses
- a method that materially increases abuse capability before mitigation

Use the security contact and private vulnerability-reporting mechanism defined by the organization.

## Corrections

Substantive errors are corrected transparently. A correction should state:

- the original error
- correction date
- replacement evidence
- impact on prior conclusions

## Claims policy

The following expressions require especially strong evidence and review:

- secure
- proven
- mathematically guaranteed
- zero leakage
- anonymous
- compliant
- production ready
- world first
- no competitor

Prefer scoped statements that identify assumptions, tested conditions, and known limitations.
