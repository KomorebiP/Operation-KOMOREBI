# GitHub staging

The proposed destination is **KomorebiP/komorebi-math**, initially **private**, on
branch `main`. This is a proposed destination, not a claim that a remote exists.
The connected GitHub account was verified as KomorebiP. No repositories were
exposed to the connector, and direct reads of the two prior repository names
returned 404. Those results do not prove the repositories do not exist.

## Prepared here

The source is the sanitized Research Preview 1 RC1, not the private research
archive. Its 92 mathematical Lean files and dependency pins are unchanged.
New Git history begins with that export and then adds GitHub maintenance files.
No raw conversations, cumulative predecessor archives, runtime binaries, or
private Git history are imported. Commit author and committer use Komorebi P.
and the ID-based GitHub no-reply address recorded in REPOSITORY.json.

## Inspect and upload privately

The supplied Git bundle retains the clean local commit history. Clone the bundle
in a new directory rather than copying an old research repository:

```bash
git clone Komorebi_Research_Preview_1_GitHub_Proof_Replayed.bundle komorebi-math
cd komorebi-math
git remote remove origin
git config user.name "Komorebi P."
git config user.email "52508850+KomorebiP@users.noreply.github.com"
python -B tools/check_github_ready.py --check-git
python -B tools/create_private_repo.py
```

The last command is a dry run. It changes nothing locally or remotely. To execute
the reviewed plan, use Git and the official GitHub CLI authenticated as KomorebiP:

```bash
gh auth login --hostname github.com --git-protocol https --scopes workflow
python -B tools/create_private_repo.py --execute
```

These commands also work in PowerShell with Python on PATH. The additional
workflow scope permits pushing the included workflow definitions with CLI OAuth
authentication. An externally supplied token must have equivalent permissions. Never paste a personal
access token into this repository, an issue, or a chat transcript. The helper uses
GitHub CLI's credential integration without writing a token into a remote URL.

The helper checks the account, clean branch, sealed files, and pseudonymous history.
It creates only a private repository or accepts an existing empty private one.
It refuses an existing remote history, a public destination, or a different owner.
It pushes only `main`, never force-pushes, and verifies the remote commit afterward.
It does not create tags, publish a release, choose a license, or change visibility.
If a failure occurs after remote creation, it leaves that private repository in
place and reports the incomplete step; it does not silently delete or overwrite it.

## Workflows and evidence boundaries

**Artifact checks** runs on pushes to main and pull requests. It checks source and
artifact identity, local links, safeguards, and the finite Python demonstration on
Linux and Windows. A passing artifact check is not a Lean proof replay.

**Extended reference audit** is manual. It installs the stated SymPy pin and saves
fresh finite evidence separately from historical evidence.

**Pinned Lean replay** is manual. It asks the pinned official Lean action to obtain
the exact toolchain and mathlib cache, then executes the existing clean proof
replay, full axiom inventories, and negative controls. A bootstrap failure blocks
the gate. Pins are never upgraded merely to make the job pass. GitHub caching is
disabled for this preparation path; the public mathlib cache is still used.

All top-level workflow actions are pinned to verified upstream commit IDs.
Permissions are read-only. There are no repository secrets, automatic publication
jobs, tag pushes, or privileged pull-request-target workflows. Upstream actions
perform runtime downloads; pinning their source does not independently rebuild or
freeze every transitive service. Hosted-runner outcomes remain untested until upload.

## Fresh local proof replay

The prepared source now passed the complete clean Lean replay with a restored,
checksum-verified pinned runtime and cache. See the [reproduction checkpoint](github/REPRODUCTION_STATUS.md)
and its separate receipt. This does not close the fresh public-bootstrap or hosted
workflow gate. The manual Lean job now checks its full receipt and records minimal
context even when bootstrap fails. No context-only record is treated as proof success.

## Finish before a public release

Use [MAINTAINER_CHECKLIST.md](MAINTAINER_CHECKLIST.md). First obtain and inspect a
fresh successful pinned Lean receipt for the exact candidate commit. Then approve
rights, attribution, file selection, and public publication. Branch protection,
review requirements, private vulnerability reporting, and repository topics are
settings to configure on the actual remote, not settings asserted by these files.

If an existing Operation-KOMOREBI repository contains private history, do not make
it public to expose this export. A separate sanitized repository avoids that step.
The research roadmap remains in [FUTURE_RESEARCH.md](FUTURE_RESEARCH.md).

## Editing this sealed candidate

The hash ledger deliberately makes unreviewed edits fail artifact CI. After reviewing
an intended documentation or tooling change, inspect the ledger difference with
`python -B tools/seal_export.py`, then explicitly apply it with `--write` and rerun
the tests. This helper first checks the frozen mathematical source; it does not
approve theorem edits or publication. Never rewrite SOURCE_IDENTITY.json merely
to disguise a change to the Block 34 proof source.

## Primary references checked for preparation

- [GitHub CLI private repository creation](https://cli.github.com/manual/gh_repo_create)
- [Commit email privacy](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address)
- [Immutable action references and workflow security](https://docs.github.com/en/actions/reference/security/secure-use)
- [Pinned Lean action source](https://github.com/leanprover/lean-action/tree/50fcf42d2e460296f1a34b402e990d1b24f8b596)

The preparation does not establish cryptographic authorship, independent proof
review, permission to redistribute, or a successfully created remote repository.
