# GitHub publishing guide

The repository archive is already arranged around `main`, standard Python
packaging, GitHub Actions, issue forms, Dependabot, citation metadata, and a
release workflow based on built wheel artifacts.

## First publication

Create an empty GitHub repository without adding a generated README, license,
or `.gitignore`. Then run from the extracted `komorebi-pr-lasm` directory:

```powershell
git init
git add .
git commit -m "Initial public release: PR-LASM 2.1.0"
git branch -M main
git remote add origin <REPOSITORY_URL>
git push -u origin main
```

## Recommended repository settings

1. Enable GitHub Actions.
2. Enable Dependabot security and version updates.
3. Enable private vulnerability reporting.
4. Protect `main` and require the `CI` workflow before merging.
5. Require pull requests rather than direct pushes for later changes.
6. Keep downloaded ARC environment files and runtime outputs out of Git.

Suggested repository topics:

```text
signal-processing
wavelets
polyphase
bayesian-inference
world-model
active-planning
exact-reconstruction
scientific-python
```

## First release

After CI passes, create and push tag `v2.1.0` from the reviewed commit:

```powershell
git tag v2.1.0
git push origin v2.1.0
```

The tag-triggered `Release` workflow verifies that the tag matches the package version, reruns the core checks, builds the wheel and source distribution, generates SHA-256 checksums, and publishes those artifacts together with the canonical manuscript PDF.

The optional local ARC fixture archive should remain separate from a public
release unless its distribution terms have been reviewed independently.
