# Komorebi Workspace Incubator v0.6
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
Its 420-file manifest and 20 tests passed before successor development. This turn
did not reconstruct missing v0.5 weights. The two required random-curriculum
parent checkpoints and relevant source modules are retained unchanged.

A and B denote two different dyad initialization lineages, not the two agents
inside one dyad. Both parents were previously selected for competence and have
different ancestral training budgets. This is not an untouched eight-seed cohort.

The original dyad has 171602 parameters. The copied access modules add 106530,
for 278132 total, about 62.1% more than the predecessor. Each agent retains one
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
Access-only trains 106530 copied parameters. Joint trains all 278132 parameters.
Each uses 1000 updates, batch 96, AdamW restart at 0.0003 and weight decay 0.00001,
one Torch thread and the same generated data. Forward calls and episode budgets
match; backward cost, trainable parameter count and wall time do not.

Training uses random nonidentity, inverse-palindrome, identity-token and repeated
flip programs at lengths 0,3,6,12,24. The named commuting-flip and swap-conjugation
generators are not sampled. Incidental short strings can occur in random programs,
so this is a generator exclusion, not a proof that every equivalent string is new.

Each post-working state has four independent terminal retrieval branches covering
all eight facts. Each branch includes a second same or changed cue. Only terminal
consumer/private labels provide targets. Four consumer types are withheld until
state formation: exact report, parity, late XOR-mask transformation and verification.
Their arguments are regenerated after target semantics are fixed. No query or
answer enters state formation. No original base parameter changes in access-only.

The final 1000-update checkpoint defines the main result. No best-checkpoint
selection is used. The data-generator states, Torch states and family/length
counts match within each lineage. All 78 original model tensors are unchanged
in both access-only lineages and remain so after secondary calibration.

## 3. Main result versus outcome-informed calibration

The main unseen-family/unseen-length result is partial. After seeing it, a
separate additional 1000-update access-only calibration exposed all six families
and lengths 12,24,48. Length 48 has 60% sampling probability in that phase.
This deliberately changes the question from generalization to learnability of
native retrieval on the known stress. The earlier main results are retained.

The table below uses a NEW 1024-history confirmation bank generated after all
checkpoints were frozen. Each score requires all eight facts correct for an
agent, averaged over the two agents. Four independent branches start from the
same post-program state. The stress is 48 operations of swap-conjugation.

| Lineage | Parent | Access-only, unseen family | Joint, unseen family | Access-only after known-stress calibration |
|---|---:|---:|---:|---:|
| A | 40.58% | 47.17% | 80.66% | 79.98% |
| B | 57.37% | 63.43% | 63.23% | 89.75% |

The calibrated column is not an unseen-family or unseen-length result. It has
an additional 1000 updates and a different distribution from the main comparison.
All 256 factual worlds and both opcode aliases may occur during training; the
confirmation concerns new histories, not unseen-world or unseen-alias learning.

Joint training is not a uniform repair. In lineage B, private recall after stress
falls from 92.09% to 83.53%.
That regression remains a failure rather than being hidden by better work scores.

The main 52-bank-per-model suite uses 512 histories per bank. The confirmation
uses 1024 histories and a new seed. Values across those suites differ slightly.
The report never substitutes an easier pooled score for all-eight exact recall.

## 4. The repaired state remains usable for native work, within limits

After repair, three new ordinary working operations are supplied, followed by the
late consumer. Access training did not contain working operations AFTER the copied
retrieval, so this is a distinct bounded interface-reuse test. Working operators,
silent updates and answer heads are frozen in calibrated models.

| Lineage | Private recall after repaired access | Short working reuse: exact | All eight facts after that reuse |
|---|---:|---:|---:|
| A | 97.57% | 93.99% | 71.44% |
| B | 97.02% | 97.61% | 85.06% |

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

In the 512-case known-stress suite, cutting both access-phase message directions
reduces calibrated all-fact recall from 78.42% to 5.27% in A and 91.11% to 3.42% in B.
Shuffling access messages reduces those scores to 2.44% and 2.15%. Directional cuts
are also retained and primarily harm the deprived recipient. Observation and
working-phase communication are left intact in these tests.

These are interventions on learned messages, not a demonstration of unique
Jacobian localization, natural subspace writing or general reciprocal authority.
They establish that the tested retrieval behavior uses the native access channel.
A full from-scratch no-wire competence control is not newly completed.

## 6. Repetition and clean-context regressions are substantial

At length 96, which neither main nor calibration training included, calibrated
all-eight recall is 9.08%
and 11.72% on confirmation.
This is a severe extrapolation failure. The unchanged incoming working computation
is itself weak at that length; it is not a pure access-only regime.

