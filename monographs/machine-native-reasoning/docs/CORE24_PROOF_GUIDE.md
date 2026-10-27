# Core 2.4 — proof guide

## Statement

Fix a field K, a finite-dimensional state space V, finite candidate and action
catalogues, a distinguished candidate theta0, and a linear protected readout Q.
Let A_a = T_a^theta0. All operation words are executed left to right.

Define E as the linear span of A_w (T_a^theta - A_a) v over every finite word w,
action a, candidate theta and initial vector v. The formal result establishes
that the following are equivalent:

1. Q T_w^theta = Q A_w for every fixed candidate theta and every word w, as
   operator identities on the whole state space.
2. E is contained in ker Q.
3. There is a surjective linear projection to a common carrier, shared linear
   updates and a matched readout, intertwining every candidate action.

The canonical witness is V/E. The same quotient predicts any finite sequence
of candidate/action pairs, allowing the candidate to change at every step.
The reference need not be identified from observations; it is supplied as one
of the candidates, exactly as in the source.

## Proof route

`CommonQuotient.lean` defines the actual word map, generator set and span.
It proves range containment, reference and candidate invariance, agreement
implying invisibility, actual quotient updates, quotient readout, the converse,
and arbitrary switching. The word executor is explicitly related to the
inherited `Komorebi.MachineTheory.run` convention.

The key forward implication tests the assumed word-operator identity not only
at v but at T_a^theta v. This is why an all-initial-vector premise matters.
The noncommuting example in the fourth module demonstrates the failure of a
one-initial-state replacement.

`CommonQuotientInterface.lean` defines `CommonModel`, the full carrier and
projection data, and constructs `canonicalModel`. A given common model yields
agreement rather than serving as an assumed answer. Arbitrary function-valued
updates and readouts also imply the agreement when their commuting equations
hold. A separate universal comparison map factors every other common projection
through V/E, is surjective, preserves actions and is unique. The span is
independent of the chosen reference among actual candidates.

`DiscrepancyClosure.lean` starts from the sum of discrepancy ranges and repeatedly
adds reference images. It proves monotonicity, containment, plateau completeness
and stabilization by `Module.finrank K V`. The main endpoints are
`source_core24` and `source_core24_reference`.

`CommonQuotientExamples.lean` supplies the source's three-coordinate family,
a noninjective two-coordinate projection, delayed observable return, fixed-
initial agreement with a switching failure, reference independence, an unrelated-
reference counterexample and zero discrepancy for identical candidates.

## Source correspondence

The original theorem is `r:common`, Core 2.4, at canonical source lines 233–250.
Setup is at lines 224–232. `THEOREM_MAP.json` retains those exact source records.
The source's finite-dimensional, finite-catalogue assumptions are explicit in
the two source-facing endpoints. Several supporting algebraic statements do not
need them; this is proved generality, not a changed source premise.
The third source condition says “updates” and “readout” without repeating their
linearity. `agreement_of_function_factor` covers that more permissive reading,
while the positive construction provides linear maps. The formal source theorem
therefore does not obtain its equivalence by imposing an unsupported necessary
assumption on arbitrary source data.

## Interpretation

The canonical quotient removes exactly the propagated inter-candidate
discrepancies. It is not asserted to be the smallest predictor for Q. It need
not reconstruct the full state, identify hidden dynamics, learn an encoder or
be numerically stable. Infinite-dimensional finite-stage stabilization is not
claimed. The underlying quotient and classical choices are mathematical data,
not a verified executable numerical algorithm.

## Checks

`checks/CheckCommonQuotientAPI.lean` checks raw all-vector agreement, supplied
linear factors, function-valued factors, the distinguished raw reference,
finite stabilization and arbitrary switching. Nine negative fixtures remove
or contradict decisive conditions in exact rational examples.

`scripts/check_common_quotient.py` is a separate exhaustive exact regression on
F_2^2 with two candidates and two actions. It enumerates all 65,536 operator
families and 262,144 scalar-readout contracts. State-pair reachability is run to
exhaustion for both fixed candidates and arbitrary switching, then compared with
an independently iterated discrepancy span and canonical coset dynamics.
69,184 readout contracts are admissible, and 8,640 have immediate invisibility
without propagated invisibility. These counts are finite cases, not theorems
or empirical measurements. The cumulative gates rerun this checker separately
from the Lean proofs and compare its exact result records.
