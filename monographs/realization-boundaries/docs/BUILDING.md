# Building and verifying

## Requirements

The Lean library uses [`leanprover/lean4:v4.34.0-rc2`](https://github.com/leanprover/lean4/releases/tag/v4.34.0-rc2) and Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All transitive revisions are recorded in `lake-manifest.json`. Install Lean through a toolchain manager such as `elan`, or provide that exact toolchain on `PATH`.

Python 3.10 or later is sufficient for the verification tooling and exact arithmetic. The full audit harness requires Linux or WSL2 with Bash and Git. Ordinary `lake build` uses Lean's supported host environment. Rebuilding the PDF additionally needs an installed TeX distribution. Matplotlib is needed only to regenerate figures.

Commands below state their working directory. The repository does not include multi-gigabyte compiler or Mathlib caches.

## Check the release files

From the repository root:

```bash
python3 verify_integrity.py
```

This checks expected files against `RELEASE_MANIFEST.json`. Rebuilding or editing tracked deliverables can legitimately change their hashes. Run this check before making changes.

## Conventional Lean and Lake setup

From the repository root, with the pinned toolchain installed:

```bash
lake exe cache get
lake build
```

Lake reads `lean-toolchain` and `lake-manifest.json`. The cache command obtains the pinned dependencies and compiled Mathlib files. Reproducing the release does not require changing dependency versions or running `lake update`.

A build checks the Lean library. To run the additional declaration audit, positive contracts, intended rejection diagnostics, executable examples, source/dependency identity checks, and kernel replays, use Linux or WSL2:

```bash
bash verify_with_lake.sh --output ../realization-boundaries-verification
```

Choose a new output directory each time. The launcher presents the existing toolchain and package checkout to the original strict verifier through temporary symbolic links. It neither upgrades dependencies nor downloads or modifies a toolchain. The verifier rebuilds project objects serially and refuses mismatched compiler identities or dependency revisions.

The accepted original run remains in `verification/accepted_v1.0.0`. New local runs are separate evidence and do not overwrite it.

## Offline portable kit

If you already have the separately supplied `Komorebi_Portable_Lean_4.34.0-rc2` kit, no network access is required. Its original `Lean_Compact_01.zip` through `Lean_Compact_05.zip` files and starter assembler are not bundled in this repository. Do not assume a public reader has those files; the conventional setup above is the public alternative.

The assembled portable archive has SHA-256:

```text
f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7
```

From the repository root:

```bash
export KOMOREBI_LEAN_KIT=/path/to/Komorebi_Portable_Lean_4.34.0-rc2
bash scripts/verify_portable.sh --output ../realization-boundaries-offline-verification
```

The original wrapper enables the kit's executable-discovery adapter only when its known launch failure occurs. The full verifier checks the adapter's bytes along with the relevant runtime and cache inputs.

## Python examples and tests

From `publication/monograph_source`:

```bash
python3 worked_example.py
python3 src/replay_printed_example.py
python3 src/exact_checks.py --output verification/local_core.json
python3 src/supplemental_checks.py --output verification/local_extra.json
python3 src/release_checks.py --output verification/local_release.json
```

These three suites cover 189,069 exact finite assertions. They exercise the Python implementation and do not replace the Lean proofs. Selectors supplied as oracles are assumed to answer correctly; the programs do not evaluate arbitrary noncomputable selectors.

## Publication

From `publication/monograph_source`:

```bash
python3 build.py
```

To replay arithmetic and regenerate the Matplotlib figures before typesetting:

```bash
python3 build.py --verify --figures
```

The publication README lists the TeX packages. Supplied vector figure PDFs allow rebuilding without regenerating images. The build script does not install dependencies or use the network.
