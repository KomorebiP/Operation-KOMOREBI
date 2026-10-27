# Reproduce AVOC v0.25.0

## Pinned environment

Linux x86-64 or WSL, Python 3.10+ with SQLite and fcntl. This run used Python 3.13.5,
SQLite 3.46.1, Lean 4.34.0-rc2 commit 6a10ac8c22beadecabdbb0919c2b50214762f91d,
and mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Nine external revisions are in
`lake-manifest.json`. The source ZIP excludes runtime and dependency caches.

```bash
export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python tools/check_manifest.py
python tools/inventory_v025.py
python tools/verify_release.py --prepare
python tools/build_parallel.py --seconds 20 --workers 3
```

Repeat the bounded build command until all 136 current targets are successful. Do not
repeat preparation between slices. Interrupted modules and descendants must be rerun;
current direct-import hashes are part of compilation provenance. External cache is kept.

```bash
python tools/verify_release.py --audit
python tools/verify_release.py --negative
```

There are 63 deliberately false files. Use `--start` and `--count` slices on capped hosts.
Import/setup failures and timeouts are not mathematical negative-test evidence.

`synthesis_source_pins.json` freezes nine source files and eight checker/runtime targets.
The wrapper verifies them and current compilation records. `tools/pin_synthesis.py` is
only a release-preparation tool AFTER reviewing and proving changes. Never rerun it to
bless an arbitrary edit in an existing protected campaign.

## Read-only synthesis

```bash
python tools/synthesize_upgrade.py search examples/synthesis/pair.json
python tools/synthesize_upgrade.py search examples/synthesis/guard.json
python tools/synthesize_upgrade.py search examples/synthesis/pair_unprofitable.json
```

The configuration supplies a reference expression, a declared deployment-call count,
campaign credit, grammar depth, trial limit and search credit. It does not provide the
replacement. The grammar enumerates its candidates. Runtime limits: depth <=2, trial
limit <=21,845, reference <=127 nodes, exact integer fields <=100,000,000. Floats,
Boolean integer substitutes, unsupported expression operators and unknown fields fail.

## New protected campaign and invocation

```bash
python tools/synthesize_upgrade.py run examples/synthesis/pair.json --run-dir /tmp/avoc-generated-new
python tools/synthesize_upgrade.py inspect --run-dir /tmp/avoc-generated-new
python tools/synthesize_upgrade.py invoke --run-dir /tmp/avoc-generated-new
```

The directory must not already exist. `authority.json` and `campaign.sqlite3` are
protected records. Do not edit them to erase charges, substitute the target or change
the selected AST. Run reserves the complete credit envelope before generation. A
completed result records actual declared charges and releases unused credit. An
interrupted/unconfirmed search keeps its reservation and has no invocable result.
No automatic retry, refund or migration from other AVOC formats is supported.

Invocation replays the inherited generated-program promotion journal and executes the
retained AST through the same Lean interpreter, without repeating candidate enumeration.
It does not install generated native code or mutate earlier scientific proof stores.

## Independent tests and provenance

```bash
python tools/record_synthesis_tests.py differential
python tools/record_synthesis_tests.py live
python tools/summarize_v025.py --baseline /path/to/AVOC_Formal_v0.24.0.zip
```

The recorders bind test source before/after hashes and retained output hashes. The
independent oracle uses Python truth bitsets and explicit grammar enumeration, not the
Lean synthesis recursion. It checks 747 campaign cases, 255 equivalence queries, ten
invalid wire requests and all eight executions of every campaign result. The live
suite uses sixteen scenarios in fresh temporary stores with actual Lean subprocesses.
Its interruption fixtures raise controlled Python exceptions; they are NOT power-loss
or SIGKILL experiments. Do not resume packaged historical test databases on another host.

The collector checks every final compilation, imported-output hash, theorem name,
axiom report, substantive negative diagnostic, inherited source and test provenance.
Old test directories are historical evidence and were not rerun in this block.

## Optional evidence manifest and package

```bash
python tools/record_v025_audit.py --baseline /path/to/AVOC_Formal_v0.24.0.zip
python tools/audit/validate_computation_manifest.py results/v0.25.0/computation_manifest.json --root .
python tools/package_v025.py --output /chosen/AVOC_Formal_v0.25.0.zip
```

The metadata recorder times a fresh evidence collector, not the entire earlier build
or test suite. The included validator is a v1-only local adaptation; metadata validation
does not prove mathematical interpretation. Per-target and per-test records carry the
execution details. Check the ORIGINAL manifest before regenerating records. Regeneration
changes hashed payload files; the manifest excludes itself and external packaging notes.
