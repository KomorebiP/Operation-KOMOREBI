# Proof ledger — v0.38

Status: clean source replay PASS. Archive replay is performed separately on the released payload and linked with its hash in the external receipt.

## Formal inventory

- Seven new modules, 754 new source lines.
- 44 theorem declarations, 15 definitions, one abbreviation.
- All 60 named declarations audited with `#print axioms`.
- Permitted reported axioms only: `propext`, `Classical.choice`, `Quot.sound`.
- Active proof escapes, custom axioms, custom opaque declarations, unsafe/native_decide uses: zero.
- All seven compiler exits and the additional axiom-audit exit: 0.
- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- Compiler flag `-DwarningAsError=true`.

## Main claims and dependencies

| Claim | Formal declaration | Evidence |
|---|---|---|
| Ordered derivative | `tangent_eq_sum` | Kernel-checked algebra |
| Nonlinear remainder | `remainder_lipschitz` | Ordered recurrence + ultrametric bound |
| Exact ball image | `power_ball_image` | Remainder estimate + Banach theorem |
| Certified inverse bounds | `inverseLinear_norm`, `inverseCertificate_left/right` | Integral B + matrix basis |
| Integral matrix root | `matrix_power_unique_iff` | Exact ball image + norm/congruence equivalence |
| Actual unit root | `matrix_unit_root_iff` | Integral root + unit-of-power lemma |
| Finite-ring criterion | `matrix_unit_root_finite_iff` | Unit root iff + reduction of coefficients |
| Residual singularity, noncommuting success, obstruction | declarations in Controls | Concrete kernel-checked computations |

All names are in `Komorebi.StrongArtin.MatrixHensel`, with control names in `.Controls`. DECLARATIONS.json contains the complete inventory. Source hashes and compiler commands are in verification/fresh/RESULT.json.

## Exact computation

`checks/exact_matrix.py` uses rational Gaussian elimination, proves both matrix products exactly by assertions, clears only p-denominators, and compares complete finite images. The contract, stdout/stderr, results, and validated provenance manifest are in computations/exact_matrix/.

| Center | p | d | s | m | H | Horizon candidates | Next-level candidates | Accepted targets at H |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [[1,1],[0,1]] | 2 | 2 | 2 | 3 | 5 | 256 | 4,096 | 16 |
| [[1,1],[0,1]] | 3 | 3 | 2 | 3 | 5 | 6,561 | 531,441 | 81 |
| [[1,1],[1,2]] | 2 | 2 | 1 | 2 | 3 | 16 | 256 | 4 |

All three image comparisons passed: 6,833 horizon candidates and 535,793 candidates one level deeper. These exhaust the declared residue balls, not all centers or p-adic inputs. They do not prove the general infinite theorem. The mod-2 square control alone has a specialized Lean certificate; the general Lean theorem applies to any supplied certificate.

## Provenance limits

The new-source dependency closure consists of these seven modules and the pinned Mathlib cache. No historical project source module is imported by the new proof. The exact v0.37 checkpoint is preserved with SHA-256 `71eb1f38502ce089e9a5ae58bea8fc831f875d6bd83144fe0f4663328e77c689`; it is not replayed in this release. There is no second-kernel verification. See FAILURE_LEDGER.md for rejected development attempts and SELF_REVIEW.md for the audit scope.
