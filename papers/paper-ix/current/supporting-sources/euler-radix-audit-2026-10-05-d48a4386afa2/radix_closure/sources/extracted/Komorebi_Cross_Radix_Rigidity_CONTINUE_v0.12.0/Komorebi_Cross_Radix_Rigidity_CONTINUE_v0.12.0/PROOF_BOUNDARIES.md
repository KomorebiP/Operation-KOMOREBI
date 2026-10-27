# Proof Boundaries — v0.12.0

Proved internally in Lean:
- every v0.11 denominator/lattice/Smith result;
- exact scalar-extension compatibility of subgroup and primitive-shell numerators;
- `complexCyclotomicShellNumerator = D_c • dftShellProjector`;
- integer-input identity `iota(N_c x)=D_c P_c(iota x)`;
- rational reconstruction by division by the exact nonzero denominator `D_c`;
- the good lattice `L_c` is exactly the integral-preservation locus of the primitive
  complex shell projector.

Not claimed:
- arbitrary integral packets lie in `L_c`;
- the earlier weighted p-adic cancellation hypotheses automatically imply membership in
  every shell lattice (this is the next block);
- explicit p-primary Smith coefficients or Fitting ideals are already computed;
- every shell defect vanishes for the arithmetic families studied elsewhere;
- scalar-extension identification by itself establishes literature novelty.

Bell remains external exactly as in v0.7-v0.11.
