#!/usr/bin/env python3
"""
Fabric AI Readiness Assessment - scoring and reporting harness.

Loads AssessmentRules.json plus an evidence file, computes weighted readiness
scores per area, applies the blocker gate, and emits JSON + Markdown findings.

Usage:
  python3 assess.py --rules AssessmentRules.json --evidence evidence.json \
                    --out-json findings.json --out-md findings.md
  python3 assess.py --rules AssessmentRules.json --template evidence.template.json
  python3 assess.py --rules AssessmentRules.json --validate
"""
import json, argparse, sys, os, datetime, collections

# ---------------------------------------------------------------- loading

def load_rules(path):
    cfg = json.load(open(path))
    try:
        import jsonschema
        sp = os.path.join(os.path.dirname(os.path.abspath(path)), "assessment-rules.schema.json")
        if os.path.exists(sp):
            jsonschema.validate(cfg, json.load(open(sp)))
    except ImportError:
        pass
    return cfg


def load_evidence(path):
    """Evidence file: {"scope": {...}, "results": {"RULE-ID": {"result": "...", ...}}}"""
    if not path or not os.path.exists(path):
        return {"scope": {}, "results": {}}
    ev = json.load(open(path))
    ev.setdefault("scope", {})
    ev.setdefault("results", {})
    return ev

# ---------------------------------------------------------------- scoring

def score(cfg, evidence):
    sev = cfg["severities"]
    states = cfg["resultStates"]
    results = evidence.get("results", {})

    scored, gate_failures = [], []
    area_acc = collections.defaultdict(lambda: {"earned": 0.0, "possible": 0.0,
                                                "counts": collections.Counter()})

    for rule in cfg["rules"]:
        rid = rule["id"]
        ev = results.get(rid, {})
        state = ev.get("result", "unknown")
        if state not in states:
            raise ValueError(f"{rid}: unknown result state {state!r}. "
                             f"Valid: {', '.join(states)}")

        weight = sev[rule["severity"]]["weight"] * rule.get("weightMultiplier", 1)
        credit = states[state]["credit"]

        row = {
            "id": rid, "area": rule["area"], "title": rule["title"],
            "severity": rule["severity"], "type": rule["type"],
            "result": state, "weight": weight,
            "earned": 0.0, "possible": 0.0,
            "note": ev.get("note", ""), "evidence": ev.get("evidence", ""),
            "owner": ev.get("owner", ""), "dueDate": ev.get("dueDate", ""),
            "remediation": rule["remediation"],
            "impactIfViolated": rule["impactIfViolated"],
            "requirement": rule["requirement"],
            "sourceIds": rule["sourceIds"], "verified": rule["verified"],
            "tags": rule.get("tags", []),
        }

        if credit is None:  # n/a - drops out of numerator and denominator
            row["applicable"] = False
        else:
            row["applicable"] = True
            row["earned"] = credit * weight
            row["possible"] = weight
            a = area_acc[rule["area"]]
            a["earned"] += row["earned"]
            a["possible"] += row["possible"]

        area_acc[rule["area"]]["counts"][state] += 1

        if sev[rule["severity"]]["gate"] and state in ("fail", "unknown"):
            gate_failures.append(row)

        scored.append(row)

    # area scores
    weights = cfg["areaWeights"]
    areas = []
    for a in cfg["areas"]:
        acc = area_acc[a["id"]]
        pct = (100.0 * acc["earned"] / acc["possible"]) if acc["possible"] else None
        areas.append({
            "id": a["id"], "title": a["title"], "weight": weights[a["id"]],
            "score": round(pct, 1) if pct is not None else None,
            "earned": round(acc["earned"], 1), "possible": round(acc["possible"], 1),
            "counts": dict(acc["counts"]),
            "applicableRules": sum(1 for r in scored
                                   if r["area"] == a["id"] and r["applicable"]),
        })

    scoring_areas = [a for a in areas if a["score"] is not None]
    tw = sum(a["weight"] for a in scoring_areas)
    overall = round(sum(a["score"] * a["weight"] for a in scoring_areas) / tw, 1) if tw else 0.0

    level = next((m for m in cfg["maturityLevels"] if m["min"] <= overall <= m["max"]),
                 cfg["maturityLevels"][0])
    gated = bool(gate_failures)
    effective = cfg["maturityLevels"][0] if gated else level

    return {
        "meta": {
            "pack": cfg["packName"], "packVersion": cfg["packVersion"],
            "specVersion": cfg["specVersion"],
            "assessedAt": datetime.datetime.now(datetime.timezone.utc)
                              .isoformat(timespec="seconds"),
            "scope": evidence.get("scope", {}),
        },
        "overallScore": overall,
        "maturity": {
            "numericLevel": level["level"], "numericName": level["name"],
            "effectiveLevel": effective["level"], "effectiveName": effective["name"],
            "meaning": effective["meaning"], "gated": gated,
            "gateReason": (f"{len(gate_failures)} blocker rule(s) not met"
                           if gated else None),
        },
        "gateFailures": [{"id": r["id"], "title": r["title"], "result": r["result"]}
                         for r in gate_failures],
        "areas": areas,
        "rules": scored,
        "summary": summarize(scored),
    }


