# Conjecture Applications: Euler Spectra, Arithmetic Hankel Matrices and Algebraic Kernels

Author: Komorebi P.

20 November 2026 · Integrated mathematical reading edition

**Abstract.** This article collects an exact finite spectral formula for Euler up/down numbers modulo every odd integer, a prime-power period-jump congruence, and a p-adic jet description of the open Euler preperiod conjecture. It connects these results to general Cauchy–Hankel numerator identities, arithmetic submatrices, and arbitrary-length algebraic coefficient kernels. Precise proofs and reproducible finite checks are distinguished throughout. The Euler preperiod conjecture remains open. The underlying Cauchy and Lagrange identities, the established period theorem, and earlier OEIS recurrence statements are credited rather than claimed as new.

The Euler material develops checkpoint **CF-20261120-02**. The Hankel, kernel and radical results are summarized from the earlier **CF-20261120-01** checkpoint. The mathematical statements are written for all indicated parameters; computational evidence is always restricted to its stated finite range.

## 1. Results and evidence boundaries

**Proved within the accompanying manuscripts:** a modular spectral formula for every odd modulus; an exact prime-power period-jump congruence; an equivalence between weighted Euler divisibility and powers of a local polynomial ideal for jet order below the prime; arithmetic-progression Cauchy–Hankel corollaries; and explicit algebraic generating functions and recurrences for several coefficient-kernel families.

**Established external results used:** the minimal Euler period at odd prime powers and the source preperiod criterion, proved by Berke Güleç in 2026. The Cauchy determinant and Lagrange inversion are classical. Some special fixed-parameter recurrences were recorded previously in the OEIS.

**Not proved here:** the assertion that all Eulerian polynomials avoid the third power of the ideal \((p,t^2+1)\), and therefore the global inequality \(s(p^r)\ge r-2\). First-discovery priority of the uniform formulations has not been established. No Lean verification or independent journal peer review is asserted.

## 2. Euler numbers, Eulerian polynomials, and preperiods

The Euler up/down numbers count alternating permutations and are defined by

\[
\sec z+\tan z
=
\sum_{n\ge0}E_n\frac{z^n}{n!}.
\]

Their initial values are

\[
1,\ 1,\ 1,\ 2,\ 5,\ 16,\ 61,\ 272,\ 1385,\ldots
\]

For a positive integer \(q\), let \(s(q)\) denote the least preperiod and \(d(q)\) the least eventual period of the sequence \(E_n\bmod q\).

For every odd prime \(p\) and \(r\ge1\), Güleç proves

\[
d(p^r)=p^{r-1}\operatorname{lcm}(p-1,4)
\]

and establishes a divisibility criterion for \(s(p^r)\). His Conjecture 6.5 asks whether

\[
\boxed{
s(p^r)\ge r-2
\qquad(p\text{ odd prime},\ r\ge2).
}
\]

Use the **ordinary Eulerian polynomials** \(A_n(t)\), not the different zigzag Eulerian polynomials, defined for \(n\ge1\) by

\[
\sum_{k\ge1}k^nt^k
=
\frac{tA_n(t)}{(1-t)^{n+1}}.
\]

They satisfy

\[
\begin{aligned}
A_1(t)&=1,\\
A_{n+1}(t)&=(1+nt)A_n(t)\\
&\quad+t(1-t)A_n'(t).
\end{aligned}
\]

The distinction between these two uses of "Euler" is essential to the jet argument below.

## 3. Exact rational evaluation of Euler numbers

Set \(D=t\,d/dt\), \(\omega=-i\), where \(i^2=-1\), and let

\[
\begin{aligned}
S_n(t)&=D^n\left(\frac{t}{1-t}\right)\\
&=\sum_{k\ge1}k^nt^k.
\end{aligned}
\]

The right-hand sum is a formal-power-series identity. At \(t=\omega\), \(S_n\) means evaluation of its **rational function**, not summation of a generally nonconvergent series.

