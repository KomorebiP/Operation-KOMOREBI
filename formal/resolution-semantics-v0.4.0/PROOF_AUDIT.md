# Exact reconstruction count: self-review

**Verdict: proved as written**, for the finite binary graph-counting contract
below. This is author-side self-review alongside Lean kernel checking. It is
not independent scientific review and does not cover the full manuscript.

## Claim card

The source is Theorem 6.1(3), label `thm:integrability`, in
`research/resolution-semantics/Komorebi_Resolution_Semantics.tex`, at base
`fefc80f574fe2315f4ef82567f54ef65e1a3fa4c`. The manuscript identity and unchanged
0.3.0 sources are recorded in `PROVENANCE.json`. The reviewed Lean inputs are
the exact file hashes bound by this companion's replay receipt.

For every `n`, every simple undirected graph on `Fin n` with decidable
adjacency, and every integrable binary edge field, the list of all integrating
vertex labelings has length `2 ^ componentCount G`. The list is complete and
duplicate-free. `componentCount G` is the length of a complete, duplicate-free
enumeration of the actual component quotient. A canonical component index is
constructed within the proof for
every finite graph; no supplied partition or numerical component count is
assumed by the final theorem.

The explicit-index theorem additionally supports a verified witness with `c`
components. The certificate requires edge compatibility, a path from each
vertex's indexed representative to that vertex, and recovery of every index
at its representative. The induced maps to and from the quotient are proved
inverse. The numerical formula counts all unpinned reconstructions.

## Dependency graph

```text
Inherited complete Boolean assignment enumeration
  -> distinct head choices and injective extension
  -> duplicate-free enumeration of length 2^c

Inherited graph reconstruction classification
  + certified inverse component indexing
  -> injective map from component bits to labelings
  -> complete duplicate-free reconstruction list of length 2^c

Complete vertex enumeration -> duplicate removal
  -> complete duplicate-free enumeration of component quotient classes
  -> canonical index for every finite graph

Executable edge filter + complete duplicate-free vertex assignments
  -> complete duplicate-free actual solution list
  -> same members as the reconstruction list when integrability holds
  -> list permutation and equal length
  -> exact 2^componentCount G formula
```

Every leaf is an internal Lean/Std proof or the preserved 0.3.0 formalization.
No external mathematical theorem or empirical computation is required. The
component enumeration and general list comparison use standard classical
reasoning. All dependencies are listed in the axiom inventory. The executable
examples corroborate the general result; they do not prove it.

## Obligations

| Obligation | Result and decisive evidence |
|---|---|
| `c` measures actual connected components | Passed: edge-compatible labels are constant along walks; component coverage and representative recovery induce mutually inverse maps between the quotient and `Fin c`. |
| A finite component index exists | Passed: enumerate all vertices, map to their quotient classes, remove duplicates and choose the index of each class; injectivity of list access follows from no duplicates. |
| Index ordering and symmetry | Passed: the index uses the supplied `Fin n` vertex enumeration. It is not asserted to be invariant under relabeling or to define a Boolean projector. |
| Boolean choices are counted without repetition | Passed: `assignments_nodup` separates false/true heads and recovers tails; `assignments_length` proves the power-of-two length by induction. |
| Every reconstruction is counted | Passed: the inherited component parameterization supplies the finite Boolean choices for every integrating labeling. |
| Distinct component choices yield distinct labelings | Passed: evaluate at the certified representatives and cancel the fixed XOR offset. |
| The actual solver count has the same meaning | Passed: filtering preserves no duplicates; its membership theorem is exactly `Integrates`. Both complete lists therefore have equal length. |
| Integrability is retained | Passed: the main theorem assumes an integrating labeling exists; symmetry and the cycle condition follow from it. The inconsistent triangle has zero solutions. |
| Isolated and empty cases | Passed: the disconnected example has three certified components and eight solutions; an empty graph has one empty labeling. The generic edgeless theorem covers every `n`, including zero. |
| Invalid counting shortcuts are rejected | Passed by the replay contract: false counts for a nonintegrable field, an omitted isolated component and the empty graph must fail with `decide` diagnostics. |
| Numerical rank formulas and partial pin counts | Out of scope. |
| Models of ZFC or forcing realizations | Out of scope. |

The strongest checked statement is the numerical contract above, together with
the preserved reconstruction results. The rank formulas and an efficient
spanning-forest solver remain separate formal increments.
