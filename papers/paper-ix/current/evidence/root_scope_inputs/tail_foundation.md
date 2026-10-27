# Dyadic Euler tails: exact wall resolution and finite polynomial reduction

**Operation Komorebi · Komorebi P. · Continuation 04 · 26 September 2026**

## Status and scope

This continuation proves a necessary-and-sufficient emergence law on every **regular carry wall**, gives an explicit classification of the five-root family for every wall distance and every dyadic argument, and supplies complete coefficient certificates for the first irregular wall, of size seventeen. It also constructs a finite-degree polynomial carrying the complete tail valuation at every first omitted depth.

The universal statements below have mathematical proofs. The seventeen-root classification at its finitely many exceptional distances is computer-assisted: each residue ball has an exact coefficientwise certificate, and a proved truncation estimate controls all uncomputed coefficients. No Lean run was performed. Historical priority is not assessed.

The earlier v3 condition `delta > 2 d_i` is a valid sufficient Hensel condition. It is **not an exact emergence threshold**. The distinction is corrected here without withdrawing the valid v3 implication.

This is not an explicit root classification for every irregular wall or every arbitrary depth. The all-depth polynomial reduction is exact, but an implicit polynomial is not the same as an explicit classification of all its roots.

## 1. Conventions and the exact tail

Use the signed Euler numbers and ordinary Bernoulli convention

\[
\operatorname{sech}t=\sum_{n\ge0}E_n\frac{t^n}{n!},\qquad
\frac{t}{e^t-1}=\sum_{n\ge0}B_n\frac{t^n}{n!},\qquad B_1=-\frac12.
\]

The target is `E_(2N)`, where `N` is the half-index. Let `M` be the last retained depth and `r=M+1` the first omitted depth. The valuation is normalized by `v_2(2)=1`, with `v_2(0)=infinity`. A residue zero modulo `2^P` means only valuation at least `P`.

Define

\[
A(N)=\frac{3^{2N+2}-1}{4(2N+1)(2N+2)},
\qquad
\left(\frac z{\sinh z}\right)^2=\sum_{m\ge0}\beta_mz^{2m},
\qquad \kappa_m=2^{2m}(2m)!\beta_m.
\]

Here `beta_0=kappa_0=1`. For `m>=1`,

\[
\beta_m=-\frac{2^{2m}(2m-1)B_{2m}}{(2m)!},
\quad v_2(\beta_m)=s_2(m)-1,
\quad \kappa_m=-2^{4m}(2m-1)B_{2m},
\quad v_2(\kappa_m)=4m-1. \tag{1.1}
\]

The coefficient identity follows by differentiating `z coth z`. The valuation uses the classical facts `v_2(B_(2m))=-1` and `v_2((2m)!)=2m-s_2(m)`. The first is the dyadic consequence of von Staudt–Clausen [S1].

The source satisfies

\[
\sum_{N\ge0}A(N)\frac{t^{2N}}{(2N)!}
=\frac{\sinh(2t)\sinh t}{2t^2}.
\]

Multiplication by `4t^2/sinh^2(2t)` gives `sech t`, hence

\[
E_{2N}=\sum_{m=0}^{N}\kappa_m\binom{2N}{2m}A(N-m). \tag{1.2}
\]

The omitted tail is

\[
\mathcal T_M(N)=E_{2N}-\sum_{m=0}^{\min(M,N)}
\kappa_m\binom{2N}{2m}A(N-m).
\]

For `N<=M`, this is exactly zero. In what follows a nonempty tail always has `N>=r=M+1`.

## 2. Analytic factorization and the finite carry minimum

Let `Z_2<X>` denote the restricted power series with integral coefficients tending to zero 2-adically. Such series converge for every `X in Z_2`. Congruences of series in this note are **coefficientwise** unless explicitly stated otherwise.

Extend the source by

\[
\mathscr A(x)=\frac{9^{x+1}-1}{8(x+1)(2x+1)},
\qquad \mathscr A(-1)=-\frac{\log9}{8}.
\]

Put `ell=log 9`. Since `v_2(ell)=3`,

