"""Assemble scoped results from completed runs, without inventing new metrics."""
from pathlib import Path
import json,hashlib,datetime,sys,platform
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1]
def get(path):return json.loads((ROOT/path).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    main={f'{l}_{a}':get(f'runs/eval_{l}_{a}/result.json') for l in 'AB' for a in ('parent','access','joint')}
    cal={l:get(f'runs/eval_{l}_calibrated/result.json') for l in 'AB'}
    conf=get('runs/confirmation/result.json');seq=get('runs/sequential/result.json');control=get('runs/distributed_control/result.json')
    result={'version':'0.6','status':'EXECUTED_ADAPTIVE_DEVELOPMENT_PARTIAL_NATIVE_ACCESS_REPAIR',
            'not_certified':['localized_J_space','original_RRCT_v062_primary','no_wire_competence','unilateral_workspace_writing','unknown_partner_transfer','pretrained_language_model'],
            'training_bounds':{'v05_parent_max_length':12,'main_max_length':24,'secondary_calibration_max_length':48,'main_named_generators_excluded':['commuting_flips','swap_conjugation'],
                               'secondary_all_six_generators_exposed':True,'ancestor_lineages':2,'new_main_continuations':4,'new_calibration_continuations':2,'full_uninterrupted_replays':1},
            'capacity':{'original_parameters':171602,'copied_access_parameters':106530,'total_parameters':278132,'message_values_each_direction':8,'cue_exchange_rounds':2},
            'main':main,'secondary_calibrated':cal,'new_history_confirmation':conf,'sequential_no_reset':seq,'engineered_distributed_control':control,
            'audits':{'main':get('checks/independent_audit.json'),'additional':get('checks/additional_audit.json'),'paired':get('checks/paired_training_audit.json')},
            'metadata_correction':'Raw main parent untrained_length flags use24 instead of12. Correct parent boundary is12. Confirmation metadata is corrected. Depth changes recall only, not separate working-reuse assay.'}
    (ROOT/'RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    def m(l,a,c='swap_conjugation_L48'):return conf[f'{l}_{a}'][c]['metrics']
    def pct(x):return f'{100*x:.2f}%'
    table='| Lineage | Parent | Access-only, unseen family | Joint, unseen family | Access-only after known-stress calibration |\n|---|---:|---:|---:|---:|\n'
    for l in 'AB':table+=f'| {l} | '+ ' | '.join(pct(m(l,a)['memory_all_eight']) for a in ('parent','access','joint','calibrated'))+' |\n'
    reuse='| Lineage | Private recall after repaired access | Short working reuse: exact | All eight facts after that reuse |\n|---|---:|---:|---:|\n'
    for l in 'AB':reuse+=f'| {l} | '+ ' | '.join(pct(m(l,'calibrated')[k]) for k in ('private_recalled','reuse_exact','reuse_memory_all_eight'))+' |\n'
    sequential='| Condition | A: first four cues | A: second four | B: first four | B: second four |\n|---|---:|---:|---:|---:|\n'
    for arm,fam,label in [('parent','identity_tokens_L0','Parent, no preceding work'),('calibrated','identity_tokens_L0','Calibrated, no preceding work'),('parent','swap_conjugation_L48','Parent, stress48'),('calibrated','swap_conjugation_L48','Calibrated, stress48')]:
        vals=[seq[f'{l}_{arm}'][fam][k] for l in 'AB' for k in ('first_pass_all_eight','second_pass_all_eight')]
        sequential+=f'| {label} | '+' | '.join(pct(x) for x in vals)+' |\n'
    text=f'''# Komorebi Workspace Incubator v0.6
## Architecture-assisted native access repair with fixed working dynamics

**Author: Komorebi P.**  
**Date: September 27, 2026**  
**Status: executed adaptive development. Partial native access repair; no certified J-space.**

## Executive result

A copied, phase-local retrieval mechanism learned to recover more retained facts
through the agents' own eight-value communication wires and existing answer heads.
The original observation, working, silent-update and answer parameters remained
exactly frozen in the access-only arms. This is not an external joint decoder
being counted as a native result. It is also not emergence without architectural
scaffolding: the phase dispatch and extra access parameters are supplied.

The initial held-out-generator test improved only modestly. A later calibration
that explicitly trained the known stress family improved more, but did not solve
longer extrapolation or repeated retrieval. It also harmed some clean sequential
recall. Reliable one-shot access and preservation of future access are distinct.

## 1. Recovery and controlled changes

The recovered v0.5 archive SHA-256 was
`f269317643f01a38190cbf64710aacae2cbc909e33a64fee493b03765a5f1dd0`.
Its420-file manifest and20 tests passed before successor development. This turn
did not reconstruct missing v0.5 weights. The two required random-curriculum
parent checkpoints and relevant source modules are retained unchanged.

A and B denote two different dyad initialization lineages, not the two agents
inside one dyad. Both parents were previously selected for competence and have
different ancestral training budgets. This is not an untouched eight-seed cohort.

The original dyad has171602 parameters. The copied access modules add106530,
for278132 total, about62.1% more than the predecessor. Each agent retains one
64-dimensional working state, independent weights and eight outgoing message
values. No central reader, semantic workspace coordinates, protected fact array
or latent supervision is introduced. Each copied module sees its own private
state, an ordinary cue and the other agent's message, never both raw states.

Copied cue/input/routing/observe/send/receive parameters execute only during the
supplied retrieval phase. Original modules execute observation and initial cue
loading, working operations, silent updates and final readouts. At initialization
the copied retrieval is byte-exactly equivalent to the original path. Frozen
weights do not mean frozen activations: working states still evolve through the
original potentially drifting computation. Every retrieval itself changes state.

## 2. Main matched continuation

For each parent, access-only and joint arms start from the same copied architecture.
Access-only trains106530 copied parameters. Joint trains all278132 parameters.
Each uses1000 updates, batch96, AdamW restart at0.0003 and weight decay0.00001,
one Torch thread and the same generated data. Forward calls and episode budgets
match; backward cost, trainable parameter count and wall time do not.

Training uses random nonidentity, inverse-palindrome, identity-token and repeated
flip programs at lengths0,3,6,12,24. The named commuting-flip and swap-conjugation
generators are not sampled. Incidental short strings can occur in random programs,
so this is a generator exclusion, not a proof that every equivalent string is new.

Each post-working state has four independent terminal retrieval branches covering
all eight facts. Each branch includes a second same or changed cue. Only terminal
consumer/private labels provide targets. Four consumer types are withheld until
state formation: exact report, parity, late XOR-mask transformation and verification.
Their arguments are regenerated after target semantics are fixed. No query or
answer enters state formation. No original base parameter changes in access-only.

The final1000-update checkpoint defines the main result. No best-checkpoint
selection is used. The data-generator states, Torch states and family/length
counts match within each lineage. All78 original model tensors are unchanged
in both access-only lineages and remain so after secondary calibration.

## 3. Main result versus outcome-informed calibration

The main unseen-family/unseen-length result is partial. After seeing it, a
separate additional1000-update access-only calibration exposed all six families
and lengths12,24,48. Length48 has60% sampling probability in that phase.
This deliberately changes the question from generalization to learnability of
native retrieval on the known stress. The earlier main results are retained.

The table below uses a NEW1024-history confirmation bank generated after all
checkpoints were frozen. Each score requires all eight facts correct for an
agent, averaged over the two agents. Four independent branches start from the
same post-program state. The stress is48 operations of swap-conjugation.

{table}
The calibrated column is not an unseen-family or unseen-length result. It has
an additional1000 updates and a different distribution from the main comparison.
All256 factual worlds and both opcode aliases may occur during training; the
confirmation concerns new histories, not unseen-world or unseen-alias learning.

Joint training is not a uniform repair. In lineage B, private recall after stress
falls from{pct(m('B','parent')['private_recalled'])} to{pct(m('B','joint')['private_recalled'])}.
That regression remains a failure rather than being hidden by better work scores.

The main52-bank-per-model suite uses512 histories per bank. The confirmation
uses1024 histories and a new seed. Values across those suites differ slightly.
The report never substitutes an easier pooled score for all-eight exact recall.

## 4. The repaired state remains usable for native work, within limits

After repair, three new ordinary working operations are supplied, followed by the
late consumer. Access training did not contain working operations AFTER the copied
retrieval, so this is a distinct bounded interface-reuse test. Working operators,
silent updates and answer heads are frozen in calibrated models.

{reuse}
All four later consumer scores are retained in RESULTS.json. The correct incoming
working state is not silently substituted for the memory being recalled. The
post-retrieval suffix starts from the factual pair loaded through the new access
path and has its own independently recomputed target.

Original pre-retrieval working predictions are EXACTLY unchanged for access-only
and calibrated arms on every saved bank. That is narrower than saying every
subsequent task is preserved. Repaired retrieval can still alter the state from
which later work or further recall proceeds. All-eight recall after reuse is
weaker than one-shot selected-content use.

## 5. Native messages are causally used

In the512-case known-stress suite, cutting both access-phase message directions
reduces calibrated all-fact recall from78.42% to5.27% in A and91.11% to3.42% in B.
Shuffling access messages reduces those scores to2.44% and2.15%. Directional cuts
are also retained and primarily harm the deprived recipient. Observation and
working-phase communication are left intact in these tests.

These are interventions on learned messages, not a demonstration of unique
Jacobian localization, natural subspace writing or general reciprocal authority.
They establish that the tested retrieval behavior uses the native access channel.
A full from-scratch no-wire competence control is not newly completed.

## 6. Repetition and clean-context regressions are substantial

At length96, which neither main nor calibration training included, calibrated
all-eight recall is{pct(m('A','calibrated','swap_conjugation_L96')['memory_all_eight'])}
and{pct(m('B','calibrated','swap_conjugation_L96')['memory_all_eight'])} on confirmation.
This is a severe extrapolation failure. The unchanged incoming working computation
is itself weak at that length; it is not a pure access-only regime.

In the512-case repeated-same-cue diagnostic, calibrated stress48 all-eight recall
falls from78.42%/91.11% after one cue to57.32%/20.80% after eight. Two successive
retrievals were trained; eight were not. This limits extrapolation, rather than
contradicting the trained-depth result.

A separate post-outcome diagnostic makes four changing cues cover all eight facts,
then repeats the pass. It does NOT reset to a saved state between cues. It uses
1024 new histories. The first/second pass scores require the four requested pairs
to be jointly correct for the agent during that pass.

{sequential}
The calibration makes stressed sequential access better but harms some unstressed
sequential use. In the calibrated no-work condition, eighth-cue private recall is
53.17% and54.79%. This is not a complete memory-preserving access mechanism.
It cannot be excused merely because the base weights did not change.

Main metadata correction: the raw parent-bank `untrained_length` flag used the
children's max24 instead of the parent's max12. Correct limits are explicit in
confirmation and consolidated metadata. No predictions or scores changed.
Depth alters recall branches only; working-reuse measurements use one new access.

## 7. An engineered bandwidth control, not a native neural result

A separate supervised linear reader was fit on4096 parent-state examples per
lineage from a mixture of eight conditions. There is ONE fixed reader per lineage,
not one refit for every test. It maps the concatenated128 coordinates to eight
fact scores. Its weights are then split into agent-local partial sums.

Each agent sends eight bounded real values using the supplied invertible scalar
codec phi(x)=x/(1+abs(x)). Each receiver reconstructs the other partial sum and
adds its own. Both reconstruct the central linear readout. Across26 tested
conditions the maximum float64 discrepancy is7.11e-15 and all bit predictions
agree exactly. On its own512-case swap48 bank, all-eight accuracy is93.75% and
94.53%. This is not the same bank as the native1024-case confirmation table.

This elementary construction rules out only a crude bandwidth impossibility for
the chosen linear partial sums. It remains a supervised compiled positive control:
it is not the GRU's learned codec, a shared hidden-state probe counted as native
repair, an autonomous writer or a discovered J-space. Finite-precision and function-
class restrictions still matter. The proof and numerical check are in the note.

## 8. Verification and exact scope

Twenty-four successor tests pass after two tooling corrections. A complete
1000-update uninterrupted replay reproduces all122 saved model tensors, optimizer,
RNG states, every checkpoint field, checkpoint bytes and all52 evaluation-bank
bytes exactly. The separate short resume test reproduces loaded computation state
and all tensor payloads; its pickle metadata bytes differ because optimizer string
keys are memoized differently after loading. Resumed-file byte identity is not
claimed. The initial failed byte assertion and its diagnosis are retained.

The independent integer/NumPy audit rechecked12779520 recorded output entries
in416 primary/calibrated banks, plus1966080 entries in32 confirmation banks and
786432 entries in24 sequential banks. These are reused histories, agents, branches
and interventions, not millions of independent experiments. The distributed codec
was checked separately across26 conditions. All parent hashes, frozen tensors,
paired schedules and actual operating-system exit records are retained.

The first audit failed by treating an eval log as a directory. Directory filtering
was corrected and the full audit rerun without changing scientific outputs. The
streaming launcher was unavailable before shell execution; a monitored supervisor
captured child return codes. The original and repaired sources/logs are included.
The canonical Mathbox manifest CLI was not installed; a documented local v1
structure/path/hash validator is used. Its limits are explicit in the manifest.

No new projected-state support audit, localization claim, no-wire competence,
unilateral workspace-write result, partner transfer, original RRCTv0.62 primary,
pretrained-language-model experiment or subjective-state certification follows.

## Research conclusion

Native retrieval can be improved while the formation of the retained state is
held fixed. The next obstacle is preserving future access AFTER access itself,
not merely improving one-shot decoding. The proposed next test evaluates full
retrieval/working trajectories and clean-context noninterference at matched
budgets. It is a design, not an executed next-stage result.
'''
    # Restore ordinary prose spacing without changing any numbers.
    import re
    text=re.sub(r'\b([A-Za-z]{2,})(\d{1,7})(?=\b)', lambda m: m.group(0) if m.group(1) in {'float','max','rank'} else m.group(1)+' '+m.group(2), text)
    text=text.replace('RRCTv 0.62','RRCT v0.62')
    (ROOT/'REPORT.md').write_text(text)
    # Aggregate evidence manifest: legacy v1 plus explicit per-command records.
    env=get('environment.json')
    outputs=[p for p in [ROOT/'RESULTS.json',ROOT/'checks/independent_audit.json',ROOT/'checks/additional_audit.json',ROOT/'checks/paired_training_audit.json',ROOT/'checks/final_unit_tests_rerun.log'] if p.exists()]
    recs=[]
    for name in ('training_execution.json','calibration_execution.json','evaluation_execution.json','secondary_evaluation_execution.json','control_execution.json','final_assay_execution.json','sequential_execution.json'):
        recs+=get('checks/'+name)['records']
    start=min(x['started_at'] for x in recs);end=max(x['finished_at'] for x in recs)
    manifest={'schema_version':1,'claim_id':'KWI-v0.6-native-access-repair','repository':{'commit':'unavailable; immutable input and source hashes identify this non-git research tree','dirty':True},
              'command':'Recorded commands in checks/*_plan.json and actual exits in checks/*_execution.json; see README reproduction commands.',
              'environment':{'software':[{'name':'Python','version':sys.version.split()[0]},{'name':'Torch','version':torch.__version__},{'name':'NumPy','version':np.__version__}], 'hardware':'CPU only, four CPU-equivalent quota,4GB cgroup RAM, one numerical thread per worker'},
              'mathematics':{'assertion_tested':'Bounded improvement of native cue-driven factual retrieval at frozen pre-retrieval state, tested separately from downstream reuse, repeated access and a supervised analytic distributed control.',
                'coefficient_domain':'Exact binary task interpretation; neural float32; compiled readout float64.',
                'conventions':'Eight factual bits, four numerical output classes, two independent64-state agents, eight messages each direction, two cue exchanges.',
                'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted((ROOT/'inputs').glob('*.pt'))],
                'bounds':{'initialization_lineages':2,'main_training_updates_per_arm':1000,'secondary_updates':1000,'batch':96,'main_max_length':24,'secondary_max_length':48,'evaluated_max_length':96,'cue_depth_max':8,'main_bank_cases':512,'confirmation_cases':1024},
                'non_claims':['No universal neural convergence','No native localized J-space certificate','No unknown-partner or no-wire competence claim','Compiled control is supervised and engineered','Selected ancestral lineages and adaptive calibration, not untouched primary']},
              'randomness':{'used':True,'generator':'PyTorch CPU generators, deterministic algorithms; NumPy default_rng for compiled nulls','seed':[330601,330603,340601,340603,930601,950701,960601,970601]},
              'run':{'started_at':datetime.datetime.fromtimestamp(start,datetime.timezone.utc).isoformat(),'runtime_seconds':end-start,'exit_status':0},
              'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in outputs],
              'checks':['24 successor tests','Byte-exact uninterrupted1000-update replay and52 banks','Independent integer output audits','Frozen78 base tensors per access lineage','Bounded-codec factorization check'],
              'result':'Partial native access improvement, stronger known-stress calibration with sequential-access regressions, continued lack of J-space certification.',
              'residual_risks':['v1 schema does not enforce resource caps or input hashes; supplementary execution records supply before/after hashes','Local validator, canonical Mathbox CLI unavailable','Adaptive development and reused evaluation conditions','Parent trained-bound metadata correction documented','Resume semantics exact but pickle byte identity not guaranteed']}
    (ROOT/'checks/COMPUTATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':run()
