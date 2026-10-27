# Reachability and finite descriptions: checked return

## Scope and ancestry

Owner: `/root/reachability`. Base: checked Lean v0.6.0.

- Parent archive SHA-256: `032f61f0e176f0f3abfeb3615b8936ebd9edb7c3f9a07b6b8ad25877ec7aef70`.
- Printed monograph PDF SHA-256: `a33739eec9f11a1c8c6e94c30301963d9ed1386ea2ede04041bbaa644b046ecc`.
- Owned production artifact: `RealizationBoundaries/Reachability.lean`.
- Final source SHA-256: `cf12de97bcfcfd14303966a18f41a4025587b767dace74749857cd90394af45c`.

No shared root imports, verification scripts, contracts, coverage registry, or ledgers were edited by this work package.

## Exact results

**Printed Proposition 1.5 is complete.** `FiniteDescriptionGrammar Alphabet Target` has a validity subset of actual finite strings `List Alphabet` and a single semantic target per valid string. `Target` can in particular be the group-isomorphism-type target used by a grammar. The semantics and validity predicate are arbitrary and need not be computable. For every countable alphabet:

- `finite_description_outputs_countable` proves the actual semantic image countable.
- `finite_description_cardinal_bound` proves `Cardinal.mk g.outputs ≤ Cardinal.aleph0`.

**Printed Theorem 1.8 is complete.** The direct sum is represented canonically as the actual subgroup `packetSum M` of the dependent product with finite support. It is not a finite truncation. `packet_decomposition` derives its finite packet sum, and `packetTransfer M T i j a` is the literal `j` coordinate after applying `T` to the literal `i` packet injection. The input hypothesis is precisely vanishing of these primitive transfer blocks outside allowed directed edges.

- `operatorWord` permits only finite lists of the declared primitive operators and includes the empty word (identity).
- `primitiveOperatorHull` is the additive subgroup closure of their seed images.
- `GraphReach` is finite directed reachability from the union of seed supports.
- `graphReach_iff_finite_path` identifies that predicate with `Relation.ReflTransGen`, including empty paths.
- `packet_operator_support` derives support confinement for one primitive step from the transfer blocks by finite decomposition.
- `operator_hull_reachable` proves the actual hull is contained in the actual subgroup supported on reachable packets.
- `unreachable_packet_obstructs` proves the omitted projection annihilates the entire hull, and a nonzero packet witnesses that the hull is proper.
- `unreachable_packet_obstructs_topological` proves the same properness after topological closure whenever the omitted projection is continuous into a Hausdorff packet. It uses its actual closed kernel.

No converse sufficiency of reachability is asserted. Empty seed sets, zero packets, arbitrary dependent packet groups, arbitrary index types, and arbitrary primitive-operator sets are admitted. The properness conclusion explicitly requires a nontrivial omitted packet, as in the printed theorem.

## Verification

- `verification/development/Reachability_005.json`: compiler exit 0, warnings as errors, autoImplicit false, 2.63 seconds, exact final source hash above.
- `verification/development/Reachability_replay.log`: `leanchecker --verbose RealizationBoundaries.Reachability`, exit 0.
- `verification/development/Reachability_contract.log`: exact theorem-type checks and axiom reports, compiler exit 0.
- The three checked headline results use only `propext`, `Classical.choice`, `Quot.sound`.
- Preliminary failed compilations are preserved as development receipts 001–004. They were implementation/import/API issues and are not accepted proof evidence.

The compiler/runtime is the pinned Lean 4.34.0-rc2 kit shared read-only at `/workspace/scratch/ea498747acd5/runtime/parts/Komorebi_Portable_Lean_4.34.0-rc2`. The package-wide clean build, production audit and negative-controls run remain the coordinator's integration gate. These local checks do not replace that gate.

## Integration

Import `RealizationBoundaries.Reachability` in the root entrypoint. Add `Reachability` to the serial production/replay module list. Registry 1.5 can cite the two finite-description theorems. Registry 1.8 can cite `operator_hull_reachable`, `unreachable_packet_obstructs`, and the topological extension.

The grammar work package was notified that the finite-description interface is available for reuse. There are no unresolved mathematical obligations for the exact printed 1.5 or 1.8 contracts in this work package.
