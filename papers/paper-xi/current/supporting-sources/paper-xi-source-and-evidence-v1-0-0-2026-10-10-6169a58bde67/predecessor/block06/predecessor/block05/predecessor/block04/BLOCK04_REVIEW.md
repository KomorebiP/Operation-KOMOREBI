# Paper XI — Publication Block 04 review

**Checkpoint:** P11-PUB-B04. **Date:** 10 October 2026. **Outcome:** a completed working research continuation, not final approval of all Paper XI readers and not closure of Conjecture 66.

## New publication material

The independently editable Part III, *Conductors, Native Markings, and the Equal-Capacity Boundary*, has **23 PDF pages**, **nine main sections (22–30)** and **13 explicit ordinary proof bodies**. The cumulative v0.4.0 reader has **77 pages**: two new map pages, the preserved 33-page Part I, the preserved 19-page Part II and the new Part III. The inherited core monograph, visual guide and Lean guide remain unchanged at 109/51/234 pages.

The ordinary proof count is a document-structure count. It is not a count of newly discovered theorems or fresh Lean results. Some arguments reconstruct classical finite mathematics, some expand inherited restricted deductions, and the conditional correction procedures develop the previous linear-defect observation.

## Mathematical progress

### Conductor normalization and candidate filters

The paper now distinguishes standard Swan conductor, ordinary Artin conductor, epsilon exponent for a specified additive character, and self-pair conductor. For the original rank-nine source the standard values are 24 and 33. End(rho) has Swan 152 and ordinary conductor 232, but its epsilon exponent for the character trivial on p is **151**, because it has dimension 81. The trace-zero adjoint has dimension 80 and corresponding exponent 152. The equality of AP delta with 152 in the torsion-one example does not identify these definitions.

The principal-order derivation retains the actual period, leading level and grade dimension. A source of rank n and Swan w necessarily requires n/gcd(n,w) dividing the principal period e. At rank nine this leaves (e,r)=(3,8) and (9,24). Source wild irreducibility independently excludes nontrivial unramified self twists.

The source self-pair calculation is expanded from its two independent projective quotients: one trivial character, eight break-one characters, and 72 break-two characters. The resulting ordinary self-pair conductor is 232. In the proposed period-nine family, the **actual order certificate** gives self-pair conductor 2c+224. Thus critical level 10 is excluded and critical level 4 passes. This is a necessary comparison, not construction of a corrected stratum, type occurrence, or H5.

### Equal arithmetic invariants do not force capacity

The floor/ceiling calculation is reduced to the exact parity identity

`2 ceil(nu/2) + 1_(nu even) = nu + 1`.

Consequently the self-pair conductor depends on a weighted sum that does not retain the Heisenberg quotient dimension separately. The full and skipped rank-eight profiles at (h1,h2,h3)=(1,3,5) share standard conductor 68, torsion number 1 and self-pair conductor 342, yet have quotient dimensions **6 and 4**. Their grade indices are 133 and 134. The arithmetic existence of the skipped profile retains its inherited ordinary proof and refinement inputs; this block freshly checks the grade consequences, not a new skipped-profile matrix build.

### Source-defined induction is not native occurrence

The positive-characteristic branch is reconciled through its original degree-nine inducing field, the unramified F81 base extension, the two cyclic cubic stages, classical tower independence, tame descent and central normalization. The full inducing character and its unramified factor remain in the input. The fixed-center descent is unique in the rank-nine/order-four fibre because the ninth-power map is bijective there.

The selected BH99, Aubert–Plymen and BH13 primary statements were checked at their exact hypotheses. BH99's original characteristic-zero restriction is not silently removed. BH13's characteristic note supplies the cited interface to Henniart–Lemaire. **The complete HL11 PDF could not be retrieved**, so its detailed III.2/III.3 statements retain inherited audit status. Pair conductor preservation is not promoted to equality of full pair epsilon factors.

### Full native markings and explicit finite corrections

The finite extension criterion preserves the center, generator squares and commutators. The dihedral/quaternion example retains both finite subgroups inside the common complex scalar pushout. A full section still requires all of its prescribed product relations.

For a freely chosen quadratic embedding, strict capacity admits either source Arf type, while equal capacity requires matching Arf invariants. At rank eight the full profile has exactly six dimensions, so this equality is unavoidable **when an independent native host refinement is required**. The transported scalar-pushout contract has a different quantifier and retains its positive attachment statement.

