#!/usr/bin/env python3
"""Merge rule fragments into a single AssessmentRules.json config."""
import json, glob, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def build():
    meta = json.load(open(os.path.join(ROOT, "rules", "_meta.json")))
    srcs = json.load(open(os.path.join(ROOT, "rules", "_sources.json")))

    rules = []
    for f in sorted(glob.glob(os.path.join(ROOT, "rules", "[0-9]*.json"))):
        rules.extend(json.load(open(f))["rules"])
    # user extension point
    for f in sorted(glob.glob(os.path.join(ROOT, "rules", "custom", "*.json"))):
        rules.extend(json.load(open(f))["rules"])

    # dedupe by id: later (custom) wins
    byid = collections.OrderedDict()
    for r in rules:
        byid[r["id"]] = r
    rules = list(byid.values())

    out = dict(meta)
    out["sources"] = srcs["sources"]
    out["areas"] = build_areas(rules, meta)
    out["rules"] = rules
    out["ruleCount"] = len(rules)
    return out

AREA_TITLES = {
 "tenant":"Tenant & admin enablement",
 "capacity":"Capacity, SKU, region & cost",
 "workspace":"Workspace & item governance",
 "schema":"AI data schema & scope reduction",
 "model":"Semantic model structure",
 "metadata":"Names, descriptions & linguistics",
 "measures":"Measures & DAX",
 "datatype":"Data types & data quality",
 "security":"Security, RLS & compliance",
 "verified":"Verified answers",
 "instructions":"AI instructions",
 "agent":"Fabric data agent configuration",
 "performance":"Performance & query efficiency",
 "validity":"Response validity & relevance",
 "operations":"Operations, ALM & adoption",
}

def build_areas(rules, meta):
    counts = collections.Counter(r["area"] for r in rules)
    areas = []
    for k, w in meta["areaWeights"].items():
        areas.append({"id": k, "title": AREA_TITLES.get(k, k), "weight": w,
                      "ruleCount": counts.get(k, 0)})
    return areas

def validate(cfg):
    errs = []
    ids = set()
    valid_sev = set(cfg["severities"])
    valid_area = {a["id"] for a in cfg["areas"]}
    valid_src = set(cfg["sources"])
    required = ["id","area","title","requirement","rationale","severity","type",
                "appliesTo","check","remediation","impactIfViolated","sourceIds","verified"]
    for r in cfg["rules"]:
        rid = r.get("id","<missing>")
        if rid in ids: errs.append(f"{rid}: duplicate id")
        ids.add(rid)
        for f in required:
            if f not in r or r[f] in (None, "", []):
                errs.append(f"{rid}: missing required field '{f}'")
        if r.get("severity") not in valid_sev:
            errs.append(f"{rid}: bad severity {r.get('severity')!r}")
        if r.get("area") not in valid_area:
            errs.append(f"{rid}: bad area {r.get('area')!r}")
        for s in r.get("sourceIds", []):
            if s not in valid_src:
                errs.append(f"{rid}: unknown sourceId {s!r}")
    for a in cfg["areas"]:
        if a["ruleCount"] == 0:
            errs.append(f"area {a['id']}: no rules")
    return errs

if __name__ == "__main__":
    cfg = build()
    errs = validate(cfg)
    if errs:
        print("VALIDATION FAILED:", file=sys.stderr)
        for e in errs: print("  -", e, file=sys.stderr)
        sys.exit(1)
    p = os.path.join(ROOT, "AssessmentRules.json")
    json.dump(cfg, open(p, "w"), indent=2)
    print(f"OK  {cfg['ruleCount']} rules -> {p}")
    c = collections.Counter(r["area"] for r in cfg["rules"])
    s = collections.Counter(r["severity"] for r in cfg["rules"])
    for a in cfg["areas"]:
        print(f"  {a['id']:<13} {a['ruleCount']:>3}  (weight {a['weight']})")
    print("  severity:", dict(s))
