# Reproduction contract

## Requirements

Quick checks: Python 3.10+ and its standard library. Full active checks: additionally a C++17 compiler (default `g++`, selected with `CXX`). No pip packages, SAT solver, Lean installation, network access, or hidden dataset are required. The original-history runner is supported here on Linux/WSL and uses its preserved original commands. We do not claim to have tested the hosted CI or native Windows full replay in this session.

## Commands

From the repository root:

```sh
python scripts/verify.py --quick
python scripts/verify.py --full
python scripts/verify.py --history
python scripts/verify.py --all
python scripts/check_integrity.py
```

Quick runs independent controls and all small restored constructions. Full includes quick, rebuilds the C++ profile table for 1–4 inputs, and executes the three maintained scientific checkers. History unpacks the pinned Complete Packets and Projection source into a new build directory, checks its seal, executes its full documented runner, and compares its seven scientific outputs. All combines full and history.

The core modules are internal research code, not a promised stable library API. Use the checked runner; direct module execution is not the release entry point.

## Outputs and immutability

Every invocation creates a fresh `build/verification/<timestamp>-<mode>/` directory with logs, scientific results where applicable, and a version-2 computation manifest. The manifest records the command, runtime, environment, input hashes before/after execution, result hashes, and per-command wall limits. Inputs and baseline evidence are not rewritten. Work files and generated binaries remain ignored by Git.

Python assertions are part of the checking implementation. Optimized Python is rejected. A failed subprocess, absent result, mismatched baseline, mutated input, or timeout makes the runner fail. There are no silent skips when a requested compiler or checker is absent.

Wall timeouts are enforced. No additional OS memory or CPU caps are installed by the runner. The full small-case domains and the fixed seed 20260921 are inherited from the baseline. Runtime is not interpreted as a performance benchmark.

## Evidence is layered

`evidence/baseline/` records frozen scientific results from the source checkpoint. `evidence/closure/` records the release-session replay. The full runner compares JSON structures exactly and profile binaries by SHA-256. A repeat need not reproduce timestamps, machine-specific logs, executable bytes, or elapsed time. It must reproduce the mathematical result files.

The artifact seal checks bytes, not mathematical truth. The complete-profile table is exhaustive only in its declared small domain. Rank controls at four inputs are the specified 765 cases; larger projection cases check symbolic coefficients and exact rank, not full truth tables. See the manuscript and JSON result scopes for every distinction.

## Validate a run record

The runner validates its manifest automatically. A recorded path printed by the runner can also be checked with:

```sh
python scripts/validate_manifest.py build/verification/RUN_ID/manifest.json --root .
```

Replace `RUN_ID` with the actual emitted directory name. Results under `build/` are deliberately not committed. The release audit summarizes the runs used for this snapshot and preserves their independent source pin.
