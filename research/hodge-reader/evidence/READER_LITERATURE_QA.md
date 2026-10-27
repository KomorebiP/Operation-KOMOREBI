# Reader and guide literature QA — 9 October 2026

## Current disposition

**Visual guide source scope: PASS for the reviewed wording and pinned revision. Full-page visual review: PASS for physical pages 13–24 and source page 36 of that revision.** This is a bounded release QA result. It does not certify every proof, every figure or every external paper.

**Reader source scope: PASS for selected statements against the checked source contracts. Reader full-page visual review: PASS for physical pages 103–126 of the final 126-page revision, including Appendix D and bibliography.** This is a bounded source/layout QA result, not a blanket proof approval.

## Reviewed revision and evidence

| File | SHA-256 |
|---|---|
| pdf/Komorebi_Hodge_Visual_Guide_v1.0.pdf | a413b1a74052a91d52bc604972404c3041148e98dbebb0e40977ac46b1c1e30d |
| visual/main.tex | 729593d6a780e2ff9e28809bc1e849359b1c3cdefb4d3a8d605c3bb5b4d8062c |
| evidence/literature/CHECKED_SOURCES.md | 6841c6640af0abb0e120d4bf31a0956339c1f452b8490232a751711471259482 |
| evidence/literature/source_contracts.json | fced558ffe79b774b1f7849c410ae7651da35e77273f64bf1a1ff44906ccdd71 |

The guide source is wholly in visual/main.tex; no separate body.tex exists. Every spread's prose and the source page were read against the literature contracts. Assigned physical pages 13–24 correspond to printed spreads 12–23. Source page 36 is printed page 35.

All twelve assigned pages and the source page were inspected as separate full-page images with original detail. After root identified a PATH renderer override, a final full-page pass used the genuine system /usr/bin/pdftoppm version 24.02.0 at 150 dpi on an immutable snapshot with the same final PDF hash. Every assigned page and source page was reinspected individually, under tmp/pdfs/hodge_qa/literature_system/. The bounded visual PASS was reconfirmed. Earlier layout findings/corrections remain historical; the current disposition relies on the system-rendered immutable revision. Exact image and snapshot pins are in READER_LITERATURE_QA_pins.json.

## Source-contract checks

| Guide statements | Result and limit |
|---|---|
| Cover and spreads 1–3: rational HC, projectivity, rational combinations, integral failure | Consistent with Clay/Deligne. No claim that a pictured gap actually exists or that a special fourfold proves general HC. |
| Spreads 4–10: projectors, positive frames, supports, degree shifts, inverse correspondences | Geometric hypotheses remain explicit. Naming an operator, numerical positivity or a linear inverse is not presented as an algebraic kernel construction. This is not a new complete audit of historical general infrastructure. |
| Spreads 11–12 and 23: balance, rational orbits, conductor | Compatible with the primary Fermat dictionary and project arithmetic. A complex line is distinguished from the rational orbit. |
| Spreads 13–14: dyadic certificates and classification | Revised wording separates the exact displayed identity and enumeration through 128 from the unresolved all-degree write-up obligation. Earlier inherited universal theorem wording is removed. |
| Spread 15: degree-33 Klein–Delsarte route | Labelled manuscript geometry and tied to project evidence. This check does not newly audit Beauville–Donagi or every step of the historical cubic proof. |
| Spreads 16–18: K23 and missing Chow arrow | Hodge compatibility and sign checks do not claim to construct the Chow map or universal mixed-prime grammar. This respects the half-twist source contract. |
| Spreads 19–22: carrier geometry and lowest-weight lifting | Normality and resolution steps are separate from arithmetic; a resolution is not assumed Fano. External inputs match BDPP Theorem 2.6, Deligne II Corollary 3.2.17/pure semisimplicity, and Arapura Corollary 4.2. Exact hypotheses remain in reader/source contracts. |
| Spreads 24–25: concatenation and pair removal | Matches Aoki Theorem 1-4. No arbitrary tensor cancellation, unknown-motive cancellation or general HC theorem for the intermediate 52-fold is assumed. |
| Spreads 28–32: constructor obstruction and surfaces | A failed constructor is not a Hodge counterexample. Defining equations are attributed to Aoki; this edition's determinant/period computation is separate. Singular-cycle allowance matches Villaflor without removing complete-intersection/nonzero-coefficient obligations. |
| Spreads 33–34: Weil audit and overall status | Negative construction audit stays local. No nonalgebraicity or Hodge counterexample is asserted. Finite PASS is not promoted to universal proof. |
| Source page 36 | Arapura v1 and Villaflor v5 pinned. Aoki's present full-text access distinguished from inherited incomplete access. Deligne correctly II, with numbered leaves; exact BDPP version/theorem included. |

