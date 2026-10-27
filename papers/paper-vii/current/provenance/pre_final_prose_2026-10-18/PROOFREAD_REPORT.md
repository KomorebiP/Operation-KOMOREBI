# Paper VII — completed proofreading

**Quantum Seeds and Effective Dynamics**  
Komorebi P. · 18 October 2026  
Original project title: *Quantum Seed and Packet Calculus*

This revision completes the proofreading of the traditional paper, visual guide and Lean/evidence guide supplied in the 11 October delivery. It retains the full monograph, all supplements, the integrated visual atlas, editable figure and text sources, formal-source snapshots, earlier computational evidence and recovery archives.

The current reading set is **280 pages**: the traditional monograph has **154**, the visual guide **42**, and the Lean guide **84**. The three copies of each reading PDF—in `papers/`, `publication/pdfs/` and the corresponding `editable/` directory—are synchronized. `EDITION.json` records their exact sizes and SHA-256 hashes.

## Corrections in the traditional paper

All nine mathematical part files were read. Six changes clarify the existing statements or the interpretation of their conclusions:

| Passage | Correction and reason |
|---|---|
| Pairwise circuit-path interference | Declare an arbitrary total order on the finite path set before using an ordered-pair sum. This identifies each unordered pair exactly once. |
| Convergence of short rotations | Define the absolute-value notation for a partition as its mesh, the largest subinterval length. |
| Meaning of the approximate Knill–Laflamme defect | Describe the estimate as controlling deviation of error overlaps from their scalar code form. The former wording also asserted control of nonorthogonality of the original error images, which the estimate does not establish. |
| Fixed-time heat-trace limit | State convergence of the spectral dimensions **defined by the heat-moment ratio**. This matches what the fixed-time trace-norm hypotheses and the proof establish. |
| Einstein infrared coefficient convention | Explain that the volume coefficient includes the sign and normalization displayed separately in Part I's cosmological term. Both action formulas remain unchanged. |
| Several-seed generation in Supplement 3 | Explicitly carry forward the positive-row hypothesis already stated above the paragraph. This is required by the stated equivalence and the corresponding nonempty-row formal endpoints. |

The changes preserve every complete proof body and every extracted mathematical expression in the nine parts. In particular, **all 107 proof bodies and all 1,795 extracted mathematical spans are identical to the retrieved baseline**. The ordered statement inventory remains **147 records**: **142 numbered** and **five unnumbered**. This includes **96 theorem, proposition, lemma or corollary records**. These counts overlap across source branches and do not count independent discoveries.

Seven complete part files remain byte-identical. The two edited parts must equal the retrieved baseline plus a **closed list** of the six prose corrections and two figure-layout changes. The current preservation comparator enforces that complete-file equality; it does not merely permit arbitrary prose changes in those two files. It independently checks proof bodies, mathematical spans and record order. The old comparator is retained in provenance.

A focused mathematical wording review accompanies the edits in `verification/proofread_2026-10-18/FOCUSED_MATHEMATICAL_REVIEW.md`. It records the relevant hypotheses and limitations rather than treating an editorial correction as a new theorem. For example, identical normalized errors can have zero Knill–Laflamme defect while their original images coincide, so the discarded orthogonality claim was too strong.

## Corrections in the Lean guide

Six guide passages were corrected:

- The recovery scale is described as a nonnegative scale **independent of the supported input operator**. It is fixed for the code already chosen; no independence across arbitrary codes is asserted.
- The multiple-seed discussion explicitly continues with a **nonempty row index type**.
- The lattice discussion names the **quadratic upper bound for sine squared**, matching the displayed formal ingredient.
- `Fin n` is described as the type of **natural numbers smaller than** `n`.
- “Data consist” replaces the grammatical error.
- A reference to two constructions replaces the mistaken reference to two chapters.

Two inline Lean binder examples also now use the appropriate monospaced text wrapper, so their braces render without literal escape backslashes. This is a typesetting correction; the displayed Lean syntax is unchanged.

The guide retains all **67 exact contiguous raw source excerpts** and the active formal sources. The static reconciliation covers **19 scoped finite manuscript items**, **323 named theorem declarations in 25 active modules**, **nine dependency pins** and **six separately audited constructed objects**. These are different units and are not added into a theorem-coverage total.

One inherited Lean source comment uses the older “code-independent” wording. The formal quantifiers are correct. To preserve the archived formal source exactly, the comment erratum is recorded in the focused review and corrected in the current guide rather than silently rewriting the inherited source snapshot.

The current source/static check passed. A fresh run of the **16 verifier-software regression tests** also passed. Those tests validate the verification software; they are not Lean proofs or an additional scientific result.

## Corrections in the visual guide and atlas

The 40 worked visual pages are retained. Their current bodies, titles and routes match the integrated atlas, and all **38 duplicated vector-plate sources** agree. The supplied generator sources reflect the same figure corrections.

| Location | Correction |
|---|---|
| V29, the S3 example | Replace the scalar dimension label `2 ⊗ 2 = 4` with `2 · 2 = 4`. This is an intentional notation correction, distinct from the unchanged mathematical spans in the traditional parts. |
| V31 | Specify conjugation by the parity operator: diagonal matrices have order zero and off-diagonal matrices have order one modulo two. |
| V13 | Refer to “the displayed small arrays” instead of an incorrect count of four. |
| V16 | Reposition the dephasing label so it is separated from the adjacent matrix entry. |
| V27 | Shorten the transfer arrow at both ends so it no longer touches the endpoint digits. |
| V38 | Reduce the rotated “new coordinate” label locally to keep it clear. |

