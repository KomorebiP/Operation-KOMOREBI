# Attempt 04 — second, synchronous full-replay failure

Reviewed: 2026-10-18T19:55:11.467935+00:00

The unchanged candidate04 source, SHA-256 `fe1c43800e7d9d4be586b1cf37f04fb18dfa7fe02547610698fcc15072d4937f`, again failed full execution under `Elab.async=false`: terminal exit code **−9** after **196.124 seconds**, with an empty compiler log and no successful terminal output artifact. The final replay status is **PARTIAL_OR_FAIL**. The source fingerprints stayed unchanged.

The separately retained runtime resource receipt records the cgroup OOM and OOM-kill counters increasing from one to two. Synchronous scheduling therefore did not prevent this resource failure. The empty log does not identify the declaration active at termination; the later bounded diagnostic is separate evidence about the comparison-package conversion issue.

- Full-replay receipt SHA-256: `f9fa6a3a32ed0f33a48fce5f7491756d27e93ca4105699558f454a7b9ba0ec6d`
- Resource receipt SHA-256: `48e6afcabe123b67d82ef34276f06a38cb157f02e74c21f21e6ca13ad8f8b2b4`
- Compiler-log SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

The positive static source review does not convert either failed run into successful kernel acceptance. No new mathematical counterexample follows from these resource failures.

No successful original module build is available for a comparison of kernel declarations. A failed compilation may still elaborate earlier declarations; this review does not assert that none did. The comparison is of the original intended mathematical reading under its explicitly declared standing data.
