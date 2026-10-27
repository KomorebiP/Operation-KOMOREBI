# Supplemental archive-review evidence, v1.12.0

Final status: **PASS**, using the independently root-reviewed external amendment.
The primary release ZIP and frozen project were not modified.

The original frozen checker failed because its directory-name exclusion also
matched six historical text/source provenance files in an inherited `runtime/`
directory. Those files are required to remain byte-identical to the pinned parent.
The original failure report is preserved byte-for-byte as `attempt_001_FAIL.json`.
Its original path and hash are retained in `FAILURE_PRESERVATION.json`.

The small external amendment preserves the global prohibition on compiled-file
suffixes and applies excluded directory names only outside `inherited_v1.11.0/`.
All inherited files still have to equal the pinned predecessor ZIP. The original
archived checker is bound to its original frozen hash, while the amended running
checker is honestly identified in the final report. Both sources, the exact diff,
freeze/contract, 29 bounded preparation tests, amendment record, and root review
are included. The initial pending amendment record is preserved as history;
`ROOT_REVIEW.json`, `FINAL_STATUS.json`, and `attempt_002_PASS.json` record the
subsequent accepted review and actual successful retry.

The final retry checked every actual ZIP payload hash and CRC, safe paths, all
5,863 predecessor files, source/export/review bindings, 238 recorded commands,
44 controls, 153 production modules plus three roots, 1,693 explicit theorems,
and 5,048 declarations including all 4,982 inherited identities and 66 new full
types. Coverage is 13 complete groups, no partial groups, and WR10–WR12 remaining.

This supplement is an artifact-identity review. Its author also authored the
CoordinateCovector proof, so it makes no claim to independently audit that proof;
a separate reviewer owns the bound mathematical audit.

`SHA256SUMS.txt` covers every supplemental artifact except itself. Reproducible
Python cache files are excluded. The main archive has SHA-256
`6304d70013b0baf30619b7c724bef4710dbd085ee590b825f9e4eecf4fc375e6`.
