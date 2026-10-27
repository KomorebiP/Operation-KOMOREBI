# Block 05 — Lindblad jumps, coherence loss and detailed balance

Komorebi Physics Lean v0.5.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, 550 pages, physical PDF pages 25–26 (printed 12–13). The literal targets are Chapter 4.7, equations (4.45)–(4.52), and Chapter 4.8, equations (4.53)–(4.58). The source page images were inspected. The authoritative cumulative result is `verification/final/report.json`.

## Scope and inventory

| New module | Theorems | Definitions | Role |
|---|---:|---:|---|
| `LindbladJumps` | 26 | 5 | Actual square-root jumps, full matrix generator and actual population derivatives |
| `DetailedBalance` | 28 | 6 | Relative-entropy derivatives, nonnegative dissipation, zero-rate edges, equality conditions and matrix-flow bridge |
| `LindbladDynamics` | 14 | 3 | Constructed coordinate atlas, coherent-plus-jump flow, coarse flux and information derivatives |
| `LindbladCoherence` | 5 | 1 | Exact off-diagonal generator and actual coherence derivative |
| `LindbladExamples` | 25 | 5 | Exact coherent mixed-state witness and hypothesis-sensitivity tests |
| **Block 05** | **98** | **20** | 73 general/support theorems and 25 example/support theorems |

The cumulative inventory is **402 theorem declarations**, **490 named declarations**, and **25 mathematical modules**. The previous 20 mathematical files are unchanged. The 402 comprise 39 recovered Paper VII declarations and 363 authored in the five full-edition blocks. These are declaration counts, not independent discoveries and not a percentage of the full physics edition.

## 1. Actual square-root jump matrices: (4.45), (4.51), (4.52)

For a finite complex matrix basis, the receiving label is the first index and the source is the second. Define

\[
L_{ab}=\sqrt{\gamma_{ab}}\,|a\rangle\langle b|,\qquad \gamma_{ab}\ge0.
\]

`LindbladJumps.jump` is the actual `Matrix.single a b (Real.sqrt (gamma a b) : Complex)`, not a formal symbol with multiplication identities assumed. The proofs establish

\[
L_{ab}^\dagger L_{ab}=\gamma_{ab}|b\rangle\langle b|,
\quad L_{ab}L_{ab}^\dagger=\gamma_{ab}|a\rangle\langle a|,
\quad L_{ab}\rho L_{ab}^\dagger=\gamma_{ab}\rho_{bb}|a\rangle\langle a|.
\]

The gain identity holds for **every complex input matrix**, with no diagonal-state assumption. Nonnegative rates discharge the actual real-square-root normalization. Negative rates are not silently treated as valid transition rates.

## 2. The actual generator gives the population law: (4.46)–(4.50)

The full one-jump expression is

\[
\mathcal D_L(\rho)=L\rho L^\dagger-\tfrac12(L^\dagger L\rho+\rho L^\dagger L),
\qquad
\mathcal L_\gamma(\rho)=\sum_{a\ne b}\mathcal D_{L_{ab}}(\rho).
\]

Both loss terms and the half factor remain in the definition. The finite sum excludes self-jumps, literally matching the source. `dissipator_jump_entry` calculates every matrix entry, not only populations. Its diagonal specialization and finite rearrangement prove

\[
(\mathcal L_\gamma\rho)_{ii}=\sum_b(\gamma_{ib}\rho_{bb}-\gamma_{bi}\rho_{ii}).
\]

Define real populations `population rho i = (rho i i).re` and

\[
K_{ib}=\gamma_{ib}p_b-\gamma_{bi}p_i.
\]

`population_cast` proves that the real population, cast back to the complex numbers, equals the literal diagonal of a Hermitian matrix. The interpretation as nonnegative normalized probabilities follows separately from an already positive semidefinite trace-one input, via the newly constructed coordinate atlas. Positivity is not assumed when establishing the algebraic reduction.

The analytic input is precisely

```lean
HasDerivAt rho (LindbladJumps.generator gamma (rho t)) t
```

along with nonnegative rates. `hasDerivAt_population` derives the coordinate derivative using continuous linear evaluation and the real-part map, then substitutes the proved generator formula:

