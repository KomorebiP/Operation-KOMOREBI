# Komorebi RH v0.14.0 — prime-cube parity barrier

## Status

The Riemann hypothesis is **not proved** in this tranche.

This push tested the strongest remaining use of the certified prime-toggle machinery: iterate a growing squarefree prime cube, pass to its exact alternating mixed difference, and attempt to obtain the missing square-root cancellation without estimating the residual Möbius signs directly.

The attempt produces a rigorous obstruction theorem:

> Any prime-cube argument that discards the remaining rough-base Möbius signs by absolute values remains on the `K^{-1/2}` scale. The RH/Báez–Duarte target is `K^{-3/4+o(1)}`. For every cube dimension compatible with a subexponential record-bootstrap loss, the method misses by a factor `K^{1/4-o(1)}`.

In the notation `K=M^2`, the absolute cube mass is at least `M^{-1-o(1)}`, whereas RH requires the signed amplitude to be `M^{-3/2+o(1)}`.

The remaining factor `M^{-1/2}` is therefore exactly cancellation among the residual rough-base Möbius signs. Prime toggles reorganize this cancellation but do not create it.

---

## 1. Packet and prime-cube decomposition

Let

\[
 w_K(n)=\frac1{n^2}\left(1-\frac1{n^2}\right)^K
 \qquad(n\ge1),
\]

and let

\[
 c_K=\sum_{n\ge1}\mu(n)w_K(n).
\]

For a squarefree integer `Q`, define the alternating prime-cube difference

\[
 \Delta_Qw_K(m)
 =\sum_{d\mid Q}\mu(d)w_K(dm).
\]

Every squarefree-supported integer has a unique decomposition into its `Q`-part and a `Q`-coprime base. Absolute convergence therefore gives the exact identity

\[
 \boxed{
 c_K
 =\sum_{(m,Q)=1}\mu(m)\Delta_Qw_K(m).
 }
 \tag{1}
\]

This is the full multi-prime version of the single-prime sign-reversing orbit decomposition. It is exact. No truncation, probabilistic model, or asymptotic approximation is involved.

The prospective strategy was to choose a growing primorial `Q`, make the mixed difference `Delta_Q w_K` small, and then bound the remaining sum without requiring deep cancellation in `mu(m)`.

The next theorem shows why that cannot reach RH.

---

## 2. Uniform positive tail of the mixed difference

Put `K=M^2`. Fix `R>0` and suppose `m>=RM`. Then

\[
 \Delta_Qw_{M^2}(m)
 =\frac1{m^2}
 \sum_{d\mid Q}\frac{\mu(d)}{d^2}
 \left(1-\frac1{d^2m^2}\right)^{M^2}.
 \tag{2}
\]

Set

\[
 A_Q=\sum_{d\mid Q}\frac{\mu(d)}{d^2}
 =\prod_{p\mid Q}\left(1-\frac1{p^2}\right).
\]

Since `Q` is squarefree,

\[
 A_Q\ge \prod_p\left(1-\frac1{p^2}\right)=\frac1{\zeta(2)}.
 \tag{3}
\]

Bernoulli's inequality gives

\[
 0\le
 1-\left(1-\frac1{d^2m^2}\right)^{M^2}
 \le \frac{M^2}{d^2m^2}.
\]

Consequently,

\[
 \begin{aligned}
 \left|
 \sum_{d\mid Q}\frac{\mu(d)}{d^2}
 \left[
 \left(1-\frac1{d^2m^2}\right)^{M^2}-1
 \right]
 \right|
 &\le
 \frac{M^2}{m^2}\sum_{d\mid Q}\frac1{d^4}\\
 &\le \frac{\zeta(4)}{R^2}.
 \end{aligned}
\]

Therefore

\[
 \boxed{
 \Delta_Qw_{M^2}(m)
 \ge
 \frac1{m^2}
 \left(
 \frac1{\zeta(2)}-\frac{\zeta(4)}{R^2}
 \right).
 }
 \tag{4}
\]

For `R=3`, the parenthesis is

\[
 c_3
 =\frac1{\zeta(2)}-\frac{\zeta(4)}9
 =0.487668964775\ldots>0.
\]

