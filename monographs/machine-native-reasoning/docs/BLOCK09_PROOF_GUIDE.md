# Block 09 — mathematical proof guide

**Machine-Native Reasoning · Reviewed Core 0.2 · Cumulative companion 0.9.0**

## 1. The objects that remain fixed

`Synthesis.Task P D Y` contains a pure total interpretation `eval : P → D → Y`, a target `D → Y`, and a finite ordered context list with proof that it contains every `D`. The program type P need not be finite. The supplied grammar is a finite ordered list of original P values. Equal output values are decidable. A grammar can be empty or contain duplicate syntax entries. An empty context type is also allowed and makes every candidate vacuously correct.

`inspect` returns the first disagreement on a supplied ordered context list and the number of equality tests actually performed. It short-circuits at that disagreement. Its proof characterizes a `none` result as consistency, a `some x` result as an actual disagreement on a listed context, and its count as bounded by the list length. The full teacher uses the complete context list, so acceptance is exactly correctness on every admitted context.

No finite example is extrapolated to a larger domain. The teacher's target and complete table are supplied inputs, not discoveries or free advice. One comparison is not one processor instruction.

## 2. Core 6.1: the executable learner and its general reply contract

`scan` inspects candidates in order. Inconsistent candidates are skipped without a teacher call. A consistent candidate is submitted; acceptance terminates, while rejection prepends the returned context to the retained examples and continues. The scan is structural recursion on the remaining candidate list, so it returns a completed mathematical result rather than an ambiguous timeout marker.

The apparent difference between a one-pass scan and repeatedly selecting the earliest consistent candidate is discharged by `scan_protocol`. Its `Protocol` relation refers to the WHOLE original grammar at every teacher call. `protocol_prefix` proves that already-refuted prefixes stay unavailable as evidence grows. Thus skipping these prefixes realizes the source learner exactly.

`accepted_first` proves that the returned syntax is the first globally correct grammar member, using an explicit prefix/suffix decomposition. `exhaustion_iff` proves that a complete `none` result means precisely that no correct member remains anywhere in that grammar. The proof says nothing about programs outside the grammar.

`TruthfulProtocol` additionally permits any truthful counterexample, even a history-dependent choice. It includes open finite prefixes as well as accepted and exhausted outcomes. A rejected syntax has a retained disagreement and cannot be submitted again. Every submitted syntax belongs to the grammar. Therefore every finite interaction prefix has at most `G.length` teacher calls, even if the grammar repeats syntax. An unbounded sequence of truthful calls would contain a prefix of length `G.length+1`, which the theorem rules out. This does not rule out stalling without making any call, or bound the cost of one teacher evaluation.

Endpoints: `counterexample_guided_synthesis`, `accepted_first`, `exhaustion_iff`, `truthful_nodup`, `truthful_call_bound`, `truthful_outcome`, `no_unbounded_truthful_calls`, and `protocol_is_truthful`.

## 3. Core 6.2: deletion preserves the entire teacher history

A supplied key function satisfies `KeySound` when equal keys imply equal values on every admitted context. The reverse implication is not required. Missed equivalences waste an opportunity but do not invalidate deletion. `representatives` retains the earliest ORIGINAL syntax at each key. It never replaces that syntax with its normalized spelling.

The induction maintains `KeysRefuted`: every already-seen key is refuted by a retained example. If the next candidate has an old key, that example makes it fail before reaching the teacher. If it has a new key and is inconsistent, its existing disagreement extends the invariant. If a new-key candidate reaches the teacher and is rejected, the new context extends the invariant. If it is accepted, both searches terminate on that same syntax.

`compression_invariant` simultaneously proves equality of the final answer, every submitted original syntax/reply pair, and the final retained example list. It also proves nonincrease of retained-example comparisons and candidate visits. `ordered_compression` applies this invariant from the empty seen-key set. The result holds for any common initial retained-example list.

Because the teacher receives the same syntax in the same order, `teacher_work_preserved` gives equality of its actual context-comparison count. Teacher work is not silently removed from the ledger. `prepare` implements list-backed key lookup and records its equality comparisons; `prepare_value` proves its output is exactly the representative list.

Only retained-example comparisons and visits receive a nonincrease theorem. Index preparation, key computation, index storage, dispatch, and the physical cost of interpretation remain distinct. The result is not a total runtime improvement theorem.

Endpoints: `ordered_compression`, `representative_search_complete`, `teacher_work_preserved`, and `prepare_value`.

## 4. Pausing without fabricating an outcome

`boundedScan` has a natural-number allowance for candidate inspections. A `Progress` value is either `complete Result` or `suspended Suspension`. The suspension stores the unprocessed ordered suffix, persistent evidence, emitted transcript, and accumulated comparison/visit counts. A nonempty pending grammar and zero allowance produces suspension, not grammar exhaustion.

`resume_bounded` proves that finishing the stored residual computation reproduces the full unbounded scan, including answer, transcript, evidence, and counters. `bounded_completion_sound` proves that an already-complete budgeted result equals the full result. `enough_inspections` proves completion when the allowance is at least the grammar length.

This is an exact semantic model of suspension. It does not certify a host checkpoint serialization, crash-recovery implementation, or a time limit on one candidate inspection. Candidate-inspection fuel and teacher-call count are different units.

## 5. A small arithmetic instance

The original grammar is:

1. `a > a`
2. `0 = 1`
3. `b > a`
4. `a < b`
5. `b > C`
6. `C < b`
7. `max(a,b) > C`
8. `max(b,a) > C`

The three complete developmental contexts are `(a,b,C)=(0,3,2),(0,1,2),(3,0,2)`. The target is the stated capacity label on those contexts. The teacher submits/replies:

`a>a → context 0; b>a → context 1; b>C → context 2; max(a,b)>C → accept`.

The key identities are proved for ALL natural-number triples, not inferred from those three probes. The four retained candidates are the first syntax in each displayed pair. The reference scan has seven visited candidates and nine retained tests; the reduced scan has four and six. Both make four teacher calls and nine teacher comparisons. The exact final retained list is `[2,1,0]` on both sides.

Preparation uses ten key comparisons in the stipulated list-backed procedure. Under an illustrative equal-price account covering only those key comparisons and subsequent retained tests, four repeated tasks first make the saving strictly positive. This is NOT the complete cost of creating, verifying, storing or using the index. With one use, even this partial account is more expensive than the original scan.

At four candidate inspections, the original scan is suspended with four candidates pending, while the reduced scan is complete. Resumption of the original reproduces its uninterrupted record exactly. This difference is not a four-teacher-call timeout or evidence of infeasibility.

## 6. Counterexamples and the next boundary

A capped formula fits every developmental context but differs at `(0,5,8)`. A one-probe key merges a false Boolean function with the only correct identity function and changes acceptance into false grammar exhaustion. Retaining a later equivalent syntax changes the literal answer and transcript. Forgetting a counterexample permits repeated submission of the identical program. Changing context order changes replies. Changing the target invalidates the previous outcome. A complete context declaration cannot omit a context.

These cases distinguish syntactic selection, semantic correctness, evidence preservation and resource accounting. Core 6.4 remains separate: a training-correct capacity formula is not yet a universally justified pruning action inside the actual diagnostic compiler.
