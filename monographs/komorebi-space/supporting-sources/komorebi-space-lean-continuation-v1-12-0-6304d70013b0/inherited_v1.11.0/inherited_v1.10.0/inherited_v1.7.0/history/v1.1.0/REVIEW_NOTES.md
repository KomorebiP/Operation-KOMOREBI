# Komorebi Space — proofreading and revision report

**Edition 1.1.0 · 10 October 2026**

## What the review changed

The review covered the editable mathematical sources, the concordance, the executable examples, and the rendered monograph and both companions. The principal outcome is not additional length alone. The revised account now closes the printed dyadic proof, separates several previously adjacent but insufficiently connected mathematical questions, and makes the corresponding distinctions visible in examples and diagrams.

| Area | Finding | Correction |
|---|---|---|
| Dyadic reconstruction | The predecessor explicitly gave only a proof outline for a changing-index construction. | Printed a scale-uniform induction, respecting the residual spaces at every scale, and added the sharper divisibility support result KS55. |
| Protected versus unconstrained repair | Existence and Hilbert stability were developed separately; the nearest answer under a fixed preservation condition needed an explicit bridge. | Added KS56 on `D` restricted to `ker p`, including feasibility, nearest repair, ambiguity, orthogonality, and the exact closed-range boundary. |
| Quantitative descent | The linear sufficient gain hid a sharper squared estimate already available in the source. | Added its exact declaration references, the Pythagorean estimate and resulting sharper sufficient gain, and an explicit failure of unrestricted successive projection. |
| Finite certificates | A worked preservation problem needed an executable positive/negative interface. | Proved KS57, supplied a rational CLI/API with ambiguity bases and normalized obstruction witnesses, and checked three preservation problems. |
| Infinite existence | The counterexample to finite-prefix reasoning had no adjacent positive criterion. | Added the finite-fiber theorem KS58 and persistent-image characterization, with a complete classical proof and primary reference. |
| Coefficient domains | Finite algebra examples could be misread as integer-solving or characteristic-independent claims. | Labelled the three worked examples over the rationals and explained why rational and integral feasibility differ. |
| Visuals | Some labels were crowded, the shift and dyadic models needed differentiation, and several boundaries were mostly verbal. | Redrew affected schematics and added explicit geometric, support, amplification, and rank-loss plots. |
| Source integration | The relationship between the two recovered source trees was unresolved at the filename/import level. | Compared all local sources, identified one byte-identical shared module, and constructed an acyclic static union inventory with no missing local imports. |

## New written results and formal scope

KS55–KS58 are new **written additions to this edition**. They have printed proofs and selected exact finite illustrations. They are not represented as new Lean declarations or as previously unknown classical principles. KS54 remains an inherited written-only example. The other 53 exposition items have 114 resolved references to recovered declarations; a source correspondence does not mechanically certify every word of an edited proof.

The underlying recovered Lean sources were not modified. No fresh cumulative Lean build or imported-axiom audit was run. A static import graph cannot detect type elaboration errors, proof failures, or incompatible imported environments. The selected Hilbert holonomy file remains outside the verified scopes of the two frozen historical archives.

## Exact checks actually executed

| Suite | Assertions | Scope |
|---|---:|---|
| Independent publication examples | 14,224 | Existing exact finite models and equations. |
| Recovered moving-space checker | 2,767 | Fresh execution of the focused historical finite checker. |
| Revision examples and certificates | 17,213 | Rational certificates, dyadic matrix models, protected geometry, persistent images, and negative controls. |
| Total | 34,204 | One executed run of each suite, not a sum over repeated builds. |

The revision suite includes 969 rational certificate problems: 729 exhaustive small two-coordinate cases and 240 seeded shape or degenerate cases. It returns 808 feasible and 161 obstructed classifications. An independent small-rank oracle uses all minors and Leibniz determinants, rather than the proposer's elimination routine. Thirty-five dyadic systems use genuine two-by-two rational operator fibers, including noncommuting factors. These are finite tests, not substitutes for the universal printed proofs.

Nine controls rejected an exact answer with wrong protected values, an incomplete ambiguity basis, a corrupted dual certificate, ragged dimensions, floating-point values, Boolean values, a zero denominator, an incorrect boundary inequality, and an invalid inference from coordinatewise to uniform convergence.

## Visual and publication review

The final reader set has 56, 21, and 22 pages. All 99 pages were rendered for review. Contact sheets were inspected for flow and layout, and selected pages were inspected at enlarged resolution for formulas, labels, diagrams, and the source inventory. The monograph includes a genuine three-dimensional Euclidean example, not a schematic projection pretending to be spatial data. The visual guide now has eighteen plates; eight numeric plot assets have reproducible Python sources.

Final mechanical preflight found no overfull-box warning, undefined reference, off-page text, replacement character, near-empty page under its stated check, or unembedded font. The final document hashes and review scope are in `audit/publication_preflight.json` and `audit/visual_review.json`. This is a recorded review, not a guarantee that no future reader can discover an error.

## Failures and defects corrected during this revision

The first numeric figure build failed because Matplotlib mathtext did not accept the command `\ge`. Replacing it with `\geq` allowed the build to proceed; the failed attempt is retained in `audit/development/figure_build_attempt1.log`.

An early three-dimensional plot clipped its vertical label. A protected-repair figure was initially too tall and pushed a warning box onto a separate page. A closing insight box and a duplicated reference also produced poor pagination in provisional builds. The plot layout, preserved figure canvas, figure placement, box text, and bibliography were revised, then all three documents were rebuilt and reviewed. The final output contains no remaining instance of these observed defects.

The first final-archive manifest check caught an overly broad exclusion inherited from the manifest helper: every file named `SHA256SUMS.txt` was omitted, including the predecessor's historical manifest. The rule was narrowed to exclude only the current root manifest. The historical manifest is now itself hashed, and the ZIP is checked for complete payload coverage as well as hash agreement. The failed packaging assertion is retained in `audit/development/packaging_manifest_attempt1.json`.

The predecessor's own errors and corrections remain recorded under `history/v1.0.0/`; they are not relabelled as newly discovered failures.

## Remaining obligations

A fresh combined Lean compilation, axiom audit, and negative-control replay are still required for an integrated formal release. New formalization of KS55–KS58 has not been supplied. The rational example is not a verified refinement of a Lean program, an integer solver, or a universally optimized numerical algorithm. Higher-categorical generalizations, unrestricted changes of view doctrine, and semantic existence for arbitrary arithmetic or physical objects remain outside this publication's claims.

For the next block, use the static import plan and frozen source hashes to build a canonical formal source tree. Do not remove the written-only classifications until actual Lean declarations and replay evidence have been produced.
