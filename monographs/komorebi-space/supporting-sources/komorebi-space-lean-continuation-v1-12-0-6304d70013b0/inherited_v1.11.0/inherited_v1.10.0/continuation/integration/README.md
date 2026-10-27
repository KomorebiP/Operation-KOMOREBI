# Cumulative Komorebi Space replay

This directory assembles the **unchanged** v1.7.0 canonical core and its focused
regularization extension into one actual source tree. The historical source
trees, controls, and evidence are retained in the parent release. Nothing in this
directory changes the formal status of the outstanding WR groups by itself.

## Accepted continuation evidence

`verification_summary.json` binds the following completed executions to their
source snapshots, logs, and declaration exports:

| Execution | Accepted result |
|---|---|
| `runs/cumulative_base_01/receipt.json` | All 144 inherited-union compilation targets passed from an empty project build; 4,842 project declarations audited; both positive and all twelve rejection controls passed. |
| `runs/cumulative_base_01/postflight.json` | Independent check of the exact command inventory, complete terminal source/control snapshot, and final object hashes passed. |
| `runs/wr01_wr02_overlay_01/receipt.json` | Three new WR modules and the changed combined root compiled; fresh full audit covered 4,872 declarations; four positive, fourteen compiler rejection, and two policy rejection controls passed. |

The enlarged final source snapshot is
`runs/wr01_wr02_overlay_01/source/`. It contains 144 production modules and three
entrypoints, for 147 module targets. The explicit named theorem/lemma inventory
is 1,580, including 22 new explicit theorems. The full declaration audit includes
generated declarations, with 30 in the new modules. These are distinct counts.
All 143 inherited production and entrypoint source files retain their archive
bytes. Only `propext`, `Classical.choice`, and `Quot.sound` occur in the audited
axiom union.

The final enlargement reused verified inherited objects and compiled four
targets. It is not a claim that all 147 final targets were compiled again from
an empty project build. The new theorem types are recorded in the summary and
the full declaration export, allowing their actual hypotheses to be reviewed.

## Exact source scope

| Item | Count |
|---|---:|
| Canonical production modules | 138 |
| Focused regularization production modules | 3 |
| Total production modules | 141 |
| Preserved inherited entrypoints | 2 |
| New combined entrypoint | 1 |
| Total source compilation targets | 144 |
| Explicit named theorem/lemma declarations, lexical count | 1,558 |
| Positive regression files | 2 |
| Compiler rejection controls | 10 |
| Custom-axiom policy rejection controls | 2 |

The explicit declaration count includes auxiliaries. It is not a count of
independent discoveries. Imported declaration and axiom counts come only from a
completed compiler run, not from this lexical inventory.

`inventory.json` records the byte hash of every assembled file and the complete
local import graph. Every inherited production module, entrypoint, control, pin
file, toolchain marker, and type-name input was compared with its exact member in
`Komorebi_Space_Complete_v1.7.0.zip`, whose SHA256 is
`914bb768686bc186d4baefd53c1e13690346b0f506560ede916d1fb87d7e6794`.
There are no conflicting source paths. The graph has no missing local import or
cycle, and the combined entrypoint reaches every production module.

These are static results. **Only a run receipt whose status is exactly `PASS`
records completed compilation, axiom export, and all controls.** A status of
`STATIC_CHECKS_PASS_NOT_LEAN_VERIFIED` deliberately carries no Lean claim.

## Reproduce

The scripts use Python's standard library and perform no downloads.

```sh
python3 scripts/verify.py --static-only --label static_check_02
python3 scripts/verify.py \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --path-adapter /path/to/Komorebi_Portable_Lean_4.34.0-rc2/compat/app_path.so \
  --label cumulative_independent_01
```

The optional path adapter is needed only for the documented executable-location
failure in some container environments. Its hash is recorded whenever selected.
Leave out `--path-adapter` on a host where the unmodified Lean executable starts
normally. The runtime remains a separately supplied Linux x86_64 bundle.

The verifier checks the pinned Lean version and commit and all nine clean Git
dependency revisions. It copies the assembled source into a new run directory,
recompiles all 144 targets from source into an empty local build directory, and
audits the actual imported declarations for all 141 production modules. It then
runs the two positive files and all twelve rejection controls. Missing modules,
missing identifiers, crashes, or timeouts do not count as successful rejections.
The policy tests must emit their designated policy-rejection diagnostics.

Existing run labels are never overwritten. Every attempt retains its logs and
receipt, including failures and interruptions. A later pass does not convert a
previous failed or incomplete attempt into success. The `runs/` directory can be
large because it preserves the exact source snapshot and compiled objects.

Once a cumulative base has completed with status `PASS`, new modules can be
verified together with it without repeating the entire inherited compilation:

```sh
python3 overlay/verify_overlay.py \
  --base runs/cumulative_independent_01 \
  --base-postflight runs/cumulative_independent_01/postflight.json \
  --overlay ../formal \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --path-adapter /path/to/Komorebi_Portable_Lean_4.34.0-rc2/compat/app_path.so \
  --label wr_overlay_independent_01
```

This second procedure validates the base receipt, source hashes, command logs,
compiler identity, and every compiled object before making a source snapshot.
First run `python3 postflight/validate.py --base /absolute/path/to/the/base/run`
to validate its complete terminal source/control snapshot and exact command
inventory. Its separate `postflight.json` must be bound to the accepted base.
It compiles the new production modules and updated combined root, then audits
the entire resulting declaration environment and runs all inherited and new
controls. Its receipt explicitly records `clean_project_build: false` and lists
the inherited objects reused. **It is a fresh incremental replay over a clean
accepted base, not a second compilation of all final modules from an empty build.**
The overlay is refused if it would overwrite an inherited production module.

To reproduce the source assembly, make a copy of this directory without
`project/`, `inventory.json`, or `runs/`, and run:

```sh
python3 scripts/assemble.py \
  --source /path/to/Komorebi_Space_Monograph_v1.7.0 \
  --archive /path/to/Komorebi_Space_Complete_v1.7.0.zip
```

## Trust boundary

The official Lean compiler/kernel and the standard axioms `propext`,
`Classical.choice`, and `Quot.sound` remain trusted. Compiled external mathlib and
package caches are reused. They are not rebuilt or independently kernel-checked.
The `Cli` package is pinned although this runtime has no compiled `Cli` cache;
all actually imported modules must still load successfully during compilation.
This replay does not certify prose translations, universally verify Python
implementations, or establish formal counterparts for the remaining WR groups.
