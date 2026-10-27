# Independent AVOC publication audit

Audit date: 2026-10-07. Source: `source/AVOC_Formal_v0.41.0`.
Role: read-only independent source review, performed before reading the new
publication manuscripts. This report does not alter the mathematical source.

## Normalized claim and primary verdict

The strongest final recorder claim is the following. In a finite rational
probability space, each identity has a finite latent Boolean source satisfying
the stated fresh-position conditional Bernoulli contract. A source-generative
recorder consumes the next latent bit on each new accepted checked report,
retains success and rejection, consumes no source position for a fault, and
retains no second sample on exact replay. For a fixed finite schedule of prefix
sizes, rational cell grids and nonnegative error allowances, every issued warm/
cold plan has the stated compatible realization and frozen-episode value, Q and
expected-policy regret guarantee except on an event of mass at most the sum of
the scheduled allowances. All rejected, globally pending and insufficient-
sample runs remain in the probability space and issue no plan.

**Primary verdict: proved as written, for the formally defined finite rational
source-generative model.** Source reconstruction agrees with the archived
kernel evidence. There was no fresh Lean compilation in this publication audit.
The verdict does not certify a physical attempt process, raw external log,
parser, host, database, authenticated authority or end-to-end deployed service.

The key theorem is
`Komorebi.AVOC.RecorderPolicy.recorder_issued_failure_le`, not a completion-
conditioned or posterior coverage claim. Its conclusion is

\[
\Pr(\exists M:\ \operatorname{recorderPlan}=\operatorname{some}(M)
    \land\neg\operatorname{EpisodeCertified}(M))\le\sum_{j\in J}\alpha_j.
\]

The equivalent complementary claim in `recorder_episode_coverage` gives mass at
least `1 − Σ alpha` to the event that every plan issued at that outcome is
certified. No issue implies that implication is vacuously true. There is no
positive lower bound on the chance of receiving a plan.

## Source provenance and evidence

The current mathematical files below match their source hashes in the archived
`results/v0.41.0/release_verification.json` receipt. An additional read-only hash
comparison covered all 188 paths in that receipt's `source_counts.source_sha256`
map: 188 matched, with no missing file or mismatch. That map is a checked subset
of the larger archive, not a new full-archive authentication claim.

| File | SHA-256 |
|---|---|
| `AVOC/RecorderPolicy.lean` | `436643930a1c503ef793dff50743b15b1d6a289f682f33f52e82bc698e565f09` |
| `AVOC/FiniteCalibration.lean` | `9ac4af6bb0d4165fe9c178520c3b834b990a3303c6197110a0cf168af99fd483` |
| `AVOC/RobustQuotePlanning.lean` | `9186283952d8d1ae784727653cd2f9ad95dd903819a908fea7eef29e1fe86ba8` |
| `AVOC/CalibrationBridge.lean` | `54357f9bb1ea9d92fc083688a94865ff01a6bd3b9a293ecf56107875aed50738` |
| `AVOC/RobustQuoteRecovery.lean` | `ac1c7e8ab0b6ac66e1dd54827cba17e288af1462f3dae97b9a8e0e2e6c62df37` |
| `AVOC/PlannerGuarantee.lean` | `03962ab3bac2419decefb5b6d753ddb4169e924924a3a4ddcca0bb2a7e204b46` |
| `AVOC/AtomicCommitModel.lean` | `de73514e541fc17bc1e1e86e5eedbd2f6f1a0662ce02640bcbeb0d56b2547361` |

The archive reports 195 non-audit mathematical modules, 2,268 named theorem/
lemma axiom reports, 222/222 passed release targets, and 135 substantive negative
rejections. Its allowed axiom union is `propext`, `Classical.choice`,
`Quot.sound`. Those are archived results, not checks rerun for this publication.
The standard Mathlib algebra, finite-sum and order facts remain part of the
pinned compiler/kernel/dependency trust boundary. This audit makes no external
historical novelty or priority determination.

## Claim cards

### C1. Exact cell-envelope confidence inversion

**Objects.** Natural `n,k,m`, rational `alpha,p`; sample count `k` lies in
`0,…,n`; `m>0`, `alpha≥0`, `0≤p≤1`. The exact count mass is

\[
b_{n,k}(p)=\binom nkp^k(1-p)^{n-k}.
\]

Cell `i`, for `0≤i<m`, is `[i/m,(i+1)/m]`. Its upper envelope is

\[
U_{n,k,m,i}=\binom nk((i+1)/m)^k(1-i/m)^{n-k}.
\]

Retain cells with `U > alpha/(n+1)` and return the hull of the retained cells.
When no cell is retained, the implemented fallback is `[0,1]`.

**Conclusion.** `FiniteCalibration.missMass_le`: the binomial probability that
the returned hull excludes `p` is at most `alpha`. No grid membership assumption
on the true rational parameter is required. This is a finite-sample confidence
statement about repeated data, not a posterior probability of the reported
interval. It is conservative and does not claim to be the shortest or an exact
tail-inversion interval.

**Proof reconstruction.** A grid cell contains every `p∈[0,1]`, including `p=1`
in the last cell. On that cell `b(p)≤U`. If `p` is outside the hull, every
containing cell was unretained, hence `b(p)≤alpha/(n+1)`. There are `n+1` possible
count values, so their excluded masses sum to at most `alpha`.

