# K-COS end-to-end verification — development checkpoint 0.1.0

A formal development branch from **The K-COS Method, official release 1.0.0**. The official monograph is unchanged. This is a checked intermediate step toward end-to-end verification, **not** a claim that the full numerical implementation is verified.

## Start here

Read `VERIFICATION_REPORT.md`, then `docs/END_TO_END_TARGET.md`. `docs/PROGRESS_LEDGER.md` gives the precise restart point, and `docs/COVERAGE.json` separates closed scoped results from open obligations. The exact declaration inventory is `docs/DECLARATIONS.json`.

The source contains the original finite Gram/enclosure modules and six new mathematical modules. The new development connects actual Gaussian measures and spectral reductions to stochastic tail bounds and an exact rational acceptance decision. Numerical spectral inclusion and COS endpoint enclosures remain explicit premises of the final composition theorem.

## Offline verification

With the pinned portable runtime already extracted:

```sh
python verify.py --runtime /absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
```

The runner uses a new temporary project, verifies the compiler and nine dependency revisions, attaches the existing cache without updating it, builds with warnings treated as errors, audits all explicit declarations, replays the project modules in the Lean kernel, and executes positive and rejection controls. It writes a new `verification/local_replay/` directory. It refuses to overwrite an existing nonempty output. Use `--output /another/new/directory` for another replay.

No network access, `lake update`, or compiler patch is needed. The runtime and Mathlib cache are intentionally not duplicated in this ZIP. Recovery details are in `docs/RUNTIME_RECOVERY.md`. The supplied script has a per-command timeout of 900 seconds, configurable with `--timeout`.

To check the packaged bytes before rebuilding:

```sh
python verify_manifest.py
```

Regenerated files can have different bytes. Preserve the delivered archive and evidence, and work in a copy.

## Source map

| Module | Purpose |
|---|---|
| `FiniteGram` | Original exact finite Gram, streamed-action, and coefficient-order algebra |
| `Certificates` | Original arithmetic consequences of valid supplied enclosures |
| `TailProbability` | Actual measure-valued events and real tail probabilities, measurability, coupling |
| `Acceptance` | Multiplicative accuracy and exact rational acceptance checker |
| `GaussianTail` | Actual independent Gaussian coordinate law and spectral-tail interface |
| `SpectralGaussian` | Exact self-adjoint Gaussian spectral reduction |
| `CentralLinearImage` | Central linear Gaussian images, including singular maps |
| `MatrixGaussian` | Original finite Gram representation connected to the spectral law and accuracy theorem |

`Controls/Positive.lean` includes boundary, zero-rank, signed-coefficient, and counterexample checks. `Controls/RecordedTilted.lean` checks four exact rational acceptance decisions for retained tilted-functional intervals, not the entire numerical enclosures. The five `Reject*.lean` files are deliberately invalid and must fail. They are never imported by the production root.

## Trust and coverage

Lean and the pinned imported Mathlib environments are the formal trust base. Project-only kernel replay uses the same Lean kernel; it is not an independent verifier or a replay of the entire Mathlib dependency closure. No admission, custom axiom, or native-decision axiom is accepted in the production audit.

The Python engine's regression suite is not rerun by this branch. The official publication's numerical evidence remains historical evidence. The extra rational controls check the inequalities written in their Lean source, not the JSON parser, transcendentals, or analytical correctness of the archived interval data.

Exact input decoding, floating computation, interval construction, spectral numerical inclusion, noncentral reduction, and COS analysis remain separate obligations. See the target document before making any end-to-end claim.
