# Continue Special Functions formalization

Current checkpoint: **SF-LEAN-B07**, based on repository commit
`ac74a88377d7c5a4daa8bc463d3f45629277e192`. Start with
`formalization/Block07/REPORT.md`, its claim map, declaration map,
self-review, I/O manifest and source-bound execution receipt.

`lean/CoupledCharacteristic.lean` adds 23 declarations proving the unique
positive real root rho of (1-q^rho)(1-b^rho)=(ar)^rho for 0<q,r,a,b<1.
For P(t)=[[q^t,r^t],[a^t,b^t]], the stated positive right and left vectors
are checked, the right vector is max-normalized, and the exact complex
spectrum at rho is {1,q^rho+b^rho-1}. The second eigenvalue has absolute
value below one. Actual complex matrix spectral radius one is equivalent
to the balance equation at positive t, hence has the same unique exponent.
The source scope is 179 names, including supporting lemmas and all preceding
156 declarations. The analytic F.2 growth estimates remain open.

Next executable target: the positive-real comparisons in
`monograph/sections_v11/coupled_growth_full.tex`. First identify canonical
values on the nonnegative real axis with their convergent nonnegative real
series; complex values themselves do not have an ordered-field inequality.
Prove U(R),V(R)>=R in that real interpretation, then the eventual lower
recurrence along q(R-1),r(R-1) and the corresponding second-row radii.
Keep the R>=B threshold from the manuscript explicit. Later establish the
explicit lower and upper type bounds, the radial exponent limit and type-
vector proportions. The characteristic result alone is not a growth theorem.
Operator decoupling and wider manuscript coverage remain separate.

Replay with `tools/verify_coupled_characteristic.py`, Lean 4.34.0-rc2,
Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and a fresh external
directory. The pinned native Windows toolchain and required caches are present.
The replay checks seven coupled modules and 36 steps, freshly axiom-auditing
140 declarations and inheriting the finite core's 39-name evidence. Imported
Mathlib is cached rather than freshly replayed; review is self-review.

`formalization/Block07/IO_MANIFEST.json` inventories input and output hashes,
including generated object hashes and their unbundled status. Source, audits,
controls, verifier, correspondence maps, current status, catalogue and this
continuation file are updated together. The immutable source manifest excludes
live continuation/release/catalogue guidance.

The explicit balance/2x2-spectrum route succeeded. General positive-matrix
comparison is deferred for larger matrices; logarithmic reparametrization is
deferred for exponent enclosures. The Block06 report retains rescaling and
earlier deferred alternatives. There are no delegated or delayed runs.
Preserve all seven blocks and dated guides, manuscript sources and reading
PDFs. New proofs belong in a new block. The root package manifest remains
an earlier release snapshot, not a current archive validation.
