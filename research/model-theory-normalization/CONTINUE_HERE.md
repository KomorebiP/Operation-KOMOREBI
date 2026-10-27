# Continue from Model-Theory Normalization v0.10

Use this archive as the scalar-backend checkpoint and its history/v0.9 archive as
the immutable discovery-evaluator predecessor. Read NORMALIZED_CORE, COST_MODEL,
FORMALIZATION_COVERAGE, PROOF_AUDIT, RESULTS and DEVELOPMENT_FAILURES first.
Check FILE_MANIFEST before rewriting any execution records.

Current proof boundary: the nine scalar modules compile, and their correctness
and declared gate/cell bounds are universal. The discovery solver still reaches
this backend only in a separately tested Python port. Do not call the 203 port
runs kernel-checked whole-discovery executions. Do not multiply the v0.9 unit
bound by the scalar budget and announce a full runtime theorem.

Next substantive block:
1. Define a persistent binary-word arithmetic interface and a source instruction
   interpreter with explicit control, rather than re-encoding every scalar value.
2. Lower the actual v0.9 costed lattice/discovery recursion through that interface.
   Prove erasure/refinement for the value AND the arithmetic trace.
3. Prove widths for the precise trace, including signed correction, modular
   intermediates, literals, modulus and observation-row reconstruction.
4. Price conversions/data access in a declared memory model and compose the
   scalar bounds. Distinguish this from native Lean/compiler runtime.
5. Preserve old semantics, all-state/all-word scope, failure boundaries, true
   source binding, and the distinction between raw tests and minimum coordinates.

The runtime/cache is not included. Reuse the exact pinned portable environment.
The provided run_audit.py supports synchronous batches, stable input hashes,
version-2 manifests, and a fresh cold local build.
