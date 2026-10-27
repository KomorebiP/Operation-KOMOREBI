# Attempt 04 — observed resource-limited full-replay failure

Observed: 2026-10-18T19:34:58.552222+00:00

This append-only execution update supplements the preserved attempt04 source review.

## Exact evidence

- Terminal source SHA-256: `fe1c43800e7d9d4be586b1cf37f04fb18dfa7fe02547610698fcc15072d4937f`
- Full-replay receipt SHA-256: `2cd5308e9a4f91e7a27d02786b6992e46e25b67ade7943bf105fb20a8fb75075`
- OOM/retry receipt SHA-256 at review: `ad0bc23c7a5f5fb16b204260c93699c4be63e44f2e0378058aaf93b969285afa`
- Compiler-log SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Full replay: **PARTIAL_OR_FAIL**.
- Terminal: **FAIL**, exit code **−9**, after **228.148 seconds**.
- Terminal log: **0 bytes**; no terminal output artifact was retained as successful.

The runtime receipt records an 8 GiB cgroup limit and an increase of both the OOM and OOM-kill counters from zero to one around the terminated process. The empty compiler log contains no Lean rejection diagnostic. This execution remains failed; a resource diagnosis does not count as proof acceptance. The exact locator for one cited pre-event observation was referred back to runtime for correction or preservation, as detailed in the JSON.

All source fingerprints were unchanged during this run. The 423 selected modules and separate interface remain successful authenticated inputs; the actual-monomial terminal has not yet passed. The source hash remains the reviewed candidate04, and the proposed retry changes execution scheduling to `Elab.async=false` without changing that source.

## Source-review effect and comparison limit

The prior positive review concerns the intended mathematical conclusions and original standing hypotheses. A failed resource-limited execution does not change that static review, and neither establishes whole-module acceptance nor an axiom-audit result.

**No successful original module build is available for a comparison of kernel declarations.** Failed compilation may still elaborate earlier declarations. This precise limitation supersedes any broader reading of wording in the preserved intermediate reviews; those records remain intact. No checked original-versus-repaired module equivalence is asserted.
