# Publishing AM-SPD 1.0.0

## Intended repository layout

The package metadata names this monorepo location:

```text
KomorebiP/Operation-KOMOREBI
packages/komorebi-am-spd
```

This is a configured destination, not evidence that the package has been pushed, merged, tagged, or made public. Verify the actual repository, visibility, and access before publishing. The release's `LICENSE` and `CITATION.cff` define its reuse terms and citation metadata.

## Validate before creating a tag

From the package directory:

```powershell
python -m pytest
python -m am_spd verify --full
python -m am_spd reproduce-paper --output-dir artifacts\paper-replay --strict-reference
python -m build
```

Test the built wheel in a clean environment outside the checkout. Run `python -m am_spd verify --full` there and replay at least one paper case with `--strict-reference`; successful `info` output alone does not verify reconstruction or bundled resources. Rebuild a wheel from the source distribution and test that artifact independently.

The full source bundle also contains `research/original`. When that snapshot is present, run `scripts/verify_full.ps1` or `scripts/verify_full.sh`. A compact source distribution may omit the research snapshot; its package tests and bundled paper replay remain available.

For monorepo use, copy the templates from `monorepo/.github/workflows` to the root `.github/workflows` directory. Workflows nested inside a package directory do not run as root GitHub Actions workflows. Check the generated workflows and actual repository URLs before publishing.

## Monorepo tag

After review and successful CI, use a package-qualified tag:

```powershell
git tag -a am-spd-v1.0.0 -m "AM-SPD 1.0.0"
git push origin am-spd-v1.0.0
```

These commands publish the tag. They are examples, not actions performed by preparing this release. The build workflow uploads distribution artifacts to its Actions run; it does not publish to PyPI or create a GitHub Release automatically.

## Standalone mirror

A standalone mirror is optional. If creating one, review its repository metadata and workflow paths before using `scripts/publish_github.ps1`. Existing uploader scripts perform remote writes and should be run only for the intended destination.
