# Continue Special Functions formalization

Current checkpoint: **SF-LEAN-B05**, based on repository commit
`ee59ff257a74fc046981e5ca633476148fe2e1a4`. Start with
`formalization/Block05/REPORT.md`, then its claim map, declaration map,
self-review and source-bound execution receipt.

`lean/CoupledGermInverse.lean` adds 13 declarations proving all-degree
coefficient extraction from equality of canonical analytic germs and the
guarded ordered-parameter inverse of Theorem G.2. It also identifies every
coefficient of arbitrary supplied Taylor-series objects for normalized
analytic solutions. The source scope contains 137 names, including supporting
lemmas and all preceding 124 declarations. Full monograph coverage is open.

For positive strict-contraction tuples, equality of both labeled germs
gives equality of the full paired coefficient sequence. Block01's finite
inverse then identifies the tuples if the first defect is nonzero. Ordinary
odd-series coefficients are used: degrees 3,5,7 correspond to indices 1,2,3;
do not insert factorial divisions. The exceptional-locus example retained
in the evidence is a finite-jet collision, not a proved full-germ collision.

Next executable step: fix an exact contract for the full analytic component-
rescaling equivalence in Theorem G.1, using
`monograph/sections_v11/coupled_inverse_full.tex`. The finite defect
factorization already identifies q=b or qb=ar. Prove both functional
directions, preserving amplitude/argument normalization and both surfaces.
Perron order/type growth is a separate larger formalization obligation.

Replay with `tools/verify_coupled_germ_inverse.py`, Lean 4.34.0-rc2,
Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and a fresh external
work directory. The pinned native Windows toolchain and caches are present;
Lean need not be on PATH. The replay checks all five coupled modules and
30 steps. Imported Mathlib cache and the finite core's earlier evidence
are reused; review is self-review.

The scalar-series route succeeded. Iterated derivatives and leading-term
tail estimates remain deferred alternatives, not refuted. The earlier local
norm-contraction uniqueness route remains deferred. There are no delegated
or delayed runs to reconcile.

Preserve all five blocks and dated guides. Put new theorems in a new block.
The root package manifest remains an earlier release snapshot. The new
immutable source manifest excludes this live continuation file and the
current catalogue. Earlier manifests retain their original snapshots.
