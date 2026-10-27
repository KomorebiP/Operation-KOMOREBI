# v0.9.0 proof and implementation audit

## Verdict and scope

**New results: proved in the written manuscript under their stated restrictions, with self-review.** No independent referee review or proof-assistant certification was performed. This audit covers K53–K61 and the modified explanatory/dependency surfaces. The rest of the corpus is preserved, not reverified from scratch.

The target was a natural arithmetic transformation/resolution comparison with a nonzero defect not manufactured by a scalar weight. K59 supplies one in enhanced unbounded derived categories. It does not supply one inside perfect fibers, nor a universal information-preserving repair.

## Dependency map

- K53 uses saturation, torsion-freeness, and the explicit division boundary.
- K54 uses K53 plus Smith data, finite generation, and completeness of finite free Z_p-modules.
- K55 uses an explicit crossed-homomorphism boundary and finite-group averaging. The coefficient long exact sequence is an independently checked classical source.
- K56 applies K54–K55 to the Hom lattice and uses the determinant unit criterion.
- K57 uses the explicit norm-quotient presentation and cyclic H¹ calculation.
- K58 uses the canonical evaluation mate, exactness, and thick generation by the coefficient unit.
- K59 uses the cyclic free resolution, a bounded-above free resolution of F_p over Z/p², evaluation naturality, and the long exact cone sequence.
- K60 uses a binomial calculation modulo p³, including the odd-prime boundary.
- K61 uses K58 and transitivity of the canonical coefficient-change comparisons, checked via their common evaluation mate.

## Adversarial obligations

| Obligation | Result |
|---|---|
| Exact source/target categories | Passed: ordinary modules and unbounded derived categories separated |
| Exchange direction | Passed: natural comparison CA→AC explicit, not inverted |
| Kernel boundary well-defined and onto | Passed by lift-change and division argument |
| Sharp uniform delay | Passed, including h=0 and c<h witness |
| Invariant residual transition | Passed: multiplication by p^(m−n), not constant identity |
| Cyclic group relation and norm | Passed for odd p and invertible J |
| p=2 or noninvertible J | Excluded hypotheses tested; claimed positive-degree vanishing fails there |
| Derived tensor model | Passed: original nonnegative invariant complex is not assumed K-flat |
| H⁰ of canonical comparison | Passed by evaluation naturality |
| Infinite-degree cofiber calculation | Written long exact sequence argument, not finite extrapolation |
| Unit loss under quotient | Passed with separate exact/coproduct-preserving conclusions |
| One-step action lift | Refuted explicitly for all matrix corrections |
| Lifted-input positive theorem | Passed via perfect common-base changes and transitivity |
| Zero defect implies lift | Not proved and not claimed |
| Perfect-fiber instantiation of K59 | Out of scope; output and defect are unbounded/nonperfect |
| Arbitrary profinite or Langlands input | Out of scope |
| Lean or independent review | Not performed |

## Executed routes

1. Kernel/invariants route: explicit first-cohomology residual and sharp repair window for fixed integral constraints. Positive written results K53–K57.
2. Fully derived regular-base route: expected defect disappears; K58 proves equivalence for perfect coefficient changes. This is a restriction, not evidence for a nonzero defect in that regime.
3. Singular finite coefficient route: K59 gives a canonical nonzero defect, K60 proves one-step nonlifting, and K61 gives a positive theorem on genuinely coefficient-lifted inputs.

## Exact tests and implementation review

`checks/run_all.py` runs all four suites, records timeout and thread caps, source hashes before/after, result hashes, and actual process exits. All four passed. No matrix or action inside the stated finite populations was skipped. No randomness or numerical tolerance is used.

The new Smith routine verifies S*A*T=D and both change-of-basis determinants are ±1. The 2×2 integer family also checks determinantal gcd data. Full bar differentials provide an orthogonal implementation check of four cyclic cohomology fixtures rather than relying solely on the periodic complex. That is implementation diversity within one session, not independent mathematical review.

The inherited three scripts match the exact supplied base package. Their new results are fresh reruns, not copied old PASS labels.

## Corrections and failures during this release

- An initial broad web search returned irrelevant results. It was discarded; direct primary sources were used instead.
- A newly added provenance checker initially looked only for `script_sha256`. Two inherited reports store this under `input_sha256[script]`, so the checker falsely flagged two hash mismatches. The initial failure report is preserved as `static_source_checks_initial_failure.json`. Schema handling was corrected and the hashes verified. No mathematical test or source mismatch occurred.
- Visual inspection found a sparse final contents page and an orphaned continuation of the historical version ledger. Scoped typography changes removed these without deleting content. Interim PDFs had 88/87 pages; the final PDF has 86.
- Self-proofreading corrected the new phrase “h annihilates” to “p^h annihilates”. It also replaced an imprecise next-step sentence about already liftable inputs with the actual unresolved sufficient representation-lifting criterion.

## Build and layout

The final `latexmk -pdf -outdir=build -interaction=nonstopmode -halt-on-error` command exited successfully. The final log contains no warnings, undefined references/citations, overfull boxes, or underfull boxes. Source checks found no duplicate labels or missing references.

All final pages were rendered in PyMuPDF. Whole-document contact sheets were inspected, with detailed new-theorem and end-matter inspection. No visible clipping, overlapping equations, broken glyphs, or unresolved citations were found in that review. The geometry checker found no word within 10 points of a page boundary. Geometry alone does not prove visual quality.

## Remaining risk

Authoring-session review can share the errors of the original derivation. General categorical arguments and unbounded derived computations deserve specialist review. No result in this release asserts historical novelty, sufficient arbitrary lifting, new physical laws, or Langlands reciprocity.
