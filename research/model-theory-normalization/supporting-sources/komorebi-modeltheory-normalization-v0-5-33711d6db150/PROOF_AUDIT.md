# v0.5 mathematical self-review

Verdict: **proved as written for the stated membership-checker, replay, and guarded-
oracle propositions**, conditional only on the ordinary imported library foundations.
Final compiler success is recorded separately. This is authoring-assistant review,
not an independent reviewer or a novelty assessment.

| Obligation | Assessment |
|---|---|
| Positive witness means actual span membership | Direct finite linear-combination lemma, with exact list-length check |
| Negative witness excludes every coefficient tuple | Actual linear functional vanishes on every generator and is nonzero on target |
| Torsion retained | Arithmetic in the actual commutative ring, no inverse of a nonunit in the checker |
| Invalid evidence distinguished from nonmembership | `none` versus `some false`, explicit tests |
| Correct source candidate | Evaluated from reconstructed FIFO word/observation queue, not supplied by evidence |
| No premature or trailing successful trace | Both lists must be empty at successful termination |
| Whole trace certifies the actual discovery result | Constructs inherited QueueTrace, then proves equality with the enumerative reference |
| Arbitrarily wrong proposer cannot change mathematical output | Checked branch or proved fallback, exact oracle substitution |
| A proposer terminates | The generic function is total in Lean; no claim about a hanging external process |
| All future words and all source states | Inherited actual observable-span and standard-formula theorems |
| Python basis compression preserves raw provenance | Independently checked complete traces and small exhaustive tests; no universal program-verification claim |
| Minimum raw test count or formula size | Not claimed; stress case has 24 accepted rows but final generator count one |
| General nonmember always has scalar separator | Not claimed over every ring; guarded fallback does not need that premise |
| JSON source equals intended mathematical problem | Literal transcription audited, informal interpretation not decided by the kernel |
| Proof execution independent of native_decide | Export uses `decide +kernel`; axiom audit rejects Lean.ofReduceBool |

The dependency chain is finite witness equations -> sound membership decision ->
certified FIFO trace -> full observable module -> exact reference output and
standard first-order definition. The guarded backend composes either the new
verified checker or the old verified finite search, never an unchecked Boolean.