The manuscript then gives an explicit correction. The discrepancy between two refinements with the same polar form is B(a,-). If q(a)=0, composing with the transvection T_a corrects the embedding. It fixes any subspace on which the original defect vanished, and remains equivariant when the supplied actions preserve both refinements and the initial map is equivariant.

A second conditional correction addresses genuine actions on the finite extensions. Their discrepancy is a cocycle in Hom(W,F2). For an odd-order action group, summing the discrepancy over the group removes it. An even-order counterexample is retained. These corrections do **not** construct initial arithmetic actions, authorize changing fixed lifts, or choose the required honest phase operators.

## Fresh verification

Three suites passed through the delivered runner in the working checkpoint:

| Gate | Scope |
|---|---|
| Block04 exact models | 23 unittest methods. Conductor conventions, grade identities, GF81 projective characters, full/skipped profiles, central extensions, all 720 labeled symplectic bases in dimension four, Arf/defect formulas through dimension six, and action controls. |
| Block03 exact models | 15 inherited methods replayed. |
| Block01 exact models | 12 inherited methods replayed. |

These are not all nine historical Block03 gates. The seven additional historical arithmetic executions, direct rank-nine/rank-eight matrix scripts, and a Lean compiler were **not** run by this block's replay. All successes and source hashes are recorded per gate. Counts are not a measure of conjecture completion.

The complete Block01 baseline passed its 8,600-entry integrity manifest again. The compact Block03 predecessor passed its 352-entry manifest, and all five queued source hashes matched. Both predecessor source trees are preserved, not rewritten to hide amendments.

## Publication verification

All **25 new pages** were rendered and reviewed on seven contact sheets. Eight selected Part III pages were inspected individually, including the corrected equation-label page at 160 dpi. The final build has no warning, overfull-box or underfull-box diagnostics. Automated bounds checks found no out-of-page text or replacement glyphs in the new pages.

The cumulative reader has **149 bookmarks and 208 links**. Every merged destination was compared with the source destination after resolving named links. All **52 preserved Part I and Part II pages** retain identical extracted text and 100-dpi rendered appearance, with the same link counts. These are preservation checks, not a fresh mathematical review of every old page.

A fresh copy of the source directory rebuilt both the continuation and the cumulative reader. Every page's text and rendered appearance matched. **Strict binary PDF identity failed** for both artifacts. No unsupported claim that only trailer IDs differ is made.

## Failures, repairs and remaining limits

An attempted streaming container session was unavailable. Ordinary bounded tool calls were used instead. Container network requests failed DNS, while web PDF screenshots succeeded for the selected primary statements. Repeated HL11 full-PDF requests failed; the failed access remains an audit boundary.

The initial manuscript build had one overfull bibliography line and several underfull text/table diagnostics. The table was set with ragged columns, the bibliography was reflowed, and one paragraph was clarified. A visual pass also found two globally numbered equations inconsistent with the section-numbered scheme. They are now (23.4a) and (23.4b). The final build is clean. No mathematical result was altered to force a numerical pass.

The replay metadata adapter initially displayed null counts for the two older JSON schemas despite successful test executions. It now reads their actual `methods` and `unittest_methods` fields and verifies the expected counts. The delivered driver was rerun successfully.

The complete editable Block02 working archive and the terminal v0.45 build receipt remain unrecovered. No fresh Lean/Lake compilation or external peer review occurred. The actual fixed native rank-eight refinement and honest phases are not computed by this block.

## Continuity and next block

The ledger now has **23 stable task IDs**, retaining all previous IDs. The two new tasks separately track the actual fixed native-marking certificate and the completed conditional finite correction theory. The selected conductor/marking audits are recorded without closing their stronger arithmetic endpoints.

Block05 starts with the dedicated conjecture visual companion against the new claim map. The exact arithmetic sources and original contract are hash-pinned in the next-source queue. Synchronization of the main, visual and Lean readers follows. General realization, same-candidate H5 and corrected-character occurrence remain separate obligations.

Archive-specific hashes, CRC results and fresh-extraction replay records accompany the delivered exports separately, avoiding a circular hash of the archive itself.
