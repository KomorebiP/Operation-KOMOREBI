# Paper I completion: Block 06

**Result: PASS for the full six-way cyclic-matrix criterion, the new scalar-extension/primary/companion constructions, the authenticated predecessor, and complete same-kernel project replay.**

**Date:** 11 October 2026. **Version:** 0.6.0.

This closes the expanded publication's cyclic-matrix corollary. It does not claim that the entire expanded monograph is formalized. Every predecessor mathematical source and dependency pin remains unchanged.

## Mathematical completion

For every finite-dimensional endomorphism T over an arbitrary field k and any field extension K, the new source proves the literal identity

    minpoly_K(T.baseChange K) = map_{k→K}(minpoly_k(T)).

It derives both preservation and reflection of cyclicity for the actual tensor-product operator on K ⊗_k V. Neither separability, algebraicity, finite extension degree, nor characteristic zero is required. The polynomial and cyclicity extension theorems include the zero space.

For nonzero V, the development proves the exact six-way equivalence between an actual cyclic vector, canonical seed rank one, cyclicity of every nonzero intrinsic primary component, an actual one-invariant-factor presentation, minpoly=charpoly, and geometric multiplicity one for every spectral value after the literal extension to an algebraic closure.

The one-factor result includes a constructed basis in which the original operator is the standard companion matrix. The monic factor is proved to be the minimal polynomial. A separate theorem proves that any actual nonconstant invariant-factor chain has exactly one factor iff the operator is cyclic. No decomposition, primary multiplicity, spectral, polynomial-preservation, or seed-number conclusion is an input to the final six-way theorem.

The construction supplies mathematical existence and equivalences, not an executable canonical-form algorithm. It does not construct a sorted invariant-factor decomposition for every noncyclic operator. The six-way statement retains its nonzero-space guard: the zero space is cyclic in the at-most-one-generator sense but has seed rank zero.

## Actual executed verification

| Check | Accepted result |
|---|---:|
| Predecessor manifested payloads authenticated | 1325 / 1325 |
| Entire predecessor compared with supplied ZIP | 1326 / 1326 files |
| Predecessor source/object pairs authenticated | 37 / 37 |
| New production modules freshly compiled | 5 / 5 |
| Original formal-contract rows preserved | 35 / 35 |
| Original mapped declarations resolved | 84 / 84 |
| Public-or-coverage declaration names resolved | 288 / 288 |
| Complete source-owned declaration audit | 1513 / 1513 |
| Source-owned entries from new modules | 38 |
| Same-kernel production-module replays | 42 / 42 |
| Additional boundary-module replay | 1 / 1 |
| New exact mathematical boundary assertions | 21 / 21 |
| Deliberately invalid controls rejected | 9 / 9 |
| Positive foreign-namespace guard control | 1 / 1 |
| Accepted expected-outcome commands | 76 / 76 |
| Final production source/object identities | 42 / 42 |
| Exact dependency revisions checked | 9 / 9 |

The separate 1,326-file comparison includes the predecessor manifest itself.

The five new modules were compiled into an initially empty isolated object directory, using authenticated predecessor objects and pinned upstream imports. All 42 production modules were then replayed serially. **The 37 predecessor sources were not freshly recompiled in this block.** Their source and object bytes were authenticated. No development object was used to replace a fresh compilation of a new module.

The boundary suite was freshly compiled and replayed. Its three prior boundary-module imports were authenticated, not separately rebuilt or replayed as test suites here. The original 35-row contract was not silently expanded or rewritten. Its 84 mapped names are included in the resolved declaration list.

The new source has 25 public theorem declarations and 4 definitions in four mathematical modules plus an import-only root. The complete owned inventory also includes supporting and generated declarations. These counts are not counts of independent discoveries.

Only `Classical.choice`, `Quot.sound`, `propext` appeared as transitive axioms. No production placeholder or additional custom axiom passed the ownership gate. The scope of that statement is production source, not intentionally invalid fixtures or archived failed drafts.

