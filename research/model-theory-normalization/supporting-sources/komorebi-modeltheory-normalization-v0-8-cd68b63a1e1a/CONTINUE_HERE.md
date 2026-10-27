# Continue from Model-Theory Normalization v0.8

Authoritative immediate predecessor: v0.7, SHA-256
31a72f98d0ea22df07a90d09b8fbc5db66b8552cd7afcf5a14718219e317866c.
This archive's checksum is provided beside the ZIP. Do not rewrite old checkpoints.

Read NORMALIZED_CORE.md, COST_MODEL.md, FORMALIZATION_COVERAGE.md, RESULTS.md,
DEVELOPMENT_FAILURES.md and PROOF_AUDIT.md first. Run distribution integrity before
replay, since replay replaces result files. Inspect the actual Lean statements.

Completed: bounded Euclidean coefficients and their high-level arithmetic peak;
exact replacement insertion with identical canonical result; full worklist peak
K=m[2m(m+1)]^d; power-of-two operand bound; <=2b Euclidean recursion steps;
203 actual kernel solver evaluations with unchanged tests and semantic endpoints.

NEXT: a costed evaluator whose value projection is proved equal to this solver,
then exact primitive-operation counts and a verified integer backend cost contract.
COST_MODEL.md is a WRITTEN polynomial analysis, not a formal runtime theorem. Keep
coefficient bounds distinct from proof checking, CPU internals, total allocations,
and the cost of reconstructing observation rows. The Python port caches source rows;
do not silently attribute that optimization to the current Lean evaluator.

Do not replace torsion with field rank; do not reduce against the wrong row pivot;
retain every coupled constraint. Do not infer all-precision mathematical discovery
or minimal formula/test count from these finite regression inputs.

A different useful route would formalize source-row caching and code extraction.
It must retain the same original state/operation/observation interface and checked
first-order semantics. Proof interpretation is self-review, not outside refereeing.
