# Lean Block 03 — finite-horizon inquiry on the same compressed belief

**Machine-Native Reasoning · Reviewed Core 0.2 · Formal companion 0.3.0 · 10 October 2026**

## Source and formal target

This block formalizes Core **5.4**, “The same compressed belief supports the same inquiry,” at printed page 20, physical page 24, canonical LaTeX lines 664–675. The retained source PDF and LaTeX are unchanged. The support from Core 3.6 is an actual import, not a restated unproved hypothesis about reports. The new module subsequently adds the separate menu, loss, and charge contract that probability preservation alone cannot supply.

The result concerns exact, finite-horizon expected charge plus terminal loss. It is not the earlier worst-case execution/storage frontier, an approximate-model regret bound, or a general extracted planning implementation.

## 1. An information-state model and a finite tree

`Planning.Model S A O D` supplies a finite action menu and a nonempty finite terminal menu at every information state `s`. The report type `O` is finite. The state type itself need not be finite: a finite hidden-state model has a continuum of real-valued probability beliefs.

The model also supplies a finite nonnegative charge, a terminal risk, a nonnegative normalized report law, and a successor information state. The successor has the dependent type

```text
next s a o : (0 < prob s a o) -> S
```

Thus a successor is requested only on a positive-probability report. No probability belief is assigned to an impossible report.

`Planning.Tree A O D` has only two constructors: a terminal decision, or an experiment with a report-indexed family of children. A node does not receive the hidden physical state. `Feasible M h s P` checks the actual menu at the current information state, enforces the remaining horizon, and checks every positive-report child. The separate `Tree.Bounded` predicate also bounds dormant syntactic branches.

`evaluate` is the finite expected-loss recursion. `value` is defined independently by Bellman backup over the actual finite menus. A nonempty terminal menu guarantees that the minimum exists, including when the experiment menu is empty.

## 2. The minimum is attained by one actual tree

For a continuation value V, the backup is

\[
Q_V(s,a)=c(s,a)+\sum_{o:P(o\mid s,a)>0}P(o\mid s,a)V(s_{a,o}).
\]

At horizon zero, only terminal choices are considered. At a positive horizon, the minimum includes every permitted terminal choice and every permitted first experiment.

The proof has two directions. `value_le_tree` proves that the Bellman value is no greater than the evaluation of any feasible tree. At an experiment node, the induction hypothesis applies to every possible child; nonnegative branch probabilities preserve its inequality. `minimizing_tree_exists` selects one minimizing first choice, then attaches minimizing lower-horizon children. It proves both admissibility and an explicit syntactic depth bound.

A zero-probability branch receives only a dormant terminal syntax node. It is neither executed nor normalized, and no permission assertion about an invented posterior is required for it. The constructed tree remains finite.

`optimal_value_characterization` combines attainment and the universal lower bound. `randomized_tree_lower_bound` separately shows that a finite probability mixture of feasible trees cannot beat that value. This last statement is specifically about finite mixtures; it is not an unformalized claim about every conceivable randomized controller.

The construction uses classical selection of exact real minima. It proves a mathematical policy exists and is finite. It does not claim efficient extraction or a shortest stored program.

## 3. Preserve the operational state, not merely its probabilities

`Planning.ExactMap M N f` requires equality of action menus, terminal menus, charges, terminal risks, and report probabilities, together with

\[
f(s_{a,o})=f(s)_{a,o}
\]

on every positive report. The map's definition does not infer costs or permissions from probability agreement.

The transport proof first compares a fixed report-weighted continuation sum. It then proves equal Bellman backups and, by induction, equal values at every finite horizon. Every first-choice value and the full set of minimizing first choices agree. `firstValue M h` uses **h further experiments after the first**: its first-choice set therefore belongs to horizon h+1. The separately exposed terminal-choice equivalence includes horizon zero.

Two further inductions prove that the same literal tree is feasible on both sides and has the same expected loss. `common_minimizing_tree` strengthens a separate-existence assertion:

> One tree chosen from q alone is optimal for every fine information state s satisfying f(s)=q.

It does not choose a different initial action after secretly observing which fine state occurred.

## 4. Construct the planning map from the actual joint instrument