**Verdict.** Proved as written. Boundary `n=0` is harmless and the empty retained
set fallback avoids returning an empty interval. `m=0` is outside coverage's
hypotheses. The theorem permits `alpha>1`; that produces a valid but potentially
uninformative numerical bound. The current source quantifies rational `p`.
No monotone interval-shrinkage or asymptotic consistency result is supplied.
Additional observations can change the observed proportion, and a fixed coarse
cell envelope can remain loose. Coverage must not be relabeled as a universal
claim that every additional datum sharpens the interval.

### C2. Primitive conditional source law implies prefix count laws

**Objects.** `Law Ω` is a finite exact rational probability distribution;
`Sample N := Finset (Fin N)` represents a whole ordered Boolean vector by its
successful positions. `ConditionalLaw` demands, after every fixed revealed
pattern on any seen set and for every fresh position, that success mass is `p`
times that pattern's mass. This multiplication-only law also treats
zero-probability histories without a division.

**Conclusion.** `ObservationStream.conditional_implies_product` derives every
full-vector product probability. `prefix_count_fiber_eq_binomial` derives the
binomial count law of each fixed first-`n` prefix, `n≤N`.

**Proof reconstruction.** Induct over the seen set, using event splitting into
fresh success/failure. The product of factors is `p^k(1-p)^(N-k)`. Finite
combinatorial aggregation supplies `choose(N,k)`. Prefix truncation preserves
the primitive pattern masses.

**Verdict.** Proved as written. The law is a supplied premise, not inferred from
matching one-coordinate marginals, observed logs or syntactic validity. No
independence between different identities is required by the later union bound.

### C3. Finite schedule and arbitrary outcome-dependent selection

**Objects.** A finite index type `J`; fixed `n_j,m_j,alpha_j,p_j`; each count has
the exact stated binomial marginal. `m_j>0`, `alpha_j≥0`, `0≤p_j≤1`. Counts at
different checkpoints can be arbitrarily correlated. The selector `Ω→J` can
depend on the whole outcome.

**Conclusion.** Scheduled simultaneous failure and any selected checkpoint
failure have mass at most `Σ_j alpha_j`.

**Proof reconstruction.** C1 gives each bad-event bound. The finite union bound
requires no checkpoint independence. The selected bad event is contained in
the union. The theorem does not replace the sum by the selected allowance.

**Verdict.** Proved as written. This is selection among a fixed finite schedule,
not unrestricted optional stopping or a confidence sequence. The formal fixed
parameters do not authenticate prospective registration of a physical schedule.

### C4. Source-generative lifecycle recorder and actual terminal prefixes

**Objects.** `ObservationRecorder.State` holds a pending list and a separate
terminal log. A begin reserves an ID/key pair. A finish requires the matching
pending intent, unless it is an exact terminal replay. Unfinished outcomes are
rejected; an ID cannot be reused for a changed key/outcome. `RecorderReveal`
generates a fresh report's outcome from the next source bit, checks exact replay
before any source consumption and records faults without consuming a bit.

**Conclusion.** Accepted finite generated runs refine the raw recorder and the
reveal machine. `run_samples_eq_take` identifies each actual terminal sample
list with a first-source prefix. New reports retain both true and false bits.

**Verdict.** Proved as written for these finite pure machines. A raw external
finish event has supplied labels and is not thereby proven to originate in this
generative machine. Global ID uniqueness is once-only terminal retention, not
exactly-once execution of physical work or detection of the same work under a
new ID.

### C5. Gates, observed counts and unconditional plan issuance

**Objects.** `RecorderPolicy.gatedCounts` returns no count for a rejected run or
any globally pending operation. After full resolution it applies
`ObservationPolicy.availableCount` to the actual terminal samples. Available
counts are exactly scheduled prefix counts by `gatedCounts_faithful`.

**Conclusion.** C2's count laws and C4's correspondence discharge the abstract
`ObservedCalibration.Faithful` obligation. Both selected warm/cold counts must be
available. C3's simultaneous good event makes every issued plan certified. The
unconditional uncertified-issuance event has mass at most `Σ alpha`.

**Additional exact hypotheses.** `n_j≤N(key_j)`; a supplied
`DeterministicRealization md` for warm/cold setup and gross fields; warm and cold
selectors always select strata whose true probabilities respectively equal
the fixed `wp,cp`. Adaptive commands/availability do not need independent
completion. The theorem accounts for failed runs by their no-plan output.

**Verdict.** Proved as written. It proves no availability, physical termination,
sampling cost, productivity or completion-conditioned confidence guarantee.

### C6. Frozen quote realization to value and whole-policy expected regret

**Objects.** A protected quote model `QModel` with exact natural setup bands,
rational nonnegative gross bands and probability bands. A `Realization md`
provides memberships for setup, gross and success probability. Nominal planning
reserves upper setup, uses lower gross and lower probability. The true system
changes the reward/probability to realized values but deliberately keeps the
same nominal state transitions, admissible actions and reservations.

Define primitive total reward-width `e`, L1 row-width budget `q`, and nominal
reward envelope `R`. Then

\[
D_h=\sum_{k=0}^{h-1}(e+qkR),\qquad E_h=D_h+e+qhR.
\]

The implementation's `valueRadius=D`, `globalQRadius=E`, and action-specific
`localQRadius = D_h + rewardRadius(a) + probabilityRadius(a)hR`.