\[
\mathscr A(x)=\frac{\ell/8}{1+2x}
\sum_{h\ge0}\frac{\ell^h}{(h+1)!}(x+1)^h. \tag{2.1}
\]

The coefficient valuations in the displayed sum tend to infinity. For `h>=1` they are positive. Also `(1+2x)^(-1)` is restricted integral. Therefore

\[
\mathscr A\in\mathbb Z_2\langle x\rangle^\times,
\qquad \mathscr A\equiv1\pmod2,
\qquad \mathscr A(N)=A(N).
\]

Define

\[
P_q(x)=\prod_{i=0}^{q-1}(x-i)(2x-(2i+1)),\qquad P_0=1.
\]

Cancelling the factorials in two summands of (1.2), and using

\[
4^q(2x)^{\underline{2q}}=8^qP_q(x),
\]

gives the exact factorization

\[
\mathcal T_{r-1}(N)
=\kappa_r\binom{2N}{2r}H_r(N-r), \tag{2.2}
\]

where

\[
H_r(x)=\sum_{q\ge0}8^q\frac{\beta_{r+q}}{\beta_r}P_q(x)\mathscr A(x-q).
\]

For a nonnegative integer `x`, the factors `P_q(x)` vanish for `q>x`. Thus (2.2) is an identity of finite rational sums at every original Euler row, not an approximation.

The scalar coefficient has exact valuation

\[
\lambda_r(q)=3q+s_2(r+q)-s_2(r). \tag{2.3}
\]

Let

\[
\mu_r=\min_{q\ge0}\lambda_r(q),\qquad
J_r=\{q:\lambda_r(q)=\mu_r\},\qquad G_r=2^{-\mu_r}H_r.
\]

Because `lambda_r(0)=0` and `lambda_r(q)>=3q+1-s_2(r)`, every minimizer lies in the finite range

\[
0\le q\le\left\lfloor\frac{s_2(r)-1}{3}\right\rfloor. \tag{2.4}
\]

In particular `mu_r<=0`. The normalized series is restricted integral and

\[
\overline G_r(X)=\sum_{q\in J_r}X^{\underline q}\quad\text{in }\mathbb F_2[X]. \tag{2.5}
\]

This polynomial is nonzero: its highest-degree term has degree `max J_r` and coefficient one. Thus the scalar normalization is the actual Gauss normalization, not only a lower bound.

For every nonempty tail,

\[
\boxed{v_2\mathcal T_{r-1}(N)
=4r-1+v_2\binom Nr+\mu_r+v_2G_r(N-r).} \tag{2.6}
\]

The equality `v_2 binom(2N,2r)=v_2 binom(N,r)` follows from the factorial digit-sum formula. The binomial coefficients themselves need not be equal.

## 3. Shifted walls and their normal form

For `j>=1` and `0<=q<j`, define

\[
e_j(q)=3q+s_2(j-1)-s_2(j-q-1),\quad
E_j=\min_{q<j}e_j(q),
\]
\[
A_j=3j+1+s_2(j-1),\qquad L_j=A_j-E_j.
\]

Here `A_j` is a wall constant, not the source `A(N)`. Take

\[
L>L_j,\qquad \delta=L-L_j,\qquad r=2^L-j.
\]

For `q<j`, binary complementation gives `lambda_r(q)=e_j(q)`. At `q=j`,

\[
\lambda_r(j)=A_j-L=E_j-\delta.
\]

For `q=j+h>j`,

\[
\lambda_r(j+h)-\lambda_r(j)
=3h+s_2(2^L+h)-1>0.
\]

Therefore

\[
\mu_r=E_j-\delta,\qquad J_r=\{j\}. \tag{3.1}
\]

Use `P_(j+h)(x)=P_j(x)P_h(x-j)` to collect all terms at and above `j`. The lower terms have normalized valuations `delta+e_j(q)-E_j`. This proves

\[
\boxed{G_r(x)=P_j(x)U(x-j)+2^\delta V(x),} \tag{3.2}
\]

where

\[
U\in\mathbb Z_2\langle x\rangle^\times,\quad U\equiv1\pmod2,
\qquad V\in\mathbb Z_2\langle x\rangle.
\]

