# Source and Claim Map

## Projector-Resolved Seed Calculus IX
### Arithmetic Packet Calculus: Euler Families, Supercongruences, and Weighted p-adic Reconstruction

**Author:** Komorebi P.

## Internal mathematical results

The paper proves the following within its stated algebraic and p-adic hypotheses:

- exact reconstruction from residue packets and exact refinement of residue addresses;
- transport of a coefficient sequence by an invertible exponential-generating-function multiplier;
- filtered triangular inversion with valuation-weighted off-diagonal coefficients;
- the congruential Euler triangular inverse and universal denominator clearing;
- the odd-power generating-function identity for
  \(S_n(p)=\sum_{a=0}^{p-1}(-1)^a(2a+1)^n\);
- the exact odd-prime Euler reconstruction
  \[
  E_n=\sum_{m=0}^{n/2}(-1)^m Z_{2m+1}\binom{n}{2m}p^{2m}S_{n-2m}(p)
  \]
  for even \(n\) and odd prime \(p\);
- the uniform odd-prime tail congruence modulo \(p^{2M+2}\);
- the separate weighted dyadic reconstruction based on
  \[
  R_n=\frac{3^{n+2}-1}{4(n+1)(n+2)}
  \]
  and the coefficients of \(z^2/\sinh^2z\);
- 2-adic integrality of the dyadic source and inverse coefficients;
- the uniform dyadic tail congruence modulo \(2^{2M+2}\);
- finite odd-prime and dyadic unit-coordinate decompositions;
- finite Mahler reconstruction and exact finite-difference formulas;
- the valuation gain for unit exponential modes;
- standard-window Lucas reduction and residue independence in that window;
- companion-jump recurrences and the Fibonacci packet recurrence;
- exact dyadic-odd CRT packet factorization.

## Classical inputs

The paper uses the following as established background rather than presenting them as new results:

- exponential generating functions and coefficient convolution;
- Euler numbers, Euler zigzag numbers, and Bernoulli numbers;
- Hensel lifting and Teichmuller representatives;
- the structure of odd-prime and dyadic unit groups;
- the lifting-the-exponent lemma;
- Mahler/Newton interpolation;
- Lucas reduction;
- the Chinese remainder theorem;
- companion matrices and classical linear recurrences.

Paper-local references are intentionally absent. Historical sources and priority comparisons are reserved for the consolidated bibliography at the end of the series.

## Finite numerical certificates

The current code reruns finite exact certificates for:

- 180 odd-prime supercongruence cases;
- 111 weighted dyadic reconstruction cases;
- 30 standard-window parameter cases;
- 192 CRT address and reconstruction cases;
- exact Mahler reconstruction;
- exact Fibonacci packet recurrence;
- coefficient and denominator registries for selected congruential Euler families.

These finite checks support the implementation and displayed examples. They do not replace the uniform proofs and are not used to promote the explicitly conjectural statements.

## Conjectural statements

The following remain conjectural or externally reviewable:

- a uniform standard-window tail period beyond the finite ranges tested;
- the full congruential Euler finite-difference valuation bound after all triangular packet losses;
- a canonical finite obstruction packet for every failed arithmetic lift;
- a minimal prime-independent spine gluing the weighted dyadic sector to all odd-adic realizations;
- historical novelty or OEIS priority for individual formulas and families.

## Claim boundary

The paper does not prove every Euler-family supercongruence, unrestricted Galois reciprocity, automorphy, or the Langlands correspondence. It supplies an exact arithmetic packet language and a set of proved coordinate, inversion, valuation, and reconstruction theorems that later papers can use.

## Reference policy

The LaTeX source contains no `\\cite`, `\\bibitem`, or `thebibliography` commands. References will be added only to the consolidated bibliography at the end of the complete series.
