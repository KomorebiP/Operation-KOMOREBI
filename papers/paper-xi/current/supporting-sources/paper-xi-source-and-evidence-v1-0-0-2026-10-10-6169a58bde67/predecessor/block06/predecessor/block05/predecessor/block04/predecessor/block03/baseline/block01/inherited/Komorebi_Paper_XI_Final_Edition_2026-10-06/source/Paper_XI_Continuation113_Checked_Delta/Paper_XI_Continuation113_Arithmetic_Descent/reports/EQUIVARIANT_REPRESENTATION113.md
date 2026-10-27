# Actual equivariant representation transport in Continuation113

## The completed interface

`EquivariantRepresentation113.exists_equivariant_actual_action` combines the
scalar correction with the literal group adapter and Continuation112's actual
representation construction. Its conclusion concerns the original group G,
original theta, original packet carrier V and original packet operator U.

Its inputs are:

- Actual groups G and P, normal subgroups D and H, and their original invariant
  characters theta and chi.
- Exact quotient homomorphisms q:G->A and r:P->A with kernels D and H, together
  with normalized sections.
- An irreducible packet representation rho on V, acting on H by precisely chi.
- Actual automorphisms alpha of G and gamma of P preserving the original
  characters, covering the same quotient automorphism beta, and satisfying
  alpha^n=gamma^n=1.
- Exponent dividing m on A, with gcd(n,m)=1.
- Equality of the labelled scalar commutators of the two actual sections.
- A supplied invertible linear operator U on V that intertwines rho with gamma.

It concludes that there exists an honest representation Xi of G on that same V,
with all of the following properties:

    Xi is irreducible,
    Xi contains the original theta on D,
    Xi(d) = theta(d) Id for every d in D,
    U Xi(g) v = Xi(alpha(g)) U v for every g in G and v in V.

There is no supplied comparison cochain, corrected covariance equation, complex
pushout action, action-defect character or norm-one condition in this endpoint.
Each is constructed or derived from the listed actual data. The quotient order
beta^n=1 is derived from alpha^n=1 using the actual quotient section.

## Why the original packet operator works

Write lambda_G and lambda_P for the original-character section scalars. The
actual source-group adapter proves

    lambda_G(alpha(g)) = lambda_G(g) f_G(q(g)),
    f_G(a) = lambda_G(alpha(t(a))),
    f_P(a) = lambda_P(gamma(u(a))).

The corrected cochain from CyclicDefect113 satisfies

    f_G(a) s'(beta(a)) = s'(a) f_P(a).

Continuation112's representation, with this constructed cochain, is

    Xi(g) = lambda_G(g) s'(q(g)) rho(u(q(g))).

The original packet covariance implies

    U rho(u(a)) = f_P(a) rho(u(beta(a))) U.

Substituting these equalities proves the displayed covariance for Xi directly.
No change to U, theta or chi is made. Irreducibility and literal theta restriction
are inherited through the already checked scalarTransport arguments, now
instantiated with the constructed equivariant cochain.

## Scope retained

This theorem solves a finite-action comparison interface on already supplied
actual group, quotient and character data. It supplies no arithmetic theta,
maximal simple stratum, canonical quotient instance, or attachment of the whole
packet to one maximal simple type. It does not assert that a supplied kappa has
any specified determinant. It does not change the original H5 family or prove H5.

The theorem retains U itself. If the supplied U satisfies U^n=1 or a determinant
normalization, those same facts continue to hold. They are not inferred from
covariance alone. The separate cyclic normalization module addresses construction
and uniqueness of a normalized operator under its exact hypotheses.

The scalar comparisons continue to use complex pushouts internally. The theorem
does not identify raw finite central groups or reconstruct their original dyadic
power data. Original Claim16.2 is not promoted.

## Checked evidence

Final source SHA256:

    f1cf8ff3343f2647c0994270f6de5bc3478925a25406ea3a221861807b08b6c9

The module imports the frozen adapter source:

    ActualScalarLift113:
    9dca2abac60d683f19c4b2bd2bd257b8f18e5b5f459cf39df9948de4ccf41ce0

and through it the frozen correction source:

    CyclicDefect113:
    b6fe373c44ebd8725be1683e7f851da03bcc708c896db2103e02a5a31fbb3a19

The representation module has two explicit theorem exports. It was freshly
compiled with warnings as errors. Its axiom and leanchecker receipt is
`evidence/equivariant_representation/EQUIVARIANT_REPRESENTATION_AUDIT113.json`.
Inherited objects were reused and left unchanged.

Three development attempts are preserved. Attempt01 failed because Lean omitted
section hypotheses absent from the interim theorem's displayed type; explicit
`include` restored the actual action and character hypotheses used in its proof.
Attempt02 then failed the unused-section-variable linter for H.Normal on that
interim covariance theorem; its proof does not need normality. An explicit `omit`
removed that unused instance. Attempt03 compiled both the interim covariance
lemma and final existence endpoint. No mathematical hypothesis was silently
removed from the final actual-source construction.

The first export-audit invocation exposed a separate runner defect: its regular
expression parsed a doc-comment line beginning with the words "theorem below"
as a declaration named `below`. The attempted audit and error log are retained
with the `failed_parser01` suffix. The parser was corrected to remove block
comments before extracting declaration names. The mathematical source did not
change, and the corrected audit covers the two actual theorem exports.
