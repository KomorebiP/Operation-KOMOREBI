# Block 13 — Finite characters, infinite residue masks and maximal ladder domains

Komorebi Physics Lean v0.13.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, physical PDF page 33 of 550, printed page 20, Section 6.6, equations (6.48)–(6.52). The source page image was inspected. The original PDF is unchanged. The authoritative cumulative result is `verification/final/report.json`; a source inventory or this guide alone is not a completed audit.

## 1. Inventory and scope

| New module | Theorems | Other inventoried declarations | Role |
|---|---:|---:|---|
| ResidueCharacters | 10 | 0 | Exact character orthogonality, exponential convention and sign test |
| ResidueProjectors | 21 | 4 | Actual finite operator average, infinite mask identity and domain preservation |
| LadderDomains | 16 | 6 | Actual lowering/raising partial maps and their common maximal domain |
| LadderAdjoints | 13 | 0 | Equality with actual unbounded adjoints, closedness and norm identities |
| LadderRouting | 10 | 1 | Domain-valued input projection and both modular routing laws |
| LadderExamples | 20 | 0 | Exact wraparound, vacuum, normalization and unboundedness tests |
| **Block 13** | **90** | **11** | **101 new inventoried declarations** |

The cumulative inventory contains 1,173 theorem declarations, 1,397 inventoried names and 71 mathematical modules. There are 95 negative controls. All 65 Block 12 mathematical files remain byte-identical. Of the 1,173 theorems, 39 are recovered Paper VII declarations and 1,134 are full-edition declarations. Counts include support lemmas and exact examples. They are not independent physical discoveries or a completion percentage for the 550-page edition.

The ambient space is the actual infinite-dimensional complex Hilbert space `Space = lp (fun _ : Nat => Complex) 2`. The modulus M is an arbitrary natural number with `[NeZero M]`, which implies M>0. Residue labels are `ZMod M`, with canonical representatives in 0,...,M-1. This is not verification at a finite list of moduli or a finite cutoff of the state space.

## 2. Finite character selection with the literal phase signs

Let chi_M(j)=exp(2 pi i j/M), evaluated on residue classes. The construction uses Mathlib's standard additive character, together with its proved primitive-character orthogonality. The new theorem derives

\[
\frac1M\sum_{k\in\mathbb Z/M\mathbb Z}
\chi_M(-rk)\chi_M(kn)
=\begin{cases}1&n=r\pmod M,\\0&\text{otherwise}.\end{cases}
\]

`character_nat`, `character_negative_nat` and `character_product_exponential` prove the actual complex exponential formulas. `exponential_selection` consequently has the literal negative receiving phase and positive number-spectrum phase. The finite index type enumerates canonical residues exactly once; no floating-point roots of unity or tolerance test is used.

The sign and normalization are material. At M=3 and receiving/input labels r=n=1, changing the receiving phase to the plus sign gives exactly zero, not one. With the correct signs but without the 1/M prefactor, the sum is exactly three, not one. Both opposite facts are checked theorems and are used by separate invalid controls.

## 3. The operator average is proved equal to an infinite mask: (6.48)–(6.49)

For each k, `rotationSymbol` constructs the actual bounded sequence chi_M(kn), using its unit modulus. `rotation` is the bounded diagonal operator on all l2 vectors associated with that sequence. Its coordinate formula, group law and inverse identity are proved.

Before supplying any mask, define the actual bounded-operator sum

\[
Q_r^{(M)}:=\frac1M\sum_k\chi_M(-rk)\,R_k,
\qquad (R_kx)_n=\chi_M(kn)x_n.
\]

`projector_apply` applies the scalar character theorem to every coordinate of an arbitrary l2 vector and proves

\[
(Q_r^{(M)}x)_n=\mathbf1_{\{n\bmod M=r\}}x_n.
\]

The result is then upgraded to equality of actual bounded operators:

\[
\boxed{Q_r^{(M)}=\operatorname{mask}\{n:n\bmod M=r\}.}
\]

The mask is the strong infinite-cell projector constructed in Block 12. `projector_hasSum` proves the genuine strong series identity on every x:

\[
\boxed{\sum_{n\equiv r\ (\mathrm{mod}\ M)}P_nx=Q_r^{(M)}x.}
\]

This is a `HasSum`, not equality to an infinite-sum notation without a convergence proof. No generator-domain restriction is needed for this bounded projector identity.

