# Route: certified budget scheduler

Target: minimize retained phase-pair work under a certified finite-depth Krylov
error budget.

Outcome: proved an edge-additive transfer majorant and a cardinality-optimal
unit-cost scheduler under the scalar additive certificate. Unequal-cost
selection reduces to 0-1 knapsack. A certified exact-envelope refinement and
an ideal double-buffer execution model were implemented and audited.

Evidence:
- `BUDGET_SCHEDULER_THEOREM.tex`
- `PROOF_AUDIT_BUDGET_SCHEDULER.md`
- `budget_scheduler.py`
- `budget_scheduler_bruteforce_audit.csv`
- `budget_scheduler_large.csv`

Boundary: exact-envelope greedy refinement is not claimed globally optimal;
double-buffer timing is an ideal model, not measured GPU performance.