The guide does not assert the unavailable exact Brosnan Proposition 4 or silently upgrade Kang's unextracted original proof. Access limits, Markman's completed scope and the narrow secant-preprint failure remain governed by the full source contracts.

## Full-page inspection and corrections

The initial guide PDF had SHA-256 080ea925038aebd99f6b202066b1d137a5f7fb16a474502bffd7491864d05961. Its embedded figures had clipping; each finding was reported immediately. The author rebuilt after correcting figure margins. Every assigned page was then inspected again from the fresh current renders.

| Physical page | Spread | Initial finding | Current result |
|---|---:|---|---|
| 13 | 12 | Clean | PASS |
| 14 | 13 | Layout clean; universal-status wording correction needed | PASS; distinction corrected |
| 15 | 14 | Layout clean; all-degree wording correction needed | PASS; write-up obligation explicit |
| 16 | 15 | Clean | PASS |
| 17 | 16 | Clean | PASS |
| 18 | 17 | Sign labels and embedding-axis label clipped | PASS; complete labels |
| 19 | 18 | Clean | PASS |
| 20 | 19 | Matrix row labels and top caption clipped | PASS; complete labels/caption |
| 21 | 20 | Top formula and y-axis label clipped | PASS; full formula/label |
| 22 | 21 | Top/left labels clipped; lower caption overlapped ticks | PASS; margins and spacing repaired |
| 23 | 22 | Top caption clipped; lower summary overlapped ticks | PASS; captions separated |
| 24 | 23 | Orbit labels and top/bottom labels clipped | PASS; full labels |
| 36 | Sources | Exact versions/current-access clarification needed | PASS; corrected text legible |

No remaining clipping, overlap or broken mathematical glyph was found in this bounded set. Headers, page labels, body columns and carry-forward boxes are legible.

The author adopted “recorded arithmetic certificate” on spread 19. A final rerender compared every assigned image against the completed second pass: only physical page 20 changed. That page was inspected again at full resolution and passed; the other twelve inspected images are byte-identical. The final PDF/source/image hashes are repinned.

## Final reader revision and review

The final reader PDF SHA-256 is **9fe0ad078543e195cbf8d1ff7bd0115de23c9adefbb09a7e4b7e48c3a71775ee**, with 126 physical pages. An earlier 125-page snapshot (816b4c77...) was individually reviewed at physical 103–125. After the release PDF changed, an independent immutable copy of the final revision was rendered with genuine system Poppler 24.02.0 at 150 dpi. **Every final physical page103–126 was individually inspected again at original full-page detail**, including the additional flowed page and both bibliography pages125–126. Contact sheets and text extraction were not substituted for visual inspection. No clipping, overlap or missing mathematical glyph was found in this set. Part-divider pages and short chapter continuations are intentional.

The final text was checked for the rational-HC scope; Deligne II locators and pure-Hodge lifting; Arapura/BDPP smooth-resolution hypotheses; Aoki attribution and restricted complementary-pair removal; Villaflor complete-intersection and singular-cycle scope; half-twist existence and missing Chow kernels; Kang and Brosnan source-access limits; Markman's completed scope; the narrow secant eigencharacter comparison; and the retained dyadic publication-status downgrade. These selected statements remain consistent with the pinned contracts.

Appendix D on final physical 124 explicitly distinguishes newly extracted selected leaves from inherited background references. Bibliography on physical 125–126 gives the corrected Deligne II leaves, primary Arapura reproof, Aoki locators, Villaflor v5, exact Markman versions, Brosnan metadata and narrow v5 secant locator. Kang remains an authenticated later attribution with its original exact proof unextracted. Current Fermat preprints are context, without fresh census certification. Broad historical book/paper entries and internal Komorebi manuscripts do not become fresh theorem approvals through their inclusion. The odd-character external analytic nonvanishing leaf does not alone certify the project's conductor reduction or integral-lattice generation.

The page-by-page statuses, image hashes, source-file hashes, snapshot pin and claim-specific boundaries are in **evidence/READER_LITERATURE_LAYOUT_QA.json**. This review does not independently certify all other reader layouts, all figures, every classical theorem, all manifold/correspondence hypotheses, universal constructive coverage or a global Hodge proof.