\[
\boxed{\dot p_i=\sum_b K_{ib}.}
\]

**The scalar gain–loss law is a conclusion, not an input to this matrix theorem.** The current is proved antisymmetric, the total current sum is zero, and every finite subsystem has the actual boundary-flux derivative. Trace cancellation is also established directly for an arbitrary one-jump matrix expression. `trace_constant` permits state- and time-dependent rates along a given all-real-time trajectory; it does not construct that trajectory.

## 3. Coherences and coherent-plus-jump dynamics

Let the total rate leaving source i be

\[
\lambda_i=\sum_{a\ne i}\gamma_{ai}.
\]

For i different from j, the full-entry calculation proves

\[
\boxed{(\mathcal L_\gamma\rho)_{ij}=-\tfrac12(\lambda_i+\lambda_j)\rho_{ij}.}
\]

`hasDerivAt_coherence` derives the actual complex derivative from the original matrix derivative. It is not an integrated exponential solution theorem. Self-jumps have zero population contribution, but generally nonzero coherence contribution. Thus the exclusion of self-jumps in the source is preserved rather than erased because their diagonal terms vanish.

The separate combined generator is

\[
\mathcal G(\rho)=-i[H,\rho]+\mathcal L_\gamma(\rho).
\]

Under the stated Hermiticity assumptions, its actual population derivative is the row sum of **both** the old Hamiltonian current and the newly derived jump current. Hermiticity of the rate, trace cancellation and subsystem flux are proved for this combined expression. Dropping coherent current is rejected by an exact witness.

For arbitrary finite address coarsening, the derivative of a coarse population is exactly the double-summed fine current. This does **not** postulate a state-independent closed coarse rate matrix; no lumpability condition is being hidden. Shannon, fixed real-order moment and Rényi derivative interfaces now consume the original jump-matrix derivative. The combined model has a Shannon derivative identity with its full current, not an unconditional entropy-production sign.

## 4. Detailed balance with valid logarithm domains: (4.53)–(4.58)

Take a fixed positive reference pi satisfying

\[
\gamma_{ab}\pi_b=\gamma_{ba}\pi_a,
\qquad \pi_a>0.
\]

Set r_a=p_a/pi_a and c_ab=gamma_ab pi_b. Detailed balance makes c symmetric. The actual current satisfies

\[
K_{ab}=c_{ab}(r_b-r_a).
\]

For strictly positive populations, differentiating the actual scalar function

\[
D(p\Vert\pi)=\sum_a p_a\log(p_a/\pi_a)
\]

and using the proved antisymmetric weighted identity gives

\[
\boxed{\frac{dD}{dt}=-\mathcal E,\qquad
\mathcal E=\tfrac12\sum_{a,b}c_{ab}(r_a-r_b)(\log r_a-\log r_b)\ge0.}
\]

The scalar derivative of x log(x/pi) is proved first. `hasDerivAt_relativeEntropy` assumes the actual component flow and derives the displayed derivative. **`hasDerivAt_matrix_relativeEntropy` instead starts with the original matrix Lindblad derivative and discharges component balance through `hasDerivAt_population`.** No entropy law is assumed in either case.

The inequality comes from nonnegative conductances and the monotonicity of the logarithm. The stronger scalar result `(x-y)(log x-log y)=0 iff x=y` is also proved on positive arguments. `relativeEntropy_antitoneOn` turns the derivative sign into nonincrease on a convex time set for a supplied strictly positive actual solution; the rates may vary with time, provided they obey detailed balance with the same fixed reference at each time. Derivatives are assumed on that time set, including endpoints.

Normalization is not needed for the derivative identity. For the probability-relative-entropy interpretation, positive normalized p and pi are required. `relativeEntropy_nonneg` separately proves Gibbs nonnegativity for that normalized domain. Zero probability is not included in the differentiability theorem.

### The zero-rate correction

The source flux-ratio expression contains

\[
(\gamma_{ab}p_b-\gamma_{ba}p_a)\log\frac{\gamma_{ab}p_b}{\gamma_{ba}p_a}.
\]

When both rates vanish, that displayed ratio is 0/0 in ordinary real analysis. The proof does **not** use Lean's totalized logarithm/division to silently declare it valid. Instead `activeFluxCost` explicitly returns zero when gamma_ab=0. The following are then proved:

