# AVOC v0.10.0 — development failures and repairs

1. **First finite-union probability proof was overcomplicated and timed out.**  The initial proof decomposed `F \ E` manually.  It also exposed a membership-direction mistake.  It was replaced by the cleaner identity `sum_union_inter` plus nonnegativity of the intersection term.

2. **Direct checking of `VerifierEnsemble.lean` initially failed because the new imported modules had no project `.olean` files yet.**  `FiniteEvents` and `Specification` were built first, then the ensemble module compiled normally.

3. **The first verifier examples used `native_decide`.**  Although convenient, `#print axioms` then reported generated native-evaluation axioms.  These examples were rewritten using explicit finite sets, `simp`, `norm_num`, and ordinary Fintype product identities.  The final audit contains no such generated project axioms.

4. **A first coordinate-joint example attempted `native_decide` on `jointFailureEvent`, which is noncomputable.**  The repair proves the joint event extensionally as the singleton `{(true,true)}` and evaluates its probability directly.

5. **The first clean-build shell line scoped `PATH` only to `lake clean`, so the subsequent bounded `timeout ... lake build` could not find `lake`.**  The project had already been cleaned; the actual clean build then started with an exported toolchain `PATH`.  The failed shell invocation is not counted as build evidence.

6. **The combined post-clean audit/negative command hit the host execution cap after ten negative tests.**  The remaining two tests were rerun separately and rejected.  The final negative evidence therefore covers all twelve files.

7. **No product-of-verifier-errors theorem is stated without an explicit factorization hypothesis.**  The checked perfectly correlated example was retained specifically to prevent accidental promotion of marginal error rates to an independence claim.