Thus the mixed difference is not merely large in absolute value on this interval. It is uniformly positive, for every squarefree prime cube `Q`.

---

## 3. Quantitative sign-free parity barrier

Let `d=omega(Q)` be the number of primes in `Q`, and define the interval mass

\[
 V_{Q,R}(M)
 =\sum_{
 \substack{RM\le m\le2RM\\(m,Q)=1}
 }
 \left|\Delta_Qw_{M^2}(m)\right|.
\]

By inclusion–exclusion,

\[
 \#\{m\in[RM,2RM]:(m,Q)=1\}
 \ge
 RM\frac{\varphi(Q)}Q-2^{d+1}.
 \tag{5}
\]

Order the prime divisors of `Q` as `p_1<...<p_d`. Since `p_i>=i+1`,

\[
 \frac{\varphi(Q)}Q
 =\prod_{i=1}^d\left(1-\frac1{p_i}\right)
 \ge\prod_{i=1}^d\frac{i}{i+1}
 =\frac1{d+1}.
 \tag{6}
\]

Assume

\[
 2^{d+2}(d+1)\le RM.
 \tag{7}
\]

Then the count in (5) is at least

\[
 \frac{RM}{2}\frac{\varphi(Q)}Q.
\]

Since `m<=2RM`, equation (4) gives

\[
 \boxed{
 V_{Q,R}(M)
 \ge
 \frac{c_R}{8R}
 \frac{\varphi(Q)}{QM}
 \ge
 \frac{c_R}{8R}
 \frac1{M(d+1)},
 }
 \tag{8}
\]

where

\[
 c_R=\frac1{\zeta(2)}-\frac{\zeta(4)}{R^2}>0.
\]

### Consequence

Suppose the prime-cube dimension satisfies

\[
 2^{d(M)}=e^{o(\log M)}.
\]

This is exactly the regime in which an exponential-in-dimension coherent-readout or Walsh cost remains subexponential in the record scale. It implies

\[
 d(M)=o(\log M),
\]

so condition (7) holds for all sufficiently large `M`. Equation (8) then gives

\[
 \boxed{
 V_{Q,R}(M)=M^{-1-o(1)}\quad\text{or larger}.
 }
 \tag{9}
\]

The Báez–Duarte/RH scale is

\[
 c_{M^2}=M^{-3/2+o(1)}.
\]

Therefore a proof that applies

\[
 \left|
 \sum_{(m,Q)=1}\mu(m)\Delta_Qw_{M^2}(m)
 \right|
 \le V_{Q,R}(M)
\]

necessarily misses the required scale by

\[
 \boxed{M^{1/2-o(1)}.}
\]

This is a tailored parity barrier for the Komorebi prime-toggle architecture.

It does **not** lower-bound `|c_{M^2}|`. The signed rough-base sum may be much smaller. It proves that this smaller size must come from cancellation in the remaining values `mu(m)`, not from the prime-cube mixed difference itself.

---

## 4. Why increasing the sieve depth does not rescue the argument

One might try to choose so many small primes that every rough base in the active interval is prime. To force this for numbers of size `M`, the sieve threshold must reach roughly `sqrt(M)`. The number of required prime coordinates is then on the order of the number of primes below `sqrt(M)`, far beyond `o(log M)`.

The associated Boolean cube has exponentially many channels in that dimension. It is incompatible with the subexponential inverse-gap budget required by the nonlinear record theorem.

This is the familiar sieve parity phenomenon in the exact coordinates of the present packet:

- shallow cubes have admissible complexity, but leave a composite rough-base sector whose Möbius parity is unresolved;
- deep cubes isolate the primitive prime sector, but their coordinate cost is far too large;
- taking absolute values at any admissible depth remains on the `M^-1` scale.

---

## 5. Common-target high-pass chart attempt

The certified single-prime transport theorem says that several prime high-pass charts approximate the same higher-scale Möbius amplitude with an explicit `O(T^-3)` transport defect. This suggests averaging many charts to cancel their smooth kernels while preserving the common target.

A favorable continuum surrogate has profile

\[
 \phi_p(x)
 =x^{-2}
 \left(
 e^{-1/x^2}-p^{-2}e^{-1/(p^2x^2)}
 \right).
 \tag{10}
\]

