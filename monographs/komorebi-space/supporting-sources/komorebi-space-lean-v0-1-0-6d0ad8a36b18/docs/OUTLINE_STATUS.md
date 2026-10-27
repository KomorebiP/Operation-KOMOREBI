# Status of the original fifty-section outline

The status applies to this release, not to unrelated Komorebi work. “Restricted” means an explicit special case or conditional theorem is checked. “Target” means no theorem establishing that section is claimed. A definition or conditional theorem is not counted as an unconditional existence result.

| Original section | Consolidated status |
|---|---|
| I. Resolution doctrine | Restricted: sequential towers in arbitrary categories; concrete type-valued systems with all restriction maps. |
| II. Exact transformation theory | Restricted: exact fixed-level maps form a category. Full pro-category Hom formula/comparison not formalized. |
| III. Premorphisms | Checked: levelwise families on a common schedule. Arbitrary source reindexing remains a target. |
| IV. Residual obstruction | Checked: typed naturality differential and exactness iff its vanishing. |
| V. Residual valuation | Restricted: norms in specified normed models, real residual functions with explicit hypotheses. No universal aggregation doctrine. |
| VI. Double category | Restricted: category of exact tower maps and horizontal/vertical square-pasting identities. No bundled residual double category. |
| VII. Composition | Checked: exact-core composition and precise Leibniz identity. The unsupported mixed term is removed. |
| VIII. Residual geometry | Corrected and restricted: independent subadditive cost gives directed-distance laws. Compatibility cost alone can collapse to zero. |
| IX. Curvature | Checked as additive square defect. Not asserted to be a geometric connection curvature in full generality. |
| X. Horizontal composition | Checked categorically and quantitatively in normed rings. |
| XI. Residual Stokes | Restricted: finite transported telescopes from supplied certified path swaps. Unweighted operator summation is not asserted. |
| XII. Coupled cell complex | Target: no universal cubical/simplicial complex is constructed. |
| XIII. Cochain theory | Restricted: an explicit three-term additive complex and its degree-two quotient. |
| XIV. Curvature cocycle | Restricted: cocycle membership must be supplied/proved in a specified complex. Automatic Bianchi claims are not retained. |
| XV. Flattening | Checked for the supplied complex and for the stronger semantics-constrained quotient. |
| XVI. Higher obstruction tower | Target. Higher-degree existence and Maurer–Cartan identities not formalized. |
| XVII. Obstruction norm | Checked: distance to a subgroup, closure criterion, and closed-subgroup criterion. |
| XVIII. Obstruction profile | Restricted: nonnegative decreasing scalar profiles and a sampling counterexample. No universal target category of profiles. |
| XIX. Cofinal invariance | Checked for realized sequential inverse limits and restricted profile vanishing. Arbitrary residual invariance is refuted. |
| XX. Completion | Checked: concrete inverse-limit points and complete-metric convergence are separate constructions. No blanket homotopy-limit identification. |
| XXI. Exactification | Checked with explicit completeness, lower semicontinuity, nonnegativity, product decay and summability. |
| XXII. Geometric special case | Checked with the residual-based tail estimate. |
| XXIII. Persistent obstruction | Checked for an eventual positive lower floor and all admissible correction sequences. |
| XXIV. Asymptotic flattening | Restricted: closedness/closure distinction is checked. No claim that arbitrary asymptotic flatness realizes a global object. |
| XXV. Globalization | Restricted: exactification plus semantic preservation; path uniqueness requires an explicit vanishing pairwise budget. |
| XXVI. Representation stack | Target. No site, cover class, or effective descent theorem has been supplied. |
| XXVII. Total Grothendieck space | Target. The categorical and analytic cores are not claimed to constitute this construction. |
| XXVIII. Connection | Target. Pullback and pushforward variance must be settled before a connection is defined. |
| XXIX. Holonomy | Target. General loop/path realization not formalized. |
| XXX. Nonabelian obstruction | Target. Only a concrete additive finite cocycle is checked. |
| XXXI. Projective model | Restricted: a nontrivial additive Z/2-valued cocycle on (Z/2)^2, not the full matrix representation theory. |
| XXXII. p-adic model | Target as a p-adic instance. Generic inverse-limit realization is checked; the Z_p identification and 1-Lipschitz classification are not. |
| XXXIII. Operator model | Restricted: exact compression-shell identity and normed-ring bounds. Compact-operator convergence not formalized. |
| XXXIV. Galois/profinite model | Target. No Galois/holonomy or Langlands identification theorem is claimed. |
| XXXV. Functoriality | Restricted: identity/composition laws for exact limit maps. No universal X ↦ K(X) construction. |
| XXXVI. K-equivalence | Target in the proposed generality. A concrete cofinal point equivalence is checked. |
| XXXVII. Universal grammar closure | Target. Free algebraic generation and semantic closure are not identified by assumption. |
| XXXVIII. Exact core | Checked for strict tower maps. Equivalence with all Pro(C) is not claimed. |
| XXXIX. Resolvable/obstructed systems | Restricted: precise sufficient convergence and persistent-floor obstruction criteria, not an exhaustive trichotomy. |
| XL. Resolution spectrum | Target. Raw rates depend on the chosen resolution parameter. |
| XLI. Residual filtration | Restricted to the supplied cost axioms. No general filtered category is bundled. |
| XLII. Associated graded | Target. Quotients of arbitrary collections of arrows are not defined without algebraic structure. |
| XLIII. Descent | Target. Obstruction-class vanishing is not silently equated with effective descent. |
| XLIV. Spectral sequence | Target. No spectral sequence construction or convergence theorem. |
| XLV. Double complex | Corrected and restricted: anticommuting square-zero additive maps have square-zero sum. Original sign inconsistency removed. |
| XLVI. Two axes | Interpretation only beyond the proved square identities. |
| XLVII. Fundamental principle | Restricted: one-way theorems with explicit hypotheses, plus a constrained algebraic equivalence. No unconditional biconditional. |
| XLVIII. Theorem program | Replaced by the actual declaration index and this status table. |
| XLIX. Universal minimal definition | Replaced in the checked release by a layered core. The stack-based tuple remains a research target. |
| L. Mathematical thesis | Supported in stated algebraic, inverse-limit and complete-metric models, not as an unrestricted universal principle. |

## Highest-leverage remaining bridges

1. Equip concrete candidate tower spaces with complete norms and prove boundedness/continuity of their actual differentials and protected semantic maps. The current algebraic tower bridge and analytic exactification theorem then connect through checked hypotheses.
2. Construct reindexed transports and their eventual-equality quotient, then prove the appropriate pro-category comparison.
3. Specify an actual site and a concrete obstruction complex before pursuing descent, stacks, higher cohomology, or spectral sequences.

None of these targets appears as an unproved axiom or placeholder in the positive Lean library.
