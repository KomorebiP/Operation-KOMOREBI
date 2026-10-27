# Releasing

A source handoff and public publication are different events. This release has an
inherited all-rights-reserved license. Public open-source publication needs the
owner's explicit license decision. No remote repository or package index was changed.

Run the procedure in [REPRODUCIBILITY](../REPRODUCIBILITY.md). Confirm the version in
`pyproject.toml`, both API namespaces and `CITATION.cff`. Preserve original-source
hashes, current verification logs and a scoped release audit. A final archive contains
no local game sources, credentials, build caches or result scratch directories.

The CI workflow tests the core on Linux/Windows and Python 3.12/3.13 when actually run.
The release workflow builds artifacts on a matching version tag. It does not publish
a public release on tag push. Manual draft publication additionally requires a matching
tag, an explicit input and a passing owner-license gate. The gate intentionally fails
for the current metadata. It is an engineering interlock, not a legal opinion.

See [publishing notes](../GITHUB_PUBLISHING.md) and the [current audit](../RELEASE_AUDIT.md).
