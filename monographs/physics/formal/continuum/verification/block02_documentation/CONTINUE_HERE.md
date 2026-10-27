# Continue Komorebi Physics Lean v0.2.0

Read AGENTS.md, README.md, STATUS.md, docs/SOURCE_MAP.md, docs/BLOCK_02_PROOF_GUIDE.md, docs/FULL_EDITION_ROADMAP.md, the declaration inventory, and verification/final/report.json before editing.

## Verified starting point

- Full 550-page physics master included; source SHA-256 `ea289c7c1bd2090296e4d436c9ef38b617066becc40cd33c44507f1386a61bc0`.
- Fresh cumulative PASS: 127 active theorems, 160 audited named declarations, 10 mathematical modules, nine rejected invalid controls.
- Counts: 51 Block 02 new + 37 Block 01 new + 39 preserved Paper VII.
- All seven Block 01 mathematical modules are byte-identical; preservation is checked by the verifier.
- Three new modules: Deformation, MovingAtlas, DeformationExamples.
- Runtime: Lean 4.34.0-rc2; Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

## Restore and rerun

Restore the seven Lean_Offline_0N.zip parts with runtime_restore_support/assemble.py when no matching kit exists. They are Zstandard chunks, not XZ. Use the pinned kit and run the cumulative verifier. Historical logs alone never count as a fresh run.

In the production session the kit was at `/mnt/data/lean_parts/Komorebi_Portable_Lean_4.34.0-rc2`. That is a historical path, not a promise that it exists in a new chat. The source package does not bundle the multi-gigabyte kit.

The v0.2.0 verifier uses bounded module-by-module axiom audits because a single large baseline audit hit an outer command deadline. All ten audit batches must pass and exactly match the complete declaration inventory. Preserve the failure history and do not count partial runs.

## Next literal target

Read physical master pages 23–24, printed pages 10–11, and page 21 for the refinement-sequent cross-reference. Chapter 4.1 has state-dependent skew flow (4.1)–(4.5); Chapter 4.3 has the associative refinement tower (4.16)–(4.22). These can reuse the now-checked pointwise derivative and coarsening interfaces. Prove actual derivatives, not fields asserting the desired balances.

Then formalize Chapter 4.2 mixed-state unitary transfer (4.6)–(4.15). Read the page image: the overbar in (4.14) matters. Start with finite matrices or impose complete trace-class/domain hypotheses. Prove the conjugation/cyclicity identity and the actual derivative of Tr(P rho); do not assume antisymmetry or encode the desired law in a structure.

Chapter 3's physical-unit, variational and asymptotic sequents are not certified merely because Chapters 2.5–2.6 are mapped. Record their status separately. Read later chapters before deciding subsequent target order.

## Boundaries to preserve

The automatic inverse-derivative theorem uses a complete normed algebra and invertibility at the base point. It does not assume an inverse derivative. The more general inverse-pair helper exposes its own separate regularity inputs. Do not conflate those interfaces.

The moving Hilbert-space layer uses bounded, everywhere-defined complex-linear maps and real-time operator-norm derivatives. Both unitary identities are explicit where needed. Generic invertible similarity does not preserve self-adjointness; the exact shear counterexample is active.

The derivative formulas work with fixed reference projectors. To identify the references literally with their values at time zero, supply initial normalization such as U(0)=I. No flow-existence theorem, strong-only differentiability extension, countable sum, unbounded domain, continuum-gravity closure, or empirical claim has been proved by this release.

Keep the corrected dark-sector branch boundaries in the master. Do not revive superseded additive models. Do not invent a full-edition completion percentage.

## One-line continuation

“Open Komorebi_Physics_Lean_v0.2.0_Checked_Block_02.zip, read CONTINUE_HERE.md and the source map completely, restore and rerun the pinned Lean verifier, then prove the next literal Chapter 4 block while preserving the bounded/unbounded, finite/countable, unitary/similarity, and mathematical/empirical boundaries.”
