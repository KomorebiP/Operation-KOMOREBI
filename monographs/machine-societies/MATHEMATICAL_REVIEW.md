# Final mathematical self-review

The 15 explicitly listed central results and supporting dependencies, under their written finite-model hypotheses. This is a targeted self-review, not a complete new proof audit of all 62 results.

**Primary verdict:** proved as written for the 15 claims below, under their stated hypotheses. This is a recorded self-review. It is not independent peer review or formal verification.

## Coverage and dependencies

| Result | Claim | Dependencies | Verdict |
|---|---|---|---|
| 18.1 | The exact bounded-sanction discrimination limit | Direct argument | Proved as written |
| 18.2 | Garbling does not increase sanctioning capacity | prop:deterrence-tv | Proved as written |
| 19.1 | Simultaneous enforcement and mixture obstruction | prop:deterrence-tv, external:finite-lp-duality | Proved as written |
| 19.3 | A robust simultaneous enforcement certificate | prop:deterrence-tv | Proved as written |
| 41.1 | Authorized staffing after any bounded agent erasure | Direct argument | Proved as written |
| 42.1 | Joint continuation under a common observation history | Direct argument | Proved as written |
| 42.2 | Safe service with a finite progress rank | thm:joint-viability | Proved as written |
| 42.4 | Soundness of a finite continuation certificate | thm:joint-viability | Proved as written |
| 42.6 | Governance abstraction preserves joint realizability | thm:joint-viability, prop:joint-progress | Proved as written |
| 43.2 | Inspection without commitment | Direct argument | Proved as written |
| 43.3 | Sharp pairwise privacy envelope for a bounded sanction | prop:deterrence-tv | Proved as written |
| 43.5 | Conditional disclosure accounting | Direct argument | Proved as written |
| 43.6 | Capacity for a finite appeal contract | thm:robust-staffing | Proved as written |
| 43.7 | Continued operation with an available authorized ending | thm:joint-viability, prop:joint-progress | Proved as written |
| 43.8 | Guarded certificate use and authorized handover | Direct argument | Proved as written |

The directed dependencies are acyclic. The finite-LP input is checked against the authors’ primary lecture material in LITERATURE_REVIEW.md. The Hall implication used for appeals has a complete alternating-path proof in Theorem 41.1. The knowledge-state and privacy source comparisons are attribution and hypothesis checks in addition to the manuscript’s direct proofs.

## Claim cards and obligations

### 18.1. The exact bounded-sanction discrimination limit

Locator: `prop:deterrence-tv` in `publication/Machine_Societies_v1.0.0.tex`. Exact statement-and-proof SHA-256: `0fe59b7daa26e7b8a2e5d55d562485fd92fdf4b947f056d2f011ff88990a0b0d`.

**Contract.** Finite probability laws on the same observation alphabet, one specified utility gain, positive collectible penalty, and all sanctions in [0,1].

**Argument checked.** The signed probability difference has total mass zero. Its positive mass equals half its l1 norm. Coordinatewise maximization attains that mass, which gives both the weak and strict incentive thresholds.

**Boundary checks.** Identical laws, disjoint supports, zero discrimination, and equality of gain and the maximum penalty gap. Strict preference is not inferred at equality.

**Verdict.** Proved as written. Typing, quantifiers, implication direction, relevant boundary cases, and dependency circularity passed this self-review. Physical implementation and truth of external modeling premises are outside this verdict. No missing implication was identified.

### 18.2. Garbling does not increase sanctioning capacity

Locator: `prop:enforcement-garbling` in `publication/Machine_Societies_v1.0.0.tex`. Exact statement-and-proof SHA-256: `630230b299dd27e07d5272d06782cb81b2003bc23919dfbfe80603d21edfbe09`.

**Contract.** One common stochastic channel acts on both laws; the false-positive cap uses the compliance law.

