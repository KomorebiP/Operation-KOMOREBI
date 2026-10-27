# Reproduce the formal checks

Use working copies of the supplied sources. Preserve the recovered originals.
The required compiler releases are exact, rather than interchangeable.

| Project | Lean pin | Dependency pin |
|---|---|---|
| KTG | `leanprover/lean4:v4.34.0-rc2` | Bundled `Std`, no external Lean packages |
| Original and checked ABCJet | `leanprover/lean4:v4.19.0` | mathlib v4.19.0 at `c44e0c8ee63ca166450922a373c7409c5d26b00b`, with the nine package commits in `ABCJet_DEPENDENCY_PINS.json` |

Exact official release URLs, sizes, local hashes and the available official
v4.34 archive digest are recorded in the runtime recovery JSON files.
The compiler binaries and mathlib cache files are external dependencies, not
bundled in the evidence ZIP.

## KTG

Copy `ktg_source` to a working directory. The supplied subset includes every
compiler input required by the original verifier, including the two required
source-map notes and the predecessor source-hash report. It excludes the
external IUT papers and historical output logs. The original 131-file archive
manifest was authenticated separately.

Set `LEAN_BIN` and `LAKE_BIN` to the exact 4.34.0-rc2 executables and run from
the working directory:

```bash
python3 verification/verify_block03.py --clean
```

Copy the supplied `KTGAxioms.lean` into the working project's
`formalization/lean` directory, then run there:

```bash
lake env lean -DwarningAsError=true KTGAxioms.lean
```

The expected source count is 22. The separate axiom audit has 42 targets.
The proof boundary and actual source-instance caveats remain those in
`../FORMAL_STATUS.md`, regardless of compiler success.

## ABCJet

Copy `jet_source` or `jet_checked_source` to a fresh working directory. Use
Lean 4.19.0. The checked copy differs by exactly the two tactic combinators
listed in `ABCJet_CHECKED_COPY_PATCH.diff`.

```bash
lake update
lake exe cache get
lake build
lake env lean -DwarningAsError=true ABCJet.lean
```

Compare the resolved package commits with `ABCJet_DEPENDENCY_PINS.json`.
The original source is expected to build with two style warnings and fail
the final warning-as-error command. The checked copy passed every command.
No linter was disabled in the checked-copy run.

Copy the supplied `ABCJetAxioms.lean` into the working directory and run:

```bash
lake env lean -DwarningAsError=true ABCJetAxioms.lean
```

The expected target count is seven. Six rational identities use the standard
axioms `propext`, `Classical.choice` and `Quot.sound`. The integer remainder
identity uses `propext` alone. These are arithmetic identities with their
stated quantifiers, not a formalization of the analytic or global ABC route.

## This host's compatibility layer

An ordinary Lean installation need not have the host issue encountered here.
This host denies a process's own numeric `/proc/<PID>/exe` lookup, while
allowing `/proc/self/exe`. The recorded runs therefore used the supplied
`proc_self_compat.c` shim. It redirects only that own-process `readlink` call.
All other paths pass unchanged. Compile it with:

```bash
cc -shared -fPIC -O2 -Wall -Wextra -Werror proc_self_compat.c -ldl -o proc_self_compat.so
```

Use `LD_PRELOAD` with the absolute path of that shared object only if this
specific host issue occurs. The exact shim used in this run has SHA-256
`f9d97611cfbbab4b36bfa7a33d0812a38f7f35384683c5fcab0954f7008bbcc1`.
Source and compiler bytes are not edited by the layer. The recorded tar
ownership correction similarly affects host metadata only.

## Provenance records

`ktg_provenance_run`, `jet_provenance_run` and
`jet_checked_provenance_run` contain the actual version 2 manifests and run
outputs. The middle run is an unsuccessful strict source check, retained as
such. All three manifests passed the current computation-audit validator
with input and output hashes checked. The runner and validator are the
current mathbox computation-audit skill helpers. Their command argv records
and all primary compiler logs are included. The direct Lean commands above
can reproduce the mathematical compilation scope without those helpers.
