# Focused self-review of factorial normalization

Primary verdict: **proved as written for the registered mathematical
recurrence and finite-array contract**. Provenance: self-review, not independent.
Exact source SHA-256 `907fd0fa37a59dff472088a2afa6cc4f9bb22663ce9d153378560cfdeaa549f8`; base `b5faff8889c48150e1fa41be11b6a3d2c47f493b`.

Claim card: arbitrary rational scale tuples, every n,N natural, both Fin 2
components. Binomial derivative recurrence uniquely equals factorial-scaled
ordinary recurrence. A finite append model equals the inclusive infinite
prefix; enumerate/divide conversion and enumerate/multiply/sum yield the
canonical polynomial. Analytic endpoint transfer retains strict positive
contractions, x>=0, S>x and adequate fuel.

Dependency graph: pinned Nat choose-factorial identity + explicit index
arithmetic -> rational factorial product -> scaled ordinary step -> binomial
solution uniqueness -> all-index equality. Prefix locality + list index laws
-> finite append invariant -> indexed conversion -> polynomial equality.
Block15 coefficient casts and endpoint theorem -> real identification and
enclosure. No Python output is used as a trusted proof leaf.

| Obligation | Result | Evidence |
| --- | --- | --- |
| Complementary factorial index | passed | i<=n proves 2n+2-(2i+1)=2(n-i)+1. |
| Cancellation | passed | All factorial casts and 2n+3 are explicitly nonzero over Q. |
| Minimum index | passed | oddFactorial(0)=1 and derivative base pair is (1,1). |
| First nonconstant coefficient | passed | A1=2qr, B1=2ab, divided by 3! yields qr/3,ab/3. |
| Source index shift | passed | Source iteration m=n+1 uses choose(2n+2,2i+1), i=0..n and j=n-i. |
| Both-row dependence | passed | Both appended entries use the same prior U,V prefix; no current new value is read. |
| Strong induction | passed | Every dependency i,n-i is smaller than output n+1. |
| Finite array bounds | passed | Length N+1 and every read index are proved; getD fallback is unreachable. |
| Enumerate divisor | passed | MapIdx index n divides by (2n+1)!, preserving positions. |
| Polynomial sum | passed | Indexed list sum equals Finset.range(N+1), then canonical polynomial. |
| Coefficient domain | passed | Algebraic results impose no positivity/contraction; signed fixture is accepted. |
| Analytic transfer | passed | Original strict contraction, nonnegative x, strict outer radius and terminal-fuel guards retained. |
| Python runtime/stdlib correspondence | not addressed | Mathematical paired-list model is not source-program execution semantics. |
| Guarded ladder/dictionary | not addressed | Next source-bound refinement obligations. |

The four rejection controls exercise missing factorials, even-factorial
normalization, an exclusive array length and placeholders. Type rejection
alone does not prove the corresponding universal negation; the exact first
coefficient also explains why the false normalizations fail. The positive
fixture checks arbitrary-index interfaces, zero last index, signed data,
noncontracting data, array-polynomial equality and analytic enclosure.

All 63 source-bound steps pass, including sixteen kernel replays and 396
fresh theorem axiom audits. The source theorem list exactly matches the
30-name declaration map. Cached imports and inherited 39-name finite-core
evidence are disclosed. No gap remains in this registered contract; full
Python refinement and whole-appendix/manuscript coverage remain open.
