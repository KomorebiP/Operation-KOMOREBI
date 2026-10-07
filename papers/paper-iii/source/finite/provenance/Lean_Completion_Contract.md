# Paper III v1.0.1 Lean Completion Contract

## Completion statement

Version 1.0.1 is complete relative to the finite algebraic denominator defined
by the authoritative theorem map
`formalization/lean/LEAN_THEOREM_MAP_v1.0.1.md`. The map contains
41 rows resolving to 143 unique compiled declarations: 88 theorem
declarations and 55 constructions. The kernel audit explicitly covers all 143
mapped declarations, with no supporting-only target, and separately fails
closed over all 468 declarations (229 theoremInfo declarations) in the
compiled `Komorebi.PaperIII` namespace.

The completion claim holds exactly when all of the following gates pass:

1. `lake --wfail build` succeeds under the pinned toolchain.
2. `scripts/verify_theorem_map.py` confirms exact parity among the manuscript,
   theorem map, compiled declaration kinds, and explicit audit targets.
3. `KernelAudit.lean` reports no `sorryAx`, user-declared axiom, opaque theorem
   substitute, unsafe declaration, or transitive axiom outside the allowed
   standard basis.
4. The source scan finds no proof placeholder or forbidden declaration form.
5. The final PDF compiles without LaTeX warnings or overfull/underfull boxes,
   passes structural checks, uses no Type 3 fonts, and has every rendered page
   visually inspected.
6. Deterministic figure regeneration and clean extracted-archive verification
   reproduce the recorded artifacts and checks.

## Included scope

1. Finite directed multigraphs with scalar packet fibers over the stated
   semiring hypotheses.
2. Target-row/source-column elementary edge matrices with an explicit
   right-to-left execution convention.
3. Vanishing of noncomposable edge products and words.
4. Endpoint collapse of composable words, including the ordered coefficient.
5. Exact finite transfer-power expansions over words and composable walks,
   with coefficient-level endpoint action and reachability-support corollaries.
6. Canonical exact coordinate transport and exact coordinate-map composition,
   cocycle, triangle, and naturality laws.
7. A separate heterogeneous reversible-connection interface with additive
   cocycle defect, triangle holonomy, flatness, and finite path transport.
8. Gauge action, gauge covariance of defect and holonomy, and reconstruction
   of a flat connection as a gauge of canonical transport.
9. Complete idempotent packet resolutions, exact obstruction-block
   reconstruction, zero-block equivalence, packet witnesses, and the stated
   packet-preserving gauge law.
10. Arbitrary-length heterogeneous factors over one common finite packet type,
    together with separately typed two- and three-step expansions and
    supported-path vanishing.
11. Finite unary/binary operation-tree syntax with arbitrary semantics and
    input locality.
12. Candidate-specific obstruction packets and their exact classical witness
    equivalence.

## Trust boundary

The trusted core is Lean 4.34.0-rc2, commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`, plus Mathlib at revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Standard logical axioms reported
through Mathlib are limited to `propext`, `Classical.choice`, and `Quot.sound`.
Classical choice is disclosed where witness extraction requires it.

## Scope boundary and nonclaims

This contract does not include colored dependent operation trees, a
multilinear packet-labeled tree expansion, nonlinear Faà di Bruno defect
propagation, infinite sums, analytic convergence, stability estimates,
topological extensions, or physical interpretation. The arbitrary-length
heterogeneous path theorem keeps one common finite packet index; only the
separate two- and three-step declarations change intermediate index types.

Formal verification does not establish novelty, historical priority, utility
for a specific application, external peer review, or correctness of claims
outside the theorem map. Definitions and roadmap interfaces do not silently
enlarge the completion denominator.

Paper III also cites twelve unique declarations from the separately verified
Papers I--II v1.2.1 bundle. Their exact names and fourteen manuscript uses are
frozen in `formalization/lean/INHERITED_DEPENDENCY_MANIFEST_v1.2.1.md`; the
dependency bundle has SHA-256
`a20cf9353f0e882834d31e665dfd819a04e43fa606d402309be63e3b94447052`.
