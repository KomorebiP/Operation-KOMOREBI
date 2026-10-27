# Self-review of v0.7.0

**Primary verdict for K32–K41: proved as written under their stated hypotheses, by written mathematical arguments.** This is authoring-session self-review. It is not an independent referee verdict, a Lean certificate, or a fresh complete audit of all inherited v0.6.0 claims.

## Exact scope

The new claims concern finite event-poset diagrams, strict chain-natural models of the pure two-axis exchange grammar, coherent stable cofibers, constructor-invariant thick kernels, and explicit integral perfect-complex examples. The running manuscript is 60 pages. The new proof fragments and the source diff isolate what changed.

## Dependency map

- K32: inherited finite event-ideal theorem + actual naturality/interchange + nerve + specified stable realization.
- K33: coherent square + finite-colimit interchange + stable cofiber equivalence criterion.
- K34: K33 + eligible-context initial ideal + finite cover decomposition.
- K35: elementary-square pasting + ideal union/intersection combinatorics + finite left Kan extension and induction.
- K36: K33–K35 + invariant thick closure + stable Verdier localization.
- K37: finite-colimit interchange + exact tensor in each variable.
- K38: explicit integral Euclidean row reduction + exterior chain-map construction and cohomological conventions.
- K39: K36–K38 + prime-power/Chinese-remainder construction + finite cohomology and localization over Z.
- K40: K39 + finite allowed pair types + exact tensor with an arbitrary perfect seed.
- K41: a verified Smith form for each supplied matrix + K37–K39 + direct-summand support and collapse tests.

No node depends on arithmetic automorphic existence or the desired Langlands statement. No conclusion of a test is used as a premise for an unbounded theorem.

## Obligation matrix

| Obligation | Result |
|---|---|
| Typed levels and variance in K32 | Passed: number of coarsenings to the left fixes the transformation level. |
| Semantic coherence | Passed in strict models by actual chain naturality; weak models outside scope. |
| Cofiber signs and grading | Passed: cohomological degrees stated, explicit matrices and exterior-power tests. |
| Square commutativity versus excision | Separated; noncoprime scalar example refutes equivalence. |
| Ordered filtration independence | Remains refuted; no restoration claimed. |
| Event-context and principal-ideal arguments | Passed by finite induction and universal properties. |
| Constructor action on quotient | Passed after invariant thick saturation; no unproved action descent. |
| Noncollapse | Proved in positive scalar model, not general. Zero/zero and free/free collapse displayed. |
| Integral quotient kernel | Proved on all source objects; no unsupported equivalence of entire quotient categories. |
| Finite certification | Restricted to fixed finite scalar label/independence signature; all finite word lengths by theorem. |
| Matrix scope | Supplied verified Smith forms; finite test is only the explicit 11-matrix family. |
| Novelty | Not established; source check is not a novelty search. |
| Lean and independent review | Not performed. |
| Arithmetic globalization | Open, explicitly not implied by event reconstruction. |

## Decisive counterexamples and limitations

A commuting square with labels 6 and 10 has a nonzero interaction supported at 2. Inverting 2 kills it while preserving primary 3- and 5-torsion. The triple (6,10,15) has zero highest Koszul interaction but nonzero pairwise interactions. Two zero labels give a free interaction containing the unit and force collapse. A dependent p,p chain retains the nonsplit p-squared extension. Free/free matrix cone summands give a shifted unit retract. These examples prevent the stronger unqualified claims.

The scalar model uses identity coarsenings. Its arithmetic is concrete integral algebra, not a local-field reciprocity construction. The general K32 theorem allows nonidentity strict coarsenings, but no actual arithmetic tower is constructed here.

## Commands and finite checks

See the exact argv, coefficient convention, input hashes, and bounds in the result JSON and `manifest.json`. Both checks returned exit 0 and PASS. The first reproduces the unmodified v0.6.0 suite. The second verifies integer chain isomorphisms, d-squared identities, finite-field homology dimensions, scalar event diagrams, localized inverse maps, and the explicit matrix-pair family. The general proofs are separate.

The 5,289 ideal-pair implementation checks test the combinatorial ideal union/exclusivity property, not a generic infinity-categorical colimit. The finite-field checks are not exhaustive over all primes; the written integral normal form supplies the uniform argument. The matrix tests do not enumerate all integer matrices.

## Manuscript integration and final layout

The standalone source regenerates byte-for-byte from the preserved v0.6.0 source and the two proof fragments via `integrate_v070.py`. The abstract, K27 status, K32–K41 ledger entries, next obligations, conclusion, bibliography, and audit were updated. Prior audit evidence remains labelled historical. The version ledger font/paragraph alignment was adjusted after rendering to remove an orphaned last paragraph, reducing the working build from 61 to 60 pages without deleting content. The phrase 'localizing at 2' was clarified to 'inverting 2'. These changes alter no theorem.

The final LaTeX log has no warnings, undefined references, overfull boxes, underfull boxes, or missing-character reports. All pages were rendered. All were contact-sheet reviewed; selected new mathematical pages, the reconstruction proof, the prime-kernel example, and the final ledger were also viewed at full-page size. A programmatic check finds no text spans outside page bounds. No claim of pixel-perfect review of every symbol is made.

## Failures and remaining risks

No proof-check script or LaTeX command in this continuation ended in a failed status. Visual review did find the orphaned historical paragraph, and the first compact-ledger rebuild produced a harmless underfull-box warning; both were corrected before release. Source discovery initially produced unrelated results, so exact primary URLs were read directly. No failed discovery was treated as evidence of novelty.

The main residual risks are mathematical mistakes not caught by self-review, inherited claims outside this pass's scope, and the missing domain interpretation for global reconstruction. Independent review and Lean formalization remain outstanding. No proof of general Langlands reciprocity, a new foundational axiom, or a physical law is supplied.
