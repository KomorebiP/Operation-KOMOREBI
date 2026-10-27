# Streaming Polyphase Factor Decomposition v0.6

This checkpoint adds a certified phase-pair scheduler on top of the approximate
light-cone transfer bounds.

New files:
- `budget_scheduler.py`
- `test_budget_scheduler.py`
- `BUDGET_SCHEDULER_THEOREM.tex`
- `PROOF_AUDIT_BUDGET_SCHEDULER.md`
- `budget_scheduler_large.csv`
- `budget_scheduler_bruteforce_audit.csv`
- `weighted_communication_schedule.csv`
- `double_buffer_model.csv`
- `edge_risk_vs_block_norm.csv`
- `VERIFICATION_V06.md`

Main new results:
1. edge-additive phase-risk majorant;
2. globally cardinality-optimal equal-cost pruning under the scalar additive certificate;
3. certified exact-envelope refinement;
4. unequal-cost 0-1 knapsack formulation;
5. ideal asynchronous double-buffer timing and memory model.

Run:
```bash
python test_streaming_skat.py
python test_formal_v02.py
python test_approximate_lightcone.py
python test_budget_scheduler.py
pdflatex -interaction=nonstopmode -halt-on-error FINAL_MANUSCRIPT.tex
pdflatex -interaction=nonstopmode -halt-on-error FINAL_MANUSCRIPT.tex
```
