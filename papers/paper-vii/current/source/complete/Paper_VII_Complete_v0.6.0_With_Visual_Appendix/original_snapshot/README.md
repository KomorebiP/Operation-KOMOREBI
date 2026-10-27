# Projector-Resolved Seed Calculus VII
## Finite proofs complete · v0.6.0

**Author: Komorebi P.**  
**Date: September 6, 2026**

**19 of 19 named finite-sector items now have Lean coverage under their recorded assumptions.** The final item, 6.4, is completed by constructing the actual global range bundle and proving the projected connection and its curvature on smooth real manifolds without boundary. There are **323 checked theorem declarations in 25 modules**, including **67 new declarations**. Supporting lemmas are included in this count.

**The five continuum conjectures remain unproved.** Finite proof completion is not a claim that every sentence, numerical experiment or conjecture in the original manuscript has been verified.

## The completed geometric construction

`GlobalRangeBundle` builds the actual fixed subspaces of P, their total space, open local domains and base-preserving local product homeomorphisms. It proves smooth, fiber-linear transitions, inverse and cocycle laws, and local constancy of rank. No bundle atlas is assumed.

`GlobalProjectedConnection` defines the actual derivative `nabla_X s = P (mvfderiv s X)`, with an additional fiber-valued version. It proves the connection laws, smoothness and local gluing.

`ManifoldProjectedCurvature` proves

```text
(nabla_X nabla_Y - nabla_Y nabla_X - nabla_[X,Y]) s
  = P (dP[X] dP[Y] - dP[Y] dP[X]) P s.
```

The derivative and Lie bracket are actual Mathlib manifold constructions. The proof localizes through arbitrary manifold charts, derives differentiated projector identities and cancels the second derivatives. It does not assume a global coordinate chart or the curvature formula.

`ProjectedBundleCompletion` checks actual local-homeomorphism overlap identities, intrinsic local smooth-section equivalence, the full connection gauge law and fiber-valued curvature. `LocalProjectedCurvature` supplies point-local differential identities.

| New module | Theorem declarations |
|---|---:|
| GlobalRangeBundle | 22 |
| LocalProjectedCurvature | 6 |
| GlobalProjectedConnection | 10 |
| ManifoldProjectedCurvature | 17 |
| ProjectedBundleCompletion | 12 |
| **Total added** | **67** |

## Exact scope

The global curvature theorem is for smooth real boundaryless parameter manifolds modeled on complete normed real spaces, and bounded real-linear idempotents on complete normed real fibers. It includes finite-dimensional real differential calculus underlying quantum spaces. No orthogonality, pre-existing range-bundle atlas, global frame or globally constant rank is assumed. The construction supports locally varying ranks on disconnected components.

The actual smooth atlas is exposed directly, rather than registered as a Mathlib `ContMDiffVectorBundle` instance. Complex spaces can be viewed through their underlying real normed spaces; a separate complex-bundle typeclass wrapper is not supplied. The boundaryless scope of the curvature result is explicit. These implementation conventions must not be silently broadened into a boundary/corner theorem.

Earlier amendments remain in force, including the full-resolvent invertibility hypothesis for the Feshbach theorem. Consult `THEOREM_LEDGER.json` and the earlier supplements for each exact statement. The original manuscript PDF and TeX are unchanged.

## Verification

The authoritative cumulative report is `verification/final_finite_release_run/SUMMARY.json`.

All 25 active modules were freshly compiled under Lean **4.34.0-rc2**, Mathlib revision **aeb72f1e9981b6d35b426b16dca7759be3e7ba06**. All 323 theorem-level axiom audits passed, with dependencies confined to `propext`, `Classical.choice` and `Quot.sound`. One upstream theorem is axiom-free. Six proof-bearing constructed objects were separately audited in `CONSTRUCTED_OBJECTS_AUDIT.json`.

Every final module exited with code 0, with warnings treated as errors. Active sources contain no admitted proofs or added axiom declarations. Both deliberate invalid controls were rejected. All 16 Python verifier regression tests passed. Nine of 16 captured development checks failed before correction; source snapshots and logs are preserved separately.

The portable kit was restored with all seven archive-part checksums and the combined checksum checked. Its runtime is not duplicated in this source ZIP.

## Recheck with the portable kit

From the extracted release directory:

```bash
python scripts/verify.py --kit /path/to/kit --out verification/my_run --timeout 240
python scripts/audit_constructions.py --kit /path/to/kit --run verification/my_run
python scripts/test_verifier.py
```

For a host with short command limits, use `--max-checks 3 --resume` on the first command and repeat until `COMPLETE PASS` is returned. A paused run is not a successful complete run. Local dependencies are compiled in order. Resume checks cover source hashes, transitive imports and public/private compiled interfaces. The construction audit refuses stale sources or build interfaces.

The low-memory launcher uses ordinary Lean, one worker and strict warnings. It does not enforce a memory limit. The source ZIP omits generated interface caches; these are recreated on checking.

## Files and preservation

`manuscript/Paper_VII_Finite_Proofs_Completion_Supplement.pdf` is the seven-page completion supplement. Its TeX source is included. All 20 upstream proof files, all earlier manuscript supplements and the original manuscript are preserved unchanged. `provenance/UPSTREAM_PRESERVATION_sixth_block.json` records the byte comparisons. Historical reports retain their original release labels; the final 25-module report is the one named above.

`SHA256SUMS.txt` covers distributed files. `verification/ARTIFACT_CHECK.json` records the pre-package audit; the separately delivered artifact check also records archive integrity and the archive SHA-256.

This block did not rerun the original numerical suite, rebuild Papers I-VI, or independently recheck all imported Mathlib proofs. The five continuum conjectures remain unproved.
