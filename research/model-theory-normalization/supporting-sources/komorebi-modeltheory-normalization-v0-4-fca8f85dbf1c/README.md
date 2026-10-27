# Komorebi Model-Theory Normalization v0.4

Verified observation-row discovery, complete queue traces, and standard logical definitions.

Start with `NORMALIZED_CORE.md`, `FORMALIZATION_COVERAGE.md`, and `RESULTS.md`.
The immediate v0.3 ZIP is frozen under `history/`. This is not a p-adic block or
Representation Calculus version update.

## Reproduce

Python 3.10+ suffices for the exact trace/reference audit (standard library only):

```sh
python tools/verify_integrity.py
python new_checks/audit_discovery.py
```

The Lean proof requires the saved pinned Lean/Mathlib runtime. Its binaries/cache
are not duplicated in this archive. Set `RUNTIME` to its extracted directory,
containing `toolchain/bin/lean` and `workspace/.lake/packages/mathlib`.
The synchronous batched protocol starts a genuinely empty local build:

```sh
python new_checks/audit_batched.py --runtime "$RUNTIME" --init
python new_checks/audit_batched.py --batch 6
# Repeat --batch 6 until it prints TASKS_COMPLETE (30 tasks total).
python new_checks/audit_batched.py --finish
python new_checks/audit_release.py --runtime "$RUNTIME" --python-only
python tools/validate_manifest.py LEAN_MANIFEST.json --root .
python tools/validate_manifest.py COMPUTATION_MANIFEST.json --root .
```

Each invocation is synchronous. Batch size one is supported on runtimes with
short enclosing execution limits. Every batch verifies accepted inputs and all
completed build artifacts before proceeding. An interrupted run is not PASS.
There are 23 module builds, one all-declaration axiom audit and six controls.
Only the finisher produces the final successful Lean manifest.

The completed distribution includes a BATCH_STATE.json from its original audit.
`--init` archives a completed state and creates a new empty build. If that file
instead says IN_PROGRESS but its external build is absent, preserve it as an
interrupted record before initializing a new audit. Do not fabricate a resume.

Reruns rewrite execution records. Run distribution integrity BEFORE rerunning
any audit. The inherited `tools/audit_all.py` and earlier results belong to the
prior bridge scope; use the `new_checks` commands for this release.

## Important distinctions

The reference Lean loop uses a correct but exponentially expensive coefficient-
enumeration oracle. The fast Python Smith backend is unverified. Its complete
queue traces have independent witnesses, and four literal traces are proved in
Lean to give the same reference result. This is not a verified fast Smith engine,
a minimum formula/test-list algorithm or a learned-discovery benchmark.
