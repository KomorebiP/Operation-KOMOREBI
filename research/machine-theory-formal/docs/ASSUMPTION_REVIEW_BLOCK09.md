# Block 09 — assumption and quantifier review

**Two admitted source statements: Core 6.1 and Core 6.2.**

| Obligation | Formal treatment | Boundary |
|---|---|---|
| Finite candidate grammar | A literal ordered `List P` | No search beyond its supplied entries |
| Complete finite context family | `Task.contexts` and `Task.complete` | No unobserved-domain conclusion from training fit |
| Correct teacher replies | General `TruthfulProtocol` requires actual disagreement/correctness | No empirical or fallible-label oracle is silently accepted |
| Arbitrary truthful choice | Relation allows different replies after different histories | Exact trace comparison later fixes one deterministic teacher |
| Earliest consistent selection | `select` over the original grammar; `scan_protocol` proof | Not just earliest globally correct output after arbitrary calls |
| Persistent evidence | Rejections prepended; old and new retention proved | Forgetful implementation has a concrete repeated-submission counterexample |
| Duplicate syntax | General no-repeat theorem needs no `G.Nodup` assumption | Bound by list length may be nonsharp |
| Pure total semantics | Interpretation is a mathematical function | Effects, partial execution and hidden interpreter state are outside this model |
| Key soundness | Equal keys imply equal interpreted values on all admitted contexts | No converse, completeness, confluence or probe-only identification assumed |
| Original syntax | First AST is retained literally | A cheaper normalized replacement is a different contract |
| Common target and context order | Same Task argument on both sides | Mutating either changes the comparison |
| Exact metering | Short-circuit retained tests; teacher tests separately; preparation key comparisons separately | These are not total CPU instructions or bytes |
| Interruptions | Distinct suspended constructor with actual pending suffix and evidence | No arbitrary wall-clock timeout interpreted as `none` |
| Empty grammar/context | Explicit kernel-checked examples | Vacuous correctness is reported, not called learning |
| Generality of numeric examples | Three fixed contexts and eight displayed candidate expressions | Not a rerun of the older 3,960-expression study |

The source statements required no mathematical weakening or prose revision. Core 6.1's reply independence is explicitly formalized rather than silently restricting it to the reference first-disagreement teacher. Core 6.2 uses the same canonical teacher, interpreter, target, candidate order and retained-example order. Its output includes the complete sequence of submitted syntaxes and replies, not merely a final class or answer.

The supplied arithmetic key has a proof for every natural-number prefix independently of target labels. It is not presented as an autonomously learned equation library. Candidate enumeration, the original syntax, interpretation, oracle access and key function are substantial supplied structure.

The finite-run semantics, the mathematical target, the teacher implementation and the host process must not be conflated. Formal acceptance does not establish that an external observed world follows the model or that a host executable refines this Lean definition. These conditional theorems remain complete within their declared mathematical scope.
