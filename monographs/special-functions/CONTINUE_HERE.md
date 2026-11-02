# Continue Special Functions formalization

Current checkpoint: **SF-LEAN-B06**, based on repository commit
`433fecf0b21011af7774fa41fde336e788949411`. Start with
`formalization/Block06/REPORT.md`, its claim map, declaration map,
self-review, input/output inventory and source-bound execution receipt.

`lean/CoupledRescaling.lean` adds 19 declarations proving Theorem G.1's
full component-rescaling equivalence and scalar representation. For real
scales in (0,1), nonzero complex A,B with V(z)=A U(Bz) exist exactly when
D=0, equivalently q=b or qb=ar. The representation uses positive real
S=sqrt(k/p), c=sqrt(S) and effective scalar scales (q,Sr) in (0,1).
The registered source scope is 156 names, including supporting lemmas and
all previous 137 declarations. The whole analytic monograph remains open.

The boundary example now has equality of both full labeled entire functions
at distinct ordered tuples. It strengthens the earlier finite-jet collision
and shows that the germ inverse's defect guard cannot be omitted. Preserve
earlier records with their dated, weaker scope rather than rewriting them.

Next executable target: the characteristic-exponent section of
`monograph/sections_v11/coupled_growth_full.tex`. For real t>0 define
P(t)=[[q^t,r^t],[a^t,b^t]]. Prove existence and uniqueness of rho>0 with
(1-q^rho)(1-b^rho)=(ar)^rho. Then check the positive eigenvector
(r^rho,1-q^rho), its max-normalization, and spectral radius one. Keep real
powers and row/column conventions explicit. These statements remain
unformalized; separate them from the later analytic order/type bounds.
Existing convergence and rescaling do not prove the growth law. Operator
decoupling is a separate remaining obligation.

Replay with `tools/verify_coupled_rescaling.py`, Lean 4.34.0-rc2,
Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and a fresh external
work directory. The pinned native Windows toolchain and caches are present.
The replay covers all six coupled modules and 33 steps. Imported Mathlib
cache and the 39-name finite core's earlier evidence are reused; review is
self-review.

File I/O is recorded explicitly in `formalization/Block06/IO_MANIFEST.json`:
actual input hashes, output log/receipt hashes and generated object hashes.
The source, audits, controls, verifier, claim maps, status, catalogue and this
continuation file are updated together. The immutable source manifest excludes
this live file and the current catalogue.

The scalar construction route succeeded; direct scaled-recurrence induction
and separate surface-symmetry constructions remain deferred alternatives.
The Block05 and Block04 reports retain the earlier derivative/tail and local
norm-contraction alternatives for future quantitative estimates.
There are no delegated or delayed runs to reconcile. Preserve all six blocks,
dated guides, manuscript sources and reading PDFs; put new proofs in a new
block. The root package manifest remains an earlier release snapshot.
