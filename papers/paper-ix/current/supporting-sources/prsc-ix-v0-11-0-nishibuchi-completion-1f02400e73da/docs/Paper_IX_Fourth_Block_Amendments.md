# Fourth-block statement clarifications

Author: Komorebi P.

## 7.2: finite samples, full sequences and interpolants

The original first formula is correct for 0<=n<=N and the coefficients computed from f(0),...,f(N). The second formula requires one of three explicit interpretations:

1. For a full sequence on the natural numbers, its full coefficient sequence gives Delta^s f(n)=sum_{j=0}^n binomial(n,j)c_(s+j), for every n,s.
2. For the degree-N binomial interpolant built from c_0,...,c_N, the same formula uses zero coefficients beyond N, for every n,s.
3. For a finite sample of an otherwise unspecified function, its actual forward difference agrees with the interpolant only on contained stencils n+s<=N.

The Lean source proves all three forms, coefficient extraction and uniqueness, and an exact counterexample to deleting the stencil condition. A sample with f(0)=0 does not distinguish the sequences f(n)=n and g(n)=0, whose first differences at zero are different. This is a clarification of the source's scope, not a claim that finite observations determine unknown future values.

## 7.3: zero and finite binomial support

The extended additive valuation used in the formal statement is infinity at zero. Mathlib's finite-valued PadicInt.valuation has a default of zero at zero; using that default in this inequality without a separate zero case would be incorrect. The new definition is proved equivalent to actual p-power divisibility in Z_p at every finite precision.

At a natural argument n, the only nonzero binomial coefficients in the shifted formula have r=s+j with 0<=j<=n. The formal minimum is over exactly these terms and includes the actual binomial valuation. Weights may themselves be infinity. This covers cancellation, identically zero functions and differences above the interpolant degree. No new convergence theorem for p-adic arguments is asserted.

## 7.4: actual units and the Fermat step

The power identity is proved for arbitrary natural h over a commutative ring. The p-adic divisibility theorem assumes u is an actual unit of Z_p and derives divisibility of u^(p-1)-1 from the residue-field map and its kernel ideal. This establishes the paper's h=p-1 claim for every prime, including p=2, as well as multiples of that step.

Coefficients of finite linear combinations belong to Z_p. Nonunits, or nonintegral linear coefficients, are not admitted. The integer example u=2, p=5, s=2, n=0 has difference 225 and valuation exactly two. The nonunit example u=3, p=3, s=1, n=0 has difference eight and no factor of three.

The global congruential Euler theorem 7.5 is not a consequence of this module alone. A representation of those particular coefficients by such modes, or another complete argument for their global bound, is still needed.
