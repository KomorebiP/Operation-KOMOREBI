# AVOC v0.18.0 — current verification record

## Proof execution

- 70 new theorem/lemma declarations; 953 total, including helpers and examples.
- 94 non-audit modules; 15,357 non-audit source lines; 415 definition-like objects.
- 98/98 local targets have successful final-source compilation records under
  warnings-as-errors. The local build directory began empty; inherited sources
  were compiled, then the final new sources and aggregate.
- 953/953 exact expected theorem names appear in the fresh axiom audit.
- Axiom union: `propext`, `Classical.choice`, `Quot.sound` only.
- 37/37 negative files failed at substantive mathematical goals, without setup
  or timeout failures. Four new cases cover zero work, missing credit, zero-credit
  search and confusing a myopic value with the full-horizon value.
- Comment-aware source census matches the inventory. No proof placeholders,
  project axioms, native evaluation or unsafe theorem-like declarations were found.
- 87/87 inherited non-audit modules are byte-identical to frozen v0.17.

The runtime is pinned Lean 4.34.0-rc2 plus nine pinned dependency revisions. All
tracked dependency worktrees are clean after restoring an interrupted extraction's
single documentation symlink. The external binary cache was retained, not
source-rebuilt. Part/combined archive hashes passed, but a separate full tar
comparison timed out; no independent full-runtime authentication is claimed.

## Actual executed planner

The CLI invokes the same Lean evaluator and computable workflow model appearing
in the refinement proofs. It does not call the old classical optimal selector.

- 378 exact-rational planning comparisons against an independent Python model.
- Six public-report traces, including successful admission and rejection retention.
- 14 invalid wire requests rejected; four invalid wrapper cases rejected.
- 64 tested policies genuinely lose return relative to full-horizon planning; their
  complete-policy loss bounds hold.
- Initial full example: value 3/2, registration chosen, work 221, reservation 1461.
- Successful trace work: 333; research fees: three; realized stage return: five.
- Rejected trace work: 328; posterior: 1/4; pending retained; research fees: two.
- Credit-181 example: depth two, work 51, stop, explicitly not full-horizon optimal.
- Credit-zero example: no search, work zero, feasible stop, conservative loss bound.

The regression requests, actual stdout, invocation/timeout record and source
hashes are under `results/v0.18.0/`. Pure checker and filesystem regressions from
older releases remain historical, not new executions here.

## Interpretation

Tree-event work is not physical runtime. The counter excludes parser/reservation
costs, rational arithmetic bit length, model-callback internals (including proof
checks), memory and startup. The price field is supplied, not calibrated or used
for net-cost optimization. The tested trace is a modeled snapshot workflow, not
an observed LLM run or a filesystem refinement theorem.
