# Beal research, Block54
## Frobenius compatibility, global cup vanishing, and reduced reciprocity

**Release v5.4.0. 19 September2026.**

The next bounded block is complete. Under the explicitly inherited actual
Frey-representation hypotheses, the higher diagonal lifting obstruction now
vanishes at every depth:

\[
\boxed{\delta(a_n)=0,\qquad [\alpha]\smile[\beta]=0.}
\]

The proof also gives stronger support congruences and an exact reduced ray
presentation. Combining that presentation with compatible Kummer coordinates
eliminates depth3 on an explicit finite-support class, even though its abstract
ray-character space is nonzero. These are written proofs with exact finite
certificates, not new Lean proofs or independent mathematical review. The
complete reducible branch and Beal remain unresolved.

## 1. The decisive new comparison uses Frobenius, not only inertia

Keep Block53's actual depth n and put m=floor(n/2)+1. Its global result gives
eta_n=1 mod7^m, hence d(g)=1 mod7^m for every actual Galois element g.
At a variable prime, write the natural toric data in that SAME global basis:

\[
N=\mu\begin{pmatrix}-xy&x^2\\-y^2&xy\end{pmatrix},\qquad
F=I+\binom{x}{y}(p,r),\qquad Q-1=px+ry.
\]

The vector(x,y) is primitive and t=w(mu)>=1. If beta ramifies, the exact
lower-left valuation is n=t+2s, where s=w(y). Since F21=yp is divisible7^n,
p is divisible7^(t+s), and t+s>=m. The other term ry is F22-1 and is divisible
7^m by the global theorem. Consequently

\[
\boxed{\beta\text{ ramified at }v\ \Longrightarrow\
 h_v=v_7(Q_v-1)\ge m,\quad s_v<h_v,\quad\alpha|_{G_v}=0.}
\]

The old upper-endpoint obstruction s=h cannot occur in the ACTUAL
representation. It still occurs in the old abstract examples, which lack the
new Frobenius precision. Their historical validity is preserved.

## 2. Diagonal inertia has strictly less than the full tame capacity

At any variable prime, even one where beta is unramified, let the nontrivial
inertia image of eta_n have order7^k. Using the same primitive factorization
and the same global Frobenius precision gives

\[
\boxed{k+1\le h_v.}
\]

Thus all h=1 primes are unramified for eta_n at every depth. At a beta-support
prime the exact order is7^s. This links the actual lattice slope to the global
character rather than to an arbitrary local extension choice.

The original q1504231 nonliftable ray-character family has h=1 and nontrivial
inertia. It therefore cannot be the actual diagonal at ANY n>=2, including
bad13. The family remains a valid abstract global character construction.

## 3. From local lifting to global cup-zero

A tame inertia value of order7^k can be lifted one precision level to order
7^(k+1). The inequality above keeps that order within the local capacity7^h.
An unramified Frobenius value can be lifted freely. Eta is already trivial
on the full fixed local groups at2,3,5,7, and at the remaining good places it
is unramified. Therefore its next-level obstruction is zero at every place.

For trivial k=F49 coefficients, global H^2 localization is injective. The proof
restricts to K(zeta7), uses restriction/corestriction of degree prime to7,
identifies k with two copies of mu7 there, and applies the Brauer local-global
injection. Exact source statements were checked in Milne's Class Field Theory
v4.03; the complete translation is in the source record.

Hence delta(eta_n)=delta(a_n)=0. The preserved matrix coupling identity then
proves alpha cup beta=0. A continuous global character lift of a_n modulo
7^(n+1) exists.

**A character lift is not necessarily the next actual matrix diagonal.** The
proof does not increase n, kill beta, make eta_n trivial, or produce a lift
with the same conductor or fixed local values. Repeating the proof on an
arbitrary lifted character would discard the natural-matrix hypotheses.

## 4. A reduced five-row global presentation

For the complete variable support S of a hypothetical fixed C, set
c_v=max(h_v-1,0), and take seven-primary residue logarithms ell_v. Then actual
eta_n and its additive correction factor through

\[
R^-_S=
\left(\bigoplus_{v\in S}\mathbb Z/7^{c_v}\mathbb Z\right)
\Big/\langle\ell(\phi),\ell(2),\ell(3),\ell(\sqrt5),\ell(7)\rangle.
\]

The first row is the global unit. The other four impose the known full local
triviality at fixed primes. The reduced exponent h-1 is the new actual
Frobenius restriction. No finite search bound is imposed on general S.

If R^-_S has exponent7^e, every beta-supporting place satisfies

\[
\boxed{s\le e,\qquad n\le t+2e,\qquad n\le h+e.}
\]

