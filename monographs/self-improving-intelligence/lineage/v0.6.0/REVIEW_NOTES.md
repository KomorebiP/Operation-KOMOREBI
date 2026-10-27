# Review and validation notes
## Self-Improving Intelligence: Representation, Discovery, and Recursive Revision
**Komorebi P. · Operation Komorebi · v0.6.0 · 8 October 2026**

## Scope and status

This 55-page, seven-part theoretical edition develops the acquisition procedure that synthesizes discovery rules. It follows the 47-page v0.3.0. The main additions are a learned, checked equation library, ordered candidate quotienting, preservation of the complete teacher transcript, repair-relative streaming bounds, and a composition statement that separates semantic preservation from resource improvement.

The five new statement/proof pairs were reviewed against their hypotheses, code paths, counterexamples, and bounded exact checks. The 23 preceding pairs were mechanically checked for verbatim preservation and their suites rerun. This is an internal mathematical and implementation review, not independent peer review, a full novelty audit, a proof-assistant result, or a demonstration of an unrestricted self-improving agent. No neural training or prior internal agent experiment is presented as evidence of the whole architecture.

## Final inventory

| Item | Outcome |
|---|---|
| Manuscript | 55 pages, seven parts, cover, contents, guide, appendices and references |
| Statements with prose proofs | 28: twelve theorems and sixteen propositions |
| New formal statements | Five relative to v0.3.0, not five priority claims |
| Other formal material | Two definitions and sixteen counterexamples |
| Figures and bibliography | Eleven analytical vector figures, eleven PNG previews, twenty-three references |
| Predecessor preservation | All 23 statement/proof pairs verbatim; nine core reference programs byte-identical |
| Exact suites | 62 groups and 318,167 assertions passed |
| New exact scope | 14 groups and 111,024 assertions |
| Source audit | No missing/duplicate references, missing/unused bibliography keys, missing figures or unpaired proofs |
| Final LaTeX | No warnings, unresolved references, missing-character diagnostics or overfull/underfull boxes |
| PDF preflight | All 55 pages rendered; no out-of-page words or unresolved/replacement text markers; used fonts embedded |
| Fresh source rebuild | PASS: identical extracted text on all 55 pages and matching scientific JSON after only declared timing/environment fields are omitted |

Counts describe document inventory and deterministic finite computations. They are not independent scientific replications, statistical samples, or universal proofs by enumeration.

## Mathematical and implementation review

### 1. Proposing an equation is not proving it

The learner generates 135 expression schemas and evaluates them on nine positive probe contexts. It proposes 1,068 equations with matching probe vectors. The limited proof procedure admits 336 and leaves 732 unproved. The replayer checks derivation steps separately from the proposer. A non-admitted equation may be false, true only on a narrower domain, or true but unavailable to this limited proof search.

The pure, total, exact integer semantics are explicit. The finite probe agreement of `max(x,1)=x` fails at zero. The natural-number identity `max(x,0)=x` is not silently accepted over all integers. The supplied primitive axioms and replayer are part of the prior structure, not discoveries of the learner. The checker is not a formal proof-assistant kernel.

### 2. The quotient preserves original proposals, not arbitrary optimization objectives

A normal form only needs to be sound. It need not be complete or confluent. Keeping the earliest original AST for each checked normal form preserves all teacher proposals when counterexamples are never forgotten, the candidate order is fixed, the teacher is deterministic and extensional, and the semantic contract is unchanged. The proof shows that every skipped later equivalent expression must fail an already retained counterexample.

Thus candidate submission ASTs, counterexamples, accepted AST, and finite grammar exhaustion agree. The same interpreter evaluates submitted ASTs. Setup, dispatch, and stored representatives remain extra costs. A teacher judging source syntax, forgotten examples, side effects, partial arithmetic, or changed operation semantics requires a different theorem. Cached representatives are bound to the grammar order and arithmetic semantics, with stale-cache negative controls.

### 3. The new acquired object and its measured effect

The learned equations reduce the grammar from 3,960 expressions to 1,362 representatives. Cold reacquisition of the old capacity rule visits 76 candidates instead of 190 and performs 1,376 interpreter-node visits instead of 1,898. The four teacher proposals, three counterexamples, 210 teacher comparisons, and final AST remain unchanged.

A frozen quotient is then applied to nine finite arithmetic targets and one genuinely out-of-grammar parity target. The full ten-target batch uses 85,162 interpreter-node visits instead of 196,384. These are exact controlled finite tasks in one language, not empirical generalization across unrelated domains. Both parity searches exhaust the grammar. Exhaustion of this grammar is not uncomputability of parity.

The stronger supplied full normalizer retains 1,352 representatives. The learned representation is not claimed superior to it. This control avoids presenting automatic acquisition from a smaller supplied substrate as a new best-in-class synthesis algorithm.

### 4. Avoided evaluations do not erase preparation costs

The development ledger includes 1,215 probe evaluations, 3,519 probe interpreter-node visits, 1,068 proposals, and 584 successful checked axiom steps. The compact library serialization is 69,518 bytes. Quotient construction records 19,440 normalization-node visits, 518,140 schema-match attempts, and 4,798 successful replacements.

