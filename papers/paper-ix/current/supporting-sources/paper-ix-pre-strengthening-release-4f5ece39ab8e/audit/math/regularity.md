# Independent mathematical audit: Paper IX, Section 40

Normalized claim: Over a complete nontrivially normed field K, for every finite e,k ≥ 0 and polynomial system F: K^(e+k) → K^e, an exact root a=(y₀,t₀) with invertible actual solved Jacobian J=D_YF(a) has an analytic local root graph on open neighborhoods U,V, unique among roots with t∈U and y∈V. The graph has strict derivative −J⁻¹K, where K=D_TF(a). A continuous supplied root selection through the base root has the same germ; on an open parameter set, pointwise nonsingularity gives this regularity at every parameter. Integral p-adic coefficients and centers are included into Q_p before applying the analytic result.

**Primary mathematical verdict: proved as written.** No missing mathematical hypothesis, counterexample, invalid implication, or manuscript correction was identified in this section. The named external inverse-function input was independently checked in its exact required mathematical form in current official Mathlib documentation and source. This is a mathematical audit, not a newly performed Lean compilation.

**Separate formal-provenance boundary:** Authentication of the exact historical Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06` remains conditional. Its source bodies and the pinned Lean kit are absent from the inspected archive; attempts to open the pinned upstream files returned `DisabledError`. The supplied JSON records source hashes and a historical compiler report, but those records are not a fresh inspection or rerun. Current official source versions are identified below and were not silently substituted for the historical revision.

## Scope, source, and independence

Audited the raw current `manuscript/consolidated/sections/40_regularity.tex`, before consulting its development source-leaf report. Independently reconstructed polynomial evaluation, augmented matrix inversion, the product-neighborhood argument, supplied-selection transfer, and coefficient inclusion. Read the raw Lean bodies attached to the relevant declarations to compare their actual contracts with the manuscript. This is an isolated subagent audit of this section, not an inference from source-verdict dashboards. No manuscript or Lean file was edited.

Section SHA256: `32f48dcc51d918d65be6dc827f31b05bc9870decb20dc596fed9276940244ffd`.

No applicable project AGENTS.md was found in the supplied workspace. The proof-audit and literature-check skills and the general logic/typing, topology, external-source, and computation-dependent obligation checklists were read. A project `.mathbox` ledger was not found in the inspected archive. Spectral sequences, representation theory, and graded-sign checklists are inapplicable to these claims.

## Claim cards

| ID / exact manuscript locator | Quantified claim and hypotheses | Mathematical conclusion / evidence type |
|---|---|---|
| REG-1, `lem:actual-polynomial-derivative`, lines 25–49 | Any finite polynomial P over complete nontrivially normed K; any evaluation point a | Analytic evaluation and strict Fréchet derivative ∑_j (∂_jP)(a)v_j; internal polynomial-induction proof plus polynomial-analyticity external input |
| REG-2, `lem:augmented-analytic-inverse`, lines 55–80 | Polynomial F:K^(e+k)→K^e; J invertible at a; no root hypothesis needed here | Φ=(F,T) has derivative [[J,K],[0,I]] with explicit two-sided inverse; its strict local inverse is analytic; internal matrix algebra plus external strict/analytic inverse theorems |
| REG-3, `thm:analytic-local-graph`, lines 89–143 | REG-2 and F(a)=0; e,k finite, possibly zero | Open U,V, globally typed ψ with analytic restriction, ψ(t₀)=y₀, ψ(U)⊆V, both directions of the root equivalence on U×V, strict derivative −J⁻¹K, differentiability on U |
| REG-4, `thm:selection-regularity`, lines 149–164 | REG-3 and ambient h continuous at t₀, h(t₀)=y₀, local exact root equation | Local equality h=ψ, analytic germ, strict derivative at t₀; internal continuity/local-uniqueness argument |
| REG-5, `cor:selection-open-regularity`, lines 170–187 | Open U, continuous h on U, exact roots and invertible solved Jacobian at every t∈U | Analyticity and strict derivative −J_t⁻¹D_TF(h(t),t) at every point; pointwise application of REG-4 |
| REG-6, `cor:integral-analytic-graph`, lines 192–212 | Any prime p; integral F,a; exact root; included solved Jacobian invertible in Q_p | Ambient Q_p root graph and included derivative formula; coefficient/evaluation/partial-derivative compatibility plus REG-3 |

All vectors and matrices use equation rows and variable columns. J is e×e, K is e×k, and −J⁻¹K maps K^k to K^e. There is no grading, equivariance, or completion beyond the complete normed-field/finite-coordinate-space hypotheses. The integral corollary makes no claim that Z_p is a Q_p-vector space or that its graph takes integral values throughout an unshrunk parameter set.

## Dependency graph

1. Formal partial-derivative identities and strict sum/product rules → actual strict derivative of each polynomial evaluation.
2. Finite coordinate assembly and continuity of matrix actions → system derivative represented by the actual Jacobian.
3. Polynomial analyticity → analyticity of Φ.
4. Two-sided triangular-block multiplication and J invertible → continuous derivative equivalence A for Φ.
5. Completeness of K^(e+k) + strict derivative A → open partial homeomorphism R for Φ and strict derivative A⁻¹ of its inverse g at Φ(a). **Named external leaf: strict inverse-function theorem.**
6. Analyticity of Φ + derivative equivalence + a∈R.source → analyticity of that same g at Φ(a). Openness of the analytic locus supplies a neighborhood. **Named external leaves: analytic inverse theorem and openness of analyticity.**
7. F(a)=0 + projection/injection composition → ψ(t)=π_Yg(0,t), base value, analyticity at t₀, derivative −J⁻¹K.
8. Product openness + target membership + continuity of ψ at t₀ → common open U,V on which both inverse identities apply and ψ(U)⊆V → complete root graph.
9. Continuity of supplied h at t₀ → eventual h(t)∈V → equality with ψ → transfer of analytic/strict-differentiability germ.
10. Open parameter set + pointwise hypotheses → REG-4 at each point.
11. Inclusion Z_p→Q_p commutes with polynomial evaluation and formal differentiation → included input satisfies REG-3.

No dependency points back to a conclusion it is used to establish. Historical quantitative charts are not needed to prove REG-3; the final paragraph expressly leaves their direct Lean identification as an interface task.

## Obligation matrix

| Obligation | Status | Decisive check |
|---|---|---|
| Exact domains and finite dimensions | passed | System has exactly e solved equations and e+k variables; derivative source/target dimensions agree |
| Polynomial strict derivative | passed | Constants, addition, and P·X_j induction reproduce the formal derivative without factorial division or characteristic-zero assumptions |
| Continuity of linear maps | passed | Finite matrix actions are bounded in coordinate sup norms; inverse is another finite matrix |
| Two-sided invertibility | passed | Both A·B and B·A have diagonal I and upper-right zero; order of J⁻¹ and K is correct |
| External strict IFT hypotheses | passed for mathematical input | Complete finite source; actual strict derivative is a continuous linear equivalence; inspected current theorem includes subsingleton domain |
| Same inverse is analytic | passed for mathematical input | Analytic inverse theorem is applied to R, whose map is Φ and whose inverse is the constructed g; no unrelated inverse is substituted |
| Product-neighborhood quantifiers | passed | V×U₀⊆R.source handles all candidate roots; preimage of an inverse target neighborhood handles all (0,t); separate inclusion condition ensures ψ(U)⊆V |
| Base and derivative | passed | Φ(a)=(0,t₀); π_Y A⁻¹(0,v)=−J⁻¹Kv |
| Root graph, both directions | passed | Left inverse gives uniqueness; right inverse simultaneously gives the zero solved equations and parameter coordinate exactly t |
| Regularity throughout U | passed | U is intersected with the open analytic locus of ψ; statement is stronger than merely analytic at t₀ |
| Supplied h, only continuity at base | passed | Eventual inclusion in V is sufficient; root/graph neighborhoods can be intersected and made open |
| Open-set pointwise selection | passed | Openness upgrades relative continuity to ambient continuity at each t; no extrapolation from base invertibility |
| Integral coefficient/center transfer | passed | Ring homomorphism preserves evaluation and pderiv; included J and K are the actual evaluated Jacobian blocks |
| e=0, k=0, e+k=0 | passed mathematically | Direct singleton checks below; inspected current IFT source explicitly includes Subsingleton E |
| p=2 and positive characteristic | passed | Main theorem has no CharZero dependency; positive-sign rejection is explicitly over Q_p, which has characteristic zero even when p=2 |
| Quantitative radius / historical subtype chart | out of scope | Section explicitly asserts qualitative local neighborhoods and leaves direct historical-chart identification as an interface task |
| Pinned external-source authentication | conditional | Exact pinned source bodies unavailable; retained hashes alone do not authenticate them anew |
| New Lean/lake compilation | not addressed | Neither toolchain was rerun; mathematical/source-contract review only |

## Fresh decisive derivations and boundary checks

For A=[[J,K],[0,I]] and B=[[J⁻¹,−J⁻¹K],[0,I]], the upper-right block of AB is J(−J⁻¹K)+K=0; for BA it is J⁻¹K−J⁻¹K=0. Both diagonal blocks are identity. A sign reversal would already fail this calculation.

Let S=R.source and W be an open inverse neighborhood contained in R.target on which g is analytic. Choose open V,U₀ with a∈V×U₀⊆S. With i(t)=(0,t), the intersection

`U₀ ∩ i⁻¹(W) ∩ {t : ψ is analytic at t} ∩ interior(ψ⁻¹(V))`

is open and contains t₀. The final condition follows from continuity at t₀, not assumed global continuity. For a candidate root (y,t)∈V×U, Φ(y,t)=i(t), and the left inverse identity gives g(i(t))=(y,t). Conversely Φ(g(i(t)))=i(t); its lower coordinates force g(i(t))=(ψ(t),t), and its upper coordinates force F(ψ(t),t)=0. This establishes the full ∀t∈U,∀y∈V equivalence without losing admissible-domain conditions.

Small and exceptional cases:

- e=0: the solved space is a singleton, the equation system is empty, its 0×0 identity is invertible, and ψ is the unique map to the singleton. The graph equivalence holds identically; the derivative is the empty matrix.
- k=0: the parameter space is a singleton. The graph assertion says a nonsingular root is isolated in a solved neighborhood; this is exactly the strict IFT conclusion. The derivative has zero-dimensional source.
- e=k=0: both spaces are singletons and all assertions reduce to identities. No positivity of a zero operator norm is needed; inspected current IFT code uses its explicit subsingleton branch.
- F(Y,T)=Y+T gives ψ(T)=−T and derivative −1. The wrong derivative +1 contradicts uniqueness because 1≠−1 in Q_p for every prime p. Reduction modulo 2 does not change the characteristic of Q_2.
- F(Y,T)=Y+Y²+T at (0,0) has J=K=1 and a valid local branch. No division by 2 is used, so the stated nonlinear control applies at p=2 and over positive-characteristic complete fields too.
- F(Y,T)=pY+T at (0,0) has included J=p≠0 and branch ψ(T)=−T/p. It validates the claimed fraction-field nonsingularity boundary while showing why this corollary is stated in ambient Q_p spaces.
- Removing solved nonsingularity would change the theorem: F(Y,T)=Y²−T at (0,0) over R has no root for arbitrarily small negative T. The existing section does not make that extension.

## Raw formal contract comparisons

Inspected `PolynomialAnalyticEvaluation.lean` (lines 42, 67, 72, 76), `PolynomialAnalyticBlocks.lean` (lines 20, 51, 59, 69), `PolynomialAnalyticInverse.lean` (lines 28, 36), `PolynomialAnalyticImplicit.lean` (lines 41, 151, 201), `PolynomialAnalyticSelection.lean` (lines 18, 39, 61), `PolynomialRegularityIntegral.lean` (lines 19–59, 87), `PolynomialRegularityContracts.lean`, and `PolynomialRegularityControls.lean`.

The generic analytic declarations assume `[NontriviallyNormedField K]` and `[CompleteSpace K]` as needed, with e,k natural numbers. `analyticAt_inverse` requires only completeness of the original domain E; its input is the actual strict derivative equivalence, and it calls `OpenPartialHomeomorph.analyticAt_symm'` on the same constructed partial homeomorphism. `exists_analytic_graph` implements the precise neighborhood intersection reconstructed above. `continuous_selection_regularity` derives the base root from a neighborhood root equation, so its formal input is no stronger than the prose. The pointwise open-set result retains an invertible actual solved Jacobian at each selected root. The integral output is Q_p-valued and evaluates the original integral polynomials via their actual coefficient inclusion. The positive-sign rejection alone has CharZero; the general analytic branch theorem does not.