**Conclusion.** `value_error`, `local_q_error` and their interval forms bound the
actual constrained value/Q. `robustChoice md h` maximizes nominal Q minus the
local radius, with `h` continuation steps (total action horizon `h+1`). Its
first-action gap is at most `2E_h`. The policy at total horizon `H` obeys

\[
0\le V_H^r(s)-V_H^{\pi,r}(s)
   \le\sum_{k=0}^{H-1}2E_k.
\]

**Proof reconstruction.** Reward-band membership bounds primitive reward
differences. The Bernoulli L1 row distance is bounded by twice the probability
width. Bounded continuation values turn row distance into transport error.
Bellman induction accumulates primitive and transport errors. Lower-Q
maximization bounds the chosen Bellman gap. Normalized expectation telescopes
the stagewise gap over the whole legal policy tree.

**Verdict.** Proved as written. The regret is an expected finite-horizon
policy-value difference, not realized trajectory loss, cumulative online
learning regret or measured speedup. Its optimum uses the same conservative
guard. A comparator with a larger exact-cost feasible set is outside the bound.
Probability learning does not establish deterministic setup/gross memberships.
Quotes stay fixed during a policy episode.
The selector is an exact maximizer of the certified lower-Q surrogate, not a
claimed exact maximin optimizer over the whole family of compatible models.

### C7. Corrected competitor-only dominance

**Objects.** A feasible selected action `a`. For every *distinct* feasible `b`,
`upperQ(b)≤lowerQ(a)`; a compatible realization is supplied.

**Conclusion.** `CalibrationBridge.competitor_dominance_sound` proves that the
true Q of `a` is at least every feasible competitor's true Q. Its Boolean checker
has a source-level soundness theorem.

**Verdict.** Proved as written. The older all-action condition includes `a`
itself and forces its radius to zero. Use the distinct-competitor version when
describing non-singleton robust evidence. Certifying this one action does not
by itself establish every later action in a policy.

### C8. Work reservations, affordable depth and truncated lookahead

**Objects.** An executable rational finite-branching model whose `Realizes`
contract exactly matches a guarded system's action set, observation list,
probability, transition and reward. A legal fallback exists. A declared reward
bound `|reward|≤R` holds on all legal actions.

**Conclusion.** `PlannerWork.evaluate_work_le` bounds the evaluator's abstract
counter under supplied action/observation branch bounds. `affordableDepth`
chooses the largest fitting depth up to the requested cap. A choice using depth
`d≤H` has first-action gap at most `2(H−d)R`. A whole schedule gets the sum of
its per-stage gaps. `charged_regret` adds a declared nonnegative bounded compute
charge to an established gross loss budget.

**Verdict.** Proved as written. Work is a counter convention, not a rational
bit-complexity or wall-time theorem. Reservation scanning/arithmetic is outside
that evaluator counter. A work-to-reward conversion is supplied, not measured.
Depth zero yields only the conservative legal-fallback bound, not optimality.

### C9. Pure recovery and atomic abstract storage

**Objects.** `RobustQuoteRecovery.Intent` contains sequence, pre-state view,
action and exact quote evidence. A commit contains that intent, outcome tag and
post-state view. A checkpoint contains the logical runtime and last commit.

**Conclusion.** Fresh accepted acknowledgment matches the supplied evidence,
pre/post-state and sequence, and successfully runs `RobustQuote.confirm` for
the committed action. Safe checkpoints stay safe. Exact duplicate
acknowledgment is idempotent. Unfinished outcomes are rejected and do not infer
a report or retry. The older `CommitRecovery` has analogous contracts.
`AtomicCommitModel.publish` makes new store view, sequence and receipt one
abstract atomic step. Reconciliation leaves that abstract store unchanged.

**Verdict.** Proved as written. These are pure reduction/reconciliation
guarantees. They do not prove physical transaction atomicity, persistence,
authentication, parser refinement, rollback of external side effects or
exactly-once operations. Acknowledgment alone does not prove the action was
originally selected by `prepare/robustChoice`; that provenance is a separate
input. Its duplicate branch correctly reuses the exact stored commit without
revalidating a separately passed outcome payload. Quote equality is comparison
against supplied current evidence; it is not a cryptographic authenticity proof.

### C10. Completion ordering is not an IID-preservation theorem

**Proposed false claim.** Independent attempted outcomes in initiation order,
complete valid terminal logs and no pending IDs imply IID first-completed
prefixes at the attempted success parameter.

**Smallest counterexample.** Two independent fair bits. Success takes one time
unit and failure two; IDs break ties. All operations finish and all reports are
retained. The first stored bit succeeds except when both attempted bits fail,
so its success probability is `3/4`, although each attempted marginal is `1/2`.

**Implemented-interval example.** Twenty independent fair attempts, success-
first completion, first ten terminal labels, `m=10,alpha=1/10`. The all-success
band is `[3/5,1]`, which excludes `p=1/2`. Every `S≥10` has that prefix and
fails coverage; `S=0` also fails with `[0,2/5]`. The exact total miss mass is

\[
(\binom{20}{0}+\sum_{s=10}^{20}\binom{20}{s})/2^{20}
=616667/1048576.
\]

The dominant event `S≥10` alone has mass `308333/524288`; it is a lower bound,
not the exact total failure mass.

