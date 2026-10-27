# Formalization scope: 20 freshly compiled theorem constants

H12PrincipalDivisor contains 14 theorems and H12DivisorCarries contains six.
They use the actual integer principal matrix on (tau,s,1/5), Euclidean division,
finite sign functions and fifth-smoothing weights. The unique lift, possible
orders, ray coefficients and translation carries are universal integer results.
They are not inferred from finite test ranges.

The analytic interpretation of those integers as orders of elliptic gamma is
an ordinary proof in PROOF.md. No analytic gamma definition, meromorphic order,
complex conjugation, field intersection or principal-norm comparison is
postulated in Lean. The three-theta zero anchor is not a compiled analytic
Lean theorem. No gamma/arithmetic equality is asserted.

All 20 declarations are compiled from clean sources with pinned Lean
4.34.0-rc2 and bundled Std, one worker, warnings as errors. Their full transitive
axiom lists are audited. Only propext, Classical.choice and Quot.sound occur
where required. No admitted proofs, custom axioms, native_decide or unsafe
declarations are allowed. The false integer equality must be rejected.

The v0.12 predecessor is preserved byte-for-byte, including its nested source
history and original evidence. It is NOT freshly rebuilt. No combined count
is presented as a fresh whole-program verification.
