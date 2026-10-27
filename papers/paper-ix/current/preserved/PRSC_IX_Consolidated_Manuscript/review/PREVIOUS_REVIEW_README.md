# Paper IX: reviewed completion and native conjecture progress

Komorebi P. | Review completed 8 September 2026

**Nishibuchi Conjecture 3.9 is proved by the included Lean release in its full stated parameter range, with the explicit sufficient threshold n0 = r.** Its correspondence with the original arXiv v2 statement has now been independently inspected, and the complete release launcher has been rerun successfully.

The two native Paper IX conjectures are separate. Their unrestricted statements remain unresolved. This continuation adds a fully checked affine obstruction theorem and precise polynomial, algebraic and gluing results with explicit scope boundaries.

## Verified status

| Item | Result |
|---|---|
| Original completion ZIP | Exact matching SHA-256 and valid CRC |
| Fresh baseline source build | 79/79 modules |
| Baseline axiom audit | 1,000/1,000 declarations; only the three permitted standard axioms |
| Exact external statement contract | Passed |
| Deliberately invalid baseline controls | 37/37 rejected as required |
| Extension infrastructure tests | 25/25 passed |
| Exact arithmetic regressions | Passed; mathematical results match historical release |
| Full baseline launcher | Exit 0; 460.315 seconds in this environment |
| New affine obstruction module | 9 theorems, 3 definitions and 1 abbreviation checked |
| New positive control module | 4 theorems checked |
| New false strengthening controls | 2/2 rejected as required |
| Polynomial implementation check | 6,502 solution points checked in the stated finite range |

The baseline retains its own 836 named theorems and 24/24 manuscript-proved register. The new affine specialization is separate and does not turn either unrestricted native conjecture into a proved entry. Counts include supporting declarations, not independent discoveries.

## Start here

- `review/CONTINUATION_SCOPE.md`: exact external theorem and completion boundary.
- `review/COMPLETION_REVIEW.json`: current machine-readable status.
- `review/EXTERNAL_STATEMENT_AUDIT.md`: original definition, normalization, quantifiers and degree shift.
- `review/NATIVE_INDEPENDENT_AUDIT.md`: independent review of the native progress.
- `native/Native_Conjectures_Progress.md`: full new proofs and exact remaining implications.
- `native/lean/FiniteAffineObstruction.lean`: the new unconditional Lean theorem.
- `baseline/PRSC_IX_v0.11.0_Nishibuchi_Completion.zip`: the byte-identical full prior release, including all 79 source modules and its five-page completion paper.

## What the new native work establishes

For every finite affine integer system A x = b and every positive integer modulus p, a solution modulo p^L has an explicit finite cokernel obstruction. It vanishes exactly when that solution lifts modulo p^(L+1). This is proved in Lean, including the actual arithmetic bridge and invariance under a change of representative.

For finite polynomial systems, the note proves the corresponding Jacobian obstruction and exact lift count in prose. It identifies a classical intrinsic obstruction theorem for finitely presented integer algebras, with checked primary references. That classical result is not newly claimed or formalized here.

The proposed global spine cannot recover diagonal global integers from their local p-adic realizations through continuous maps to a Hausdorff common space. Finite CRT and profinite completion provide precise valid alternatives. A further theorem characterizes exact finite gluing by rectangularity of the compatibility relation and constructs its universal component quotient. These gluing results are prose proofs, not Lean formalizations.

For unrestricted native 13.2, the remaining task is to define and prove a lift-preserving encoding of the general seed systems. For native 13.3, it is to define the intended global or completed object, category and compatibility maps, and establish the required descent condition. The original manuscript's undefined generality is not silently replaced by a convenient special case.

## Reproduce

The baseline archive excludes Lean and Mathlib. Use the previously released Linux x86-64 portable kit, Lean 4.34.0-rc2, with the baseline's pinned Mathlib revision.

From this extracted review directory:

```sh
python3 review/replay_review.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /new/replay_directory
```

This checks the baseline archive hash, extracts into a new directory, runs the original complete launcher, and runs the native verifier with fresh local compiled outputs. It writes an aggregate report and logs. The component commands were executed successfully in this review; the new convenience wrapper was syntax/help checked and inspected, not itself used for a second full replay.

To rerun only the native proof:

```sh
python3 native/lean/verify_native.py --kit /path/to/kit --output /new/native_replay
```

The bounded polynomial script is self-contained and can be run as `python3 native/check_polynomial_obstructions.py`. Its recorded historical command used the earlier `native_work` directory name.

## Evidence and limitations

`historical/` preserves the supplied audit. `review/fresh_baseline/` and `native/lean/replay_02/` contain the fresh proof and control records. The failed first native aggregate check is recorded under `review/development_parser_failure/`: a case-sensitive expected-error parser caused the failure despite passing proof checks. The corrected verifier passed. No failed proof check is relabeled as a pass.

The runtime's pinned Mathlib compiled dependencies were reused. No different proof kernel, human peer review, full original-manuscript rewrite, or rerun of Papers I through VIII is claimed. The external source PDF was inspected and authenticated locally; its URL, version and hash are recorded, rather than redistributing the complete external article. No optimal period, optimal threshold or historical-priority claim is made.
