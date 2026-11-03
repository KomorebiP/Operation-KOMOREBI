# Continue Special Functions formalization

Current checkpoint: **SF-LEAN-B12**, based on `c6c529a58b70ebdedac1d0a7dc232153688735b3`.
Start with formalization/Block12/REPORT.md, CLAIM_MAP.json, declarations.json,
SELF_REVIEW.md, IO_MANIFEST.json and evidence/receipt.json. The current
source-bound backlog is formalization/Block12/REMAINING_WORK.md (also JSON).

`lean/CoupledTypeProportions.lean` adds 26 theorem declarations. The registered
canonical **F.3 contract is complete**: positive ordered scalar proportions
of both type vectors, both explicit component ratios, equivalence of ordinary
component type-limit existence and the conditional vector limit. Actual
maximum-modulus profiles are identified. The registered scope is **299 names**,
including supporting lemmas. F.1, F.2, G.1 and guarded G.2 remain complete
within their registered scopes. Ordinary type convergence is not asserted
unconditionally, nor is a ratio limit under persistent type oscillations.

Next executable target: **ancillary Appendix F**, lines 425 onward of
monograph/sections_v11/coupled_growth_full.tex. Prove exactly U=V iff the
unordered scale pairs coincide, equivalently (q=a and r=b) or (q=b and r=a)
under positive strict contractions. Necessity can use the degree-three and
degree-five coefficient identities to recover equal products and square sums.
Sufficiency can use the existing global scalar representation or canonical
uniqueness. Retain global complex function equality, not just finite jets.
Then establish the q=r=a=b=1/2 sinh closed form and remaining example/parameter
wrappers. Check source definitions before adding a new contract.

Further work: H.1 all-analytic-input autonomous projections and operator
decoupling obstruction; I-J analytic resolution and arbitrary-radius certified
evaluation/Python refinement; full multi-tap, arithmetic, sieve, spectral and
polyphase development in A-E. No full manuscript-wide correspondence map or
completion percentage is established. Reading proofreading remains distinct.

Replay tools/verify_coupled_type_proportions.py with Lean 4.34.0-rc2 and
Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06, in a new external directory.
All 51 steps pass: twelve coupled module compilations/audits/kernel replays,
260 fresh theorem axiom audits, four rejection controls and one positive
fixture. Inherited finite core evidence covers 39 names. Imported Mathlib
is cached rather than freshly rebuilt/replayed. Review provenance: self-review.

Actual I/O records 44 formal inputs, 52 packaged outputs, twelve unbundled
objects and 29 staging copies; twenty source-assessment inputs/two outputs
are separate. Earlier failed Block11 execution is preserved unchanged.
Source, controls, maps, evidence, status, catalogue and dated guide are updated
together. The website reading index now takes its formal scope from maintained
status instead of a hardcoded historical count. The subject hub links the
current guide and repository additions without rewriting imported ZIP receipts.

Primary epsilon-envelope route succeeded. Exact scaled-liminf equalities are
deferred for reuse if needed; joint-cluster route is deferred because extrema
must not be assumed simultaneous. Neither alternative is refuted or exhausted.
No delegated or delayed research run remains. Preserve all twelve blocks,
dated guides, manuscript sources and reading PDFs. New proofs belong in a
new block. Root archive manifests remain earlier release snapshots.

Publication: the complete Block12 history through
`c6e93f265bbfed4924ccd41a6cb161b90745d204` is on the GitHub branch
`codex/special-functions-local-analysis`. The native Git client has no saved
GitHub credentials in this checkout. The connected GitHub/Composio tools can
publish exact Git trees and commits, including original author/committer dates;
verify every returned hash and read main before a fast-forward ref update.
Large merge trees may need bottom-up immediate subtree creation. The `.io`
reader site deploys from main through `.github/workflows/reader-site.yml`.
After a merge, run the catalogue generator before its check: sparse checkout
can omit generated root README files until the generator materializes them.
