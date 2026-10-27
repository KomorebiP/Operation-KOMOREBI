# Machine-Native Reasoning: Reviewed Mathematical Core

**PASS · 27/27 selected source results · Version 1.0.0**

Author: Komorebi P.

## Completed mathematics

Core 3.2, the last selected source result, is now formally accepted. For finite worlds, a cell partition and an arbitrary target map, admitted evidence consists exactly of unions of cells. If r cell–target pairs are attained, correction signatures correspond exactly to all subsets of those pairs. There are 2^r signatures. Exactly r fixed binary bits suffice, with exact readout and evidence updates after every finite continuation. Every exact fixed-b-bit memory on all candidate subsets satisfies r ≤ b.

The construction uses attained pairs rather than the full cell/target product, so unused target values add no states. Empty candidates, contradictory evidence, empty worlds, repeated targets across cells and multiple targets within a cell are retained. The source endpoint includes nonempty cells. The internal result also permits unused labels.

The original proof chooses one representative per included pair. The Lean proof instead takes the full preimage of the selected pairs. Both realize exactly the same occupancy records. The formal binary construction uses classical finite enumeration; it is not a certified executable implementation or a timing result.

The source eight-world sensor has four attained pairs, sixteen signatures and four necessary and sufficient bits. Examples show why the current target set loses needed associations, why splitting a cell invalidates the old memory, and why removing singleton-cell evidence can invalidate the lower bound.

## Verification actually completed

| Check | Each cold run |
|---|---:|
| Production modules, including aggregate | 79 |
| Substantive kernel replays | 78 |
| Axiom-audited declarations | 3,018 |
| Elaborated theorem constants, including generated auxiliaries | 2,364 |
| Expected negative-control outcomes | 188 |
| Frozen proof-gate inputs | 501 |
| Authenticated upstream artifacts | 13,440 |
| Required commands | 372 |

The first run took 739.3 seconds; the separately extracted run took 725.3 seconds. Both began with empty local object directories, used warnings as errors and terminated without timeout. All 79 production objects agree byte for byte. The comparison passed 663 checks, including exact snapshot membership and every source hash against both receipts. Snapshot SHA-256: `727af49876690ee83bb18b46895dea01aae296bfeaf83331221870970e59daf0`.

The actual transitive axiom union is `Classical.choice`, `Quot.sound`, `propext`. The production scan, actual compiled declaration audit and rejection controls cover proof placeholders, additional axioms and forbidden implementation hooks. There are 1,927 authored declarations and 1,273 authored theorem declarations, of which 86 and 51 are new here. These are code inventories, not counts of independent discoveries.

All 75 inherited substantive modules and all five source-book files retain their exact bytes. The 181 inherited negative controls remain, with seven added for Core 3.2. Expected mathematical failures are accepted only with the specified diagnostics; missing imports, parse failures, unknown identifiers and timeouts do not count as rejection evidence. Complete control classifications are in the machine-readable reports.

Nonproduction helper differences: Audit.olean. The generated audit source and complete axiom records agree. An independent semantic review separately checked definitions, quantifiers, source correspondence, realizability, binary bounds and boundary cases. It found the pinned result proved as written. That review is not a separate proof kernel.

## Finite regression

The exact integer/Boolean enumerator covers all canonical partitions and all ternary target maps on zero through five worlds: 14,008 primary families. With four explicit boundary families, it checks 425,232 candidate classifications, 3,661,286 updates, 3,661,286 event readouts and 267,114 realizations. It additionally checks all 65,536 combinations of a sensor candidate subset and an ordered two-event sequence, and rejects all 65,553 encoding assignments for (r,b)=(1,0),(2,1),(3,2). Both cold gates reproduce the same finite record. The universal theorem is supplied by Lean, not inferred from these bounded computations.

## Execution history and reproduction

The saved five-part portable runtime was restored and its complete archive hash verified. The first direct compiler startup failed with `failed to locate application`; the distribution's shipped executable-path adapter resolved this host issue. Both accepted gates used that same adapter. Earlier elaboration failures and their source snapshots are retained under evidence/development19. They are development attempts, not accepted proof runs.

Lean is pinned to 4.34.0-rc2 and mathlib to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine dependency revisions and actual imported cache artifacts were checked. The external dependency cache was reused, not rebuilt. Both runs use the same Lean kernel. No native Windows execution, independent kernel, host-runtime correctness or learned-system capability is claimed.

Use RUNTIME_REPRODUCTION.md and the root README for the offline commands. The immutable package manifest covers its exact regular-file set. Current proof objects and both receipts are included; the separately stored runtime is not bundled.

## Publication boundary and remaining work

This completes the 27 selected statements in Reviewed Core v0.2. The refreshed reader preserves their original mathematics and includes a new formal-status appendix. It is titled Reviewed Mathematical Core.

The latest 1,155-page, 97-chapter expanded monograph was not recovered. The accessible prose-refinement report records that edition, but neither `Machine_Native_Reasoning_Prose_Refined_Source.zip` nor its matching PDF was present in the searched files or inspected repository sources. The available older monograph and continuation are not relabeled as that latest edition. Recovery limits and exact inspected sources are preserved in BOOK_RECOVERY.md and github_recovery/.

To finish the expanded publication, recover its exact source archive and matching PDF, reconcile that edition against the completed selected-core status, rebuild it, and audit its own coverage and publication checks. That is a separate remaining task; the present 27/27 result does not certify all specialist chapters.
