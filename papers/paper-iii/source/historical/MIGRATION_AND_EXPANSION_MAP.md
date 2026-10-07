# Paper III Migration and Expansion Map

Paper II was audited before this rewrite. Its refinement, filtration, lattice separation, and defect interface was already complete, so it was left unchanged. All work in this phase was devoted to Paper III.

## Structural decision

The revised paper makes obstruction theory the center of the article. The former finite projector formulation is replaced by a canonical cokernel construction relative to a declared correction map. Mapping cones provide the cohomological extension. A relative exact sequence now separates loss under coarsening from genuine fine vanishing. Filtered lifting and the spectral sequence describe the passage from local depth obstructions to a complete solution. Finite holonomy and smooth projector transport form the gluing part of the paper.

## Major migrations and expansions

| Earlier material or open target | Final treatment |
|---|---|
| Exact nonlinear packet coordinates | Retained as the opening representation theorem and separated from any claim of automatic solvability |
| Packet jets and higher composition | Retained and expanded by a norm bound, a term count, and structural pruning |
| Quadratic rooted trees | Strengthened to a polynomial rooted tree theorem with the Catalan case as a corollary |
| Cyclic products and Maurer Cartan equations | Retained, with an added formulation for higher operations and a divided square treatment |
| Nonlinear refinement defects | Retained and expanded to composition, iterates, fixed points, derivatives, and several refinement levels |
| Finite obstruction projector | Replaced by the universal cokernel obstruction relative to a declared correction map |
| Universal obstruction conjecture | Replaced by theorem level cokernel, naturality, quotient projector, and mapping cone results |
| Fine versus coarse obstruction | Resolved by a relative six term exact sequence and an explicit cancellation example |
| Nonlinear correction | Expanded to a quantitative right inverse theorem and Lyapunov Schmidt reduction |
| Filtered continuation | Expanded to depth obstruction classes, lift trees, complete inverse limit lifting, and Maurer Cartan lifting |
| Fine obstruction packets | Organized through the spectral sequence of a filtered correction complex |
| Elimination | Added exact local elimination and Schur derivative formulas through second order |
| Finite graph holonomy | Retained and strengthened by a fundamental cycle intertwining criterion and gauge classification |
| Projector connection material from the quantum paper | Moved upstream and expanded to a complete moving packet family |
| Local holonomy material from the local representation paper | Moved upstream as a general finite transport theorem |
| Discrete to continuous bridge | Added direct packet rotations and convergence to canonical smooth transport |
| Nonlinear signal example | Reserved for Paper V as an application of the general theory |
| Numerical certificates | Moved to the verification directory and kept outside the article body |

## Ledger coverage

The Phase 0 ledger contains 55 records whose source or destination involves Paper III.

| Source paper | Records |
|---|---:|
| III | 49 |
| IV | 1 |
| V | 1 |
| VII | 2 |
| XI | 2 |

| Disposition | Records |
|---|---:|
| `demote_to_verification` | 11 |
| `merge_into_symbolic_note_or_boundary` | 1 |
| `move_to_upstream_core` | 5 |
| `remove_duplicate_proof` | 1 |
| `replace_or_strengthen` | 5 |
| `retain_boundary` | 4 |
| `retain_core` | 28 |

## Record by record ledger

