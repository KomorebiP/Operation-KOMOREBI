# Euler wall resolution XII: nearest neighbors, quadratic–cubic cores, and terminal 514

**Operation Komorebi — 3 October 2026 — continuation v12**

## Status and boundaries

This continuation strengthens v11's degree estimate at a slope match. For an
actual terminal label j>=4 whose lower reduction has only simple F_2 roots,
every still-candidate skeleton ball has an exact normalized prepared degree
at most THREE. One closest integer neighbor forces a quadratic. Two closest
neighbors give either an already resolved constant/affine reduction or a cubic.
The result is independent of the size of j, the odd multiplier, and the wall
scale, subject to the inherited true-terminal hypothesis.

A general cubic core has one exact inflection point. Its derivative has an
exact square coordinate. These facts reduce its possible repeated roots to
explicit critical-value tests. They do NOT prove those values nonzero for all
Euler families. A synthetic terminal-form example with a simple lower reduction
has an exact triple root, proving that the degree-three upper bound is sharp
under these analytic hypotheses. It is not an Euler-prefix counterexample.

The strict address-two Euler family j=514 is now completely classified at ALL
admitted odd multipliers and all distances. The inherited lower-routing theorem
reduces its outstanding question to delta=503. Two independently checked local
quadratic certificates settle that distance using b modulo 4.

A separate small certificate excludes triple roots at every admitted terminal-161
depth. This is a compact all-parameter third-order nondegeneracy test, not a
solution of its remaining possible double-root progression.

The inherited consecutive all-parameter terminal-degree guarantee remains 128,
and the sufficient digit-sum guarantee remains s_2(r)<=646. Neither the two
terminal-129 progressions nor the remaining terminal-161 progression is closed
here. No universal Euler simplicity, all-label degree-three assertion for
MULTIPLE lower residue roots, algebraic squarefreeness, Lean compilation, or
historical-priority claim is made.

## 1. Exact inherited setting

For an actual first omitted depth r whose last global minimizing carry packet is j,

\[
r=b2^{L_j+\delta}-j,\quad b>0\text{ odd},\quad\delta\ge0,
\]
\[
G_r(x)=P_j(x)U(x-j)+2^\delta V_r(x),\qquad
P_j(x)=\prod_{0\le h<j}(x-h)(2x-2h-1).
\]

Here U is an integral restricted analytic unit, and V_r is the integral lower
prefix. U and V_r are the exact functions for that r; they are not assumed fixed
while b or delta changes. The whole nonempty Euler tail satisfies

\[
v_2\mathcal T_{r-1}(N)=4r-1+v_2\binom Nr+E_j-\delta+v_2G_r(N-r),\quad N\ge r.
\]

For 0<=i<j, put

\[
k_i=\operatorname{bitlength}(\max(i,j-1-i)),\quad
 d_i=v_2(i!)+v_2((j-1-i)!),\quad t_i=d_i+k_i.
\]

The balls i+2^{k_i}Z_2 partition Z_2. Assume every F_2 root of bar V_r is simple.
Then there are at most two lower roots, on different parities. V11 proves that
all balls/scales are resolved except possibly a ball containing a lower root
beta, with delta=d_i and z=(beta-i)/2^{k_i} even. On this candidate ball,

\[
G_r(i+2^kY)=2^{d+k}\{Y A(Y)+(Y-z)B(Y)\},
\quad A,B\in\mathbf Z_2\langle Y\rangle^\times,\quad\bar A=\bar B=1.
\]

Consequently, writing R=A/B,

\[
G_r(i+2^kY)=2^{d+k+1}B(Y)H(Y),\qquad
H(Y)=\frac{Y(1+R(Y))}{2}-\frac z2.                       \tag{1}
\]

The slope-routing and lower-coefficient stability proofs are preserved in
history/Komorebi_Euler_Slope_Walls_v11/PROOF_AND_STATUS.md. Their universal
quantifiers depend on the true last-global-minimum condition. The actual Euler
labels <=3 are already handled by the inherited results. The general theorem
below uses j>=4 so that every separating depth k is at least two.

## 2. An exact nearest-neighbor factorization

Let

\[
\mathcal N_i=\{h\ne i:0\le h<j,\ v_2(i-h)=k-1\}.
\]

**Lemma 1.** This set has one or two elements, and its elements are exactly the
admitted points i-2^{k-1} and i+2^{k-1}. On the candidate ball,

\[
R(Y)=r_0\,N_i(Y)\,E(Y),\qquad r_0\in\mathbf Z_2^\times,
\quad E(Y)=1+\sum_{m\ge1}4^m e_mY^m,\ e_m\in\mathbf Z_2,    \tag{2}
\]