The higher terms forming `U` tend to zero in Gauss norm. Its leading term is a scalar unit times `mathscr A`, and all subsequent terms are even. No assumption that `V` is a unit has been made.

The reduction degree of `G_r` is exactly `j`. The half-integral roots of `P_j` are outside `Z_2`; its integral root skeleton is `0,...,j-1`.

## 4. Separating the skeleton at the correct local scale

For `0<=i<j`, put

\[
d_i=v_2(i!)+v_2((j-1-i)!).
\]

For `j>1`, define

\[
k_i=1+\max_{h\ne i,\ 0\le h<j}v_2(i-h)
=1+\left\lfloor\log_2\max(i,j-1-i)\right\rfloor.
\]

For `j=1`, define `k_0=d_0=0`. Let

\[
B_i=i+2^{k_i}\mathbb Z_2,\qquad t_i=d_i+k_i. \tag{4.1}
\]

### Lemma 4.1. The balls `B_i` partition `Z_2`

They are disjoint since, for `i!=h`, the valuation of `i-h` is smaller than both `k_i` and `k_h`.

For coverage, let `K=ceil(log_2 j)` and `b=2^(K-1)` when `j>1`. Write `j=b+h`, with `1<=h<=b`. The residue classes modulo `b` from `0` to `h-1` occur twice in the skeleton, as `i` and `i+b`; these points have `k_i=K` and split that class into its two children. The remaining classes from `h` to `b-1` occur once and have `k_i=K-1`. Hence every dyadic integer lies in exactly one `B_i`. The case `j=1` is immediate.

### Lemma 4.2. Exact content on a separating ball

On `x=i+2^(k_i)y`,

\[
P_j(i+2^{k_i}y)=2^{t_i}yQ_i(y),
\qquad Q_i\in\mathbb Z_2\langle y\rangle^\times,
\quad Q_i\equiv1\pmod2. \tag{4.2}
\]

Indeed the factor `x-i` contributes `2^(k_i)y`. Each `x-h`, `h!=i`, has a fixed factor `2^(v_2(i-h))`, and after removing it has constant odd reduction because `k_i>v_2(i-h)`. The remaining factors `2x-(2h+1)` are units. Their total fixed valuation is `d_i`.

### Lemma 4.3. A coefficientwise affine reduction is an isometry

If `F in Z_2<y>` has coefficientwise reduction `y+c`, then

\[
v_2(F(y)-F(z))=v_2(y-z)\qquad(y\ne z).
\]

To see this, divide the difference by `y-z`. The linear coefficient is odd and every contribution of degree at least two is even. The convergent quotient is therefore a unit. The one root modulo two lifts uniquely at every digit, giving a unique root `eta in Z_2`, and

\[
v_2F(y)=v_2(y-\eta).
\]

This is the elementary simple-root Hensel mechanism for restricted series [S3]. Importantly, coefficientwise reduction is stronger than merely checking values at the two residues.

### Theorem 4.4. Improved separation bound for every wall

If `delta>=t_i`, the ball `B_i` contains exactly one simple root `alpha_i` of `G_r`, and

\[
\boxed{v_2G_r(x)=d_i+v_2(x-\alpha_i)\qquad(x\in B_i).} \tag{4.3}
\]

Also `v_2(alpha_i-i)>=delta-d_i`.

**Proof.** Divide (3.2), after the substitution in (4.2), by `2^(t_i)`. Its main term is `y` times a unit. If `k_i>=1`, the reduction of `V(i+2^(k_i)y)` is constant. Therefore the normalized series has reduction `y+c`. Apply Lemma 4.3. The original derivative has exact valuation `t_i-k_i=d_i`. Evaluating the distance law at `x=i`, and using `v_2G_r(i)>=delta`, proves the displacement estimate. For `j=1`, post-wall `delta>=1` makes the entire perturbation even and the same argument applies.

The largest threshold is

\[
\boxed{\max_i t_i=v_2((j-1)!)+\lceil\log_2j\rceil.} \tag{4.4}
\]