## Boundary checks

The rational test module is a one-coordinate product explicitly identified with Q[t]/((t²+1)²) by `squaredOneFactor`. Its actual polynomial-action operator has dimension four, exact minimal polynomial (t²+1)², and no rational eigenspaces of positive dimension. The new tests prove the exact mapped minimal polynomial after its actual complex extension, unchanged degree four, cyclicity, and geometric multiplicity one at every actual complex spectral value. This exercises scalar extension rather than substituting a theorem over an originally algebraically closed field.

The suite also verifies an actual companion basis and quotient-action intertwining, entrywise companion signs and orientation for t²+1, noncyclicity of repeated Jordan chains after extension, zero-space conventions, and characteristic-two instances of both extension identities and cyclicity descent.

The rejection suite detects missing finite-dimensionality, missing nontriviality, missing algebraic closure, the wrong companion sign, an invalid substitution of a cyclic operator for a repeated-chain operator, a false equality, and a placeholder. Imported custom-axiom and placeholder controls in foreign namespaces are correctly rejected, while the clean foreign-namespace control is accepted.

## Failed attempts and recovery

There are 14 recorded development compiler runs: 7 rejected drafts and 7 zero-exit exploratory runs. Rejected drafts involved API names or argument order, tensor-endomorphism elaboration, polynomial map inference, a split qualified name, a local-instance style check, polynomial-module action rewriting, companion-matrix definitional equality, monic divisibility, dependent finite-index instances, a coefficient simplification, and the missing characteristic-two field import/instance. The preserved snapshots and compiler diagnostics show which error occurred in which attempt.

The initial foreground driver was interrupted by the tool's execution limit before an exit receipt could be collected. Its log remains explicitly unaccepted. A persistent driver with per-command receipts was used thereafter. One source-inspection command also addressed the AEval source under the wrong directory; it was corrected to the pinned polynomial-module path. No predecessor theorem or dependency pin was altered by these recoveries.

None of the exploratory, rejected, or interrupted runs is counted as final acceptance. The fresh accepted run, after the corrections, completed every required check. The final run's exact wall time was 1734.492 seconds, excluding development, runtime recovery, and packaging.

## Publication coverage

All 108 stored statements, source proofs, and source-location/hash records are unchanged. Exactly one proof-level record changes status: `PSC-I-C-CYCLIC-MATRIX` moves from partial to covered.

The 69 proof-level records now have **19 covered, 30 partial, and 20 not mapped**. These are reviewed statement-correspondence categories, not an overall completion percentage. Legacy conditional wrappers are retained for compatibility; the new unconditional theorem provides the stronger publication-facing result.

## Trust and reproduction

The combined `run_block06.sh` launcher was actually executed. Its command-level receipts record observed exits, elapsed times, complete logs, source snapshots, and hashes. The exact Lean runtime and nine dependency revisions are authenticated.

Mathlib's pinned cache is reused rather than freshly rebuilt or fully replayed. Replay uses Lean's own official kernel, not an independently implemented verifier. The publication correspondence is reviewed semantic matching, not a kernel interpretation of TeX prose. All constructions here are noncomputable mathematical objects and proofs. Publication PDFs were not rebuilt. Prior license-status records remain unchanged. The large runtime is an external prerequisite.

## Next restart

Stay on Paper I. Prove the general noncommutative module-top/Nakayama lifting theorem, then the local residue-division-ring formula. A genuine noncommutative upstream Nakayama form was identified in the pinned Mathlib source and is recorded in `CONTINUE_HERE.md`; identifying that API is not counted as a new verified project theorem.

The nonsplit semisimple, expanded packet/functorial/topological, and executable-algorithm obligations remain. Papers II–XII have not been rerun in this sweep.

No audit or compiler process remains active at this handoff. `evidence/HANDOFF_POSTFLIGHT.json` records the final source/object, log, startup-guard, and process checks.
