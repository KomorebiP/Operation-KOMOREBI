# Block 04 semantic review

## Authoritative target

Publication record PSC-I-T-SINGLE-OPERATOR, current traditional 02_foundations.tex lines 891–905, is unchanged. Its proof text is unchanged too. The new Lean proof follows a different valid route through stabilized scalar images rather than requiring the separately unfinished module-top/Nakayama development. This does not mark the latter development complete.

## Objects and hypotheses

- The acting module is Module.AEval' T with literal polynomial evaluation. Membership and scalar-image transport are proved explicitly.
- X_p is an actual Submodule with power-annihilation membership, proved equal to Mathlib's ideal primary component.
- The quotient is the literal quotient by p times top in the primary subtype.
- Its action is the canonical R/(p) action. Equivalences are linear over R/(p), not merely over k.
- Kernel exactness is proved without Artinian hypotheses. Surjectivity of the primary-to-global map requires Artinian M. Finite-dimensionality supplies that hypothesis for operators.
- Irreducibility is used to make the residue ring a field and to obtain coprimality of distinct primary labels. The intrinsicMultiplicity definition accepts other polynomials syntactically, but its primary dimension/count theorems retain irreducibility.
- Positive exponents prevent counting zero factors. Associate labels are grouped by their principal ideals.
- The maximum in the public theorem is defined over all monic irreducibles and proved bounded and attained. The zero space is included.
- PrimaryPresentation still contains an actual equivalence and irreducible-power data, not a desired dimension or seed-count conclusion. Its existence was proved in Block 03 and is reused.

## Complete target correspondence

The maximum formula is operator_seedRank_eq_intrinsicSeedMaximum. The individual quotient identification is operatorPrimaryQuotientEquiv and intrinsicMultiplicity_eq_fiber. The actual elementary-divisor decomposition of X_p is operatorPrimaryComponentEquiv. The "moreover" count for any positive decomposition of X_p is intrinsicMultiplicity_eq_card_of_component_decomposition. Together these map the full printed single-operator theorem. The separate six-way cyclic criterion is not upgraded.

## Trust boundary

A successful compiler checks these Lean statements, not this prose-to-Lean interpretation. Source ownership includes generated and private declarations. Kernel replay is the same official Lean kernel. The authenticated pinned Mathlib cache is reused, not rebuilt. Final acceptance requires the fresh baseline and extension reports both to pass.
