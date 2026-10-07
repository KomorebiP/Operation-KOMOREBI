# Paper IV v1.0.0: independent audit

**Date:** September 5, 2026  
**Manuscript author:** Komorebi P.  
**Input:** `PRSC_IV_v1.0.0(1).zip`  
**Input SHA-256:** `9ea785dd8e20eecc856ae87b9063b0949c5cb52472de241bf5f8d143d26cb42b`

## Verdict

**Archive integrity and source-level consistency passed the checks described below. A fresh Lean proof build was not completed.**

The contents support the release's claim that it is a substantial, source-complete candidate for the scoped Paper IV formalization. They do not justify saying that this independent run re-certified all 68 manuscript results in Lean. The release verifier was actually executed and stopped because `lake` was absent. No installed Lean toolchain was found, and attempts to obtain runtime dependencies failed. This is an execution-environment limitation, not a demonstrated failure of any Lean theorem.

The manuscript-to-Lean comparisons below are targeted source reviews, not an exhaustive independent review of every clause and dependency of all 68 results. Recorded build and axiom logs were inspected as supplied evidence, not represented as newly generated proof-checking output.

## 1. Checks performed in this audit

| Check | Observed result | What it establishes |
|---|---|---|
| Original ZIP CRC | Passed for every entry | The ZIP is readable without detected CRC corruption. |
| Release entry set | 148 files, one root prefix | The supplied verifier's entry-set and portability checks pass. |
| SHA-256 manifest | All 147 covered files match, independently recomputed | Extracted contents agree with the supplied manifest. The manifest is the remaining ZIP file. This establishes internal integrity, not external authenticity. |
| Lean source inventory | 119 files, 18,267 lines | Substantial Lean source is present, not only a status ledger. |
| Manuscript register regeneration | Byte-identical, 95 records | The supplied register generator reproduces the shipped register. |
| Theorem-like manuscript environments | 30 theorems, 11 propositions, 25 corollaries, 2 lemmas | The stated total is 68. |
| Proof environments | 68, paired by the supplied verifier | Each theorem-like manuscript record has a paired prose proof environment. This alone does not prove mathematical correctness. |
| Imported standard facts | 1 | The excluded standard-fact record is separately counted. |
| Completion ledger | 68 records marked full | This confirms the ledger's classification, not an independently proved semantic-completeness percentage. |
| Map and contract | 151 rows; 1,164 targets, comprising 953 theorems and 211 definitions | Reviewed record associations agree structurally between the map and the contract. |
| Target source search | No missing textual names or kind mismatches in the lexical checks | Matching named declarations are present in the source. Lean environment resolution was not rerun. |
| Local import graph | No missing local imports | The umbrella module reaches 118 local modules, including itself. The remaining module is the separately executed `KernelAudit`. |
| Placeholder and bypass scan | No findings after removing comments and strings | No `sorry`, `admit`, custom `axiom` declarations, `unsafe`, `opaque`, `native_decide`, `implemented_by`, `debug.skipKernelTC`, or selected environment-injection markers were found by this scanner. This is not a substitute for compilation and a live transitive-axiom audit. |
| Semantic-check source | 43 named theorem declarations | The reported semantic checks exist in source. They were not executed in this audit. |
| Shipped PDF | 39 pages; matching manifest hash; every listed font embedded | The delivered PDF passes the metadata and font checks. |
| PDF visual samples | Pages 1, 14, 28, and 36 rendered and inspected | These samples are legible and show the stated formulas and evidence boundaries. This was not a full 39-page render audit. |

The input archive was not modified. Unix file modes were restored from ZIP metadata after Python extraction, including the shipped executable mode of `VERIFY.sh`. An initial extraction-mode failure was thereby corrected before the meaningful release-verifier run.

## 2. Actual release-verifier outcome

The following command was executed against the extracted, unchanged source contents:

```sh
bash /mnt/data/prsc_iv_audit/source/PRSC_IV/VERIFY.sh \
  --release --archive '/mnt/data/PRSC_IV_v1.0.0(1).zip'
```

It passed the archive, checksum, register, and map/contract checks, then exited with code 1:

```text
FAIL: lake is required for the pinned Lean build
```

The exact output is in `logs/release_gate.txt` in the companion audit ZIP. The failure does not establish that the project fails to compile. It establishes that this session did not run its Lean compilation gate. In particular, the release's claimed 3,521-job successful integration build was not independently reproduced.

