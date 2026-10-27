# Reproduce Block 28

Pins: Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d;
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The compiler and dependency cache
are not embedded in this release.

Work on an extracted copy. Keep the immutable evidence copy unchanged.

```bash
export KOMOREBI_LEAN_RUNTIME=/path/to/Komorebi_Portable_Lean_4.34.0-rc2
export PATH="$KOMOREBI_LEAN_RUNTIME/toolchain/bin:$PATH"
export PYTHONDONTWRITEBYTECODE=1
python3 verification/prepare_offline.py "$KOMOREBI_LEAN_RUNTIME"
lake build
lake env lean -DwarningAsError=true verification/AxiomAudit.lean
lake env leanchecker -v KomorebiPadic.SupportExamples
lake env lean -DwarningAsError=true verification/Examples.lean
lake env lean -DwarningAsError=true verification/Universal.lean
lake env lean -DwarningAsError=true verification/PredecessorExamples.lean
python3 verification/audit_support.py --output results/reproduced_support_audit.json
```

Files in verification/negative are deliberately invalid and must fail with the
expected contradiction or placeholder diagnostic, not merely any nonzero exit.
A fresh project-only rebuild may remove .lake/build after checking that it is not
a symlink. Never clean the shared mathlib cache. Cached dependency objects were
pinned and their Git revisions checked, not independently rebuilt from scratch.

Read-only release checks (no new Lean computation):

```bash
python3 verify_release.py
```

The included verification/run_job.py can record individually bounded commands.
Read its returned results/*.json exit and inputs_unchanged fields: the supervisor's
own exit is not a substitute for the command's recorded exit. A timeout is not a
successful check. The arithmetic audit requires only Python's standard library.
