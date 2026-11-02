# Continue Special Functions formalization

Current checkpoint: **SF-LEAN-B08**, based on repository commit
`13e65505a1ce2de3ece418b22b93b38811573207`. Start with
`formalization/Block08/REPORT.md`, its claim map, declaration map,
self-review, I/O inventory and source-bound execution receipt.

`lean/CoupledPositiveReal.lean` adds 22 declarations identifying the complex
canonical functions with their convergent real series on the real axis.
For R>=0, UReal(R),VReal(R)>=R; both are strictly increasing there. Their
real derivative equations hold globally. The maximum complex norm on each
nonnegative radius is attained at the corresponding real point and equals
its real value. Both unit-shift product lower recurrences hold at R>=1,
and their logarithmic forms at R>1. All child radii are >=2 at R>=B=1+2/m,
where m=min(q,r,a,b)>0. These radius conditions are distinct.

The registered scope is 201 names, including supporting lemmas and the
preceding 179 declarations. F.2's explicit lower and upper type bounds,
radial exponent limit and type-vector proportions remain open.

Next executable target in `monograph/sections_v11/coupled_growth_full.tex`:
prove log(F_i(R)) >= c_minus*w_i*(R+C)^rho for every R>=2, where
Q=maxScale, C=Q/(1-Q), B=lowerThreshold,
c_minus=log(2)/(B+C)^rho, rho is the positive characteristic exponent, and
w is the max-normalized characteristic right vector from Block07.
First prove the seed interval [2,B] using the linear lower bound and w_i<=1.
Then prove p(R-1)+C>=p(R+C) for each scale p<=Q. Finally use
d=(1-Q)*B+Q>0: for R>=B every child is >=2 and <=R-d. Simultaneous induction
over closed intervals [2,B+n*d], with an Archimedean covering argument,
should propagate both rows. Keep real powers, positivity and endpoints
explicit. No explicit power/type comparison is yet formalized.

Later establish upper type bounds, the radial exponent limit and type-vector
proportions. Operator decoupling and broader coverage remain separate.
Use the real-valued restrictions and the proved complex embeddings;
do not introduce an ordered-field inequality on complex values.

Replay with `tools/verify_coupled_positive_real.py`, Lean 4.34.0-rc2,
Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and a fresh external
directory. The pinned native Windows toolchain and imports are cached.
The replay checks eight coupled modules and 39 steps, freshly axiom-auditing
162 declarations and inheriting the finite core's 39-name evidence. Imported
Mathlib is cached rather than freshly replayed; review is self-review.

`formalization/Block08/IO_MANIFEST.json` inventories input/output hashes and
unbundled generated object hashes. Source, audits, controls, verifier,
correspondence maps, current status, catalogue and this continuation file
are updated together. Immutable source manifests exclude live guidance.

The real-restriction/mean-value route succeeded. The FTC route is deferred
for future integral estimates; the direct coefficient/binomial route is
deferred for stronger unit-shift coefficient bounds. The Block07 report
retains the characteristic result and older alternatives. No delegated or
delayed runs remain. Preserve all eight blocks and dated guides, manuscript
sources and reading PDFs. New proofs belong in a new block. The root package
manifest remains an earlier release snapshot, not a current archive validation.
