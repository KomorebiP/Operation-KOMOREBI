# Multiplicative–Additive Reconstruction, Block 03
## Finite observation, recurrence grammars, and Witt carry obstructions

**Realization Calculus · Komorebi Space · exact research continuation**

### Abstract

A multiplicative transfer of the positive integers can relabel primes without preserving addition. Earlier blocks established transported semiring/field structures and sharp finite annihilators for additive scaling plus bounded-degree polynomial-depth corrections. This block tests two much broader forms of reconstruction: arbitrary functions of fixed finite local arithmetic observations, and sequences governed by arbitrary fixed linear recurrences. Both admit finite impossibility certificates. In contrast, arithmetic Teichmüller sections yield exact local reconstruction using a nontrivial Witt carry cocycle. The two phenomena clarify the mathematical gap between local algebraic compatibility and global archimedean height control. No form of abc or IUT is proved or disproved.

**Statement types:** `THEOREM` = proved in this note under explicit assumptions; `LEAN` = corresponding proposition compiled in the supplied pinned portable Lean 4.34.0-rc2 runtime; `EXACT TEST` = reproducible finite calculation; `BOUNDARY` = an assumption that cannot be omitted. Classical results (finite recurrence annihilation, elementary cocycles, Teichmüller lifting, the nonsplit cyclic additive extension, compactness) are not claimed as historically new. The proposed contribution is their integration into a typed quantitative reconstruction framework.

---

## 1. Arithmetic setup and protected data

Let `T` be a multiplicative prime-relabeling bijection, sending a prime `p` to a distinct prime `q`. On prime powers, `T(p^k)=q^k`. Assume `2 ≤ p < q` so that we can exhibit an unbounded expanding direction. Let an attempted additive reconstruction be

\[
\mathscr R(n)=\lambda n+F(\operatorname{rad}(n),\,n\bmod M),
\]

with a **fixed** positive integer `M`, arbitrary `F` on these observations (no continuity, linearity, or computability assumption), and arbitrary real `λ`. The residual on the prime-power sector is

\[
e_k=q^k-\lambda p^k-F(p,p^k\bmod M).
\]

The protected information is the original ordinary additive scaling and finitely observed modular and radical data. The problem is to bound `e_k` uniformly. This is a specific, deliberately narrow reconstruction class, not all of Realization Calculus or arithmetic geometry.

## 2. Finite-observation rigidity [AMR-09: THEOREM]

Write `e=v_p(M)` and `M_0=M/p^e`, so `gcd(p,M_0)=1`. Define `L=1` if `M_0=1` and otherwise let `L` be the multiplicative order of `p` modulo `M_0`.

For every `k ≥ max(1,e)` and each `j≥0`, the Chinese remainder theorem yields

\[
p^{k+jL}\equiv p^k\pmod M.
\]

All these integers have radical `p`. Their values under `F` are therefore the *same* arbitrary real number `κ`.

Put `u=p^L`, `v=q^L`, `A=p^k`, and `B=q^k`. For the three sampled depths `k,k+L,k+2L`, the residuals become

\[
r_j=Bv^j-\lambda Au^j-\kappa,\qquad j=0,1,2.
\]

The finite filter `(u,-(u+1),1)` kills the affine constant and the additive mode. It returns

\[
ur_0-(u+1)r_1+r_2=B(v-1)(v-u).
\]

By the triangle inequality, if all residuals have absolute value at most `E`,

\[
\boxed{E\ge\frac{q^k(q^L-1)(q^L-p^L)}{2(p^L+1)}.}\tag{1}
\]

**Sharpness.** Set

\[
t=\frac{B(v-1)(v-u)}{2(u+1)},\quad
\lambda=\frac{B(v-1)+2t}{A(u-1)},\quad
\kappa=B-t-\lambda A.
\]

Then `(r_0,r_1,r_2)=(t,-t,t)`, attaining equality. This proves the *three-sample* minimax identity. It does not assert that the same `λ,κ` globally minimize the error over all positive integers.

**Corollary.** For fixed `p<q` and fixed modulus `M`, every `λ` and arbitrary `F` above satisfy `sup_k |e_k|=∞`, since (1) grows as `q^k` with fixed positive `L`. No finite-precision local correction of this form uniformly recovers the height of a prime-relabeling transfer.

**Example.** For `(p,q,M,k)=(2,3,12,2)`, `L=2` and the observations of `4,16,64` are all `4 mod 12`. Their targets are `9,81,729`. The sharp error is `36`. It is achieved by `λ=12` and `κ=-75`, with residuals `(36,-36,36)`.

**LEAN:** `FiniteObservation.lean` checks the filter identity, exact impossibility condition, sharp finite lower bound, and an attaining witness. **Not formalized in this Lean block:** the CRT/order argument that generates the repetitions. It is given here as a complete elementary proof and checked over 108 exact cases.

