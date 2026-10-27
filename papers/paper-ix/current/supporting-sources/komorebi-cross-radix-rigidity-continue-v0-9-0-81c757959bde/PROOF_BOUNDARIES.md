# Proof Boundaries — v0.9.0

## Certified internally in Lean

- Exact DFT transition for positive affine pullback, including alias sums for nonunit multipliers.
- Exact Fourier-side polynomial affine-substitution formula.
- Hasse-derivative coefficient formula for bounded affine substitution.
- Nonzero output shell/jet coordinate implies a source coordinate with divisor-upward shell movement and jet-downward movement.
- Explicit divisor-upward / jet-downward closure is section-invariant.
- Every invariant shell/jet mask is necessarily divisor-upward.
- Every invariant shell/jet mask is necessarily jet-downward over `ℂ`.
- `InvariantShellJetSet` equals the explicit closure of `ActiveShellJetSet`.
- Exact retained-coordinate finrank formula for the resulting invariant shell/jet envelope.

## Not claimed

- The explicit shell/jet mask envelope is not asserted equal to the absolute `ProfileOrbitHull` in general.
- The active set of an arbitrary submodule is not claimed to be algorithmically recoverable from finite black-box data.
- The jet-downward necessity proof is not promoted unchanged to positive characteristic; binomial coefficients can vanish there.
- No base-independent integral lattice theorem is claimed.
- No arbitrary-ring, semiring, infinite-dimensional, or unrestricted-category classification follows from this finite complex theorem.
- Bell's generalized Cobham theorem is not formalized here.
- Root-of-unity rational generating-function to eventual quasi-polynomial normalization remains external.
- Lean verification does not establish literature novelty or independent peer review.
