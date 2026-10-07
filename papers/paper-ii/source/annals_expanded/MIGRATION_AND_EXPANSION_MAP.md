# Migration and Expansion Map

## Article identity

The original project manuscript was titled *Projector Resolved Seed Calculus II: Polyphase Refinement, Weighted Transfer, and Dyadic Odd Resolution*. The journal article is titled *Refinement Towers, Weighted Transfer, and Integral Separation of Operator Packets*.

The journal version is not a change of class file alone. It reorganizes the article around four mathematical questions.

1. How do exact packet coordinates refine across several scales
2. How does a positive weight transfer system invert path by path
3. When does a rational packet decomposition split the chosen integral lattice
4. How does a fine to coarse defect propagate through operator functions

## Section migration

| Original material | Journal location | Treatment |
|---|---|---|
| The refinement problem | Introduction and Section 2 | Rewritten as four distinct notions of depth |
| Nested packet systems | Section 3 | Retained and expanded with coherence, common refinements, support reflection, and a universal common refinement statement |
| Residue and polyphase selectors | Section 4 | Retained over arbitrary coefficient rings, then related to character averages only under the required root and division hypotheses |
| Dyadic odd factorization | Section 4 | Absorbed into the coprime residue factorization theorem |
| Weighted transfer paths | Section 5 | Strengthened with a block path formula, minimum path weights, an acyclic termination theorem, inverse stability, and exact finite precision truncation |
| Transfer zeta functions | Section 6 | Recast as rational weighted transfer series, with recurrence and multigraded extensions |
| Integral spectral packets | Sections 7 and 8 | Split into a resultant upper bound and an exact lattice theorem |
| Exceptional dyadic sign split | Section 9 | Retained and placed after the general lattice theorem, with a general character average integrality statement |
| Smith weights and lifting | Section 10 | Strengthened to a rectangular congruence theorem with exact solvability and solution counts |
| Linear refinement defects | Section 11 | Expanded from powers to polynomials, resolvents, holomorphic functions, exponentials, and multilevel towers |
| Smith chart realization | Removed from the core article | Reserved for the later signal realization where it fits the analytic narrative |
| Numerical certificates | Verification directory | Removed from the article body and retained as executable support |
| Project boundaries and release metadata | Scope section and package documents | Rewritten in journal form or moved out of the manuscript |

## Main additions

The largest new result is the exact lattice gluing theorem. If
\[
V=\bigoplus_\alpha V_\alpha
\]
is a rational packet decomposition and
\[
\Lambda_{\mathrm{{split}}}=\bigoplus_\alpha(\Lambda\cap V_\alpha),
\]
then the common packet denominator is exactly the exponent of
\[
\Lambda/\Lambda_{\mathrm{{split}}}.
\]
The largest Smith exponent is therefore the exact precision loss. The resultant remains an explicit upper bound, but it is no longer presented as the intrinsic answer.

The journal version also adds common refinements of commuting packet systems, pathwise inverse blocks, minimum path weights, several coprime spectral projectors, refinement monotonicity of the lattice weight, an exact necessary and sufficient precision delay, the full rectangular Smith congruence count, and the holomorphic and exponential defect formulas.

## Result counts

The original source contained 15 proof environments. The journal manuscript contains 43 proof environments. The increase comes from splitting compressed arguments into separate results and from proving the added lattice, path, congruence, and defect statements.
