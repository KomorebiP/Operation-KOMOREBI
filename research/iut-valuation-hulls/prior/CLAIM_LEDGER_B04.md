# Claim ledger: IUT / Komorebi Hodge reduct experiment B04

| Claim | Exact scope | Evidence | Status |
| --- | --- | --- | --- |
| R1 | Strong reduct link preserves powers and torsion equations | `KTG/HodgeReduct.lean` | Lean proved |
| R2 | A fixed reduct link lifts additively iff it has no additive-obstruction witness | `KTG/HodgeReduct.lean` | Lean proved |
| R3 | With inhabited output, factorization of an observable through a reduct iff constancy on its fibers | `KTG/HodgeReduct.lean` | Lean proved |
| R4 | `F_5` inversion preserves multiplication, is involutive, fails additive compatibility | `KTG/HodgeFinite.lean` | Lean proved |
| R5 | Transported addition forms a commutative additive group and distributes with unchanged multiplication on `Fin 5` | `KTG/HodgeFinite.lean` | Lean proved (finite exhaustive decision) |
| R6 | Two layers with same multiplication are `KTG.KTransport.Related` and disagree on `1+1` | `KTG/HodgeFinite.lean` | Lean proved |
| R7 | Uniform reconstruction of labelled `1+1` from multiplication table alone is impossible in this class | `KTG/HodgeFinite.lean` | Lean proved |
| R8 | For a fixed labelled `F_p` multiplication, exactly `phi(p-1)` field additions exist | `notes/BRIDGE_NOTE.md`, Section 4 | Mathematical proof supplied, not separately formalized |
| R9 | Six small prime fields satisfy the transported field identities and have the expected number of distinct tables | `experiments/finite_theaters.py` | Exhaustively tested |
| N1 | False additive preservation and false reconstruction claims | `experiments/negative_controls/*.lean` | Lean intentionally rejects |
| IUT1 | Actual IUT Hodge theaters or theta links instantiated | IUT I/II originals, predecessor source map | **Open** |
| IUT2 | Actual multiradiality/coricity and source-specific `SourceWitnessTheorem` proved | Prior KTG Block03, RR5 IUT route | **Open** |
| ABC | Unrestricted abc established or IUT III Corollary 3.12 proved/disproved | No such proof | **Open** |

All standard mathematical statements should be interpreted in their explicit model. The formal witness obstruction is not an IUT counterexample.
