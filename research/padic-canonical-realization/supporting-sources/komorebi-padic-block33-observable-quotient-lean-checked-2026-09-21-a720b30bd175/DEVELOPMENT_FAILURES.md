# Block 33 development failures and recoveries

1. Two development container calls exceeded the outer tool response window. The
tracked predecessor process subsequently returned zero with a successful 2,609-job
build, and the affected new module was explicitly recompiled. Neither interrupted
call was itself treated as a pass. The authoritative later clean build and all
final phases completed without timeouts.

2. LinearObservability's first proof draft was rejected under warning-as-error
because push_neg is deprecated in the pinned environment. The equivalent push Not
tactic replaced it. No theorem statement changed.

3. The first quotient proof used ext on a linear quotient map and inadvertently
performed quotient induction twice. Explicit LinearMap.ext and one source
representative fixed the proof. A cardinality product needed commutativity, and
the finite quotient comparison needed an explicit Fintype.ofFinite instance.
These were proof elaboration repairs, not changes to mathematical scope.

4. The actual-mask draft required normalization of least coordinate support and
linear-output projections. Explicit system arguments and the observation-horizon
abbreviation resolved dependent inference. Reachability was then added and
checked from the previously proved reachable restriction theorem.

5. Finite-ring witnesses needed explicit ring-typed inequalities and normalization
of conditional coordinate functions. An ambiguous one_ne_zero invocation was
replaced with the intended finite-ring decidable statement. Expected values and
theorem conclusions were unchanged.

6. A direct leanchecker help probe failed because its subprocess could not find
lean on PATH. The authoritative replay used lake env leanchecker with the pinned
runtime first on PATH and passed. This is an environment probe failure, not a
failed theorem or successful negative control.

The development directory retains available drafts and diagnostics. The initial
integer audit passed. All 13 authoritative final verification phases passed with
frozen inputs. Four negative controls were rejected for the specifically required
false-proposition or sorry diagnostic. No inherited theorem was weakened or
retracted. No claim of a broader cross-realization minimality proof is made.