## 3. A universal finite-recurrence grammar obstruction [AMR-10: THEOREM]

Let `E` be the left-shift operator on sequences, `Ef(k)=f(k+1)`. Suppose a correction `h_k` obeys a fixed homogeneous linear recurrence `P(E)h=0` for all sufficiently large `k`, where `P(z)=∑_{j=0}^d c_j z^j` is a nonzero real polynomial. Consider the repaired sequence `λ p^k+h_k`. Define the annihilator

\[
Q(z)=(z-p)P(z)=\sum_{j=0}^{d+1}a_jz^j.
\]

It kills both admissible terms, while

\[
Q(E)q^k=q^k(q-p)P(q).
\]

For residuals `r_k=q^k-λp^k-h_k`, finite summation yields

\[
\boxed{
\max_{0\le j\le d+1}|r_{k+j}|\ge
\frac{q^k|q-p||P(q)|}{\sum_{j=0}^{d+1}|a_j|}.
}\tag{2}
\]

When `P(q)≠0`, the right side diverges exponentially. **Necessary condition for a uniformly bounded error** in this recurrence class is `P(q)=0`. This condition is not sufficient for every restricted correction family, but it is the correct algebraic boundary.

**Negative control:** if `P(z)=z-q`, the admissible correction includes `h_k=q^k`, and `λ=0` gives exact reconstruction. This evades the obstruction by explicitly importing the entire transported exponential mode; it is not a useful arithmetic saving. The failure of (2) to exclude this case is intentional and necessary.

**LEAN:** `FilterBudget.lean` verifies the arbitrary-length finite-filter absolute-error bound and its protected-correction corollary, with no fixed sequence length. The polynomial recurrence specialization (2) is proved algebraically here and checked in 2,772 exact rational cases across 66 recurrence families; it has not yet been formalized in Lean as a complete arbitrary-polynomial theorem.

## 4. Exact sharp polyphase-depth reconstruction [AMR-11: THEOREM]

Sample only one phase of a valuation signal: `k,k+s,...,k+(d+2)s`, where `s≥1` and `d≥0`. Allow additive scaling `λp^{k+sj}` together with any real polynomial in the phase index `j` of degree at most `d`.

Apply the annihilator `(E-p^s)(E-1)^{d+1}` in the phase variable `j`. Its coefficient ℓ¹ norm is `2^{d+1}(p^s+1)`, and its action on the transported output is `q^k(q^s-p^s)(q^s-1)^{d+1}`. The permitted reconstruction space has dimension `d+2` in the `d+3` observations (because `p^s>1`), so its unique linear annihilator is the filter above. The coefficients alternate in sign. Taking a residual proportional to the signs of the coefficients and solving for the unique correction proves *attainment* of the lower bound:

\[
\boxed{ E_{s,d,k}^{\mathrm{sharp}}=
\frac{q^k(q^s-p^s)(q^s-1)^{d+1}}{2^{d+1}(p^s+1)}.}\tag{3}
\]

**Consequences.** Every fixed polyphase/degree grammar fails to reconstruct a growing transfer `p<q` with uniformly bounded error over sufficiently deep observations. For `p=2,q=3,s=1`, (3) simplifies to `3^{k-1}`, independently of `d`. Allowing additional *finite* polynomial degrees does not fix this tested obstruction when the observation window expands correspondingly.

**EXACT TEST:** 420 rational sharpness cases, including explicit interpolation witnesses up to polynomial degree six. General all-degree proof is mathematical, not claimed as a finished Lean all-degree formalization.

## 5. Multiplicative Teichmüller lifts and exact additive carries [AMR-12]

Let `p` be prime, `N≥2`, and represent `x∈F_p` by `x∈{0,...,p−1}`. The Teichmüller lift modulo `p^N` is

\[
t_N(x)=x^{p^{N-1}}\pmod {p^N}.
\]

This is well-defined on `F_p`, multiplicative, and satisfies `t_N(x)≡x mod p`. Define

\[
C_{p,N}(x,y)=\frac{t_N(x)+t_N(y)-t_N(x+y)}p \quad\pmod {p^{N-1}},
\]

where `x+y` inside `t_N` is reduced modulo `p`. This is well-defined because the numerator is divisible by `p`. It is the exact additive correction of the multiplicative section:

\[
t_N(x)+t_N(y)\equiv t_N(x+y)+pC_{p,N}(x,y)\pmod{p^N}.
\]

**THEOREM (carry cocycle).** For all residues,

\[
C(x,y)+C(x+y,z)=C(y,z)+C(x,y+z)\quad\pmod{p^{N-1}}.
\]

The identity follows by substituting the defining defect and cancelling all lifts. It is not evidence of an additional independent estimate; every additive section has an analogous cocycle.

