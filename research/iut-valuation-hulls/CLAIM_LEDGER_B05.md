# Claim ledger — Komorebi × IUT B05

| Claim | Scope and evidence | Verification | Status |
|---|---|---|---|
| B05-A1 | Unit saturation iff source contains same valuation level; `KTG/ValuationHulls.lean` | Lean | Proved in abstract valuation shell |
| B05-A2 | Integral multiplier closure iff source contains no deeper-than-target valuation; same module | Lean | Proved in abstract valuation shell |
| B05-A3 | Strictly shallower pilot cannot lie in the integral closure; unit multiplication cannot cross levels | Lean | Proved for stated closure |
| B05-C1 | Joint ideal hull exponent is `min(a,b)`; optimal cost `a-min(a,b)` | Lean | Proved for DVR exponent model |
| B05-C2 | Weighted diagonal cost `m Σ(s_j-1)` and unboundedness for positive slope | Lean | Proved for listed weights `s_j≥1` |
| B05-C3 | Matrix GL_k(O) determinant volume bound | ABC IUT RR5 mathematical proof | Inherited mathematical proof, **not B05 Lean** |
| B05-N1 | Discrete negative-depth comparison and joint-hull repair cost | Lean | Proved in surrogate |
| B05-N2 | Normalized approximation witness implies bound with explicit error, with branch-specificity | Lean | Proved, conditional numeric interface |
| B05-F1 | `F17` twist `x↦x^9` preserves multiplication and `1+1=2` but changes `1+2` | Lean | Proved |
| B05-F2 | Transported F17 laws are valid field operations; full reduct + first additive anchor cannot reconstruct second anchor | Lean | Proved |
| B05-V1 | 28 modules, 1 entry point; clean build, independent compilation, source checks | `verification/b05/verification.json` | PASS |
| IUT O1–O6 | Actual theta links, hulls, log shells, normalized witness / IUT III Cor 3.12 | No real source instantiation | **OPEN** |
| ABC | Unrestricted abc | No proof | **OPEN** |

No B05 result is advertised as an IUT counterexample or source theorem.