The new proofs supply Hermiticity, idempotence, orthogonality between different labels, completeness and the norm bound at most one. The probability/weight identity also has a genuine scalar `HasSum`:

\[
\|Q_r^{(M)}x\|^2=\sum_{n\equiv r\ (\mathrm{mod}\ M)}|x_n|^2.
\]

### The number operator is not silently replaced by the harmonic Hamiltonian

`rotation_eq_number_evolution` identifies R_k with the previously constructed spectral evolution for eigenvalues n at time -2 pi k/M. Since that evolution is exp(-itN), its multiplier is exp(+2 pi i kn/M). `projector_number_average` proves (6.48) using those actual operators and the literal exponential weights.

The source uses the number spectrum n here. The harmonic Hamiltonian spectrum n+1/2 would introduce an additional phase. It is not substituted for N. The projector nevertheless preserves the maximal domain of every real diagonal generator and commutes with each of its constructed spectral evolutions, by the separately proved mask identities.

## 4. The ladders are actual partial operators on their maximal domains

For a sequence x, the raw coordinate formulas are

\[
(ax)_n=\sqrt{n+1}\,x_{n+1},
\qquad (a^\dagger x)_0=0,
\qquad (a^\dagger x)_{n+1}=\sqrt{n+1}\,x_n.
\]

These first define linear maps on raw sequences. A raw result is not automatically an l2 vector. `lower_mem_iff` and `raise_mem_iff` prove, for every original x in l2,

\[
ax\in\ell^2\iff\sum_n n|x_n|^2<\infty,
\qquad
 a^\dagger x\in\ell^2\iff\sum_n n|x_n|^2<\infty.
\]

The raising formula initially gives the weight n+1. Its equivalence with the n-weighted condition uses the original x being in l2, not an omitted term at the vacuum. Define

\[
\mathcal D=\{x\in\ell^2:\sum_n n|x_n|^2<\infty\}.
\]

It is the previously constructed maximal diagonal domain for the symbol sqrt(n). Only after the square-summability proofs are complete does the code construct `lower` and `raise` as partially defined linear maps from Space to Space with actual domain D. The domain is proved dense. Neither operator is declared bounded on all l2.

These results identify the maximal domains for the stated coordinate formulas, not just a finitely supported invariant core. They do not assert that the ladder outputs belong to D again. Products such as a-dagger a and repeated unbounded compositions require additional membership proofs.

## 5. The dagger notation is justified by actual adjoint equality

First, `formalAdjoint` proves the inner-product identity on D by shifting absolutely convergent scalar inner-product series, retaining the zero boundary coordinate. The stronger results are

\[
\boxed{a^*=a^\dagger,\qquad (a^\dagger)^*=a.}
\]

These are equalities of Mathlib's actual partially defined adjoints, including equality of domains. To exclude additional adjoint-domain vectors, the proof tests the adjoint relation on each coordinate basis vector. This forces the adjoint's coordinates to equal the opposite ladder's raw formula. Since an actual adjoint output lies in l2, the earlier maximal-domain criterion forces the input to belong to D. The reverse inclusion follows from the proved formal-adjoint identity and density.

Both ladders are therefore proved closed. Adjointness and closedness are conclusions, not fields installed in a proposed ladder structure.

The exact norm formulas are also checked:

\[
\|ax\|^2=\sum_n n|x_n|^2,
\qquad
\|a^\dagger x\|^2=\sum_n(n+1)|x_n|^2,
\]

\[
\boxed{\|a^\dagger x\|^2=\|ax\|^2+\|x\|^2.}
\]

This is a quadratic norm identity on D. It is not presented as an operator commutator theorem on an unproved product domain.

## 6. Actual residue routing with the domain obligations discharged: (6.50)–(6.52)

Every Q_s preserves D. `packet` is a domain-valued linear map constructed only after this membership theorem. Thus a Q_s x and a-dagger Q_s x are genuine l2 vectors for every x in D.

The coordinate proofs yield the stronger intertwining identities

\[
\boxed{aQ_sx=Q_{s-1}ax,\qquad a^\dagger Q_sx=Q_{s+1}a^\dagger x.}
\]

Orthogonality then gives the source's zero-corner assertions:

\[
\boxed{Q_raQ_sx=0\quad(r\ne s-1),}
\qquad
\boxed{Q_ra^\dagger Q_sx=0\quad(r\ne s+1).}
\]

