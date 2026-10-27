# Information Realization and Obstruction: finite foundation v0.1

**Project:** Operation Komorebi / Realization Calculus  
**Date:** 2026-10-14  
**Status:** mathematical propositions proved below on paper; Python verification completed for stated finite samples; **not formally verified in Lean**.  
**Novelty:** base results are established mathematics (partition refinement, conditional entropy, sufficient statistics, Bayes decoding, and orthogonal projection). Their integration into a future Komorebi calculus is a *research proposal*, not presently a novel theorem.

## 1. Scope and data

Let `X` be a nonempty finite state set, `F : X -> Y` the desired task output, `r : X -> R` an available deterministic realization, and `P` an optional probability mass function on `X`. All image and fiber cardinalities below are over the entire state space, not merely the support of `P`.

Let `K(r,F)` be the maximum number of distinct task outputs occurring in any fiber of `r`:

\[
K(r,F)=\max_{z\in r(X)}\left|\{F(x):r(x)=z\}\right|.
\]

Define the fixed-width exact-repair cost
\[
B(r,F)=\lceil\log_2 K(r,F)\rceil.
\]

When `P` is specified, let `R=r(X)` be the observed random variable. Define the average information deficit `H(F(X)|R)` (bits) and Bayes-optimal exact-decoding error

\[
E(r,F)=1-\sum_z\max_y\Pr(R=z,F(X)=y).
\]

This information profile is deliberately **vector-valued**, not a sum of incomparable units. It depends on a chosen task `F`; there is no assumption of context-free information content.

## 2. Exact recoverability and obstruction

**Theorem A (finite factorization).** The following are equivalent:

1. There is a function `g : r(X) -> Y` such that `F = g ∘ r`.
2. For every `x,y ∈ X`, `r(x)=r(y)` implies `F(x)=F(y)`.
3. `K(r,F)=1`.

**Proof.** (1) implies (2) by substitution. (2) implies (3) because `F` takes one value on each nonempty `r`-fiber. Under (3), define `g(z)` to be the unique `F`-value on `r^{-1}(z)`. This is well-defined and yields (1). QED.

An **obstruction witness** is a pair `x,y` with equal observations but unequal required answers. It is a checkable certificate that no decoder using only `r` can be exact on both states.

**Theorem B (minimal side-information alphabet).** Suppose an additional deterministic code `c : X -> C` is allowed, and the decoder may use the pair `(r(x),c(x))`. The smallest possible `|C|` making exact recovery of `F` possible equals `K(r,F)`.

**Proof.** In each `r`-fiber, distinct `F` outputs require distinct code values, giving the lower bound. Conversely, enumerate the distinct `F` outputs within each fiber and assign labels from a common alphabet of size `K`; labels may be reused in different fibers because the decoder also knows `r(x)`. QED.

*Interpretation:* `B(r,F)` is the minimum **worst-case fixed-width** number of extra bits, assuming the supplemental encoder has access to the underlying state and to the task. This is not a claim that erased information can be regenerated solely from `r(x)`.

## 3. Composition and transport bounds

Let `s : R -> S` be a deterministic postprocessing of the existing realization. Write `sr=s∘r` and `K(sr,r)` for the maximum number of distinct intermediate `r` values within one `sr`-fiber.

**Theorem C (exact composition law).**

\[
K(r,F)\le K(sr,F)\le K(r,F)\,K(sr,r).
\]

Consequently
\[
B(r,F)\le B(sr,F)\le B(r,F)+B(sr,r).
\]

**Proof.** Every `r`-fiber lies in a single `sr`-fiber. Thus the largest possible count of distinct task answers cannot shrink after postprocessing. Conversely, each `sr`-fiber is the union of at most `K(sr,r)` intermediate `r`-fibers, each containing at most `K(r,F)` distinct `F` outputs. Counting their union yields the upper bound. Taking ceilings of base-2 logarithms gives the bit bounds. QED.