**Lemma 3.1.** For every \(n\ge1\),

\[
\boxed{E_n=2i^{n+1}S_n(\omega).}
\]

**Proof.** Define

\[
\begin{aligned}
Y(t)&=i\frac{1+t}{1-t},\\
t(z)&=\omega e^{iz}.
\end{aligned}
\]

Then \(Y(t(0))=1\), and direct differentiation gives

\[
\frac{d}{dz}Y(t(z))
=
\frac{1+Y(t(z))^2}{2}.
\]

The series \(\sec z+\tan z\) is the unique formal solution to this differential equation with constant term one. Because \(D^nY=2iS_n\) for \(n\ge1\), differentiating at \(z=0\) gives the lemma.

## 4. Finite spectral packets for every odd modulus

Work in

\[
R_q=(\mathbb Z/q\mathbb Z)[i],
\qquad i^2=-1.
\]

This is a rank-two coefficient ring whether or not \(-1\) is a square modulo \(q\).

**Theorem 4.1 (finite modular spectrum).** For every odd integer \(q\ge3\) and \(n\ge1\),

\[
\boxed{
\begin{aligned}
E_n&\equiv
\frac{2i^{n+1}}{1-\omega^q}\\
&\quad\times\sum_{k=1}^{q}
k^n\omega^k
\pmod q.
\end{aligned}
}
\]

The denominator \(1-\omega^q\) is a unit in \(R_q\).

**Proof.** Since \((k+q)^n\equiv k^n\pmod q\),

\[
\begin{aligned}
(1-t^q)S_n(t)
&\equiv\sum_{k=1}^{q}k^nt^k\\
&\pmod q.
\end{aligned}
\]

Both sides are rational expressions after clearing denominators, so the identity can be evaluated at \(t=\omega\). Because \(q\) is odd, \(\omega^q=\pm i\) and the norm of \(1-\omega^q\) is two, which is invertible modulo \(q\). Division and Lemma 3.1 give the displayed formula.

Summing its coefficients in the ordinary generating variable \(x\) yields a second identity in \(R_q[[x]]\):

\[
\boxed{
\begin{aligned}
\sum_{n\ge1}E_nx^n
&=\frac{2i}{1-\omega^q}\\
&\quad\times
\sum_{k=1}^{q}\omega^k
\frac{ikx}{1-ikx}
\pmod q.
\end{aligned}
}
\]

Although the separate summands use \(i\), the sum represents elements of the scalar subring \(\mathbb Z/q\mathbb Z\).

**Why this is useful.** The infinite sequence modulo \(q\) is represented by finitely many geometric modes, with no factorial division and with no primality assumption on \(q\). The spectral perspective is related to the Hurwitz-frequency method in Güleç’s paper; the theorem here provides a direct rational-power-sum derivation.

## 5. An exact prime-power period jump

For an odd prime \(p\), define

\[
\begin{aligned}
L_r&=p^{r-1}\operatorname{lcm}(p-1,4),\\
\varepsilon_{p,n}&=
\begin{cases}
1,&p\equiv1\pmod4,\\
(-1)^{n+1},&p\equiv3\pmod4.
\end{cases}
\end{aligned}
\]

**Theorem 5.1 (period-jump congruence).** For every \(r\ge1\) and \(n\ge1\),

\[
\boxed{
\begin{aligned}
E_{n+L_r}-E_n
&\equiv-\varepsilon_{p,n}p^nE_n\\
&\pmod{p^r}.
\end{aligned}
}
\]

If \(n+v_p(E_n)<r\), then

\[
v_p(E_{n+L_r}-E_n)
=n+v_p(E_n).
\]

**Proof.** The integer \(L_r\) is divisible by four. In the finite spectrum modulo \(p^r\), a frequency \(k\) prime to \(p\) satisfies \(k^{L_r}\equiv1\pmod{p^r}\), whereas a frequency divisible by \(p\) satisfies \(k^{L_r}\equiv0\pmod{p^r}\). Subtracting the two spectral expressions therefore leaves only the latter modes, with a minus sign.

