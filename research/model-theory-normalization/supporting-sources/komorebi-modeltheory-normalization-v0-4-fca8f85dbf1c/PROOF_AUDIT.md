# Self-review of the discovery-to-definition theorem

**Verdict: proved as written for the declared finite-linear reference algorithm.**
This is authoring-assistant semantic self-review backed by the recorded Lean
kernel checks, not an independent researcher or a novelty audit.

## Dependency graph

Lagrange/cardinality + finite module --> bounded strict rank.
Actual test-word recursion + span laws --> invariant frontier --> exact terminal span.
Bounded rank + queue potential --> enough-fuel termination and size bounds.
Finite linear-combination theorem --> executable correct enumeration oracle.
Actual row/evaluation identity + exact span --> local observation-code certificate.
Inherited standard syntax semantics --> finite defining formula and IsQF/Definable.
Branch witnesses + inductive FIFO trace --> same exact span --> same reference result.

## Obligations checked

| Obligation | Verdict |
|---|---|
| Correct coefficient ring including zero divisors | Passed: submodule cardinality, not field rank |
| Proper prefix/right-row word order | Passed: `testValue_behavior`; generated noncommuting queue checks |
| Seed/root inclusion | Passed: frontier initialized by every declared observation |
| Closure at stop, including dependent skipped rows | Passed: skip/accept lemmas preserve both frontier clauses |
| Reverse inclusion/no invented rows | Passed: every retained item is a real finite word/observation |
| Finite termination, not just Option structural recursion | Passed: `finitePrimeDiscover_total_correct` proves some-result at stated fuel |
| An actual membership implementation | Passed: enumerationOracle with finite coefficient search and proof |
| Rank not secretly computed by the algorithm | Passed: proof-only noncomputable rank; executable fuel uses rd |
| r=0, d=0, k=0, o=0 | Passed universally and through concrete reference cases |
| Fuel cap not confused with mathematical failure | Passed: insufficient-fuel theorem and resource refusal tests |
| Arbitrary states/words, not finite simulation horizon | Passed: universal observable-span and standard semantic theorem |
| Fully checked loop trace versus trusted success bit | Passed: QueueTrace constructors require each exact branch witness |
| Fast Smith implementation universally correct | Not claimed: instance traces replace that trust obligation |
| Minimum test count, horizon or formula size | Not claimed |
| Full first-order elementarity | Out of scope: the inherited observational fragment is explicit |
| JSON/formal source equals intended informal problem | Tested literal transcription only; not a semantic oracle |

## Boundary cases and controls

Zero observations return the empty code, not an empty state space. Precision zero
is the trivial coefficient ring. The rank bound counts accepted tests, not word
candidates or tuple-enumeration steps. Torsion directions remain detectable.
A zero separating functional cannot justify an acceptance; the corresponding
Lean control rejects. A done constructor cannot discharge a pending queue.

The executable discovery primitive is now verified in its reference form. The
next genuinely separate engineering obligation is an efficient verified membership
backend or a broadly automated proof-producing optimized backend, not another
informal claim that a completed result was probably reached correctly.
