# Independent publication integrity review

Status: **PASS within the scope below.** No source was edited by this reviewer.

This is an independent publication-preservation and reader-coverage review. It is not a fresh theorem-by-theorem mathematical audit, another Lean compilation, or external literature verification. The accepted compilation remains the evidence for the unchanged formal sources.

## Source and mathematical preservation

- All 153 production modules and three root Lean files are byte-identical to the accepted formal source: 156 of 156 targets.
- Independently recounted 1,693 explicit theorem/lemma declarations; the accepted axiom report has 5,048 exported declarations and no unexpected axioms.
- The declared 44 controls reconcile with 14 positive, 28 compiler-negative, and two policy controls. The public toolchain and mathlib commit agree with the accepted pins.
- All 192 inherited statement/proof environments remain present. The 18 changed environments comprise 17 proofs and one proposition; their mathematical fragments are unchanged. Read-through of those differences found ordinary theorem-reference modernization and one updated formal-status sentence, with no changed hypothesis, conclusion, coefficient, or proof step.
- All inline/display mathematical fragments of the substantive chapters remain unchanged. The rewritten formal-coverage appendix is separately reviewed as exposition. The final leading-page-break removal in the phase chapter affects only pagination.
- All 43 displays in the visual guide are byte-identical to its inherited source; its full inline/display fragment sequence is unchanged.

## Reader coverage and source correspondence

- Public coverage consistently states thirteen of sixteen principal later results have complete formal counterparts. The exact infinite diagonal family/tail estimates, its sharp budget asymptotic, and the rounded noisy diagonal rate retain printed proofs without an assigned Lean instance.
- The printed weak-subsequence proof route, background prose, and finite numerical checks retain their distinct evidentiary limits.
- All 53 representative analytic declarations in the monograph resolve in the accepted axiom inventory. All 94 module references across the 80 foundational rows resolve in the production tree. Explicit theorem-kind references match their target environments.
- The Lean guide's 69 map entries independently match declaration name, kind, module, source SHA-256, and exact declaration line. They also resolve in the accepted axiom inventory.
- All three main LaTeX documents have complete literal input/graphics/reference closure, with no duplicate literal labels or unresolved references.
- The public Lake metadata changes are limited to edition metadata and the supplied manifest root name; dependency package pins remain unchanged.

## Final documents

The final02 build report binds the actual final source hashes without a mismatch. All three final PDFs were scanned in full. No visible internal KS/WR catalogue codes, checkpoint/continuation identifiers, selected obsolete status claims, or unresolved `??` markers were found. Mathematical uses of “block” remain appropriate.

| Book | Pages | SHA-256 |
|---|---:|---|
| monograph | 160 | `c073cea764cd210fa48eb2ecf1b5e809c34d395d7be092bbf1b88d621e731f48` |
| visual | 45 | `3c2bf6786e9e910a09d72c6ace7ceccf2fea828a2c00b246794a0fad035ada56` |
| lean | 19 | `d40cb5259d1309164f5bfc76a8bc0f23f69de0fa2cc6cdf9dcac51c8ceff9300` |

Independent visual coverage was PDF pages 121–161 of the first final monograph artifact, SHA-256 `d48aa460748c372f78a21de294d722468c7d4d210b02cc65c0a7824ef37a15b0`, using four contact sheets and full-page views of pages 144, 152, 153, 154, and 159. No clipping, overlap, broken formula/table, missing glyph, blank page, or unresolved reference was found. The coordinator owns the final artifact image comparison and the other visual-review ranges.

## Evidence

The review folder retains `audit_publication.py`, before/after diffs, exact Lean-target hashes, source-closure results, source-preservation details, monograph visual coverage, final PDF scans, and exact declaration-map checks. The gate reports are `final_source.json` and `final_pdf_and_map_gate.json`.

Archive assembly and extraction verification are separate final checks, pending the assembled package paths.
