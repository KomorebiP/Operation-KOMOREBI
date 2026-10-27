# Exact formalization coverage — Logical Resolution v0.1

## Completed execution

PASS: eight library modules, 73 named theorem declarations, 54 definitions, one
abbreviation, two structures, and two inductive syntaxes. All 132 explicit named
declarations are axiom-audited. Six new modules contribute 50 theorem declarations,
37 definitions, and two inductive syntaxes. These counts include routine lemmas,
not 50 claims of historical novelty.

Only `propext`, `Classical.choice`, and `Quot.sound` occur. No custom project axiom,
`sorryAx`, or `Lean.ofReduceBool` occurs in accepted dependencies. All library files
pass warnings-as-errors. A positive control accepts; two false-claim controls and
a placeholder control reject. All accepted input hashes are unchanged.

Toolchain: Lean 4.34.0-rc2, commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`, with matching Std. No Mathlib import is used.

| Module | Exact checked scope |
|---|---|
| RepresentationCore (inherited unchanged) | Unary deterministic system, all-word equivalence, exact transport and actual quotient |
| FiniteCertificates (inherited unchanged) | Finite horizons, distinguishing words, sufficient tests and finite local transport checks |
| ObservationSyntax | Well-scoped value terms and formulas, binder semantics, exact quantified preservation under SURJECTIVE transport, actual quotient preservation |
| LogicalHorizon | Full behavior iff observational qf-type agreement iff observational formula agreement; finite word-depth characterization at every quantifier rank; distinguishing atomic formulas |
| SemanticBoundaries | Actual state-equality/cardinality counterexamples, failure of nonsurjective quantified preservation, qf preservation without surjectivity, no uniform QE across a two-model example |
| StreamBoundary | Actual infinite stream dynamics; behavior equals stream identity; no uniform finite horizon; no single finite observational formula defines full behavior |
| FiniteDefinability | Pair-atom schema, finite code equality formula, exact depth/rank, certified all-word definability under the local closure contract |
| ConcreteLogical | Explicit 8-state/4-state example, verified quotient, all-formula transport, finite formula defining complete behavior |

## Crucial boundaries

The language has STATE quantifiers and VALUE equality, not state equality. Its
fixed value sort includes literals for all values. These restrictions are part
of every scope claim. The depth/rank collapse is within a fixed structure and
this fragment, not uniform quantifier elimination or a theorem about full logical
types. The stream nondefinability theorem excludes this fragment only.

The custom syntax has not been embedded into Mathlib's standard first-order
syntax. No compactness, elimination of imaginaries, saturation, ultraproduct,
forcing, arbitrary relational-profile, or historical novelty theorem is claimed.
Python evaluation and discovery, the parser interface, and the textual exposition
are not kernel-verified programs. Semantic proof audit is self-review.

Only TWO semantic predecessor modules were reused and rebuilt. The frozen parent
archive is included for provenance, not claimed to have been entirely rechecked.