**Theorem D (average composition law).** Under any probability mass function `P`,

\[
H(F|R)\le H(F|S)\le H(F|R)+H(R|S)
\]

where `S=s(R)`.

**Proof.** As `S` is determined by `R`, the conditional mutual-information identity gives
`H(F|S)-H(F|R)=I(F;R|S)`. The right side belongs to `[0,H(R|S)]`. QED.

**Theorem E (decoding-error composition law).**

\[
E(R,F)\le E(S,F)\le E(R,F)+E(S,R).
\]

**Proof.** Any S-based decoder can be simulated from R, so the optimal R-decoder cannot be worse. For the upper bound, first decode R from S using an optimal function `h`, then decode F from the guessed R using an optimal function `g`. The composite can err only when `h(S)≠R` or `g(R)≠F`, so the union bound gives the claim. QED.

These three results give coherent *worst-case*, *average-uncertainty*, and *decision-error* loss budgets across cascades of transfer blocks.

## 4. Hilbert-space information projection and residual energy

Let `(Ω,𝓕,P)` be a probability space; let `F∈L²(P)` be a real-valued target. For an observation random variable `R`, define the conditional-expectation operator

\[
P_R F=\mathbb E[F\mid\sigma(R)].
\]

This is the orthogonal projector from `L²(P)` onto the closed subspace of square-integrable `σ(R)`-measurable random variables. Define the residual `Q_R=I-P_R` and the optimal squared prediction error

\[
M_R(F)=\|Q_R F\|_2^2.
\]

**Theorem F (exact transport loss identity).** If `S=s(R)` is deterministic postprocessing, then

\[
\boxed{M_S(F)-M_R(F)=\|P_R F-P_S F\|_2^2\ge 0.}
\]

**Proof.** Since `σ(S)⊂σ(R)`, the projector ranges are nested, and `P_S P_R=P_S`. Decompose
`F-P_S F=(F-P_R F)+(P_R F-P_S F)`. The first term is orthogonal to all `σ(R)`-measurable functions, while the second is `σ(R)`-measurable. Pythagoras gives the identity. QED.

**Komorebi interpretation:** a residual packet measures the prediction error inaccessible to a realization, and the loss created by a transfer is an exactly quantified orthogonal projection difference. This is standard conditional expectation / law of total variance in existing mathematics, but a natural bridge from Komorebi projector calculus to operational information.

## 5. A finite observable dynamics model

Let `X={(a,b,c): a,b,c∈{0,1}}`, with transition

\[
T(a,b,c)=(b,c,a\oplus b).
\]

At horizon `h`, observe `r_h(x)=(a(T^j x))_{j=0}^h`, where `a(x)` denotes the first coordinate. The task `F` is the first three observations `(a,b,c)`; equivalently, recover the initial state exactly. As h increases from 0 to 2, the observation separates 2, 4, and 8 states.

Two priors are evaluated:
- **Uniform:** every state has probability `1/8`.
- **Biased:** independent coordinates with `P(a=1)=1/2`, `P(b=1)=1/4`, and `P(c=1)=1/8`.

For the MSE column, use the scalar task `F_num=4a+2b+c`. This encodes all eight states injectively; squared-loss estimates are Bayes-optimal conditional means.

| Prior | h | Represented classes | Exact extra bits | H(F|r_h) bits | Optimal error | Optimal MSE for F_num |
|---|---:|---:|---:|---:|---:|---:|
| uniform | 0 | 2 | 2 | 2.000000 | 0.750000 | 1.250000 |
| uniform | 1 | 4 | 1 | 1.000000 | 0.500000 | 0.250000 |
| uniform | 2 | 8 | 0 | 0.000000 | 0.000000 | 0.000000 |
| biased | 0 | 2 | 2 | 1.354843 | 0.343750 | 0.859375 |
| biased | 1 | 4 | 1 | 0.543564 | 0.125000 | 0.109375 |
| biased | 2 | 8 | 0 | 0.000000 | 0.000000 | 0.000000 |

