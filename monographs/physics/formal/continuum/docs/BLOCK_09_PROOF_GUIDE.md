# Block 09 — Explicit domains, countable continuity and a genuine unbounded model

Source: *Projector-Refinement Physics: Complete Unified Theory*, 550 physical PDF pages, Chapter 6.1–6.4, physical pages 30–33 (printed 17–20). This block targets (6.1)–(6.9), the spectral realization of (6.10)–(6.11) and (6.13)–(6.14), and the continuity/Parseval consequences (6.27)–(6.41). Equation (6.26)'s unitary group is **not constructed**. The source page images were inspected. Files did not supply three previews; the unchanged included PDF was rendered locally for them. The overbar in (6.34) is retained.

The authoritative current result is `verification/final/report.json`. This guide describes conditional mathematics and constructed spectral examples, not observational confirmation of the later physics.

## 1. Scope and inventory

| Module | Theorems | Definitions | Structures |
|---|---:|---:|---:|
| GraphDomain | 16 | 4 | 0 |
| CountableAtlas | 17 | 6 | 2 |
| CountableContinuity | 23 | 3 | 0 |
| DiagonalDomain | 14 | 6 | 0 |
| SpectralGraph | 13 | 0 | 0 |
| UnboundedExamples | 19 | 5 | 0 |
| DomainExamples | 11 | 5 | 0 |
| **Block 09** | **113** | **29** | **2** |

The cumulative inventory is **783 theorem declarations, 952 named declarations and 47 mathematical modules**. All 40 Block 08 mathematical files are byte-identical. Of the cumulative theorems, 39 are recovered Paper VII declarations and 744 are authored across nine full-edition blocks. These are declaration counts, including support lemmas and examples, not independent discoveries or a percentage of 550-page completion.

The generic spaces are complex inner-product spaces. The index type can be arbitrary; countable labels are a specialization. Sums are unconditional nets over finite subsets, not just one chosen enumeration. The constructed diagonal model uses the complete infinite-dimensional Hilbert space `ℓ²(ℕ, ℂ)`. The unbounded operator is never assigned a bounded-map type. Its individual projector maps are bounded.

## 2. An actual operator domain and graph norm

The generator has the type

```lean
T : H →ₗ.[ℂ] H
```

This is Mathlib's partially defined linear-map interface. It contains a complex-linear subspace `T.domain` and a linear map from that domain into H. Evaluation `T x` requires an actual domain element. No continuity or norm bound is assumed for this map.

`GraphDomain.graphMap` constructs the linear embedding

\[
x\longmapsto (x,Tx)\in H\oplus_2 H.
\]

Its actual `WithLp 2` product norm defines `graphNorm`. It is not the max/sup product norm. The formalization proves injectivity, definiteness, homogeneity and triangle inequality, and the literal identity

\[
\|x\|_T^2=\|x\|^2+\|Tx\|^2.
\]

For any filter and any domain-valued family x_a, it proves

\[
\|x_a-x\|_T\to0
\iff
x_a\to x\text{ in }H\quad\text{and}\quad Tx_a\to Tx\text{ in }H.
\]

It separately proves equivalence with the source's squared-error formulation. The ambient subtype norm is not silently relabeled as the graph norm.

`StrongAtlas` has only bounded projectors, idempotence, pairwise orthogonality, Hermiticity and strong reconstruction. It has no current, derivative or graph-convergence field. `DomainAtlas` adds only invariance of `T.domain` under each projector. Restricted projectors and their finite sums are then actually constructed on that domain.

`GraphCompatible` explicitly requires convergence of the graph-norm error of the finite sums. The two component limits and the vector `HasSum` of generator images are derived. Graph compatibility is not assumed by every domain atlas. A bounded operator is included as a consistency specialization, not used to represent all operators.

## 3. Actual derivatives and literal graph-compatible current limits

Define

\[
E_i(\psi)=\|P_i\psi\|^2,
\qquad J_{ij}(\psi)=2\operatorname{Im}\langle P_i\psi,TP_j\psi\rangle.
\]

Every application of T to a packet is justified by the domain-invariance field. Finite linearity is proved on that domain.

The analytic input is the original ambient state derivative, with the curve taking values in the true domain:

```lean
HasDerivAt (fun s => (psi s : H)) ((-Complex.I) • T (psi t)) t
```

No derivative of T, graph differentiability of psi, packet-energy derivative or continuity law is supplied as an input. Differentiating the bounded projection of the actual state gives

