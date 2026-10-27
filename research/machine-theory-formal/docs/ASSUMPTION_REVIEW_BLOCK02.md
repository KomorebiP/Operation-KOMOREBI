# Block 02 — source-to-formal assumption review

**10 October 2026 · Reviewed Core 0.2 · Two added results**

## Admission 3.4, `r:bayes`

- Finite model, observation and report alphabets are explicit. Global equivalences require a nonempty model type and a nonempty raw-observation type. A probability prior itself rules out an empty model set. Nonempty observations are needed for the arbitrary reconstruction row of an impossible report.
- Observation likelihoods and reporting rows are nonnegative and normalized. The channel cannot inspect the hidden model. The exact joint likelihood is constructed from these two objects.
- All-prior preservation means equality on every positive-probability **pair**, not merely matching a marginal law or one realized observation.
- One full-support prior means exact posterior agreement for that prior at all such pairs. It does not mean one sample or a prior supported on only a subset. The point-mass/erasure example refutes that weakening.
- The reverse stochastic kernel factors the actual coupled experiment modelwise. It is not an unrelated simulator of matching marginals.
- Every impossible pair is handled by nonnegativity and zero mass. No cancellation uses a zero denominator or zero prior coordinate. The utility `update` is a total algebraic expression, but the semantic equivalence is guarded by positive mass.
- The arbitrary normalized row on an impossible report remains only a reconstruction row. The probability interface gives no posterior on that report.
- The formalization proves both directions and explicitly constructs a reconstruction. It introduces no statistical estimation, finite-sample extrapolation, or learned likelihood assumption.

## Admission 3.5, `r:joint-refinement`

- X is finite. Actions and likelihood indices can be arbitrary types in the abstract statement, strengthening the finite-index manuscript case without changing its instance. Kernel entries remain exact real values. Supplied `Law X A Unit` gives normalized nonnegative transition columns.
- The mandatory partition has at least two blocks, represented by two nonequivalent states. Every likelihood is strictly positive at every state. These are the manuscript's premises, not consequences of the refinement.
- Bayesian necessity is derived from two-point priors. It does not define admissibility to contain fibre constancy as an unproved extra condition.
- Separate Bayesian updates are permitted as operations in their own right and must commute for every prior with one fixed positive coarse likelihood per observation. This is stronger than one chosen transition/report schedule. Optional normalization over a complete report alphabet is unnecessary for the individual-update theorem and not inferred.
- The initial partition preserves all likelihood values and mandatory distinctions. Every subsequent split uses complete successor probabilities into every current block. `step_rel_iff` establishes the exact displayed block-sum semantics.
- Strict refinement implies strict block-count increase. The stated bound is the number of states minus the initial block count, not a looser bound substituted without disclosure.
- The stopping index is selected from a proved bounded existence statement; the result establishes stability, normalization of the coarse transition, separate Bayesian closure, coarseness and uniqueness.
- The coarseness proof covers every admissible refinement, not just partitions visited by the implemented iteration.
- The construction relies on classical finite quotients and `Nat.find` for mathematical existence. It is not an extracted efficient algorithm, a claim to acquire the input tables, or a certificate of finite-precision arithmetic.
- One-block and omitted-likelihood examples expose separate hypotheses. The four-state example connects the exact iteration to the operational admissibility predicate.

## Retained six results

The six predecessor source modules are byte-identical and recompiled from source in each current cumulative run. Their earlier source-assumption review is preserved as `docs/ASSUMPTION_REVIEW.md`. This block reviews their use at the new interface and reruns their formal verification. It does not relabel them as two additional discoveries or import the assurance of unrelated Lean projects.

## Proof and execution boundaries

API examples restate central types independently of their declaration statements. They help catch a weakened export, but do not replace mathematical interpretation of the model. The axiom audit checks actual elaborated dependencies. Local `leanchecker` replay uses Lean's same kernel and the pinned imported objects. Neither it nor checksum matching provides independent implementation, origin authentication, model truth, or a host-language refinement theorem.
