# Actual undepletion at every Jacobi depth

Base: Euler-Bernoulli-structure-20261005, archive SHA256
b1dd12d9e0904b7d9a0b999e961fd1b12b4e3afde71995da4064d7849cdfacf7.

This note settles a comparison issue at the missing bound: the stable Jacobi
construction can approximate the *actual* stationary scalar to unbounded
precision, without stopping at the independent-undepletion exponent. It does
not prove that scalar nonzero. The remaining termination criterion is stated
as an equivalence, rather than inferred from convergence.

## 1. Reinsert the exact actual Euler factor

Fix an admitted ordinary terminal-161 index r. Set

    delta_r=2^(2r-1),
    d_(r,q)=D(r+q)/D(r),
    e_(r,q)=(1-delta_r)/(1-delta_r*4^q),
    R_(r,q)=2^(154+5q) (2r+2q-1)/(2r-1)
                           / product_(j=1)^(2q)(2r+j).

Since r>=1, e_(r,q) is a dyadic unit for every q>=0, and e_(r,0)=1.
The exact ordinary Bernoulli identity is

    2B_(2(r+q))/2B_(2r) = d_(r,q) e_(r,q).

Thus the actual packet coefficient is exactly R_(r,q)d_(r,q)e_(r,q).
No Euler factor is discarded and no approximation to the ordinary index is
introduced. The true-terminal hypothesis gives R_(r,q) in Z_2 and its
valuation tends to infinity with q.

Let d_(r,q)^[m] be the finite shifted Jacobi moments in the reviewed parent
theorem. Define the actual model on x=10202+2^15 Z by

    K_(r,m)^actual(Z)
      =2^-178 sum_(q>=0) R_(r,q)d_(r,q)^[m]e_(r,q)
                                      P_q(x)A(x-q).

Every model moment and every e_(r,q) is a unit. The full source series and
its derivatives converge restricted analytically. It matches all actual
packets q<2m exactly.

## 2. Unbounded actual precision

The parent all-q moment estimate is

    d_(r,q)^[m]-d_(r,q) in2^h_m Z_2,
    h_m=4m+4v_2(m!)=8m-4s_2(m).

Multiplication by e_(r,q) preserves this divisibility. Consequently

    K_(r,m)^actual-K_r in2^L_m Z_2<Z>,
    L_m=8m-4s_2(m)-178.                              (1)

This holds for every m>=1 as a function-error bound. Its proof includes
every omitted packet; it is not limited to the first carry range and has
no upper bound imposed by 2r-25. It does not use the all-rank Padé theorem.

For L_m>=9, the actual quadratic-chart theorem and (1) imply that the
model half derivative remains an isometry. If c_r,c_(r,m) are the unique
actual and model critical points, then

    v_2(c_(r,m)-c_r)>=L_m-1,
    v_2(Phi_(r,m)^actual-Phi_r^actual)>=L_m,           (2)

where Phi_(r,m)^actual=K_(r,m)^actual(c_(r,m)) and
Phi_r^actual=Phi_r(2^(2r-25)). For the second inequality the direct error
has valuation at least L_m; stationarity makes the displacement term have
valuation at least 2L_m-2. The inherited actual chart supplies the required
integral Taylor expansion and unit quadratic term.

In particular (2) holds for every m>=25, and L_m tends to infinity. This
is actual stationary convergence, with the undepletion factors retained.

## 3. Exact separation criterion and what it does not prove

For each fixed admitted ordinary r there is the equivalence

    Phi_r^actual != 0
       iff there exists m>=25 with
           v_2(Phi_(r,m)^actual)<L_m.                (3)

The reverse implication follows directly from (2). For the forward
implication, let v_2(Phi_r^actual)=v<infinity and choose m with L_m>v.
Equation (2) then gives v_2(Phi_(r,m)^actual)=v<L_m.

Therefore arbitrarily deep approximation exists, but proving that its
strict test eventually succeeds remains exactly the arithmetic exclusion.
If Phi_r^actual=0, (2) permits every model value to be nonzero while its
valuation grows at least as fast as L_m. Neither integral moment inverses
nor the exact undepletion formula contradict that behavior.

An explicit depth-independent bound C(r) on model critical valuations
at cofinal depths would prove the desired termination. Such a bound is
not obtained from (1)-(2). Formula (3) is a rigorous comparison reduction,
not a substitute for the requested Bernoulli-specific nonvanishing proof.

## 4. Scope and bounded checks

The checker uses exact rational Bernoulli numbers at small ordinary indices
to verify the actual/depleted factor identity and reinsertion into the
shifted Jacobi moments, including exact first-exit errors. These checks
do not test the giant terminal-161 chart. The all-depth chart conclusion
rests on the reviewed parent Jacobi theorem, the actual packet identity,
and the inherited uniform quadratic-chart theorem explicitly used above.

No additional multiplier digits or critical valuations were searched.