`BeliefPlanning.Belief X` is a nonnegative normalized real vector with its proof. For an aggregation pi, `aggregate pi` pushes the vector to the coarse state and uses the inherited normalization theorem.

A `Contract` fixes finite menus and nonnegative charges as functions of the coarse belief, and a terminal loss on the coarse physical state. The fine model uses the pulled-back menus and charges. Its terminal risk is computed on the fine state, not defined to be equal to the coarse risk:

\[
\sum_x p(x)\ell_d(\pi x)=\sum_z(Cp)(z)\ell_d(z).
\]

`terminal_risk_eq` proves the equality by fibrewise finite summation.

For each action and report, the fine model computes its report mass from the actual joint instrument and its next belief by normalizing the post-experiment vector. Positivity is supplied by the branch premise. The inherited report-mass and normalization theorems give the operational `instrumentMap` from

\[
C K_{a,o}=\bar K_{a,o}C.
\]

`compressed_belief_planning` proves value, experiment-value, and minimizing-choice equality. `common_optimal_inquiry` constructs the uniform coarse-belief tree. `constructed_quotient_planning` additionally obtains the coarse instrument from the inherited fibre criterion and surjectivity theorem. Supplying a quotient map does not assert its acquisition from data or the truth of a physical model.

## 5. Kernel-checked sensor optimum

The fine model is the manuscript's eight worlds `(target bit, sensor convention, nuisance bit)`. Calibration is nondestructive and reports the convention correctly with probability 3/4. The four-state quotient retains the target/convention pair. The nuisance is genuinely irrelevant to the report law and terminal loss.

The initial display-zero prior assigns mass 1/4 to each world with equal target and convention, and zero to the others. `initialFine_aggregates` proves its two diagonal coarse masses are 1/2.

For exact evaluation, a pair of natural counts stores the number of true and false reports. Its diagonal likelihood weights are `3^n_true` and `3^n_false`. `countMap` proves that updating those counts is the actual Bayesian update of `sensorLaw` **for all counts**, not only the tested three-step instance. The finite scalar Bellman recursion is separately proved equal to the general finite-menu recursion.

Lean establishes the exact value table:

| Report horizon | Minimum expected charge plus classification loss |
|---|---:|
| 0 | 1/2 |
| 1 | 3/10 |
| 2 | 3/10 |
| 3 | 11/40 |

The delivered `adaptiveThree` tree takes two reports, stops if they agree, and uses one final report if they disagree. Its admissibility and optimality are proved. Its expected report count is 19/8 and classification error is 5/32, with the same transitions and branches used by all three evaluators:

\[
\frac1{20}\frac{19}{8}+\frac5{32}=\frac{11}{40}.
\]

`eight_world_adaptive_optimal` transports this exact tree to every fine prior having the required coarse belief, allowing arbitrary compatible nuisance distribution. `source_sensor_optimum` applies it to the explicit normalized initial prior. These are kernel-checked statements about the specified finite mathematical sensor, not observed performance of an agent.

## 6. Boundary examples

`PlanningControls` proves that an empty experiment menu leaves only stopping, and that a forbidden terminal choice cannot be included in optimization. A one-report experiment shows that an impossible branch contributes zero, while the possible branch's terminal loss remains charged.

Another model has identical report laws but different allowed terminal decisions. No one-state planner preserves both catalogues. A further example has equal optimal values but different minimizing decisions, so equality of numbers alone does not establish policy transport.

Changing only the source sensor fee to one leaves the report and posterior rules unchanged. Nevertheless, at horizon one its optimum changes from 3/10 to 1/2, and the experiment is no longer an optimal first choice. Finally, the adaptive source tree has depth three, not two. Its expected report count is not a hard two-report guarantee.

## 7. Assurance and remaining scope

The mathematical argument assumes exact normalized finite instruments and exact real arithmetic. All variables affecting permissions, charges, or targets must be represented in the planning state. Unmodeled history, model misspecification, changing likelihoods, or hidden restrictions are not resolved by accepting the formal proof.

Source-result coverage is nine of 27. Core 3.8's approximate history bound, Core 4.1's decision bound, and Core 5.6's approximate changed-policy guarantee remain unformalized in this block. The exact planning theorem does not silently promote them.