**Argument checked.** Pull back every coarse sanction by conditional expectation through the same channel. Its range, objective and compliance expectation are unchanged. Inclusion of the pulled-back feasible policies proves the inequality.

**Boundary checks.** Identity and constant channels; cap zero and one; a case-dependent channel would violate the premise.

**Verdict.** Proved as written. Typing, quantifiers, implication direction, relevant boundary cases, and dependency circularity passed this self-review. Physical implementation and truth of external modeling premises are outside this verdict. No missing implication was identified.

### 19.1. Simultaneous enforcement and mixture obstruction

Locator: `thm:joint-enforcement` in `publication/Machine_Societies_v1.0.0.tex`. Exact statement-and-proof SHA-256: `45ae081e7ac43249e92e678e606195af8c33db0477dbdfd910af57e0c7b6204c`.

**Contract.** Nonempty finite observations and deviations, fixed common laws and gains, positive penalty, and one monitor in the compact polytope at cap alpha in [0,1].

**Argument checked.** List monitor-polytope vertices v_i and form M_ij=F(P_j-P_C).v_i-g_j. The primal matrix game maximizes t subject to M^T p >= t*1 and p in a simplex. Its LP dual minimizes z subject to M lambda <= z*1 and lambda in the deviation simplex. Finite feasible bounded LP duality proves equality. The average vertex monitor realizes p. Compactness gives both extrema.

**Boundary checks.** Cap zero can make the polytope lower dimensional, but LP duality for affine constraints still applies. One deviation, zero gains, mixture equal to compliance, and cap one are covered.

**Verdict.** Proved as written. Typing, quantifiers, implication direction, relevant boundary cases, and dependency circularity passed this self-review. Physical implementation and truth of external modeling premises are outside this verdict. No missing implication was identified.

### 19.3. A robust simultaneous enforcement certificate

Locator: `prop:joint-robust` in `publication/Machine_Societies_v1.0.0.tex`. Exact statement-and-proof SHA-256: `4d44bdb4788b18e75e5cc7736ffa28ae02849f5f055a401e66627bc293512ff4`.

**Contract.** One monitor, stated total-variation errors for every complete observation law, alpha at least epsilon_C, and nonnegative target margin eta.

**Argument checked.** A [0,1]-valued function changes in expectation by at most total variation. One application controls false positives; two applications bound each margin error by F(epsilon_j+epsilon_C). The monitor never changes with j.

**Boundary checks.** Zero errors, the tightened-cap boundary, and correlated errors. The result is sufficient and need not be necessary.

**Verdict.** Proved as written. Typing, quantifiers, implication direction, relevant boundary cases, and dependency circularity passed this self-review. Physical implementation and truth of external modeling premises are outside this verdict. No missing implication was identified.

### 41.1. Authorized staffing after any bounded agent erasure

Locator: `thm:robust-staffing` in `publication/Machine_Societies_v1.0.0.tex`. Exact statement-and-proof SHA-256: `092d9fc3f9b1669857e7afbb084c2c97388b19b7c963a7b6792fb2235822370f`.

**Contract.** Finite nonempty roles, finite unit-capacity agents, 0<=k<=|A|, fixed capability/authorization edges, and rematching after the erased set is known.

**Argument checked.** A deficient role set loses enough neighboring agents to violate injectivity. Conversely, every surviving neighborhood satisfies Hall. The included maximum-matching alternating-path argument proves the required Hall implication directly.

**Boundary checks.** k=0, k=|A|, no neighbors, and two roles sharing the same two backups. No timing or decentralized reassignment claim is inferred.

**Verdict.** Proved as written. Typing, quantifiers, implication direction, relevant boundary cases, and dependency circularity passed this self-review. Physical implementation and truth of external modeling premises are outside this verdict. No missing implication was identified.

### 42.1. Joint continuation under a common observation history

