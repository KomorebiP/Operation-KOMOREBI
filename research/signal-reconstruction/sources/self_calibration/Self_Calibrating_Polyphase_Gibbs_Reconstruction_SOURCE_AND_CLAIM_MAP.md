# Source and Claim Map

## Proved in the paper

1. Exact offset progression
   
   `b_(ell,r+1) = z_ell b_(ell,r)`.

2. Multi-offset phase identity and perturbation bound.

3. Hankel-gap model-order criterion under an operator-norm perturbation bound.

4. Branch-margin theorem for selecting the unique physical root of an aliased node.

5. One-order root perturbation gain.

6. Oracle-equivalence corollary. Under the margin condition, the self-calibrated branch equals the branch chosen by a true-neighborhood oracle.

7. Rate-preserving lift from aliased-node error `O(N^(-p-1))` to physical-node error `O(N^(-p-2))`.

8. Exact self-calibration in the bandlimited control class.

9. Perturbed self-calibration under a Fourier-tail bound and uniform local inverse hypotheses.

10. Explicit finite innovation budget of `3*Lmax + 1` high-frequency coefficients in the exact bandlimited control class.

11. Resolved synthesis inequality

   `||f - fhat_M|| <= ||s - A_M s|| + (1 + ||A_M||) ||j - jhat||`.

12. Confluent offset ratio for higher jump jets.

## Established inputs used

- Prony and annihilating-filter recovery of exponential sums
- finite-rate-of-innovation sampling
- algebraic Fourier reconstruction of piecewise-smooth functions
- decimated Fourier equations and their asymptotic benefit
- shifted or coprime sample channels for de-aliasing exponential nodes
- classical Gibbs reconstruction methods
- the Fourier stability barrier for unrestricted stable recovery

## Numerical certificates

- exact four-edge control recovery
- non-bandlimited analytic-background recovery
- four power-tail rate families
- five noise scales
- multi-offset averaging
- near-collision negative control
- principal-root negative control
- exact symbolic confluent example
- oracle comparison over 28 tail/decimation combinations
- 100 separated random unknown-order cases
- end-to-end raw, Fejer, and resolved reconstruction comparison
- exact nineteen-coefficient unknown-order control recovery

These are finite experiments. They are not substituted for the theorem hypotheses.

## Not claimed

- universal recovery without a model class
- stability without separation
- arbitrary two-dimensional curves
- unbounded edge count
- arbitrary blind measurements
- a global minimax risk theorem
- a violation of known Fourier stability barriers
- confirmed priority for the complete theorem package

## Literature-position statement

The branch-recovery identity is not presented as the first use of shifted samples in exponential analysis. The paper's narrower candidate contribution is the proof that offset phases derived from the same Fourier data can replace externally supplied jump neighborhoods in a decimated piecewise-smooth reconstruction, equal the oracle branch under a margin, preserve the one-order gain, support unknown-order detection, and feed a native edge synthesis theorem.
