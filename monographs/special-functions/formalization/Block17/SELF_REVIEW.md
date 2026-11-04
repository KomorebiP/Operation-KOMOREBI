# Focused self-review of the guarded majorant

Verdict: **proved as written for the registered exact algorithm specification**.
Provenance: self-review, not independent review. Source SHA-256
`349f0d3ae54d93aa5035cee180e26c8d8ba30169c478511136af20cc6d421b0c`; mathematical base `200a2798532028f863f923028cb0ead95563975a`.

Claim card: rational Q,R; natural step budget; Boolean post-update size guard.
Success gives a first-small trace of bounded length, terminal power condition
and the fuel-model value. Analytic conclusions retain strict positive
contractions, nonnegative target radius, and S>x>=0 for endpoints. Abstract
resource inputs distinguish invalid tags, zero step budget and positive bits.

Dependency graph: trace induction -> terminal and adequate-fuel identities;
budget induction <-> trace with length bound; trace foldr -> fuel majorant.
List induction -> guarded-fold success/value/check equivalence and bit failure.
These facts -> guarded majorant success -> Block15/16 actual-function bounds
and array-polynomial endpoint enclosures. Ordered wrapper case analysis ->
input/error order and checked success. No Python computation is a proof leaf.

| Obligation | Result | Evidence |
| --- | --- | --- |
| Strict first-small threshold | passed | Trace records R>=1 and stops only at R<1; equality at 1 is not small. |
| Step-budget equivalence | passed | Build success iff trace exists with length<=budget. |
| Terminal power | passed | Child radius Q*R and length successor give Q^k*R exactly. |
| Fold orientation | passed | foldr on original ladder equals iteration on reversed ladder; exact [2,1] example separates wrong orientation. |
| Post-update guard | passed | Every unwinding update is checked, including inner updates; seed is not checked. |
| Explicit failures | passed | Ladder cannot emit bit error, fold cannot emit step error; each resource error propagates. |
| Success is essential | passed | Actual-function theorem requires successful guarded return; the omitted-success control is rejected. |
| Zero and negative radii | passed | Wrapper rejects negative radius after scales; valid scales at zero bypass all resource checks. |
| Resource validation order | passed | Invalid step tag precedes bit validation, with positive-bit requirement. |
| Binary width | passed as a definition | Exact rational numerator/denominator mathematical size; runtime bit_length implementation is not certified. |
| Analytic transfer | passed | Existing exact coefficient, majorant and canonical-function identifications are retained. |
| Runtime/source execution refinement | not addressed | Python interpreter, Fraction, type/exception objects, mutation and dictionary semantics remain separate. |

Four controls reject omitted success, wrong fold direction, mandatory seed
checking and placeholders. The positive fixture includes exact half-scale
trace/value, step and bit failures, radius one, invalid scales at zero,
zero-before-resources and an oversized unchecked seed. These are kernel-checked
exact examples; they supplement universal proofs rather than replace them.
All 66 fresh steps pass. Only the declared standard axioms are allowed.
No gap remains in the registered algorithm model; full Python refinement
and whole-manuscript coverage remain open.