The release gate was also inspected. It requests a warning-fatal `lake --wfail build`, constructs live declaration-resolution and declaration-kind probes, and executes the namespace axiom audit separately. It does not merely accept the saved audit text as proof of a new build.

A separate attempt to exercise the clean PDF-build routines stopped because `bibtex` was absent. `pdflatex` was present. Consequently the claims of a byte-identical deterministic PDF rebuild and a clean final LaTeX build log were not reproduced here. The existing PDF's hash, page count, and embedded fonts were checked separately.

## 3. Recorded kernel-audit evidence

`KernelAudit.lean` explicitly requests axiom reports for 1,164 targets. Its target set agrees with the release contract. The saved `kernel_audit_output.txt` contains exactly 1,164 corresponding unique target reports, with the same target set.

The saved target reports list only:

```text
propext
Classical.choice
Quot.sound
```

No `sorryAx` occurs in that saved output. Its final sentinel reports 2,234 namespace declarations, including 1,999 theorem declarations. Those namespace counts were not independently regenerated. Generated declarations also mean that namespace counts should not be conflated with the number of explicit source-level theorem commands or the 68 manuscript records.

The audit implementation traverses `Komorebi.PaperIV`, rejects unsafe, axiom, and opaque declarations, calls `Lean.collectAxioms`, and rejects axioms outside the three-name allowlist. This is an appropriate intended safeguard against undeclared proof assumptions, subject to executing it in the pinned environment.

The 43 separate semantic-check theorems live in `Komorebi.PaperIVChecks`. The source includes axiom-printing commands for them, and the umbrella module imports their module. However, the namespace sweep filters `Komorebi.PaperIV`, not this sibling namespace. The Python gate parses the separately executed `KernelAudit` output; it does not explicitly enforce the 43-check count or separately sweep `Komorebi.PaperIVChecks`. These checks should not be silently included in the `Komorebi.PaperIV` namespace-count claim. A useful verifier hardening is to audit the sibling namespace explicitly and enforce its advertised count. This is an audit-coverage improvement, not evidence that a semantic-check theorem is false.

## 4. Targeted manuscript-to-source review

These observations describe the definitions and statements that were inspected. They are not claims that their proof terms were executed during this audit.

### Pointwise root filters and addition

`PointwiseFilters.lean` uses actual finite averages of function values over root-of-unity orbits. Its statements include covariance, projector resolution, product decomposition, and a `HasSum` coefficient-selection statement. `PointwiseAddition.lean` supplies statements for arbitrary complex arguments, with the signed carry factor derived under `rho^N = -1`. These are materially more than formal-series names alone.

### Fixed-logarithm reciprocal laws and Riccati identity

`AnalyticReciprocalLaws.lean` defines `IsLogarithmOn` by differentiability on the domain and `exp(L z) = f z`. The reciprocal-power derivative theorem explicitly retains an open-domain hypothesis and one chosen logarithm. The higher Riccati statement uses the actual canonical signed denominator and assumes it is nonzero at the point. No global branch-independent complex-power law is being asserted by those statements.

### Polynomial operator bridge and the order-one boundary

`OperatorEncodingBridge.lean` connects the truncated derivative operator to the factorial/Hasse encoding and states forward and inverse actions on the named residue Appell polynomial. `TangentBoundary.lean` explicitly identifies the order-one denominator with `exp(-z)` and the order-one tangent with the constant function 1, then joins that case with the positive-order expansion statement.

### Compact reciprocal formulas and Newton determinant

`CompactReciprocal.lean` states the literal second and third reciprocal-polynomial formulas with their factorial and binomial factors. `NewtonDeterminant.lean` defines the lower Hessenberg matrix with the negative integer superdiagonal and states its determinant identity from Newton's recurrence. The specialization is the displayed reciprocal-coefficient determinant, rather than an unrelated determinant definition.

### Hypergeometric identification

`HypergeometricAnalytic.lean` constructs the parameter multiset with the unit parameter omitted, includes parameter-cardinality and positivity statements, normalizes the regularized hypergeometric coefficients using Gamma factors, and states an everywhere-convergent series identity and the pointwise transfer-function formula. The source does not merely rename the original transfer series as an unspecified hypergeometric object.

