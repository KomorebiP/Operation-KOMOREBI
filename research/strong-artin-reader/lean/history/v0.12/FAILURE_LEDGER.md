# v0.12 development failure ledger

Failures are retained separately from successful proof evidence.

1. **First compile:** warnings-as-errors rejected one unnecessary `simpa`. Mathematical declarations otherwise elaborated and emitted ordinary axiom reports. Fixed by replacing it with `simp`; no theorem statement changed.
2. **Cokernel-equivalence draft:** two Lean API mismatches occurred: `mkQ` needed an explicit rewrite to `Quotient.mk`, and `range (0)` was propositionally rather than definitionally `⊥`. Both were repaired with exact quotient/range equivalences; no mathematical hypothesis changed.
3. **Finite-rank corollary draft:** direct simplification of the zero-range quotient made no progress. Replaced by the already-proved explicit linear equivalence to the cyclic output. No statement changed.
4. **Obstruction-class draft:** one equality was reversed (`q = -Ju` versus `-Ju = q`). Fixed by symmetry. No theorem statement changed.

No failed development compile is counted as proof. The release verifier is the positive evidence.

5. **Probe module first compile:** warnings-as-errors reported an automatically included but unused `Fintype ι` assumption. The proof did not require finiteness, so the assumption was removed, strengthening rather than weakening the theorem.
6. **Combined capstone first compile:** module import failed because direct Lean invocation did not include the workspace directory in `LEAN_PATH`. The prerequisite modules were then compiled to `.olean`, and the unchanged capstone source passed with the correct search path.
7. **Aggregate six-module verifier wrapper:** the outer execution tool hit its wall-clock limit before recording an exit code. The log itself reached `PASS`, but this run is not used as the release certificate because the wrapper did not capture a return code. A smaller additive verifier is supplied and used instead.
