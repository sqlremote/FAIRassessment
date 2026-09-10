Drop your own rule files here as `*.json` with the shape:

    { "rules": [ { "id": "ORG-001", "area": "schema", ... } ] }

They are merged by `build_rules.py`. A custom rule whose `id` matches a built-in
rule **overrides** it — that is the supported way to change a threshold to your
own standard while keeping the pack updatable. Use your own id prefix (ORG-, or
your team's) for genuinely new rules. See METHODOLOGY.md for the field reference.
