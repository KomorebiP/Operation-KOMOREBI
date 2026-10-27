# Portable serial replay

The proof runtime is supplied separately. This package contains proof sources,
finite companion code, source guides, historical verification and current
bounded evidence. It does not contain Lean executables or an imported Mathlib
build cache.

Required proof environment:

- Linux x86_64, including x86_64 WSL2 on Windows.
- Komorebi portable Lean 4.34.0-rc2, commit
  `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06` and
  dependency revisions in `lake-manifest.json`.
- Python with SymPy 1.14.0 for the finite companion cross-checks. Use
  `requirements-rational-tests.txt`; Python is tested separately from Lean.

From this `formal` directory, inspect the source plan without a proof runtime:

```bash
python3 scripts/verify.py --plan-only
```

With the separately restored matching runtime, launch the full discovered
corpus serially:

```bash
bash verify_low_memory.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --out verification/full93-local --timeout 240
```

The driver requires exact Lean version/commit and dependency revisions. It
freshly compiles every discovered production module, builds the root, audits
every enumerated declaration, runs the stated negative controls, and replays
the production modules with the same Lean kernel. Imported Mathlib artifacts
are reused. The source parser is checked on this package and is not a general
Lean parser. A successful full runtime run has not been performed for this
edition.

The launcher sets one Lean thread, serial commands and a default per-process
address-space limit of 4 GiB. To choose a different limit, set
`KOMOREBI_VERIFY_MEMORY_KIB`. The limit is not aggregate process-tree memory.
The verifier has a per-command wall timeout. `--skip-kernel-replay` explicitly
reduces verification and is recorded in the report. It never means replay
passed.

From the release root, finite Python companions can be rerun without Lean:

```bash
python3 verification/replay_finite_companions.py --plan-only
python3 verification/replay_finite_companions.py \
  --output verification/local_python_replay
```

Choose a new output directory for each run. The finite driver uses unchanged
check scripts in private per-suite trees, records native JSON results, and
validates bounded version-2 manifests. Each suite is capped at 600 wall
seconds, 500 CPU seconds per process, 1 GiB address space, one inherited core,
one cooperative numerical-library thread, and 1 MiB outer log output.
The fixed suites use their own documented seeds. Current bundled evidence
resides at `verification/python_replay`.

Validate a bundled manifest from the release root:

```bash
python3 formal/scripts/provenance/validate_manifest.py \
  verification/python_replay/calibration/manifest.json --root .
```

The bundled provenance utilities are unchanged copies from mathbox
computation-audit 3.2.0. Their origin and hashes are recorded. Provenance
validation checks records and hashes. It does not prove the mathematics.
