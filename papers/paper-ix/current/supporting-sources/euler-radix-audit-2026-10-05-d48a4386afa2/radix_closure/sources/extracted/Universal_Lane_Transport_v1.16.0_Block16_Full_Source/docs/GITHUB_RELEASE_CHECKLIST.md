# GitHub release checklist

## Before making the repository public

- [ ] Choose the repository owner and name.
- [ ] Select the intended license or licensing split.
- [ ] Replace the interim all-rights-reserved notice when appropriate.
- [ ] Add a stable repository URL to `CITATION.cff` when available.
- [ ] Add an author contact or issue-routing policy when desired.
- [ ] Run `python scripts/check_release.py`.
- [ ] Run `make verify` or the equivalent PowerShell commands.
- [ ] Run `python scripts/package_release.py`.
- [ ] Confirm both ZIP hashes against the generated checksum file.
- [ ] Confirm that GitHub Actions passes.
- [ ] Review the two PDFs, both theorem sections, scope note, and release
      checksums.

## Create and push with GitHub CLI

PowerShell:

```powershell
& .\scripts\publish_to_github.ps1 -Repository "OWNER/universal-lane-transport-theorem" -Visibility public
```

POSIX shell:

```bash
./scripts/publish_to_github.sh OWNER/universal-lane-transport-theorem public
```

The helper initializes Git when needed, creates the remote, pushes `main`, and
tags the version read from `VERSION`.

## After the push

- [ ] Confirm the verification and LaTeX workflows pass.
- [ ] Confirm the tagged-release workflow attaches both PDFs, both ZIPs, and
      the distribution checksum file.
- [ ] Confirm citation metadata renders correctly.
- [ ] Confirm issue templates are enabled.
- [ ] Consider archival deposition only after license and metadata review.