**Verdict.** Refuted, with the two-bit finite counterexample. The interval
example is exact finite rational computation, explicitly **not a new Lean
theorem**. It does not refute the source-generative formal theorem, whose
accepted bits are assigned in report order and whose source law is a premise.
General physical attempt/report-order coupling remains incomplete.

## Dependency graph

```text
Finite rational Law + per-key ConditionalLaw [supplied model contract]
    → pattern/product probabilities [ObservationStream internal proof]
    → fixed prefix binomial count laws [ObservationStream internal proof]

source-generative report commands [definition; not physical host theorem]
    → recorder/reveal refinement [RecorderReveal internal proof]
    → actual terminal lists are source prefixes [internal proof]
    → gated available counts are fixed latent counts [RecorderPolicy proof]

binomial count laws + exact cell-envelope construction
    → fixed-checkpoint confidence coverage [FiniteCalibration proof]
    → simultaneous coverage for finite fixed schedule [union-bound proof]
    → adaptive selected warm/cold bands cover [event containment]

deterministic setup/gross memberships + selected true strata [supplied]
    → compatible quote realization [CalibrationBridge constructor]
    → value/Q bands + expected frozen-policy regret [internal proofs]

all of the above + rejected/pending/insufficient samples issue nothing
    → unconditional uncertified-issuance bound [RecorderPolicy final theorem]
```

This is an obligation graph, not a new proof artifact. There is no dependency
cycle in the audited chain: the source law is never justified by the final
coverage theorem, and pointwise episode validity is proved before the outer
probability transfer.

## Obligation matrix

| Obligation | Status | Decisive locator / boundary |
|---|---|---|
| Finite probability normalization/nonnegative weights | passed | `CalibrationSchedule.Law`; event sum/complement proofs |
| Count mass arises from ordered product vectors | passed | `ObservationStream.vectorMass_card_sum`, `conditional_implies_product` |
| Physical service satisfies ConditionalLaw | conditional | supplied contract; no physical coupling proof |
| Source prefixes agree with actual generative terminal records | passed | `RecorderReveal.run_refines`, `run_samples_eq_take` |
| Faults and replay do not consume samples in the machine | passed | next-bit/replay command definitions and refinement |
| Raw external events universally follow the generative machine | not addressed | syntax/typed label acceptance is insufficient |
| Exact grid envelope includes rational endpoint probabilities | passed | `grid_covers`, `mass_le_envelope` |
| Empty retained set and `n=0` boundaries | passed | `[0,1]` fallback; mass-sum argument still applies |
| Calibration when `m=0` | out of scope | theorem requires `m>0` |
| Finite simultaneous and selected coverage without cross-checkpoint independence | passed | `scheduled_binomial_failure_le`, `selected_binomial_failure_le` |
| Physical prospective schedule authenticity | not addressed | fixed theorem parameters do not authenticate commitment |
| Available observed count is the scheduled latent count | passed | `gatedCounts_faithful` |
| Global pending, rejection or insufficient selected sample blocks issue | passed | recorder gates and `observedPlan_none_*` |
| Deterministic setup/gross match the quote bands | conditional | `DeterministicRealization` membership inputs |
| Selected warm/cold stratum matches fixed true parameter | conditional | `hwparam/hcparam` quantified for every outcome |
| Realization to value/Q error | passed | `RobustQuotePlanning.nominal_certificate`, `value_error`, `local_q_error` |
| Whole frozen-policy expected regret | passed | `robust_policy_nearGreedy`, `robust_policy_regret` |
| Same conservative action sets in true/nominal comparator | passed | `trueSystem.actions := nominal.actions` |
| Broader exact-cost optimum, sample-path regret or adaptive mid-episode quote changes | out of scope | not the stated system/comparator |
| Corrected dominance permits nonzero selected radius | passed | distinct competitors in `CompetitorDominance` |
| Counted planner work never exceeds reservation | passed | `PlannerWork.evaluate_work_le`, `runReserved_success` |
| Physical bit-operation/time complexity or empirical utility conversion | out of scope | explicit counter convention / declared conversion |
| Recovery preserves safe logical checkpoint and exact replay | passed | `acknowledge_safe`, `acknowledge_idempotent` |
| Original recommendation provenance of arbitrary accepted commit | conditional | prepare-derived intent must be supplied separately |
| Universal Python, JSON, OS, SQLite or remote authority refinement | not addressed | bounded executable comparisons are evidence only |
| Complete resolved logs preserve initiation-order IID law | failed | two-bit completion-order counterexample |
| Completion-conditioned nominal coverage follows from issued-risk theorem | failed | conditioning can select failures; no such theorem |
| Positive availability/productivity lower bound | not addressed | universal no-plan output is allowed by final bound |
| Infinite streams, real parameters, drift or unrestricted stopping | out of scope | current finite rational theorem |
| New publication freshly compiles all Lean | not addressed | compiler unavailable here; archive evidence only |

## Manuscript risks to prevent

1. Do not describe the final result as unconditional correctness of physical
   artifact selection. It is an unconditional *issuance-risk* theorem under
   explicit statistical and deterministic model contracts.
2. Do not write `P(certified | issued) ≥ 1 − Σ alpha`. That conclusion requires
   extra information and can be false even when the stated issued-risk theorem
   holds. Also avoid a posterior probability attached to one observed band.