Writing \(k=pj\) extracts the factor \(p^n\). The remaining sum is the same rational power sum at \(\omega^p\) modulo the remaining precision. The rational identity

\[
S_n(t^{-1})=(-1)^{n+1}S_n(t)
\]

converts \(\omega^p\) to \(\omega\): it is \(\omega\) for \(p\equiv1\pmod4\) and \(\omega^{-1}\) for \(p\equiv3\pmod4\). This yields the congruence. The valuation assertion follows whenever the displayed residue remains nonzero modulo \(p^r\).

The restriction \(n\ge1\) matters. The index-zero boundary is not periodic, because \(E_0=1\) and the appropriate period shift produces a different residue modulo every odd prime.

**Corollary 5.2 (preperiod criterion).** For \(1\le k\le r\),

\[
\boxed{
\begin{gathered}
s(p^r)\le r-k\\
\Longleftrightarrow\\
p^j\mid E_{r-j}
\quad(1\le j\le k).
\end{gathered}
}
\]

**Proof.** The period jump vanishes automatically for \(n\ge r\) and, for \(1\le n<r\), vanishes precisely when \(p^{r-n}\mid E_n\). An eventual period divisible by the minimal period has the same least onset on a periodic tail. Apply the period-jump criterion at \(n=r-j\). If \(j=r\), the condition would require \(p^r\mid E_0=1\) and correctly fails.

The source paper already proves this preperiod criterion by a different method. The explicit jump congruence supplies an independent derivation, not an originality claim for the criterion.

## 6. Weighted Euler divisibility as a local jet condition

Let \(\mathbb Z_p\) be the ring of \(p\)-adic integers and put

\[
\boxed{J_p=(p,t^2+1)\subset\mathbb Z_p[t].}
\]

**Theorem 6.1 (weighted jet equivalence).** For every odd prime \(p\), \(n\ge1\), and integer \(0\le c<p\),

\[
\boxed{
\begin{gathered}
p^{c+1-j}\mid E_{n+j}\\
(0\le j\le c)\\
\Longleftrightarrow\\
A_n(t)\in J_p^{c+1}.
\end{gathered}
}
\]

The range \(c<p\) is part of the theorem, not merely a technical preference.

**Proof.** Work over \(\mathbb Z_p[i]\), set \(u=t-\omega\), and write

\[
S_n(\omega+u)=\sum_{k\ge0}c_ku^k.
\]

Near \(t=\omega\),

\[
S_n(t)=\frac{tA_n(t)}{(1-t)^{n+1}}
\]

differs from \(A_n(t)\) by a unit. Further,

\[
\begin{aligned}
D^jS_n(\omega)
&=j!\,\omega^jc_j\\
&\quad+\sum_{k<j}\gamma_{j,k}c_k.
\end{aligned}
\]

For \(j<p\), the diagonal factor \(j!\omega^j\) is a \(p\)-adic unit. The system is triangular, so the weighted divisibilities of the Euler numbers are equivalent, successively, to

\[
c_j\in p^{c+1-j}\mathbb Z_p[i]
\qquad(0\le j\le c).
\]

These are exactly the coefficients required for membership in \((p,t-\omega)^{c+1}\). Conjugation sends \(\omega=-i\) to \(i\). The two conjugate ideals are comaximal because their roots differ by the unit \(2i\). Their product is \((p,t^2+1)\). Contracting back from the free rank-two extension proves the theorem.

When \(j\ge p\), the factorial \(j!\) is no longer a \(p\)-adic unit. The simple criterion must then be replaced by a factorial-aware or Hasse-derivative filtration.

## 7. The precise open Euler conjecture

Using Corollary 5.2 with \(k=3\), the conjectured lower bound fails exactly when, for some \(n\ge1\),

\[
\boxed{
\begin{aligned}
p^3&\mid E_n,\\
p^2&\mid E_{n+1},\\
p&\mid E_{n+2}.
\end{aligned}
}
\]

