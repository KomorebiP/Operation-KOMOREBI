# Publishing this package on GitHub

1. Extract the final ZIP. Use the contents of its `Realization-Boundaries` directory as the repository root.
2. Run `python3 verify_integrity.py` before editing the extracted files.
3. Review the root README, MIT license, citation metadata, monograph, and accepted verification receipt.
4. Commit the source tree, publication files, documentation, and verification evidence. Local `.lake` directories and caches are excluded. No Git LFS is required by the files shipped here.
5. Create a release tag such as `v1.0.0` and use `RELEASE_NOTES.md` as the release description. Attach the final ZIP as a release asset if desired.

To start a new local repository after extraction, run these commands from its root:

```bash
git init
git add .
git commit -m "Realization Boundaries 1.0.0"
git branch -M main
```

After creating your GitHub repository, use the remote and push commands GitHub supplies for its actual URL.

Creating this ZIP does not publish a repository or release. No repository URL or DOI has been invented. Add the actual public repository URL to the citation metadata after it exists.

For a later mathematical change, preserve the existing accepted evidence, run checks into a fresh directory, update the statement map and ledger, and create a new release version. Regenerate the outer manifest and checksums for a changed distribution. Keep development failures distinguishable from accepted evidence.
