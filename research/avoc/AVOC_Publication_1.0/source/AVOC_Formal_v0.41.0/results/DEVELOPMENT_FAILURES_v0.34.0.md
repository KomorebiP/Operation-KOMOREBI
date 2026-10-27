# AVOC v0.34.0 — development failures and repairs

The following failures were preserved rather than hidden.

1. **New entrypoint omitted from the build graph.** `build_parallel.py` initially raised a `KeyError` for `AVOC.AffineTerminalCodec` because `AffineTerminalMain.lean` had not been added to `verify_release.py`.  The entrypoint was added, the graph was reindexed, and it was rebuilt from current imports.
2. **First concrete examples did not elaborate.** Initial proofs used definitional `rfl` for rational payoff normalization, referenced one theorem under the wrong name, attempted an overcomplicated rank proof, and triggered recursive simplification in action-membership goals.  They were replaced by explicit arithmetic normalization, the exact inherited rank theorem, action-membership iff lemmas and constructor contradictions.
3. **First adversarial tests failed for setup reasons.** Two new negative tests initially lacked opened namespaces or the `ZMod 5` prime instance.  They were repaired so the final failures are the intended impossible equalities `none = some ...`.
4. **Stale terminal-main record.** After adding batch mode, the runtime correctly rejected the old compiled record.  The build graph was updated and the final source was recompiled before execution evidence was regenerated.
5. **Unbatched catalogue construction exceeded the outer execution limit.** The first command constructed each world's normalization and certificate in a separate Lean process.  The cold output completed, but the subsequent warm output was truncated.  The coordinator was refactored to batch normalization, cold checking and warm checking through the same Lean codec, then both examples were rerun from scratch.
6. **Clean build slices hit the host limit.** Two bounded parallel-build calls were interrupted.  No Lean child remained; the build resumed at the unfinished graph nodes until all 188 targets had current successful records.
7. **The first two negative-test runs hit the host limit.** Completed records were retained, and execution resumed at the first unfinished index in bounded groups.  Timeouts and setup failures were not counted as mathematical rejections.
8. **The first release summarizer was too strict.** It rejected an inherited deliberate negative whose intended failure includes typeclass synthesis.  The collector was aligned with earlier audit policy: it excludes import/setup failures but permits substantive elaboration/typeclass failures in deliberately invalid files.  The collector was rerun successfully.

No admitted proof placeholder, custom axiom or native-evaluation shortcut was used to repair these failures.
