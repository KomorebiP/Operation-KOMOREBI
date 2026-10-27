# Komorebi H12: Norm Projector and Lean Core v0.1.0

Read PROOF.md and FORMALIZATION_SCOPE.md first. The mathematical advance is an exact norm-action projector with a nontrivial lost component, plus its recovery through signed half-period products. The 50 Lean lemmas formalize the exact algebraic and finite-support core, not the unproved gamma-to-algebraic comparison.

## Run

Use the previously restored portable Linux/WSL x86-64 kit `Komorebi_Portable_Lean_4.34.0-rc2`. Its compiler and Mathlib are pinned; the runtime is intentionally not duplicated in this small source package.

```sh
python -m pip install -r requirements.txt
python checks/validate_manifest.py evidence/manifest.json --root .
python checks/run_all.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --part core
python checks/run_all.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --part high
```

Run the manifest validator before reproduction: reproduction overwrites runtime-bearing evidence files, so their new hashes differ from the shipped manifest.

Only Lean:

```sh
python checks/run_lean.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The runner obtains the pinned Lake environment, then invokes Lean directly with one worker and warnings as errors. It compiles copied sources in a fresh directory, audits all theorem axioms, and rejects a false-statement control. No network is needed once Python dependencies and the portable kit are available.

The inherited version-one manifest validator checks metadata structure and file hashes, not mathematical truth. Exact proof scope and numerical non-claims are specified in the notes.