Locator: `thm:joint-viability` in `publication/Machine_Societies_v1.0.0.tex`. Exact statement-and-proof SHA-256: `f011dd47e68569554ad6470fc6c14385381293821858c500037f0a10351cf74a`.

**Contract.** Finite states and protocol catalogue, nonempty full successor sets, one observation map, a nonempty initial observation fibre subset, and statewise admissibility intersected over all possibilities.

**Argument checked.** Induction proves that the posterior possibility set is exact and W_k is precisely k-step safe feasibility, including time zero. The decreasing finite sequence stabilizes. Selecting a witnessing profile at each fixed-point element gives one stationary knowledge-state strategy. An indefinitely successful history strategy belongs to every finite layer.

**Boundary checks.** Empty admissible intersections, unsafe initial sets, hidden states requiring different actions, and retained rare failure paths. Randomization and inaccessible private history are not silently added.

**Verdict.** Proved as written. Typing, quantifiers, implication direction, relevant boundary cases, and dependency circularity passed this self-review. Physical implementation and truth of external modeling premises are outside this verdict. No missing implication was identified.

### 42.2. Safe service with a finite progress rank

Locator: `prop:joint-progress` in `publication/Machine_Societies_v1.0.0.tex`. Exact statement-and-proof SHA-256: `6d413c135befcb19df718ebaee5292c4b6bb1fc5fb72631476c589bd35d61d5f`.

**Contract.** The same finite sure contract, target G inside the safe set, certified completion B subset G, and safety continued after the first completion.

**Argument checked.** Bounded reachability is an induction on attractor layers within W_*. For an eventually successful deterministic history strategy, the tree stopped at certified completion is finitely branching. Unbounded depths would supply an infinite unfinished public branch. A second finite-branching argument supplies a consistent complete-state realization, contradicting sure success. Hence a finite bound exists.

**Boundary checks.** Already completed states, empty targets, safe idle loops, and almost-sure but not sure completion. A safety suffix need not stay in the service attractor after completion.

**Verdict.** Proved as written. Typing, quantifiers, implication direction, relevant boundary cases, and dependency circularity passed this self-review. Physical implementation and truth of external modeling premises are outside this verdict. No missing implication was identified.

### 42.4. Soundness of a finite continuation certificate

Locator: `prop:continuation-certificate` in `publication/Machine_Societies_v1.0.0.tex`. Exact statement-and-proof SHA-256: `ee7331f939a3481b266591185b14dcd3a8c01ec3616e3bf063f3a460b3f608ba`.

**Contract.** A finite family contains the initial possibility set, all its states are safe, selected profiles are admissible, and every successor remains in the family. Optional ranks are nonnegative integers on that whole domain.

**Argument checked.** Closure proves invariant safety by induction. A strictly decreasing nonnegative rank reaches zero within its initial value; zero rank implies certified completion. Equality of the proposed family with the maximal kernel is unnecessary.

**Boundary checks.** Missing successors, inadmissible actions, omitted initial states, false zero-rank goals, and nondecreasing ranks are rejected by the finite checker.

**Verdict.** Proved as written. Typing, quantifiers, implication direction, relevant boundary cases, and dependency circularity passed this self-review. Physical implementation and truth of external modeling premises are outside this verdict. No missing implication was identified.

### 42.6. Governance abstraction preserves joint realizability

Locator: `thm:synthesis-transport` in `publication/Machine_Societies_v1.0.0.tex`. Exact statement-and-proof SHA-256: `4247156fcc5e7273631110fae0f543efe304eeddb4bae686ed88ecf241bfdb33`.

**Contract.** A surjection preserves observations, enabled profiles, safety and target labels in both directions, and the exact image of every admissible successor set.

**Argument checked.** Image commutes with unions and, using observation equality, with the relevant observation-fibre intersection. Therefore Post commutes and successor-set nonemptiness is reflected. Induction transports every W_k and R_k, so stabilized membership and entry ranks agree. The pulled-back profile remains admissible for every concrete possibility.

