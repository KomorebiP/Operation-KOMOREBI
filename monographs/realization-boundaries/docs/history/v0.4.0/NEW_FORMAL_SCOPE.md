# New formal scope — v0.4.0

Six modules extend the actual infinite-group development. No inherited production module is edited.

| Module | New checked content |
|---|---|
| `DiagonalHomomorphisms` | Arbitrary additive maps between rational preimages are diagonal; unique coefficients; automatic continuity; induced rational-linear quotient map. |
| `DiagonalRealization` | Exact admissibility and finite-defect criterion; equivalence classifying all homomorphisms; genuine endomorphism-ring equivalence and commutativity. |
| `EndomorphismScalars` | Unique rational quotient scalar; eventual-rational characterization; ring laws, surjectivity, and exact kernel. |
| `DiagonalAutomorphisms` | Nonzero-coordinate criterion; actual reciprocal inverse on original rank-one groups; injective, surjective, bijective equivalences in that scope. |
| `CompletionReflection` | Unique continuous extension to canonical completions; eta compatibility and coordinate formula; composition and hom-set faithfulness; supplied-map reflection. |
| `DirectSumEndomorphisms` | The complete ring End(D), actual diagonal action, and zero-coordinate preservation. |

## Mathematical interpretation

Let P be the full product of the prime cyclic groups, D its actual finite-support subgroup, and H_W the preimage of a rational subspace W of P/D. Every additive homomorphism f:H_U -> H_V has a unique coordinate family c with (f x)_p = c_p x_p. Continuity follows rather than being assumed.

For selector lines, c defines a map G_S -> G_T exactly when there is a rational r with c*u_S - s_T(r) in D. The endomorphism ring consists precisely of families eventually equal to reduction of a single rational along the selected primes. Its rational quotient scalar is a surjective ring homomorphism. The map r -> the chosen rational-section multiplier is a set-theoretic right inverse, not a proved ring-homomorphic section. A contract proves the specific half-plus-half lift failure.

For an infinite source selector, a supplied map is bijective exactly when every coordinate is nonzero. The reciprocal multiplier is proved admissible on the original groups, using the nonzero rational-line scalar. This conclusion is not generalized to all rational preimages. In particular D -> G_A remains a proper inclusion with invertible completion.

The extension to canonical profinite completions is explicitly constructed and proved continuous, eta-compatible and unique. Its coordinate action is c on all of P after the prior comparison equivalences. Thus the book's supplied-map reflection result is fully proved for paired groups, without asserting a reconstruction of an unknown group from a completion object.

## Tests protecting the boundaries

The positive contracts prove zero off-diagonal seed entries, a noninjective endomorphism with quotient scalar one, a zero-diagonal inverse failure, inadmissibility of the identity multiplier across the two constant-selector groups, nonadditivity of chosen rational lifts, and properness of D -> G_A with bijective completed map. Six new expected failures exercise these distinctions. Compiler rejection alone is not used as a mathematical counterexample.

## Explicit remaining scope

No new proof of exact cardinal seed rank, topological cyclicity, CRT cyclic identification, root-fiber cardinality, rational-dimension classification, computable presentation semantics, oracle-degree decoding, or grammar diagonalization is claimed. The global category of all residually finite groups and the exact Pro-object decoder syntax remain separate from the checked family-level completion interfaces. No Python code extraction theorem or independently implemented kernel verification is claimed.
