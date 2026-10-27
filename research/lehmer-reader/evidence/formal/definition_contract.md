# Exact mathematical definition contract

## Fixed global object

The object is Ramanujan's tau function, defined by

\[
\Delta(q)=q\prod_{m\geq1}(1-q^m)^{24}
          =\sum_{n\geq1}\tau(n)q^n.
\]

This is Lehmer's nonvanishing conjecture for tau. It is not the Mahler-measure
problem or the totient problem with the same surname. The all-index target is
`for every integer n >= 1, tau(n) != 0`. Its prime reduction is an exact
conclusion from the weight-12 Hecke recurrence and its actual initial prime
values. It must not be replaced by a bounded search.

## Packets and residual

All five coordinate indices are `i = 0,1,2,3,4`. For positive integer n,

\[
\mathcal V_n=\{v\in\mathbb Z^5:
v_i\equiv i\pmod5,\quad \sum_i v_i=0,\quad \sum_i v_i^2=10n\},
\qquad W(v)=\frac{1}{288}\prod_{0\leq i<j\leq4}(v_i-v_j).
\]

The shell is finite. Its coordinates are pairwise distinct since their
residues are distinct. Thus every individual W is nonzero. W is an integer:
the Vandermonde product of any five integers is divisible by
`0!1!2!3!4! = 288`. This does not imply that its shell sum is nonzero.

The character chi_5 is the quadratic Dirichlet character modulo 5, extended
by zero on multiples of 5. The content is the positive coordinate gcd. It
cannot be divisible by 5. The primitive packet sum is

\[
R(n)=\sum_{v\in\mathcal V_n,\,\gcd(v_0,\ldots,v_4)=1}W(v)
=\sum_{d^2\mid n}\mu(d)\chi_5(d)d^{10}\tau(n/d^2).
\]

The equality with tau is a consequence of the checked packet theorem and
the content-scaling argument. It is not the definition of every possible
weighted shell model. Boundary values are `R(1)=1` and `R(p)=tau(p)`.

The involution is `J(v)_i = -v_{(-i mod 5)}`. It preserves the standard
residues, zero sum, norm, coordinate gcd and W. “J-orbits” means actual orbits
of this involution on the shell. A plotted two-dimensional projection does
not provide new mathematical packets.

## Local recurrences

For a prime p set `a=tau(p)`, `b=p^11`, `c=chi_5(p)p^10`. Define

\[
T_0=1,\qquad T_1=a,\qquad T_r=aT_{r-1}-bT_{r-2}\quad(r\geq2).
\]

Then `T_r=tau(p^r)`, and `R(p^r)=T_r-cT_{r-2}` begins only at `r=2`.
There is no negative-index T in the source definition. Equivalently,

\[
\sum_{r\geq0}R(p^r)X^r
 =\frac{1-cX^2}{1-aX+bX^2}.
\]

This identity is in `Z[[X]]`. After reduction modulo M its denominator
remains invertible because its constant coefficient is 1. It does not use
analytic convergence in X.

## Quantified conclusions and boundaries

1. For every prime p and integer m >= 1, `R(p^(2m)) != 0`. Therefore
   `R(s^2) != 0` for every integer s >= 1. This does not assert that every
   primitive coefficient has been proved nonzero.
2. For every odd prime p different from 5 and integer m >= 0, an odd integer
   multiplier U satisfies `R(p^(2m+1)) = tau(p) U`. U is defined by polynomial
   division before evaluation, including the case `tau(p)=0`.
3. For every positive integer n, `R(n)=0` if and only if `tau(n)=0`. More
   explicitly each vanishes precisely when some prime p with odd `v_p(n)`
   has `tau(p)=0`.
4. For every M >= 1 there is a positive-density set of actual rational primes
   p with `p=-1 mod 5M`, `tau(p)=0 mod M`, and `R(p^r)=0 mod M` for all r >= 1.
   The witnesses depend on M. This is not an actual prime zero and does not
   exchange `for every M, there exists p` with `there exists p, for every M`.
5. The trace-zero filtered Frobenius example is over Q_p and has filtration
   jumps 0 and 11 in the stated cohomological convention. The construction
   does not identify it with the restriction of Delta's global Galois
   representation.
6. Content conservation concerns finite symmetric polynomial corrections
   universally null on every positive shell. Shell-specific interpolation,
   an arbitrary indicator function or a nonpolynomial correction is not in
   that domain merely because it has zero total on one shell.
7. Transfer ranks, certificates, bounded congruences and finite recurrence
   evaluations retain their explicit tested ranges. They are not quantified
   all-prime theorems.

No “axiom tau(p) != 0” is smuggled into the square or zero-equivalence proof.
The all-prime nonvanishing implication remains absent from this source set.
