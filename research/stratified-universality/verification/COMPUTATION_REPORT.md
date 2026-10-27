# Stratified Universality computation replay

Date: 2026-10-06. Frozen scientific input: the supplied v2.0.0 source package.

## Result

All three documented finite verifiers completed successfully in an isolated full
copy of the upstream source tree. The fresh scientific result JSON files are
byte-identical to the inherited reports. Every v2 run manifest passed the
computation-audit validator with `--root`, including input-freshness and output
hash checks.

| Suite | Assertions | Failures | Elapsed seconds |
|---|---:|---:|---:|
| Block 15 lane transport | 197,099 | 0 | 34.513203 |
| Block 16 holonomy and orbit transport | 1,344,823 | 0 | 8.624891 |
| Block 17 semantic extension | 3,022 | 0 | 19.599771 |
| Total | 1,544,944 | 0 | Separate concurrent executions |

These numbers count implementation assertions, including scalar entries,
repeated reconstruction anchors, and source-literal checks. They are neither
independent theorem counts nor a completion percentage.

## Exact scope and implementation review

Block 15 uses integer and `Fraction` arithmetic. Its 250 dimension-5
unimodular trials construct split projector systems from conjugated coordinate
partitions and check selected scalar entries of projector, reconstruction,
composition, and refinement identities. Its 150 dimension-6 rational Cauchy
trials use fine/middle/coarse lane counts 6/4/2. Both families shuffle a full
probe pool and check fixed scalar quotas, rather than checking every pool
entry. The 500 fold trials use 3 through 11 edges and 2 through 5 target labels.
The 150 support-loss trials use 4 through 18 edges and 2 through 7 target
labels. Factorial identities exhaust `1 <= N <= 30`, `0 <= n <= 80`, and all
positive representatives `1 <= r <= N`; some global reconstruction checks are
repeated under distinct residue anchors. Five negative controls reject overlap,
incompleteness, a false refinement sum, repeated edge tags, and a shifted
factorial target. The tagged-selection checks concern the expressly constructed
finite coordinate model.

Block 16 uses exact integer arithmetic with cyclotomic denominators cleared.
It constructs the 14 groups C2 through C8, D3, D4, D5, V4, S3, A4, and S4 and
the finite permutation actions explicitly encoded in the script. The group
actions are checked against their multiplication tables. Point and pair orbit
partitions, indicator bases, products of orbital basis matrices, constant
structure coefficients, and products of random invariant matrices are checked.
Compatible selectors use unions of pair orbits. Negative controls select a
single endpoint in a nontrivial orbit of a unit-coefficient permutation matrix
and check that the result is not invariant. Refinements use trivial fibers of
size 2 and 3. The rational cyclic projector check exhausts moduli 1 through 48
and 54, 60, 64, 72, 84, 90, 96. Source checks test thirteen required strings.

The Block 16 endpoint controls do **not** prove that a non-orbit selector must
fail on arbitrary lane objects with arbitrary Hom spaces. In particular, they
do not certify the overly strong general O4 nonzero-selector wording flagged
by the mathematical reviewer. The original finite unit-coefficient benchmark
and the general categorical inference must remain distinct.

Block 17 uses SymPy exact integer, rational, and polynomial algebra. It tests
1,000 seeded random pairs of matrices with 1 through 10 common source columns,
1 through 10 rows each, and entries in -3 through 3. Three assertions per pair
compare quotient/intersection dimension formulas and compare kernel inclusion
with a stacked-row-rank factorization criterion. The dimension checks do not
construct or verify the maps in a semantic exact sequence. It also checks one
symbolic quadratic identity, eight symbolic Hankel determinant identities
(`N=1..8`), and thirteen theorem-label/source-literal checks. The original
Block 17 script has no separate negative-control mutation suite. Its quadratic
identity does not on its own verify the analytic convexity hypotheses of the
written theorem.

The smallest group-algebra modulus, empty-product index, and Hankel dimension
are included in the stated ranges. Matrix composition, simultaneous pair
actions, projector normalization, and positive residue representatives were
read from the actual code rather than inferred from PASS totals. Exact
arithmetic removes floating-tolerance uncertainty. Fixed seeds make random
sampling reproducible but do not make it exhaustive. No silent truncation or
resource-limited partial range occurred.

## Provenance and environment

The replay tree is `work/stratified/replay`; upstream and the traditional-paper
working tree were not modified. The bounded runner launched a thin wrapper,
which runs the documented unchanged verifier in its manuscript directory,
removes stale replay outputs, and copies the freshly generated result and TeX
table into the evidence directory. The manifest records actual argv, input
hashes before and after, declared-result hashes, UTC start, elapsed time,
software versions, logs, exit status, and limits.

Python was 3.12.14 on Linux x86_64. Both the primary and system interpreters
initially lacked SymPy; the import failed with `ModuleNotFoundError`. Cached
wheels then supplied SymPy 1.14.0 and mpmath 1.3.0 into a private task dependency
directory, without changing global packages. Their successful imports and
versions were checked after installation. The installation report is retained.
Blocks 15 and 16 have only standard-library arithmetic dependencies. No source
archive Git commit was available; pinned SHA-256 input hashes identify the
executed revision instead. The run was capped at 600 wall seconds, 550 CPU
seconds per process, 2 GiB address space, one inherited CPU core, one cooperative
numerical-library thread, and 1 MiB combined log output per suite. All runs
finished within those limits.

The three suite commands were:

```text
python verify_block15_lane_transport.py
python verify_block16_holonomy_lane_transport.py
python verify_block17_semantic_extension.py
```

Each was executed from the isolated replay `manuscript` directory. The wrapper
and exact bounded-run argv are archived with the v2 manifests. Interpreter
dependency discovery and installation did not count as mathematical tests.

## Interpretation and residual risks

Classification: **the stated finite outputs were freshly reproduced; the code
contracts and selected invariants were reviewed, but the complete implementation
was not independently reimplemented.** The controlling proofs remain the
written proofs. PASS does not establish arbitrary additive-category transport,
universal semantic descent, infinite convergence, nonsplit or noninvertible
descent, higher-stack effectivity, historical novelty, external peer review, or
full Lean correspondence.

The structural identities implicated by the tests are finite projector
orthogonality/completeness, insertion of a complete intermediate splitting in
composition, orbit constancy of permutation intertwiners, and exact dimension
identities for kernel sums and intersections. The written symbolic proofs must
justify their uniform versions. Increasing assertion counts alone would not
resolve the general O4 inference or other categorical hypotheses.

The official v2 manifests use the actual workspace-relative paths from the
executions. `execution_inputs` preserves the corresponding files for portable
archive checking, and `validate_archived_hashes.py` verifies that mapping without
changing the manifests. That archive-integrity checker is separate from the
official full-schema manifest validation already performed. The pinned source
contracts are the frozen upstream sources, not a claim that every later prose
correction was part of these runs.

## Evidence location

`output/Komorebi_Stratified_Universality_Final_Edition_2026-10-06/verification`
contains separate inherited reports, the fresh evidence for each suite,
contracts, pinned execution inputs, environment and dependency records, logs,
the result summary, this report, and an archive hash checker.
