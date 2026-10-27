# AVOC Formal v0.27.0 — globally optimal, checked reusable libraries

This cumulative source release extends the **semantic-feedback v0.26 branch**. It does not merge the alternate rewrite-transfer branch that previously shared the version number.

## New result

A finite table with (1) realized semantic/cost witnesses and (2) lower-bound inequalities for every constructor certifies minimum AST node counts over **all finite expression heights**. Structural induction connects the finite checker to that unbounded-height claim. The fixed executable instance uses three Boolean inputs, literals, variables, not, and, or, and xor.

The actual Lean importer validates a saved 256-entry certificate. Every funded query returns an equivalent globally minimum-node expression. Reloads recheck the certificate rather than trust an old success flag or generation depth. Validation and queries carry explicit per-call tariffs; these are not physical costs or a durable payment ledger.

## Deliverables

- `AVOC/SemanticCostCertificate.lean`: generic semantic-algebra lower bound and attained global minimum.
- `AVOC/BooleanCostClosure.lean`: exhaustive closure checker, checked bank, globally optimal queries.
- `AVOC/SemanticLibrary.lean`: funded import/query, accounting, limited stopping bound.
- `AVOC/SemanticLibraryCodec.lean`: data parser and checked-import correspondence.
- `tools/global_library.py`: validate, publish a new snapshot, and freshly validate/query a saved bank.
- `examples/library/global.json`: concrete certificate; 256 behaviors, cost sum 1,640, maximum cost 10.
- `THEOREM_INDEX.md`, `AUDIT.json`, `PROOF_BOUNDARY.md`, `REPRODUCE.md`, and versioned results.

## Verification distinction

54 new declarations; 1,447 total including helper lemmas and examples. All 150 current local compilation targets and the 1,447-name axiom audit pass against pinned external caches. The actual executed checker accepts the concrete certificate. An optional attempt to reduce the entire concrete table to a standalone kernel proof timed out after 30 seconds and is **not** counted as successful. No native-evaluation axiom was used to bypass that limit.

The reference source theorem and executed-checker/data validation are separate evidence layers. The compiler/runtime, standard parser, protected host, Python and filesystem remain trusted.

Read `REPRODUCE.md` to run; read `PROOF_BOUNDARY.md` before extending the claims. The source package excludes runtimes and `.lake` caches. Historical records remain historical, not fresh v0.27 tests.
