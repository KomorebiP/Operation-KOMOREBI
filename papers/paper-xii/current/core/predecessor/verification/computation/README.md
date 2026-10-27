# Reproducing Paper XII checks

`audit/computation/COMPUTATION_AUDIT.md` explains the finite contract and interpretation. `runs/` preserves result JSON, stdout/stderr, and validated version 2 manifests. No fresh Lean replay is claimed. `verification/lean/ENVIRONMENT_AUDIT.json` records the actual local runtime search.

## Fresh Python replay

Use Python 3.10+ in Linux/WSL with NumPy 2.3.5 and SymPy 1.14.0 available. The bounded runner uses POSIX resource caps. Run from the package/project root, which contains `source/`, `downloads/`, and `verification/`:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 verification/computation/run_fresh_checks.py --project . --run-id my-fresh-run
```

Every run identifier must be new. The entry point generates a concrete contract, hashes all declared inputs before and after execution, invokes the unchanged programs in disposable copies, enforces resource caps and validates the result manifest. `integrity` executes the delivered `Run-PaperXII.py verify`; `appendix-exact` executes the delivered `Run-PaperXII.py examples` from an isolated complete copy. The historical checker is copied before execution and old result files are removed from the copy.

The actual October 6 command additionally used the existing exact symbolic dependencies:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/workspace/scratch/cbc2b5a746c7/paper_xi_test_dependencies python3 paper_xii_work/verification/computation/run_fresh_checks.py --run-id fresh-20261006
```

The `PYTHONPATH` is an environment-specific dependency location, not a portable requirement. Install the stated versions in your normal Python environment or supply your own compatible local dependency path. Native Windows users can execute the raw Python checkers from disposable copies; the hard-capped runner and Lean commands are documented for Linux/WSL.

## Independent primitive and native-preservation checks

These direct commands are short, deterministic checks. Their completed bounded-run versions and exact argv are preserved in the corresponding `runs/fresh-20261006/*/manifest.json` records:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 verification/computation/benchmark_no_bytecode.py --source source/latest_v0171/Paper_XII_Complete_v0.17.1_With_Visual_Appendix/history/original_manuscript/verification/verify_paper_xii.py --output /tmp/paper_xii_rank_benchmark.json
python3 verification/computation/audit_native_reverification.py --project . --output /tmp/paper_xii_native_integrity.json
python3 verification/computation/probe_lean_environment.py
```

The benchmark entry point disables bytecode caching before importing the preserved checker. Use this safe entry point; the first archived benchmark script is retained solely to preserve the recorded run.

To validate any saved manifest against the current inputs and result hashes:

```bash
python3 verification/computation/tools/validate_manifest.py verification/computation/runs/fresh-20261006/appendix-exact/manifest.json --root .
```

The manifest paths are relative to the project root. Disposable `isolated_bundle/` and `isolated_original/` copies are reproducible working directories; they are not required for validating saved declared result JSON and input hashes. All authoritative source trees remain under `source/`.

## Prospective Lean replay

The required external runtime is Lean 4.34.0-rc2, compiler commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`, binary SHA256 `e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550`; Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine dependency revisions are in the current formal release's `RUNTIME_DEPENDENCY_PINS.json`. Validate the compiler and actual dependency HEADs against these pins first.

From a fresh disposable copy of the complete source bundle in Linux/WSL:

```bash
ulimit -v 4194304
export MALLOC_ARENA_MAX=2
python3 Run-PaperXII.py lean --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The wrapper performs cumulative production compilation, all named axiom audits and negative controls, then three `FinalClaimsConsumer` checks against the same fresh objects. The separately preserved native `ManuscriptContractReplay.lean` adds three direct manuscript-contract tests; it must be compiled with the same compiler, dependency pins, fresh production objects and matching `LEAN_PATH` before any fresh claim is made about that consumer. The companion Lean guide gives its explicit contracts and consumer entry points.

The inherited batch verifier uses one Lean thread and warning-as-error. A `RUNNING` report is incomplete and must never be labeled `PASS`; resume only with unchanged source/compiler/object hashes. Preserve logs and any failed operation. These are prospective commands, not commands executed during this audit.

## Provenance helper

The unchanged `tools/run_experiment.py` and `tools/validate_manifest.py` are copied from the installed `mathbox:computation-audit` skill, package version 3.2.0. They provide bounded provenance recording and manifest validation, not theorem verification. Their exact bytes are pinned in each completed manifest.
