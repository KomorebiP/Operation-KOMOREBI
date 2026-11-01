# Graph reconstruction correspondence: self-review

**Verdict: proved as written**, for the bounded contract below. This verdict
does not cover the full manuscript or the omitted cardinality and dimension
formulas. Review provenance: author-side self-review, alongside Lean kernel
checking with the pinned compiler; no independent review is claimed.

## Claim card

The source is Theorem 6.1, label `thm:integrability`, in
`research/resolution-semantics/Komorebi_Resolution_Semantics.tex`, at repository
base `f1fb5583961b3e6798a378b0140c7681c2e4ce6a`. Its SHA-256 identity is recorded
in `PROVENANCE.json`. The reviewed formal sources are the exact `*.lean` input
hashes bound by this companion's replay receipt.

For every simple undirected graph and every edgewise symmetric binary field,
there exists a binary vertex labeling inducing that field exactly when every
simple cycle has zero XOR sum. The kernel consists of componentwise constants.
Every integrable field's reconstructions are uniquely parameterized by Boolean
values on connected components. Agreement at one vertex in each component
forces two reconstructions to coincide. These arguments cover arbitrary
vertex types; hence they specialize to all finite graphs.

For graphs on `Fin n` with decidable adjacency, `solve` enumerates all binary
assignments and returns a solution satisfying every edge and supplied pin if
one exists. Its soundness and completeness do not assume the cycle condition.
The additional theorem connecting successful unpinned search to cycle sums
does assume edgewise symmetry, matching undirected edge data.

## Dependency graph

```text
Bool XOR identities and list/walk induction
  -> walk concatenation, reversal and integration
  -> removal of a simple zero-sum cycle from a walk
  -> simple representative with unchanged integral
  -> all closed walks have zero integral
  -> path independence
  -> component representatives and chosen paths
  -> reconstruction and the cycle criterion
  -> component parameterization and root-fixed uniqueness

complete enumeration of Fin n -> Bool
  + decidable edge/pin checker
  -> search soundness and completeness
  -> exact example results and rejection of an inconsistent triangle
```

All leaves are internal Lean/Std proofs or conventions stated above. No
external mathematical theorem or empirical computation is required. Standard
classical choice, quotient soundness and propositional extensionality occur
where listed in the complete axiom inventory. The concrete `by decide`
examples are kernel-checked finite propositions; they are not the proof of the
general theorem.

## Obligations

| Obligation | Result and decisive check |
|---|---|
| Graph and coefficient types match the manuscript | Passed: symmetric irreflexive adjacency; Bool XOR; ordered-pair field values constrained only on edges. |
| Cycle condition means simple cycles, not an assumed condition on all walks | Passed: length at least three and no repeated internal vertices; `simple_representative` and `closed_zero_of_cycle_zero` establish the extension to all closed walks. |
| Reversal and backtracking preserve the required integrals | Passed: adjacency symmetry, field symmetry and XOR cancellation; loops are excluded by the graph structure. |
| Component selection supplies actual paths | Passed: the connectivity setoid is defined by nonempty walks; representatives and walks use explicit standard choice. |
| Reconstruction satisfies every edge | Passed: compare the root-to-target path with the root-to-source path followed by the edge. |
| Uniqueness has sufficient root hypotheses | Passed: `pins_cover_unique` requires coverage of every component; the isolated-vertex example exhibits nonuniqueness when coverage is absent. |
| Empty and disconnected graphs | Passed: the universal proofs have no nonemptiness assumption; executable examples include an empty graph and two edges plus an isolated vertex. |
| Search implements the stated finite problem | Passed: `assignments_complete` covers every function `Fin n -> Bool`; the checker quantifies over all ordered vertex pairs and every supplied pin. |
| Rejections are mathematical failures | Passed by the replay contract: false triangle integrability, false root-free uniqueness, the inherited false symmetry/additivity claims and `sorry` are rejected with required diagnostics. |
| Manuscript count/rank formulas | Out of scope: no Lean theorem for `2^c`, `n-c` or `m-n+c` is claimed. |
| General transport and forcing interpretation | Out of scope. No realization of graphs by forcing worlds is asserted. |

The strongest checked statement is the contract above. The next efficient
implementation task is a spanning-forest solver with a refinement proof
against the same specification. A separate formal increment can supply finite
cardinality and rank formulas.
