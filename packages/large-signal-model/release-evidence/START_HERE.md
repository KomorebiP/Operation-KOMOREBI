# Komorebi Large Signal Model 2.3.0

Author: Komorebi P.  
Date: 9 October 2026  
Status: locally verified finite-core source handoff. Not remotely published.

## Open these first

- `docs/Komorebi_Large_Signal_Model_2.3.0_Guide.pdf`: new 22-page guide with nine
  pairs of Python-generated figures, worked mathematics, APIs and claim boundaries.
- `docs/RELEASE_AUDIT.md`: current verification, repaired failures and limitations.
- `source/komorebi-pr-lasm`: the complete current repository, including source,
  tests, examples, paper, guides, build tools and row-level verification records.
- `dist`: the installable wheel and complete source distribution.

## Install from this folder

For a new connected Windows environment:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python -m pip install .\dist\komorebi_pr_lasm-2.3.0-py3-none-any.whl
.\.venv\Scripts\python -m komorebi_pr_lasm self-check
```

For an existing environment with compatible NumPy and SciPy already installed,
the following route does not download dependencies:

```powershell
python -m pip install --no-index --no-deps .\dist\komorebi_pr_lasm-2.3.0-py3-none-any.whl
python -m komorebi_pr_lasm self-check
```

The full handoff is not an all-platform dependency wheelhouse. Do not co-install
this core with the separate `komorebi-arc3-offline` ARC3 agent distribution, because
they own the same compatibility namespace. Runtime uses no hosted model.

## Verify the delivered bytes

```powershell
python verify_release.py --strict
```

Run the strict check before creating a local environment or test outputs here.
The source repository has its own `scripts/verify_manifest.py`. Checksums detect
changes relative to the supplied manifest. They are not a digital signature.

## Companion material is preserved, not merged

`predecessors` holds the unchanged core 2.1.0 archive. `companions` holds the recovered
October signal reconstruction collection, the integer Euler bridge, and the older
ARC2 diagnostic branch. The three reconstruction reading PDFs are also exposed in
`companions/reading`. They remain historical companion documents, not freshly
certified 2.3.0 runtime or proof-assistant results. The old ARC2 archive is not claimed
to be the latest ARC solver. No score is transferred between these lineages.

The optional 25-game local fixture source archive is not included here. It was used
for eight static tests and then excluded from the distributable source. This bundle
contains no official ARC execution result. Synthetic interactive results include
explicit probes and resets, whose accounting is in the audit.

## License and public release

The recovered core license remains all rights reserved / LicenseRef-Proprietary.
This handoff is not an open-source license grant. The owner must explicitly select
a public license before open-source publication. No GitHub repository, release or
package index was changed. The supplied workflows do not publish automatically on
tag push. Third-party components and companion archives retain their own notices.

Final file counts, executed tests and scope exclusions are recorded in
`verification/FINAL_ARTIFACT_CHECKS.json`. The runtime contains 42 Python files and
7,078 source lines. The name “Large Signal Model” is not a parameter-count claim.
