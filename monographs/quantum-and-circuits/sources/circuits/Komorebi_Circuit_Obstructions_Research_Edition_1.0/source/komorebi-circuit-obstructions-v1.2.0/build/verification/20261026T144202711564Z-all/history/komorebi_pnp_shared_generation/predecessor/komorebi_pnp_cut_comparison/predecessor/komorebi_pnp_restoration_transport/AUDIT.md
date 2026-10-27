# Audit and execution boundaries

## Immutable predecessor

Archive: `Komorebi_PNP_Stable_Dirty_Metric_Block_2026-09-21.zip`.
SHA256: `9a27b285bb1970ddf9c2d77a8b6ea2ad84e41aa759a117ff487f10e2f8f451ad`.
The extracted source is preserved under `predecessor/`. There was no predecessor checksum manifest; we pinned the archive hash and compared the replayed scientific JSON with its retained output. We did NOT claim to validate a nonexistent predecessor seal.

The replay changes only the absolute JSON output path, avoiding writes outside this continuation. Its reported numbers match the saved predecessor result. The predecessor checks only target=0 in its source-circuit loop and admits repeated-control generalized Toffoli operations.

## Model defect found and repaired

The predecessor generates source AND/OR gates with repeated operands. It compiled these into TOF(a,a,t), violating the three-distinct-wire standard Toffoli model. Among the 630 seeded source circuits, 378 source gates had equal operands, producing 756 such occurrences including uncomputation.

Repair: AND(a,a)=OR(a,a)=a, so emit CNOT(a,t). The new validator rejects every repeated-wire gate. The corrected compiler was rerun on both initial target values, 11,760 scalar cases in total. The original theorem's upper constants remain valid because this replacement only shortens the circuit.

This was an implementation/model defect, not a counterexample to the written circuit equivalence.

## Inconclusive exploratory run

The first CLIQUE endpoint checker timed out under a 45-second call limit. Its generic maximum-clique search was unnecessarily expensive on large structured multipartite fixed graphs. The original script is preserved as `historical/verify_clique_endpoint_timeout_original.py`.

The replacement checks a genuine clique witness and proper coloring of the same size. These independently certify the clique number without an exponential search. Exact maximum-clique enumeration remains enabled through 16 vertices. No timeout was interpreted as UNSAT or as a lower bound.

## Review

Written proofs were self-reviewed against gate conventions, initial subspaces, count conventions, and the constant-factor transfer. In particular:

- The 2d-3 bound is output-passive, not an unrestricted lower bound.
- The unrestricted consequence is d-1, not 2d-3.
- The full-degree majority-clique family is NP-complete but the obtained bound is linear in edge-input length.
- The decoding-grade construction is an explicit reversible prefix inside an identity loop; it does not show that an optimal circuit needs such a prefix.
- All degree assertions concern F2 algebraic normal form.
- The number of graph vertices is not confused with the number of input bits.
- No claimed novelty, formal Lean verification, independent peer review, or P-versus-NP solution.
