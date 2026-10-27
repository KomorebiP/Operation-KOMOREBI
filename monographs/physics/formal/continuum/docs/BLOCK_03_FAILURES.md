# Block 03 — failures, repairs and evidence boundaries

No failed invocation or incomplete run is counted as a checked theorem. The cumulative production proof audit is `verification/final/report.json`.

## Runtime and baseline

The runtime was restored from the seven archived Lean_Offline parts using the existing checked assembler. Chunk hashes and the combined Zstandard archive hash were verified. A request for a streaming container execution session failed because that execution mode was unavailable; ordinary commands and supervised processes with log files were used instead. This was a tool-interface failure, not a mathematical result.

The first cumulative Block 02 baseline attempt was interrupted by the outer tool execution deadline. Its report remains incomplete in `verification/block03_baseline_interrupted/`. It is not credited as a successful baseline. The retry completed all ten prior mathematical modules, 160 named-declaration audits and all nine old negative controls; its raw report and logs are in `verification/block03_baseline_retry/`.

## Development failures

Retained per-invocation source snapshots, compiler outputs and receipts are under `verification/development/block03/`; the index is `verification/block03_development_index.json`. Some API probes deliberately queried candidate names that do not exist in the pinned Mathlib. They are not active mathematical modules.

The development failures included an unavailable matrix-notation import path, inaccessible/unexposed definitions when unfolding the recovered coarse implementation, matrix/function reducibility and namespace mismatches, finite-sum ordering, and partially discharged proof obligations. These were fixed by using the actual pinned API, explicit operator/sum identities, `Matrix.of` or an explicit `change`, and `import all TensorRefinement` when its definition needed to be unfolded.

An attempt to use `simp_rw` indiscriminately with current antisymmetry looped and hit the recursion bound. It was replaced by a finite-sum congruence and explicit interchange of indices, rather than treating a larger recursion budget as a proof.

Concrete matrix derivative construction initially lacked the correct norm interface. The proof now imports `Mathlib.Analysis.Matrix.Normed`, opens `Matrix.Norms.Elementwise`, and uses explicit real-time derivative composition. A concrete positive-factorization proof initially left complex conjugation of numeral 2 unresolved; an explicit ring-hom numeral identity completed the exact arithmetic. Function-addition and bare-definition unfolding were made explicit in the affine-curve and source-derivative witnesses. Style-linter failures from unnecessary local instance syntax were repaired rather than ignored.

Every active new mathematical module now compiles with warnings as errors. No repair uses an admission, custom axiom, native-evaluation escape, weakened intended conclusion, assumed energy/current balance in place of differentiation, or a false claim of global validity for the local affine example.

## Deliberately false alternatives

The six new controls are expected to fail: wrong mixed current sign, removal of the trace conjugation, missing density Hermiticity, missing Hamiltonian Hermiticity, binary overlap without a partition, and deletion of source terms. Their rejected proof obligations are evidence that those false alternatives are not accepted. They are not unresolved proof gaps in the valid statements.

The ten prior source files are byte-for-byte unchanged. All final axiom dependencies remain among `propext`, `Classical.choice` and `Quot.sound`. Imported Lean/Mathlib libraries were used at the exact clean pins, not rebuilt wholesale. A complete rerun from the extracted release is reported separately by the archive-recheck receipt.
