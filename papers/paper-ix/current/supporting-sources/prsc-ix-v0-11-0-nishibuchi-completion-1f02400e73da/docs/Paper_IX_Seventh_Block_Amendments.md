# Paper IX seventh-block amendments

**Author: Komorebi P. — release v0.7.0**

The original corrected PDF remains unchanged. These amendments describe the precise correspondence of this block's checked statements to that PDF.

## 8.5: replace the dependence on 7.5 by a direct proof

For any prime p, positive divisor m of p-1, h=(p-1)/m, and n>=1, the independently constructed reduced inverse obeys e(n+h)=e(n) in F_p. The proof operates on actual Hurwitz coefficient sequences, with binomial convolution and degree shifts. Factorials are never inverted in F_p.

The section g(d)=1 when m divides d, zero otherwise, has g(0)=1 and U^p g=Ug. The reciprocal is constructed by forward substitution. Both the ordinary and pth product rules, and cancellation against g, are proved. They imply U^p f=Uf. Support of the reciprocal on multiples of m is separately established, and its row recurrence is identified by uniqueness with the earlier reduced inverse. Evaluating at degree mn-1 proves the period.

The original odd-prime statement is a specialization. The source also covers p=2, m=1. It proves that h is a period, not that it is minimal. The row restriction is necessary in general: e(0)=1 and e(1)=2 for (p,m)=(3,2). The divisor hypothesis is also substantive: at (p,m)=(5,3), e(2)=4 and e(3)=2.

The earlier residue-independence proof transports this period to actual p-adic lifts of every rational standard-window coefficient. The image in Q_p of each lifted iterated difference is proved equal to the corresponding rational-coefficient difference. There is no reduction homomorphism from all of Q to F_p and no vacuous divisibility claim in Q_p.

## 7.5: still pending, with explicit partial results

The new unconditional fragment gives divisibility by p for every positive-order difference, on positive rows and in the standard window, at any multiple of h. This does not establish divisibility by p^min(k,m*n).

The exact example C_(6,0)(1)=-1, C_(6,0)(2)=923 has first difference 924 and valuation v_3=1. It excludes an automatic modulus-square upgrade. It does not refute the proposed global theorem, whose k=1 bound is only one power.

The new Dwork operator criterion defines actual sparse Hurwitz coefficients and proves the coefficient-extraction formula. It assumes coefficientwise flatness, then derives the full saturated base-step bound. A separate equivalence reduces all orders to the triangular range k<=m*n. None of these implications supplies a flat integral lift of the general unnormalized Euler sequence.

Normalization uses the existing Congruential.unnormalized definition, not a renamed surrogate. If an unnormalized finite difference has precision L, the normalized one has precision L-v_p(j!). This is a conditional theorem. Zero-safe precision means x=0 or v_p(x)>=L, allowing negative loss thresholds. The zero coefficient is never assigned finite order zero.

The original all-residue higher-power theorem still needs a checked argument for the actual family. The retrieved supporting prose proof describes weighted Amice bounds, dual Mahler estimates, singular ratios and nonsingular propagation. Those results are not silently imported as axioms or declared checked in this block.

## Counts and preservation

Only item 8.5 changes from PENDING_LEAN to LEAN_CHECKED. Item 7.5 retains that pending status, with its proved partial targets recorded in a separate field. There are 23 checked and one pending manuscript-proved items, three classical inputs and two conjectures. All 31 upstream proof sources, the original PDF and the six earlier supplement PDF/TeX pairs are unchanged.