The index \(n=0\) is impossible because \(E_0=1\), and the bound at \(r=2\) is automatic.

Theorem 6.1 with \(c=2\) therefore gives an **equivalent formulation of the open conjecture**:

\[
\boxed{
\begin{gathered}
A_n(t)\notin(p,t^2+1)^3\\
\text{for all odd }p,\ n\ge1.
\end{gathered}
}
\]

This equivalence is proved. The nonmembership statement itself is **not proved**.

### Six exact integer tests at each fixed index

Divide \(A_n(t)\) repeatedly by the monic polynomial \(Q(t)=1+t^2\) to obtain the unique expansion

\[
\begin{aligned}
A_n(t)
&=\sum_{j\ge0}(a_j+b_jt)Q(t)^j,\\
&a_j,b_j\in\mathbb Z.
\end{aligned}
\]

Then the conjectural obstruction at prime \(p\) is precisely the simultaneous condition

\[
\boxed{
\begin{aligned}
p^3&\mid a_0,\ b_0,\\
p^2&\mid a_1,\ b_1,\\
p&\mid a_2,\ b_2.
\end{aligned}
}
\]

The recurrence for \(A_n\) in Section 2 and monic polynomial division make these six conditions directly computable modulo \(p^3\), without constructing the full integer \(E_n\).

**A strictly stronger sufficient condition** is the absence of three consecutive Euler numbers divisible by \(p\). That ordinary zero-run statement would imply the conjecture, but the weighted obstruction above is the exact target and is weaker.

### Worked arithmetic control at \(p=43\)

At index \(n=978\), the recorded exact checks confirm

\[
\begin{aligned}
A_{978}(t)&\in J_{43}^2,\\
A_{978}(t)&\notin J_{43}^3.
\end{aligned}
\]

Thus the weighted two-term obstruction can occur without the forbidden three-term obstruction. This is a **positive test of the distinction**, not a counterexample to the conjecture. The known preperiod example \(s(43^{980})=978\) is retained with attribution to the source discussion.

The remaining research goal is a uniform \(p\)-adic nonmembership or transversality theorem. An induction using the Eulerian recurrence must control the loss of \(Q\)-adic order under differentiation. No such global invariant is established here.

## 8. Prime-power and composite-modulus consequences

The previous research checkpoint contains complete finite certificates for each of the 45 odd primes through 199. Using the established period and preperiod criterion, those certificates classify \(s(p^r)\) **for every exponent** of each tested prime, not merely for the tested small exponents.

For example, the recorded \(43\)-power classification is

\[
\boxed{
\begin{aligned}
s(43^r)=r
&-\mathbf1_{\{r\bmod42\in\{13,14,28\}\}}\\
&-\mathbf1_{\{r\bmod1806=980\}}.
\end{aligned}
}
\]

In particular, the defect two occurs precisely when \(r\equiv980\pmod{1806}\). This is a fixed-prime classification; it does not prove the conjecture for unbounded primes.

For an odd modulus

\[
q=\prod_{j=1}^{m}p_j^{r_j},
\]

the Chinese remainder theorem gives

\[
\boxed{
\begin{aligned}
s(q)&=\max_j s(p_j^{r_j}),\\
d(q)&=\operatorname{lcm}_j d(p_j^{r_j}).
\end{aligned}
}
\]

**Proof.** A congruence modulo \(q\) holds precisely when it holds modulo every prime-power factor. The earliest common onset is the maximum of the component onsets. The minimal period on the common tail is the least common multiple of the component minimal periods.

This elementary corollary extends the recorded fixed-prime computations to composite moduli supported on the checked primes. It is not a claim of a new Chinese-remainder theorem.

## 9. Companion result: Hankel numerators and arithmetic submatrices

For positive integers \(d,h\), define the size-\((n+1)\) determinant

\[
\begin{aligned}
H_n(d,h)
&=\det\left[
\frac1{d(i+j)+h}
\right]_{0\le i,j\le n}.
\end{aligned}
\]

