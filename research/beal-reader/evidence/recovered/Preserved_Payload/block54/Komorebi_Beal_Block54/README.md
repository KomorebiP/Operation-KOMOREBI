# Komorebi Beal research — Block54 v5.4.0

Frobenius compatibility, actual global cup vanishing, and reduced reciprocity.
Start with work54/REPORT.md, then TARGET_CONTRACT.md and PROOF_BOUNDARY.md.

The original Block53 ZIP is in predecessor/, unchanged and recursively complete.
This block supplies written proofs, exact Python certificates, source/lineage
records, failure records, and an executable verifier. It does not solve Beal or
the complete(3,5,7) branch. No new Lean certificate or independent mathematical
review is claimed.

## Replay

Python3.10 or later, standard library only. From the extracted package root:

    python verify.py --replay-predecessors --report ../Block54_Replay.json

Windows PowerShell uses the same command; a relative report path outside the
package is required. No installation of external packages is needed. The
verifier checks member/hash integrity, checks15 named inherited source hashes,
extracts predecessors in a temporary directory, replays their declared checks,
then recomputes four new exact outputs in a fresh temporary copy. It rejects
stale or differing results. Reports are kept outside the immutable package.

Without --replay-predecessors, original archive/source hashes are still checked,
but historical computation is explicitly marked NOT_REQUESTED. Per-job timeouts
are configurable with --timeout-seconds and are always inconclusive. The
verifier does not formalize the written proofs or external source theorems.

## Layout

- work54/notes/: complete local/global proofs, arithmetic consequences,
  reduced reciprocity, and adversarial self-review.
- work54/computations/: four portable exact programs, no proprietary dependency.
- work54/verification/: frozen finite reference outputs and startup replay.
- work54/source_records/: classical source translation and pinned input hashes.
- work54/GAP_LEDGER.md and CONTINUE_HERE.md: current gaps and next-block contract.

PACKAGE_SHA256SUMS.txt covers every packaged payload file except itself. The
separate final release audit checks the ZIP CRC, exact member list and hashes.
