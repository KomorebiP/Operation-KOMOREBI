# Self-review

This is self-review plus Lean checking, not an independent referee audit.

- Original obstruction: the bridge uses the exact parent frobeniusMatchingClass and localConjugacyObstruction. No slack variables are used.
- Quantifiers: one x is shared across the family; z_i varies only with the local index, not with a group element.
- Sign: localization is S_d x+(1-T^d)z; the filtration proof replaces z by -z, an explicitly reversible change.
- Scope: prime-power theorem requires characteristic p, but not nilpotence, semisimplicity, finite dimension or finite index set.
- Mixed degrees: m_i is nonzero in k, and T-lambda is nilpotent. For lambda=1 the entire invertible operator S_m(T)^(p^a) is removed; its constant term is not silently substituted.
- Edge cases: degree 1 has exponent 0, and the corresponding norm is identity; the generic power-family theorem handles r=0. Empty families are proved vacuous. Least natural exponents exist for nonempty families. No degree-zero p-valuation is used.
- Negative control: e1=0,e3=E12 for actual unipotent dual-number matrices gives individual roots but a nonzero matching class.
- Positive control: e1=E21,e3=E12 gives a zero class and an actual common lift.
- Finite corroboration: 598 exact linear-image/kernel comparisons plus independent dual-number matrix power/conjugation enumeration.
- No claim of higher-tower compatibility, mixed-characteristic automatic coordinates, local-field dictionary, global Selmer vanishing, automorphic occurrence or Strong Artin.
