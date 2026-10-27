# Euler terminal 161: a rigorously recentered finite certificate

## Result

The prior certificate retained one residue class `T = tau_450 mod 2^450`
for the integer family

\[
 B=17659+2^{18}T,\qquad r=B2^{640}-161.
\]

A fresh computation at its least nonnegative representative produces a valid
1096-bit finite Euler coefficient model. It retains exactly one pair

\[
 (T,Z)=(\tau_{917},\zeta_{917})\pmod {2^{917}},
 \qquad x=10202+2^{15}Z.
\]

The complete residues and coefficient records are in `recenter_1096.json`.
The new parameter residue has bitlength **915**. Consequently, for every
ordinary integer

\[
 0\le T<2^{914}
\]

and every `x` in `Z_2`, the actual Euler residual has no simultaneous zero
of its value and derivative. The stronger exact interval is
`0 <= T < tau_917`.

This is conditional on the inherited exact Euler packet identities and
restrictedness, the global terminal/skeleton reductions, and the old
629-bit certificate. The new local parameter stability is proved below.
This is not a claim of universal Euler simplicity or an exact singular
Euler parameter. No Lean compiler was run.

## 1. The local multiplier stability theorem

Set `j=161`, `L=640`, and let `Bc` be a positive odd integer less than
`2^s`. On the cylinder

\[
 B=B_c+2^s S,\quad S\in\mathbf Z_{\ge0},\quad r_B=B2^{640}-161,
\]

suppose the true terminal label is 161 and hence `mu=-154`.
Let `P` be a positive precision and `Q=2P`. Assume

\[
 2^{640}>2(161+Q),\qquad P\le 2r_{B_c}-1,
\]

and

\[
 P\le 641+s-\left\lceil\log_2(2(161+Q)+1)\right\rceil.
 \tag{1}
\]

Let `Lc` and `Uc` be the actual center residual's packet sums over
`q<161` and `161<=q<Q`, respectively. On either parity ball, coefficientwise,

\[
 \boxed{B G_{r_B}=B L_c+B_c U_c\pmod {2^P}.}
 \tag{2}
\]

In contrast to the old model at `B=1`, this assertion is restricted to the
specified cylinder. Its coefficients are recomputed from the actual Euler
index at `Bc`.

### Bernoulli units

For even `n` in the relevant range, the inherited exact midpoint identity
and the Bernoulli denominator valuations give

\[
 2B_n\equiv \sum_{k=0}^P\binom nk2^kB_k\pmod {2^P},
 \tag{3}
\]

provided `n-1>=P`. The omitted undepletion factor is `1-2^(n-1)`, which is
one modulo `2^P` under this explicit bound.

If `n'=n+Delta`, `v_2(Delta)>=K`, and `k<2^K`, Vandermonde's identity and

\[
 \binom{\Delta}{i}=\frac{\Delta}{i}\binom{\Delta-1}{i-1}
\]

give

