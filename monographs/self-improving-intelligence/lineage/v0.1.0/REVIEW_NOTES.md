# Review and validation notes
## Self-Improving Intelligence: Representation, Discovery, and Recursive Revision

**Komorebi P. · Operation Komorebi · Version 0.1.0 · 8 October 2026**

## Scope and status

A new 28-page first theoretical draft, not a new edition of *Machine Understanding* or *Machine Societies*. It selectively connects the theoretical SRIC framework to reusable representations, investigation, semantic transport, selection, and recursive continuation. Historical internal agent experiments are not reported as results. The reference construction is a fully specified finite mathematical model.

The twelve statement/proof pairs were internally reviewed against their explicit assumptions and analytical examples. The exact implementation was checked on the bounded domains below. This is not independent peer review, a comprehensive novelty audit, or a proof-assistant certificate. The operational framing of general intelligence remains a proposal.

## Final inventory

| Item | Recorded result |
|---|---|
| PDF | 28 pages including cover, contents, guide, four parts, appendices and references |
| Formal statements | 12 with prose proofs: four theorems and eight propositions |
| Definitions / counterexamples | Two definitions and six formal counterexamples |
| Illustrations | Three analytical vector figures with three PNG previews |
| References | Sixteen, including four Komorebi predecessors |
| Exact finite suite | 18 groups and 147,180 assertions passed |
| Source audit | No duplicate labels, missing references, missing/unused bibliography entries, missing figures, or unmatched proof environments |
| LaTeX | Final compilation has no warnings, overfull/underfull boxes or missing-character diagnostics |
| PDF preflight | All 28 pages rendered; no out-of-page words, unresolved reference markers, replacement characters or unembedded font rows found |
| Clean rebuild | Fresh source copy rebuilt successfully with identical extracted PDF text on every page |
| Clean exact rerun | Same groups and assertion count, and identical scientific demonstration payload after excluding runtime |

These counts describe document and implemented finite-domain inventory. They are not counts of independent replications, statistical samples, new mathematical discoveries or proof-kernel certificates.

## Main mathematical review points

**The improver is not an oracle.** Productivity evaluates the selected descendant actually returned by a procedure. It does not take the highest final-test result among all generated candidates after the fact. A permitted fallback does not establish nonnegative true gain if a noisy selector fails to use it appropriately.

**Information concerns the complete transcript.** The repair-discrimination bound uses full observation laws and disjoint successful repair sets. Equal marginal observations do not imply equal joint histories. Full case identification is unnecessary when a single repair succeeds throughout the remaining support. Pairwise repair-set overlap is not enough for a common repair.

**Stable refinement assumes a complete model.** The partition theorem preserves the labels initially retained and the stated operations. It does not learn the transition table, and it need not minimize a representation allowed to discard old labels.

**The compiler retains post-experiment state.** The support update includes the effect of the experiment. A reset can make a current state known without revealing its origin. Origin-dependent targets require an immutable state component, and that variant is checked explicitly.

**The resource claim uses one complete tree.** Execution cost includes the final repair. Storage includes every stored branch, not only the visited branch. Pareto pruning is valid because the parent maximum and sum are monotone. Model acquisition, compilation and validation are separately identified costs. The count is for literal tree records, not minimal bytecode or shared-subroutine graphs.

**The same library is available to the baseline and compiler.** Equality-first testing is a fixed procedure, not a claim that singleton tests are the strongest baseline when bit queries exist. The optimality comparison separately proves what is attainable in the stated query class. The eight-cell demonstration establishes a compiled diagnostic improvement, not a learned abstraction or self-modifying compiler.

**Transport covers the investigation.** The theorem assumes exact correspondence of experiments, admissibility, report labels, state transitions, repair success and costs. Transferring only successful repair effects does not provide missing diagnostic observations. Affine cell adapters are supplied, not learned. Repair IDs in the program remain fixed while their target effects are transported, and the demonstration records the state correspondence explicitly.

**Acceptance guarantees have premises.** Candidate selection requires uniform estimation error. Adaptive lineage control requires conditional validity for each attempt and a summable budget. The displayed fresh-sample bound assumes conditional iid paired scores, a fixed sample count selected before the fresh audit, and no access to that audit during proposal. The deterministic suite does not validate a general statistical testing service.

**Recursive progress uses one policy.** The finite recurrence chooses an action before its possible outcomes and requires every successor to preserve the remaining target. The system state includes all relevant information and resources. Progress marks must be independently justified by the declared comparison; their mere presence in a table is not evidence of actual learning.

**A fixed-score ceiling needs nondecrease outside marked events.** Without that condition, repeated losses and recoveries can create arbitrarily many positive increments without unbounded cumulative progress. Summable positive increments likewise do not imply acceleration.