where

\[
N_i(Y)=
\begin{cases}
1+2\epsilon Y,&|\mathcal N_i|=1,\ \epsilon\in\{1,-1\},\\
1-4Y^2,&|\mathcal N_i|=2.
\end{cases}
\]

**Proof.** All ordinary distances |i-h| are strictly below 2^k. At least one
is at least 2^{k-1}, and the corresponding point at distance exactly 2^{k-1}
is still in the interval. A distance with valuation k-1 must therefore equal
plus or minus 2^{k-1}. There are no other possibilities.

After removing the isolated root Y, the factor contributed by h is

\[
1+\frac{2^k}{i-h}Y.
\]

The closest factors are exactly 1+2Y and/or 1-2Y. Every other integer-skeleton
factor has linear coefficient divisible by four. The odd-companion factors
have linear coefficient divisible by 2^{k+1}. Their products, after constants
are divided out, have coefficient of degree m divisible by 4^m.

The evaluated restricted unit U has coefficient of degree m divisible by
2^{km}. The same is true of B(Y)/B(0). To see the latter, expand V_r at its
simple root beta and divide by 2^k(Y-z); translating by the integral z
preserves this weighted bound. Since k>=2, these unit series and their inverses
have the required 4^m bound. Products preserve the bound. Dividing all odd
constant factors into r_0 proves (2). QED.

This is stronger than merely knowing v_2([Y^m]R)>=m. It retains the fact that
there can be only two closest skeleton factors and that, when both occur,
they form the EXACT symmetric product 1-4Y^2.

## 3. Uniform quadratic–cubic core theorem

**Theorem 2.** Under the setting in Section 1, let c be the additional Gauss
content of H in (1), and let F be G on this ball divided by its FULL content.
Then:

1. With one closest neighbor, c=0, the full content is t_i+1, and the prepared
   degree is exactly two. Moreover
   \[
   F(Y)=a_0+a_1Y+a_2Y^2+\sum_{n\ge3}a_nY^n,\quad a_2\text{ odd},
   \quad v_2(a_n)\ge2n-4\ (n\ge3).                         \tag{3}
   \]
2. With two closest neighbors, c is either 0 or 1. If c=0 the reduction is
   constant or affine and is already resolved. If c=1, the full content is
   t_i+2, the prepared degree is exactly three, and
   \[
   F(Y)=a_0+a_1Y+a_2Y^2+a_3Y^3+\sum_{n\ge4}a_nY^n,
   \quad a_3\text{ odd},\quad v_2(a_n)\ge2n-6\ (n\ge4).    \tag{4}
   \]

In the two-neighbor case c=1 occurs exactly when z is divisible by four and
r_0 is 3 modulo four. These are tests on exact local coordinates; finite
certificates need only the displayed residue bits.

**Proof.** If N_i=1+2epsilon Y, the coefficient of Y in R is
r_0(2epsilon+E_1), where E_1 is divisible by four. Thus the coefficient of
Y^2 in H is odd. For n>=3, its coefficient has valuation at least 2n-4.
The content is zero and the last odd coefficient is the quadratic one.

If N_i=1-4Y^2, then R_1 is divisible by four and

\[
R_2=r_0(E_2-4),\qquad v_2(R_2)=2.
\]

So H_2 is even and H_3 has exact valuation one. For n>=4, H_n has valuation
at least 2n-5. Its constant is -z/2 and its linear coefficient is (1+r_0)/2.
If either is odd, c=0 and the reduction has degree at most one. If both are
even, the cubic coefficient forces c=1, giving exactly degree three and the
bounds after division by two.

Multiplication by B in (1) does not change content or prepared degree, since
bar B=1. It also preserves (3) and (4): its degree-m coefficients have valuation
at least km>=2m, and a product coefficient has the stated bound term by term.
This proves the assertions for the fully normalized G, not only for H. QED.

### Multiplicity consequences

At every such Euler slope match the prepared degree is <=3. All other balls
have only simple roots or no roots by v11. Therefore any repeated dyadic root
has multiplicity exactly two or three. A quadratic/cubic box can contain at
most one repeated root: two double roots would already require degree four.
There are at most two candidate boxes for a fixed residual, so at most two
repeated-root locations are possible under these hypotheses.

This statement is about the separated skeleton coordinates and a SIMPLE lower
residue. It does not assert that a coarser ball has degree <=3. The earlier
quartic reductions at coarser scales are compatible with this theorem. It also
does not cover a lower reduction that itself has a multiple F_2 root.

