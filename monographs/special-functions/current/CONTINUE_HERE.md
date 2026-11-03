# Continue Special Functions formalization

Current checkpoint: **SF-LEAN-B15**, based on `f5b2651f182244afd4d979d9aed386e45c898381`.
Start with formalization/Block15/CLOSEOUT.md, REPORT.md, CLAIM_MAP.json, declarations.json,
SELF_REVIEW.md, IO_MANIFEST.json and evidence/receipt.json. The source-bound
backlog is formalization/Block15/REMAINING_WORK.md (also JSON).

`lean/CoupledEvaluation.lean` adds 36 theorem declarations, for 405 registered
names. The registered J mathematical certificate is complete: arbitrary-radius
finite majorants with adequate-fuel existence, actual complex outer-radius
Taylor error, real enclosures and exact rational endpoint semantics for
rational scale/radius data. Last
index N retains N+1 coefficients and leaves degree 2N+3 first omitted. For
the unequal worked pair at R=1, S=2, N=30 the error is <1.6e-13 throughout
the unit disk. This is 31 retained coefficients through degree 61.

Next executable target: **J implementation correspondence**, beginning with
the factorial-normalized derivative arrays in research/coupled_lab.py and
ordinary_taylor_coefficients in research/family_lab.py. Prove their relation
to RationalScales.coefficients and RationalScales.polynomial for every index.
Then relate the Python disk_majorant while-loop/reverse fold to the proved
fuel model, preserve max_steps/max_bits failures and validate the returned
certified_evaluation dictionary's exact endpoints. The zero-radius early
return precedes resource validation in the current source; preserve exact
guard order. Inputs must be strict contractions, x>=0 and S>x. A matching
formula or bounded test run is not a full Python-to-Lean refinement proof.
Additional J degree, denominator-clearing and symmetry wrappers remain to map.

Registered F.1-F.3, G.1, guarded G.2, named ancillary F and main H.1 contracts
remain complete. Ordinary type convergence is conditional. Other F/H
correspondence, I's resolution certificates and broad A-E analytic chapters
remain. Preserve G.2's nonzero-defect guard. No full manuscript-wide claim
map or completion percentage is established. Reading proofreading is separate.

Replay tools/verify_coupled_evaluation.py with Lean 4.34.0-rc2 and Mathlib
aeb72f1e9981b6d35b426b16dca7759be3e7ba06 in a new external directory.
All 60 steps pass: fifteen compilations/audits/kernel replays, 366 fresh
theorem axiom audits, four rejection controls and one positive fixture.
Inherited finite-core evidence covers 39 names. Mathlib imports are cached.
Review provenance is self-review. Formal I/O records 53 inputs, 61 raw
packaged outputs, fifteen unbundled objects and 35 staging copies; 31
assessment inputs/two outputs and unaccepted diagnostics are separate.
Python source assessment files are not formal proof leaves. No input changed
during the accepted replay.

The positive-series tail, exact-seed ladder and rational recurrence routes
succeeded. Cauchy-tail and unit-seeded alternatives remain deferred for other
regimes; they are not exhausted. No delegated or delayed mathematical run
remains. Preserve all fifteen blocks, dated guides, manuscripts, Python
sources, PDFs and frozen imported receipts. Root archive manifests are older
snapshots. Live website scope comes from maintained status; current guidance
resolves to repository files.
