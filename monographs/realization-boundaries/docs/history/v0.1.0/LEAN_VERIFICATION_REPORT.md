# Lean verification report

## Result

**PASS — algebraic-core tranche, not full-book formalization.**

The actual infinite-coordinate constructions have been compiled and audited in this session. The original finalized publication is preserved, and the new formal scope is described by `docs/MONOGRAPH_COVERAGE.md`.

| Gate | Observed result |
|---|---|
| Production modules | 9 compiled from clean project output |
| Import entrypoint | 1 compiled |
| Explicit source theorem/lemma declarations | 90 |
| All audited project declarations | 232 |
| Production source lines | 967 |
| Positive contract proofs | 11 passed |
| Expected rejection controls | 10 rejected for the required diagnostics |
| Production kernel replays | 9 passed |
| Compiler/verification commands | 33 gates passed |
| Source endpoint identity | PASS |
| Imported cache and compiler endpoint identity | PASS across 14,255 recorded files |

These are different counts. Generated helpers, structure declarations, instances, and definitions are included in the full declaration count. They are not counted as independent mathematical discoveries or as completed monograph theorems.

Accepted compiler identity:

```text
Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)
```

All nine dependency revisions match the lockfile. Mathlib is pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The accepted run started at `2026-10-23T17:16:31.809780+00:00` and ended at `2026-10-23T17:22:05.318428+00:00`. Its raw duration and individual command durations are recorded in `verification/accepted/run.json`.

## What the new proofs establish

1. **The actual product and quotient.** Finite support is equivalent to torsion in the unrestricted prime product. Every positive integer acts bijectively on the actual quotient P/D. The rational module structure is then derived, not supplied as an assumption.
2. **Admissible preimages and exact roots.** For every rational subspace W, H_W is an actual subgroup of P. The root condition is equivalent to vanishing at the prime coordinates dividing the multiplier. Successful coordinate roots, obstructing coordinates, purity, and torsion statements are proved.
3. **Canonical algebraic quotients.** An actual additive equivalence identifies H_W/mH_W with its finite divisor-coordinate product. The map on representatives and the coordinate transition laws are proved. Every map to a finite additive-group target kills a canonical integer-multiple subgroup. This is the cofinal-kernel input to the later completion theorem, not a proof of profinite completion by itself.
4. **Explicit section and nonsplit extension.** The reduced-rational section has the required zero branch at denominator primes, and its quotient image is exactly the intended rational multiple. The rational quotient map has no additive section when its target is nontrivial.
5. **Cocycle and normal-form group.** The infinite-coordinate cocycle has support inside a finite denominator-prime set. Its exact laws are proved. A separate `NormalForm` group carries the twisted operation, and a genuine `AddEquiv` identifies it with the original ambient preimage. No D-valued correction can remove the cocycle.
6. **Every binary selector.** The prime-pair construction proves infinite selected support for all selectors. Selected primes obstruct roots of the marked element, and omitted primes admit them. The all-false selector's no-half and third-root tests pass as concrete formal corollaries.

These are universal Lean proofs, not extrapolations from finite arithmetic tests. The Python assertion counts from the earlier monograph release were not rerun or added to this Lean count.

## Audit policy

Every audited declaration has transitive axiom dependencies contained in:

```text
propext
Classical.choice
Quot.sound
```

No production declaration is an axiom or unsafe, and no accepted theorem depends on `sorryAx`, a project-specific axiom, or a native-decision trust axiom. The audit selects declarations by defining module as well as namespace, includes generated helpers, and fails on an empty inventory. The exported exact types and per-declaration dependencies are in `verification/accepted/declarations.json`.

The negative controls deliberately attempt an impossible half-root, uniqueness for a finite selector, removal of the cocycle, unique division without positivity, a composite prime coordinate, a unit at a denominator prime, an undeclared implicit variable, an extra axiom, an admitted proof with warnings suppressed, and an unsafe definition. Compilation must fail with the designated diagnostic. Positive proofs establish the corresponding mathematical obstructions independently of those failure messages.

## Trust boundary

Kernel replay uses Lean's own kernel. It is not an independent implementation or external peer review. The compiler, standard logical axioms, imported compiled dependencies, runtime and hardware remain trusted. The compiler and Mathlib were restored from the user's archived kit, not rebuilt from source or independently authenticated against upstream releases. The accepted run recorded hashes for imported cache artifacts and compiler files before the clean project rebuild and after the checks, and found no changes. Endpoint equality does not detect a transient alteration restored before the second snapshot.

The source is noncomputable where it uses classical membership or choice. An existence proof or a rational-section definition is not a formal verification of oracle-computable presentation semantics. The Python normal-form engine has not been proved equivalent by extraction.

## Remaining work

The full topology and profinite-completion identification, reverse pure-preimage correspondence, countability/dimension results, radical root-fiber counts and CRT cyclic identification, isomorphism classification, all-homomorphism and endomorphism structure, seed ranks, oracle-degree theorem, and grammar diagonalization remain to be formalized. Some have checked algebraic inputs now. None is silently assumed or advertised as completed.

The source map retains every numbered result in the original 45-result registry. The book's unique-normal-form result is marked partial only because its countability clause is not yet formally established. Its existence, uniqueness, group laws and actual additive equivalence are checked.

## Failures encountered and resolved

Direct compiler downloads failed because network name resolution was unavailable. The existing five-part offline Library runtime provided the working compiler and caches. A previous attempt's runtime reset occurred before proof compilation, so no verification from that lost attempt is counted here.

Several development compilations failed on API names, scalar-instance normalization, exact type annotations, or warnings promoted to errors. The failed logs remain in `verification/development`. In particular, the normal-form group initially needed its zero/add/neg instances separated before defining recursive scalar operations. Positive root tests needed explicit natural-number multipliers to avoid an ambiguous scalar instance.

The first full declaration-audit attempts timed out. The audit was rebuilding the module-name array inside the per-declaration scan. Caching that array once removed the unnecessary repeated work; the accepted audit passed. This was a verification-tool implementation defect, not acceptance of an unproved theorem. Intentional negative-control failures are separately identified and are successful rejection tests, not unresolved production failures.

## Reproduction

```bash
export KOMOREBI_LEAN_KIT=/path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 scripts/verify.py --output ../new-boundary-verification
```

Use a new evidence directory. The verifier performs real compiler and replay calls and exits nonzero on a failed gate. A rejection is accepted only with a nonzero exit, no timeout, and the required diagnostic. The accepted negative logs were additionally checked for missing-import and runtime-startup failures; none was present.
