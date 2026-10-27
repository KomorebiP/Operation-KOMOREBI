# Controls for the centered Dirac release

These are proposed controls. They have not been compiled or counted as passed.
Prefer actual instantiated counterexamples and interface tests over a bare
unprovable assertion. Expected compilation failures must be classified by
their intended diagnostic, never merely by a nonzero process exit.

## Positive interface cases

1. `m=0`, zero Fourier mode, arbitrary time: both generators vanish and the
   propagators agree exactly. Both nonreal resolvents must be actual inverses.
2. Negative mass and negative nonzero spacing: the bounded operator and all
   quantitative interfaces must still apply.
3. Negative time: the propagator bound must use `|t|` and remain nonnegative.
4. `z=i` and `z=-i`: both half planes must satisfy inverse identities and the
   same reciprocal imaginary-part bound.
5. `T=0`: the compact-time error is exactly zero.
6. A one-axis single mode: the exact difference norm reduces to the scalar
   sine-quotient residual and matches the third-moment normalization.
7. A generic nonzero three-axis mode with mass: derivative/product arguments
   must not require cross-commutation of the distinct generators.

## Expected rejection controls

1. **Missing spacing hypothesis.** Attempt to use the bounded centered
   operator with `h=0` and its actual continuum modal action. It must not be
   accepted as a bounded all-input continuum operator.
2. **Missing graph-domain witness.** Apply `H` to arbitrary `CoeffL2` through
   an interface advertised as domain-free. The intended rejection is a
   missing domain premise or type mismatch, not an unavailable import.
3. **Missing nonreal hypothesis.** Try the inverse identity at `m=0,n=0,z=0`.
   An actual zero operator cannot have a left inverse.
4. **Wrong resolvent sign.** Replace `H-z` by `H+z` while keeping the same
   resolvent. At `m=0,n=0,z=i`, the false composition is `-I`, not `I`.
5. **Missing third moment.** Attempt the global `h² M3/6` rate without a
   summability witness. The release must not treat a totalized `tsum` as
   finite-moment evidence.
6. **Signed time in the bound.** Replace `|t|` by `t` for unrestricted real
   time. Negative time and a nonzero moment make the proposed right side
   negative, contradicting norm nonnegativity.
7. **False cross-commutation.** Assert that all continuum and centered modal
   Dirac operators commute. With nonzero mass and a nonzero one-axis mode,
   `[mβ+qα,mβ+kα]=m(k-q)[β,α]`, generally nonzero.
8. **Placeholder/custom axiom policies.** Isolate an admitted proof and a
   custom axiom in separate tests; reject the former in strict compilation
   and the latter in recursive axiom-policy analysis. Neither belongs in
   active imports.

## Analytic boundary controls

The high-mode resonance in `INDEPENDENT_MATHEMATICAL_AUDIT.md` refutes a
uniform operator-norm resolvent claim. Preserve it in the release scope even
if a dedicated formal counterexample is not added in this block.

The scalar constant `1/6` comes from the cubic sine remainder. Replacing it
by a uniformly smaller constant fails in the small-argument limit. A finite
numerical check alone cannot certify optimality of that constant.

The physical Fourier comparison must use the existing unitary equivalence;
replacing it by an arbitrary map or a changing finite grid is outside the
accepted type and theorem contract.
