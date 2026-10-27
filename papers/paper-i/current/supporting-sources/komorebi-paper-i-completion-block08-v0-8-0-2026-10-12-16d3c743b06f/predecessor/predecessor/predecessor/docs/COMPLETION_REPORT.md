# Paper I completion: Block 05

**Result: PASS for the new geometric-multiplicity and cyclicity extension, authenticated predecessor, and complete same-kernel replay.**

This is not a claim that the expanded monograph is entirely formalized. The original 35-row component and all Block 02–04 mathematical sources and dependency pins remain unchanged.

## Mathematical completion

For every finite-dimensional endomorphism T over an algebraically closed field k, the new Lean sources prove

    seedRank_{k[T]}(V) = max_{a in spectrum(k,T)} dim_k ker(T-aI).

The natural-valued seedFinrank formula is proved as well. No diagonalizability, self-adjointness, eigenbasis, Jordan basis, supplied decomposition, multiplicity certificate, or assumed seed-rank equality is required. The empty-spectrum/zero-space maximum is zero. The spectral maximum is attained on nonzero spaces.

The key new bridge, valid over any field, is

    mu_{t-a}(T) = dim_k ker(T-aI).

It composes Block 04's natural primary-to-global quotient equivalence with a new actual cokernel equivalence, the one-dimensional evaluation residue field, and rank-nullity. The exact kernel and action on representatives are proved. This proof does not construct or assume a Jordan normal form.

For nonzero spaces whose original field is algebraically closed, cyclicity and minpoly=charpoly are each proved equivalent to geometric multiplicity one at every spectral value. For any field, cyclicity is also proved equivalent to an actual polynomial-module presentation by k[t]/(minpoly(T)). The latter is not an executable invariant-factor algorithm.

These are classical results completed inside Paper I's actual definitions, not claims of new classical discoveries.

## What actually ran

| Check | Accepted result |
|---|---:|
| Predecessor manifested payloads authenticated | 1010 / 1010 |
| Preserved source/object pairs authenticated | 33 / 33 |
| New production modules freshly compiled | 4 / 4 |
| Complete source-owned declaration audit | 1475 / 1475 |
| Source-owned entries from the new modules | 61 |
| Public-or-coverage declaration names resolved | 259 |
| Complete same-kernel production-module replays | 37 / 37 |
| Additional boundary-module replay | 1 / 1 |
| New exact mathematical boundary assertions | 23 / 23 |
| Deliberately invalid controls rejected | 8 / 8 |
| Positive foreign-namespace control | 1 / 1 |
| Accepted expected-outcome commands | 69 / 69 |
| Final source/object identity checks | 37 / 37 |
| Exact dependency revisions checked | 9 / 9 |

**The 33 predecessor modules were not freshly rebuilt in the accepted run.** Their actual source and object bytes were authenticated against the unchanged predecessor receipts, copied to an isolated import directory, and all replayed through the official Lean kernel. The four new production modules were freshly compiled into a separate empty output directory. No development object was accepted in place of those new compilations. The 23 new boundary assertions were also freshly compiled and their module replayed. Earlier boundary suites are authenticated imports, not separately rerun test suites in this block.

The new source contains 27 public theorem declarations and 7 definitions. Three new modules contain mathematics and one is import-only. The full owned inventory includes generated helpers, private declarations, constructors, and other supporting entries. These are not counts of independent discoveries.

The only reported transitive axioms were `Classical.choice`, `Quot.sound`, `propext`. No production placeholder or additional custom axiom passed the source/ownership gates. Complete full public types, axioms, and source snapshots accompany the receipts.

## Tests

The literal X-action on C[t]/(t^2) has dimension two, is nonzero with square zero, has no Fin-2 eigenbasis, and has geometric multiplicity and seed maximum one. Two primary chains of lengths one and two have multiplicity and seed count two. The rational operator on Q[t]/((t^2+1)^2) has seed rank one but zero-dimensional eigenspaces for every rational scalar. This is an actual counterexample to dropping algebraic closure, not just a failed typeclass search.

Other assertions check zero spaces, quotient representatives, the exact scalar-image kernel, and the one-factor presentation. Negative controls reject a false equality, an authored placeholder, a missing algebraic-closure instance, a missing nonzero-space instance, the wrong Jordan multiplicity, surjectivity incorrectly used as injectivity, an imported custom axiom outside the project namespaces, and an imported placeholder compiled with warnings deliberately disabled. The clean foreign-namespace fixture passes.

## Failures and recoveries

The development index retains 11 compiler receipts: 6 rejected drafts/API probes and 5 zero-exit development runs. Rejected drafts included unknown API names, a quotient representative simplification, a beta-reduced maximum expression, a missing `map_one`, quotient coefficient inference, missing complex algebraic-closure import, dependent-index inference, and an overbroad extensionality tactic that hit a heartbeat limit. These were corrected before the accepted run. A separate foreground driver was interrupted by the tool timeout and did not produce an accepted object or command exit receipt. An unavailable streaming execution mode failed before command execution.

A supplemental archive-identity diagnostic initially compared paths with and without the enclosing archive directory and failed that path comparison. After normalizing the single root directory, all 1,011 predecessor files matched in name and bytes. No predecessor content changed.

An optional full predecessor rebuild was paused to serialize compiler work under the container memory limit and then deliberately cancelled after three successful source compilations. Its raw partial logs remain, explicitly marked CANCELLED_NOT_ACCEPTED. The accepted run instead uses the authenticated-predecessor strategy described above. The cancelled run is not counted as a complete rebuild or added to PASS totals.

## Publication coverage

All 108 stored statement, source-proof, and source-location/hash records remain unchanged. Exactly one proof-level record moves from partial to covered: `PSC-I-C-ALGEBRAICALLY-CLOSED-SINGLE-OPERATOR`.

Among the 69 proof-level records: **18 covered, 31 partial, 20 not mapped**. The 35-row formal contract and the expanded monograph use different inventories. These figures are not an overall completion percentage.

`PSC-I-C-CYCLIC-MATRIX` remains partial. The native algebraically closed geometric criterion and an actual one-factor module presentation are added, but the full scalar-extension clause from an arbitrary base field and the exact remaining six-way assembly are not silently marked complete.

## Trust, reproduction, and next restart

The combined `run_block05.sh` launcher was actually executed. The accepted run recorded 1743.239 seconds, excluding development, runtime recovery, and packaging. All detailed commands have observed outcomes, elapsed times, and hashed logs. The pinned Mathlib cache was reused, not rebuilt or fully replayed. Replay uses Lean's own kernel, not an independently implemented verifier. The correspondence between the manuscript and Lean types is a reviewed semantic artifact, not kernel interpretation of prose.

The mathematical constructions are noncomputable. There is no executable eigensolver, factorization routine, or canonical-form computation. Publication PDFs were not rebuilt. Prior license-status records are preserved without choosing a new license. The large pinned runtime remains an external prerequisite.

**Next restart:** the actual scalar-extension bridge for the six-way cyclic criterion, followed by its exact intrinsic-primary/rational-canonical assembly. Other recorded semisimple, module-top/Nakayama, packet/topological, and executable obligations remain. Papers II–XII have not been rerun in this sweep. See `CONTINUE_HERE.md`.

No audit or compiler process remains active at this handoff. `evidence/HANDOFF_POSTFLIGHT.json` records the process and final source/object checks.