| Current ID | Source | Type | Title | Disposition | Revision or expansion |
|---|---|---|---|---|---|
| CUR-III-D01 | III | definition | Nonlinear packet conjugate | retain_core | normalize notation and ensure every object has an explicit ambient category, domain, codomain, and topology |
| CUR-III-T01 | III | theorem | Exact nonlinear packet-coordinate theorem | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-C01 | III | corollary | Dynamical equivalence | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-R01 | III | remark |  | merge_into_symbolic_note_or_boundary | compress into a formal note, boundary statement, or dependency annotation |
| CUR-III-D02 | III | definition | Packet jet | retain_core | normalize notation and ensure every object has an explicit ambient category, domain, codomain, and topology |
| CUR-III-T02 | III | theorem | Exact jet reconstruction | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-C02 | III | corollary | Packet Taylor formula | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-B01 | III | boundary |  | retain_boundary | compress into a formal note, boundary statement, or dependency annotation |
| CUR-III-T03 | III | theorem | Packet Fa\`a di Bruno formula | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-P01 | III | proposition | Term count | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-N01 | III | certificate |  | demote_to_verification | retain exact parameters, expected identities, negative controls, and source-code pointer in the verification manifest |
| CUR-III-T04 | III | theorem | Convergent quadratic tree expansion | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-C03 | III | corollary | Packet-labeled tree expansion | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-N02 | III | certificate |  | demote_to_verification | retain exact parameters, expected identities, negative controls, and source-code pointer in the verification manifest |
| CUR-III-T05 | III | theorem | Cyclic product convolution | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-N03 | III | certificate |  | demote_to_verification | retain exact parameters, expected identities, negative controls, and source-code pointer in the verification manifest |
| CUR-III-T06 | III | theorem | Polyphase Maurer--Cartan decomposition | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-D03 | III | definition | Divided square | retain_core | normalize notation and ensure every object has an explicit ambient category, domain, codomain, and topology |
| CUR-III-B02 | III | boundary |  | retain_boundary | compress into a formal note, boundary statement, or dependency annotation |
| CUR-III-N04 | III | certificate |  | demote_to_verification | retain exact parameters, expected identities, negative controls, and source-code pointer in the verification manifest |
| CUR-III-D04 | III | definition | Refinement defect | retain_core | normalize notation and ensure every object has an explicit ambient category, domain, codomain, and topology |
| CUR-III-T07 | III | theorem | Iterated nonlinear defect bound | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-T08 | III | theorem | Fixed-point refinement stability | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-C04 | III | corollary | Multilevel bound | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-N05 | III | certificate |  | demote_to_verification | retain exact parameters, expected identities, negative controls, and source-code pointer in the verification manifest |
| CUR-III-T09 | III | theorem | Linear defect product rule | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-P02 | III | proposition | Nonlinear composition bound | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-N06 | III | certificate |  | demote_to_verification | retain exact parameters, expected identities, negative controls, and source-code pointer in the verification manifest |
| CUR-III-T10 | III | theorem | Obstruction-projector criterion | replace_or_strengthen | use cokernels/cofibers as universal obstruction objects; retain Moore-Penrose projectors only after a splitting; demote to the split Hilbert realization of a new universal cokernel/cofiber obstruction theorem |
| CUR-III-D05 | III | definition | Obstruction packet | replace_or_strengthen | use cokernels/cofibers as universal obstruction objects; retain Moore-Penrose projectors only after a splitting; replace projector-first definition by cokernel/cofiber definition |
| CUR-III-N07 | III | certificate |  | demote_to_verification | use cokernels/cofibers as universal obstruction objects; retain Moore-Penrose projectors only after a splitting |
| CUR-III-T11 | III | theorem | Contraction correction theorem | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-N08 | III | certificate |  | demote_to_verification | retain exact parameters, expected identities, negative controls, and source-code pointer in the verification manifest |
| CUR-III-D06 | III | definition | Depth-$m$ obstruction | retain_core | normalize notation and ensure every object has an explicit ambient category, domain, codomain, and topology |
| CUR-III-T12 | III | theorem | Filtered lifting criterion | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-B03 | III | boundary |  | retain_boundary | compress into a formal note, boundary statement, or dependency annotation |
| CUR-III-T13 | III | theorem | Nonlinear Schur derivative | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-N09 | III | certificate |  | demote_to_verification | retain exact parameters, expected identities, negative controls, and source-code pointer in the verification manifest |
| CUR-III-D07 | III | definition | Gauge change | retain_core | normalize notation and ensure every object has an explicit ambient category, domain, codomain, and topology |
| CUR-III-P03 | III | proposition | Gauge covariance of holonomy | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-T14 | III | theorem | Spanning-tree normalization | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-T15 | III | theorem | Finite cycle-gluing criterion | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-C05 | III | corollary | Number of independent cycle packets | retain_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-III-N10 | III | certificate |  | demote_to_verification | retain exact parameters, expected identities, negative controls, and source-code pointer in the verification manifest |
| CUR-III-N11 | III | certificate |  | demote_to_verification | retain exact parameters, expected identities, negative controls, and source-code pointer in the verification manifest |
| CUR-III-Q01 | III | conjecture | Universal packet-obstruction principle | replace_or_strengthen | replace a single universal conjecture by universal property, filtered spectral sequence, and realization schema; promote a restricted, universal-property formulation to theorem target; split Hilbert projector as corollary |
| CUR-III-Q02 | III | conjecture | Obstruction refinement | replace_or_strengthen | replace a single universal conjecture by universal property, filtered spectral sequence, and realization schema; replace vague refinement conjecture by filtered-complex spectral sequence theorem target |
| CUR-III-Q03 | III | conjecture | Natural realization | replace_or_strengthen | replace a single universal conjecture by universal property, filtered spectral sequence, and realization schema; replace broad naturality conjecture by explicit realization schema and functoriality theorem target |
| CUR-III-B04 | III | boundary |  | retain_boundary | replace a single universal conjecture by universal property, filtered spectral sequence, and realization schema |
| CUR-IV-E07 | IV | example | Catalan seed | move_to_upstream_core | retain only after theorem spine is frozen; classify as minimal example, substantive realization, or negative control |
| CUR-V-T10 | V | theorem | Cyclic product law | remove_duplicate_proof | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-VII-T11 | VII | theorem | Canonical packet connection | move_to_upstream_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
| CUR-VII-CI01 | VII | classical | Projected connection | move_to_upstream_core | attach an exact external theorem statement and applicability checklist; do not reproduce as a seed-calculus theorem |
| CUR-XI-D01 | XI | definition | Cycle holonomy | move_to_upstream_core | normalize notation and ensure every object has an explicit ambient category, domain, codomain, and topology |
| CUR-XI-T05 | XI | theorem | Finite scalar-holonomy bridge | move_to_upstream_core | preserve mathematical content, normalize notation, expose exact hypotheses, and place proof dependencies before the proof |