All 16 intra-guide V-page references resolve. The final crosswalk retains **80 traditional reading targets** for the 40 visual pages. The Lean crosswalk retains **110 locators**, including 12 supplement endpoints. Both distinguish actual printed page labels from physical PDF positions; no assumed cover offset is used.

## Bibliography and page layout

Six bibliography title fields now protect the existing capitalization of C in “C star algebras,” Heisenberg, Schrieffer and Wolff, Euclidean and Green, and the Roman volume numerals I and II. All **29 bibliography keys** and all nonbrace characters are unchanged. An isolated BibTeX check passed, and the final bibliography was rebuilt. This was a capitalization correction, not an external audit of every citation's bibliographic facts.

Figure 28, the Kato-transport sphere, had been deferred into the middle of Theorem II.6.7. A local float barrier now keeps the figure before the curvature subsection. Reducing that figure's width from 0.62 to 0.58 of the text width leaves room for the theorem, proof, final equation and end-of-proof marker together on physical page 54. Page 55 begins cleanly with the following corollary. The figure remains readable, and no proof-body edit was needed. Two isolated subsection headings—Projector curvature and Quantum dynamical semigroups—are now kept with their opening statements by narrow wrapper-level spacing guards. The protected part files are unaffected by those guards. Their proper placement adds one page to the traditional volume.

### Retained minor pagination observations

The final review records three nonblocking flow observations in the traditional PDF: subsection I.7.2, “Kraus transfer,” is at the bottom of physical page 24 with its body on page 25; subsection I.11.2, “One- and two-dimensional plateaus,” is at the bottom of page 33 with its figure on page 34; and Theorem I.10.1 continues from page 30 to page 31 with Figure 16 above the continuation. All headings, statements, figures, equations and proof markers are present and readable. These are recorded pagination observations, not missing text, clipping, glyph failures or mathematical changes. They were retained after the final review to avoid further broad reflow of the complete reading set.

## Font and build repairs

The retrieved 11 October archive had removed standalone font files while its source still expected relative font files. The active styles now accept those relative files if present and otherwise select installed fonts explicitly.

An intermediate fallback based on face names selected a mixture of OpenType and older Type1 faces. This caused PDF-driver errors and, in one successfully generated candidate, a missing bold capital A that extracted as U+0357. Visual review caught that defect even though the final TeX log was clean. That candidate failed acceptance.

The final fallback selects the exact installed **OpenType P052 and Nimbus Sans files** for regular, bold, italic and bold italic. All eight faces passed rendered and extracted full-alphabet checks. The established font families and sans scale remain. No fonts or dependencies were installed, and no standalone font binaries were added to the package.

Each builder runs four XeLaTeX reference passes without emitting intermediate PDFs, invokes BibTeX when needed, and emits the final PDF once through xdvipdfmx. The isolated build, optional output directory, final diagnostic checks and atomic output behavior remain. Failed intermediate candidates and their causes are retained as diagnostic history, separately from accepted final PDF evidence.

## Final validation

The authoritative current acceptance record is `verification/proofread_2026-10-18/RELEASE_VALIDATION.json`. Its source and report pins identify the exact reviewed release. Supporting records distinguish:

1. Complete source proofreading and the focused review of the six mathematical wording changes.
2. Closed-list source preservation, static formal-source/excerpt reconciliation, and verifier-software tests.
3. Fresh builds of all three PDFs, final diagnostic checks and synchronized PDF copies.
4. Mechanical preflight of every page: text bounds, known invalid character mappings, internal links, bookmarks and final typesetting diagnostics.
5. Hash-pinned visual review covering the complete final reading set, with the traditional volume divided between the mathematical text and atlas/bibliography reviewers.
6. An isolated rebuild from the packaged sources, comparing exact extracted text and page counts against the shipped PDFs. Byte identity is recorded separately.
7. Actual printed/physical page navigation, package metadata and report/source-pin consistency.
8. Preservation of the retrieved source trees and a size/SHA-256 manifest for every shipped file, followed by ZIP integrity verification.

Generating a page image is not itself a manual review; the final visual record names the inspected ranges. PDF and source checks do not constitute a new mathematical correctness certificate.

## What remains inherited or open

**No fresh Lean compiler or kernel run was performed.** Lean, Lake and Elan are absent from the review environment, and the retrieved archive does not include the portable compiler kit or compiled interfaces needed for the pinned replay. The compiler and axiom records remain the inherited **6 September 2026 v0.6.0** evidence, pinned to **Lean 4.34.0-rc2** and **Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06**.

The numerical, rational, symbolic and deterministic-plate reports under `verification/monograph_checks/` retain their **9 October** date and exact earlier scope. The scientific symbolic suites were not rerun in this proofreading; no new run is inferred from a preserved PASS record. Earlier source/PDF pins remain historical and have not been silently rebound to revised files.

The five previously open physical continuum targets remain open:

- Anomaly-free refinement.
- Uniform Feshbach control for the proposed tower.
- Lorentzian reconstruction.
- An Einstein infrared limit.
- A positive physical massless spin-two sector.

The finite, bounded and explicitly conditional statements retain their individual hypotheses. This revision does not claim an interacting continuum field theory, unbounded gravitational closure, a physical massless spin-two construction, or a new global novelty result.

## Preservation and use

All **784 files** in the retrieved source trees, both retained recovery ZIPs, and the **13 comparison-baseline files** match the actual October 11 delivery. This includes **121 inherited `.lean` files** across the retained branches. That comparison does not claim that the earlier archives were untouched by October 11's font-removal step.

Original versions of edited current sources, prior reading PDFs, metadata and active verification scripts are preserved under `provenance/pre_proofread_2026-10-18/`. The current root README identifies the reading set, dependencies and read-only verification commands. The exact correction ledger, current source diff, review records and final build logs are supplied with the package.
