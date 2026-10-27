# AVOC v0.29.0 verification record

PASS in the following distinct scopes:

- 161/161 local targets rebuilt from an initially empty local build directory, using the pinned external caches.
- 1,548/1,548 exact-name theorem axiom reports. Union: propext, Classical.choice, Quot.sound.
- 49 new theorem/lemma declarations across four new AVOC modules; 140 inherited non-audit modules byte-identical to v0.28.
- 80/80 deliberate negative files substantively rejected, including five new rank/offset/cost/search-accounting counterclaims.
- Positive-source scan: zero proof placeholders, custom axioms, native_decide or unsafe declarations.
- 960 executed checker requests: 791 certified outputs, 143 invalid certificates rejected, 16 unfunded checks, 10 malformed requests rejected.
- All 625 two-by-two GF(5) linear matrices tested with specified varying biases, plus rectangular/zero-dimensional/known-rank examples and sampled pipelines. This is not all matrices of all shapes or all affine maps.
- 17,746 input-vector comparisons; 25 nonzero first-offset variants; 30 generator-credit cases; four Python input-validation rejection cases.
- Eight actual CLI example invocations, including the 13/14-call break-even pair.
- The independent semantic oracle uses homogeneous matrices and direct AST execution. Its independent small-rank oracle builds exact column-image spans, not the RREF algorithm used by the proposer.
- Baseline v0.28 archive CRC and 7,961 original payload hashes matched before this release was packaged.

The mathematical theorem is generic over fields and dimensions. Execution regression is exact GF(5). A successful output has a proof-carrying candidate; the Python Gaussian proposer itself has bounded regression evidence, not a universal correctness/complexity theorem. The codec theorem concerns parsed typed certificates, not universal Python/JSON round-trip refinement.

The runtime was recovered from seven available offline ZIP parts using the original assembler. It verified each part and the combined 66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34 archive SHA. The actual Lean version is 4.34.0-rc2 at 6a10ac8c22beadecabdbb0919c2b50214762f91d. Nine exact dependency pins were checked. This is not an independent kernel or a full-source mathlib rebuild.

Current per-source commands, hashes, import hashes and exit statuses are under results/v0.29.0. `verification_summary.json` is rebuilt by the evidence collector, which rejects stale/partial/setup-only records. Historical outputs under older versions remain historical.

No physical speedup, novel rank identity, empirical LLM benefit or durable deployment is asserted.