The distinction between an abstract ray character and the actual diagonal
remains essential: factoring through R^- is necessary, not sufficient for
Frey realization.

## 5. A genuinely incompatible finite-support case

Let P0={11,13,19,29,31,43,71}. The complete exact presentations give

| Explicit support assumption | Unreduced ray quotient | Reduced necessary quotient |
|---|---|---|
| P0 | C7 x C7 | 0 |
| P0 union{491} | C7^3 | 0 |
| P0 union{491,1471} | C7^4 x C49 | C7 |

Here C_d is cyclic of order d, not the Diophantine integer C. Both491 and1471
split in K and have h=2.

Despite the nonzero C7 in the last row, the SAME global Kummer coefficients
exclude depth3. The exponent bound first gives n<=3. If n=3, eta cannot be
trivial, because that would require h>=3 at some beta-support prime. Its
nonzero ray line has coordinates proportional to(3,4,6,1), forcing inertia
at both places over491 and both places over1471. At depth3 this also forces
beta ramification at all four places.

The natural local class must therefore vanish at all four. Its compatible
Kummer matrix, on(a_phi,a_3,a_5), is

\[
\begin{pmatrix}
4&5&6\\3&5&6\\5&5&2\\2&5&2
\end{pmatrix}.
\]

The first three rows have determinant-20=1mod7, so this matrix has rank3 over
F49. Equivalently the491 pair forces a_phi=0 and a_3/a_5=3, while the1471 pair
forces a_3/a_5=1. This contradicts a_3*a_5!=0. Thus

\[
\boxed{\operatorname{supp}_{\rm var}(C)\subseteq P0\cup\{491,1471\}
\quad\Longrightarrow\quad n\le2.}
\]

No semilinear descent or general paired-ramification principle is assumed.
Paired support in this particular proof is forced by the exact ray kernel.
Depths1 and2 remain possible under the current necessary conditions, and no
theorem bounds arbitrary C to this support class.

## 6. General arithmetic consequences

If every eligible norm has v7(Q-1)=1, then n=1, without ANY multiplicity
assumption. This strengthens the previous ordinary{1,3} alternative.

If n>=2, some beta-supporting q must satisfy q^f=1mod49. In rational residue
classes this is q mod245 in{1,48,97,99,148,197}. None of the variable primes
in the earlier forced divisor1566013238790 meets the new supporting condition.
So higher depth needs at least one additional prime divisor outside the full
list{2,3,5,7,11,13,19,29,31,43,71}. This is not a contradiction and does not
force any particular new prime. Good13 still forces n=1 by Block53.

## 7. Exact verification and negative controls

The original Block53 verifier, including Blocks52,51 and the six selected
historical checks, passed before this work. Original ZIP bytes are preserved.
New deterministic standard-library programs provide:

| Check | Exact declared range/result |
|---|---:|
| Nonrational local Frobenius/monodromy grid | 9952 admissible cases |
| Nonunit first-coordinate cases | 216 cases |
| Split K-norm491 local example | 1 tight example |
| Beta-unramified but eta-ramified examples in the grid | 1056 cases |
| Tight supporting-norm / capacity-loss examples | 408 / 272 cases |
| Independent six-variable F7 kernel enumeration | 117649 vectors |
| Independent full multiplicative groups | 6132 elements over10 places |
| Independent principal-unit order checks | 1344 cases |
| Integral Smith toy presentations | 2793 exhaustive cases |
| Reduced quotient exhaustive coefficient vectors | 1,49,2401 |
| Normalized F49 Kummer directions in the joint obstruction | 2352 rejected by both implementations |

The independent residue code uses a different basis and full multiplicative
logs, imports no primary arithmetic code, and replays the Smith operations.
It is an independent implementation, not an independent mathematical reviewer.
Universal proofs do not follow from these finite counts.

Two draft overstatements were corrected before release:197 is not itself a
K-prime norm, so the local positive control now uses split491; and an
exponent-only depth3 argument cannot discard t=3,s=0 at an individual support
place. The later simultaneous proof supplies the missing extra restriction.
A direct PDF download failed; the source was checked through web text/images,
and no binary cache is claimed. Earlier historical failures remain untouched.
No new Lean compiler or independent mathematical reviewer was used.

## 8. Next boundary

The ACTUAL cup/character-lifting obstruction is now closed under the inherited
hypotheses. Remaining problems are the actual Kummer coefficients, nonzero
beta supported on compatible local zeros, actual eta values within the reduced
ray quotient, and unbounded prime support. The finite joint calculation is a
worked model for a stronger compatibility method, not a uniform solution.
The CM cover, three higher Hilbert levels, full signature and full Beal remain
separate unresolved obligations.
