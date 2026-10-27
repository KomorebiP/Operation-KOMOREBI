# Summary

The catalytic component is now a coherent release with repaired general hypotheses, restored reproducibility inputs, fresh finite replays, and a new analytic certificate for the four two-qubit entangling defects. The latest corrected chapter sources are in `sources/catalytic/Catalytic_Gate_Set_Distortion_Monograph_Source/chapters/` relative to the workspace root.

This review surveyed all catalytic chapter files for scope and consistency and closely reviewed the universal atom, interval-tree bound, snapshot family, direct-sum and tensor arguments, group-metric templates, finite-census architecture, and the new two-qubit theorem. It did not independently reconstruct every proof in the 2,305-line linear core or authenticate every cited external source. No catalytic Lean formalization is supplied or newly claimed.

# Mathematical changes

The retraction and inheritance statements now require homomorphisms and compatible costs. Schreier cosets and action order agree, and the base-fiber characterization has the required alphabet-intersection hypothesis. Ordinary weighted Green counting series require strictly positive costs. Direct-sum additivity uses an aggregate generator bound. The source explicitly distinguishes additive gate costs from layer depth, excludes undefined infinite-minus-infinite defects, states inverse-cost symmetry, and specifies the algebraic setting of generic rigidity.

The no-ancilla reversible discussion now records the parity obstruction above three bits. Scalarized defects of nested models remain nonnegative. The ambient lower bound for the ring-universal atom explicitly handles the four-gate case before the five-gate case. The concrete linear construction and finite census conclusions are unchanged.

# New analytic closure

Theorem `thm:clifford-two-analytic` proves exact restricted entangling cost three and ambient entangling cost two for

\[
M_D=\begin{pmatrix}J&0\\I+DJ&J\end{pmatrix},\qquad
J=\begin{pmatrix}0&1\\1&0\end{pmatrix},\quad D=\operatorname{diag}(d_0,d_1),\quad d_i\in\mathbb F_2.
\]

The four matrices form one orbit under free final phase gates. The restricted lower bound follows because the swap block requires at least three elementary CNOT matrices. The ambient lower bound uses rank-one local diagonal blocks, which cannot occur with at most one charged CNOT or CZ and arbitrary free local Clifford gates. Explicit words attain both bounds. The complete census still supplies the assertion that these four matrices exhaust the two-qubit defects.

The root reviewer independently reconstructed the matrix identities and rank obstruction. Its receipt is `review/root/clifford_two_analytic_check.json`. The computational check also verifies that this four-element family equals the exact two-qubit exceptional set. Appendix C1 and the research tasks now reflect this closure.

# Finite replay

The small Python atlas matches the frozen JSON byte for byte. The three C++ Clifford censuses each reached 1,451,520 ambient states and 10,752 restricted states:

| Cost convention | Defective targets | Maximum defect |
|---|---:|---:|
| Total count, no primitive SWAP | 24 | 1 |
| Total count, primitive SWAP | 0 | 0 |
| Entangling count, free local gates | 1,624 | 2 |

The two-qubit entangling census has four defects, all of type 3 to 2. Both three-bit affine-versus-Toffoli cost models have zero defects among 1,344 affine targets in the 40,320-state ambient group.

All eleven recovered linear supplement programs pass against frozen output. This includes the complete binary dimensions two through six, the complete ternary dimensions two through five, canonical atom checks over three and five, analytic motif matching, exact Green coefficients, higher-family and resource checks, and selected exact ambient distances seven, eight, and nine for binary snapshot targets in dimensions seven through nine. These are bounded exact computations in their stated domains.

Thirteen orthogonal checks cover independent dense symplectic identities, Python/C++ agreement at one and two qubits, agreement of every zero-one BFS distance with heap Dijkstra for the 720-state Clifford and 40,320-state reversible examples, displayed witness endpoints, four-bit generator parity, and the new analytic four-element family.

The initially attempted pytest command failed because pytest was absent. All four unchanged, fixture-free smoke test functions were then invoked directly and passed. The final mathematical replay script avoids requiring pytest. It does not build the PDF.

# Recovered and missing evidence

Four Python files referenced by the inherited core driver were absent. They were restored byte for byte from the earlier source-and-supplement archive retrieved by the root agent. `recovered_files.json` records all source locations and SHA-256 values. The complete core driver then passed.

The four-bit Toffoli sandwich experiment, its affine distance table, and the twelve-class Latin atlas were not present. Specific claims that the current archive reproduces those experiments have been replaced by pending verification obligations. General Latin spectral collapse remains a symbolic consequence of the displayed projector formulas. The contextual Ball–Simoens source was authenticated by the symmetry reviewer, recorded in `review/symmetry/source_record_qls.json`. This reviewer did not independently authenticate it.

# Remaining research scope

The following are still open and are clearly labeled in the source: universal minimality of six over all coefficient rings, sharp asymptotic and multiplicative distortion bounds, border length and tensor activation, larger Clifford classifications, four-bit nonlinear assistance, phase-polynomial and Gaussian catalytic gaps, and broader root-system thresholds. Completing this release does not claim to resolve that research program.

# Artifacts

- `source_changes.patch` and `source_changes.json`: exact chapter changes and hashes.
- `originals/`: immutable pre-edit chapter snapshots.
- `catalytic-component-review.json`: raw grouped findings, coverage, and repair dispositions.
- `recovered_files.json`: restored supplement provenance.
- `runs/`: initial fresh computations and checks.
- `final_v2_replay/`: consolidated replay and before/after input-hash manifest.
- Component `checks/verify_release.py`: dependency-free repeatable mathematical replay command.

Root volume construction is responsible for unified PDF layout, reference reconciliation, and final packaging. No numerical test is represented as a universal proof, and the exact Clifford results refer to the binary symplectic quotient, not complete unitary equality including Pauli and phase data.

The first consolidated manifest used absolute artifact paths and classified log files as declared results. This did not affect its successful mathematical replay, but it did not meet the stricter v2 evidence schema. The emitter was corrected and the complete replay repeated with relative paths and separately typed results. One intervening shell patch used a wrong working-directory-relative path and failed before changing source; the successful corrected driver is retained.

The final v2 manifest validator returned `valid evidence record (run status: completed)`. The final replay took 55.61 seconds and recorded 42 unchanged input artifacts and 11 hashed outputs. This is an evidence-format and replay result, not a certificate of all mathematical prose.