These are static contract and proof-body inspections. They do not assert elaboration or kernel acceptance on this host.

## External theorem checks and version boundary

Checked on 2026-10-06 through the web retrieval tool, using primary official documentation and the source links it provides:

1. [Mathlib strict inverse-function documentation](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Calculus/InverseFunctionTheorem/FDeriv.html), and [source revision 17e9f587d815324cbb86deaa91761c9741696ac7](https://github.com/leanprover-community/mathlib4/blob/17e9f587d815324cbb86deaa91761c9741696ac7/Mathlib/Analysis/Calculus/InverseFunctionTheorem/FDeriv.lean). The source has generic nontrivial normed field assumptions; complete E; a continuous derivative equivalence; and `to_localInverse`. Its construction explicitly treats a subsingleton E. Translation: E=F=K^(e+k), derivative equivalence=A, inverse=g.
2. [Mathlib analytic-derivative documentation](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Calculus/FDeriv/Analytic.html), and [source revision ff9a7c19e5c26a798978176b0c5cd03c426fd74f](https://github.com/leanprover-community/mathlib4/blob/ff9a7c19e5c26a798978176b0c5cd03c426fd74f/Mathlib/Analysis/Calculus/FDeriv/Analytic.lean). `OpenPartialHomeomorph.analyticAt_symm'` takes source membership, analyticity of the forward map, and equality of its derivative to a continuous equivalence, then concludes inverse analyticity at the image. Its proof uses the forward power series and an inverse-series theorem. Translation: partial homeomorphism=R, base=a, forward map=Φ, equivalence=A. No RCLike, CharZero, or odd-prime assumption appears.

The external arrows needed by the mathematics are valid under the section's hypotheses. This is a standard theorem application; no novelty search was performed or needed.

The retained `polynomial_regularity/dev/analytic_inverse_source_leaf.json` identifies upstream SHA256 values and a historical PASS, and the verification JSON names pinned revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. No file bodies from that revision were found. Opening raw.githubusercontent.com and github.com URLs for that pinned revision returned `DisabledError`; the available current official source versions above differ. Accordingly the exact historical dependency authentication is conditional, independently of the mathematical correctness verdict.

Commands used for local work: `rg --files` to locate the current raw section, formal modules, project instructions, and possible cached upstream sources; `rg -n` for exact declaration/hypothesis locators; `cat`/`nl -ba` for fresh raw proof reading; Python `hashlib.sha256` for target/module hashes. No Lean/lake command was executed, no retained PASS was described as a new run, and no bounded computation was used as universal mathematical evidence.

## Exact remaining gap and strongest safe statement

There is no remaining mathematical implication in the audited section requiring a manuscript repair. The strongest safe mathematical statement is the section as written: a qualitative analytic local graph at any exact root whose actual solved block is invertible over the ambient complete normed field, plus the supplied-selection and integral-inclusion consequences.

The remaining evidence gap is solely an exact-version formal provenance check: acquire the authorized historical Mathlib kit/source revision, verify the recorded upstream hashes, then elaborate the unchanged modules with the pinned toolchain if a new formal rerun is desired. That would authenticate the archived formal implementation; it does not supply a missing mathematical hypothesis or change the conclusion. No uniform radius, global branch, integral-valued branch on all integral parameters, or fraction-field-singular persistence is inferred.
