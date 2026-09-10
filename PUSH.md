# Pushing this to GitHub

This folder is already a git repository with one commit on `main`. Nothing has been pushed —
that step needs your credentials, which only exist on your machine.

## First: confirm the repo URL

The link shared was `github.com/marydev_microsoft/FAIRDRAFT`. GitHub account names cannot contain
underscores, so that owner name is not valid as written — it is likely `marydev-microsoft`, or a
different account or organisation. Open the repo, click the green **Code** button, and copy the
HTTPS URL exactly. Use that below in place of `<REPO-URL>`.

## If this folder already has git history

Open a terminal here and run:

```bash
git remote add origin <REPO-URL>
git push -u origin main
```

If the remote already exists (you'll see `error: remote origin already exists`):

```bash
git remote set-url origin <REPO-URL>
git push -u origin main
```

## If this folder has no `.git` directory

That happens if the files were copied in without the history. Run:

```bash
git init -b main
git add .
git commit -m "Initial draft: Fabric AI readiness rule pack"
git remote add origin <REPO-URL>
git push -u origin main
```

## If GitHub rejects the push

**`Updates were rejected because the remote contains work that you do not have locally`** — the repo
was created with a README or .gitignore, so it already has a commit. Either:

```bash
git pull --rebase origin main    # keep both, replay your commit on top
git push -u origin main
```

or, if the remote only has GitHub's auto-generated starter files and you want this content to
replace them:

```bash
git push -u --force-with-lease origin main
```

`--force-with-lease` refuses if someone else pushed in the meantime; plain `--force` does not. Prefer
the lease.

**`main` vs `master`** — if the repo was created with a `master` default branch, either rename yours
(`git branch -M master`) or push explicitly (`git push -u origin main:main`) and set `main` as the
default in the repo's Settings → Branches.

**Authentication prompts** — GitHub no longer accepts account passwords over HTTPS. Use
[GitHub CLI](https://cli.github.com/) (`gh auth login`), Git Credential Manager (bundled with Git for
Windows), or a personal access token as the password.

## After the first push

CI runs automatically on push to `main` and on pull requests — see `.github/workflows/validate.yml`.
It checks that:

- the rule pack validates against its JSON Schema
- `AssessmentRules.json` matches a fresh build from `rules/` (so nobody hand-edits the generated file)
- every rule cites a resolvable source, every source is used, and every `hard` limit is `documented`
- the blocker gate returns exit 2 on unassessed blockers
- the console and the CLI harness score the sample evidence identically
- the workbook rebuilds with the right row count

All of these pass on this commit — they were run locally before it was made.

## A note on what not to commit

`.gitignore` deliberately excludes `evidence.json`, `evidence-*.json`, `findings.json` and
`findings.md`. Real assessment evidence names your tenant, capacities, models and owners, and often
records which controls are currently failing. That is not repo material. The samples under
`samples/` are synthetic and safe to keep.
