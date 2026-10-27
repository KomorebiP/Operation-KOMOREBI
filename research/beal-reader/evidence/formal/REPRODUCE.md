# Reproduce the Beal formal subset

Use separate working copies. Preserve the recovered originals. The two exact
compiler and library environments are distinct.

| Source group | Lean toolchain | mathlib commit |
|---|---|---|
| Historical Block 47 and 48 | `leanprover/lean4:v4.34.0-rc2` | `aeb72f1e9981b6d35b426b16dca7759be3e7ba06` |
| New `BealAffineReader` | `leanprover/lean4:v4.19.0` | `c44e0c8ee63ca166450922a373c7409c5d26b00b` |

The successful exact historical source run is in `historical_exact_run02`.
The successful reader run is in `affine_formal_run04`. The compiler and package
pins, declared commands, source hashes and actual outputs are in those folders.
`MANIFEST_VALIDATION.json` records all seven successful validations of provenance
records, including the five unsuccessful commands.

## Standalone reader project

Copy `reader_project` to a writable working directory. Its toolchain and project
file select the exact Lean and mathlib pins. With a normal Lean installation,
run from that copy:

```bash
lake update
lake exe cache get
lake build
lake env lean -j 1 -DwarningAsError=true BealAffineReader.lean
```

The last command is the portable equivalent of the successful current direct
elaboration. Expect eleven axiom reports, using only `propext`, `Classical.choice`
and `Quot.sound`. The theorem names are all under
`KomorebiBeal.ReaderAffine`. No independent `leanchecker` run is claimed for this
Lean 4.19 module.

## Standalone historical source project

Copy `historical_project` to a writable working directory and use its exact
toolchain file. Run:

```bash
lake update
lake exe cache get
lake build
lake env lean -DwarningAsError=true AxiomAudit.lean
lake env lean -j 1 -DwarningAsError=true AxiomAudit48.lean
lake env lean -j 1 -DwarningAsError=true BealBlock48LocalAlgebra.lean
```

The first axiom audit has twenty-one targets. The second has eight targets.
The final Block 48 source check also emits those same eight reports, rather
than eight additional theorems. The standalone projects are small source entry
points. The current successful run used direct compiler calls and the unchanged
historical Block 47 verifier, as recorded below. The supplied project files do
not claim a new mathematical scope.

## Exact original Block 47 verifier

The original `historical_source/verify_block47.py` expects a working project
containing `lean/BealLaneCertificate.lean`, `BealCorrelationExamples.lean`,
`BealModSevenCartier.lean`, and `BealBlock47.lean`. Place the unchanged verifier
at `verification/formal/verify_block47.py` in that project.

It expects a portable runtime root with the exact compiler under
`toolchain/bin`, and a Lake workspace under `workspace`. Mathlib must be a
dependency at `workspace/.lake/packages/mathlib`, not the workspace root itself.
The other declared packages and cached compiled objects must also be available.
After resolving those pins, run:

```bash
python3 verification/formal/verify_block47.py --runtime /absolute/runtime/root
```

This is the actual original verifier invoked by the successful current wrapper.
Its receipt records four strict source compilations, the replay-source build,
the project-only `leanchecker` call, all twenty-one axiom reports and the three
expected rejected controls. The top-level current wrapper
`check_historical_exact.py` copies the recovered inputs to a private working
project. It does not modify any historical proof or the original verifier.

The wrapper paths in the archived receipts name this host's cached runtimes.
Portable reproduction replaces those infrastructure paths with a local exact
installation. It does not replace mathematical inputs or change theorem
statements.

## Host-specific executable compatibility

This host's own-process numeric `/proc/PID/exe` lookup is denied. The supplied
`proc_self_compat.c` redirects only that lookup to `/proc/self/exe`. On this host,
the successful commands used the resulting shared object via `LD_PRELOAD`.
An ordinary host may not need the shim. Build it only when that specific lookup
failure occurs:

```bash
cc -shared -fPIC -O2 -Wall -Wextra -Werror proc_self_compat.c -ldl -o proc_self_compat.so
```

The successful current shared object SHA-256 is
`f9d97611cfbbab4b36bfa7a33d0812a38f7f35384683c5fcab0954f7008bbcc1`.
Compiler and proof bytes remain unmodified.

## Recheck provenance

From the source package root, a representative current validation is:

```bash
python3 evidence/computation/tools/validate_manifest.py evidence/formal/historical_exact_run02/manifest.json --root .
python3 evidence/computation/tools/validate_manifest.py evidence/formal/affine_formal_run04/manifest.json --root .
```

Validation checks the declared input and output bytes. It does not prove the
external arithmetic application. Failed manifests remain failed command
records even when their provenance validates successfully. Compiler binaries,
the official library cache and generated working-project `.olean` files are
external dependencies rather than release payloads.
