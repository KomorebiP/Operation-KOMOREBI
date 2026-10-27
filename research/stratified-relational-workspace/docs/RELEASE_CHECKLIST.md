# Release checklist

## Before tagging

- [ ] Resolve or document every confirmed item in `ERRATA.md`.
- [ ] Run `python scripts/repo.py verify --strict` in a clean checkout.
- [ ] Confirm the rebuilt PDF has 209 pages unless the version intentionally changes the manuscript.
- [ ] Review `audits/priority_register.csv` for novelty and precedence changes.
- [ ] Update `CHANGELOG.md`, `RELEASE_NOTES.md`, `VERSION`, and `CITATION.cff`.
- [ ] Confirm the author name, release date, repository URL, and DOI metadata when available.
- [ ] Decide whether the all-rights-reserved notice remains appropriate.
- [ ] Run `python scripts/repo.py package --strict`.
- [ ] Verify `dist/SHA256SUMS.txt`.

## Publish

```bash
git tag -a v1.0.0 -m "Stratified Relational Workspace Theory v1.0.0"
git push origin v1.0.0
```

The release workflow builds and verifies the monograph, creates versioned release assets, and publishes them through GitHub Releases.

## After publishing

- [ ] Confirm the release assets and checksums are downloadable.
- [ ] Confirm GitHub renders `CITATION.cff` correctly.
- [ ] Archive the release with Zenodo or another preservation service when desired.
- [ ] Add the DOI to `CITATION.cff`, `CITATION.bib`, and the README in the next metadata commit.