The prepared-degree/multiplicity step uses one-variable Weierstrass preparation;
its unit factor preserves zeros and multiplicities [S1]. The nearest-factor
coefficient argument above is the additional structure particular to this
terminal skeleton setting.

## 4. The cubic has one inflection coordinate and two critical-value tests

Let F have the cubic form (4). Its half-second derivative satisfies

\[
F''(Y)/2=a_2+3a_3Y+4R_2(Y),
\]

where the degree >=2 coefficients of the correction are even; the exact
linear coefficient is odd. It is an isometric bijection, so it has a unique
zero rho in Z_2. Let

\[
C=F(\rho),\qquad A=F'(\rho),\qquad u=F^{[3]}(\rho)\in\mathbf Z_2^\times.
\]

Translation preserves the coefficient bounds, and

\[
F(\rho+Z)=C+AZ+uZ^3+4Z^4S(Z).
\]

More precisely, coefficients at degree n>=4 still have valuation >=2n-6.
The derivative consequently has the stronger form

\[
F'(\rho+Z)=A+3uZ^2(1+16Z R(Z)).
\]

The square-root series converges and belongs to 1+8Z Z_2<Z>. Define

\[
\Psi(Z)=Z\sqrt{1+16ZR(Z)}.
\]

It is an analytic isometric bijection. Therefore

