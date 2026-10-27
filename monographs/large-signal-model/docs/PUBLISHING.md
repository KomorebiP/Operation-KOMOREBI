# Publishing this release

This package is prepared for a GitHub repository. No repository, tag or remote release was created by the packaging work. The destination account and repository are intentionally not guessed.

Keep the checked formal companion at `Lean/`, the publication at `Monograph/` and the reference code at `Reference_Laboratory/`. Commit the complete frozen Lean payload, including its `history/`, `verification/` and `MANIFEST.json`. Do not commit generated dependency or proof-object directories. The root `.gitignore` does not exclude the publication PDF at `Monograph/build/`.

Before publishing, run from the repository root:

```bash
python3 ci/quick_checks.py --project Lean
```

Use `git ls-files` to confirm that all expected Lean manifest files and the publication PDF are tracked. The outer release archive should carry its own complete file inventory and checksums. Those packaging checks do not replace the formal companion's source-bound verification.

When you choose a GitHub destination, create or select that repository, push the reviewed source commit, and run the opt-in full workflow. Inspect its new receipt before describing it as a GitHub CI verification. The completed verification bundled with this release remains a separate record.

The manually dispatched **Prepare verified draft release** workflow performs full clean verification, packages the reviewed commit through `ci/package_release.py`, and creates a draft for static version `v1.0.0`. Only its draft job has repository write permission. An existing tag must resolve to the verified commit, and an existing release is never overwritten. The missing tag may be created at that verified commit by the draft operation.

A tag and draft release can also be created explicitly through the CLI. Substitute your actual repository, reviewed commit and built archive paths:

```bash
git tag -a v1.0.0 REVIEWED_COMMIT -m "Large Signal Model 1.0.0"
git push origin v1.0.0
gh release create v1.0.0 RELEASE_ARCHIVE.zip SHA256SUMS.txt \
  --repo OWNER/REPOSITORY --verify-tag --draft \
  --title "Large Signal Model 1.0.0" --notes-file RELEASE_NOTES.md
```

Review the draft's files, title and notes, then publish it through GitHub when intended. No workflow in this repository publishes a release automatically. Authentication belongs to your existing GitHub CLI or browser session; credentials are not stored in this repository.
