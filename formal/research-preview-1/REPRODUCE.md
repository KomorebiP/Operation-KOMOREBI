# Reproducing the release candidate

A source hash, a finite experiment, and a Lean proof replay answer different questions. This package keeps those results separate. None is a substitute for the others.

## 1. Check the downloaded package

From the repository root, using Python 3.10 or later:

```bash
python -B tools/check_release.py
```

This checks the sealed file hashes, preserved Block 34 source identity, local imports, public claim anchors, document links, and the coverage of retained axiom logs. It does not run Lean, inspect all historical receipts, or establish independent proof review. For a tree being edited before sealing, `--unsealed` allows the whole-package hash ledger to be absent, but still checks the frozen source identity.

## 2. Run the standard-library demonstration

```bash
python -B demo.py
```

The default performs 96 scalar coefficient comparisons: 32 coefficients for each of three masks. `--count 256` exercises 768 comparisons. `--output PATH` writes a new optional JSON receipt. The example compares direct Mahler recurrence with the included sufficient finite Cartier machine, not the minimal-realization implementation. It never overwrites retained evidence unless explicitly given such a path; use a new results path.

The preparation environment used Python 3.13.5. The demonstration and wrapper scripts require Python 3.10 or later; cross-platform execution is not claimed solely from compatible syntax.

## 3. Run the larger exact reference audit

Use an isolated Python environment and the included reference dependency pin:

```bash
python -m pip install -r padic/requirements-reference.txt
python -B padic/verification/audit_residual.py
```

The pin is SymPy 1.14.0. The audit writes `padic/results/audit_residual.json`; historical evidence is separately stored under `padic/evidence/`. It tests 90 generic realization pairs and 16 mask cases in its finite ranges. This is not a formal executable refinement or an unbounded theorem. The dependency installation command was not run in this preparation environment, where the pinned SymPy was already installed.

## 4. Obtain the exact public Lean environment

Install Git and Elan using the [official Lean installation instructions](https://lean-lang.org/install/manual/), including the platform-specific Windows instructions where applicable. Elan chooses the version named by a project's `lean-toolchain` file. Do not replace this project's pin with `stable`, and do not update the dependency manifest to a new revision merely to make a build pass.

The pinned values are:

```text
Lean:    leanprover/lean4:v4.34.0-rc2
Commit:  6a10ac8c22beadecabdbb0919c2b50214762f91d
mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06
```

From `padic/`, the standard existing-project cache command is:

```bash
lake exe cache get
```

It obtains compatible dependency artifacts when available. The source dependency revisions are locked in `lake-manifest.json`. A missing cache is not a counterexample to a theorem; any fallback source build must still use the exact revisions. Confirm the pins again after dependency setup. The replay harness checks each checkout's `HEAD` against the manifest.

The official release page and the pinned mathlib toolchain file were located during initial preparation. The subsequent launch-reproduction pass restored the exact retained runtime and completed a clean project proof build. Direct network retrieval still failed with a DNS-resolution error. **A successful fresh public bootstrap is not claimed.** See the [reproduction checkpoint](github/REPRODUCTION_STATUS.md) for the completed local run and remaining hosted gate.

## 5. Replay the proof and controls

Once the pinned tools and dependency checkouts are available, run from the repository root:

```bash
python -B tools/replay_lean.py --clean
```

The same Python command can be used in a Unix shell or PowerShell. It does not install or upgrade anything. `--clean` removes only `padic/.lake/build`, leaving dependency caches intact. The runner records separate logs, exit statuses, times, and before/after source hashes. It checks the pinned tool version and dependency revisions, builds the project, runs concrete and universal examples, checks complete fresh axiom inventories, and demands the expected proof diagnostic for each intentionally false control.

The per-command timeout defaults to 900 seconds and can be increased with `--timeout`. A timeout is recorded as inconclusive, never as a proof failure or a passed negative control. A missing executable or dependency produces `BLOCKED`. Each run creates a new receipt directory under `padic/results/`; an explicit `--output PATH` must name a new directory.

The core direct commands, from `padic/`, are:

```bash
lake build
lake env lean -DwarningAsError=true verification/ResidualChecks.lean
lake env lean -DwarningAsError=true verification/ResidualUniversal.lean
lake env lean verification/AllAxioms34.lean
lake env lean verification/KernelAxiomInventory.lean
```

`verification/FalseControl.lean`, `PlaceholderControl.lean`, `FalseAllWord.lean`, `FalseIgnoreOutput.lean`, and `FalseLinearMinimum.lean` are required to fail under warning-as-error. They are not production modules. The wrapper distinguishes their expected contradictions from arbitrary import, inference, resource, or execution errors.

The wrapper's complete execution path has now passed on the prepared release with the restored pinned toolchain and dependency cache, including a clean project build, both axiom inventories, examples, and five expected rejections. This fresh run is separate from the historical Block 34 evidence and from the still-pending public-bootstrap run. Validate an extracted fresh receipt without rerunning Lean using `python -B tools/check_proof_receipt.py PATH_TO_RECEIPT_DIRECTORY`. That checker compares the exact proof-input hashes, all command/log records, axiom coverage, and negative controls with this checkout.

## 6. Interpret the result at the right level

A complete proof replay checks the project against its specified dependency artifacts. It does not constitute an independent reimplementation of Lean's kernel, a reconstruction of every dependency from source, a novelty audit, or a formal proof that the Python reference is equivalent as executable code.

The currently recorded status and publication requirements are in [PUBLICATION_STATUS.md](PUBLICATION_STATUS.md). The longer research agenda is in [FUTURE_RESEARCH.md](FUTURE_RESEARCH.md) and does not add prerequisites to the finite-precision claim.
