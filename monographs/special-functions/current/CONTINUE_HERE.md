# Continue Special Functions formalization

Current checkpoint: **SF-LEAN-B17**, mathematical base `200a2798532028f863f923028cb0ead95563975a`,
editorial parent `0eae1fe6a4bf55db27af69ef40b405643aa2e5a9`. Start with formalization/Block17/CLOSEOUT.md,
REPORT.md, CLAIM_MAP.json, declarations.json, SELF_REVIEW.md, IO_MANIFEST.json
and evidence/receipt.json. The exact backlog is REMAINING_WORK.md/.json there.
Paths here are relative to monographs/special-functions/ unless stated otherwise.

lean/CoupledGuardedMajorant.lean adds 30 theorems, for 465 registered names.
The exact rational first-small ladder and guarded reverse fold are proved:
success supplies trace length<=budget, adequate fuel and the proved majorant
value. Successful results bound actual complex functions and enclose real
components using the Block16 array polynomial. Step and post-update size
errors stay errors. The abstract wrapper preserves scale/radius/resource
validation order. This is an algorithm specification, not full Python refinement.

**Next: typed certified-evaluation result and source correspondence.** Compose
arrayPolynomial with checkedMajorant into metadata, tail and U/V endpoint
fields; prove every successful result encloses both actual functions and
preserves last_index=N, N+1 coefficients and exponent 2N+3. Then connect the
actual certified_evaluation call path with explicit interpreter, Fraction,
stdlib, runtime type/exception and mutation assumptions. None resource inputs
are abstract invalid tags; no Python runtime type classifier is proved.

Preserve critical source cases: radius zero skips resource checks after valid
scales/radius; nonzero steps validate before positive bits. Radius one needs
a step. The seed for radius<1 is not bit-checked. Checks follow each reverse
update, not just the final value. Q=1/2,R=2 records [2,1] and gives 500/81;
forward folding gives the wrong 757/81. Adequate mathematical fuel does not
guarantee fixed resource limits succeed. Analytic inputs retain contractions
and x>=0,S>x. No error is treated as a weaker certificate.

Registered F.1-F.3, G.1, guarded G.2, named ancillary F, main H.1 and J's
mathematical evaluation/normalization/finite-array contracts remain complete.
Other J degree/denominator/symmetry, F/H correspondence, I and A-E remain.
Ordinary type convergence is conditional; G.2's nonzero-defect guard remains.
No full manuscript claim map or completion percentage is established.

Replay tools/verify_coupled_guarded_majorant.py with Lean 4.34.0-rc2 and Mathlib
aeb72f1e9981b6d35b426b16dca7759be3e7ba06 in a new external directory.
All 66 steps pass: seventeen compilations/audits/kernel replays, 426 fresh
coupled axiom audits, four rejection controls and one positive fixture.
39 finite-core names retain inherited evidence; Mathlib is cached. Review is
self-review. Formal I/O: 59 inputs, 67 packaged outputs, seventeen objects,
39 staging copies. Assessment: 37 inputs/two outputs. Development and preflight
source/log pairs are diagnostics; Python sources are not trusted proof leaves.

Trace and guarded-fold routes succeeded; a direct while-state invariant is
deferred for source-language refinement, not exhausted. No delegation or
delayed mathematical run remains. Preserve all seventeen blocks, dated guides,
manuscripts, Python, PDFs and imported parent guidance. Only current/ guidance
is maintained; root archive manifests and parent guides are historical. Reading
proofreading remains separate from proof review and formalization.
