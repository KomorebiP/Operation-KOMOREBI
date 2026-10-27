# Beal formal development failures and corrections

The failed commands remain failed evidence. They are not included in any pass
count. A compiler failure caused by a missing dependency or wrapper path is not
a mathematical counterexample.

1. The first attempt to compile the unchanged Block 47 and 48 sources under the
   available Lean 4.19 and mathlib 4.19 cache failed at the first import. The
   historical sources require `Mathlib.Data.Set.Lattice.Bounded`, a module absent
   in that older library. The source snapshot and log are in
   `historical_compatibility_attempt01`. The separately recorded version 2 run in
   `compatibility_failure_run` reproduces that failure. It is explicitly a
   compatibility attempt, not an exact replay of the original pins.

2. The first new `BealAffine` source used the quotient lemma
   `Submodule.Quotient.mk_eq_zero` without its required submodule argument. Lean
   rejected that proof. Its temporary axiom print included `sorryAx` for the
   declaration whose elaboration failed. That is an unsuccessful development
   output, not a passed certificate. The exact failed source is preserved in
   `development_sources/BealAffine_attempt01.lean`, together with
   `BealAffine_development_attempt01.log`. Supplying `LinearMap.range A` as the
   explicit argument repaired the API use. The corrected source's second direct
   warning-as-error elaboration passed all eleven axiom reports.

3. The first version 2 affine wrapper completed strict source compilation but
   then tried to launch an extra `leanchecker` executable. The official Lean
   4.19 distribution in this workspace has no such executable. The wrapper
   failed with `FileNotFoundError`. `affine_formal_run` preserves the traceback
   and successful source-compile log. No independent checker replay is claimed
   for the new module. Lean's ordinary elaboration kernel checks the generated
   proofs, using the pinned imported library objects.

4. The first exact historical replay laid out mathlib as the runtime workspace
   itself. The unchanged Block 47 verifier expects mathlib under the workspace's
   `.lake/packages/mathlib`. That path mismatch stopped its metadata check.
   Block 48 separately passed its eight strict source and axiom checks during
   that same run. `historical_exact_run` preserves the failed overall result.
   A private Lake-style workspace with links to the freshly pinned checkout and
   dependencies repairs the layout without changing historical source bytes,
   compiler bytes or the original Block 47 verifier.

5. The second affine provenance wrapper used the broad `import Mathlib` under
   one CPU affinity core. Its strict compilation hit the wrapper's 120-second
   timeout. `affine_formal_run02` preserves that resource failure. A separate
   `BealAffineChecked.lean` copy tried four narrower imports. Every definition,
   theorem, proof and axiom target below the imports is byte-identical.
   `AFFINE_IMPORT_PATCH.json` records that intermediate change.

6. The four-import attempt omitted the linear-map range and kernel library.
   Lean rejected the unresolved `LinearMap.range` and `LinearMap.ker` constants.
   `affine_formal_run03` preserves that dependency error. The final separate
   `BealAffineReader.lean` imports the required
   `Mathlib.Algebra.Module.Submodule.Range` as well. Its five-import change is
   recorded in `AFFINE_READER_IMPORT_PATCH.json`. The final bounded run uses
   two affinity cores and a 180-second subprocess limit, with Lean's worker
   count set to one. All eleven proofs and their statements remain unchanged.

The recovered historical Block 48 logs also retain its original missing-private-
cache and thread-creation failures. Those records predate this publication and
are preserved unchanged as history.
