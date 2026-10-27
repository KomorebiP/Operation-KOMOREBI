# Proofreading and validation report — v0.6.0

**Machine Societies: A Theory of Persistent Plural Computational Organization**  
**Komorebi P. · 8 October 2026 · 79 pages**

## Scope and evidence boundary

The five approved additions were integrated into the theoretical manuscript and reviewed against their explicit assumptions. New proofs, counterexamples, notation, references, and analytical figures were checked. The retained material was checked for preservation, integration, cross-references, and finite regression behavior. This is not a new independent proof audit of every retained theorem, independent peer review, or formal-kernel verification.

The manuscript does not report the author's agent experiments. All calculations described here concern finite mathematical constructions. The proof arguments, not a large assertion count, support the general conditional statements.

## Recorded final outcome

| Item | Result |
|---|---|
| PDF | 79 pages, including cover, contents, appendices, and references |
| Statements and proofs | 50 theorem/proposition statements and 50 prose-proof environments: 8 theorems, 42 propositions |
| New statements | 9 relative to v0.5.0; not nine mathematical priority claims |
| Other formal material | 6 definitions and 15 counterexamples |
| Figures | 12 vector figures; 4 new analytical diagrams/plots |
| Bibliography | 50 entries; 10 new entries with targeted source review |
| Exact mathematical checks | 52 groups and 367,813 assertions passed |
| Predecessor assertions | All 39 groups and 325,054 assertions rerun |
| New finite assertions | 13 groups and 42,759 assertions passed |
| Source preservation | All 41 prior theorem/proposition environments retained verbatim |
| Cross-references | No duplicate labels, missing references, missing bibliography keys, or unused bibliography entries |
| Final LaTeX diagnostics | No warnings, overfull/underfull boxes, unresolved references, or missing-character diagnostics |
| PDF checks | All 79 pages rendered; no out-of-page words or unresolved/replacement text markers detected |
| Visual review | All pages inspected in contact sheets; cover, contents, new figures, selected proof pages, and final references reviewed at full-page scale |
| Manifest and artifact integrity | Recorded output hash and separately pinned inputs checked; legacy v1 schema limitations retained |
| Fresh extraction | See `validation/fresh_rebuild.json` for actual rebuild and finite-rerun results |

The suite uses exact integers and `fractions.Fraction`. Actual timing, interpreter/platform information, source hashes, and per-group domains are recorded in the manifest and `finite_checks.json`. Figures convert exact analytical probabilities to floating-point coordinates only for plotting.

## Important mathematical clarifications

**Convergence does not imply a valid allocation.** The merge result assumes a fixed finite set of accepted contributions and eventual inclusion at every replica. It does not certify which updates are authorized, that different schedules generate identical updates, or that quiescence is detectable. Invariant preservation additionally requires safe local transitions and closure of the safe set under merge. The double-grant example violates that last condition.

**Exclusive service needs a realizable information contract.** The impossibility result assumes no cross-request information or separate atomic grant operation before the deadline, and unconditional singleton service. Preallocation, waiting, or stronger coordination changes a premise. The randomized extension uses probability-one local guarantees and request-independent tape laws; it does not require independent tapes.

**The sanction bound is an exact, restricted criterion.** The total-variation threshold is necessary and sufficient for one specified deviation under a committed, risk-neutral, collectible, authorized fixed penalty. Equality permits indifference. False-positive protections impose a separate optimization constraint. Pairwise optimal monitors for different deviations need not combine into one valid policy. The enforcer's own incentives are not assumed solved by the calculation.

**Averaging requires both mixing and a review schedule.** The block theorem assumes finite fast and institutional state spaces, a fixed positive block length, a uniform endpoint mixing bound, and endpoint-based revision. Its path-law result permits dependent fast-state resets but does not preserve unrecorded fast events. A stopping-time counterexample shows that data-selected reviews can bias the result despite exact deterministic-time stationarity. The robust enforcement margin carries approximation error into deterrence and false-positive guarantees rather than ignoring it.

**The cascade formula depends on the tie convention.** The binary model follows the private signal at posterior indifference. The original classical paper's basic example instead uses random tie-breaking. The manuscript states this difference explicitly. The formula and plotted last-action probabilities were verified by an independent recursion over Bayesian action-history distributions, not merely by recoding the closed form. The full-signal comparison assumes authentic conditionally independent signals and does not settle privacy or reporting incentives.

**Individual backups are weaker than joint replacement capacity.** The staffing theorem is exact for simultaneous roles, unit-capacity agents, fixed surviving capability/authorization edges, known erasures, and permitted reassignment. The proof includes the matching argument. It does not guarantee that distributed agents discover or execute the rematching before a deadline. The temporal-path counterexample shows why a connected union of contacts may not carry evidence in the required order.

## Finite test coverage

New domains include semilattice laws and delivery permutations, safe/unsafe grant merges, local exclusive-service functions, rational probability laws and sanction policies, exact false-positive LP vertices, common-channel garbling, refresh-kernel powers, institutional path laws with dependent resets, bounded adaptive review histories, robust enforcement margins, Bayesian cascade histories, independent binomial majority tails, every bipartite graph with up to three roles and four agents, every associated erasure set/budget, and explicit temporal communication controls. Detailed bounds are attached to each group.

These are bounded implementation checks, not universal enumeration of arbitrary societies, unrestricted programs, strategic adversaries, or all institutional rule languages. No statistical confidence claim is made from these deterministic counts.

## Presentation and technical corrections

The first successful layout produced an 80-page PDF because two contents entries spilled onto a nearly empty second contents page. Reducing only the inter-entry contents spacing from 1.5 pt to 0.5 pt corrected this while keeping the contents and body font sizes unchanged. The final PDF is 79 pages. The cascade figure caption was tightened to identify the last action's error. Fixed-contribution and zero-horizon conventions were made explicit before final checking.

The first exact run passed; no finite assertion failure was encountered. Some source fetches failed, and several broad searches were irrelevant. Those retrieval outcomes were not treated as successful evidence. The reference review records the access challenge, original-publisher 403, inaccessible author copy, and the primary alternatives actually used. Full text was not obtained for every added source.

## Reproducibility and remaining limits

A clean Bash LaTeX build was executed. The supplied Windows PowerShell script was inspected but not run on Windows. No separate font files are distributed; the PDF embeds its used fonts. PDF/A and tagged accessibility were not certified.

The computation record retains the inherited **legacy v1** schema. The schema validation logic read from the computation-audit skill was transcribed into the working environment and executed; the shipped `verify_release.py` separately checks the pinned inputs, outputs, group counts, and snapshot inventory. The transcribed schema checker is not an independently authenticated software distribution. The legacy record does not provide a Git revision, independent execution attestation, or machine-checkable resource-limit enforcement. The run was CPU-only and submitted with a 45-second tool timeout; no separate process memory or affinity cap was imposed.

The newly added proofs are self-contained conditional arguments. There has been no independent peer review, Lean build, comprehensive novelty/priority audit, or target-publication acceptance review. The preserved source lineage and finite checks make review easier; they do not remove these remaining obligations.