In the 512-case repeated-same-cue diagnostic, calibrated stress 48 all-eight recall
falls from 78.42%/91.11% after one cue to 57.32%/20.80% after eight. Two successive
retrievals were trained; eight were not. This limits extrapolation, rather than
contradicting the trained-depth result.

A separate post-outcome diagnostic makes four changing cues cover all eight facts,
then repeats the pass. It does NOT reset to a saved state between cues. It uses
1024 new histories. The first/second pass scores require the four requested pairs
to be jointly correct for the agent during that pass.

| Condition | A: first four cues | A: second four | B: first four | B: second four |
|---|---:|---:|---:|---:|
| Parent, no preceding work | 99.76% | 94.92% | 99.61% | 85.01% |
| Calibrated, no preceding work | 96.58% | 81.45% | 93.41% | 51.17% |
| Parent, stress 48 | 35.11% | 28.71% | 54.20% | 43.70% |
| Calibrated, stress 48 | 75.05% | 60.69% | 88.33% | 55.52% |

The calibration makes stressed sequential access better but harms some unstressed
sequential use. In the calibrated no-work condition, eighth-cue private recall is
53.17% and 54.79%. This is not a complete memory-preserving access mechanism.
It cannot be excused merely because the base weights did not change.

Main metadata correction: the raw parent-bank `untrained_length` flag used the
children's max24 instead of the parent's max12. Correct limits are explicit in
confirmation and consolidated metadata. No predictions or scores changed.
Depth alters recall branches only; working-reuse measurements use one new access.

## 7. An engineered bandwidth control, not a native neural result

A separate supervised linear reader was fit on 4096 parent-state examples per
lineage from a mixture of eight conditions. There is ONE fixed reader per lineage,
not one refit for every test. It maps the concatenated 128 coordinates to eight
fact scores. Its weights are then split into agent-local partial sums.

Each agent sends eight bounded real values using the supplied invertible scalar
codec phi(x)=x/(1+abs(x)). Each receiver reconstructs the other partial sum and
adds its own. Both reconstruct the central linear readout. Across 26 tested
conditions the maximum float64 discrepancy is 7.11e-15 and all bit predictions
agree exactly. On its own 512-case swap 48 bank, all-eight accuracy is 93.75% and
94.53%. This is not the same bank as the native 1024-case confirmation table.

This elementary construction rules out only a crude bandwidth impossibility for
the chosen linear partial sums. It remains a supervised compiled positive control:
it is not the GRU's learned codec, a shared hidden-state probe counted as native
repair, an autonomous writer or a discovered J-space. Finite-precision and function-
class restrictions still matter. The proof and numerical check are in the note.

## 8. Verification and exact scope

Twenty-four successor tests pass after two tooling corrections. A complete
1000-update uninterrupted replay reproduces all 122 saved model tensors, optimizer,
RNG states, every checkpoint field, checkpoint bytes and all 52 evaluation-bank
bytes exactly. The separate short resume test reproduces loaded computation state
and all tensor payloads; its pickle metadata bytes differ because optimizer string
keys are memoized differently after loading. Resumed-file byte identity is not
claimed. The initial failed byte assertion and its diagnosis are retained.

The independent integer/NumPy audit rechecked12779520 recorded output entries
in 416 primary/calibrated banks, plus 1966080 entries in 32 confirmation banks and
786432 entries in 24 sequential banks. These are reused histories, agents, branches
and interventions, not millions of independent experiments. The distributed codec
was checked separately across 26 conditions. All parent hashes, frozen tensors,
paired schedules and actual operating-system exit records are retained.

The first audit failed by treating an eval log as a directory. Directory filtering
was corrected and the full audit rerun without changing scientific outputs. The
streaming launcher was unavailable before shell execution; a monitored supervisor
captured child return codes. The original and repaired sources/logs are included.
The canonical Mathbox manifest CLI was not installed; a documented local v1
structure/path/hash validator is used. Its limits are explicit in the manifest.

No new projected-state support audit, localization claim, no-wire competence,
unilateral workspace-write result, partner transfer, original RRCT v0.62 primary,
pretrained-language-model experiment or subjective-state certification follows.

## Research conclusion

Native retrieval can be improved while the formation of the retained state is
held fixed. The next obstacle is preserving future access AFTER access itself,
not merely improving one-shot decoding. The proposed next test evaluates full
retrieval/working trajectories and clean-context noninterference at matched
budgets. It is a design, not an executed next-stage result.