\[
\boxed{F'(\rho+Z)=A+3u\Psi(Z)^2.}                         \tag{5}
\]

This is an exact square normal form for the DERIVATIVE of the cubic core.
The binomial square-root terms have valuations at least 2m+1; this justifies
both restricted convergence and the unit derivative of the coordinate map.

Put chi=-A/(3u). If chi is nonsquare, there is no dyadic critical point and
all dyadic roots of F are simple. If chi is a nonzero square, there are two
simple critical points, and a repeated zero exists precisely if F vanishes
at one of those points. Such a zero is double. If chi=0, the only critical
point is rho and it has derivative multiplicity two; F has an exact triple
zero precisely when

\[
\boxed{A=C=0.}                                            \tag{6}
\]

Thus no fourth-order condition can remain in this class. These are exact
critical-value tests, not a proof that Euler critical values never vanish.

For comparison, a quadratic core (3) has no critical point if a_1 is odd.
If a_1 is even, F'/2 is an isometric bijection and has one critical point;
its critical value decides whether an exact double zero occurs.

### The degree-three bound is sharp under the analytic hypotheses

Take j=5, U=1, delta=2, and the SYNTHETIC lower polynomial

\[
V(x)=-162+117x-18x^2.
\]

Its reduction is X, so its lower residue is simple. Direct exact expansion gives

\[
(P_5+4V)(2+Z)=1025Z^3-410Z^4-1365Z^5+\cdots.
\]

There is an exact triple zero at x=2. On 2+4Z_2 the content is six and the
prepared degree is three, attaining Theorem 2. This is not the Euler lower
prefix for that label. It refutes only a generic claim that the terminal
normal-form hypotheses alone exclude triple roots.

A one-neighbor sharp control is j=4, delta=1, U=1, V=15(x-1). The function
P_4+2V has an exact double zero at x=1 with quadratic Taylor coefficient 47.

## 5. A compact exact non-triple certificate at terminal 161

V11 isolated the only possible distance at delta=153, in the skeleton ball
90+128Z_2. Here d_i=153, k_i=7, t_i=160, and the two nearest points are 26,154.
The new theorem therefore allows only an affine state or a cubic state.

New 256-bit local coefficients were compared with the independently saved
224-bit global v11 coefficients. They give these WHOLE-parameter congruences:

* b=1+4t: 2^(-161)bG(90+128Y) = Y modulo 2.
* b=3+8t: 2^(-162)bG(90+128Y) = Y^3+Y modulo 2.
* b=7+8t: putting F=2^(-162)bG(90+128Y),
  \[
  F(Y)=4+(2+6t)Y+6Y^2+Y^3\pmod8.                         \tag{7}
  \]

All multipliers must be actual positive integers with the stated last global
minimum. The finite template is used only at its proved coefficient precision.
The three classes partition the odd multipliers.

The first class is already simple. In the second, the unique cubic inflection
rho is even and F'(rho) is odd, so a triple root is impossible.
For the last class,

\[
F''(Y)/2=6+3Y\pmod8,\qquad\rho=6\pmod8.
\]

Substitution yields

\[
F(\rho)=4t\pmod8,\qquad F'(\rho)=2+2t\pmod4.
\]

If t is even, the second quantity has exact valuation one. If t is odd, the
first has exact valuation two. They cannot both vanish. This rules out triple
roots for every admitted terminal-161 multiplier, without resolving all the
quadratic square classes. The prior remaining possible double-root progression
b=17659+2^18 T is NOT closed here.

## 6. Complete all-distance classification at terminal 514

This is the first strict address-two family. The inherited and independently
recomputed lower routing data are

\[
E_{514}=-1,\quad I_{514}=\{2\},\quad L_{514}=1546,
\quad r_b=b2^{1546+\delta}-514.
\]

The lower reduction is X(X+1), with two simple residues. At precision 2^12 the
lower roots are 2278 and 2483. Their skeleton data are

| i | k_i | d_i | (beta-i)/2^k_i modulo 4 | closest integer neighbor |
|---:|---:|---:|---:|---:|
|230|9|503|0|486|
|435|9|503|0|179|

Thus delta=503 is the ONLY potentially difficult distance. Each candidate box
has one closest neighbor, so Theorem 2 forces prepared degree two immediately.
No cubic or higher multiplicity is possible in these two boxes.

### Uniform critical certificates

At delta=503, r_b=b2^2049-514 and mu=-504. Write b=1+2t and define

\[
F_{a,b}(Y)=2^{-513}bG_{r_b}(a+512Y),\qquad a=230,435.
\]

The independently rechecked coefficient certificates are

\[
\boxed{F_{230,b}(Y)=Y^2+3(1+t)Y+2\pmod4,}                 \tag{8}
\]
\[
\boxed{F_{435,b}(Y)=3Y^2+3(1+t)Y+2\pmod4.}                \tag{9}
\]

These hold on whole parameter/argument balls, not just at sampled integers.
When t is even (b=1 mod4), both reduce to Y^2+Y and each has two simple roots.
When t is odd (b=3 mod4), the only possible residue is even; at even Y the
value is exactly 2 modulo4. Neither box has a root. No other skeleton ball
contains a root at delta=503 by the lower-routing thresholds. Therefore

\[
\boxed{\#\text{roots at }\delta=503=
4\text{ for }b=1\pmod4,\quad0\text{ for }b=3\pmod4.}     \tag{10}
\]

The eight saved constant/affine child certificates refine the two quadratic
boxes and the two parameter classes. Every saved simple leaf has content 514
and original x-depth ten, hence derivative order 504.

In the splitting class the root balls are

\[
230,\ 742,\ 435,\ 947\pmod{1024}.
\]

Their next digits, as verified from the coefficient identities, are

| b mod8 | root residues mod2048 |
|---:|---|
|1|1254,1766,1459,947|
|5|1254,742,1459,1971|

These are finite root residues, not asserted exact integer roots.
On each of those balls,

\[
v_2G_{r_b}(x)=504+v_2(x-\alpha).
\]

Thus for the indicated nonempty Euler rows,

\[
\boxed{v_2\mathcal T_{r_b-1}(N)=4r_b-1+v_2\binom N{r_b}
       +v_2(N-r_b-\alpha).}                               \tag{11}
\]

The old optimal uniform exponent 4r_b-1 is unchanged.

### All other distances and the full table

The two lower-root boxes each contribute one root whenever delta!=503. Each
other skeleton ball contributes exactly when delta+s_i>=t_i. The 512 other
thresholds are computed from the same twelve-bit lower certificate. Their
minimum is 504 and maximum is 520. The complete result is

| delta | number of dyadic roots |
|---:|---:|
|0..502|2|
|503|4 for b=1 mod4; 0 for b=3 mod4|
|504|4|
|505|8|
|506|16|
|507|32|
|508|64|
|509|128|
|510..511|256|
|512|384|
|513|448|
|514|480|
|515|496|
|516|504|
|517|508|
|518..519|510|
|520 and above|514|

Every listed root is simple, for ALL admitted positive odd multipliers.
The all-distance assertion is the v11 routing theorem plus (8)-(9), not an
extrapolation from a finite window. The first strict address-two case is now
fully resolved. The earlier j=258 equality case remains distinct: it has the
extra constant lower packet and no early roots.

### Coefficient and parameter precision contract

The critical base is the actual b=1 residual at delta=503, computed at P=544.
Its last minimizing packet is 514 and mu=-504. The global cutoff is Q=695.
The v11/v6 two-polynomial template applies at L=2049: the size inequalities and
L+1-ceil(log_2(2(j+2P)+1))>=P hold with a large margin. On either parity ball,

\[
bG_{r_b}\equiv bG_{r_1,<514}+G_{r_1,\ge514}\pmod{2^{544}}.
\]

True terminality guarantees integrality of all normalized coefficients,
including remotely indexed packets of other multipliers. Removing local content
513 leaves 31 coefficient bits, far more than the two bits used by (8)-(9).
The eight normalized child leaves retain at least 30 bits.

The local assembly drops Y-degrees above floor((P-1)/k), because integral global
coefficients acquire 2^{km} after x=a+2^kY. The verification does not infer any
coefficient assertion from values at sample points.

## 7. Scope that has not been promoted

The all-label quadratic–cubic theorem is conditional on simple lower F_2 roots.
It does not yet supply a nonvanishing theorem for every quadratic/cubic critical
invariant. The strongest new assertion is a UNIFORM small prepared degree on
separated collision balls, not universal simplicity.

The two terminal-129 progressions remain open. The terminal-161 progression
remains open for possible double roots; the new eight-bit test only excludes
triples. The inherited all-parameter consecutive degree bound remains 128,
and the sufficient s_2(r)<=646 bound remains unchanged. Terminal 514 is a new
complete higher family, not a claim of completeness at every degree below 514.

A generic double/triple counterexample shows why one cannot finish by using
only integral units, slope matching and degree bounds. Exact Euler coefficient
relations must still exclude the remaining critical-value zeros, or classify
one if it actually occurs. Nothing here establishes an actual repeated Euler root.

## 8. Executed evidence

All 1007 tracked incoming v11 manifest entries matched. The preserved v11
lower-routing verifier replayed its 84 exact-rational lower packets and 150
retrospective phase-count comparisons. No claim is made that every historical
scientific checker was rerun.

New retained evidence includes:

* 18,522 skeleton balls and 2,359,224 integer-factor valuation checks.
* 960 weighted nearest-neighbor normal forms and 612 complete synthetic
  terminal-form slope collisions. All four prepared degrees 0,1,2,3 occurred.
* 80 cubic derivative square charts, with their squared identities checked
  coefficientwise; 480 additional value checks. The exact synthetic double
  and triple controls are saved explicitly and labeled non-Euler examples.
* Terminal 514: 696 normalized scalar coefficients independently recomputed
  through a DIFFERENT rising-factorial/odd-lane factorization; 390 nonzero
  source-packet terms independently rebuilt from the GLOBAL logarithmic source.
  The Bernoulli unit evaluator is shared in this scalar cross-check. The small
  routing polynomial is independently reconstructed with rational Bernoulli
  arithmetic (seven packets). No stronger independence claim is made.
* All eight uniform critical leaves, their coverings, root residues, and the
  512 noncollision thresholds were independently verified. The 522 recorded
  distances corroborate the closed root-count rule, whose infinite tail is
  justified by the maximum threshold.
* Six original-index 514 residuals at P=576 supplied twelve local coefficient
  comparisons, thirty-six finite packet-product values, and twenty-eight
  independently verified resolution-tree nodes. Actual multipliers include
  2^120+5 and 2^60+3.
* Terminal 161: three complete paired congruences checked against a different
  224-bit global source; eight original-index reconstructions at P=288, with
  twenty-four finite packet-value comparisons and seven cubic critical-jet tests.
  These are evidence for the finite certificates, not a substitute for the
  uniform coefficient error and nearest-neighbor theorems.

All retained new scientific runs completed and passed. No timeout or failed
mathematical assertion occurred in these retained runs. No Lean compilation or
historical-priority assessment was performed.

## 9. Reproduction

Python 3.10+ and only the standard library are required. Use fresh output names:

```text
python code/audit_core_theorem.py --output results/recheck_core.json
python code/verify_terminal514.py --output results/recheck_514.json
python code/verify_cubic161.py --output results/recheck_161.json
python code/verify_manifest.py
```

Generators refuse to overwrite their outputs. `check_actuals.py` also creates
fixed ACTUAL514 case files, so run it on a copy and remove only the copied case
files when reproducing the original-index experiment.

## Sources and provenance

[S1] Keith Conrad, Hensel's Lemma, Theorem 8.2 and Remark 8.3, restricted-series
lifting and one-variable Weierstrass preparation. Official author notes read in
this run: https://kconrad.math.uconn.edu/blurbs/gradnumthy/hensel.pdf .

[S2] Unmodified v11 PROOF_AND_STATUS.md, Sections 2–6: skeleton partition, slope
matching, averaged-unit transform and lower-root routing. Its full source and
nested history are preserved here.

[S3] Inherited v8/v2 exact modular engine: Bernoulli coefficients, original
source, scalar cutoffs, original packet-value evaluator, and local source
constructor. All current new construction/verification code is in code/.

The nearest-neighbor coefficient reduction, conditional quadratic–cubic degree
bound, cubic critical normal form, and the particular 514 and 161 certificates
are derived here. Classical inputs are not cited as claims of priority for these
specialized deductions.
