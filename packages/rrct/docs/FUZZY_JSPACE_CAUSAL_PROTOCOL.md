# Fuzzy-to-J Workspace Causal Protocol

## Purpose

This protocol tests a serial functional hypothesis:

\[
U_t \longrightarrow J_t \longrightarrow B_t \longrightarrow P_t \longrightarrow R_{t+1}.
\]

Here:

- \(U_t\) is task-conditioned fuzzy coalition membership
- \(J_t\) is a moving Jacobian-discovered sparse accessible state
- \(B_t\) is coherent broadcast into independent downstream consumers
- \(P_t\) is provenance-conditioned planning and memory action
- \(R_{t+1}\) is consequence-driven reopening and repair

The full chain is supported only when every link passes its own causal test. A
single aggregate score cannot compensate for a failed link. Runs report the
longest supported prefix.

This is a bounded engineering and synthetic-mechanism protocol. It is not a
test of subjective experience, consciousness, sentience, valence, welfare, or
moral status.

## Controller and evaluator separation

The evaluator may retain latent task variables for scoring. The controller may
not use them to diagnose, repair, route, plan, or write memory.

In particular, the controller must not:

- compare an estimated hidden coordinate map with the true map
- copy a true permutation, world rule, or source label into its estimate
- receive target coalition memberships
- train against J-space coordinates or semantic probe labels
- use event names to select a task or repair rule

Formation is learned from terminal consumer loss and declared resource costs.
Event type and task demand are sampled independently.

## End-to-end measurements

### Link 1: fuzzy formation to J-space admission

Measure:

- workspace-need balanced accuracy
- correlation between \(u_{ik}\) and the effect of \(do(u_{ik}=0)\)
- fuzzy versus hardened task performance
- fuzzy versus entropy-and-sparsity-matched shuffled membership
- change in J-space occupancy after a formation cut
- temporally shifted \(U_{t-1}\) and \(U_{t+1}\) controls

The result is formative only if changing membership changes later workspace
admission while matched shams do not.

### Link 2: sparse Jacobian-accessible state

At the declared residual state \(h_t\), collect consumer-directed Jacobians:

\[
G_t = \frac{\partial y_t^{\mathrm{accessible}}}{\partial h_t}.
\]

Fit the moving frame from development observations only. Report:

\[
\eta_J = \frac{\lVert G P_J\rVert_F^2}{\lVert G\rVert_F^2},
\]

plus:

- selected rank
- mean active nonnegative directions
- projector idempotence defect
- residual activation variance fraction
- held-out decoding
- frame transport and principal-angle stability
- same-rank PCA performance
- same-rank random-subspace performance

Decodability without causal transplantation or necessity is classified as a
probe subspace, not a workspace.

### Link 3: causal broadcast

The report, derived inference, plan, and memory-decision consumers branch from
the same pre-consumer state. They cannot communicate through a generated answer.

Test:

- semantic content transplantation
- coherent multi-consumer change
- J-space ablation
- norm-matched sham patches
- orthogonal-complement patches
- preservation of routine processing

A report-only effect is a report channel, not broad broadcast.

### Link 4: provenance-conditioned planning

Use identical accessible content under different causal histories. Include:

- valid information from a valid source
- correct information from an invalid source
- incorrect information from a valid source
- external activation injection
- foreign-memory import
- incompatible-context transplantation

Measure plan accuracy, false autobiographical writes, quarantine accuracy, and
content preservation under provenance cuts. A provenance cut should damage
source-correct planning and memory action without erasing the report content.

### Link 5: recurrence

Compare intact outcome feedback with:

- feedback cut
- recurrence cut
- equal extra feedforward compute
- null event boundaries

Measure true reopening, null reopening, post-error recovery, time to recovery,
and first-pass equivalence. Persistence alone is insufficient. A later action
must change because the consequence returned to the same controller.

## Selective intervention ladder

