# Block 39 failure ledger

## Rejected or repaired attempts

1. **Direct identification with ordinary dyadic boxes.** The checked predecessor supplies a measure-preserving decoder but no almost-everywhere inverse. A pointwise or unitary-equivalence claim would therefore overreach. The block instead uses the Hilbert adjoint of the isometric pullback.

2. **Recursive simplification of projection membership.** An initial `simpa [Submodule.starProjection_apply]` reached Lean's maximum recursion depth. The final proof changes the goal to the subtype returned by `orthogonalProjectionOnto` and uses its membership field directly.

3. **Top-level warning-as-error check before restoring root object files.** The first attempt failed because `MovingFrames.olean` was absent from the restored cache. This was an environment/build-order failure, not a Block 39 theorem failure. The missing root libraries were rebuilt before the accepted verification run.

4. **Long cumulative build attempt.** An interactive top-level build exceeded the command-interface window after substantial progress. It was not counted. The build was resumed under a detached process to a terminal receipt.