3. Keep the finite schedule's total error distinct from a selected checkpoint's
   individual error, and from the separate expected policy regret budget.
4. Do not call rational cell-hull inversion Clopper–Pearson or shortest interval
   inversion. It uses a conservative per-count envelope threshold.
5. Distinguish attempted-outcome success probability from accepted/report-order
   source success probability. Honest complete logs do not bridge them.
6. Do not advertise exactly-once physical execution, automatic retries, persisted
   crash-safe recording or external rollback on the basis of recorder/acknowledge
   pure functions. The recorder CLI is a snapshot reducer.
7. Preserve action-horizon indexing: `Q_h` and `robustChoice h` have one selected
   action plus `h` continuation steps; `V_H` has total horizon `H`.
8. Quote model agreement is exact data equality relative to a protected record,
   not a signature or independent empirical verification of quote truth.
9. Formal source theorem inventory counts named theorem/lemma reports, including
   inherited helpers, not 2,268 independent new mathematical breakthroughs.
10. Lean status must say archived kernel checks. Fresh Python or prose review
    must not be silently substituted for a fresh kernel run.

## Commands and review scope

The review read the raw `.lean` definitions and proofs with `sed/cat`, followed
the imports through `FiniteCalibration`, `CalibrationSchedule`,
`ObservationStream`, `ObservationRecorder`, `RecorderReveal`,
`ObservedCalibration`, `CalibratedPolicy`, `CalibrationBridge`, `QuoteAuthority`,
`RobustQuotePlanning`, `GuardedModelError`, `GuardedPolicyRegret`, `PlannerWork`,
`PlannerGuarantee`, `RobustQuoteRecovery`, `CommitRecovery` and
`AtomicCommitModel`. It read `PROOF_BOUNDARY.md` and `GAP_LEDGER.md` after
establishing the core definitions. Current source hashes were computed with
Python `hashlib.sha256` and compared to the release receipt. The exact archived
completion-order JSON was read, and its small two-bit counterexample and count
class formula were reconstructed analytically. The publication's independent
numerical checks are delegated to the separate exact-figure/evidence agent and
are not duplicated or claimed here.

## Remaining gap and strongest safe publication statement

No missing mathematical implication was found inside the audited source-
generative recorder → finite confidence schedule → frozen policy chain.
The smallest missing implication for a physical-service claim is a justified
coupling from its initiation/outcome/fault/completion process to the finite
report-order latent stream satisfying the exact conditional source law.
Universal host decoding/storage refinement and authenticated evidence are
separate additional obligations. Fixing a physical record's order to initiation
indices is a possible future route, not a proved repair in this archive.

The strongest safe summary is: **AVOC provides certified finite artifact
planning, model error and expected-policy regret bounds, exact rational
calibration, lifecycle retention and recoverable logical accounting within
explicit source and execution contracts.** It also preserves exact
counterexamples identifying why valid complete logs alone cannot supply its
statistical contract. The cheapest further checks for publication are matching
each manuscript theorem to these claim cards and reading its quantifiers,
comparator and evidence label; a fresh Lean run remains a separate reproduction
step when a compatible compiler is available.

## Manuscript audit status

### Core chapters

`manuscripts/core_chapters.tex` was independently read after the source-first
audit. Its own source map was used only to identify further raw files; the
review checked the actual definitions in `Core`, `ArtifactBinding`,
`RecursiveSynthesis`, `SemanticCostCertificate`, `AffineFactorization` and
`BayesianInstability`, in addition to the earlier chain. The prose proofs were
also reconstructed directly, including the finite-fiber decoder, Bayes
normalizer cancellation, expectation grouping and both rank bounds.

| Manuscript claim | Verdict | Scope preserved |
|---|---|---|
| Fiber criterion, coarsest sufficient target and joint decoder | proved as written | Nonempty target for total unreachable-state default; no efficient/shortest representation claim |
| Deterministic and stochastic information-value domination | proved as written | Fixed utility/action space; garbling direction only; cost inequality explicit |
| Bayesian total update, sequential weight products and compression square | proved as written | Nonnegative weights, positive ordinary conditioning masses; likelihood factorization explicit |
| Rare-evidence posterior flip | proved as written | Exact rational two-world example; full L1 distance 2 |
| Deterministic control value preservation and refinement counterexample | proved as written | Common finite admissible action set; transition closure required |
| Projected stochastic quotient | proved as written | Finite raw/quotient spaces, surjective abstraction, admissible-action representative independence |
| Data-only propositional checker and ticket admission | proved as written | Dependency truth supplied; no arbitrary Lean ingestion or authenticated external work |
| Bounded Boolean synthesis and recursive semantic compaction | proved as written | Fixed three-variable tree grammar, examined/full-layer cost scope distinct |
| Attained semantic global minimum | proved as written | Constructor lower bounds plus attaining witnesses; entire defined tree grammar only |
| Zero-and-basis affine probes and typed replacement | proved as written | Ring-valued affine candidates; no arbitrary function interpolation |
| Affine minimum-width/rank tariff and retargeted reuse | proved as written | Field coefficients, both offsets checked, two-dense-stage tariff scope preserved |

No blocking correction was required. One optional premise clarification was
sent to the author: the deterministic information-value theorem should
explicitly say both observation alphabets are finite because its maximum-policy
notation was defined only in that regime. That assumption is already implicit
in the preceding definition. The new worked examples are elementary prose
applications, not relabeled Lean theorems. No novelty conclusion is inferred.

