# Continue K-COS end-to-end work

Use this checkpoint's `lean/` tree and `verification/accepted/run.json`. Do not restart from the 26-theorem publication companion or overwrite the frozen monograph.

Read `docs/PROGRESS_LEDGER.md`, `docs/END_TO_END_TARGET.md`, and `docs/COVERAGE.json` first. The new central Gaussian, matrix/spectral, stochastic-coupling, and rational-acceptance links are present. The final composition theorem still requires valid numerical spectral bounds and endpoint probability bounds.

The next module is `KomorebiQCOS/TiltedMeasure.lean`: define the actual exponential tilt from a density, prove normalization, and derive the change-of-measure identity. Do not assume that identity or treat a preexisting numerical Boolean as a theorem.

Use the stored exact-pin Lean runtime. `docs/RUNTIME_RECOVERY.md` identifies the five archive parts and the verified combined hash. `python verify.py --runtime PATH` runs an isolated verification without replacing accepted evidence.