These are distinct units, not a conversion to processor instructions or optimal information content. Failed proof attempts, bookkeeping, grammar generation, and serialization remain separate phases rather than disappearing from the account. A cost inequality specifies when reuse repays the additional setup. No unqualified CPU-time or end-to-end speedup is claimed. The equational proposer and proof procedure themselves have not learned to improve.

### 5. Repair-relative weights change the semantic scope

A checked nonnegative weight assignment puts total weight at most one on every repair's success set. Every successful leaf therefore covers at most unit weight, and a binary depth-h tree can cover at most 2^h total weight. With immutable experiments, unread rows can only increase a prefix weight. Streaming omission of already doomed root suffixes preserves the exact first returned tree of the corresponding full ordered depth-first search.

The result is not a Pareto-optimal storage theorem, a claim that weights are free, or a guarantee that the greedy constructor gives an optimal bound. Three overlapping two-case repairs give a simple fractional witness stronger than the implemented greedy witness. Zero weights are valid and prune nothing. An uncovered state can be assigned positive finite weight, but remains unrepairable for an independent reason.

The 32-hidden-case paired-repair example has sixteen required repair classes. Full and streaming search reads are 4,416 and 2,864, respectively. The common scope check adds 1,152 reads and the witness check adds 256. Both return the same literal tree with five online units and 31 records. Added weight arithmetic and comparisons are retained separately. Adding a universal repair invalidates the stale weight certificate; rebuilt weights permit a correct one-step, one-record result.

### 6. One composed change does not prove indefinite recursion

The compositional statement keeps three stages explicit: acquire checked equations, use their quotient to synthesize the identical task rule, then apply the separately justified compiler change. The semantic result is exact under the common hypotheses. Positive total savings require a separate common cost model. A supplied semantic proof is not evidence that the learner invented its own theory, and a terminated resource allowance is not grammar exhaustion.

## Exact finite domains

The new suite checks all accepted equation certificates on the declared signed-integer grid, every grammar AST on signed corner contexts, proof/typing/scope mutations, normalization and earliest representatives, deterministic teacher-trace equality for the ten targets and original rule, stale grammar and arithmetic caches, nondecreasing-cost controls, all declared small binary experiment tables and nonempty repair families through three cases, depth bounds through two, fractional cover examples, paired repair families, universal-repair invalidation, and the composed acquisition/compiler witness.

Where applicable, direct unpruned search and independently coded local certificate replays cross-check the optimized algorithms. Both implementations remain project-authored. All correctness decisions use integers, finite sets, or exact rational arithmetic. The new scope and each group count are recorded in `validation/meta_checks.json`. The unchanged earlier suites retain their original domains and limitations.

## Actual failures and corrections

1. The first proposed parity exhaustion control used values {0,1,3,5}, which have only one even value. The demo correctly returned a finite-consistent expression. The negative-control design was wrong, not the implementation's result. The parity control was changed to all contexts over {0,1,2,3}, and both implementations now demonstrably exhaust the grammar. No claim about the first domain is retained.
2. A combined execution call was interrupted at its outer tool allowance before a final execution receipt was written. That incomplete attempt was not treated as validation. Its log is preserved under `validation/development/`. The stable source was subsequently rerun under supervised subprocess limits and polled to confirmed exit zero. The large unchanged inherited suite has a 90-second wall limit; each other command has 45 seconds.
3. The first complete layout had 56 pages, including a nearly empty continuation page caused by a redundant added related-work paragraph. Removing that paragraph left its references in the substantive new section and produced the final 55-page edition without changing any formal statement or proof. Updated claim-map and open-problem prose were included before the final rerun.

No mathematical assertion failed in the completed exact suites, and no LaTeX compilation failed in this revision. This does not erase the mistaken negative control or interrupted execution. Deliberate rejections of unsafe equations, invalid weights and stale certificates are successful negative controls.

## Visual review and rebuilding

All 55 final pages were inspected in four contact sheets. The cover, new ordered-quotient proof, synthesis-cost figure/table, weighted streaming proof, new repair diagram, and bibliography received full-page inspection. The PDF preflight separately checks geometry, text markers, fonts and LaTeX diagnostics. Mechanical checks and contact sheets do not prove that every mathematical argument is correct.

The clean rebuilding procedure uses a fresh copy without the build directory, the supplied vector assets, the Bash script, and all exact suites and demonstrations. Its record compares extracted text page by page and scientific JSON after omitting only identified time/environment fields. PDF byte identity, Windows behavior, accessibility tagging and PDF/A are not certified. Python figures were actually generated; no generated pictorial imagery is used.

## Evidence and release boundary

The three added primary references received targeted metadata/abstract and selected full-text review as specified in `SOURCE_MAP.md`. No comprehensive re-review of every inherited source or novelty survey is claimed. No third-party full papers are included.

The computation record uses the inherited legacy-v1 format with a separate before/after input-hash receipt. The shipped computation-record checker is project-authored, not an authenticated copy of an external audit tool. It was executed. There is no repository revision, independent attestation, separately imposed process-memory cap, or proof-kernel verification. The programs do not access external services, accounts, or network resources.

Verify the frozen `SHA256SUMS.json` inventory before rerunning commands that overwrite timing records. Checksum agreement establishes integrity relative to the included inventory, not origin authentication or mathematical truth. The prior v0.3 deliverables remain unchanged. `FIRST_EDITION_PLAN.md` separates attainable first-edition consolidation from the open problem of repeated improvements of the equational learner itself.