**Boundary checks.** Beliefs need not be saturated fibres. Many concrete beliefs may share one reduced image. Dropping any of observation, action, goal, safety, or successor preservation can change the answer.

**Verdict.** Proved as written. Typing, quantifiers, implication direction, relevant boundary cases, and dependency circularity passed this self-review. Physical implementation and truth of external modeling premises are outside this verdict. No missing implication was identified.

### 43.2. Inspection without commitment

Locator: `prop:strategic-inspector` in `publication/Machine_Societies_v1.0.0.tex`. Exact statement-and-proof SHA-256: `5dac607b42204fd3f619987bd85e101b0d1946662928ee6c2ed6b881b6b8a39a`.

**Contract.** The specified simultaneous 2x2 risk-neutral game, 0<g<F and 0<c<b, independently mixed strategies, no commitment, side payments, or false accusations.

**Argument checked.** The four pure profiles each admit a strict profitable deviation. A pure strategy by either player forces a strict pure response and cannot yield equilibrium. Both mix, so indifference forces q=g/F and p=c/b, strictly inside (0,1). These make both supported actions best responses.

**Boundary checks.** Equality boundaries are excluded. A verified fee w>c changes the game and gives certain inspection; w=c loses strictness.

**Verdict.** Proved as written. Typing, quantifiers, implication direction, relevant boundary cases, and dependency circularity passed this self-review. Physical implementation and truth of external modeling premises are outside this verdict. No missing implication was identified.

### 43.3. Sharp pairwise privacy envelope for a bounded sanction

Locator: `thm:privacy-envelope` in `publication/Machine_Societies_v1.0.0.tex`. Exact statement-and-proof SHA-256: `8fd1e9109bd0750f69eb525766ee0cd79444e590f77b219e3a0276a839a3bc49`.

**Contract.** Finite laws for the complete sanctioning record, bidirectional likelihood-ratio factor lambda>=1, and one sanction at false-positive cap alpha in [0,1].

**Argument checked.** Set a=E_C s and b=E_D s. The record and its complement imply b-a <= min((lambda-1)a,(lambda-1)(1-a)/lambda). The crossing is a=1/(lambda+1). Maximizing over a<=alpha gives the envelope. The displayed two-outcome laws and randomized sanction attain it for every permitted parameter.

**Boundary checks.** lambda=1, alpha=0, alpha=1, zero-probability outcomes, and the crossing cap. The envelope is necessary for any fixed pair, with sharpness over pairs, not sufficiency for every pair.

**Verdict.** Proved as written. Typing, quantifiers, implication direction, relevant boundary cases, and dependency circularity passed this self-review. Physical implementation and truth of external modeling premises are outside this verdict. No missing implication was identified.

### 43.5. Conditional disclosure accounting

Locator: `prop:privacy-transcript` in `publication/Machine_Societies_v1.0.0.tex`. Exact statement-and-proof SHA-256: `70bd13e2bd3863b6fd2da91d2797cae862fc351e57376cb2d5c2f87a6c88a30d`.

**Contract.** A fixed finite number of finite-alphabet releases, uniform bidirectional conditional bounds at every possible common prefix, and the same stochastic postprocessing under both cases.

**Argument checked.** The empty prefix is shared. Finite factors give equal support for the next release, inductively for all prefixes. On positive-probability transcripts the ratio factors into the conditional ratios; their product yields the bound. Common zero-probability transcripts and common postprocessing are handled by nonnegative summation.

**Boundary checks.** Identical marginals alone do not satisfy the conditional premise. Unbounded or data-selected stopping and unmodeled side information are outside this statement.

**Verdict.** Proved as written. Typing, quantifiers, implication direction, relevant boundary cases, and dependency circularity passed this self-review. Physical implementation and truth of external modeling premises are outside this verdict. No missing implication was identified.

### 43.6. Capacity for a finite appeal contract

