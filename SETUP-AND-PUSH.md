# Getting this onto GitHub — Windows, from scratch

Everything below runs in **PowerShell**. Open it with Start → type `powershell` → Enter.

---

## Step 1 — Is git installed?

```powershell
git --version
```

**If you see a version number** (e.g. `git version 2.47.1.windows.1`) → skip to Step 2.

**If you see** `'git' is not recognized...` → install it:

```powershell
winget install --id Git.Git -e --source winget
```

Then **close PowerShell and open a new one** — the PATH only updates in new windows. Check again
with `git --version`.

If `winget` isn't available either, download the installer from <https://git-scm.com/download/win>
and accept the defaults. The defaults matter: they include **Git Credential Manager**, which is what
makes Step 5 a browser sign-in instead of a token hunt.

---

## Step 2 — Tell git who you are

```powershell
git config --global user.name "Mary Mary"
git config --global user.email "your-github-email@example.com"
```

Use the email **on your GitHub account**. If you'd rather not publish an address, GitHub gives you a
private one — Settings → Emails → *Keep my email addresses private* — it looks like
`12345678+username@users.noreply.github.com`. Use that as the email above.

This is only about commit authorship. It is not your login.

---

## Step 3 — Confirm the repo URL

The link shared earlier was `github.com/marydev_microsoft/FAIRDRAFT`. **That owner name can't be
right** — GitHub account names cannot contain underscores. It's likely `marydev-microsoft`, or a
different account or organisation.

Open the repo in a browser, click the green **Code** button, choose **HTTPS**, and copy the URL. It
looks like:

```
https://github.com/SOMETHING/FAIRDRAFT.git
```

Use that exact string wherever `<REPO-URL>` appears below.

---

## Step 4 — Create the working repo from the bundle

`FAIRDRAFT.bundle` holds the complete history. Cloning from it also restores
`.github/workflows/validate.yml`, which could not be written to your disk directly (workflow files
execute code in CI, so remote tools are blocked from writing them).

```powershell
cd C:\MarysFiles
git clone FAIRDRAFT\FAIRDRAFT.bundle FAIRDRAFT-repo
cd FAIRDRAFT-repo
```

Confirm you got everything:

```powershell
git log --oneline
git ls-files | Measure-Object -Line
```

Expect **3 commits** and **30 files**.

`C:\MarysFiles\FAIRDRAFT` (the original loose copy) is now redundant — `FAIRDRAFT-repo` is the real
repository. Keep the old folder until the push succeeds, then delete it so you don't edit the wrong
copy later.

---

## Step 5 — Point it at GitHub and push

Cloning from a bundle sets `origin` to the bundle file, so this **replaces** it:

```powershell
git remote set-url origin <REPO-URL>
git remote -v
```

Both lines should now show your GitHub URL. Then:

```powershell
git push -u origin main
```

**First push will open a browser** asking you to sign in to GitHub and authorise Git Credential
Manager. Approve it. Credentials are cached in Windows Credential Manager, so this happens once.

`-u` sets `origin/main` as the upstream, so future pushes are just `git push`.

---

## Step 6 — Confirm

Refresh the repo page. You should see the README rendered, and an **Actions** tab where the
`Validate rule pack` workflow is running. It checks that:

- the rule pack validates against its JSON Schema
- `AssessmentRules.json` matches a fresh build from `rules/` — so nobody hand-edits the generated file
- every rule cites a resolvable source, every source is used, and every `hard` limit is `documented`
- the blocker gate returns exit 2 on unassessed blockers
- the console and the CLI harness score the sample evidence identically
- the workbook rebuilds with the right row count

All six passed locally before the commit was made, so a red run means something changed in transit —
tell me and I'll look.

---

## If the push is rejected

**`Updates were rejected because the remote contains work that you do not have locally`**

The repo was created with a README or .gitignore, so it already has a commit. Either keep both:

```powershell
git pull --rebase origin main
git push -u origin main
```

or, if the remote only holds GitHub's starter files and you want this content to replace them:

```powershell
git push -u --force-with-lease origin main
```

`--force-with-lease` refuses if someone else pushed meanwhile. Plain `--force` doesn't. Prefer
the lease.

**`src refspec main does not match any`** — you're on a differently-named branch. Check with
`git branch --show-current` and either rename (`git branch -M main`) or push that name.

**Repo default branch is `master`** — push explicitly and change the default afterwards in
Settings → Branches:

```powershell
git push -u origin main:main
```

**`remote: Repository not found`** — usually a wrong URL (see Step 3) or an account without access.
Confirm you can open the repo in a browser while signed in as the same account.

---

## Day-to-day after this

```powershell
git add .
git commit -m "what changed"
git push
```

If you edit anything under `rules/`, regenerate before committing or CI will fail:

```powershell
python src\build_rules.py
python src\build_workbook.py
python src\build_page.py
```

---

## Don't commit real evidence

`.gitignore` already excludes `evidence.json`, `evidence-*.json`, `findings.json` and `findings.md`.
A filled-in assessment names your tenant, capacities, models and owners, and records which controls
are currently failing. That doesn't belong in a repo — especially not one that might become public.
The files under `samples/` are synthetic and safe.
