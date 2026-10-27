# Komorebi Space expansion and review report — 1.4.0

**Recorded:** 2026-10-11T19:54:50.029667+00:00

## Result

The monograph expands from **84 to 105 pages**, with **six parts, 29 numbered sections, and four appendices**. The visual guide has **33 pages and 30 plates**. The Lean/evidence guide has **33 pages**. The complete reader set is **171 pages**. The existing accepted formal source baseline is unchanged.

## Mathematical development

Five new chapters supply an explicit progression from approximation to exact realization and examine two independent kinds of obstruction.

The exactification treatment proves the summable-movement theorem, a variable-rate version, and a restarted geometric bound, with hypotheses retained. A polynomial path has no fixed contraction factor below one but has an exact summable tail. A second path repeatedly doubles its residual and still converges because its two-step product is one quarter and its weighted movements are summable. Further examples distinguish residual decay from drift and distinguish convergence of one path from equality of answers selected by different paths. The cofinal-profile comparison preserves vanishing under monotonicity, not the numerical rate.

The floor chapter distinguishes exact membership in an admissible correction image from membership in its closure. A uniformly positive eventual floor blocks every admissible correction sequence. In contrast, pointwise positive floors can tend to zero. Closedness, attainment of an infimum, and control of a preimage norm are kept separate.

The new Hilbert-space model uses d(u,t)_n=(u_n+t)/n and p(u,t)=t on ell2 plus R. Every finite protected problem has a unique solution. The associated ordinary inverse-limit point exists, but it is not represented in the chosen square-summable semantic space. The actual algebraic obstruction is nonzero while its numerical floor is zero. The displayed prefix corrections have squared norm N, while their infinite residual square lies between 1/(N+1) and 1/N. A separate all-candidate inequality proves that every protected sequence with residual tending to zero has correction norm tending to infinity. Thus this is not merely a bad iteration example. The whole infinite model is a complete written derivation, **not a new Lean instance or a finite extrapolation**.

The transport-cost chapter proves the directed and symmetric-zero laws from a separately specified subadditive arrow cost. A free-path example has zero-cost distinct objects which are not isomorphic, asymmetric finite costs, and an isolated component. The zero-arrow collapse theorem shows why compatibility is not by itself an information geometry.

The phase chapter develops the retained F2 pair-cocycle obstruction. Explicit X and Z matrices demonstrate coherent associative composition with a scalar phase that cannot be removed. Retaining a phase bit yields an eight-element group with a faithful matrix representation. The matrix interpretation, the nonzero-complex-scalar observation, and the extension group are separately marked printed derivations with finite tests. They do not convert the model into the earlier arrow-cocycle stack.

A new hypothesis atlas indexes conclusions by their needed data and assumptions. The reader's workshop now has **nine fully solved problems**, up from five.

## Formal and editorial evidence

The principal concordance grows from **70 items and 180 references to 80 items and 211 references**. KS71–KS80 use actual declarations in Exactification, LinearExactification, RepairExamples, Profiles, ObstructionFloor, WeightedGeometry, and ProjectiveExample. Their exact names, hypotheses, current source hashes and retained accepted environment entries are checked. There are no written-only principal IDs, but this does **not** mean every added example has a newly compiled Lean theorem.

All **156 files in the formal tree** are byte-identical to the predecessor, including production sources, metadata, scripts, and tests. The retained **version 1.2.0** record remains 138 production modules plus one root, 139 accepted compilation targets, 4,745 audited project declarations, and 1,507 explicit theorem/lemma declarations including auxiliaries. **No Lean compilation or axiom audit was run in this edition.** Source correspondence is editorial, not a machine translation of the manuscript.

`audit/deepening/mathematical_scope_review.md` records the hypothesis audit. `data/deepening_models.json` separates formal general principles from printed models and finite checks.

## Freshly executed checks

Five exact finite suites passed: 14,224 original assertions, 2,767 recovered moving-space assertions, 17,213 revision assertions, 96,345 prior-expansion assertions, and **13,817 new assertions**, totaling **144,366**. The new suite has **eight rejection controls**. Its stated cases include 195 polynomial-path states, 65 burst states, 330 geometric states, 257 harmonic states, 65 profile-sampling indices, 768 diagonal prefix/tail windows, 32 finite inverse dimensions, 81 rational escape-inequality vectors, 175 floor cases, 16 directed-cost pairs, 64 phase triples, all 16 scalar gauges, all 512 triples in the eight-element extension, and 64 matrix-lift pairs. These counts describe finite regression coverage, not independent theorems.

The exact-example command `examples/approximation_models.py` runs with input validation and records rational path data, finite repairs, proved infinite-tail bounds, and the phase table. It does not numerically approximate an infinite proof.

Archive/source integrity, current source concordance, finite checks, figure generation, the three PDF builds, and mechanical preflight passed in the accepted supervised run `audit/deepening/build_attempt05.json`, with terminal exit code zero. Formal preservation is separately recorded in `audit/deepening/formal_preservation.json`.

## Publication and visual review

All **171 final PDF pages** were rendered. Every draft contact sheet was inspected, new models were enlarged, and the final pages were compared by rendered-pixel hashes. The 163 unchanged final pages match reviewed draft pixels. The eight changed final pages were individually inspected. The final render and review are bound to the actual PDF hashes in `audit/visual_review.json`.

Final preflight found no overfull boxes, undefined references, off-page text, replacement characters, or unembedded fonts. The monograph has 226 internal links. Six new vector plates were added without changing the underlying formal tree. The new directed graph complements the distance matrix rather than repeating it. Labels retain direction and cost separately from path length.

## Failures and corrections

The first outer publication command was interrupted by the tool timeout before producing a terminal receipt. It is recorded as **INTERRUPTED**, not PASS. A supervised runner then produced durable exit-code records. Later complete builds passed mechanically but were superseded after visual review.

Review removed a nearly empty final continuation page, improved a split sentence around the phase invariant, and replaced a duplicated numerical table with a directed graph. The first graph draft had its two nonzero arrow-cost labels reversed. That error was caught against the stated generators, corrected, and rebuilt. Enlarged review then separated two inner labels. The accepted final graph uses explicit oriented-edge records for both arrows and labels. No failed or superseded artifact is promoted to final visual evidence.

Historical Lean-development failures retain their original records and scopes. None is represented as a new compiler run.

## Limits and restart

The official kernel, compiler, standard axioms, and pinned imported caches retain the accepted baseline's trust boundary. There is no independent kernel check, full-source mathlib rebuild, native Windows execution, or universal Python refinement. The infinite Hilbert model and additional matrix interpretations are proved in print and distinguished from formal instances. No new universal-view doctrine, arbitrary higher-stack theorem, unrestricted semantic realization, arithmetic correspondence, or historical novelty claim is made.

Begin from this package, verify the payload before editing, preserve KS01–KS80 and the original archives, and follow `PROGRESS_LEDGER.md`. A future formalization of the new worked models requires an actual versioned source change and a fresh compiler and axiom replay, not relabeling the retained evidence.
