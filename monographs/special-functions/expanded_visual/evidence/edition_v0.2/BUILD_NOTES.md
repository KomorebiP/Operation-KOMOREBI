# Build and review notes

The expanded guide is a separate teaching companion to the v0.1 consolidation. It has 116 pages, 110 illustrated lessons, and 110 distinct lesson figures. The eight source releases and prior consolidated manuscript were not modified.

## Reproduction scope

The default `reproduce_guide.py` runner regenerated all lesson figures and compiled the complete guide three times. A subsequent page review led to presentation refinements: a cover paragraph break, shorter I04 subplot titles, 300-dpi rasterization of the colored meshes in V03/VI03, and precise figure-format wording. The affected figure generators were executed for those blocks. Their mathematics, ranges, sampled data, and numerical checks were retained. The final TeX sources were compiled three times and passed structural validation with no warnings or overfull/underfull boxes.

Most figure content is vector. V03 and VI03 retain vector axes and labels while embedding 300-dpi colored image layers, avoiding fine white PDF cell seams. All figure PNG copies are retained. No AI-generated imagery was used.

## Corrected intermediate failures

- An early foundation preview used an incorrect relative TeX path. The working directory/path was corrected and the eight-page preview compiled successfully.
- MathText labels in synthesis, VIII12, and IV11 initially omitted required braces. The labels were corrected and the affected generators executed successfully. IV11's earlier reviewed image predated its final generator source; timestamps support a late unexecuted edit, while the exact introducing edit is unverified. The full default build caught that discrepancy.
- One tail-bound metadata calculation overflowed a fixed-width NumPy integer. It was replaced with Python integer arithmetic and rerun. The original plotted values were unaffected.
- The first independent Decimal witness evaluated the constant Taylor term as `0**0`. The checker was corrected to handle the constant term explicitly. Its failed record and successful successors remain in the evidence.
- A large VII/VIII prose patch was rejected because TeX quote backticks terminated a JavaScript template string. It was submitted in smaller blocks; no mathematical content was lost.
- An initial final-spacing assertion stopped before creating the render directory, so that render did not start. Explicit paragraph breaks after the notation table resolved the spacing warning; all final pages were subsequently rendered successfully.
- The final mathematical report inventory initially counted the aggregate IV--VI wrapper as an additional generator. It was corrected to distinguish seven generators from their wrapper.
- A presentation-only arithmetic provenance checker initially used a shallow JSON copy. Its attempted restoration of an old hash also altered its in-memory comparison object. The on-disk audit was correct. The checker was corrected to use a deep copy; the failed attempt is preserved with the successful check.

- A final packaging check initially looked for the VII/VIII PDF hash inside its binding record; that schema stores the hash in `pdf.sha256`. The check was corrected and passed. The review record and PDF were already correct.

## Verification limits

All 110 lessons received mathematical consistency review. Five independent bounded computation records distinguish exact arithmetic or symbolic checks from finite floating-point evidence. A separate provenance bridge preserves the unchanged arithmetic results after the I04 title adjustment. Declared tail bounds, quadrature ranges, recurrence gauges, scalar domains, and inherited proof dependencies remain explicit.

The old 148-test result belongs to the earlier consolidation and was not rerun for this guide. The guide does not claim a complete analytic Lean formalization, a solution to the signed-coherence problem, a full scalar-to-matrix q-Racah normalization map, or a universal proof from finite plots.

All 116 pages were rendered at 110 dpi and reviewed. After the final presentation refinements, 111 pages were verified pixel-identical to the reviewed baseline; pages 1, 17, 64, 76, and 116 were rechecked at full size. Final page, figure, navigation, and mathematical review records are included separately.
