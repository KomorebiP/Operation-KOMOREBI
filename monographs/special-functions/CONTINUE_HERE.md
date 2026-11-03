# Continue Special Functions formalization

Current checkpoint: **SF-LEAN-B14**, based on `297118ccc10550500619224d44f168f6491d02e5`.
Start with formalization/Block14/REPORT.md, CLAIM_MAP.json, declarations.json,
SELF_REVIEW.md, IO_MANIFEST.json and evidence/receipt.json. The current
source-bound backlog is formalization/Block14/REMAINING_WORK.md (also JSON).

`lean/CoupledOperator.lean` adds 27 theorem declarations, for 369 registered
names. The registered main H.1 contract is complete: arbitrary-functional
autonomous projections on all zero-constant entire inputs and local analytic
germs are exactly the nonzero multiples of (1,-1) when q=a and r=b. The
projected field is identically zero; no invertible constant complex 2x2
change decouples the operator. Positive scales need not be contractions or
distinct. Canonical U=V for swapped rows is a different statement.

Next executable major target: **Appendix J's elementary exact evaluation
certificate**, lines 44-87 of monograph/sections_v11/coupled_lab_full.tex.
Prove an arbitrary-radius disk-majorant ladder from Q=max(q,r,a,b), a small
disk bound and M(x)<=x*(1+M(Q*x)^2). Then prove the outer-radius tail
B(S)*(R/S)^(2N+3) for S>R>=0 when odd indices 0 through N are retained;
connect the exact rational real interval with the guarded Python API. Reuse
entire continuation and coefficient positivity; do not substitute the local
geometric remainder for this whole-plane certificate. Recheck endpoint and
index conventions, rational arithmetic and API guard behavior before claiming
end-to-end refinement.

Registered F.1-F.3, G.1, guarded G.2 and Block13's named ancillary F contracts
remain complete. Ordinary type convergence is conditional. Remaining F
explanatory wrappers, H's odd-input-only remark and tensor/rank explanations,
I's resolution mechanisms and broad A-E development remain. Preserve G.2's
nonzero-defect guard. No full manuscript-wide claim map or completion
percentage is established. Reading proofreading is a distinct record.

Replay tools/verify_coupled_operator.py with Lean 4.34.0-rc2 and Mathlib
aeb72f1e9981b6d35b426b16dca7759be3e7ba06 in a new external directory.
All 57 steps pass: fourteen compilations/audits/kernel replays, 330 fresh
theorem axiom audits, four rejection controls and one positive fixture.
Inherited finite-core evidence covers 39 names. Mathlib imports are cached.
Review provenance is self-review. Formal I/O records 50 inputs, 58 raw
packaged outputs, fourteen unbundled objects and 33 staging copies; 26
assessment inputs/two outputs and unaccepted development diagnostics are
separate. No input changed during the accepted replay.

The explicit-polynomial fiber route and local-to-entire identity-principle
bridge succeeded. The interpolation/derivative and tensor routes are deferred
for variants needing them; they are not refuted or exhausted. No delegated
or delayed mathematical run remains. Preserve all fourteen blocks, dated
guides, manuscript sources, PDFs and frozen imported bundle receipts. Root
archive manifests remain older release snapshots. Live website scope comes
from maintained status; current guidance resolves to repository files.
