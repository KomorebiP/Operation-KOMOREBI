# AVOC v0.36.0 — targeted gap update

## G33. Staged warm/cold operations

**CLOSED AT THE FORMAL CONTROLLER LEVEL FOR ONE CHECKED AFFINE WORKLOAD.**

Cache validation and cold generation are paid, fallible, nonterminal actions.  Their reports
update readiness and budget before a deployment action becomes available.  The executable
evaluator is exactly Bellman-optimal at its finite depth, and setup-plus-deployment agrees
with the inherited proof-derived payoff.

**Remaining:** the current codec eagerly validates both candidates to construct the typed
model.  A live adapter must let the controller invoke only the selected operation, validate
its actual output, charge physical work, and resume from that report.

## G34. Operation/report acknowledgement

**STAGED REPORT CONTRACT CLOSED IN MEMORY.**

Faults are not observations.  A report is accepted only for an available action with positive
model probability; accepted reports preserve the budget and expose only proof-carrying
implementations.

**Remaining:** connect this acknowledgement to the durable transaction/recovery and paid
retry protocols used by the earlier protected proof workflow.

## G20. Metareasoning cost

**LOGICAL SETUP FEES ARE NOW INSIDE THE OBJECTIVE; PHYSICAL MODEL CONSTRUCTION IS NOT.**

The controller can decline unaffordable or horizon-useless setup.  It still does not price
eager certificate validation, parsing, process startup, or exhaustive planning work in the
same objective.

## G17. Model error

**UNCHANGED.**

The v0.15 model-error-to-policy theorem remains available, but staged success probabilities
and fees are exact supplied inputs in this release.

## Recommended next block

Construct a lazy protected staged runtime:

1. ask the planner for `inspectWarm`, `generateCold`, deploy or stop;
2. run only the selected external checker/generator;
3. distinguish valid report, model mismatch and infrastructure fault;
4. commit the checked result and exact charge transactionally;
5. resume the staged controller without repeating a committed operation.

This would unite the present staged Bellman model with the earlier artifact binding,
recovery, and paid-retry infrastructure.