\[
E_i'(t)=2\operatorname{Im}\langle P_i\psi(t),T\psi(t)\rangle.
\]

The literal source route uses graph convergence to prove

\[
\sum_{j\in F}J_{ij}\longrightarrow
2\operatorname{Im}\langle P_i\psi,T\psi\rangle=E_i'(t).
\]

A quantified estimate is also checked:

\[
\left|\sum_{j\in F}J_{ij}-E_i'(t)\right|
\le2\|P_i\psi\|\,\|T S_F\psi-T\psi\|.
\]

The derivative and the limiting value are independently derived before they are identified.

## 4. Added strengthening: fixed rows need less than full graph convergence

For the current and conservation identities, formal symmetry on the domain is sufficient:

\[
\langle Tx,y\rangle=\langle x,Ty\rangle\quad(x,y\in D(T)).
\]

This is weaker than self-adjointness and is named `IsSymmetric`, not misleadingly called a complete self-adjoint operator. The constructed spectral model below satisfies actual equality with its adjoint.

For one fixed packet i, symmetry gives

\[
\langle P_i\psi,TP_j\psi\rangle
=\langle TP_i\psi,P_j\psi\rangle.
\]

The right side pairs the strongly convergent packet sum against the fixed vector TP_i psi. Therefore the scalar current row has an unconditional sum **without adding graph compatibility**:

\[
\sum_jJ_{ij}=2\operatorname{Im}\langle P_i\psi,T\psi\rangle.
\]

The stronger error bound is

\[
\boxed{\left|\sum_{j\in F}J_{ij}-E_i'(t)\right|
\le2\|TP_i\psi\|\,\|S_F\psi-\psi\|.}
\]

This is a strengthening relative to the source's stated graph-limit route, not a literature novelty claim. It does **not** prove convergence of TS_F psi in Hilbert norm or provide a bound uniform in i. Symmetry and packet-domain invariance remain essential inputs to this route.

`current_row_abs_summable` proves absolute summability of each real scalar row. This is derived from the unconditional real `HasSum`; it is not inferred from convergence of an arbitrary ordered series. No absolute summability of the entire double current array is asserted.

## 5. Boundary flux and global energy without illegal infinite interchanges

Symmetry and conjugate symmetry establish

\[
\langle P_j\psi,TP_i\psi\rangle
=\overline{\langle P_i\psi,TP_j\psi\rangle},
\qquad J_{ij}=-J_{ji}.
\]

For every finite receiving region B, the actual derivative is proved to equal

\[
\boxed{\frac{d}{dt}\sum_{i\in B}E_i(t)
=\lim_{F\uparrow I}\sum_{i\in B}\sum_{j\in F\setminus B}J_{ij}(t).}
\]

The proof first cancels the finite internal double sum. The identity is used eventually when F contains B. Only the finite receiving sum passes through the limit.

Strong completeness and finite Pythagoras yield the actual infinite Parseval statement

\[
\sum_i\|P_i\psi\|^2=\|\psi\|^2.
\]

For a supplied all-real-time domain-valued solution, differentiating the original state norm and using symmetry gives global norm constancy. Combined with Parseval this proves global packet-energy constancy. No infinite sum of derivatives or unrestricted double-current rearrangement is used.

This does not construct e^{-itT}, prove Stone's theorem locally, or establish existence/domain invariance/differentiability of a general unitary group. The source's (6.41) is covered as a conservation consequence along a supplied actual trajectory, not as proof of the construction in (6.26).

## 6. Constructed maximal spectral domain, including self-adjointness

For any real coefficient family lambda_i, define

\[
D(T_\lambda)=\{x\in\ell^2:\ (\lambda_i x_i)_i\in\ell^2\},
\qquad (T_\lambda x)_i=\lambda_i x_i.
\]

This is the maximal weighted domain, not only finitely supported vectors. The module constructs its subspace laws and partial linear operator. Coordinate projectors are actual bounded operators and are proved to preserve the domain. Finite coordinate approximations prove domain density.

The formalization proves formal symmetry, then tests the adjoint on the actual coordinate singletons to show

\[
(T_\lambda^*y)_i=\lambda_i y_i.
\]

Since T_lambda* y is an actual l2 vector, this coordinate formula forces y into the declared maximal domain. Together with the symmetric inclusion it gives

\[
\boxed{T_\lambda^*=T_\lambda.}
\]

Closedness follows from the imported adjoint theory. Self-adjointness, density, and graph compatibility are **proved properties of this construction**, not assumed fields.

The exact domain and graph norm formulas are