The upper bound follows from `binom(j-1,i)` being integral and `k_i<=ceil(log_2j)`; equality occurs at an endpoint. Thus (4.4), with `delta>=1` understood, guarantees exactly `j` simple roots. They exhaust the dyadic roots because the balls partition `Z_2`.

Once all balls contain their root,

\[
\boxed{v_2G_r(x)=\sum_{i=0}^{j-1}v_2(x-\alpha_i).} \tag{4.5}
\]

For a direct proof of (4.5), if `x in B_i`, every other root has distance from `x` equal to the distance between its skeleton point and `i`. Those valuations sum to `d_i`. Equation (4.3) then gives (4.5).

This replaces v3's sufficient `delta>2 max d_i` with a generally smaller sufficient bound. Necessity requires more information about `V`, supplied next.

## 5. Complete exact classification of regular walls

**Definition.** A wall label `j` is regular here if

\[
\boxed{e_j(q)>0\qquad(1\le q<j).} \tag{5.1}
\]

This is a finite binary-digit condition, not an appeal to numerical root data. The terminology refers only to this note's wall condition.

For a regular wall, `e_j(0)=E_j=0`, so `mu_r=-delta`. In (3.2), the `q=0` contribution to `V` is `mathscr A(x)` and every other contribution is even. Hence

\[
V\equiv1\pmod2. \tag{5.2}
\]

### Theorem 5.1. Necessary-and-sufficient root emergence

For a regular wall, for every integer `delta>=1`, each `B_i` has exactly the following behavior:

\[
\boxed{v_2G_r(x)=
\begin{cases}
\delta,&\delta<t_i,\quad x\in B_i,\\
d_i+v_2(x-\alpha_i),&\delta\ge t_i,\quad x\in B_i.
\end{cases}} \tag{5.3}
\]

In the second case there is exactly one simple root in `B_i`. Its displacement is exact:

\[
v_2(\alpha_i-i)=\delta-d_i.
\]

Consequently

