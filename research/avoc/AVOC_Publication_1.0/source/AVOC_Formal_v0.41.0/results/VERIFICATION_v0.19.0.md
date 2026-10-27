# AVOC v0.19.0 — final current-source verification

## Result

**PASS: 101/101 local compilation targets, 983/983 theorem axiom reports, 40/40 substantive negative rejections, 22/22 live bridge cases.**

30 new theorem/lemma declarations in `LiveExecution.lean` and `LiveExecutionCodec.lean`. The complete library has 983 declarations, 434 definition-like declarations, 96 non-audit modules and 15,761 non-audit Lean source lines. Counts include helpers and examples, not independent discoveries.

## Source and toolchain

- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06` and eight other exact dependency pins.
- All 94 inherited non-audit modules are byte-identical to the frozen v0.18 ZIP.
- All nine dependency heads match; tracked dependency worktrees are clean.
- The local build directory began empty. All finalized sources have successful current source/output/log hash records. Host-interrupted targets were rerun before acceptance.
- External binary caches were retained. This is not a source rebuild of mathlib, an independent Lean kernel, or comprehensive authentication of the physical runtime.
- The portable runtime recovery completed individual-part CRC/SHA and combined-archive SHA checks. These are transport integrity checks under the same toolchain/host trust boundary.

## Full axiom and source audit

The current `AVOC/FullAudit.lean` names exactly all 983 indexed theorem/lemma declarations. It passes with warnings as errors. The dependency union is only `propext`, `Classical.choice`, and `Quot.sound`. The comment-aware census agrees per module, including attributed declarations. The positive sources and trusted entrypoints contain no proof placeholders, project axioms, native evaluation shortcuts, or unsafe declarations.

## Deliberate false claims

All 40 current-source negative files fail without import/setup failures or timeout. The three new cases attempt to accept an operational fault as a normal report, match changed ticket generations, or confirm an empty-context falsity proof. The positive library separately proves the relevant obstructions. Proof-script failure by itself is not a universal mathematical negation.

## Live filesystem regression

`checks/test_live_workflow.py` passes all 22 named cases using fresh temporary stores. These include a real successful workflow, no-search/short-horizon/no-budget/invalid-candidate stops, target/candidate mutations, generation and receipt substitution, real checker and planner subprocess timeouts, environment drift, post-commit failure, configuration boundaries, model-impossible and fault reports, and consumed-receipt rejection.

The timeout records actually mark timed-out subprocesses. In the post-commit case the physical store contains a valid committed admission, but the run remains unconfirmed at its previous prefix. It neither claims clean success nor retries automatically. Other infrastructure faults are not converted into Bayesian rejection evidence.

The test result records are tied to the final test and implementation sources. Temporary stores are not retained for every regression; exact current input-generating test code, results and relevant process hashes are retained. The separate final demo retains its actual store and complete requests. This is bounded implementation evidence, not universal filesystem refinement or a production LLM benchmark.

## Final retained live demonstration

Record: `results/v0.19.0/live_success_final/run.json`.

- Two actual proof files are offered; candidate index 1 is selected.
- Actual stage sequence: register, verify, admit.
- Confirmed steps: 3; real retained admissions: 1; final pending: empty.
- The retained source equals `examples/live/identity.proof.json`, proving P -> P.
- Nominal attempted fee debit and confirmed research spend: 3.
- Planning tree work: 838, accumulated once across the three real decisions.
- Declared planning charge at 1/1000 per unit: 419/500.
- Six planner/monitor subprocess calls (three planning, three acknowledgement). Acknowledgement calls perform no search-tree evaluation; their physical replay/checking work is not zero.
- Three actual separate checker subprocess calls: verify, admission proof recheck, admission binding check.
- Belief remains 1/2: deterministic availability is required; no fabricated availability evidence is used.

Measured in this final local run: total elapsed including setup 15.130064 s, planner/monitor subprocess sum 9.954682 s, checker subprocess sum 1.679800 s, environment capture 3.326053 s in 17 captures. These timing categories overlap; do not sum them. Startup, JSON, rational arithmetic, replay, proof checking, snapshots and host overhead are real costs distinct from the abstract tree counter. These measurements do not establish a portable speed claim or optimal metareasoning.

## Evidence and residual boundaries

`AUDIT.json` and `results/v0.19.0/final_audit.json` are the fail-closed collector outputs. Current build records, exact name audit, all negative records, live regressions and the retained demo are under `results/v0.19.0/`.

Earlier version directories and the preliminary `live_success/` run are historical/development evidence, not the final demo. Packaging hashes are generated afterward and checked independently. Read `PROOF_BOUNDARY.md` for the single-root deterministic model, protected-host assumption, supplied-view I/O trust, unrecoverable ambiguous commits and absence of a regret guarantee for aborted external runs.
