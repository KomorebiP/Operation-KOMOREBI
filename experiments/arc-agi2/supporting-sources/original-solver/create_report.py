"""Render the measured result without changing selection policies.
Author: Komorebi P.
"""
from pathlib import Path
import engine,solver

ROOT=Path(__file__).resolve().parent

def create_report():
    r=engine.read(ROOT/'results/evaluation.json');engine.verify(r)
    v=engine.read(ROOT/'results/validation.json');engine.verify(v)
    primary=r['policies'][solver.PRIMARY];s=primary['score'];base=r['policies']['base']['score']
    oracle=r['candidate_plus_live_base_oracle_diagnostic'];repair=r['typed_repair_ablation']
    selected=primary['candidate_only_selection']
    supported=r['policies']['typed_supported'];supported_score=supported['score']
    supported_selected=supported['candidate_only_selection']
    oracle_missing_g47=set(r['reference_g47']['exact_keys'])-set(oracle['exact_keys'])
    started=engine.read(ROOT/'results/runtime_start.json')['start_epoch_seconds']
    completion=engine.read(ROOT/'results/census_completion.json') if (ROOT/'results/census_completion.json').exists() else None
    elapsed=(completion['completed_epoch_seconds']-started)/3600 if completion else (((ROOT/'results/final_legacy_census.json').stat().st_mtime-started)/3600 if (ROOT/'results/final_legacy_census.json').exists() else None)
    elapsed_note=f'Elapsed time from the initial start to census completion was approximately {elapsed:.2f} hours, including interrupted periods. Active scanning used eight workers. ' if elapsed is not None else ''
    lines=['# Komorebi PR-LASM — Block 17 final report','','Author: Komorebi P.','',
        f"The preregistered `typed_recent` policy scored **{s['pass2_exact_outputs']}/1,076 exact outputs ({s['pass2_fraction']:.2%})** and **{s['whole_tasks']}/1,000 whole tasks ({s['whole_task_fraction']:.1%})**. These are unfiltered predictions from the integrated executable solver on exposed public training data.",'',
        f"The preserved G47 retrospective frontier remains **{r['reference_g47']['pass2_exact_outputs']}/1,076 outputs and {r['reference_g47']['whole_tasks']}/1,000 tasks**. It was never used as a prediction fallback. No hidden or untouched evaluation set was opened.",'',
        '## Frozen policy comparison','',
        '| Policy | Pass@1 outputs | Pass@2 outputs | Whole tasks | Gains / losses vs live base |',
        '|---|---:|---:|---:|---:|']
    for name,row in r['policies'].items():
        z=row['score'];label=name+(' (primary)' if name==solver.PRIMARY else '')
        lines.append(f"| {label} | {z['pass1_exact_outputs']} | {z['pass2_exact_outputs']} | {z['whole_tasks']} | +{len(row['gains'])} / −{len(row['losses'])} |")
    lines+=['',f"The primary policy changes {len(primary['changed_outputs'])} output positions relative to the live base. Of those, {len(primary['changed_wrong_outputs_including_losses'])} remain wrong. All are retained in the submission and audit. Its first-attempt changes relative to the live base: {primary['live_base_attempt1_changes']}.",'',
        '## What the experiment established','',
        'The runtime now has a complete path from demonstration grids and test inputs through the live core/Block 2/Block 4 solver, seven native compiler stages for Blocks 6–12, 21 Block 13 entrants, and 48 Block 14–15 entrants. Block 5 supplies the shared execution IR. The dispatcher consumes candidate evidence and live predictions; it does not consult a task-specific success mask.', '',
        f"The combined census contains {r['runtime']['candidates']} candidates across {r['runtime']['tasks_with_candidates']} tasks. The candidate-plus-live-base oracle diagnostic contains a correct answer at {oracle['exact_outputs']} output positions. The primary policy leaves {len(primary['available_correct_outputs_not_selected'])} of those available exact outputs unselected. That diagnostic uses labels after the freeze; it is not a runtime score.",'',
        f"Relative to G47, the primary runtime misses {len(primary['g47_missing_outputs'])} preserved exact outputs and produces {len(primary['gains_beyond_g47'])} exact outputs outside that frontier. Those outside-frontier cases are listed in the evaluation JSON; they have not been silently promoted.",'',
        f"Excluding live-base fallback credit, selected candidates are correct on {selected['outputs_with_correct_candidate']}/{selected['activated_outputs']} activated output positions. There are {selected['exact_candidate_attempts']} exact candidate attempts out of {selected['selected_candidate_attempts']} selected candidate attempts, and {selected['false_activation_tasks_no_correct_candidate']} activated tasks receive no correct candidate. These counts preserve wrong activations.",'',
        '## Typed repair result','',
        f"The scoped multiscale codebook veto emitted {len(primary['typed_vetoes'])} witness records. Compared with the otherwise identical no-veto control, it produced {len(repair['gains'])} gains, {len(repair['losses'])} losses, and {len(repair['changed_wrong_outputs_including_losses'])} changed outputs that remained wrong.",'',
        'A repair abstention alone does not suppress its ancestor. The veto requires a checked noninjective structural codebook and names the colliding learned keys and program hash. The explicit binary symmetry predicate remains outside its scope. This repair was motivated by a previously exposed failure, so its development is score-seeded.', '',
        f"The additional trace-support control changes the primary result by +{len(r['trace_support_ablation']['gains'])} exact gains and −{len(r['trace_support_ablation']['losses'])} losses. It was added before scoring and does not replace the preregistered primary.",'',
        f"That control scores **{supported_score['pass2_exact_outputs']}/1,076 outputs ({supported_score['pass2_fraction']:.2%}) and {supported_score['whole_tasks']}/1,000 whole tasks**. It rejects feature-induction candidates whose evidence reports unseen test keys. Its candidate-only accuracy is {supported_selected['outputs_with_correct_candidate']}/{supported_selected['activated_outputs']} ({supported_selected['candidate_output_conditional_accuracy']:.2%}); {supported_selected['false_activation_tasks_no_correct_candidate']} activated tasks still receive no correct selected candidate. Relative to the live base it gains {len(supported['gains'])} exact outputs and loses {len(supported['losses'])}. This stronger control remains an ablation result, not a retroactive change to the primary policy.",'',
        f"The trace-support control leaves {len(supported['available_correct_outputs_not_selected'])} available correct outputs unselected. The candidate-plus-base oracle omits {len(oracle_missing_g47)} G47 exact outputs. Its higher diagnostic coverage identifies remaining selection failures; it does not provide a label-free way to choose those answers.",'',
        '## Compute and verification limits','',
        'The complete older-bank run is fresh. The unchanged 48-entrant modern bank reuses Block 16’s full live replay census after source, challenge and per-task binding checks. The release also supplies `engine.py scan --include-new` to recompute every bank for arbitrary challenge files. Reusing that census is disclosed; it is not claimed as a new 48,000-call scan.', '',
        elapsed_note+'Both core entry points use deterministic nominal tier 2.0, including 2,200 composition expansions. Feature induction uses conjunction depth 2, beam width 32 and at most 32 emitted programs. Other compiler limits are inherited. Several higher-budget pre-score attempts were stopped during profiling. Exact task-local feature caching was verified before the budget reductions; the reduced budgets are separately documented and are not asserted to reproduce deeper-search candidates.', '',
        f"The full run recorded {r['runtime']['error_count']} failed compiler receipts. They are exposed in the evaluation JSON and fail closed. Verification tiers differ: {r['runtime']['verification_tiers']}. Modern entrants replay serialized programs; earlier interfaces provide native exact-fit executions or recorded training executions. A shared interface does not upgrade their evidence by assertion.",'',
        f"Validation passed {v['unit_tests_passed']}/{v['unit_tests_run']} tests, source authentication, byte-identical fresh-process dispatch, and task-ID/corpus-order invariance. The runtime Python literal-ID scan found {len(v['literal_task_id_runtime_hits'])} matches. Exact feature-cache equivalence was checked against the archived reference candidates. These checks establish the stated implementation properties, not unseen generalization.",'',
        f"Fresh full-bank compiler replay also matched all {v['fresh_process_full_bank_compiler_samples']} saved task samples, covering 56 candidates and 231 interface calls. Those records were checked against the completed census. This is sampled compiler replay, separate from the complete fresh dispatch check.",'',
        'An initial process-stop request did not stop all earlier workers. The execution runner subsequently terminated them; incompatible checkpoints were rejected by source hashes and separated. A later restart also rejected stale checkpoints. The final run uses a separate output path. No such checkpoint entered its completed census.', '',
        'The final run was later resumed after its worker processes ended between conversation turns. All 336 completed checkpoint records were retained and authenticated under the unchanged code and budget before further compilation. The recorded elapsed time includes this interruption.', '',
        'At 574 completed records, the scan switched from forked workers to fresh spawned workers through `run_scan.py`. This avoids inheriting the large graph of loaded checkpoints. The frozen engine, policies and search budgets stayed unchanged. Before the switch, the spawned-worker run reproduced the complete three-task sample census byte for byte. The launcher and this comparison have separate authenticated receipts.', '',
        'Near completion, the execution service disconnected twice. The first recovery preserved live workers and 997 completed records. After the second disconnect, the worker processes had ended; 998 completed records survived and only the remaining two tasks were restarted with unchanged source and budgets. These interruptions are recorded separately and included in elapsed time.', '',
        'Writing the combined evidence initially exceeded the workspace disk limit, before policy predictions were frozen or scored. The large censuses now use lossless gzip storage. The complete older census passed a byte-exact compression/decompression check, and the storage helpers are authenticated in the prediction freeze. Working records were reclaimed only after their archived bytes were verified. Compiler code, budgets and selection policies did not change during this storage repair.', '',
        'Obsolete working copies were restored during background synchronization, so closing work moved to a clean directory. All 369 retained files were checked byte for byte, the complete task-record archive was verified, and source authentication passed before the obsolete working directory was retired.', '',
        '## Geometry-domain repair','',
        'The separate micro-schema repair adds dimension preconditions to three operators that paint or recolor in the input frame. Its paired all-corpus check removes 237 original compiler exceptions with zero remaining exceptions and zero changes to candidates from successful original calls. The repaired compiler still activates on the same 26 tasks and emits no new activations. This is a robustness improvement with no coverage gain. Both its primary-parent and trace-support-parent submissions are frozen and evaluated separately under `repair_results/`.','',
        '## Reproduction','',
        'See `README.md` and `PROTOCOL.md` for commands, budgets and policy definitions. The machine-readable evaluation retains every gain, loss, wrong change, veto witness and unselected exact candidate. The primary submission is `results/submission.json`. The complete release contains the source bank, training challenges, separate evaluation evidence, frozen predictions and validation artifacts.', '',
        f"G47 reference SHA-256: `{r['frontier_unchanged']['sha256']}`",'',
        f"Final prediction code hash: `{solver.prediction_hash()}`",'',
        f"Census content hash: `{r['census_hash']}`",'']
    path=ROOT/'BLOCK17_FINAL_REPORT.md';path.write_text('\n'.join(lines))
    frozen=engine.read(ROOT/f'results/{solver.PRIMARY}.json');engine.write(ROOT/'results/submission.json',frozen['submission'])
    return path

if __name__=='__main__':print(create_report())