Subtraction is in ZMod M. It is not natural-number subtraction, which would incorrectly erase modular wraparound at label zero. This label arithmetic is separate from the physical vacuum: the operator itself satisfies a e_0=0, while a-dagger e_0=e_1. The proof does not create a negative-index basis state.

The allowed corner equals the full corresponding ladder output. Summing all output residue projections reconstructs the actual l2 output. None of these statements assumes that an output is in D for a second unbounded application.

## 7. Nonzero exact examples and genuine unboundedness

Lean proves the basis actions with their square-root amplitudes:

\[
a e_{n+1}=\sqrt{n+1}\,e_n,
\qquad a^\dagger e_n=\sqrt{n+1}\,e_{n+1}.
\]

For M=3, the exact wraparound examples are

\[
\boxed{Q_2aQ_0 e_9=3e_8,\qquad Q_0a^\dagger Q_2 e_8=3e_9.}
\]

Both examples act in the genuine infinite-dimensional space with actual domain-valued inputs. Wrong receiving lanes are proved zero. The first displayed output is proved nonzero and has squared norm nine. Replacing sqrt(9) by nine is separately proved wrong.

The norm-one coordinate vectors also prove that no real constant C bounds either ladder on its domain:

\[
\neg\exists C\ \forall x\in\mathcal D:\|ax\|\le C\|x\|,
\qquad
\neg\exists C\ \forall x\in\mathcal D:\|a^\dagger x\|\le C\|x\|.
\]

There is consequently no bounded everywhere-defined linear operator agreeing with either ladder on D. These are universal nonexistence proofs using growing basis norms, not observations from a bounded test range.

## 8. Verification contract and failures

The production verifier freshly recompiles all 71 mathematical modules plus the aggregate with one worker and warnings as errors. It audits all 1,397 inventoried names, including the eleven new constructors/definitions, checks all 95 intentionally invalid controls and checks every historical preservation layer, including all 65 Block 12 mathematical sources.

The eight new invalid controls cover the wrong character sign, missing normalization, wrong square-root amplitude, two incorrect routing lanes, failure to annihilate the vacuum and two false bounded-extension claims. Every control must produce its own intended diagnostic in its mapped source range. A timeout, import failure or nonzero batch exit alone does not satisfy the contract. Their separate complete development batch passed, after an earlier outer execution-window interruption that is not counted as a pass.

Seven mathematical development compilations failed on API/linter compatibility, summability type inference, dependent rewriting, domain-coercion normalization and exact-example arithmetic. They were repaired without admissions or weakened statements; snapshots and logs remain under `verification/development/block13/`. Two supplementary API inspection commands were interrupted by outer execution windows and did not establish any result. See `BLOCK_13_FAILURES.md` for the exact records and repairs.

The 1,083-theorem Block 12 baseline was freshly verified before extension, with report `verification/block12_baseline/report.json`. Lean is 4.34.0-rc2, Mathlib is aeb72f1e9981b6d35b426b16dca7759be3e7ba06, and all nine clean pinned dependency trees are checked. Imported dependency caches are reused, not rebuilt wholesale. Runtime restoration succeeded with all seven part hashes checked; runtime bytes remain external. Only propext, Classical.choice and Quot.sound are allowed axiom dependencies. No active admissions, custom axioms, native evaluation or kernel-bypass options are used.

The completed production report determines current PASS status. The finished ZIP is then independently extracted and the full cumulative verifier rerun; that external receipt refers to the unchanged archive.

## 9. Boundaries and next source target

Section 6.6 is formalized in the actual sequence-space oscillator realization under its positive-modulus and maximal-domain assumptions. This does not establish differential-oscillator equivalence on L2(R), a general spectral representation or Stone theorem, the full harmonic half-power domain hierarchy, product-domain equalities for a-dagger a or a a-dagger, canonical commutation on such a domain, or coherent-state factorial-lane weights. The source's coherent-state sentence points to a companion chapter; no such probability formula is newly proved here.

No arbitrary unbounded composition, infinite current rearrangement, nonlinear/dissipative solution, density positivity-preserving semigroup, continuum gravitational model, cosmological model or empirical claim is discharged by this block. Existing bounded/unbounded, summability and positivity boundaries remain.

**Next literal target:** Section 6.7, equations (6.53)–(6.56), the nonreducing-packet resolvent-commutator certificate. Keep actual domain invariance, genuine two-sided resolvent identities, the bounded extension of [H,P], the negative sign and the nonreal resolvent parameter explicit. An expression naming an inverse or a commutator is not a substitute for those proofs.