### Lean companion

`manuscripts/lean.tex` was read in full for its explanatory prose, selected
signatures, proof excerpts, evidence interpretation and reproduction guidance.
A separate literal-source comparison then checked all 74 file-attributed
listing blocks (including definitions and negative controls): all 74 occur
unchanged in their stated raw source files, with zero mismatches. This verifies
source fidelity of the excerpts, not independent compilation of the snippets.
The document correctly explains that statement excerpts omit their proof body
and ambient instances and are not standalone Lean files.

Three manuscript corrections were requested and verified in the revised text:

1. The affine factorization paragraph originally described a nonzero-minor
   lower witness. It now correctly describes the actual sandwich witness
   `L A H = I_k`, exact `VU=A` composition and affine offset obligations.
2. The unique-optimum paragraph now explicitly requires an action margin
   greater than `2 eta`, matching `q_margin_preserves_unique_optimum`.
3. The older self-inclusive dominance test is now explicitly labeled
   restrictive because it forces the selected radius to zero. The corrected
   competitor-only proof and checked-optimal statement are shown separately.

| Companion claim family | Verdict | Evidence boundary |
|---|---|---|
| Source excerpts and exact locators | proved as written as source-fidelity claims | 74/74 literal raw-source matches; no Lean snippet compilation |
| Approximate-Q policy regret and lookahead charge | proved as written | Legal state-dependent actions, expected finite-horizon value, declared work tariff |
| Affine lower witness and unique-action margin | proved as written after the verified local corrections | Actual `LAH=I_k`; strict `2 eta` margin |
| Robust interval dominance | proved as written after the verified distinction | Old self-inclusive and new distinct-competitor tests are separated |
| Final recorder calibration and issued certificate | proved as written | Explicit source law, fixed schedule/strata, deterministic fields; unconditional issued-risk bound |
| Raw/generated machine and host decoding distinctions | proved as written | Raw labels not authenticated; executor proof starts with already-decoded commands |
| Recovery/intent provenance explanation | proved as written | Prepared recommendation provenance separate from supplied-action acknowledgment |
| Archived counts and fresh evidence labels | correct as stated | Archived kernel/compiler results remain archived; current source/receipt checks are identified |
| Completion-order physical interpretation | refuted as the document states | Exact two-bit/20-attempt evidence; no false counterexample to the generative theorem |

No unresolved substantive issue remains in the reviewed companion prose. The
reproduction commands are instructions, not executions claimed by this audit.

### Introduction and closing material

`manuscripts/introduction.tex` and `manuscripts/closing.tex` were independently
read. The running rank-one example was checked against the actual
`StagedAffineExamples`, `LazyStagedExamples` and `RobustQuoteExamples`
definitions: dense cost 36, width-one cost 21, 1,000-call gross saving 15,000,
warm setup 133/net 14,867, and cold setup 196/net 14,804 all agree. These are
declared model tariffs/payoffs, as the prose states.

Two local scope corrections were requested and verified in the introduction:
the decision layer now permits an infinite state space with finite action/
observation branching, and pointwise certification is now asserted only on
the simultaneous-coverage event. Outside that event the text explicitly permits
an uncertified issued plan and gives the unconditional risk bound.

The closing assurance matrix correctly keeps the artifact, tariff, source law,
frozen controller and recovery obligations separate. Its integration claims
refer to the proved internal chains and do not claim historical novelty or
unrestricted physical correctness. Its bibliographic scope is documented in
`reviews/literature_scope.md`: Blackwell is historical context with a self-
contained finite proof, and current official Lean/SQLite references explain
trust boundaries rather than substituting for a missing mathematical proof.

Additional independent read-only integrity checks confirmed the closing's
payload claims: `python3 tools/check_manifest.py` returned
`16912/16912 file hashes match`, exit 0. The delivered original ZIP digest is
`04efab87010b3b88c9a119275e190423a2465da32ba1e526edb7e6d2e0cd077e`, matching the
quoted baseline. Those checks establish consistency with the delivered manifest
and baseline, not physical provider authenticity or a new compiler run.

**Verdict: proved as written for the internal mathematical/model summaries;
the named physical obligations remain conditional/out of scope as stated.** No
unresolved substantive issue remains in the reviewed introductory/closing prose.

Planning and visual manuscript reviews are recorded below.

### Independent figure 6/7 restriction audit

A separately delegated, read-only check reconstructed the raw quote model,
feasibility guard, horizon convention, Q transport bounds and competitor test
before comparing the plotted values. The primary verdict is **correct only
after a stated restriction**: these are abstract quote-planning fixtures at
the initial both-untried, zero-budget state with zero setup fees, and at
continuation horizon `h=1`, meaning two total actions. Initially the legal
actions are stop, warm inspection and cold generation; deployment is illegal.

