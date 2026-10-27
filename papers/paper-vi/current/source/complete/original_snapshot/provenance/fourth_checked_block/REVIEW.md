# Paper VI — fourth checked formalization block

Author: Komorebi P. · 6 September 2026 · v0.4.0

**Three of the last five results are now complete: 10.3, 10.4 and 10.5. Two remain partial: 13.2 and 15.1. This block does not finish all five.** This is a checked progress release, not a fully formalized paper.

| Count | Previous checked block | This release |
|---|---:|---:|
| Explicit Lean theorem declarations | 227 | 310 |
| Proof modules | 30 | 42 |
| Complete manuscript results | 28 | 31 |
| Partial manuscript results | 5 | 2 |
| Pending manuscript results | 0 | 0 |
| Namespace declarations audited | 512 | 710 |

The 83 new supporting theorem declarations are not 83 new manuscript results. Namespace declarations include definitions and generated auxiliaries, so they are a third counting unit. Counts concern Paper VI only; no cumulative total for Papers I–VI is inferred. The original three conjectures remain open and are excluded from the 33-result ledger.

## Fresh verification

- The complete project builds with Lean 4.34.0-rc2, strict elaboration options and warnings treated as errors.
- Every explicit theorem is audited, and every declaration in the project namespace is inspected. Only `propext`, `Classical.choice`, and `Quot.sound` are allowed.
- No active proof placeholder, custom axiom or unregistered unsafe code is accepted.
- All nine dependency revisions match the lockfile with no tracked source changes; mathlib is pinned at `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- All 54 companion tests and six verifier controls pass, including the optimized-Python negative control.
- Source hashes, root imports, theorem inventory, audit targets and the 33-result ledger pass.

The authoritative evidence is `verification/verification_status.json`, `lean_build.log`, and `lean_axiom_audit.log`. The report explicitly records `full_paper_formalized: false`. Failed development attempts are retained separately. A successful build checks the Lean declarations; prose-to-Lean correspondence and ordinary real/complex specializations remain manually reviewed.

## Newly completed results

| Result | Statement | Checked scope |
|---|---|---|
| 10.3 | Fractional intertwining theorem | Actual normalized Lebesgue/Bochner resolvent-defect integral for bounded nonnegative self-adjoint operators between distinct complex Hilbert spaces, the exact Holder constant, the alpha*m^(alpha-1) common-gap estimate, and exact fractional intertwining. Real finite matrices use their standard complexification; this ordinary specialization is manually reviewed. |
| 10.4 | Fractional semigroup refinement | Actual fractional exponentials between distinct complex Hilbert spaces, rectangular Duhamel identity, contraction estimate, and the final common-gap bound in terms of the original generator defect. |
| 10.5 | Fractional refinement towers | Varying complex Hilbert-space towers: both printed generator criteria imply summability of fractional-defect norms and time-defect norms, with uniform convergence of the real norm series on bounded nonnegative time intervals. Operator-series convergence is additionally proved in the inherited fixed-space formulation; no sum across unrelated operator spaces is asserted. |

## Fractional proof details

The scalar normalization is proved, not supplied as a hypothesis. The substitution `x=t/(1+t)` converts the positive-half-line integral into the beta integral. Euler's reflection formula gives `pi/sin(pi*alpha)`. The weighted beta integral gives the exact common-gap coefficient `alpha*m^(alpha-1)`.

The CFC representation is proved using the explicit measure `(sin(pi*alpha)/pi) * Lebesgue`; positivity and nonzero normalization then transfer integrability to Lebesgue measure. Literal positive resolvents are identified with actual inverses of `tI+A`, with both inverse identities and the norm bounds `1/t` and `1/(t+m)`.

The rectangular proof works between distinct complex Hilbert spaces. It carries composition through the actual Bochner integral and obtains the resolvent-defect formula. Splitting the norm integral at `norm(D)/(2*norm(C))` gives the exact printed Holder constant. Both zero cases are included. The common-gap integral yields the linear estimate, and vanishing generator defect yields exact fractional intertwining.

The real-time Duhamel derivative for complex linear maps is proved using the continuous bilinear composition map restricted to real scalars. Actual positive fractional exponentials are contractions, with gap decay `exp(-t*m^alpha)`. Substituting the proved fractional estimate gives the printed final bound in terms of the original generator defect.

The tower proof permits a different Hilbert space at every level. The two printed generator hypotheses imply summability of fractional-defect norms. The bound `norm(time_defect_n(t)) <= T*norm(fractional_defect_n)` supplies a summable majorant on `[0,T]`, and uniform convergence of the real norm series is proved. An operator sum across unrelated codomains is not meaningful; the formalization appendix now explains “summable in norm” explicitly. The inherited fixed-C-star-algebra module separately proves operator-series convergence where a common space exists.

The main Lean statements use complex Hilbert spaces. Complexification gives the corresponding real mathematical statements; that specialization is explained in prose and is not a separate Lean complexification theorem. This boundary is disclosed rather than included in the explicit theorem count.

## Progress and remaining obligations

### 13.2 — Memory/self-energy correspondence

Literal complex damping, Bochner integrability, two-sided inverse and self-energy equality in a C-star algebra under a supplied exponential-growth bound. For normal operators the growth bound is derived from a spectral real-part bound.

**Still unproved:** Derive exponential growth from the spectral-abscissa condition for arbitrary finite nonnormal complex matrices and finish the retained/hidden rectangular matrix specialization. The general nonnormal clause is not proved.

### 15.1 — Naturality under exact intertwining

Actual finite complex rectangular resolvent intertwining and common contour naturality. Holomorphicity on the declared neighborhood now supplies contour integrability rather than assuming that integrability separately.

**Still unproved:** Construct an admissible common contour for an arbitrary neighborhood of both spectra and prove independence/identification with the canonical holomorphic functional calculus.

For memory, the new proof identifies `exp(-z*t) * exp(t*A)` with the shifted exponential for complex `z`, proves integrability, derives both inverse identities, and identifies the actual ring inverse and self-energy integral. Normal operators obtain the required growth estimate directly from CFC and a real-part spectral bound. The printed theorem also includes nonnormal matrices; that general spectral-growth implication is not replaced by a stronger assumption and is not marked complete.

For holomorphic naturality, continuity of the literal matrix resolvent and holomorphicity on the declared neighborhood now prove circle integrability automatically. The common-contour identity consequently no longer assumes integrability as separate data. It still requires supplied common resolvent circles. Choosing admissible contours and proving their canonical independence are substantive missing work, so 15.1 remains partial.

## Manuscript, provenance and reproduction

All earlier mathematical corrections and all 33 theorem-like records are retained, as are the three open conjectures and authorship Komorebi P. The title, abstract and formalization appendix now reflect this block. The appendix distinguishes norm summability from an undefined operator sum across varying spaces. No numerical algorithm or figure was changed. All 54 tests were rerun; the first-block 79-field numerical comparison and 19 regenerated figure pairs are retained historical evidence, not experiments repeated in this block.

The untouched supplied edition and prior checked ledgers/audits remain under `provenance`. The source archive includes exact patches, current hashes and a verified release manifest; dependency caches, build products and toolchain binaries are excluded. An adapted Mathlib integral proof is credited in its module header and `THIRD_PARTY_NOTICES.md`, with the Apache 2.0 license included.

Install the pinned Lean toolchain, preserve `lake-manifest.json`, obtain dependencies and the mathlib cache with `lake exe cache get`, then run `lake build KomorebiPaperVI` and `lake env lean -DwarningAsError=true KernelAudit.lean` from `formalization/lean`. The complete gate is `python3 verification/verify.py` with the companion Python requirements installed and `lake` on PATH. Missing Lean is a failure to verify, not a pass. The producing runtime adapter is documented in `verification/runtime/RUNTIME.md`; compiler, kernel and dependency sources are unchanged.

Compile `manuscript/Paper_VI_Reviewed.tex` until references stabilize. The PDF is rendered and visually inspected; `verification/pdf_validation.json` records its final hash and inspection scope. Run `companion/run_all.py` to reproduce the numerical study.
