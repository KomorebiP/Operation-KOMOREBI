# Carry-Newton reduction for arbitrary dyadic Euler truncation depth

Research continuation, 26 September 2026.

## Status

This note continues `PROOF.md`. The exact tail factorization from that note is retained. The new result is a finite carry-based reduction for **every** first omitted depth `r`, together with a residual-polynomial criterion for no-root, one-root, two-root, and multiple-root branches.

The mathematical reductions below are proofs. `check_carry_newton.py` supplies exact finite evidence and independent modular checks. No Lean compilation or historical-priority claim is made here.

## 1. Exact carry valuation of the factored coefficients

From the existing factorization

\[
\mathcal T_{r-1}(N)=\kappa_r\binom{2N}{2r}H_r(N-r),
\]

with

\[
H_r(x)=\sum_{j\ge0}8^j\frac{\beta_{r+j}}{\beta_r}P_j(x)\mathscr A(x-j),
\qquad
P_j(x)=x^{\underline j}\prod_{i=0}^{j-1}(2x-2i-1),
\]

define

\[
\lambda_r(j)=v_2\!\left(8^j\frac{\beta_{r+j}}{\beta_r}\right).
\]

Since \(v_2(\beta_m)=s_2(m)-1\),

\[
\boxed{\lambda_r(j)=3j+s_2(r+j)-s_2(r).}
\]

Kummer gives

\[
v_2\binom{r+j}{j}=s_2(r)+s_2(j)-s_2(r+j),
\]

hence equivalently

\[
\boxed{
\lambda_r(j)=3j+s_2(j)-v_2\binom{r+j}{j}.
}
\]

Thus every anomalously low analytic coefficient is exactly a binary-carry event.

## 2. The infinite minimization is actually finite

Let

\[
\mu_r=\min_{j\ge0}\lambda_r(j),
\qquad
J_r=\{j:\lambda_r(j)=\mu_r\}.
\]

Since \(\lambda_r(0)=0\), one always has \(\mu_r\le0\). For \(j\ge1\),

\[
\lambda_r(j)
=3j+s_2(r+j)-s_2(r)
\ge 3j+1-s_2(r).
\]

Therefore any minimizer must satisfy

\[
\boxed{
0\le j\le \left\lfloor\frac{s_2(r)-1}{3}\right\rfloor.
}
\]

So an infinite tail has a finite carry Newton polygon whose size is controlled by the **binary digit sum of the omitted depth**, not by the magnitude of the depth.

## 3. Residual cancellation polynomial

Normalize

\[
G_r(x)=2^{-\mu_r}H_r(x).
\]

Because the coefficient valuations tend to infinity, \(G_r\in\mathbb Z_2\langle x\rangle\). The analytic source satisfies \(\mathscr A\equiv1\pmod2\) coefficientwise, and every normalized minimum coefficient is a dyadic unit. Therefore

\[
\boxed{
\overline G_r(X)
=\sum_{j\in J_r}X^{\underline j}
\in\mathbb F_2[X].
}
\]

Since

\[
X^{\underline j}
\equiv
X^{\lceil j/2\rceil}(X+1)^{\lfloor j/2\rfloor}
\pmod2,
\]

the first cancellation layer is completely explicit.

The whole-tail valuation becomes

\[
\boxed{
 v_2\mathcal T_{r-1}(N)
 =4r-1+v_2\binom Nr+\mu_r+v_2G_r(N-r).
}
\]

This is an exact identity, not a lower bound.

## 4. Root taxonomy at the first residual level

Write `1_S` for an indicator modulo two. Then

\[
\overline G_r(0)=1_{0\in J_r},
\qquad
\overline G_r(1)=1_{0\in J_r}+1_{1\in J_r}.
\]

Also

\[
\overline G_r'(0)=1_{1\in J_r}+1_{2\in J_r},
\]

\[
\overline G_r'(1)=1_{1\in J_r}+1_{2\in J_r}+1_{3\in J_r}.
\]

Hence:

- if \(0\in J_r\) and \(1\notin J_r\), there is no residual root and \(G_r(x)\) is a unit for every integer/dyadic `x`;
- if \(0,1\in J_r\), the only residual root is `1`;
- if \(0\notin J_r\) and \(1\in J_r\), the only residual root is `0`;
- if neither `0` nor `1` is in \(J_r\), both residue classes are roots.

A residual root `e` is simple exactly when the displayed derivative at `e` is one.

For a simple root, if `x,y` lie in the same residue class `e mod 2`, the divided difference

\[
\frac{G_r(x)-G_r(y)}{x-y}
\]

