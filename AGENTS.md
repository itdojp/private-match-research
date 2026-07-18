# AGENTS.md

## Repository purpose

This is the public research repository for Private Match. Changes must remain publishable, source-grounded, and separate from confidential product and commercial information.

## Operating model

- GitHub Issues are the work units.
- Work on one issue at a time unless the issue explicitly permits otherwise.
- Do not create new issues unless a human explicitly requests it.
- Do not broaden an issue into adjacent research.
- Do not push directly to `main`.
- Open a pull request for review.
- Do not merge a pull request.

## Public / private boundary

Never add:

- customer names or interview transcripts
- sales pipeline, pricing strategy, or win probability
- private repository content
- service source code or infrastructure details
- unpublished inventions or patent candidates
- unremediated vulnerability details
- secrets, tokens, internal hostnames, or production identifiers

If a task requires any of these, stop and report that the work belongs in `private-match-strategy` or `private-match-product`.

## Research rules

1. Prefer current primary sources.
2. Record `observed_at` and `last_verified_at` for changeable facts.
3. Separate facts, inferences, hypotheses, decisions, and unknowns.
4. Do not convert missing information into a favorable assumption.
5. Distinguish vendor-published claims from independently reproduced results.
6. Do not classify a product as a direct competitor only because it uses similar technology.
7. Include non-cryptographic substitutes and reasons Private Match may not be needed.
8. Avoid absolute claims such as secure, proven, anonymous, compliant, zero leakage, world first, no competitor, or production ready unless the issue explicitly defines evidence and review requirements.
9. Use the templates under `templates/` for structured records.
10. Follow `docs/RESEARCH_METHOD.md` and `GOVERNANCE.md`.

## Source handling

- Link to the canonical source.
- Prefer standards, official documentation, official repositories, and technical papers over marketing summaries.
- Do not copy long third-party passages.
- Paraphrase and identify the source.
- Preserve material dates such as release date, observation date, and status date.
- If sources disagree, record the disagreement instead of selecting the convenient answer.

## Context conflicts

Before implementation, inspect repository instructions and the target issue.

If requirements conflict, stop and report:

```text
Context Pack conflict: found
```

Otherwise report:

```text
Context Pack conflict: none
```

Do not silently resolve a material policy, privacy, or publication conflict.

## Required issue workflow

1. Read the target issue and linked repository documents.
2. Search for existing files and duplicate work.
3. Confirm the public/private boundary.
4. Make the smallest coherent change that satisfies the issue.
5. Run relevant validation.
6. Review all new claims and links.
7. Open a pull request.
8. Report unresolved questions as candidates in the PR; do not create follow-up issues.

## Minimum validation

Run the strongest applicable checks available in the repository. Until automated checks are implemented, include at least:

```bash
git diff --check
```

Also verify manually:

- YAML files parse correctly.
- Markdown links are syntactically valid.
- every factual market claim has a primary source.
- no private or embargoed content is included.
- dates and confidence are present in structured records.

After Issue #7 adds validation scripts, use the commands documented by that issue and the repository README.

## Pull request body

Include:

- issue reference
- goal and scope
- files changed
- primary sources added or updated
- fact / inference / hypothesis boundary
- validation performed
- private-data and publication-boundary check
- `Context Pack conflict: none` or details of a conflict
- remaining risks and candidate follow-ups

## Human-only decisions

Do not decide the following without explicit human approval:

- publishing embargoed material
- patent or license strategy changes
- legal or regulatory conclusions
- direct-competitor designation with material strategic impact
- final product priority or go/no-go
- customer interview interpretation that changes evidence level