Under the biased prior, Theorem F predicts an exact MSE drop of `0.859375-0.109375=0.750000` from the first refinement and `0.109375` from the next. Both are certified consequences of the conditional-expectation decomposition.

## 6. Reproducible verification

Execute `python komorebi_information_probe_v0_1.py` with Python >= 3.9. No external libraries are required.

Verification performed in this environment:
- 199,017 triples of small finite maps tested for the exact composition inequalities and fixed-width bit-cost bounds. **PASS.**
- 2,000 seeded, randomized finite probability models tested for entropy monotonicity, entropy composition, Bayes error monotonicity, Bayes error composition, and the squared-error projection identity using exact rational arithmetic. **PASS.**
- Exact rational probability mass used for Bayes error and MSE. Shannon entropies computed in floating point; comparisons allow `1e-12` numerical tolerance.

This is **computational checking of instances**, not a formal proof of the general assertions. The proofs are in Sections 2–4.

## 7. Statistical estimation from observations

For any fixed decoder evaluated on `n` *independent held-out* observations, let `ê` denote its empirical 0-1 error. Hoeffding's bound yields

\[
\Pr(|\hat e-e|>\varepsilon)\le 2e^{-2n\varepsilon^2}.
\]

For `n=1000` and a nominal `95%` confidence level, this gives an approximately `±0.0429` error-rate confidence radius. It **does not** apply without adjustment when one both selects and evaluates the decoder on the same observations. Estimating conditional entropy reliably may require much stronger structural assumptions in large or continuous state spaces.

## 8. Connection to broader realizations

On a standard measurable probability space, the information accessible through `R` is naturally the sigma-algebra `σ(R)`. Under standard target-space assumptions, a task `F` is recoverable as `g(R)` precisely when it is `σ(R)`-measurable (Doob–Dynkin factorization). These conditions differ in detail from the *pointwise* finite fiber theorem if equality is required only almost surely.

In stochastic settings, Blackwell's order of statistical experiments compares observation channels via stochastic garblings. In prediction, computational mechanics identifies minimal sufficient predictive states by equivalence of future conditional distributions. These are existing mathematical pillars to integrate rather than claim as discoveries.

## 9. Next work and disconfirmation tests

1. **Lean:** formalize finite factorization and obstruction witnesses, exact repair alphabet, and composition of fiber-count repair costs. No Lean proof has been compiled in the current session; Lean binaries are unavailable here.
2. **Analytic:** formally link sigma-algebra inclusions and projections to generic Komorebi transfer blocks and residual objects.
3. **Stochastic:** use Markov kernels rather than only deterministic functions. Recover Blackwell/data-processing results without introducing contradictions.
4. **Cross-domain:** construct typed, non-toy realizations for polyphase signal recovery, residue lifting, and machine-state prediction; prove the *same* theorem yields useful estimates in all three.
5. **Novelty test:** formulate and prove at least one substantive new composition, repair-optimality, or obstruction propagation theorem *not already reducible to a direct restatement* of classical sufficiency or partition arguments.
6. **Failure criterion:** if no robust cross-domain translation survives detailed proof and stress testing, retain the result as a useful special-purpose information layer rather than labeling the entire framework a universal calculus of information.

### Verification ledger

| Obligation | Status |
|---|---|
| Define task-relative exact, entropic, and error deficits | DONE |
| Paper proofs of finite recoverability/repair/transport | DONE |
| Paper proof of Hilbert projection loss identity | DONE |
| Python exact example and finite tests | PASS |
| Lean compile/audit | NOT ATTEMPTED (runtime missing) |
| Infinite/stochastic/quantum extension | OPEN |
| New independent theorem demonstrating cross-domain value | OPEN |
| Universality claim | HYPOTHESIS, NOT ESTABLISHED |
