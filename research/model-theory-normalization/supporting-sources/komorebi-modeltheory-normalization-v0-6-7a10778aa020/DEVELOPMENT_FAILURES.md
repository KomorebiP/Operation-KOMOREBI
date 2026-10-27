# Development and execution failures — v0.6

All failures below are distinct from successful accepted runs. Raw module diagnostics
are retained under v06_evidence/dev_*.log with command records.

1. The attempted interactive streaming interface was unavailable. A synchronous
runtime extraction then reached the tool wall-clock limit partway through unpacking.
The interrupted payload files were identified and removed, the remaining archive
was resumed with exact existing-file preservation, and required runtime, compiler
and pinned source hashes were verified. Runtime/cache bytes are not distributed.

2. Six incremental Lean module checks failed before correction: one EchelonCore
check (tail simplification/eta and strict simp warnings), one EchelonInsert check
(rewriting through the gcd coefficients), three EchelonModular checks (submodule
span API, Insert namespace collision and coercion/order of rewrites), and one
EchelonDiscovery check (making the invariant and sup inclusion types explicit).
The accepted proofs correct the elaboration, not the mathematical scope. No custom
axioms or placeholders were introduced to bypass the obligations.

3. After all 39 cold module builds succeeded, the combined axiom audit exceeded its
enclosing time limit repeatedly. Those invocations did not produce a complete
audit result and are not counted as passes. No process remains running from them.
The same 1,536 names were partitioned into eight smaller Lean files. The revision
is explicit in COLD_STATE.json: previous proof input hashes were retained and the
new audit-only source hashes were added. Completed groups are logged separately,
then their raw outputs are combined for the final name/axiom comparison.
The first grouped invocation was likewise interrupted by its enclosing call before
recording an outcome. Its complete retry and later groups have actual exit records.

4. Actual Python exhaustive tests produced no unexpected mathematical mismatch.
Invalid input, insufficient-fuel and deliberately false proof cases are intentional
negative controls and are not evidence of solver incompleteness.

Axiom collection groups and finite integer coefficient growth are operational issues;
neither supplies a new theorem or invalidates a theorem that compiled. The final
reports count only fully completed, checked expected outcomes. Further packaging
issues, if any, are to be appended rather than hidden.

5. An enclosing controls batch was interrupted after its first completed control.
The remaining controls resumed from the source- and artifact-hash-checked state.
Only their subsequently completed individual executions are retained as outcomes.
