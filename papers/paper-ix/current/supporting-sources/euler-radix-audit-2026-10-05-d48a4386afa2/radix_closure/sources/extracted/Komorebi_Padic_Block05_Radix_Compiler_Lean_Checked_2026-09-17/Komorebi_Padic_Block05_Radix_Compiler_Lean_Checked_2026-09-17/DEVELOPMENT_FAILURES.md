# Development failures and repairs

All items below are preserved because a failed command is not evidence against
the mathematics unless it produces a valid counterexample.

## Lean proof repairs

1. The first root build placed a new import after the module documentation.
   Lean rejected the file. The import order was corrected.
2. The first digit-sum proof rewrote `Q = (Q-1)+1` too aggressively, including
   nested occurrences. `omega` then saw a malformed arithmetic goal. The proof
   was replaced by an explicit congruence for multiplication followed by a
   separate subtraction identity.
3. The first representative compiler proof attempted to unfold
   `barrierBranchCost` inside a hypothesis that contained only `ActiveAt`.
   Unfolding was restricted to the hypothesis where the definition actually
   occurred.
4. The reverse compiler implication tried to rewrite a named `barrierCarry`
   theorem after the target had already unfolded the definition. The target was
   first changed back to the named definition.
5. The first finite-minimum proof used the wrong rewrite orientation for the
   witness equality. The orientation was corrected.

## Concrete-vector expectation error

An initial smoke test asserted

```text
minRadixBarrierCost 2 0 5 = 8.
```

`native_decide` correctly rejected it. The exact value is `6`; the mistaken
expectation came from omitting the terminal partial radix block. The corrected
independent generator produced 72 passing concrete checks. No production
source theorem was changed to accommodate the bad expectation.

## Runtime and build failures

A clean warning-as-error rebuild traversed the full cached dependency graph and
exceeded the five-minute command cap. `lake clean` also removed the cached
mathlib build from that runtime copy. The exact five compact parts were
reassembled, hash-checked, and re-extracted to a fresh runtime. The subsequent
warning-as-error build completed successfully in 17.71 seconds.

## Predecessor replay timeout

The first aggregate replay driver entered the long Block 03 interval audit and
exceeded the aggregate cap. That run was treated as inconclusive. The quick
predecessor scripts were rerun individually and all passed. The long Block 03
result was not recomputed in the final replay; its retained result and source
hashes were validated by `Block03/verify_retained_results.py`.
