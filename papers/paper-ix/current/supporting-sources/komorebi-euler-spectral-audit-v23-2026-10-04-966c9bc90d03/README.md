# Komorebi Euler Spectral Audit — v23

This continuation preserves v22 and adds four Lean modules. It proves finite
spectral detection for the ACTUAL infinite depleted Euler packet series. It
also records a proved synthetic counterexample to an overstrong undepletion
simplicity inference. No new Euler family is declared solved.

Start with `PROOF_AND_STATUS.md`. Machine-readable status is in
`RELEASE_STATUS.json`; proof names are in `THEOREM_INDEX.json`.

## Verify the download

From this directory, using Python 3.10 or newer:

```bash
python scripts/verify_manifest.py
```

This checks file integrity only; it is not a proof checker.

## Replay Lean

The release uses the existing portable Linux runtime with Lean 4.34.0-rc2 and
mathlib revision aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The large runtime and
its dependency caches are not bundled. Pass the actual restored runtime path:

```bash
python scripts/replay.py \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --evidence /path/to/NEW-v23-replay-directory \
  --timeout 120
```

Use a new evidence directory for every replay. The script refuses to overwrite an
existing directory, compiles the full project, and prints/audits the transitive
axioms of every indexed theorem and lemma. It does not rebuild mathlib.
The inherited Lake package version string is not the continuation version; this
release is identified by its directory, documentation, and hash manifest.

## Run the exact-arithmetic checks

```bash
python checks/check_spectral.py
```

This standard-library-only audit writes `evidence/spectral_exact_checks.json`.
Run it from a fresh copy to preserve the original receipt. It uses exact integers
and fractions, not floating p-adic approximations. The finite checks do not supply
the universal quantifiers of the Lean theorems.

## New source

- `Euler/UndepletionAlgebra.lean`: rational coefficient identities and remainders.
- `Euler/SpectralSeparation.lean`: classical finite Vandermonde observation.
- `Euler/CriticalPerturbationJets.lean`: moving critical values and negative controls.
- `Euler/DepletedSpectralEscape.lean`: actual infinite sums and finite spectral escape.

## Essential interpretation

The depleted series and the undepleted Euler residual are different objects.
A nonzero correction at a fixed point does not by itself prevent a moving double
root. The release proves a counterexample using the same resolvent weights.
A valid simplicity application must locate the actual perturbed critical point
and prove a strict error margin for its critical value.

Historical input is preserved as an unchanged ZIP. Current runtime files,
compiled caches, and font files are intentionally absent from this distribution.
The logs contain paths used during execution; those paths are provenance, not
portable installation requirements.