def summarize(scored):
    c = collections.Counter(r["result"] for r in scored)
    return {
        "totalRules": len(scored),
        "byResult": dict(c),
        "assessmentDebt": c.get("unknown", 0),
        "openFindings": c.get("fail", 0) + c.get("partial", 0),
        "bySeverityFailed": dict(collections.Counter(
            r["severity"] for r in scored if r["result"] in ("fail", "partial"))),
    }

# ---------------------------------------------------------------- reporting

SEV_ORDER = {"blocker": 0, "critical": 1, "high": 2, "medium": 3, "low": 4}

def remediation_plan(rep, limit=None):
    """Open findings ranked by severity then by weight."""
    open_ = [r for r in rep["rules"] if r["result"] in ("fail", "partial", "unknown")]
    open_.sort(key=lambda r: (SEV_ORDER[r["severity"]], -r["weight"], r["id"]))
    return open_[:limit] if limit else open_


def to_markdown(rep, cfg):
    m = rep["maturity"]
    L = []
    L.append(f"# {rep['meta']['pack']} - findings\n")
    L.append(f"*Rule pack {rep['meta']['packVersion']} - assessed {rep['meta']['assessedAt']}*\n")
    sc = rep["meta"]["scope"]
    if sc:
        L.append("**Scope:** " + ", ".join(f"{k}: {v}" for k, v in sc.items()) + "\n")

    L.append(f"## Readiness: {m['effectiveName']} (level {m['effectiveLevel']})\n")
    L.append(f"**Weighted score: {rep['overallScore']} / 100**\n")
    if m["gated"]:
        L.append(f"> Maturity is gated at level 0: {m['gateReason']}. "
                 f"The numeric score of {rep['overallScore']} is reported for "
                 f"trending only.\n")
        L.append("| Blocker | Rule | Result |")
        L.append("|---|---|---|")
        for g in rep["gateFailures"]:
            L.append(f"| `{g['id']}` | {g['title']} | {g['result']} |")
        L.append("")
    L.append(f"{m['meaning']}\n")

    s = rep["summary"]
    L.append("## Summary\n")
    L.append(f"- Rules evaluated: **{s['totalRules']}**")
    L.append(f"- Open findings (fail or partial): **{s['openFindings']}**")
    L.append(f"- Not yet assessed: **{s['assessmentDebt']}**")
    if s["bySeverityFailed"]:
        L.append("- Open by severity: " + ", ".join(
            f"{k} {v}" for k, v in sorted(s["bySeverityFailed"].items(),
                                          key=lambda kv: SEV_ORDER[kv[0]])))
    L.append("")

    L.append("## Area scores\n")
    L.append("| Area | Score | Weight | Rules | Pass | Partial | Fail | N/A | Unknown |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for a in sorted(rep["areas"], key=lambda x: (x["score"] is None, x["score"] or 0)):
        c = a["counts"]
        sc_ = "n/a" if a["score"] is None else f"{a['score']}"
        L.append(f"| {a['title']} | {sc_} | {a['weight']} | {a['applicableRules']} | "
                 f"{c.get('pass',0)} | {c.get('partial',0)} | {c.get('fail',0)} | "
                 f"{c.get('na',0)} | {c.get('unknown',0)} |")
    L.append("")

    plan = remediation_plan(rep)
    L.append(f"## Remediation plan ({len(plan)} items, most severe first)\n")
    cur = None
    for r in plan:
        if r["severity"] != cur:
            cur = r["severity"]
            L.append(f"\n### {cur.title()}\n")
        L.append(f"**`{r['id']}` {r['title']}** - _{r['result']}_")
        L.append(f"- Requirement: {r['requirement']}")
        L.append(f"- Fix: {r['remediation']}")
        L.append(f"- If not fixed: {r['impactIfViolated']}")
        bits = []
        if r["owner"]:
            bits.append(f"owner {r['owner']}")
        if r["dueDate"]:
            bits.append(f"due {r['dueDate']}")
        if bits:
            L.append(f"- {', '.join(bits)}")
        if r["note"]:
            L.append(f"- Note: {r['note']}")
        srcs = [cfg["sources"][s] for s in r["sourceIds"] if s in cfg["sources"]]
        links = [f"[{s['title']}]({s['url']})" if s.get("url") else s["title"]
                 for s in srcs]
        L.append(f"- Source ({r['verified']}): " + "; ".join(links))
        L.append("")
    return "\n".join(L)


def make_template(cfg, path):
    tmpl = {
        "scope": {
            "tenant": "<tenant name>",
            "capacities": "<capacity names>",
            "semanticModels": "<models in scope>",
            "dataAgents": "<agents in scope>",
            "assessor": "<your name>",
        },
        "_legend": {k: v["description"] for k, v in cfg["resultStates"].items()},
        "results": {
            r["id"]: {"result": "unknown", "evidence": "", "note": "",
                      "owner": "", "dueDate": ""}
            for r in cfg["rules"]
        },
    }
    json.dump(tmpl, open(path, "w"), indent=2)
    return len(cfg["rules"])

# ---------------------------------------------------------------- cli

def main():
    ap = argparse.ArgumentParser(description="Fabric AI Readiness assessment harness")
    ap.add_argument("--rules", default="AssessmentRules.json")
    ap.add_argument("--evidence")
    ap.add_argument("--out-json")
    ap.add_argument("--out-md")
    ap.add_argument("--template", help="write a blank evidence template here and exit")
    ap.add_argument("--validate", action="store_true", help="validate the rule pack and exit")
    ap.add_argument("--fail-under", type=float,
                    help="exit non-zero if the overall score is below this (for CI gating)")
    ap.add_argument("--fail-on-blocker", action="store_true",
                    help="exit non-zero if any blocker rule fails")
    a = ap.parse_args()

    cfg = load_rules(a.rules)

    if a.validate:
        print(f"Rule pack {cfg['packName']} {cfg['packVersion']}: "
              f"{len(cfg['rules'])} rules across {len(cfg['areas'])} areas - valid.")
        return 0

    if a.template:
        n = make_template(cfg, a.template)
        print(f"Wrote evidence template with {n} rules -> {a.template}")
        return 0

    rep = score(cfg, load_evidence(a.evidence))

    if a.out_json:
        json.dump(rep, open(a.out_json, "w"), indent=2)
        print(f"-> {a.out_json}")
    if a.out_md:
        open(a.out_md, "w").write(to_markdown(rep, cfg))
        print(f"-> {a.out_md}")
    if not (a.out_json or a.out_md):
        print(to_markdown(rep, cfg))

    m = rep["maturity"]
    print(f"\nScore {rep['overallScore']}/100 - {m['effectiveName']}"
          + (f"  [GATED: {m['gateReason']}]" if m["gated"] else ""), file=sys.stderr)

    if a.fail_on_blocker and rep["gateFailures"]:
        return 2
    if a.fail_under is not None and rep["overallScore"] < a.fail_under:
        return 3
    return 0

if __name__ == "__main__":
    sys.exit(main())
