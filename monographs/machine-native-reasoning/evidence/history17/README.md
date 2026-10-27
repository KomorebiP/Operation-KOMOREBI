# Machine-Native Reasoning — common observable quotient

**Formal companion 0.17.1 · Komorebi P.**

This cumulative project adds Core 2.4, *A common observable quotient*, to the
previous 24-result selected correspondence. Release acceptance requires both
complete current-source gates and their comparison to pass. The actual status,
counts and receipt hashes are in `release/ADMISSION_RECORD.json` and
`release/REPORT.md`. On acceptance the selected correspondence is **25/27**.
The pending source results are 2.5 and 3.2. The larger monograph and the Large
Signal Model have separate formalization inventories.

The principal theorem is
`Komorebi.MachineTheory.CommonQuotient.source_core24`.
It proves equivalence of all-vector fixed-candidate observable agreement,
invisibility of the constructed propagated discrepancy subspace, and existence
of actual common linear quotient data. The same data preserve arbitrary finite
switching of candidate operators. Finite-dimensional closure is proved by the
ambient dimension. The original source book and all inherited substantive Lean
modules are unchanged.

## Read and reproduce

Start with `docs/CORE24_PROOF_GUIDE.md`,
`docs/CORE24_SOURCE_CORRESPONDENCE.md`, and `docs/CORE24_RECOVERY.md`.

```sh
python3 tools/verify_package.py
python3 scripts/verify.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out evidence/my_replay
```

Use a new evidence directory. Verify the immutable delivered package before
creating local outputs. `scripts/supervise.py` also records a bounded whole-run
receipt. Every Lean command retains the 45-second command limit, one worker,
warnings-as-errors, and 4,096 MiB internal memory limit. Dependencies are the
pinned offline Lean 4.34.0-rc2 and Mathlib environment, not the current online
release. The runtime is external and is not redistributed in this package.

## Important recovery distinction

The received 0.16.1 outer ZIP was incomplete, and intentional rematerialization
returned the same bytes. Its complete embedded frozen-source snapshot matches
the externally recorded hash, and all 397 source-bound inputs match the recovered
successful prior gate. Every source needed to continue is intact. Sixty-five
historical payload files were not recovered. The precise list is retained.
This package does not claim that the old outer archive was fully authenticated
or that missing historical receipts were recreated. New cumulative runs verify
the recovered sources together with the new work.

The package contains the full current formal source, checks, source-facing APIs,
source binding, pinned dependency declarations, current verification records,
development failures, exact finite regressions and a restart ledger. The
preserved prior frozen-source snapshot and selected recovered historical records
are included under `evidence/history_core83`; this is not a duplicate of the
incomplete outer archive or the entire earlier research history.

These are formal mathematical results under their stated premises. Neither an
externally learned model, a numerical quotient finder, an action dispatcher,
native Windows execution, independent kernel validation nor public hosting is
asserted. Same-kernel replay and dependency-byte authentication have their own
explicit trust boundary.