Locator: `prop:appeal-capacity` in `publication/Machine_Societies_v1.0.0.tex`. Exact statement-and-proof SHA-256: `810585cf471f2ded47e3ee326287c37b4e7b1926179b9de4ea7e3cc3a5c36a5b`.

**Contract.** Finitely many admitted unit-slot appeals, finite integer epoch windows, nonnegative integer slot capacities, and ready evidence plus qualified authorized reviewers throughout the windows.

**Argument checked.** Expand capacity into distinct slot vertices and apply the already proved matching argument. For any appeal subset, its union of interval windows decomposes into disjoint maximal integer intervals. Each selected window lies wholly in one component. The interval inequalities bound selected demand componentwise, giving Hall for every subset.

**Boundary checks.** Empty workload, zero capacity, singleton windows, touching or disjoint windows, and sufficient total capacity with a missed deadline. Arbitrary noninterval eligibility sets require the full Hall test.

**Verdict.** Proved as written. Typing, quantifiers, implication direction, relevant boundary cases, and dependency circularity passed this self-review. Physical implementation and truth of external modeling premises are outside this verdict. No missing implication was identified.

### 43.7. Continued operation with an available authorized ending

Locator: `thm:stoppable-operation` in `publication/Machine_Societies_v1.0.0.tex`. Exact statement-and-proof SHA-256: `f8a2d86d064cb60855b7c38e699ebd27b1030ab99f657f8c1601d4d9250cf5a4`.

**Contract.** The finite common-observation contract with specified running and ending actions, an ending target inside safety with a safe hold, and authenticated stop commands visible before profile selection.

**Argument checked.** The ending attractor is exactly sure safe ending reachability by the finite-rank and stopped-tree arguments. The greatest running invariant inside that attractor gives one policy that preserves the option to stop. Conversely, a command can arrive at every reachable pre-command history, so every such belief must be in the ending attractor and hence in every running-kernel approximation.

**Boundary checks.** Immediate commands, no command, empty ending targets, safe but settlement-locked states, and finite maximum rank over a nonempty finite running kernel. Delivery delay belongs in the model.

**Verdict.** Proved as written. Typing, quantifiers, implication direction, relevant boundary cases, and dependency circularity passed this self-review. Physical implementation and truth of external modeling premises are outside this verdict. No missing implication was identified.

### 43.8. Guarded certificate use and authorized handover

Locator: `thm:guarded-certificates` in `publication/Machine_Societies_v1.0.0.tex`. Exact statement-and-proof SHA-256: `552079950e579a42a620cf649ee309633e65c3fc9c895c11011dd8cdb6f25590`.

**Contract.** Certified local domains inside a common protected set, a selector with a justified action at every reachable decision epoch, sound guards over whole action intervals, authorized handovers preserving every intermediate state, and a certified target hold.

**Argument checked.** A sound local guard includes every actual successor in the certified successor set. A valid handover preserves the common invariant and establishes the next mode domain. Induction gives safety. One shared nonnegative integer rank decreasing at every selected primitive step before the target gives the claimed completion bound.

**Boundary checks.** Stale guards, unavailable justified actions, intermediate handover states, checking/waiting costs, and switches that reset local ranks. No claim is made that a universal guard can establish its own assumptions.

**Verdict.** Proved as written. Typing, quantifiers, implication direction, relevant boundary cases, and dependency circularity passed this self-review. Physical implementation and truth of external modeling premises are outside this verdict. No missing implication was identified.

## Release finding

every coherent concrete support was too broad in the quotient test description. The active description now records the actual two-family range. The original source release and its historical records remain unchanged.

## Evidence boundary

No mathematical statement, proof body, or mathematical token was changed. Forty-seven retained theorem/proposition proofs were not newly audited in this targeted pass. All 62 are indexed and checked for preservation. Bounded program checks and PDF production checks have separate records. Open research questions in the manuscript remain open.
