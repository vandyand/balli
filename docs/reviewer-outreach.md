# Reviewer Outreach

Balli needs third-party review from both Malli and Basilisp perspectives before
claiming mature parity. This page defines a targeted outreach plan for finding
roughly 100 potential reviewers without mass-tagging people or creating noisy
GitHub notifications.

## Goal

Build a pool of 100 reviewer prospects and convert that into several focused
reviews of small, well-scoped parts of Balli:

- Malli semantic parity
- Basilisp API ergonomics
- Coercion and transformer behavior
- Provider inference and generator behavior
- Packaging, docs, and first-run user experience
- Security and adversarial testing assumptions

The target is not 100 completed reviews. The target is a broad, well-routed
search that makes it realistic to obtain enough independent feedback.

## Outreach Rules

- Do not tag a large list of people in one issue or discussion.
- Prefer public opt-in calls, small direct asks, and channel-specific posts.
- Ask for narrow reviews that fit into 15 to 30 minutes.
- Make it easy to decline, redirect, or review only one surface.
- Track where outreach happened so the same people are not repeatedly pinged.
- Keep review requests tied to concrete files, commands, and open questions.

## Reviewer Lanes

| Lane | Target prospects | Review focus |
|---|---:|---|
| Malli maintainers and contributors | 10-15 | Schema semantics, compatibility matrix, transformer expectations |
| Basilisp maintainers and users | 10-15 | Idiomatic API shape, install path, Python interop friction |
| Clojure validation ecosystem | 20-25 | Specs, coercion, explain output, function contracts |
| Generative testing and fuzzing users | 10-15 | Generator coverage, shrink assumptions, adversarial cases |
| Docs and package adoption reviewers | 15-20 | README, hosted docs, PyPI install, examples, quick-start flow |
| Security and robustness reviewers | 5-10 | Unsafe evaluation, registry boundaries, serialization assumptions |
| Potential production users | 15-20 | Real-world schemas, migration blockers, missing integrations |

The lanes add up to more than 100 because some prospects will overlap. The
operating target is 100 distinct people or organizations considered, with a
smaller subset contacted directly.

## Channels

Use a mix of public channels and small direct requests:

- GitHub issue: keep the canonical review checklist in
  [issue #16](https://github.com/vandyand/balli/issues/16).
- GitHub Discussions: post an opt-in review request if discussions are enabled.
- Basilisp repository/community channels: ask for Basilisp ergonomics review.
- Malli repository/community channels: ask for semantic parity review.
- Clojurians Slack: use focused channels such as Malli, Basilisp, testing, and
  library development where appropriate.
- ClojureVerse: post a longer review request with context and links.
- PyPI/GitHub users: ask people who try the package to file adoption blockers.

Avoid drive-by mentions in unrelated issues. If a channel has posting rules,
follow those rules first.

## Review Requests

Small review asks work better than whole-project asks. Use one of these prompts:

### Malli Semantics

Could you spend 15 to 30 minutes checking whether Balli's documented Malli
compatibility claims look accurate? The highest-value files are:

- `docs/malli-compatibility.md`
- `docs/malli-comparison.md`
- `tests/test_compatibility_corpus.lpy`

Useful feedback: incorrect compatibility claims, missing high-value Malli
features, or places where Balli's behavior should intentionally differ because
of Basilisp/Python semantics.

### Basilisp Ergonomics

Could you try Balli from a fresh clone or `pip install balli` and report what
feels non-idiomatic for Basilisp users? The quickest path is:

```bash
python -m pip install balli
basilisp test tests/test_user_suite.lpy
```

Useful feedback: confusing namespace names, awkward Python/Basilisp interop,
installation friction, or docs gaps.

### Transformers And Coercion

Could you review coercion behavior and report edge cases that should be tested?
The highest-value areas are:

- `balli.transform`
- `balli.integrations`
- `balli.core/coercion-report`
- `balli.core/roundtrip?`

Useful feedback: lossy transforms, surprising string/JSON coercions, missing
error context, or unsafe defaults.

### Generators And Fuzzing

Could you review Balli's generator and fuzz coverage for blind spots? The
highest-value areas are:

- `balli.generator`
- `tests/test_fuzz_stress.lpy`
- `tests/test_adversarial_review.lpy`
- `tests/test_compatibility_corpus.lpy`

Useful feedback: schemas that generate invalid values, shrinker assumptions,
missing adversarial cases, or property checks that are too weak.

### Package And Docs

Could you install Balli and read only the first-run docs? The highest-value
pages are:

- `README.md`
- `docs/install.md`
- `docs/quick-start.md`
- `docs/malli-users-start-here.md`
- `docs/cookbook/parity-tooling.md`

Useful feedback: anything that prevents a new user from installing, running,
or understanding where Balli matches Malli.

## Tracking

Use this lightweight tracker while expanding the search:

| Field | Meaning |
|---|---|
| Prospect | Person, project, organization, or channel |
| Lane | One reviewer lane from this page |
| Source | Why this prospect is relevant |
| Contact method | Issue, discussion, Slack, email, direct message, or none |
| Status | Candidate, contacted, declined, redirected, reviewing, complete |
| Follow-up date | Date to follow up once, if appropriate |
| Notes | Scope requested, response, or review link |

Store detailed private contact data outside the repository. Public repo updates
should contain only opt-in responses, public links, and review outcomes.

## Success Criteria

The outreach push is working when Balli has:

- At least 100 relevant prospects identified across the lanes.
- At least 20 direct or channel-specific review requests sent.
- At least 5 independent review responses or redirects.
- At least 2 substantive external reviews covering Malli semantics or Basilisp
  ergonomics.
- Follow-up issues created for every credible defect or parity gap found.

Until those criteria are met, keep third-party review listed as an open
ecosystem maturity item rather than a completed parity claim.
