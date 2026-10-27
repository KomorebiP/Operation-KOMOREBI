# Dyadic Euler tails — research record v6

**Operation Komorebi · Komorebi P. · 26 September 2026**

## Read first

- `manuscript/Dyadic_Euler_Tails_Running_v6.pdf`: 78-page cumulative manuscript. The complete v5 reading record is retained and Continuation VI is appended.
- `manuscript/Dyadic_Euler_Tails_Appendix_v6.pdf`: 18-page standalone v6 continuation.
- `manuscript/CONTINUATION_06.md`: current proof note and exact claim boundary.
- `manuscript/Dyadic_Euler_Tails_Running_v6.md`: editable cumulative source.

The PDF contents include the cover and navigation pages in these page counts. Each continuation retains its own equation numbering.

## What changed

Every nonconstant residual has a canonical terminal carry representation

    r = b*2^L - j,   b positive odd,   j = max argmin(lambda_r).

The exact regular-wall proof extends to arbitrary odd multipliers once the true terminal label has been identified. Parameter-uniform coefficient certificates complete the finite exceptional ranges at labels 17, 33 and 49. Consequently every depth with prepared-polynomial degree at most 64 has a complete dyadic constant-or-simple-root valuation atlas. Every positive r with at most 195 binary ones is included. This is a theorem, not an enumeration of those integers.

The new unit dependence is real. At terminal label 17 and L=64, two dyadic roots occur precisely for b congruent to 1 or 41 modulo 64. Every other odd multiplier class has no dyadic root at that distance. The normal form and the carry weights by themselves therefore do not determine the root count.

The proof does not construct a joint exact analytic family in the undepleted multiplier. Its template is a finite-precision theorem for actual positive integer indices, under the true-terminal-label hypothesis.

## Boundaries

The optimal uniform truncation exponent remains 4M+3. The new result supplies exact additional, row-dependent cancellation.

Every dyadic root in the classified region is simple. This does not establish squarefreeness over an algebraic closure. Larger irregular terminal labels remain outside the complete classification, except where a stated all-depth criterion or the regular-terminal theorem already applies. An unresolved finite-precision root or resultant is never called an exact repeated root.

No Lean compilation or historical-priority assessment was performed in these continuations. Universal proofs, whole-ball coefficient certificates, and sampled implementation comparisons are kept separate.

## Preserved history

The incoming v5 release matched all 124 entries of its integrity ledger. Its files are retained. The original top-level release metadata are in `history/v5_release/`, and the recovered earlier proof notes and source are in `history/v4/`. Earlier reading maps describe the then-current state; Continuation VI and the v6 front matter specify the current boundary.

## New exact evidence

The five new mathematical audits and two foundation reruns completed successfully. Their version-2 manifests record actual commands, before/after input hashes, scientific result hashes, resource caps, elapsed times and exit status. All seven new manifests passed the retained validator.

Selected new counts:

| Check | Count |
|---|---:|
| Consecutive-depth terminal identities | 262,144 |
| Large/adversarial terminal identities | 2,240 |
| Generalized regular members | 285 |
| Regular whole-ball certificates | 4,539 |
| Irregular equality/positive-distance cases | 112 |
| Covering parameter balls | 119 |
| Parameter-uniform argument-leaf certificates | 1,163 |
| Independent multiplier atlases | 233 |
| Original-series parity coefficient comparisons | 466 |
| New original unfactored-tail comparisons | 285 |
| Local quadratic preparations | 3 |

The fresh foundation rerun includes all 8,256 nonempty rational tails through N=128. The fresh v5 distribution/resultant rerun includes 94,208 residue evaluations and the repeated-root safety test. These are preserved-theorem checks, not new mathematical claims.

## Reproduce

Python's standard library suffices for all scientific arithmetic. Matplotlib is needed only for plots. Pandoc and XeLaTeX build the manuscripts. No font files are distributed.

From the release root, use a fresh output name:

```text
python code/run_audit_v6.py --name NEW_CARRY --result results/NEW_CARRY.json --timeout 35 -- python check_terminal_v6.py --mode combinatorial --output ../results/NEW_CARRY.json
python code/run_audit_v6.py --name NEW_REGULAR --result results/NEW_REGULAR.json --timeout 35 -- python check_terminal_v6.py --mode regular --output ../results/NEW_REGULAR.json
python code/run_audit_v6.py --name NEW_J17 --result results/NEW_J17.json --timeout 35 -- python check_terminal_v6.py --mode irregular --j 17 --output ../results/NEW_J17.json
```

The bounded runner uses POSIX resource limits and executes the declared command from the `code` directory. On Windows, the scientific checkers themselves can be run directly from that directory with standard Python and fresh output filenames; the POSIX runner is not required for the mathematics.

The retained size-49 run completed in approximately 30 seconds on this environment. A different machine can require a larger declared runtime cap. Do not overwrite retained scientific results.

Validate one execution record:

```text
python code/support/validate_manifest.py results/MANIFEST_UNIFORM_J17_V6.json --root .
```

Regenerate plots and documents:

```text
python code/make_figures_v6.py
python code/build_running_document_v6.py
```

Verify the delivered bytes before regenerating files:

```text
python verify_release.py
```

Regeneration can change PDF timestamps and hashes. An integrity mismatch after an intentional rebuild is not, by itself, a mathematical failure.

## Important files

`code/terminal_carry_v6.py` implements the terminal descriptor, separating scales, multiplier template and paired certificates. `code/check_terminal_v6.py` contains the independent comparisons and retained test scopes. `results/UNIFORM_J17_V6.json`, `UNIFORM_J33_V6.json` and `UNIFORM_J49_V6.json` contain the finite template coefficients and all parameter/argument leaf certificates. `results/V6_SUMMARY.json` aggregates the new executed counts.

`results/PDF_QC_V6.json` records the render and layout checks. `results/DEVELOPMENT_V6.md` records the figure-export permission failure and its successful repair. The earlier v5 timeouts remain in the historical record and are not counted as successful executions.

The root-level SHA-256 ledger covers the release files other than the ledger itself. It is an integrity check, not a theorem prover.
