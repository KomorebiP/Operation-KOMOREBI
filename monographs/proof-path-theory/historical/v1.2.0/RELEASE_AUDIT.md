# Proof Path Theory 1.2.0 release audit

**Parent:** the complete 1.1.0 archive. **Author:** Komorebi P.

## What changed

The finite proof-field model now induces local Horn-model fibers with actual
contravariant restrictions. Its complete patch diagram is explicitly equivalent
to coherent global sections. A separate theorem glues proper-patch data when
whole certified rule supports are covered. A three-node counterexample proves
that pairwise dependency coverage can lose a conjunction constraint.

Protected linear realization now has a compiled general functional alternative,
a matrix row-witness alternative, affine-fiber equivalences, finite-field counts
and exact observation-count identities. Concrete binary certificates are emitted
by the Python solver and checked as Lean propositions.

The sufficiency claim for all queries was corrected to injectivity, allowing
lossless recoding. Audit and discovery equivalence were made incomparable unless
the declared tasks are nested. Certification booleans are no longer coerced from
strings. Exact binary inputs are validated before arithmetic. Empty diagrams,
empty fibers and immutable copies of restriction data are handled explicitly.

## Verification evidence

`data/release_verification.json` records the full run: Python syntax and tests,
18 inherited minimum-certificate comparisons, 100 greedy-bound instances, 1,024
retention identities, 114 covariance comparisons, 5,039 exhaustive binary
realization systems, the generated Lean examples, native export, CLI behavior,
package build and isolated wheel import, and a three-pass warning-free paper
build. The numeric totals are distinct categories, not one interchangeable test
count.

`evidence/lean/verification.json` records eight fresh builds, eight own-kernel
module replays, an axiom audit of 78 named declarations, and five negative-control
outcomes. Of these, four are Lean rejections. The explicitly introduced false
axiom is detected by the separate policy, not rejected by Lean's inference rules.

The named theorem total is 42, including ten generated binary example theorems.
Their ledger is not equated to the manuscript's 33 result groups. The inherited
23 groups are retained, with formal coverage only where the concordance specifies
it. Source hashes and command logs attach evidence to the actual delivered code.

## Limitations

The project does not claim a Lean proof of arbitrary Python execution, a general
verified Lean metadata parser, automatic recovery of failed discovery history,
semantic completeness of arbitrary mathematical encodings, empirical validation
of social interpretation models, a fresh build of all Mathlib, independent peer
review, or historical priority.

No license was selected without the author's instruction. `LICENSE_NOTICE.md`
is retained. Source visibility alone is not an unrestricted redistribution grant.

## Failures encountered

The internet runtime download failed. An offline Library archive was recovered,
its full assembled hash matched, and extraction completed. Early Lean proof
engineering errors were repaired. A full wrapper invocation exceeded the outer
execution window and was not counted as PASS. Two further wrapper attempts
failed closed on diagnostic formatting, first backticks and then abbreviated
axiom names. Their logs are retained in `evidence/development`. The final run
rebuilds and rechecks rather than treating those interrupted attempts as success.
