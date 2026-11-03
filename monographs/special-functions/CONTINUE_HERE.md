# Continue Special Functions formalization

Current checkpoint: **SF-LEAN-B11**, based on repository commit
`1c7814ef551709f44547561fe9b04ff7f9faa505`. Start with
`formalization/Block11/REPORT.md`, its claim/declaration maps, self-review,
I/O inventory and source-bound receipt. The dated remaining-work inventory
is `formalization/Block11/REMAINING_WORK.md` (also available as JSON).

`lean/CoupledGrowthTypes.lean` adds 22 theorem declarations. The registered
canonical **F.2 growth contract is complete**: both explicit comparisons,
positive real lower and finite upper types, the actual maximum-modulus radial
exponent limit, and exact limsup order rho. Boundedness/coboundedness and
supremum nonemptiness are supplied explicitly. The registered scope is 273
names, including supporting lemmas and the preceding 251 names. This does
not assert ordinary type convergence or complete all Appendix F.

Next executable target: **Theorem F.3**, lines 354-422 in
`monograph/sections_v11/coupled_growth_full.tex`. Prove scaled liminf/limsup
transport for p(R-1) and pR, including the factors (p(R-1))^rho/R^rho and
vanishing log(R)/R^rho terms. Derive lowerTypeVector>=P(rho)*lowerTypeVector
and upperTypeVector<=P(rho)*upperTypeVector from the proved recurrences.
Dot with the strictly positive left characteristic vector to force equality
coordinatewise. Prove the eigenvalue-one space is one-dimensional, obtain
both Perron proportions and explicit component ratios, then the equivalence
of ordinary type-limit existence for the two components. F.2 supplies the
positive finite real type bounds needed for these operations.

Do not confuse the type ratio with the radial exponent profile. The manuscript
does not assert that ordinary type limits always exist. Continue from the
actual real types and spherical supremum definitions in CoupledGrowthTypes;
retain all real filter boundedness premises during scaled transport.

Further source-mapped work: ancillary Appendix F identities/examples and
parameter structure; H.1 autonomous projections/operator obstruction; I-J
resolution and arbitrary-radius certified-evaluator correspondence; and the
broader multi-tap, arithmetic, sieve, spectral and polyphase development in
A-E. G.1 and guarded G.2 registered contracts are complete. There is no full
manuscript-wide theorem correspondence map or honest completion percentage.
Reading-edition proofreading and finite foundations are distinct evidence.

Replay `tools/verify_coupled_growth_types.py` with Lean 4.34.0-rc2,
Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and a new external
directory. All 48 steps cover eleven coupled modules, freshly axiom-auditing
234 declarations and inheriting the finite core's 39-name evidence. Imported
Mathlib is cached rather than freshly rebuilt/replayed. Review is self-review.

Block11/IO_MANIFEST.json inventories the accepted run's 41 formal inputs, 49 packaged outputs,
eleven unbundled generated objects, 27 staged source copies, and separately
16 remaining-work assessment inputs/two outputs and the preserved resource-
failed first replay with hashes. Source, audits,
controls, verifier, correspondence, status, catalogue and this live file are
updated together. Immutable manifests exclude live guidance. Preserve all
eleven blocks, dated guides, manuscripts and reading PDFs.

The real bounded-filter/logarithmic-squeeze route succeeded. An extended-real
route is deferred for unbounded profiles (infinity conversion unresolved);
a little-o route is deferred for sharper errors (positive-domain transport
untried). Neither is refuted or exhausted. Older reports retain earlier
alternatives. No delegated or delayed runs remain. New proofs belong in a
new block. The root archive manifest remains an older release snapshot.