| Figure claim | Verdict and exact evidence |
|---|---|
| Figure 6 warm nominal Q 120, radius 208, enclosure [-88,328] | proved as written for the stated fixture; reward error is zero, envelope 260, and local probability term is `2*(2/5)*260=208` |
| Figure 6 cold Q 60 and lower-Q choice cold | proved as written at `h=1`; lower scores are -88, 60 and 0 |
| Figure 6 sharper warm range [120,200] | proved as written as the true expected acquisition-then-deployment Q range `200*p`; it is not the primitive one-step reward interval |
| Figure 7 learned band [361/500,433/500] | proved as written for the specified finite grid; independent integer boundary comparisons and decreasing envelope ratios identify the retained contiguous cells |
| Figure 7 nominal 722/5, radius 1872/25, enclosure [1738/25,5482/25] | proved as written; width 18/125 and `2*(18/125)*260=1872/25` |
| Figure 7 competitor-only exact-optimum certificate | proved as written conditional on compatible frozen realization; `1738/25>60>0` gives distinct-competitor dominance |
| Executable affine artifact attainability for these gross quotes | not established, and impossible for the bound one-call source under its declared artifact gross formula |

The last row is substantive: `uncertainModel` binds `rankOneProgram`, whose
declared source cost is 36, at one call, but quotes gross 200 and 60.
`deploymentGross = calls*(sourceCost-selectedCost)` and natural selected cost
imply artifact gross at most 36. `QuoteAuthority.Realization` deliberately only
requires interval membership; it does not require the existence of executable
artifacts realizing each abstract gross quote. The plots must therefore say
**abstract quote-planning fixture** and cannot be integrated into the running
affine example as attainable savings. Authors were notified.

The horizon restriction is also essential: an independent small exact Bellman
reconstruction at `h=2` and `p=3/5` gives warm and cold Q both 144, rather than
120 and 60. Finally, figure 6 itself refutes an exact-minimax interpretation:
warm's true worst-case two-action payoff is 120, but lower-Q selection chooses
cold with payoff 60. This is a valid conservative selector, with the advertised
formal regret bounds, rather than an exact maximin optimizer. The confidence
coverage dependency remains separate from observed-count arithmetic.

No source was changed, no large enumeration was duplicated, and no Lean
compilation was run. This audit used raw-source inspection, exact Fraction
arithmetic, a small horizon-0/1/2 Bellman reconstruction, and four integer
calibration-boundary comparisons. The regenerated figure script and catalogue
captions were subsequently inspected: both now state the abstract fixture,
initial state, zero fees and `h=1`/two-action convention, and explicitly explain
the unattainable gross quotes. Figure 6's embedded label now reads "Warm true Q
range" and its caption distinguishes this expected Q range from primitive
reward. These requested figure corrections are verified. Planning and visual
reviews are recorded below.

### Planning, calibration, recorder and recovery chapters

`manuscripts/planning_chapters.tex` was read in full, together with its source
map. The added durable-upgrade portion was checked independently against raw
`VerifiedUpgrade.lean`, `DurableUpgrade.lean` and `DurableUpgradeLaws.lean`.
Those definitions charge the protected evaluation cost at a fresh funded begin,
bind the complete parent state, settle with zero second evaluation debit,
retain the charge on abandon and carry explicit paid-trace debit totals.
Restoration is equality with a replay from a specified initial version; its
safety theorem additionally requires the authority contract for that version.

Two substantive manuscript corrections and one related premise clarification
were requested and verified in the saved revision:

1. The final integration paragraph now states episode guarantees on the
   simultaneous-coverage event and bounds uncertified issuance by the total
   scheduled allowance, rather than implying every issue is certified.
2. Restoration's safety conclusion now explicitly assumes the specified
   initial version satisfies the authority's contract.
3. The upgrade section now states that checker soundness and lower/upper
   utility-bound soundness are supplied authority obligations for one fixed
   workload, objective and unit convention, not proved by receiving a score.

| Planning claim family | Verdict | Exact scope/evidence |
|---|---|---|
| Guarded Bellman recursion and complete adaptive optimum | proved as written | Finite feasible actions and observations; states may be infinite; same information/guards; all branches legal |
| Artifact-backed 1,000-call rank-one comparison | proved as written | Source witnesses and declared tariffs; two-action scores 14,867 and 14,804; no measured return |
| Executable evaluator correspondence and planning allowance | proved as written | `Realizes`/workflow connection; abstract recursive-node cost, not whole-host time or bit complexity |
| Protected quote identities and nominal guard | proved as written | Exact protected evidence equality; true system keeps upper-setup reservations and nominal action guards |
| Bernoulli L1 transport, primitive errors and Q/value radii | proved as written | `D_h`, local radius and global radius match raw formulas and induction |
| Distinct-competitor dominance and old self-inclusion | proved as written | Sound enclosure chain; self-inclusion forces chosen radius zero |
| Lower-Q surrogate choice | proved as written | Explicitly distinct from exact minimax; figure fixture demonstrates conservatism |
| Whole frozen-policy regret | proved as written | Expected complete-plan regret against same guarded comparator; no pathwise bound |
| Polynomial regret formula | proved as written as a prose algebraic consequence | Sum simplifies to `epsilon H(H+1) + delta M H(H-1)(H+1)/3`; no new Lean declaration |
| Finite-grid exclusion-budget coverage | proved as written | Rational true parameter, positive grid, nonnegative allowance, strict envelope retention and full-band fallback |
| Scheduled/adaptively selected coverage | proved as written | Fixed finite schedule; correlated counts and arbitrary selector allowed; total allowance retained |
| Primitive source law and correlated-bit obstruction | proved as written | Fresh conditional law is supplied; equal marginals do not establish it |
| Lifecycle retention and whole-run source-prefix refinement | proved as written | Generated fresh reports, exact replay before consumption, faults no sample; arbitrary external labels not thereby coupled |
| Unconditional recorder-to-policy bound | proved as written | Gates derive/check acceptance, global resolution and selected sample availability; deterministic fields and fixed strata remain supplied |
| Completion-conditioned coverage claim | refuted as the chapter states | Archived two-bit proof plus clearly labeled elementary ten-success issuance illustration |
| Fully completed outcome-dependent report ordering | refuted as the chapter states | Explicit two-bit rational derivation and exact twenty-attempt lower bound; no new kernel theorem |
| Fresh acknowledgment, duplicate replay and prepare provenance | proved as written | `confirm` transition checked fresh; replay does not revalidate arbitrary new payload; planner origin requires prepare provenance |
| Upgrade prepaid accounting and utility monotonicity | proved as written | Pure funded traces, protected authority soundness and credits; physical payment/execution not inferred |
| Restored equality and safety | proved as written after correction | Equality unconditional on successful restore; safety additionally needs initial authority contract |