| Intervention | State expected to remain | Expected downstream loss |
|---|---|---|
| Membership shuffle or formation cut | Input observations | J admission, broadcast, planning, recurrence |
| J-space projection cut | Fuzzy membership | Broadcast and all later links |
| Broadcast cut | Membership and J decodability | Coherent multi-consumer behavior |
| Provenance cut | Content report and broadcast | Source-correct plans and memory actions |
| Feedback cut | First-pass report and plan | Reopening and post-error recovery |

Upstream preservation is tested with explicit equivalence margins. It is not
inferred from a nonsignificant difference.

## Matched baselines

Primary comparisons use identical examples, seeds, data order, rank, active
count, intervention norm, optimization budget, state bytes, and communication
bandwidth whenever applicable.

- same-rank PCA
- multiple same-rank random subspaces
- ordinary linear-probe subspace
- hard membership
- entropy-and-sparsity-matched random membership
- fuzzy direct-edge routing
- ordinary attention with matched top-k bandwidth
- recurrent message state with matched dimension
- no workspace
- full residual access as an unmatched upper bound
- label-aware oracle as a diagnostic ceiling only

Parameter count, optimization steps, examples, forward and VJP counts, state
bytes, peak memory, and wall time must be reported for a frozen comparison.

## Development and frozen gates

The values below are protocol targets, not universal cognitive constants. They
may be revised during development but must be frozen before holdout seeds are
exposed.

| Link | Proposed frozen practical gate |
|---|---|
| Formation | Need-balanced accuracy lower bound above 0.70, causal membership correlation lower bound above 0.20, fuzzy advantage lower bound above 0.05 |
| J-space | Normalized decoding lower bound above 0.60, Jacobian energy above 0.50, mean active directions at most 4, advantage above every matched subspace lower bound above 0.05 |
| Broadcast | At least three of four patch accuracies at least 0.70, flexible ablation drop lower bound above 0.20, routine change within plus or minus 0.05 |
| Provenance | Plan accuracy lower bound above 0.75, provenance-cut plan drop lower bound above 0.15, intact false-write upper bound below 0.10 |
| Recurrence | Reopen true-positive lower bound above 0.70, null false-positive upper bound below 0.10, feedback-cut drop lower bound above 0.20 |

Each primary contrast requires a one-sided seed-level 95 percent confidence
bound in the expected direction. The overall chain is an intersection claim.

## Smoke campaign

Smoke execution is limited to engineering validation:

- deterministic completion
- finite metrics and nonzero denominators
- strict feature contract acceptance
- exact interrupted and resumed trajectory equality
- intervention targets actually changed
- paired example identities remained aligned
- sham patch norms matched
- expected raw effect signs

Smoke results do not establish emergence rates or scientific endpoints.

## Frozen local campaign

The intended confirmation uses a fixed, hashed base model and 16 unseen seeds.
Seed is the primary statistical unit. Bootstrap seeds first and episodes within
seeds second. Holm correction applies to multiple baselines within each link.

The freeze must bind:

- model and tokenizer hashes
- adapter architecture and initialization policy
- generator and template files
- development and holdout manifests
- seed list
- layer, rank, sparsity, and moving-frame objective
- patch pairs and norms
- endpoint definitions, thresholds, and equivalence margins
- baseline definitions and fairness tolerances
- statistical source and compute budgets

## Falsifying outcomes

- If \(U_t\) predicts \(J_t\) but cutting \(U_t\) does not change \(J_t\), formation is descriptive rather than causal.
- If J-space is decodable but patching fails, it is a probe subspace.
- If PCA or random controls are equivalent, the Jacobian construction is not privileged.
- If patches change only reports, broad broadcast is unsupported.
- If provenance cuts preserve source-conditioned planning, provenance binding is unsupported.
- If feedback cuts preserve reopening and recovery, functional recurrence is unsupported.
- If only the explicitly scaffolded arm passes, the conclusion is induced mechanism, not spontaneous native emergence.