**THEOREM (nonzero cycle / nonsplitting).** The telescope

\[
\boxed{\sum_{i=0}^{p-1} C_{p,N}(1,i)\equiv 1\pmod{p^{N-1}}}
\]

holds because the intermediate Teichmüller representatives cancel and `t_N(1)=1`. Changing the section by `t'_N(x)=t_N(x)+p b(x)` changes this cyclic sum by `p b(1)` modulo `p^{N-1}`; the sum remains **1 modulo p**. Consequently, no additive section of `Z/p^N→F_p` exists: a lift of the generator `1∈F_p` has additive order `p^N` (in particular it cannot have order dividing `p`). Equivalently, the additive extension `0→Z/p^{N-1}→Z/p^N→Z/p→0` is nonsplit. This is a classical cyclic-group extension phenomenon, not a novel proof of arithmetic conjectures.

**LEAN:** `WittCarryExample.lean` checks multiplicativity and the carry cocycle for the complete finite ring `F_3→Z/9`, its nonzero cycle, and a proof that an additive section modulo 9 is impossible. **Not yet Lean-formalized:** the general all-prime/all-precision version; its elementary proof and tests are supplied.

**EXACT TEST:** 31,398 multiplicativity pairs and 12,093 carry cocycle triples, plus section-perturbation controls and first-level nonsplitting controls. All passed.

## 6. Profinite-to-archimedean obstruction [AMR-13: classical theorem]

Let `Ẑ` be the profinite completion of the integers, a compact topological ring, and embed positive integers diagonally into it. There is **no continuous real-valued function** `H:Ẑ→R` such that `H(n)=log n` for every positive integer `n`. Indeed, the continuous image of a compact space in `R` is bounded, whereas `log n` is unbounded.

In particular, even having *all* finite modular observations does not provide a continuous real-valued reconstruction of the ordinary unbounded archimedean height. A candidate arithmetic framework needs a real/archimedean channel, a noncompact realization, a discontinuity, a changing resolution, or some other mechanism whose quantitative cost is explicitly justified.

This statement does **not** rule out arithmetic inequalities involving profinite or adelic data, and it does not apply to all height functionals or to IUT's full structures. It rules out one very specific class of continuous reconstructions.

## 7. Verification and boundaries

| Component | Mathematical proof | Lean 4.34.0-rc2 | Exact finite tests |
|---|---|---|---|
| Three-sample annihilator and sharp budget | Complete | Complete (algebraic) | 108 CRT/residue cases |
| CRT-generated modular periodicity | Complete | Not added | 108 cases |
| Arbitrary finite recurrence filter budget | Complete | Abstract finite-filter budget complete | 2,772 cases; 66 families |
| Polyphase all-degree sharp minimax | Complete | Specialization not added | 420 cases |
| Witt first-carry and nonsplitting | Complete | `p=3,N=2` complete | 31,398 pairs, 12,093 triples |
| Profinite compactness obstruction | Classical proof given | Not added | Not a numerical claim |
| General abc height bridge | **Open** | Not proved | Not implied by these tests |

**Key negative controls:** (i) `P(z)=z-q` permits exact recurrence reconstruction because the target mode is already inserted; (ii) changing the Witt section does not remove the nonzero class modulo `p`; (iii) restoring `T` by its full inverse or by carrying full archimedean height is formally possible but cannot count as a new estimate.

### The genuinely unresolved question

The local carry cocycle shows how one can preserve multiplication and recover addition at each finite arithmetic level. The finite-recursion and compactness obstructions show why this alone does not yield a uniform global height inequality. The right research target is therefore a **quantitative, globally coupled arithmetic realization** whose input costs are controlled by radical/conductor data and whose archimedean output controls `c/rad(abc)` in primitive `a+b=c`. Such a theorem remains unknown here. No proof of abc is asserted.

### Restart point

1. Formalize the CRT orbit period and the all-degree polynomial/recurrence annihilator in Lean, reusing the checked abstract filter-budget theorem.
2. Make the Witt cocycle an actual Komorebi Space protected-correction class with typed finite-level realizations and prove naturality of its reduction maps.
3. Study an adelic realization **including** the infinite place. Demand an explicit, uniform height-control hypothesis and identify exactly where an estimate stronger than prior formulas first enters.

This block is a research continuation and technical audit, **not** a claim of priority over classical finite-difference, Witt-vector, cohomological, or compactness mathematics.

### Development diagnostics

During the verification pass, the first finite-sum proof attempt imported the entire `Mathlib.Tactic` umbrella and timed out. Replacing it with targeted algebra/order imports resolved the issue. A first Witt example referenced a Mathlib import path not supplied by the pinned package; the unsupported import was removed. The corrected positive files all compiled with warning rejection, and the false negative-control theorem was rejected as intended. The distributable archive retains final verification records, not intermediate failed development snapshots.