The abstract `uncertainModel` fixture restriction and `h=1`/two-total-action
indexing are now explicit in the chapter; it cannot be confused with the
separate artifact-backed 1,000-call comparison. No unresolved substantive issue
remains in the reviewed planning text. All mathematical manuscripts have now
been independently read, with the visual review recorded below. This remains a
read-only source/prose audit using archived kernel evidence, not fresh Lean
compilation or universal host/storage verification.

### Visual guide

The full 31-section `manuscripts/visual.tex` and its source map were read. The
final saved revision was inspected after the author applied the requested
corrections. The finite-grid page now explicitly assumes rational
`p in [0,1]`, `m>0`, `alpha>=0`, and states the `[0,1]` empty-retention fallback.
The general fiber converse now names its inhabited-target premise; the bit
example satisfies it. The prefix display's missing `left` backslash was also
corrected. The reading route now agrees with all 31 section numbers.

| Visual claim family | Verdict | Scope retained in the final saved guide |
|---|---|---|
| Task sufficiency, collisions and exact admission | proved as written | Defined decoders, inhabited target for converse, supported proof syntax and exact protected subject |
| Finite-field rank-one factorization and minimum width | proved as written | Actual archived map/offset and width witnesses; 625-input numerical check distinguished from the theorem |
| 36/21 per-call tariffs, 133/196 setup and amortization | proved as written | Declared source cost model; warm threshold9, cold14 and 1,000-call nets14,867/14,804 |
| Success-probability crossing4979/5000 | proved as written as exact two-action route arithmetic | Unsuccessful setup paid; additional continuations not included in the plotted route comparison |
| Grid and n500 synthetic intervals | proved as written | Positive grids/nonnegative allocation/full-band fallback; separate prospectively fixed grid scenarios |
| L1 transport, horizon convention and planner reservation | proved as written | Factor2 Boolean row error; continuation h1 means two actions; evaluator-node work1461, not host time |
| Conservative abstract fixture and distinct-competitor dominance | proved as written after verified fixture restrictions | Initial untried/setup0/two actions; gross200/60 not artifact-backed savings; conditioned on valid compatible membership |
| Whole-policy regret and exact-band recovery | proved as written | Expected frozen finite-horizon policy value, same conservative guards, no pathwise claim |
| Budget, selected execution and deterministic refinement | proved as written | Reserved spending, selected checked artifact, probability band retained as a separate statistical premise |
| Recovery, lifecycle, replay and actual source-prefix relation | proved as written | Pure recorder distinguished from external executor/storage; generated labels versus raw supplied labels |
| Conditional source laws and final issuance | proved as written | Fixed finite rational within-source law, fixed schedule/strata, global pending gate and unconditional bad-issuance mass |
| Completion conditioning and completion-order shortcuts | refuted as the guide states | Kernel two-bit obstruction distinguished from exact larger computations; lower-bound event and total miss mass distinct |
| Bayesian receipt beliefs and persistent/IID retry distinction | proved as written | Source posterior values3/4,1/4,1/3; persistent value1 versus IID three-step7/4; no-revival scope explicit |
| Rare-evidence instability | proved as written | Nonnegative likelihood weights and positive evidence mass; maximal posterior L1 separation2; denominator assumptions explicit |
| Formal/executable/physical assurance layers | correct as stated | No physical exactly-once, universal host refinement, source authentication, unrestricted stopping or measured-productivity theorem |

The extra Bayesian/retry/planner values were checked against their raw source
statements, not inferred from visual similarity. The guide consistently treats
the two plot examples as abstract quote planning and the rank-one example as
artifact-backed declared savings. No unresolved substantive issue remains in
the final saved visual text. PDF rendering/layout review is a separate task and
is not claimed by this mathematical audit.

## Completed audit status

Independent source-first review and subsequent manuscript review are complete
for the main paper, Lean companion and visual guide. All requested substantive
scope/premise corrections were verified in their saved revisions. The exact
claim-family verdicts above apply to their stated hypotheses; they are not a
blanket certification of the external service. The strongest final statistical
claim remains the unconditional uncertified-issuance bound under the explicit
finite rational source-generative model. Physical coupling, authentication,
universal host/storage refinement and useful issuance/productivity remain open
or outside scope as the manuscripts state. No fresh Lean compilation was run.
