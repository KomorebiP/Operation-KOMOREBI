# AVOC v0.38.0 — development failures and corrections

The following failures were retained because they materially affect the interpretation of the release.

## 1. Sparse draft workspace

The preserved v0.38 directory initially contained only five draft modules.  The full project was reconstructed by extracting the authoritative v0.37 archive and then overlaying the drafts byte-for-byte.  The sparse directory was not treated as a complete prior release.

## 2. Offline runtime extraction failure

The first restored portable environment had a usable Lean executable but incomplete workspace/cache payload.  The missing pinned payload was reassembled from the preserved runtime parts.  One truncated runtime archive object was rebuilt from the exact pinned dependency source.  Environment damage was not interpreted as an AVOC proof failure.

## 3. Inherited negative-wrapper defect

The inherited negative wrapper invoked bare Lean without the project module path in one execution route.  Its first error could therefore be `unknown module prefix AVOC`, which is not mathematical evidence.

The v0.38 suite uses the project environment and rejects setup failures as inconclusive.  `FalseFreeRankProbe.lean` and `FalseProposalPromotion.lean`, previously timed out under CPU contention, were rerun sequentially and rejected substantively.

## 4. Invalid direct probability-endpoint argument

A proposed proof route attempted to substitute interval endpoints directly into Bellman expectations.  That is not valid without the required monotonicity of the continuation-value difference.

The corrected construction is:

```text
quote widths
  -> reward and binary observation-law errors
  -> inherited finite-horizon value/Q transport
  -> robust lower-Q selection.
```

## 5. Concrete evaluator reductions were too large

Several initial example proofs attempted large direct kernel reductions of complete finite-horizon evaluators.  They were impractical in the pinned environment.

The examples were refactored into small exact lemmas for interval widths, reward/probability radii, local Q radii, and numerical ordering.  Universal selector and dominance statements remain generic kernel-checked theorems; executable choices are independently cross-checked.

No `native_decide` or compiler-trust axiom was introduced as a workaround.

## 6. Runtime transition was initially noncomputable only

The formal artifact installation path was first exposed only through a noncomputable definition.  That was insufficient for the required JSON runtime.

A finite executable implementation was added:

- `reportPossibleCheck`;
- `supportedCheck`;
- `installExec`;
- `confirmExec`.

Lean proves `confirmExec_eq_confirm`.

## 7. First independent regression exceeded the outer limit

The first regression launched too many individual Lean processes and exceeded the host's outer execution limit.  That run was discarded as inconclusive.

The final regression batches requests through one Lean entrypoint and independently checks the responses with exact Python `Fraction` dynamic programming.  It completed 21 plan comparisons and 1,523 compatible-realization checks.

## 8. Negative-test fixture repairs

`FalseArtifactOutsideQuoteAccepted.lean` initially failed for an unrelated missing namespace/open declaration.  It was corrected so that it imports successfully and reaches the intended impossible interval-membership claim.

`FalseDuplicateAckChargesAgain.lean` initially used an unnecessarily complex optional-value extraction.  It was replaced by an explicit valid artifact/checkpoint construction.  The final file fails at the intended duplicate-charge equality.

## 9. Workflow batching timeout

A combined normal-workflow and recovery regression exceeded the outer command limit after the normal cases completed.  The recovery case was rerun independently and completed in approximately 15 seconds.  Only completed records are included.

## 10. Clean-build interruptions

Several dependency-aware build calls exceeded the host's outer command limit while active Lean children were running.  The children were checked, unfinished targets were rerun, and no interrupted target was counted.

The final direct local build records 205/205 current source/import/output hashes.

## 11. Redundant Lake frontend interruptions

After the complete direct build, redundant `lake build` frontend runs repeatedly hit the long-command cap while rebuilding cached targets.  They were not treated as successful aggregate evidence.  Those invocations changed some local object files, so the complete 205-target direct build was rerun afterward and all records were revalidated.

## 12. Controlled recovery scope

The recovery test uses a controlled Python interpreter exit after SQLite commit and before acknowledgement.  It is not a power-loss test.  The release therefore claims idempotent protocol recovery under the tested protected-store boundary, not universal physical durability.
