# Local Lean status

The stored portable runtime was recovered and executed locally. It is not necessary to download a compiler from the internet.

- Lean: 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
- Lake: 5.0.0-src+6a10ac8.
- Mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
- Runtime assembly SHA-256: 66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34.
- Current local runtime directory: /mnt/data/lean_runtime/Komorebi_Portable_Lean_4.34.0-rc2.

Fresh runtime validation passed 16 checks: compiler and Lake startup, nine pinned dependency revisions, a kernel arithmetic proof, a cached Mathlib ring proof, the bundled nine-theorem Paper VI algebra module, rejection of a false statement, and rejection of a sorry placeholder. Exact commands, output and return codes are in verification/local_lean/runtime_validation.json. These are runtime checks; Paper VI in that test is the core-series algebra module, not Special Functions VI.

The initial full-Mathlib import test timed out and is documented separately. This failure is not hidden or counted as a pass.

The original discovery source, eight paper archives and registry contain no .lean files. Their scope notes pointed to a separate stored projector-calculus finite core, which has now been retrieved and included in lean/. Its 39 theorem declarations passed locally after narrowing the imports and replacing one unnecessary simpa with simp. All statements are unchanged. Its axiom audit contains no sorryAx or unexpected axioms. This is a checked supporting finite core, not a completed Lean formalization of the monograph's analytic results. Python assertions, mathematical prose and figures are not Lean proofs.

## Repeat the checks locally

The runtime is a separate approximately 11 GB Linux x86-64 toolchain/cache bundle, not included in this publication ZIP. Reuse it from storage. On Windows, run the Linux runtime inside WSL2. The Linux path was tested here; native Windows execution was not.

```bash
python tools/check_local_lean.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /tmp/special-functions-lean-checks.json
```

The checker replays the 16 runtime checks plus the recovered 39-theorem finite core. It uses only the stored runtime and caches, sets one worker, and avoids the full Mathlib import. It does not install packages or fetch dependencies. A source with a false theorem or a placeholder is deliberately expected to fail. Future Special Functions formalization must be tracked separately against the exact manuscript statements and hypotheses.