is a dyadic unit because its reduction is \(\overline G_r'(e)=1\). Therefore the branch is an isometry. It has a unique root \(\alpha_{r,e}\in e+2\mathbb Z_2\), and

\[
\boxed{
 v_2G_r(x)=v_2(x-\alpha_{r,e})
 \quad(x\equiv e\pmod2).
}
\]

On a nonroot residue class, \(v_2G_r(x)=0\).

If a residual root is multiple, substitute `x=e+2y`, remove the common dyadic content, and repeat the same construction. This gives a recursive dyadic cancellation tree.

## 5. First two-root example: r = 510

For

\[
r=510=2^9-2,
\]

the finite carry polygon has

\[
\lambda_{510}(0)=0,
\quad
\lambda_{510}(1)=4,
\quad
\lambda_{510}(2)=-1.
\]

Thus

\[
\mu_{510}=-1,
\qquad J_{510}=\{2\},
\]

and

\[
\overline G_{510}(X)=X(X+1).
\]

Both residual roots are simple. Hence there are unique roots

\[
\alpha_0\in2\mathbb Z_2,
\qquad
\alpha_1\in1+2\mathbb Z_2,
\]

and, with `x=N-510`,

\[
\boxed{
 v_2\mathcal T_{509}(N)
 =2038+v_2\binom N{510}
 +v_2(x-\alpha_{x\bmod2}).
}
\]

The audit lifts the roots to 64 bits:

\[
\alpha_0\equiv
1840775104690357186
\pmod{2^{64}},
\]

\[
\alpha_1\equiv
14399460289900872487
\pmod{2^{64}}.
\]

This formula was checked independently against the original unfactored tail modulo \(2^{2100}\) at fifteen rows from `N=510` through `N=605`.

## 6. Exact shifted-power-of-two wall crossing

The appearance of powers of two has an exact formulation.

Fix `j>=1`. Define for `0<=k<j`

\[
e_j(k)
=3k+s_2(j-1)-s_2(j-k-1),
\]

\[
E_j=\min_{0\le k<j}e_j(k),
\qquad
K_j=\{k<j:e_j(k)=E_j\},
\]

and

\[
A_j=3j+1+s_2(j-1),
\qquad
L_j=A_j-E_j.
\]

For `L` large enough that `2^L>j`, put

\[
r_L=2^L-j.
\]

Then for `k<j`,

\[
\lambda_{r_L}(k)=e_j(k),
\]

while

\[
\lambda_{r_L}(j)=A_j-L.
\]

For `k>j` in the only range capable of minimizing,

\[
\lambda_{r_L}(k)
=\lambda_{r_L}(j)+3(k-j)+s_2(k-j)
>\lambda_{r_L}(j).
\]

Consequently:

\[
\boxed{
L<L_j\Rightarrow j\notin J_{r_L},
}
\]

\[
\boxed{
L=L_j\Rightarrow J_{r_L}=K_j\cup\{j\},
}
\]

\[
\boxed{
L>L_j\Rightarrow J_{r_L}=\{j\}.
}
\]

Thus every correction layer `j` has an exact **shifted power-of-two wall**

\[
\boxed{r=2^{L_j}-j.}
\]

Crossing that wall makes the `j`th analytic tail layer the unique dominant residual term.

The first walls are

\[
15,\ 254,\ 2045,\ 32764,\ 131067,\ldots
\]

for `j=1,2,3,4,5,...`.

The first three post-wall residual geometries are:

- `j=1`: one simple root;
- `j=2`: two simple roots;
- `j=3`: an even double root and an odd simple root.

For singleton `J={j}` in general,

\[
\overline G_r(X)
=X^{\lceil j/2\rceil}(X+1)^{\lfloor j/2\rfloor},
\]

so higher `j` produce increasingly ramified cancellation trees.

## 7. Computational audit

`check_carry_newton.py` uses exact rationals and arbitrary-precision integers only.

The retained run reports:

- 805,004 exact checks of the carry formula;
- 499,995 checks immediately beyond the finite minimizer cutoff;
- 600 shifted-wall checks (`j<=200`, before/at/after each wall);
- all 131,328 nonempty exact rational tails with `N<=512` matched the no-root/simple-root prediction;
- 123,325 of those tails were no-root cases;
- 8,003 were simple-root cases;
- no multiple-root case occurs below `r=513`;
- the first two-root case `r=510` was also checked through the original unfactored kernel modulo `2^2100` at fifteen selected rows.

The finite run is evidence for the implementation. The universal statements above follow from the explicit carry identities, the finite-minimizer bound, reduction modulo two, and the divided-difference argument.

## 8. Remaining frontier

The next unsolved layer is no longer “the exact dyadic tail valuation” in undifferentiated form. It is narrower:

1. classify the multiple-root branches generated by the residual polynomials;
2. derive closed carry formulas for their successive rescalings;
3. identify when the recursive dyadic tree admits a finite symbolic description;
4. connect this tree to the already-developed affine Mahler/polyphase refinement operators.

The first genuinely multiple branch appears at the post-wall `j=3` family: the odd branch is already solved by a simple Hensel root, while the even branch requires one more dyadic blow-up.