### Quotient-algebra exponential

`QuotientExponential.lean` supplies coefficient-induced normed-space instances on the actual quotient algebras. It states `HasSum` results for the ordinary exponential series under `x^N = 1` and `x^N = -1`, followed by the pointwise quotient-algebra identities. The source contains an explicit convergence bridge, rather than only a finite coordinate definition.

### Selected difficult analytic interfaces

`HadamardIdentification.lean` states equality of the actual reduced denominator with its full multiplicity-sensitive canonical product for `N >= 2`. The final equality theorem does not simply assume the desired product identity or a free quotient-growth certificate as a hypothesis; its proof invokes earlier growth and quotient lemmas. Those dependencies were not exhaustively re-proved in this audit.

`DiagonalNuclear.lean` defines trace class by a summable rank-one representation on a Hilbert space. `DiagonalFredholm.lean` contains an actual diagonal operator, finite-compression determinant identities, a compression-limit statement, and the equality with the reduced denominator. This supports the explicitly specialized diagonal interpretation. It is not a general trace-class spectral theory or Feshbach theorem.

No definite mathematical contradiction was identified in these reviewed interfaces. This is not an assertion that every result in the paper has received a complete independent semantic review.

## 5. Scope and the remaining certification boundary

The release explicitly excludes imported standard fact 11.1 and historical-priority claims from the 68-result contract. Its evidence boundary retains the stated logarithm domains, multiplicities, factorial normalizations, positive integral reciprocal orders, and simple-nearest-zero assumptions where applicable.

The manuscript also leaves open universal simplicity of all zeros, positivity of every reduced zero, full displacement expansions, and a zeta functional equation. Those open questions do not themselves contradict completion of the narrower 68-result contract.

There are two separate remaining questions:

1. Does the unchanged project actually compile and pass the live axiom and declaration-kind audits in the pinned environment? This session did not establish that.
2. Do the elaborated Lean statements, including every hypothesis and definition, cover every clause of the intended manuscript claims? The name/kind/record contract does not mechanically establish that equivalence. This audit performed targeted comparisons, not a full independent semantic certification.

The pinned Mathlib revision's public `lean-toolchain` file was checked and specifies the same Lean release, `leanprover/lean4:v4.34.0-rc2`. That is compatibility evidence for the declared pin, not a project build.

## 6. Reproduction and recommended next gate

With the exact Lean toolchain and pinned dependencies installed, run the shipped verifier from a fresh extraction:

```sh
cd /path/to/PRSC_IV
bash ./VERIFY.sh --release --archive '/path/to/PRSC_IV_v1.0.0(1).zip'
```

Its advertised release outcome requires all gates to pass. Do not replace missing-tool failures with a success marker. Preserve the fresh build, target-resolution, and axiom-audit logs alongside the hash of the input ZIP.

For additional assurance, Lean's official validation guidance recommends replaying built proof objects with `lean4checker`. That is stronger than inspecting a saved transcript, but it still does not eliminate the need to check that the formal statement means what the manuscript claims.

The companion `independent_static_audit.py` is a reusable lexical/integrity checker, not a proof checker:

```sh
python independent_static_audit.py \
  --root /path/to/PRSC_IV \
  --archive '/path/to/PRSC_IV_v1.0.0(1).zip' \
  --out /path/to/audit_output
```

Use an output directory outside the release source tree. The script does not run Lean or rebuild the PDF.

## Reference locations

Bundle evidence: `README.md`; `RELEASE.json`; `provenance/COMPLETION_STATUS.md`; `provenance/EVIDENCE_BOUNDARY.md`; `formalization/lean/LEAN_THEOREM_MAP_v1.0.0.md`; `formalization/lean/KomorebiPaperIV/KernelAudit.lean`; `formalization/lean/kernel_audit_output.txt`; `verification/check_release.py`; `verification/lean_contract_v1.0.0.json`.

Official validation reference: Lean Language Reference, “Validating a Lean Proof,” consulted September 5, 2026. Address for reproduction:

```text
https://lean-lang.org/doc/reference/latest/ValidatingProofs/
https://raw.githubusercontent.com/leanprover-community/mathlib4/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/lean-toolchain
```

**Final classification: integrity verified; source structure consistent; recorded audit internally consistent; fresh Lean compilation and full semantic certification not independently completed.**
