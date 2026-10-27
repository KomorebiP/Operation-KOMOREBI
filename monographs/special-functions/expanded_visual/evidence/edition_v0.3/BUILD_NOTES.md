# Build and review notes for v0.3

The guide has 167 pages and 158 illustrated lessons. The original 110 lessons remain intact; 48 new lessons cover sequences, polyphase channels and taps. The topology guide and eight original special-function releases were not modified.

## Reproduction

The default eight-script runner regenerated all 158 PDF/PNG figure pairs and compiled the guide three times, then passed structural validation. That complete run is retained in FULL_REPRODUCTION.log. Final visual QA found one overlap in the P05 cube-root label. The author changed only its label coordinates/alignment, regenerated the polyphase figures and exact check record, and independently bridged that change to the previously audited source. The final TeX sources were compiled three times and validated again; FINAL_REBUILD.log and FINAL_COMPILE.log pin this final build.

All 167 pages were rendered at 110 dpi. The final P05 label correction changed only physical page 138; the remaining 166 renders are byte-identical to the reviewed build. Original lesson body/footer pixels match the 110 inspected v0.2 pages. The 57 opening, new-lesson and source pages received fresh visual review. The final compile has zero warnings or overfull/underfull boxes, and no visual defect remains.

## Corrected intermediate failures

- A README patch combined two operations on the same file and was rejected. It was replaced by one complete update.
- The first sequence figure run passed an empty row-label option to a Matplotlib table. That rendering option was corrected, and all sixteen figures generated successfully.
- Assembled-page inspection found the P05 lower cube-root label overlapping a marker. Its position was adjusted and the final page rechecked at native resolution. The author review records the initial miss and resolution.

The independent audit retains six resolved mathematical/semantic findings and four bounded-execution revisions. Their final status, source pins, domains and exact limits are recorded separately. Historical v0.2 build failures and evidence remain in edition_v0.2.

## Scope

Thirty compact official OEIS extracts retain names, offsets, dated revisions, attribution and eight indexed terms. Definitions and source formula statements are separate from exact algebraic derivations and bounded computation. The independent addition suite passed 24 exact contract families and 33,943 checks without importing the author generators. The source-defined Apéry and up/down identities remain named inputs, rather than new universal proofs from finite output. The P05 layout refresh did not change the independent execution inputs and was verified through a reversible presentation bridge.

Existing special-function proofs and research boundaries are inherited through unchanged sources and unchanged numerical facts. Finite causal FIR sums may act on growing formal sequences; no bounded norm statement for Fibonacci is added. Ordinary versus exponential generating coefficients, recurrence kernels versus reciprocal responses, and paired Haar versus causal decimation conventions remain explicit. No new analytic Lean formalization, historical novelty result, generic stationary recurrence for all OEIS entries, or anti-aliasing performance claim is made.