For weights `alpha_p` satisfying

\[
 \sum_p\alpha_p=1,
\]

we minimized

\[
 \left\|\sum_p\alpha_p\phi_p\right\|_{L^2(0,\infty)}^2.
\]

The Gram entries are closed form:

\[
 \int_0^\infty x^{-4}e^{-A/x^2}\,dx
 =\frac12\Gamma\!\left(\frac32\right)A^{-3/2}.
\]

Hence the optimization is an exact finite quadratic problem, solved at high precision.

### Observed result

Through the first twenty primes:

\[
 \min_{\sum\alpha_p=1}
 \left\|\sum_p\alpha_p\phi_p\right\|_2^2
 =0.0433393836113\ldots,
\]

while the `l1` norm of the optimal coefficients grows to

\[
 3.60\times10^6.
\]

The profile norm does not exhibit decay over the tested range, while the extrapolation becomes rapidly unstable.

This is a **finite diagnostic**, not a proof that the infinite-dimensional distance is positive. It does show that the most favorable common-target Bessel combination does not reveal the missing square-root factor at accessible depth.

---

## 6. What the computation establishes and does not establish

The reproducible computation performs three finite checks.

1. It verifies the truncated exact orbit decomposition by an independent direct Möbius sum.
2. It evaluates the positive interval mass `V_{Q,3}(M)` for
   `M in {100,316,1000,3162,10000}` and cube dimensions through `d=12`.
3. It solves the continuum common-target quadratic optimization through `d=20` using 120-digit arithmetic.

The largest orbit-decomposition discrepancy was below `6e-19`.

For every tested cube dimension, the absolute mixed-difference interval mass remains on the `M^-1` scale, and its ratio to `M^-3/2` grows with `sqrt(M)`.

The computation does **not**:

- estimate cancellation from `mu(m)`;
- prove the asymptotic lower bound—the proof above does that;
- prove an infinite-dimensional common-target profile floor;
- prove or disprove RH.

---

## 7. Exact remaining theorem after this push

Equation (1) and the barrier theorem reduce the viable prime-cube route to the signed estimate

\[
 \boxed{
 \left|
 \sum_{(m,Q)=1}\mu(m)\Delta_Qw_{M^2}(m)
 \right|
 \le
 M^{-3/2+o(1)},
 }
 \tag{11}
\]

for an admissible growing `Q`.

But equation (8) shows that the absolute mass on only one positive tail interval is already

\[
 M^{-1-o(1)}.
\]

Thus (11) requires a square-root cancellation factor

\[
 M^{-1/2+o(1)}
\]

among the rough-base Möbius signs.

This is the same content as:

- subpolynomial Báez–Duarte coherence;
- a strict signed collision saving;
- physical prime leakage from the primitive first-prime channel;
- exclusion of a shifted zero of the normalized critical transfer.

The surrounding Komorebi machinery changes the coordinate system, controls transport errors, and supplies the nonlinear closure once such a saving is available. It does not currently prove that saving.

---

## 8. Research decision

The following lanes should no longer be treated as likely closure mechanisms by themselves:

1. absolute values after any subexponential-size prime cube;
2. additional exact prime-toggle transport identities without a rough-base sign estimate;
3. common-target chart averaging based only on smooth continuum profiles;
4. higher prime-power refinements, which are already analytically stable;
5. global sign-blind Hardy norms or positive fourth moments.

The only remaining productive target is a genuinely signed estimate for the primitive first-prime/rough-base sector. Possible interfaces include:

- an amplified character dispersion theorem that controls the principal channel rather than only its average;
- a signed rough-shell correlation theorem beyond the sieve parity barrier;
- convergence of finite Weil-positive compressions with a quantitative gap compatible with the heat scale;
- a new arithmetic operator that mixes rough bases and does not commute with the Möbius observable.

No such theorem is proved here.

---

## 9. Final boundary

This push proves a new **methodological no-go theorem**, not RH:

\[
 \boxed{
 \text{prime-cube transport + sign-free majorization}
 \quad\text{cannot reach the RH scale.}
 }
\]

The missing theorem is now exactly the square-root cancellation of the residual rough-base Möbius signs.

\[
 \boxed{\text{RH remains unproved.}}
\]