\[
\boxed{\#\{x\in\mathbb Z_2:G_r(x)=0\}=\#\{i:t_i\le\delta\}.} \tag{5.4}
\]

**Proof.** If `delta<t_i`, the first term of (3.2) is divisible by `2^(t_i)` on the ball and the second has exact valuation `delta`, by (5.2). This proves the first line and excludes roots. If `delta>=t_i`, Theorem 4.4 applies. The reduction after division by `2^(t_i)` is `y+1` at equality and `y` when the inequality is strict. Since `G_r(i)=2^delta V(i)` has exact valuation `delta`, (4.3) gives the exact displacement. The partition lemma proves that no other dyadic roots are missed.

Combining (2.6) and (5.3) is an exact all-row valuation formula for the original Euler remainder, including the possibility of an exact zero at a dyadic root.

### Corollary 5.2. Power-of-two skeletons

For `j=2^a`,

\[
e_j(q)=3q+s_2(q)>0\quad(1\le q<j).
\]

Every `k_i=a` and every `d_i=j-1-a`. Hence every `t_i=j-1`, and

\[
\boxed{\#\text{ dyadic roots}=
\begin{cases}
0,&\delta<j-1,\\
j,&\delta\ge j-1.
\end{cases}} \tag{5.5}
\]

Here only positive wall distances are considered; at `j=1` the second case always applies. This is an infinite exact family, proved without extrapolating finite tests.

### Corollary 5.3. The boundary and pre-wall range

For a regular wall, the classification also closes the start of the family. If `2^L>j` and `L<L_j`, then `J_r={0}`, `mu_r=0`, and `G_r` is a restricted analytic unit. There are no dyadic roots and the remainder valuation is exactly the first omitted term weight.

At `L=L_j`, there are two minimum layers, `J_r={0,j}`, and `mu_r=0`. The reduction is

\[
\overline G_r(X)=1+X^{\underline j}.
\]

For `j>=2`, the falling product contains `X(X-1)`, so the reduction takes the value one at both residues. Consequently `v_2G_r(x)=0` for every `x in Z_2`, and there are no roots. For `j=1`, the reduction is `1+X`; there is one simple root in the odd class. Thus Theorem 5.1 extends to `delta=0`, with its `j=1` convention, and the negative-distance range is root-free.

The separate checker `check_wall_boundary_v4.py` verifies the minima at every pre-wall scale for regular `j<=32`, and computes complete coefficient certificates at the equality scales. The proof above, rather than extrapolation, covers all regular wall labels.

## 6. The five-root family is completely resolved

For `j=5`,

\[
(e_5(0),\ldots,e_5(4))=(0,2,6,9,13),\qquad L_5=17.
\]

Thus `r=2^(17+delta)-5`, `M=r-1`, `mu_r=-delta`, and the wall is regular.

| Skeleton `i` | `d_i` | `k_i` | Ball `B_i` | Exact emergence distance `t_i` |
|---:|---:|---:|---|---:|
| 0 | 3 | 3 | `0 mod 8` | 6 |
| 1 | 1 | 2 | `1 mod 4` | 3 |
| 2 | 2 | 2 | `2 mod 4` | 4 |
| 3 | 1 | 2 | `3 mod 4` | 3 |
| 4 | 3 | 3 | `4 mod 8` | 6 |

These five balls partition `Z_2`. The exact root counts are therefore

| Wall distance `delta` | 1 | 2 | 3 | 4 | 5 | 6 and above |
|---|---:|---:|---:|---:|---:|---:|
| Number of roots | 0 | 0 | 2 | 3 | 3 | 5 |

The earlier v3 sufficient stages `3,5,7` must not be read as sharp. The sharp stages are **3,4,6**. At the equality wall `delta=0` and throughout the valid pre-wall range there are no roots, by Corollary 5.3.

For `x=N-r`, the original nonempty tail satisfies

\[
\boxed{v_2\mathcal T_{r-1}(N)
=4r-1+v_2\binom Nr-\delta+
\begin{cases}
\delta,&x\in B_i,\ \delta<t_i,\\
d_i+v_2(x-\alpha_i),&x\in B_i,\ \delta\ge t_i.
\end{cases}} \tag{6.1}
\]

This is valid at every admissible row, not only near the first omitted row.

### Executed example at `delta=6`

Here `r=8,388,603`. All five roots are present. The following residues are certified modulo `2^16`; the actual roots are dyadic numbers, not these finite integers.

| Skeleton | Root residue modulo `65536` |
|---:|---:|
| 0 | 47240 |
| 1 | 39521 |
| 2 | 21714 |
| 3 | 60643 |
| 4 | 50028 |

The calculation used 64-bit coefficient precision. Because the derivative has valuation `d_i`, a root generally has `64-d_i` certified bits. Full precision metadata is retained in the JSON, and no 64-bit claim is made for every root.

At `x=0,...,12`, the exact values of `v_2G_r(x)` are

\[
6,6,6,6,6,3,4,3,10,4,5,4,8.
\]

For example `x=8` is in `B_0`; the root residue gives `v_2(8-alpha_0)=7`, hence `v_2G_r(8)=3+7=10`. The original unfactored tail calculation agrees after normalization.

The monic degree-five polynomial carrying the same valuations begins, modulo `256`, as

\[
W_r(X)\equiv X^5+246X^4+35X^3+206X^2+152X+192\pmod{256}.
\]

These eight-bit coefficients are a displayed check, not sufficient by themselves to establish the more precise root residues.

## 7. The first irregular wall: a finite complete certificate

At `j=17`,

\[
L_{17}=53,\qquad e_{17}(0)=e_{17}(1)=0.
\]

Thus `V mod 2=1+X`, rather than the unit reduction required by Theorem 5.1. The regular-wall formula must not be used here.

Nevertheless the general separation theorem guarantees all seventeen simple roots for

\[
\delta\ge v_2(16!)+\lceil\log_2 17\rceil=15+5=20.
\]

Only the finite prefix `delta=1,...,19` remains. For each such distance, and also for distance twenty as an endpoint check, the code produces a disjoint covering by balls `s+2^k Z_2`. Every leaf has a coefficient certificate of one of the two forms

\[
2^{-c}G_r(s+2^kY)\equiv1\pmod2, \tag{7.1}
\]

or

\[
2^{-c}G_r(s+2^kY)\equiv Y+\epsilon\pmod2. \tag{7.2}
\]

Case (7.1) proves that the exact valuation is `c` everywhere on the ball. Case (7.2), by Lemma 4.3, proves a unique simple root `alpha` on the ball and the exact law

\[
v_2G_r(x)=c-k+v_2(x-\alpha).
\]

The recorded polynomials are correct coefficientwise at a precision strictly beyond `c`; the rigorous cutoff in Section 9 controls the infinite analytic remainder. This is why these are whole-ball certificates rather than a collection of sampled values.

The executed root counts are:

| `delta` | 1–10 | 11–12 | 13 | 14–15 | 16 | 17 | 18–19 | 20 and above |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Roots | 1 | 2 | 4 | 8 | 12 | 14 | 15 | 17 |

The JSON `first_irregular_wall` records all **163 leaf certificates** for distances one through twenty, with addresses, contents, polynomial reductions, root residues, and precision. There are no unresolved leaves. For larger distances Theorem 4.4 supplies the result. Together these establish the classification at every positive distance in this family.

The pre-wall and equality scales for seventeen also close. For `5<=L<53`, `J_r={0,1}` and `G_r mod 2=1+X`, so there is exactly one odd simple root. At `L=53`, the reduction becomes

\[
1+X+X^{\underline{17}}.
\]

Its only root in the residue field is `X=1`, and its derivative there is one. Hence this equality scale again has exactly one odd simple root. The boundary checker verifies all scales `L=5,...,53` with coefficient certificates and original-tail comparisons.

Every `j` from one through thirty-two other than seventeen satisfies (5.1). This can be seen directly: for `j>=2`, `e_j(1)=4-v_2(j-1)`, and the only nonpositive case in this range is `j=17`; for `q>=2`, the digit-sum bound makes `e_j(q)` positive. The case `j=1` is vacuous.

Consequently Theorem 5.1, Corollary 5.3, and the seventeen-wall certificates cover every shifted-wall family with `1<=j<=32`, at every integer scale satisfying `2^L>j`, including pre-wall and equality scales. This statement concerns those wall families, not every possible first omitted index `r`.

## 8. Every depth has a finite polynomial controlling the exact tail

### Theorem 8.1. Constructive finite-degree preparation

For every `r>=1`, put `d_r=max J_r`. There are unique factors

\[
G_r(X)=W_r(X)U_r(X),
\]

where `W_r in Z_2[X]` is monic of degree `d_r`, and `U_r in Z_2<X>` is a unit with `U_r mod 2=1`. In particular

\[
\boxed{\deg W_r=d_r\le\left\lfloor\frac{s_2(r)-1}{3}\right\rfloor,} \tag{8.1}
\]

and

\[
\boxed{v_2\mathcal T_{r-1}(N)
=4r-1+v_2\binom Nr+\mu_r+v_2W_r(N-r).} \tag{8.2}
\]

This is a specialization of one-variable Weierstrass preparation [S3]. The following proof also gives the implemented coefficient algorithm.

**Constructive proof.** Let `g=G_r mod 2`, which is monic of degree `d_r` by (2.5). Start with its zero-one lift `W_1=g`, `U_1=1`. Suppose monic `W_k` of degree `d_r` and polynomial `U_k` satisfy

\[
G_r-W_kU_k\in2^k\mathbb Z_2\langle X\rangle.
\]

Reduce the divided error modulo two. It is an ordinary polynomial, since the series is restricted. Divide it in `F_2[X]` by `g`:

\[
\overline{(G_r-W_kU_k)/2^k}=gq+s,\qquad\deg s<d_r.
\]

Lift `q,s` with zero-one coefficients and set

\[
W_{k+1}=W_k+2^ks,\qquad U_{k+1}=U_k+2^kq.
\]

The new error is divisible by `2^(k+1)`. The leading coefficient of `W_k` remains one and its degree remains fixed. Both sequences are Cauchy in the Gauss norm. Completeness produces the required finite polynomial `W_r` and restricted series `U_r`. The latter reduces to one and is therefore invertible. Uniqueness follows from uniqueness of quotient and remainder at each binary digit, or by comparing two factorizations modulo successive powers of two. At degree zero take `W_r=1`, `U_r=G_r`.

The bound (8.1) follows from (2.4); (8.2) follows since a restricted integral unit takes unit values at every dyadic argument.

### Corollary 8.2. Finite valuation descriptions exist at every depth

Every fixed `r` has finitely many dyadic roots, at most `d_r` when multiplicities are counted. On a sufficiently small ball around a root `alpha` of multiplicity `e`,

\[
v_2W_r(x)=c+e\,v_2(x-\alpha).
\]

Outside disjoint root neighborhoods, compactness gives a finite partition into balls on which `v_2W_r` is constant. Indeed the root-free quotient is continuous and nonzero near each root, while the complement is compact and root-free.

This proves existence of a finite exact valuation description for every depth. It does **not** say that a fixed-precision computation can decide a repeated root, or that the current simple-root splitter always terminates on every input. The implementation reports unresolved precision/depth leaves instead of promoting them to results. An explicit arithmetic classification of all remaining irregular polynomials is not supplied here.

## 9. Exact computation without constructing enormous Bernoulli numbers

### 9.1 A precision-local Bernoulli identity

The generating-function identity

\[
e^t\frac{2t}{e^{2t}-1}
=\frac{2t}{e^t-1}-\frac{2t}{e^{2t}-1}
\]

implies, for positive even `n`,

\[
(1-2^{n-1})\,2B_n
=\sum_{k=0}^n\binom nk2^kB_k.
\]

Since `v_2(B_k)>=-1`, every term with `k>=P+1` is zero modulo `2^P`. The factor on the left is odd. Thus

\[
\boxed{2B_n\equiv(1-2^{n-1})^{-1}
\sum_{k=0}^{\min(n,P)}\binom nk2^kB_k\pmod{2^P}.} \tag{9.1}
\]

Only `B_0,...,B_P` are needed, even when the index `n` is enormous. Formula (9.1) is derived here from the classical Bernoulli finite-expansion and multiplication identities [S2], and is not asserted to be historically new.

The independent power-sum check uses, for `h=P+1`,

\[
2B_n\equiv2^{1-h}\sum_{a=0}^{2^h-1}a^n\pmod{2^P}.
\]

Faulhaber's expansion proves the error estimate. Since `n` is even, `n+1` is odd; after removing the leading `2B_n`, every term has valuation at least `h-1`. The finite sum is computed modulo `2^(P+h-1)` before exact division by `2^(h-1)`.

### 9.2 Kernel coefficients and a complete tail cutoff

The normalized coefficient in `G_r` can be computed by

\[
2^{-\mu_r}8^q\frac{\beta_{r+q}}{\beta_r}
=2^{5q-\mu_r}\frac{2r+2q-1}{2r-1}
\frac{2B_{2r+2q}}{2B_{2r}}
\frac{(2r)!}{(2r+2q)!}. \tag{9.2}
\]

Strip powers of two from the finite product `(2r+1)...(2r+2q)` before modular inversion. The exact resulting power is `lambda_r(q)-mu_r`, and every remaining denominator is odd.

For coefficient precision `P`, it suffices to retain

\[
0\le q\le Q=\max\left(0,\left\lfloor
\frac{P+s_2(r)+\mu_r-2}{3}\right\rfloor\right). \tag{9.3}
\]

Indeed for `q>=Q+1`,

\[
\lambda_r(q)-\mu_r\ge3q+1-s_2(r)-\mu_r\ge P.
\]

Thus all omitted terms vanish coefficientwise. Affine substitutions by integral addresses preserve coefficientwise precision.

Formula (2.1) computes the source polynomial modulo `2^P`. For `log9/8`, terms have valuation `3h-3-v_2(h)`; for the main source sum, valuation `3k-v_2((k+1)!)`; and the geometric inverse has coefficient valuation equal to its degree. These bounds justify the finite loops in the code.

### 9.3 Independent original-tail evaluation

`original_normalized_tail` uses the original `kappa_m`, the binomial complement `binom(2N,2(x-q))`, and a modular-power source calculation. It does not use the factorial cancellation defining `P_q`. Precision is increased before dividing by the valuation of the prefactor. Both this path and (9.2) use (9.1), whose Bernoulli residues are independently checked against exact small-index rationals and finite power sums at large indices.

## 10. Executed audit and reproduction

Run with standard Python; no third-party numerical library is required:

```text
python check_completion_v4.py
```

The retained run completed in **10.334768 seconds** with exit status zero. All scientific arithmetic is exact rational or modular integer arithmetic. Floating point is used only for elapsed-time metadata; infinity is a sentinel for the valuation of zero.

Selected executed checks:

| Check | Count or range |
|---|---:|
| Full Euler reconstruction, independent inverse and Euler recurrence | `N=0,...,128`, 129 rows |
| Every nonempty rational tail in those rows | 8,256 |
| Bernoulli residues against exact rational coefficients | 640 |
| Large-index Bernoulli residues against finite power sums | 64 |
| Source series against modular powers, including negative arguments | 363 |
| Five-wall original unfactored-tail checks | 483 |
| Seventeen-wall original unfactored-tail checks | 660 |
| Five-wall sampled checks against the certified valuation atlas | 28,672 |
| Five-wall whole-ball certificates | 28 |
| Regular-wall whole-ball certificates | 11,969 |
| First-irregular-wall whole-ball certificates | 163 |
| Arbitrary-depth finite polynomial preparations | 75 |
| Prepared-polynomial versus full-series valuation checks | 4,875 |

The general separating-ball scales were separately checked at 8,255 skeleton points for `2<=j<=128`, and the maximum-scale identity at 127 values of `j`. All counts and all certificate data are in `RESULTS_COMPLETION_04.json`.

A separate boundary-closure run completed in **0.352971 seconds**, with 1,513 pre-wall minimum checks, 111 whole-ball boundary/pre-wall certificates, and 1,280 additional original-tail comparisons. Its results, manifest, and log are retained under the `BOUNDARY_04` names.

A finite coefficient certificate with a proved omitted-term bound proves its corresponding whole-ball statement. The sampled comparisons are implementation checks, not independent universal proofs. Larger untested domains are covered only where an explicit theorem above applies.

## 11. Boundaries, corrections, and preserved history

The five-root family is now completely classified at every valid shifted-wall scale and every argument, including the pre-wall and equality scales. The regular-wall theorem and all power-of-two skeleton corollaries are universal. The first irregular wall is covered by its finite certificates and the all-large-distance theorem. These together cover all shifted-wall labels up to thirty-two.

Every arbitrary depth has an exact finite-polynomial valuation reduction, but its root geometry is not explicitly classified here. In particular, neither simplicity of every root at arbitrary depth nor automatic resolution of every multiple root is asserted.

The optimal uniform exponent `4M+3` is unchanged. Extra root-distance gains are row-specific and do not increase a bound required to hold at the first omitted row.

Historical files from v1–v3 are preserved. Their retained logs are not claimed to have all been rerun in v4. This continuation reruns its own exact construction and the declared checks. No Lean compilation or priority review was performed.

## Sources for classical inputs

[S1] NIST Digital Library of Mathematical Functions, Section 24.10(i), equation 24.10.1, von Staudt–Clausen denominator theorem. https://dlmf.nist.gov/24.10

[S2] NIST Digital Library of Mathematical Functions, Section 24.4, finite Bernoulli expansions, power sums, and multiplication formulas. https://dlmf.nist.gov/24.4

[S3] Keith Conrad, *Hensel's Lemma*, Theorem 8.2 and Remark 8.3, printed pages 16–17: restricted power series Hensel lifting and Weierstrass preparation. https://kconrad.math.uconn.edu/blurbs/gradnumthy/hensel.pdf

The general wall thresholds and specialized Euler-tail formulas proved above should not be attributed to these classical references. They are the deductions of this continuation from the stated inputs.
