# v0.13 development and replay failure ledger

Failures are retained because a failed Lean invocation can indicate a mathematical error, a proof-engineering issue, or an execution issue. Only final warning-free compiler exits with code 0 support the checked statements.

## Centered probe development

Early drafts failed on simplification and bundled scalar-action normal forms. The theorem statements were unchanged. Final source passed.

## Trace-projector development

Early drafts used `LinearMap.id` where the endomorphism-ring identity `1` was required for multiplication simplification, followed by an unused simplifier warning. Both were repaired without changing theorem statements. Final source passed.

## Adequate/simple-packet detection development

Failures encountered:

1. invariant-kernel membership remained expressed through `Submodule.comap`;
2. a non-existent `Submodule.mem_iInf.mp` API was used;
3. an incorrect namespaced use of `Submodule.mem_bot` was used;
4. a restricted simp set did not reduce `g * g^-1` in the index action.

The final proof uses an explicit finite group-algebra Artinian argument to extract a simple submodule from a nonzero invariant kernel. Final source passed without assuming semisimplicity.

## Conjugation covariance development

The first draft had an associativity-normalization mismatch. A second draft supplied one extra explicit parameter to `LinearMap.trace_mul_comm`. Both were proof-engineering errors. Final source passed.

## Finite probe extraction development

The mathematical proof passed while warnings-as-errors rejected an unnecessary `simpa` and a proof-valued local instance style. Both were cleaned rather than suppressing linters. Final source passed.

## Finite projector extraction development

The first theorem statement left the `Set` type in `LinearIndepOn` underspecified. Making the quotient-dual type explicit resolved elaboration. Final source passed.

## Relative spectral detection development

The first draft attempted `SetLike.exists_of_lt` directly on `Representation.invtSubmodule`, whose carrier interface differs from an ordinary `Submodule`. The proof was moved to the underlying `k`-submodule. Later warnings concerned unused section variables and one invalid `omit` placement. The section was minimized instead of disabling the linter. Final source passed.

## Aggregate replay timeout

A single outer replay of all ten new modules completed the first four with RC=0, then hit the container's 300-second wall while beginning the fifth. This is classified as an execution timeout and is **not** counted as a successful aggregate replay.

The modules were subsequently replayed in smaller dependency-ordered batches. Every one has an observed `.rc` value of `0` in `verification/replay_logs/`.
