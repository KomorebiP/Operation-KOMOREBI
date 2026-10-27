# Contract review — v0.10.0

1. `normalEquiv` is constructed from the actual coercive bilinear form by Mathlib
   Lax–Milgram. `normalEquiv_apply` identifies the map with A* A + lambda I.
   No inverse, minimizer or closed range of A is assumed in the core.
2. `objective` is the literal squared residual plus lambda times squared source norm.
   The exact quadratic increment proves uniqueness globally, not just stationarity.
3. The noise bound 1/(2 sqrt lambda) is proved with the actual Hilbert norm and attained
   by the scalar example. No sample-to-operator inference is made.
4. Bias and noise may cancel. The exact squared formula retains their cross term
   implicitly inside a single norm; only source-kernel energy splits orthogonally.
5. `CoerciveOffKernel A alpha` is the existing contract; alpha conditions the source
   map A, never the compatibility operator delta.
6. `source_condition_noise_bound` requires source=A* A w. It does not claim all
   identifiable sources have such a representative with controlled norm.
7. Fixed-lambda changing-operator bounds allow rank changes and depend on operator
   norms and lambda. They do not bound the lambda=0 pseudoinverse across rank changes.
8. The globalization integration uses the OLD quotient type/norm and pseudoinverse.
   Its CompleteSpace A.range hypothesis remains explicit. The core needs no such premise.
9. `regularized_equals_pseudoinverse_iff` clarifies that positive regularization usually
   introduces bias. This is not mislabeled as exact best-image recovery.
10. Scalar examples use the actual constructed maps and real variables, not finite
    numeric evidence. Lambda=0 is separately a nonuniqueness boundary.
11. All current proofs concern bounded real Hilbert maps. No constrained/nonlinear
    inverse, unknown-operator learning, or general strong-limit theorem is supplied.
12. Tikhonov and Lax–Milgram are classical. The contribution here is checked integration,
    not priority/novelty certification. The named census includes supporting lemmas.
