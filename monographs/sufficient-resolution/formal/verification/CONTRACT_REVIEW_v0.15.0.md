# Contract review — v0.15.0

## Positive contract

Block 15 replaces a supplied source-norm cap in the **acceptance predicate** with the
candidate-dependent allowance `eta + delta*||x||`. The lower discrepancy inequality
then proves accepted-source norm domination relative to any feasible comparison source.
This yields fixed-true-operator consistency for accepted and near-accepted families.

## Feasibility contract

Existence of an accepted parameter is not unconditional. The proved total selector uses
`eta>0`, `tau>1`, valid true operator/data bounds, and the sufficient condition
`delta*||p|| < (tau-1)*eta`. A scaled form `delta ≤ gamma*eta` plus
`gamma*||p|| < tau-1` is also proved.

The generalized acceptance predicate itself does not contain `p` or a supplied `M`.
The selected-source construction contains the comparison source because it is an
existence theorem, not an implementable source-blind numerical algorithm.

## Negative contract

True `A=I`, available `C=0`, source/data `1`, `eta=1/10`, `delta=1`, `tau=2` gives valid
truth bounds but no generalized accepted source. Therefore neither candidate-dependent
noise nor a small fitting residual licenses unconditional model feasibility.

## Trust boundary

The universal statements are Lean theorems. Exact rational controls audit finite code
paths only. Imported Mathlib artifacts are pinned but not independently rebuilt; the
same Lean kernel performs replay. No novelty or priority conclusion follows from proof
checking.
