# Komorebi Euler Cubic Critical v25

Kernel-checked cubic inflection and critical-value continuation, 4 October 2026.
923 theorem/lemma declarations in 104 mathematical Lean modules. The eight new
modules add 45 declarations; all 96 v24 modules are unchanged.

## Main result

For the actual restricted series

    F = a + b X + c X² + u X³ + 4 X⁴ R,  u a dyadic unit,

there is a uniquely constructed inflection point rho. Set A=F'(rho), C=F(rho).
The strict norm mismatch |C|² != |A|³/4 excludes every critical zero on the disc.
For any two critical points x,y, |F(y)-F(x)|=2|y-x|³. Thus the core has at most one
critical zero. A finite value/slope/curvature test supplies a certifiable version.
The permitted class is derived from the existing actual two-neighbor Euler core.

This is not a universal Euler simplicity theorem. Equality in the test is
inconclusive, and exact synthetic double-root controls are retained.
See PROOF_AND_STATUS.md for the precise theorems and numerical boundaries.

## Replay

The existing pinned portable runtime is not bundled. Given its root directory:

```sh
python3 scripts/verify_manifest.py
python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --evidence /new/path/v25_replay --build-dir /new/path/v25_build
```

The replay refuses existing output directories. It checks compiler/mathlib pins,
rebuilds every project module, and audits all transitive proof axioms. It reuses
cached dependencies; it does not rebuild Lean or mathlib. With a separately
configured matching Lake project, omit `--runtime`.

## New computations

Python 3.10+ standard library only. Run from the project root; choose fresh files:

```sh
python3 checks/check_cubic_critical.py --output /new/path/generic.json
python3 checks/check_cubic_critical.py --actual 3 --precision 224 --output /new/path/v25_actual_3.json
# Repeat the preceding command for B=7,11,15, keeping the same record directory.
python3 checks/check_cubic_reconstruction.py --records /new/path \
  --output /new/path/alternative.json
python3 checks/check_cubic_trial_certificate.py --records /new/path \
  --output /new/path/trial.json
```

Each actual record uses a freshly reconstructed original index B*2^640-161.
The alternative algorithm uses 256 bits, a logarithmic source, rising factorials,
and a different translation algorithm. The Bernoulli evaluator and polynomial
multiplication are shared; no stronger independence claim is made.

Generic computations are labelled synthetic. Zero modular residues are only
precision bounds. Four actual integers do not classify an infinite family.

## Evidence

- evidence/v25_incoming_replay: fresh v24 baseline.
- evidence/v25_replay_A and v25_replay_B: two full clean v25 builds and audits.
- evidence/v25_replay_comparison.json: identical source/axiom/106-olean checks.
- evidence/v25_generic.json: 25,826 finite corroborating checks.
- evidence/v25_actual_*.json: four actual-index coefficient records.
- evidence/v25_alternative.json: 1,528 alternative reconstruction comparisons.
- evidence/v25_trial_certificate.json: finite three-jet tests at Y=6.
- history/: frozen v24 input and metadata; older evidence keeps its own version.

The complete transitive axiom union is Classical.choice, Quot.sound, propext.
No custom mathematical axioms, unfinished proofs, or native evaluation proof
axioms occur. No historical-priority assessment was performed.