The classical Cauchy identity gives

\[
\boxed{
\begin{gathered}
H_n(d,h)=\\[-2pt]
\frac{d^{n(n+1)}
\bigl(\prod_{k=1}^{n}k!\bigr)^2}
{\prod_{i,j=0}^{n}(d(i+j)+h)}.
\end{gathered}
}
\]

When \(\gcd(d,h)=1\), its reduced numerator is

\[
\boxed{
\begin{aligned}
\operatorname{num}H_n(d,h)
&=\prod_{p\mid d}p^{e_p},\\
e_p&=n(n+1)v_p(d)\\
&\quad+2\sum_{k=1}^{n}v_p(k!).
\end{aligned}
}
\]

This contains the prime-step numerator conjecture recorded in OEIS A122251. It also works for composite steps and arbitrary positive coprime shifts. Its proof counts, for every prime power not dividing \(d\), the denominator factors with \(i+j\) in the required residue class and compares them with factorial valuations. The denominator count dominates, so no such prime survives in the numerator.

For an arbitrary positive shift, set

\[
\begin{aligned}
g&=\gcd(d,h),\\
D&=d/g,\qquad N=n+1.
\end{aligned}
\]

Then the complete result is

\[
\boxed{
\begin{aligned}
\operatorname{num}H_n(d,h)
&=\prod_{p\mid D}p^{f_p},\\
f_p&=\max(0,\rho_p),\\
\rho_p&=nN\,v_p(D)\\
&\quad+2\sum_{k=1}^{n}v_p(k!)\\
&\quad-Nv_p(g).
\end{aligned}
}
\]

For fixed \(d,n\), this depends on \(h\) only through \(\gcd(d,h)\).

### Arithmetic-progression submatrices

Selecting rows \(a+si\) and columns \(b+tj\) from a Cauchy–Hankel matrix with base step \(d\) gives entries

\[
\begin{aligned}
M_{ij}&=\frac1{dsi+dtj+H},\\
H&=h+d(a+b).
\end{aligned}
\]

When \(s=t=w\), the preceding numerator formula applies with effective step \(dw\) and shift \(H\). For unequal strides, the inverse-Cauchy localization theorem in the base manuscript shows that every prime in the reduced numerator of \(\det M\) divides \(dst\).

The nonconsecutive Hilbert minor illustrates why the stride matters:

\[
\det
\begin{pmatrix}
1&1/3\\
1/3&1/5
\end{pmatrix}
=\frac4{45}.
\]

This section summarizes earlier proved results; the complete proofs and independent exact checks are preserved in the preceding research checkpoint.

## 10. Companion result: algebraic coefficient kernels

For an arbitrary integer \(m\ge2\), put

\[
\begin{aligned}
a_n(u,v)&=[t^{n-1}](1+ut+vt^m)^n,\\
&n\ge1.
\end{aligned}
\]

with \(a_0=0\). The exact terminating sum can be written compactly by taking
\(j_k=n-1-mk\) and \(h_k=(m-1)k+1\):

\[
\boxed{
\begin{aligned}
a_n(u,v)
&=\sum_{k=0}^{\lfloor(n-1)/m\rfloor}\\
&\quad\frac{n!}{k!\,j_k!\,h_k!}
u^{j_k}v^k.
\end{aligned}
}
\]

Let \(T\) be uniquely specified by

\[
\begin{aligned}
T&=x(1+uT+vT^m),\\
T(0)&=0.
\end{aligned}
\]

Classical Lagrange coefficient transfer gives the algebraic generating function

\[
\boxed{
\begin{aligned}
G(x)&=\sum_{n\ge0}a_nx^n\\
&=xT'(x)\\
&=\frac{T}{1-x(u+mvT^{m-1})}.
\end{aligned}
}
\]

