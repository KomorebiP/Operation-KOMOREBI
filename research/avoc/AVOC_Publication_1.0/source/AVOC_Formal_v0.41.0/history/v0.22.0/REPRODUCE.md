# Reproduce AVOC v0.22.0

## Environment

Linux x86-64/WSL; Python 3.10+; Lean 4.34.0-rc2 at commit
6a10ac8c22beadecabdbb0919c2b50214762f91d; mathlib
 aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
The nine external revision pins are in `lake-manifest.json`.
The source package excludes the runtime and `.lake/` outputs.

```bash
export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python tools/check_manifest.py
python tools/inventory_v022.py
python tools/verify_release.py --prepare
python tools/build_parallel.py --seconds 10 --workers 2
```

Repeat the bounded build command until it reports 119/119 current targets. Do not
repeat --prepare between slices. After a host interruption ensure no prior Lean
child is still running, then rerun unfinished targets. External caches are retained.
The current clean run begins from empty local output and does not rely on old logs.

```bash
python tools/verify_release.py --audit
python tools/verify_release.py --negative
python checks/test_retry_advisor.py
python tools/summarize_v022.py --baseline /path/to/AVOC_Formal_v0.21.0.zip
```

On a capped host run negative files in slices via `--start 0 --count 10`, then
starts 10,20,30,40. A missing import, timeout, or missing log is not a substantive
negative rejection. All current records are under `results/v0.22.0/`.

## Read-only executed Lean advisor

```bash
python tools/run_retry_advisor.py examples/retry_advisor/persistent.json
python tools/run_retry_advisor.py examples/retry_advisor/observed_fault.json
python tools/run_retry_advisor.py examples/retry_advisor/iid.json
python tools/run_retry_advisor.py examples/retry_advisor/exhausted.json
```

The wrapper calls `tools/RetryDecisionMain.lean`, not a Python substitute for the
proved evaluator. Fractions must be integers or exact strings. Horizon <=32.
Unknown fields, floats, Boolean integer substitutes, invalid probability values,
invalid ledgers and zero-probability supplied faults are rejected. Published
outcomes recommend reconciliation rather than retry.

`observe_operational_fault` explicitly evaluates a hypothetical/supplied operational
observation under the declared model. It DOES NOT inspect a real process or infer
that a timeout or unfinished log is that observation. The output ledger is only a
hypothetical next state; nothing is authorized or written to a proof store.

The independent oracle integrates each possible cutoff strategy over latent
reliability types directly; it does not reproduce the Lean Bayesian recursion.
It checks 5,400 base cases and 491 fault-update cases plus invalid/phase cases.
This is bounded implementation evidence, separate from the universal Lean proofs.

## Existing backend

Use `tools/run_retry_workflow.py` and the inherited `RETRY_FORMAT.md` for actual
explicit keyed authorization. This release does not change those commands, migrate
old stores, or automatically apply advice. They must still verify current phase,
exact generation, authoritative absence of a commit, source and receipt identity.

## Packaging and evidence

Check the delivered payload manifest BEFORE regenerating evidence. Historical
version directories stay historical. The package manifest excludes itself and
`.lake`, `.git`, Python caches and bytecode. Current checks are not full rebuilds
of the compiler, external dependency source, Python or the OS.