- With positive pi and detailed balance, gamma_ab=0 exactly when gamma_ba=0.
- With nonnegative rates and positive p, both directed fluxes on an active edge are strictly positive.
- The explicitly defined active-edge cost equals c_ab(r_a-r_b)(log r_a-log r_b).
- The sum of active-edge costs gives exactly the source's derivative with the inactive-edge convention made explicit.

The conductance formula is valid with zero rates without ever logging a zero flux. This is a domain clarification and strengthening of the formal statement, not a claim that the entire physical theory has been validated.

### Equality is not automatic equilibration

`dissipation_zero_iff` proves that zero dissipation is equivalent to r_a=r_b on every positive-rate directed edge. An additional theorem proves p=pi when every distinct pair has strictly positive rate and p and pi are positive normalized distributions on a nonempty finite type. That is an explicit sufficient connectivity assumption, **not** a formalized theorem for every irreducible transition graph or a convergence-rate theorem. A zero-rate graph supplies an exact counterexample to uniqueness without a connectivity hypothesis.

## 5. Exact witnesses

Reuse the previously checked positive trace-one mixed density

\[
\rho=\begin{pmatrix}1/2&1/4\\1/4&1/2\end{pmatrix},
\quad \gamma_{01}=4,\quad\gamma_{10}=1.
\]

The new exact matrix result is

\[
\mathcal L_\gamma(\rho)=
\begin{pmatrix}3/2&-5/8\\-5/8&-3/2\end{pmatrix}.
\]

The actual local affine matrix curve rho+t L_gamma(rho) satisfies the original flow derivative at zero. Applying the general theorems produces population derivatives +3/2 and -3/2 and coherence derivative -5/8 there. The detailed-balance reference is pi=(4/5,1/5), and the exact relative-entropy derivative is

\[
D'(0)=-3\log 2<0.
\]

For a second PSD trace-one input diag(3/4,1/4), with the same nonnegative rates but the **wrong** reference (1/2,1/2), an actual local matrix-flow witness gives

\[
D'(0)=\tfrac14\log 3>0.
\]

The reference is proved not detailed-balanced. This is not a contradiction: the sign theorem's omitted hypothesis is genuinely necessary for that reference-dependent claim. The affine witnesses are local, not claimed to stay positive for all real time or solve the ODE away from zero.

Other exact proofs detect source/receiver reversal, using the rate instead of its square root, negative rates, omitted loss terms, an omitted anticommutator half, incorrect self-jump cancellation, omission of coherent current, and uniqueness without active transitions. Eleven new intentionally invalid compilation controls separately reject those false variants and the wrong coherence/relative-entropy signs. A timeout or import failure never counts as rejection.

## 6. Verification and limitations

The completed final report is authoritative. The cumulative verifier deletes local compiled outputs, rebuilds all 25 mathematical modules plus the aggregate, audits all 490 named declarations including proof-bearing definitions, requires all 34 negative controls to fail with designated proof diagnostics, and checks all 20 Block 04 mathematical files against preserved SHA-256 values. The starting 304-theorem Block 04 audit was freshly rerun successfully before extension.

Lean is 4.34.0-rc2. Mathlib is pinned to aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine dependency revisions and clean tracked trees are checked. The imported compiled dependency cache is used, not independently rebuilt wholesale. Only propext, Classical.choice and Quot.sound are permitted axiom dependencies. Failed development snapshots and receipts remain separate from checked sources.

This release does not prove ODE existence or uniqueness, positivity preservation from initial data, construction of a completely positive dynamical semigroup, zero-population entropy limits, q=1 limits, general graph convergence or rates, closed coarse Markov evolution without lumpability, infinite-dimensional trace-class results, countable/unbounded limits, gravity, cosmology or empirical adequacy. The proved relative entropy is classical packet/population relative entropy, not quantum relative entropy of two density operators.

**Next literal source: Chapter 4.9, equations (4.59)–(4.67), the general refinement-cancellation tower.** Exact coefficient cancellation must be separated from analytic asymptotic remainder bounds. Chapter 3's unit, variational and asymptotic claims also remain separately uninventoried.