The base manuscript derives a uniform polynomial recurrence with at most \(m+1\) consecutive terms and includes zero weights, the cubic and quartic cases, and shifted coefficient extraction. Previously recorded fixed-parameter cubic and quartic recurrences are identified there as known after translation of notation. This uniform construction complements the block-weight theorem in the [weighted binomial reading page](https://komorebip.github.io/Operation-KOMOREBI/sequence-central-binomial.html).

Another companion result classifies the scaled radical recurrence associated with OEIS A134389, including arbitrary initial values. Its closed form gives explicit parity formulas for the original sequence. That fixed generating function was already recorded, so the novelty assessment applies only to the wider derivation and not to the original special case.

## 11. Verification, scope, and reproduction

Two independent exact programs in the continuation checkpoint use integer and rational arithmetic, without floating point or random sampling. Their verified totals are:

- 665 finite spectral comparisons across 19 odd moduli, including composite moduli.
- 306 prime-power period-jump comparisons.
- 2,025 weighted-jet equivalences over nine primes and indices 1 through 75.
- 8,960 equal-stride and 11,520 unequal-stride arithmetic-subminor checks.
- The high-index \(p=43,n=978\) weighted-pair positive control and weighted-triple negative control.

The original checkpoint additionally includes full exact verification of its Hankel, algebraic-kernel, radical, and fixed-prime Euler statements. Finite checks corroborate their tested ranges; **universal mathematical assertions are supported by written proofs, not extrapolation from finite checks**.

The original continuation packages include the editable LaTeX sources, exact Python programs, frozen JSON outputs, SHA-256 checksums, and handoff instructions.

The current exact checkers are also available directly in the repository: [Euler spectra and jets](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/tools/sequence_euler_spectral_jet.py), [arithmetic Cauchy minors](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/tools/sequence_arithmetic_subminors.py), and [test contracts](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/tools/test_sequence_conjecture_applications.py).

Run the published verification programs from the repository root using Python 3.10 or later:

```bash
python -B tools/sequence_euler_spectral_jet.py --output euler-jet-results.json
python -B tools/sequence_arithmetic_subminors.py --output cauchy-minor-results.json
python -B -m unittest discover -s tools -p test_sequence_conjecture_applications.py -v
``` The source files for this web reading edition are versioned in the Operation-KOMOREBI repository.

**Research boundary.** A global proof of \(A_n\notin(p,t^2+1)^3\) for all odd primes and all \(n\ge1\) is still missing. The article does not claim the original preperiod conjecture is resolved, does not claim historical first discovery, and does not claim a Lean formalization.

## 12. Sources and attribution

- Berke Güleç. [Modular periodicity of the Euler up/down numbers at odd prime powers](https://arxiv.org/abs/2608.27058), arXiv:2608.27058v2, 2026. Established exact periods and the prime-power preperiod criterion; stated the lower-bound conjecture.
- [Coprimality of consecutive Euler up/down numbers and the preperiod at odd prime powers](https://ideosphere.ai/papers/updown-preperiod), August 2026. Earlier finite gcd and Lean checks for Euler up/down numbers.
- Ira M. Gessel. [Lagrange Inversion](https://arxiv.org/abs/1609.05988), 2016. Classical coefficient-transfer framework used for algebraic kernels.
- The On-Line Encyclopedia of Integer Sequences. [A122251](https://oeis.org/A122251), [A127905](https://oeis.org/A127905), [A071879](https://oeis.org/A071879), [A127902](https://oeis.org/A127902), and [A134389](https://oeis.org/A134389). Historical sequence definitions, conjecture labels, generating functions, and equivalent recorded recurrences.
- Komorebi P. *Conjecture Applications: Hankel Numerators, Algebraic Kernels, Radical Recurrences, and Euler Preperiods*, checkpoint CF-20261120-01, 20 November 2026.
- Komorebi P. *Spectral Euler Packets and p-adic Jet Obstructions*, checkpoint CF-20261120-02, 20 November 2026. The present article integrates this continuation.

**Author: Komorebi P.** No institutional affiliation or location is included.
