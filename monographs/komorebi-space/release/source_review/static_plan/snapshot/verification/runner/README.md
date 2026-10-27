# Integrated Lean verification

This runner recompiles the publication's complete Lean project into an initially
empty object directory. It then inventories every project declaration by Lean's
module provenance, recursively checks axiom dependencies, and runs the recorded
positive and negative controls. It uses Python 3's standard library and the
installed Lean/Lake toolchain. It contains no host-specific paths or adapters.

## Prepare the pinned environment

Install the toolchain named in `lean/lean-toolchain`. The required compiler is
Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
The exact external revisions are locked by `lean/lake-manifest.json`, including
mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

From the publication's `lean` directory, prepare the external dependency caches:

```sh
lake exe cache get
```

This preparation can require network access. The verification run uses the
installed caches. It does not rebuild mathlib or authenticate downloaded object
files. Keep enough disk space for a fresh project source snapshot, object files,
logs, and an inventory of the installed compiler and cache bytes.

## Run the complete check

From the publication's root directory:

```sh
python3 verification/runner/runner.py --output ../verification-v1.15.0-01
```

The output directory must not already exist and must be outside the publication
tree. Use a new numbered directory for each attempt. A failed or interrupted run
is retained. No flag reuses old project objects or skips the declaration audit.

The runner compiles one project module at a time with `-j1`,
`-DwarningAsError=true`, and `-DautoImplicit=false`. This limits concurrent memory
use. It does not impose a fixed memory cap. Per-command timeouts default to 300
seconds, with 1800 seconds for the declaration audit. Increase `--timeout` or
`--audit-timeout` for a slower machine, preserving the recorded settings.

For a static input check without executing Lean:

```sh
python3 verification/runner/runner.py --output ../verification-plan-01 --plan-only
```

This produces `STATIC_VALIDATION_ONLY`, which is not a proof-verification pass.
If an installation needs an external environment wrapper, prefix the Python
command with that wrapper. The runner inherits the environment and records the
effective Lean paths and any explicit `LD_PRELOAD` files. It does not install or
select a compatibility shim.

## What PASS means

`receipt.json` has status `PASS` only after all of these conditions hold:

- Every project module is reachable from the four declared import roots and is
  compiled freshly in dependency order. All project objects originate in this
  attempt's empty build directory.
- The installed compiler version and commit match, and all nine dependency Git
  revisions match the lockfile with no tracked changes.
- The declaration inventory includes every production module and excludes
  declarations attributed to dependency modules. Generated declarations are
  included. Direct project axioms and unsafe declarations are rejected.
- Recursive axiom dependencies are contained in `propext`, `Classical.choice`,
  and `Quot.sound`. In particular, `sorryAx` is rejected.
- All control outcomes match their specifications. Compilation success and
  policy rejection are recorded separately. Every expected rejection must
  match the complete list of error positions and headlines as well as the
  required diagnostic text. Infrastructure and resource errors do not count as
  successful negative controls.
- Sources, controls, verifier files, generated audit inputs, fresh project
  objects, command logs, and recorded evidence remain identical at the final
  check. The installed compiler and external cache bytes are hashed before and
  after the replay. Every expected command occurs exactly once in order.

The result is a compiler/kernel check of the supplied formal statements. It
does not by itself prove that every statement faithfully expresses the printed
mathematics. The publication's independent statement reviews address that
separate question. Endpoint checks also cannot detect a transient change that
was restored before the final check.

## Controls and provenance

`control_manifest.json` contains 56 controls:

| Source | Accept | Elaboration rejection | Policy rejection | Total |
|---|---:|---:|---:|---:|
| Accepted v1.12.0 cumulative project | 14 | 28 | 2 | 44 |
| Accepted diagonal completion | 2 | 5 | 1 | 8 |
| v1.15.0 statement connections | 2 | 2 | 0 | 4 |
| Total | 18 | 35 | 3 | 56 |

The 52 inherited control sources are byte-preserved. Each manifest entry records
its archive identity, archive member, and SHA-256 digest. The two inherited
cumulative policy controls raise an explicit error inside Lean after detecting
a forbidden axiom. Their expected compiler status is failure at that embedded
policy check. The diagonal custom-axiom control elaborates successfully and
prints its recursive axiom dependencies, after which the runner rejects the
foreign axiom. Neither case is reported as ordinary elaboration failure.

The four new controls check the exact rounded inexact-solver statement, reject
replacement of its measured-residual hypothesis by the scalar tolerance budget,
check the actual diagonal unit vectors and nonclosed range, and reject deletion
of the nonclosed-range theorem's negation. These are focused interface checks,
not an exhaustive mutation test suite.

The runner and Lean exporter adapt the accepted cumulative replay's source
inventory, sequential compilation, and recursive-axiom methods, and the accepted
diagonal audit's explicit direct-axiom rejection. The new implementation places
all 166 project targets and all 56 controls in one portable invocation.

## Evidence files

- `receipt.json`: commands, statuses, counts, settings, and input/output hashes.
- `snapshot/`: exact production sources, configuration, verifier, and controls.
- `build/`: freshly compiled project object files.
- `declarations.json`: every project declaration with its module, kind, safety
  status, and recursively collected axiom dependencies.
- `runtime_snapshot.json`: endpoint identities of trusted compiler/cache bytes.
- `logs/`: complete stdout and stderr for every command, including intentional
  control failures.

Read a non-PASS receipt's `failure` field and named log before starting another
attempt. A timeout, environment failure, unexpected diagnostic, or changed input
is a failed verification attempt, not a mathematical counterexample.
