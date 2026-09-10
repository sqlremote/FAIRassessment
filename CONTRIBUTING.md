# Contributing

## The rule pack is generated

`AssessmentRules.json` is built from `rules/`. Never hand-edit it — your change will be
overwritten on the next build. Edit the fragment file, then:

```bash
python3 src/build_rules.py       # merges + validates, fails on any error
python3 src/build_workbook.py    # regenerate the workbook
python3 src/build_page.py        # regenerate the console
```

Commit the regenerated `AssessmentRules.json`, `AssessmentRules.xlsx` and
`readiness-console.html` alongside the fragment change. CI fails if they are out of sync.

## Adding a rule

Put new rules in `rules/custom/*.json` with your own id prefix (`ORG-001`), or extend a
built-in fragment if you're changing the pack itself.

```json
{ "rules": [{
  "id": "ORG-001",
  "area": "schema",
  "title": "Short imperative statement of the control",
  "requirement": "What must be true. Normative.",
  "rationale": "Why it matters for enablement, answer quality, or query cost.",
  "severity": "high",
  "type": "config",
  "appliesTo": ["copilot-powerbi", "fabric-data-agent"],
  "check": {
    "method": "dax",
    "how": "The actual procedure for gathering evidence.",
    "operator": "lte",
    "threshold": 200,
    "unit": "characters"
  },
  "remediation": "What to do about a failure.",
  "impactIfViolated": "What goes wrong if you don't.",
  "sourceIds": ["ms-copilot-evaluate-data"],
  "verified": "documented",
  "tags": ["metadata"]
}]}
```

A custom rule whose `id` matches a built-in rule **overrides** it. That is the supported way
to tighten or relax a threshold to your own standard without forking the pack.

## Field rules

**`severity`** drives the weight: `blocker` 13 · `critical` 8 · `high` 5 · `medium` 3 · `low` 1.
Reserve `blocker` for things that make the AI surface non-functional or untrustworthy outright —
a failed blocker gates the whole assessment at level 0. There are currently 8; adding a ninth
should be a deliberate, argued decision.

**`verified`** is the honesty field and reviewers will check it:

- `documented` — the requirement is stated in a cited source. Link it in `sourceIds`.
- `inferred` — engineering judgement built on documented platform behaviour. Any numeric
  threshold you invented belongs here, and say so in the `unit` string too
  (e.g. `"percent of golden questions correct (recommended promotion gate)"`).
- `community` — unofficial. Note where it came from.

Do not mark something `documented` because it is obviously true. Mark it `documented` because a
source says it.

**`sourceIds`** must reference a key in `rules/_sources.json`. Add new sources there with a
title, URL and retrieval date. A rule with no source will not build.

**`limit`** is only for actual platform limits. Set `hard: true` when the platform enforces it
and `false` for published guidance. Every `hard` limit must be `documented`.

## Adding an area

Add it to `areaWeights` in `rules/_meta.json` and to `AREA_TITLES` in `src/build_rules.py`.
Area weights are a statement of priorities — changing them changes every historical score, so
raise it in a PR description rather than slipping it in.

## Before opening a PR

```bash
python3 src/build_rules.py
python3 src/assess.py --rules AssessmentRules.json --validate
python3 src/assess.py --rules AssessmentRules.json --evidence samples/evidence.sample.json --out-md /dev/null
```

CI runs these plus a check that the committed artifacts match a fresh build.
