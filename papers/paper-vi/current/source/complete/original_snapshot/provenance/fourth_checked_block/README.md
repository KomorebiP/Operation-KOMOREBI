# PRSC VI v0.4.0 — fourth checked block

Author: Komorebi P.

**Three of the last five results closed. Paper VI has 31/33 complete and 2 partial results.** The three original conjectures remain open. This is not full-paper certification.

The fresh pinned Lean build and namespace audit pass: **310 explicit theorem declarations across 42 modules**, with 710 namespace declarations audited. All 54 companion tests and six verifier controls pass.

Completed this block: fractional intertwining (10.3), its semigroup refinement (10.4), and varying-space towers (10.5). Still partial: general nonnormal memory/Laplace self-energy (13.2), and canonical holomorphic naturality (15.1). Both have additional checked supporting proofs.

Start with `manuscript/Paper_VI_Reviewed.pdf`, `REVIEW.md` and `THEOREM_LEDGER.md`. Reproduce with `python3 verification/verify.py` using the pinned toolchain and Python requirements. `verification/verification_status.json` is the authoritative report. Supporting declarations, audited definitions and manuscript results are different counting units. The older numerical comparison is retained evidence; the numerical study was not repeated this block.
