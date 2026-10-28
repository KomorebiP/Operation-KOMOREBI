# Machine Societies: safety, amendment, and computability review

**27 October 2026 · Komorebi P. · AI-assisted sequential self-review · Batch 4**

Six additional statement/proof pairs were checked against [commit 3cc5bd4d7282](https://github.com/KomorebiP/Operation-KOMOREBI/commit/3cc5bd4d728265f489a1e5fdc2ad68ec6c78eb93). **Five are proved as written. The computability theorem is correct only after an explicit restriction on its program class.** Its proof assumes that an arbitrary simulation can trigger the actual forbidden event on halting. The stated simulation premise alone does not ensure that. A counterclass below demonstrates the difference.

Combined coverage is **38 of 62 distinct pairs: 36 recorded passes, two qualified statements, and 24 unreviewed**. The two qualifications are the earlier positive finite-index condition for `prop:memory` and the substantive program-class restriction for `thm:undecidable`. Neither is counted as a pass of the current written statement. The earlier [batch 3 report](MACHINE_SOCIETIES_PROOF_REVIEW_BATCH3_2026-10-27.md) links the previous reviews. Their recorded scope and provenance remain unchanged.

The [review record](../manifests/machine-societies-review-batch4-2026-10-27.json) contains the exact statement/proof blocks, hashes, claim cards, and literature records. The [coverage index](../manifests/machine-societies-review-index.json) binds the counts to the source. The manuscript SHA-256 is `600a8100804c4c91d7cf79a4985e9312eacc19195395aee01debb240cb0a6be0`. Surrounding definitions and downstream references were also inspected. Original source files, the PDF, and earlier reviews are preserved. The two source-edition corrections remain explicit finalization work.

## Claim reviews

<a id="constitutional-inductive-safety--propsafety"></a>

### Constitutional inductive safety: `prop:safety`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 1117.

**Claim.** If the initial full operating state satisfies a predicate and every admitted edge preserves it from a satisfying state, every state reachable by finitely many admitted edges satisfies that predicate.

**Hypotheses.** The state includes the operating and institutional variables. The relation includes both ordinary actions and amendments. Closure is required for every admitted edge with a safe source, including edges that change the checker.

**Argument.** The zero-edge path is the initial premise. For a path of length n+1, the induction hypothesis gives the predicate at its penultimate state, and the final admitted edge gives it at the endpoint. Every finitely reachable state has such a path.

**Dependencies.** Initial predicate + universal edge closure → induction on finite path length → reachable-state predicate. Leaves are internal premises and finite induction. There is no external theorem or computation dependency.

**Boundary checks.** Zero steps, deadlocked safe states, loops, nondeterministic choices, and unreachable unsafe states. A safe deadlock satisfies this proposition without providing service. The nearby unchecked-checker example violates edge closure on the second edge. It is not a counterexample to the proposition.

**Strongest safe statement.** The predicate is invariant relative to the declared transition relation. Actual implementation adherence, ethical adequacy, liveness, and timely service are additional obligations.

**Remaining gap.** None in this implication under the declared hypotheses.

**Next check.** For an implementation, include all checker-changing transitions in the relation and establish the closure premise for each admitted transition family.

<a id="finite-horizon-almost-sure-viability--propviability"></a>

### Finite-horizon almost-sure viability: `prop:viability`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 1145.

**Claim.** For each nonnegative finite horizon h, membership in the recursively defined set V_h is equivalent to the existence of an admissible policy that executes h transitions and stays in the safe set almost surely, including the present state. A deterministic time-dependent Markov policy suffices on the viable states.

**Hypotheses.** Finite full state space, finite safe subset and action sets, a Markov transition law for each available state/action, and policies allowed to observe the full state and remaining horizon. The horizon counts actual transitions. A deadlocked run is not treated as an h-transition policy.

**Argument.** At horizon zero the condition is exactly membership in S. A successful first action must put all positive-probability successors in V_h: at each such successor the conditional continuation is an admissible successful h-step policy. Conversely, an action with support in V_h followed by the inductively chosen actions preserves safety. Select one witness action for each viable state and remaining horizon. Randomization cannot rescue a first action with positive probability of reaching a nonviable successor.

**Dependencies.** Full Markov state + support criterion → backward induction. Finite action selection → deterministic time-dependent Markov witnesses. Randomized-policy necessity uses conditional continuations on positive-probability branches. All leaves are internal finite-probability facts and premises.

**Boundary checks.** h=0 needs no available action. An empty action set excludes a state from V_1 even when it is safe. An empty safe set makes all V_h empty. Zero-probability successors are irrelevant. A positive but small chance of leaving V_h still prevents an almost-sure guarantee. Partial observation and an unbounded horizon are outside this statement.

**Strongest safe statement.** The recurrence exactly solves the stated finite-horizon full-information safety problem. It does not prove decentralized implementability, eventual service, or infinite-horizon viability.

**Remaining gap.** None in this implication under the declared hypotheses.

**Next check.** Before applying the recurrence, verify the full-state Markov representation, action availability, and whether the intended policy observes that state.

<a id="order-independent-amendment-normal-forms--thmconfluence"></a>

### Order-independent amendment normal forms: `thm:confluence`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 1173.

**Claim.** A terminating locally confluent amendment relation is confluent. Each starting state has one reachable normal form, and every maximal amendment sequence ends there.

**Hypotheses.** Termination excludes every infinite chain of actual steps within the declared episode. Local confluence joins every pair of one-step successors by finite paths. The full state includes pending proposals, versions, permissions, and consequence records. Well-founded induction uses the ordinary classical set-theoretic convention.

**Argument.** For descendants y,z of s, the case y=s or z=s is immediate. Otherwise local confluence joins their first successors a,b at c. Induction at a joins y,c at p. Induction at b joins z,c at q. Termination makes a,b,c strict descendants of s, so induction at c joins p,q. Concatenation joins y,z. A maximal path cannot be infinite or end with an available edge, so it ends at a normal form. Two reachable normal forms joined by confluence must coincide.

**Dependencies.** Termination → well-founded strict-descendant induction. Local joining + three induction uses → confluence. Termination + maximality → normal-form existence. Confluence + terminality → uniqueness. Newman Theorem 3 supplies the same confluence implication after translating his path terminology. The manuscript also supplies its own proof.

**Boundary checks.** A starting normal form permits the empty path. The local join may equal a or b but cannot equal s, since that would make a cycle. Local joinability does not require one-step commutation. A finite rulebook alone does not imply termination. Equal projected policy text does not establish confluence of the full consequence state.

**Strongest safe statement.** Order independence holds for the specified terminating episode and state representation. It gives neither equal path costs nor termination of all future institutional change.

**Remaining gap.** None in this implication under the declared hypotheses.

**Next check.** For a concrete amendment system, prove a ranking or another termination argument and discharge every local fork in the full declared state.

<a id="quiescent-convergence-and-invariant-preservation--propmerge-convergence"></a>

### Quiescent convergence and invariant preservation: `prop:merge-convergence`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 1207.

**Claim.** With finitely many replicas and finitely many fixed contributions, eventual inclusion of every contribution in every replica makes all states eventually equal the join of the initial state and those contributions. A set containing the initial state and preserved by local updates and binary joins remains invariant.

**Hypotheses.** A join-semilattice, a common initial element, updates by joining a fixed contribution, merges by joining replica states, finite replicas/contributions, and eventual dissemination to every replica. For invariant preservation, all permitted local updates preserve V and V is join-closed.

**Argument.** Inductively each replica holds the initial element joined with some created contributions. Associativity, commutativity, and idempotence remove order and multiplicity. Once all contributions are included, that join is the same fixed element and cannot change. The maximum of finitely many eventual inclusion points gives a common finite point for all replicas. A separate induction over updates and merges proves membership in V.

**Dependencies.** Join laws + update/merge definitions → representation by a subset of contributions → common final join after dissemination. Finiteness → one common eventual point. Initial membership + local-update preservation + join closure → invariant induction. No external CRDT theorem is needed for this restricted proof.

**Boundary checks.** No contributions gives the initial state. One replica works without communication. Repeated deliveries do not change a join. No bottom element or finite semilattice is required. The result conditions on the same accepted contributions: a different schedule can generate different contributions when generation depends on local state.

**Strongest safe statement.** The stated algebra ensures quiescent convergence and the specified invariant. It does not certify authorization, detect completed dissemination, or undo the physical effects of conflicting irrevocable grants.

**Remaining gap.** None in this implication under the declared hypotheses.

**Next check.** Verify that actual update and merge operations have the declared join form and that the intended validity predicate is closed under every independently reachable merge.

<a id="exclusive-service-cannot-be-unconditionally-local--propexclusive-service"></a>

### Exclusive service cannot be unconditionally local: `prop:exclusive-service`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 1233.

**Claim.** Two isolated decision sites cannot both guarantee irrevocable singleton-request service before a deadline and at most one grant for simultaneous requests. The impossibility also holds for probability-one guarantees with request-independent random tapes.

**Hypotheses.** Each site observes its own requests and receives no information about the other site’s requests before the common deadline. There is no separate shared atomic resource operation before that deadline. Compare executions with the same initial resource state and matching local request timing. Random tapes have the same joint request-independent law in the compared executions.

**Argument.** In the concurrent execution, each site has the same local history as in its own singleton execution. The singleton requirement therefore forces both deterministic grants. With randomization, each local grant event still has probability one by equality of its local law. The union of the two complementary null events has probability zero, so both grants occur almost surely. Independence of the two random tapes is unnecessary.

**Dependencies.** Information restriction + matched local inputs → indistinguishable local histories/laws → singleton service forces two grants → contradiction. For randomized protocols the only probability step is closure of null events under a finite union. No general consensus impossibility result is used.

**Boundary checks.** Shared correlated randomness does not avoid the probability-one contradiction. The proposition does not quantify an approximate service probability. A preassigned owner drops singleton service at the nonowner. An atomic grant primitive changes the premises. Tentative reservations are not the required irrevocable grants.

**Strongest safe statement.** The incompatible guarantees are those of this particular deadline and information contract. This is not an impossibility theorem for every distributed allocation protocol.

**Remaining gap.** None in this implication under the declared hypotheses.

**Next check.** Specify the actual communication, atomic resource, preallocation, or deadline assumption that makes the intended service contract feasible.

<a id="no-universal-constitutional-safety-decider--thmundecidable"></a>

### No universal constitutional safety decider: `thm:undecidable`

**Primary verdict: correct only after a stated restriction.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 1261.

**Claim.** The manuscript asserts that any class with effective initial encodings, deterministic total computable steps, a forbidden event, and effective step-by-step Turing simulation has undecidable safety and non-semidecidable safety, while event occurrence is semidecidable.

**Hypotheses.** The stated simulation premise does not explicitly require the class to admit a simulator that emits the actual forbidden event when its simulated machine halts. Event occurrence must also be effectively recognizable from a simulated finite step, as the execution-based semidecision argument presumes.

**Argument.** The first reduction requires an effective map from every machine/input pair to an admissible program whose actual forbidden event occurs if and only if that machine halts. Universal simulation of internal configurations alone does not supply this map. A class containing silent universal simulators and a separately tagged immediate-event program meets the literal simulation premise while its safety is decidable by the tag. Under the explicit event-emitting compilation restriction, the manuscript’s existing reduction and dovetailing argument are valid.

**Dependencies.** Missing class-closure arrow: machine/input → admissible event-emitting simulator. With that arrow, halting undecidability → no total safety decider. Recognizable event + total effective steps → semidecision of occurrence. A hypothetical safety semidecision + occurrence semidecision → total decision by dovetailing → contradiction. The classical undecidability leaf is checked against Turing’s symbol-printing result with an explicit standard encoding translation.

**Boundary checks.** A never-emitting universal simulator already gives an all-safe counterclass. Adding one immediate-event program makes both safety and unsafety nonempty and still decidable, so merely requiring a nontrivial event does not repair the premise. Finite state spaces, finite step bounds, and restricted program languages are outside the strengthened universal impossibility claim.

**Strongest safe statement.** For an effectively presented program class with uniformly computable total steps, decidable event recognition, and an effective admissible compilation that emits the forbidden event exactly when any input Turing computation halts, event occurrence is semidecidable, safety is undecidable, and safety is not semidecidable.

**Remaining gap.** Universal simulation does not imply closure under the event-emitting instrumentation used by the reduction. The literal broad class claim is false. The explicitly restricted version follows by the existing proof.

**Next check.** State the event-emitting compilation and event-recognition premises in a revised source edition, and apply the same restriction to the complete-certificate consequence at source line 1275.

## The computability restriction and its downstream effect

The formal setup at source line 1259 permits the following effective program class. A tag-0 program carries an arbitrary Turing machine and input. It updates the encoded simulated configuration by one step, keeps a separate actual event bit at zero, and stutters after the simulated machine halts. A tag-1 program emits the actual forbidden event on its first step and then stutters. Invalid machine descriptions can be assigned a fixed harmless stuttering interpretation, so encodings and transitions remain total and effective.

This class simulates every Turing computation step by step. Both safe and unsafe programs exist, yet safety is decided by reading the tag. The simulated tape may contain any symbol. It is internal data, not the actual forbidden-event channel. This distinction is precisely what a simulation must connect to the event for the reduction to work. The smaller class containing only tag-0 programs already refutes the unrestricted class inference. Adding tag 1 shows that merely requiring a nontrivial event is insufficient.

The smallest missing implication is the existence of an **effective admissible compilation** from each machine/input pair $(M,w)$ to a program $P_{M,w}$ in the chosen class such that

$$
P_{M,w}\text{ produces the actual forbidden event}
\quad\Longleftrightarrow\quad M(w)\text{ halts}.
$$

Restricting the theorem to classes with that compilation, uniformly effective total steps, and decidable event recognition makes the existing proof work. A safety decider would decide halting by complementing its answer. Event occurrence has a finite observable witness. If safety were also semidecidable, interleaving the two procedures would decide every input. This is the manuscript's reduction with its required domain stated explicitly, not a new proof route. Ordinary unrestricted programming models with an accessible event operation can meet this premise. Effective simulation by itself does not state it.

**Downstream consequence.** At source line 1275, the impossibility of a sound and complete recursively enumerable safety-certificate system depends on the same restricted program class. Enumerating certificates and checking them would semidecide safety. In the counterclass, however, a checker that accepts one fixed certificate exactly for tag-0 codes is sound, complete, and decidable. The revised source must therefore carry the stronger premise into this paragraph. The finite-state safety and viability results reviewed above do not depend on the computability theorem and retain their verdicts.

## External source checks

These are bounded checks of the named implications, not a bibliography or novelty audit. Stable-identifier cache lookups found no project cache. No full paper is included in the publication payload. Source records and acquisition/extraction details are preserved in the review JSON.

**Newman (verified application).** M. H. A. Newman, *On Theories with a Combinatorial Definition of “Equivalence”*, *Annals of Mathematics* 43(2), 223–243 (1942), [DOI 10.2307/1968867](https://doi.org/10.2307/1968867). The [publisher issue record](https://www.jstor.org/stable/i307210) matches the [scanned paper](https://www.ens-lyon.fr/LIP/REWRITING/TERMINATION/NEWMAN/Newman.pdf). Theorem 3 on page 226 uses the definitions and conditions on page 224. Its proof continues on pages 227–228. Positive cells correspond to admitted amendment steps, descending paths to reductions, and lower bounds to common descendants. Condition (D) is local confluence. With no infinite descending path, the theorem yields condition (A), joinability of connected vertices. This gives the required confluence implication. The manuscript separately derives existence and uniqueness of normal forms. The scan was inspected visually on pages 223–228 because text extraction returned no text. Its SHA-256 is `1a5243d6e42cc3c240c77b7fc81f441263786bd93abf3e6fd344b819fe89def3`. Overlap: known after translation of notation. Checked 27 October 2026.

**Turing (classical leaf verified, project application requires the restriction).** A. M. Turing, *On Computable Numbers, with an Application to the Entscheidungsproblem*, *Proceedings of the London Mathematical Society* s2-42(1), 230–265 (1937), [DOI 10.1112/plms/s2-42.1.230](https://doi.org/10.1112/plms/s2-42.1.230). The [facsimile](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf) records receipt and reading in 1936. Section 8, page 248, proves undecidability of whether an arbitrary machine ever prints a designated symbol. A machine that watches a simulation and halts upon that symbol translates a hypothetical halting decider into the forbidden symbol-printing decider. This establishes the classical leaf used here. Turing's circle-free property is not ordinary halting. That terminology is not substituted silently. Applying the leaf to the project's program class still needs the event-emitting compiler above. Overlap: a formal corollary under the explicit restriction, not a new AI-specific limit. The relevant PDF text and pagination were inspected. No retained project-cache hash is claimed. Checked 27 October 2026.

Other references near these claims, including consensus, proof-carrying code, CRDTs, invariant confluence, and CALM, provide surrounding context. The five passing proof implications do not require those external results. Their broader contextual claims were not audited in this batch.

## Obligation matrix and finalization

| Obligation | Five passing claims | Computability theorem |
|---|---|---|
| Types, domains, and hypotheses | Passed under the declared contracts | Failed as a sufficient class specification: event-emitting compilation is missing |
| Written implication | Passed | Conditional on the explicit restriction |
| Boundary checks | Passed, including zero horizon, empty actions, quiescence, and correlated randomness | Literal broad-class inference fails. Counterclass supplied |
| External theorem | Newman application verified. Other four need no external theorem | Classical undecidability leaf verified. Application needs the missing bridge |
| Dependency direction | No cycle identified | Certificate consequence inherits the same restriction |
| New Lean or executed mathematical computation | None | None |
| Implementation, empirical, or independent review | Out of scope | Out of scope |

The final proofreading pass covers this report and the changed status/navigation sentences. It checks prose, notation, source locators, and links. It makes no mathematical-token edits to the original manuscript. Source-binding and navigation checks validate the report's identity and publication consistency, not the mathematical verdicts.

Remaining work is to review the other **24 pairs**, integrate the **two explicit restrictions** into a revised source edition with its downstream prose, and keep implementation/empirical and independent review separate. A useful next bounded batch is decentralized observation, monitoring, and institutional accounting, with each cited theorem checked at the exact point of use. The 13 recently imported collections retain their separate unassessed status and F16 gate. Coverage is an inventory of scoped review, not a correctness percentage or whole-book certification.
