#!/usr/bin/env python3
"""Generate the readiness console HTML with the rule pack embedded."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = json.load(open(os.path.join(ROOT, "AssessmentRules.json")))

# trim the payload to what the page renders
slim = {
    "packName": cfg["packName"], "packVersion": cfg["packVersion"],
    "updated": cfg["updated"],
    "severities": cfg["severities"], "resultStates": cfg["resultStates"],
    "areaWeights": cfg["areaWeights"], "maturityLevels": cfg["maturityLevels"],
    "areas": cfg["areas"], "sources": cfg["sources"],
    "rules": [{k: r[k] for k in
               ("id","area","title","requirement","rationale","severity","type",
                "appliesTo","check","remediation","impactIfViolated","sourceIds",
                "verified","tags")
               if k in r} | ({"limit": r["limit"]} if "limit" in r else {})
                          | ({"notes": r["notes"]} if "notes" in r else {})
                          | ({"weightMultiplier": r["weightMultiplier"]}
                             if r.get("weightMultiplier", 1) != 1 else {})
              for r in cfg["rules"]],
}

TRIAGE = ["SCH-001","SCH-005","PRF-003","AGT-001","AGT-005","MEA-007",
          "VER-001","MOD-001","PRF-005"]
TRIAGE_WHY = {
 "SCH-001":"Does an AI data schema exist at all, or is the full model exposed?",
 "SCH-005":"Is AgentSchemaReduced appearing? The platform is already truncating for you.",
 "PRF-003":"Capture the generated DAX and trace it. Measure actual scan breadth per question.",
 "AGT-001":"Do source instructions state default filters, grain and join paths?",
 "AGT-005":"For KQL and time-series sources, is a default time window enforced?",
 "MEA-007":"Are common calculations pre-built, or composed from scratch each time?",
 "VER-001":"Are the top recurring questions served by verified answers?",
 "MOD-001":"Is the model a star schema? A flat model makes efficient DAX hard to generate.",
 "PRF-005":"Measure tokens per question. Cached input bills at a tenth the uncached rate.",
}
slim["triage"] = [{"id": i, "why": TRIAGE_WHY[i]} for i in TRIAGE]

HTML = open(os.path.join(ROOT, "src", "page.template.html")).read()
out = HTML.replace("/*__RULEPACK__*/ null",
                   json.dumps(slim, separators=(",", ":")))
p = os.path.join(ROOT, "readiness-console.html")
open(p, "w").write(out)
print(f"wrote {p}  ({len(out)/1024:.0f} KB, {len(slim['rules'])} rules)")
