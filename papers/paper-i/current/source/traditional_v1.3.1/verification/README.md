# Verification provenance

`bundle_check/` contains checks actually executed while assembling this complete ZIP:
Python regression, isolated figure/example regeneration, source PDF rebuild and page
comparison, plus Lean source-hash comparison against the previous audit.

The other directories were carried forward from the previous source package. They
contain historical runs, including earlier failures, later corrections and final
checks. They have not been rewritten to claim a new execution date.

`lean/fresh_verification.json` is the original successful local Lean rebuild record.
Its twenty source hashes match the delivered Lean sources. No compiler execution
occurred in the current packaging pass. Its compiled local objects and the external
Mathlib/toolchain cache are not included.

Historical build logs and generator records may refer to old absolute paths or older
figure hashes. They are evidence of those runs, not the current release inventory.
The current inventories are `RELEASE.json`, `results/run_record.json`, and
`SHA256SUMS.txt` at the package root.

The source rebuild comparison checks that the delivered PDF can be reproduced. It is
not a fresh aesthetic or accessibility review of that PDF.