\[
 v_2\!\left(\binom{n'}k-\binom nk\right)
 \ge K-\lfloor\log_2 k\rfloor.
\]

For nonzero `2^k B_k` with `k>=1`, its valuation is `k-1` (including `k=1`),
and

\[
 k-1\ge\lfloor\log_2 k\rfloor.
\]

Thus every summand difference in (3) is divisible by `2^K`. In this cylinder,
`K=641+s`, so `2 B_(2r_B+2q)` and `2 B_(2r_c+2q)` agree modulo `2^P` for
all relevant `q`, as do their odd inverses and ratios.

### Factorial units

The finite factorial quotient occurring in packet `q` consists of the
factors

\[
 2^{641}B+d,\qquad -321\le d\le 2(q-161).
\]

For `d!=0`, its valuation is `v_2(d)` by the size assumption, and its stripped
odd unit changes by a multiple of

\[
 2^{641+s-v_2(d)}.
\]

The logarithmic bound in (1) makes this invisible modulo `2^P` for every
`q<Q`. There is exactly one zero offset when `q>=161`, whose stripped odd
unit is `B`. It is absent when `q<161`. The remaining odd prefactor changes
only modulo `2^(641+s)`.

Using the exact packet formula, all other factors are therefore fixed to the
required relative precision, while the single zero offset contributes the
ratio `Bc/B` for upper packets. Packet valuation factors are nonnegative
because `mu` is the true normalization. Hence

\[
 B\gamma_{r_B,q}\equiv
 \begin{cases}
 B\gamma_{r_c,q},&q<161,\\
 B_c\gamma_{r_c,q},&161\le q<Q,
 \end{cases}\pmod {2^P}.
\]

### Tail

On either parity ball `x=a+2Y`, at least `floor(q/2)` factors of `P_q(x)`
are coefficientwise even. Consequently `P_q(a+2Y)` is coefficientwise
divisible by `2^floor(q/2)`. Integral packet normalization and the integral
source make every term with `q>=2P` vanish modulo `2^P` on that ball.
This controls all later carry events and proves (2).

## 2. Apply the theorem at the retained center

Read `tau_450` from the old complete certificate and put

\[
 B_c=17659+2^{18}\tau_{450},\qquad s=468.
\]

Take `P=1096`, `Q=2192`. The local budget is

\[
 641+468-\lceil\log_2(2(161+2192)+1)\rceil
 =1109-13=1096.
\]

The Bernoulli and size inequalities hold by enormous margins. A fresh exact
carry scan using the proved finite minimizer cutoff verifies that the center
has `mu=-154`, `j=161`.

We compute `Lc` and `Uc` directly at this center, first substituting
`x=10202+2^15 Z`. Form

\[
 H_0=2^{-178}(17659 L_c+B_cU_c),\qquad
 H_1=2^{-178}(2^{18}L_c).
\]

The complete coefficient records verify integrality and imply, only on the
retained cylinder,

\[
 B\,2^{-178}G_{r_B}(10202+2^{15}Z)
   =H_0(Z)+T H_1(Z)\pmod {2^{918}}.
 \tag{4}
\]

No old coefficients were extrapolated past 629 bits. The actual center's
Bernoulli and factorial units are rebuilt at 1096 bits.

The complete derivative coefficient records are even. Put `Q_i=H_i'/2`,
retaining 917 bits. Their reductions have the same nonsingular form as in
the preceding certificate:

\[
 H_1\equiv1,\quad Q_0\equiv Z,\quad Q_1\equiv0\pmod2,
\]

and the pair `(H_0+T H_1,Q_0+T Q_1)` has identity Jacobian modulo two.
The two-variable binary lift checks all four successors at every bit and
retains exactly one. An independent univariate elimination lift using

\[
 T=-H_0/H_1,\qquad Q_0-H_0Q_1/H_1=0
\]

returns precisely the same pair through 917 bits. The new pair reduces to
the old pair modulo `2^450`.

Together with the old global certificate outside its retained cylinder,
this proves the new necessary congruence for every admissible integer
parameter whose true terminal label is 161.

## 3. The initial interval really has terminal label 161

The center's terminal scan alone would not establish the conclusion for an
interval. For every positive odd `B`,

\[
 s_2(B2^{640}-161)=s_2(B)+637.
\]

For `T<2^917`, `B<2^935`, so a safe global minimizer cutoff is 524. For all
`q` in this cutoff,

\[
 \lambda_r(q)=
 \begin{cases}
 3q+2-s_2(160-q),&0\le q<161,\\
 -154+3(q-161)+s_2(q-161),&161\le q\le524.
 \end{cases}
\]

The first finite table has minimum `-1` only at `q=1`. The second has minimum
`-154` only at `q=161`. This proves `mu=-154`, `j=161` throughout the whole
asserted interval. The old skeleton reduction therefore controls every
`x in Z_2`, rather than merely the computed local ball.

## 4. What recentering does and does not close

This removes the old 629-bit *uniform factorial-unit ceiling*. It is a
new finite family certificate, giving 467 additional parameter bits and
increasing the transparent initial exclusion from `2^449` to `2^914`.

It does not prove that the surviving parameter is not an ordinary integer.
Nor does it construct an analytic interpolation of the undepleted family
at all precisions.

Every use of the finite Bernoulli model still requires

\[
 P\le 2r_{\rm center}-1.
\]

If the retained centers stabilized at an ordinary integer parameter, their
Euler index would eventually be fixed. Sufficiently many hypothetical
refinements would encounter this nonunit/depletion boundary. Asserting
that recentering can continue indefinitely *and* always changes the center
would therefore assume part of the desired nonintersection statement.
The affine step also retains its growing-cutoff size condition. If the
old parameter precision is `h`, then `s=h+18` and the displayed bound gives

\[
 h_{\rm new}\le h+480-\lceil\log_2(2(161+2P)+1)\rceil,
 \qquad P=h_{\rm new}+179.
\]

This gives a positive gain of 467 now. It does not prove positive gain at
arbitrary precision: the logarithmic loss grows, and the cutoff must remain
below the specified wall scale. An actual universal closure still needs
arithmetic nonintersection, a transversality theorem, or a stronger exact
parameter model through those boundaries.

## 5. Reproducibility and failures

Run `recenter_certificate.py --precision 1096 --out <fresh-output.json>` with
the inherited certificate sources at the relative path used in the script.
The construction uses standard-library integer and rational arithmetic.
`verify_recenter.py` rebuilds actual Euler coefficient records at three
integer parameters in the cylinder and compares every retained local
coefficient against (4). It also checks factorial offsets and exact giant
binomial congruences. These checks corroborate the proof, not replace its
universal quantifiers.

The first verifier launch failed with a Python syntax error caused by an
unclosed parenthesis in a factorial comparison. The parenthesis was fixed
before any arithmetic checks ran. No failed launch is counted as a pass.

Final verification passed in 90.82287740707397 seconds. At each of the three
actual parameters `S=0,1,3`, all 74 retained local coefficients agree modulo
`2^918`; 4383 factorial offsets and the binomial inequalities for
`1<=k<=1096` also pass. A negative control deliberately extrapolates the old
global template to 1096 bits. That extrapolation fails first at global
valuation 790, or 612 bits after chart content. Thus the new computation
repairs an actual arithmetic discrepancy, not only a conservative budget.
