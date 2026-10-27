# Mathematical self-review: v0.6

Primary verdict for the new source statements: proved as written by completed Lean
module checks; the retained cold/axiom/control result must be read in RESULTS.md.
This is authoring-assistant self-review, not an independent agent or referee.

| Obligation | Assessment | Concrete reason |
|---|---|---|
| Positive pivot domain | Passed | Basis constructor requires an actual proof of positive integer pivot |
| Zero-dimensional case | Passed | Empty synthesis/coordinates/insertion; kernel-computed example |
| Membership soundness and completeness | Passed | Recursive Represents equivalence and returned-coefficient reconstruction |
| Torsion/nonunit safety | Passed | Integer preimage includes m Z^d; no modular nonunit division |
| Bezout premise | Passed | Actual Int.gcdA/gcdB and imported gcd theorem, not an assumed solver output |
| Insertion forward and reverse spans | Passed | Determinant-one update with explicit integral inverse |
| Integer representative choice | Passed | Kernel m Z^d included; reduction/lift identity |
| Cached basis invariant | Passed | Exact preimage invariant propagated through every acceptance |
| Word orientation | Passed | Inherited actual testValue/rowRight semantics, right action prepends |
| Exhausted fuel | Passed | Returns none, including zero-fuel terminal call |
| Universal enough-fuel claim | Passed in stated prime-power regime | Reuses checked rank/worklist termination via actual output equality |
| Logical semantics | Passed for inherited fragment | Builds FiniteCodeCertificate and standard guarded formula theorem |
| Regression instance evaluation | Actual kernel evaluation | Does not consume old membership witnesses or traces |
| Arbitrary positive modulus | Membership/update covered | Enough-fuel bound remains separately prime-power-scoped |
| Canonical Smith form | Out of scope | New basis is integer echelon, not claimed canonical or minimal modular basis |
| Polynomial bit complexity | Not addressed | Stored coefficients are not reduced; growth may dominate |
| Python/source transcription | Finite independent audit only | Port and parser are not extracted/verified programs |
| Historical novelty | Not addressed | Standard integer-lattice mechanism, no priority verdict |