**Local semantics need invariant scope and outputs.** Operation commutation extends to finite words only on the declared invariant domain, and required outputs must factor through the representation. That statement does not discover the map or demonstrate that a neural solver uses it causally.

## Executed finite domains

The suite uses exact integers, finite sets and `fractions.Fraction`, with no randomized samples. Named groups and domains are retained in `validation/finite_checks.json`.

Coverage includes quarter-grid binary transcript laws; complete small partition-refinement models with pair-orbit comparisons; every pair of binary transition/report tables on two states with every nonempty support at horizons zero through two; unpruned policy-tree enumeration; partial domains; destructive resets and immutable-origin controls; repair-relevant partitions; a genuine execution/storage tradeoff; all cells in power-of-two families through 32; all 32 affine cell permutations modulo eight and eight report-flip choices; malformed and over-budget certificates; rational selection margins; grammar dilution; amortization and score ceilings; all 128 specified history-dependent error-hazard choices; 1,296 two-state recursive action models with three safe-set choices and bounded targets; retry/dead-end controls; and all words through length four in the specified three-register F5 continuation model.

Unpruned tree enumeration, full-case replay, pair-orbit comparison, and stationary-policy enumeration are separately coded alternatives. They are authored within this project, so they are cross-checks rather than independent external validation.

The cell compiler visits 263 support/horizon states, considers 1,199 experiment roots, and evaluates 227 child combinations in the recorded run. These are algorithm counters, not a claim to count every processor operation. It returns work four and storage fifteen. Under three diagnostic calls and one repair call, the fixed equality-first baseline succeeds on 3/8 of the uniform cases and explicitly abstains on the others. The compiled tree succeeds on all eight. The supplied complete observation table has 88 entries; no claim of 88 executed physical calibrations is made.

## Presentation corrections and execution outcomes

No mathematical assertion or LaTeX compilation failed during the recorded drafting runs. Invalid models and certificates were deliberately submitted to the checker and rejected as expected.

The first successful PDF had 30 pages, including two isolated floating-figure pages. Repositioning the figures, shortening repeated introductory prose and removing a short redundant spillover paragraph produced 28 pages without removing any formal statement or proof. A long source filename initially caused two underfull-box diagnostics in the bibliography; the exact filename was moved to `SOURCE_MAP.md` and the citation kept readable.

Full-page visual review found a vertical arrow crossing the label and heading in the initial two-loop diagram. The unnecessary arrow was removed and the figure regenerated. The cost figure's caption was also tightened to distinguish diagnostic queries from the plotted total including the repair call. The repair-partition figure was placed after the completed counterexample text rather than between its two page-spanning portions. These corrections did not change the finite arithmetic.

The source audit includes a numbering cache derived from the canonical LaTeX auxiliary file, so the Python-only validation path can preserve statement numbers when a user has not installed LaTeX. This is editorial metadata, not a proof witness.

## Visual and reproducibility review

All pages were rendered and inspected in contact sheets. Physical pages 1, 5, 10, 11, 18, 22 and 28 received full-page review. The changed figures and their surrounding pages were inspected again after correction. The final preflight records page bounds, diagnostics, rendering version and font results. Text bounds are a mechanical screen, not a replacement for that visual review.

A fresh source copy without the build directory rebuilt through `build.sh`, reran the exact suite, and reproduced the scientific demonstration. The comparison is identical extracted PDF text and matching mathematical payloads, not PDF binary identity. The Bash build was executed. Windows execution, PDF/A conformance and tagged accessibility were not certified.

`validation/execution_manifest.json` pins the final source/scripts and numbering record before and after execution, records actual commands and timings, and hashes the output records. Each validation subprocess has a 45-second wall timeout. No separate memory cap, Git revision, externally authenticated receipt or operating-system sandbox is claimed. The snapshot checker verifies the supplied hashes; it cannot establish mathematical truth by hashing them.

## Source and open-scope limits

`SOURCE_MAP.md` records the primary-source review. The public literature was reviewed mainly through primary abstracts/metadata, with targeted full-text inspection of the Hyperagents and AIDE2 claims about the improver. The Hyperagents abstract and rendered-version metadata differed, so no reconciled full author/version record is claimed. The large SRIC predecessor was selectively consulted, not re-proved or replayed in its entirety. Prior neural experiments remain outside the evidence of this new draft.

The main outstanding tasks are learning the experiment model, discovering a costed new repair constructor, and demonstrating a genuine improvement of the compiler or discovery procedure on comparable fresh problems. This first draft provides conditional theory and an exact compiled example, not an empirical claim that any of those wider tasks has been completed.

The package includes no private conversation transcript, third-party paper full text, standalone font files, neural checkpoint or external-action integration. Prior Komorebi manuscripts remain unchanged.
