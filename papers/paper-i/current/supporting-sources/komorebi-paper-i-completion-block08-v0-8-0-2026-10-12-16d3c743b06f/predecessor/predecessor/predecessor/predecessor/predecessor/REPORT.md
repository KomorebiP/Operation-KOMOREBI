# Paper I completion: Block 03

**Result: PASS for the full current 28-module source closure and the new primary-block/invariant-factor extension.**

This is a verified completion block, not full formalization of the expanded monograph. The original 35-row component and all Block 02 mathematical sources are unchanged.

## Mathematical results

For every finite-dimensional operator T over an arbitrary field, the new Lean code constructs the actual polynomial-module decomposition into positive irreducible-power quotients and proves

    seedRank_{k[T]}(V) = maximum number of primary blocks with the same irreducible ideal.

The proof supplies the decomposition, residue-field lower bounds and Chinese-remainder shared generators internally. It does not receive the desired rank equality, an eigenbasis, a Jordan basis or extraction certificates from the caller. Nonlinear irreducible factors are included. Associated irreducibles are grouped by their principal ideals. Exponent-zero factors are removed as zero modules.

The canonical rank is proved equal to this count, and the maximum is proved independent of the chosen actual primary presentation. Cyclicity is equivalent to having no repeated primary label. This criterion is linked to the already proved minimal-polynomial/characteristic-polynomial equivalence.

The conditional invariant-factor corollary is also proved: an actual nonconstant divisibility-chain presentation with r factors has seed rank r. Its count is derived from coordinate generators and a common irreducible residue-field quotient, not assumed. Existence or computation of a sorted invariant-factor presentation is not asserted by that conditional theorem.

These are classical mathematical results integrated into Paper I's actual objects and seed-rank definitions. Declaration counts are not claims of independent novelty.

## Actual executed verification

| Check | Result |
|---|---:|
| Preserved predecessor manifested payloads | 378 / 378 |
| Freshly compiled production source files | 28 / 28 |
| Original + Block 02 + Block 03 modules | 20 + 4 + 4 |
| New mathematical modules / import-only root | 3 / 1 |
| Original normative contract rows | 35 / 35 |
| Original mapped declarations resolved | 84 / 84 |
| Public-or-coverage declaration names resolved | 173 |
| Complete compiler-owned declaration audit | 1301 / 1301 |
| Entries owned by new Block 03 modules | 78 |
| New public theorem / definition / structure declarations | 32 / 10 / 1 |
| Exact same-kernel production-module replays | 28 / 28 |
| Additional regression-module replay | 1 / 1 |
| Original + Block 02 + Block 03 mathematical assertions | 4 + 12 + 18 = 34 |
| Deliberately invalid controls rejected as intended | 11 / 11 |
| Positive foreign-namespace audit control | 1 / 1 |
| Accepted expected-outcome commands, including environment checks | 90 / 90 |
| Post-replay source/object identity checks | 28 / 28 |
| Exact dependency Git revisions checked | 9 / 9 |

The only reported transitive axioms were `Classical.choice`, `Quot.sound`, `propext`. No production placeholder or additional custom axiom passed the gate. The owned inventory includes definitions, private/generated proofs, structure fields, constructors and recursors. It is not a count of independent theorems.

The composed `run_block03.sh` launcher was actually executed. It built all project modules into a new, initially empty object directory and did not import saved predecessor project objects. Its recorded wall time was 1492.996 seconds. This excludes development, runtime recovery and final packaging. Every command receipt, full log, source snapshot and final object is preserved.

## Exact mathematical boundaries

The full printed single-operator theorem defines each multiplicity as

    dim_{k[t]/(p)}(X_p / p(T)X_p).

This block proves the actual primary-block count formula and constructs surjective residue-field maps. It has not yet identified the grouped primary factor with the literal intrinsic X_p or proved that the residue map's kernel is exactly p(T)X_p. Surjectivity is not silently treated as that kernel/quotient identification. Individual intrinsic multiplicities are therefore not yet identified, even though their presentation maximum is proved invariant.

The arbitrary algebraically closed, non-diagonalizable eigenspace formula and the complete scalar-extension clause of the six-way cyclic criterion also remain. The earlier self-adjoint result remains verified and unchanged.

All new constructions are noncomputable. There is no executable factorization routine, invariant-factor algorithm, eigensolver or extraction/performance guarantee.

## Publication coverage delta

All 108 publication statements and their source-proof fields are unchanged. Exactly one proof-level record moves from partial to covered: `PSC-I-C-INVARIANT-FACTOR-COUNT`, at its printed conditional scope. Four other entries receive more precise progress and remaining-work notes without a status upgrade.

The 69 proof-level records now have **16 covered, 33 partial and 20 not mapped**. These are different units from the 35-row formal contract. The primary-count construction is substantive progress even though the more expansive intrinsic-quotient record remains partial. No blanket completion percentage is inferred from these counts.

The deterministic coverage generator was rerun, producing byte-identical JSON and Markdown maps. The original normative row sequence and all 84 declaration names were checked directly against the mapped-type file.

## Tests and failed development attempts

The new suite contains 18 exact Lean assertions. They cover nonlinear irreducibility over the rationals, repeated-primary lower bounds, one nonlinear squared block versus its larger base-field dimension, the zero module, empty label sets, dropped exponent-zero factors, associate labels, invariant-factor chains and shared CRT generation across coprime factors.

Four new invalid applications are rejected: treating a zero exponent as positive, using base-field residue dimension as the seed count, using a two-generator witness as a one-generator witness, and supplying reflexive divisibility where a full invariant-factor chain is required. The earlier seven rejection controls and their positive audit control were also rerun.

The development log records 16 rejected runs among 25 recorded development compilations, including API probes and intermediate typing, simplification, dependent-index and proof-witness errors. The accepted sources were subsequently rerun cleanly. No rejected or exploratory run is counted toward PASS.

A separate foreground status-polling command was reported timed out by the tool. It did not interrupt the Lean verification process. The monitoring incident is retained separately and is not counted as a proof-check result.

Three negative fixture expressions were changed before their execution to use explicit applications, selecting the compiler's `Application type mismatch` diagnostic rather than a differently capitalized bare type-mismatch message. Their before/after hashes and snapshots are preserved. This adjusted the diagnostic form of the same invalid mathematical uses, not the production proofs or the required rejection outcomes.

## Trust, reproduction and next restart

The pinned Lean runtime was restored from the authenticated offline archive and bound to the same compiler and dependency versions as the predecessor. Cached upstream Mathlib objects were reused rather than rebuilt or fully replayed. The module replays use Lean's own kernel, not an independently implemented verifier. The TeX-to-Lean map is a reviewed semantic artifact, not a kernel interpretation of prose.

The compact package contains the complete predecessor, new source, tests, audit tools, compiled objects, logs, failed-development records, coverage map and progress ledger. The large runtime remains an external prerequisite. Publication PDFs were not rebuilt. License-status records are inherited unchanged.

**Next restart:** prove the intrinsic-primary and exact residue-kernel/quotient identification, then derive the arbitrary-operator geometric formula and complete the remaining cyclic-criterion clauses. Papers II–XII have not been rerun in this sweep.

No audit or compiler process remains active at this handoff. See `CONTINUE_HERE.md` for exact source paths and the next proof obligations.