\[
x\in D(T_\lambda)\iff\sum_i\lambda_i^2|x_i|^2<\infty,
\qquad
\|x\|_{T_\lambda}^2=\sum_i(1+\lambda_i^2)|x_i|^2.
\]

Here `< infinity` is formalized by summability of the nonnegative real series. For natural-number labels, the literal tail is checked:

\[
\boxed{\|x-S_Mx\|_{T_\lambda}^2
=\sum_{n\ge M}(1+\lambda_n^2)|x_n|^2\longrightarrow0.}
\]

The code represents this tail as a tsum over n+M. The convergence is genuine, for every vector in the maximal domain, not eventual equality on a finite-support test set.

## 7. Genuine unboundedness and topology-sensitive exact tests

Set lambda_n=n+1/2. The resulting spectral harmonic model is self-adjoint and graph-compatible on l2(N,C). Norm-one coordinate vectors satisfy

\[
\|e_n\|=1,\qquad\|T e_n\|=n+\tfrac12.
\]

Lean proves that no finite real constant bounds \|Tx\| by C\|x\| over the domain, and that no bounded everywhere-defined operator agrees with T there.

For the actual domain sequence

\[
u_n=\frac{e_n}{n+1/2},
\]

it proves

\[
u_n\to0\text{ in Hilbert norm},\qquad
Tu_n=e_n,\qquad\|Tu_n\|=1,
\]

and rejects generator-image convergence to zero and graph convergence. The exact squared graph norm is

\[
\|u_n\|_T^2=(n+1/2)^{-2}+1.
\]

These are sequence-limit and universal unboundedness proofs, not numerical checks at finitely many n. The sequence u_n is **not** presented as the truncations of one fixed state or as a counterexample to the separately proved coordinate graph compatibility.

This is a spectral multiplier realization. Its unitary equivalence to the differential harmonic oscillator on L2(R), the form-domain D(T^{1/2}), and the full physical oscillator realization remain separate. The spectral coordinate currents are proved zero and are not advertised as nonzero transport.

## 8. Separate nonzero derivative consistency test

`DomainExamples` embeds the earlier two-sector rotation into the partial-map interface using the genuine bounded Hamiltonian H=iA. Its graph compatibility and symmetry are proved. The actual current values are -2 and +2. The original affine state curve satisfies the required ambient evolution derivative at zero, and the generic domain theorem yields packet derivative -2 and a current row with that nonzero sum.

The reverse amplitude without conjugation is proved false. This is a finite-dimensional local derivative witness, not the unboundedness example, not a global solution, and not a claim that all spectral currents are nonzero.

## 9. Verification and remaining boundaries

The cumulative verifier removes local compiled outputs, recompiles 47 mathematical modules and the aggregate with one worker and warnings as errors, and audits all 952 inventoried names, including structures and proof-bearing definitions. Six new invalid controls bring the cumulative control count to 65. Each must produce its own intended diagnostic in its mapped source range. An import failure, timeout or nonzero batch exit alone is insufficient.

All 40 prior mathematical modules are checked against `reference/block08_preservation.json`; all earlier preservation layers remain active. The v0.8.0 baseline was freshly reverified before extension. Lean is 4.34.0-rc2; Mathlib is pinned to aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Nine clean pinned dependency repositories are checked. Only propext, Classical.choice and Quot.sound are allowed axiom dependencies. Imported Lean/Mathlib caches are reused, not rebuilt wholesale. No admissions, custom axioms, native evaluation or disabled kernel checks occur in active mathematics.

The completed final report controls release status. The external fresh-extraction receipt reports the second complete run and hashes the unchanged ZIP. Development failures remain separate and are documented in `BLOCK_09_FAILURES.md`.

Not covered: construction of a general unitary group or solution, physical differential-oscillator identification, full form-domain hierarchy, Section 6.3's bounded functional surrogates and operator-norm limits, Section 6.5's infinite coarse-cell domain/rearrangement obligations, spectral residue/ladder routing, countable dilation, measurement instruments, zero-probability entropy extensions, continuum gravity, cosmology, or empirical adequacy. No finite-stage floating-point residual is relabeled as a universal theorem.

**Next target:** Chapter 6.3's actual bounded diagonal multipliers and topology-specific truncation, including resolvent, heat, unitary, bounded and Cayley tails. Keep heat-time and denominator assumptions explicit. Also retain the unclosed D(T^{1/2}) hierarchy of 6.2 and coarse-cell obligations of 6.5 in the ledger.
