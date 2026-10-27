# Review and validation notes
## Self-Improving Intelligence: Representation, Discovery, and Recursive Revision
**Komorebi P. · Operation Komorebi · v0.2.0 · 8 October 2026**

## Scope

This 38-page expanded theoretical draft follows the 28-page v0.1.0. It adds a five-part structure, six statement/proof pairs, three counterexamples, and three analytical vector figures. Its principal constructive advance changes the discovery algorithm, rather than only the repair controller returned by that algorithm. The new finite selector chooses among supplied compiler templates. It does not invent those templates or improve itself.

The additions received internal review against their explicit assumptions, proofs, and finite implementations. The twelve predecessor statement/proof pairs and three core reference programs were retained verbatim and checked mechanically. This is not independent peer review, a complete novelty search, or a Lean/proof-kernel certificate. The mathematical construction is not a neural-agent experiment, and no historical experimental score is used as evidence for the integrated architecture.

## Final inventory

| Item | Recorded result |
|---|---|
| PDF | 38 pages including cover, contents, guide, five parts, appendices, and references |
| Formal statements | 18 paired with prose proofs: 7 theorems and 11 propositions |
| Added statements | Six relative to v0.1.0, not six priority claims |
| Definitions and counterexamples | Two definitions and nine formal counterexamples |
| Illustrations | Six analytical vector figures and six PNG previews |
| References | Eighteen, including the four inherited Komorebi sources |
| Exact suites | 34 groups and 162,784 assertions passed |
| Predecessor suite | 18 groups and 147,180 assertions rerun unchanged |
| New suite | 16 groups and 15,604 assertions passed |
| Preservation | All 12 prior statement/proof pairs plus the three core reference programs unchanged |
| Source audit | No missing or duplicate labels, missing/unused bibliography keys, missing figures, or unmatched proof environments |
| Final PDF preflight | All 38 pages rendered; no out-of-page text, unresolved reference markers, replacement characters, or unembedded font rows detected |
| LaTeX | No final warnings, overfull/underfull boxes, or missing-character diagnostics |
| Fresh rebuild | PASS: identical extracted text on all 38 pages and identical scientific outputs after timing/environment fields are excluded |

The counts describe the manuscript and bounded exact programs. They are not independent replications, statistical samples, new-discovery counts, or general proof certificates.

## Mathematical and implementation review

### 1. Unknown means one fixed unknown model

Theorem 7.1 retains a persistent model tag through every experiment. It does not independently select a different adversarial transition model at each step. Uniform admissibility, the post-experiment state, observed report, and common successful repair are all computed on the tagged support. Conditional correctness requires the actual model to belong to the represented class.

The unknown-orientation example uses `o = x XOR theta`. Repeated nondestructive ordinary queries cannot distinguish `(x,theta)` from `(1-x,1-theta)`, and those possibilities require different repairs. A cost-two reference measurement reports theta. The reference query, ordinary query, and terminal repair then have exact worst-case execution cost four and seven literal stored records. This is a supplied finite calibration model, not learned physical sensor identification.

### 2. The shortcut is authorized by a checked optimum, not by heuristic confidence

The guard verifies total immutable binary unit-cost queries and unit-cost singleton-success repairs. A valid candidate must attain **both** the information-depth work lower bound and the literal-tree storage lower bound. Only then can it return the entire optimal frontier. If a guard, proposal, or optimality check fails, it invokes the unchanged parent compiler. A failed candidate does not establish infeasibility.

The checker reconstructs every branch support and separately replays every represented initial case. Tests deliberately mutate query scope, reports, effects, branch sets, terminal repairs, and budgets. The same project authors the proposer and checker. Their distinct code paths are useful cross-checks, not independent external attestation.

### 3. A table read is a specific charged operation

The meter charges lookups of transition/report records during guard, proposal, exhaustive search, and witness checking. Common input-shape validation precedes the measured compilation allowance and is separately recorded for both methods. Other Python instructions, repair-set scans, source storage, model acquisition, theorem discovery, and human construction of the templates are not claimed to be represented by the read counter.

For sixteen cells, the parent uses 576,128 measured reads. The descendant uses 1,728: guard 320, proposal 1,280, verification 128. Each method also has common shape-validation cost 320. Both return the same optimum, five online units including the repair and 31 stored tree records. This is not a claim of identical literal trees or a measured processor-time ratio.

The universal table-scope lower bound assumes independent arbitrary entries accessed directly. A trusted constructor, cached checked table, or proof-carrying representation changes that contract. The theorem does not require re-reading a table after its scope has already been justified under an applicable cached certificate.

### 4. The selector is supplied, frozen, and finite

The development costs of the parent, first-query wrapper, and balanced wrapper are 10,256, 10,380, and 488 respectively. The full finite selection costs 21,124 model-record reads across all candidates, not merely the winning trial's 488. The configuration is serialized before evaluating additional cases, and its hash is retained in the demonstration.

The comparison then uses cold caches on the larger sixteen-case model, a six-case support, a coordinate-only query library, and an equality-only negative control. These variants are not an empirical statistical holdout population or a claim of generality across unrelated tasks. No target defect or solved controller is installed in the chosen proposal rule.

The outcome changes the compiler's future discovery control flow. The templates, lower bounds, checker, model tables, and selector remain supplied. A successful selection among those candidates is not evidence that the selector has become better at generating the next set of candidates.

### 5. Fallback consumes resources

On the equality-only four-case control, the wrapper returns the same optimum but uses 472 reads versus 402 for the parent. Preserving meaning does not imply nonincreasing work. The separately stated two-worker race requires resumable workers and charged dispatch work. Its finite test uses synthetic worker traces. The sequential reference compiler does not implement that scheduler or receive its bound for free.

### 6. Sequential evidence requires commitment order

Theorem 15.1 uses frozen paired comparisons, scores in [-1,1], a conditional mean null, and predictable nonnegative bets no larger than `1/(1+gamma)`. It yields a nonnegative supermartingale and a time-uniform threshold bound. It permits choosing when to stop from previous audit outcomes. It does not permit looking at the current score before choosing its bet.

The hindsight-betting counterexample crosses the nominal threshold four within four fair scores with probability 11/16, greater than 1/4. Every bet is numerically in range, but its timing violates the theorem. A verifier of numbers alone cannot authenticate when an external decision was made.

The unit of evidence is a complete comparable attempt on a stipulated task, not one message within that attempt. A changed candidate or task law requires its own valid comparison. Finite enumerations of null paths are exact implementation checks, not stochastic trials establishing that a real learner improved.

## Exact finite domains

The new suite covers all pairs of total immutable binary query tables on one through four states, direct destructive/nonbinary/inadmissible mutations, the binary family through 64 cells, parent comparisons through 16, 256 affine/report-flip/order variants, finite template selection, record caps, equality-only fallback, six-case support, unknown sensor orientation with and without a reference, 625 specified two-model transition-table pairs, exact rational evidence multipliers, all fair-sign histories through length ten, hindsight and invalid-bet controls, finite worker races through forty work units with one-sided nontermination controls, independent-record adversaries, and malformed witness trees.

The unchanged earlier suite additionally checks exact frontier synthesis against unpruned tree enumeration, partitions against pair-orbit reasoning, transport, repair-relevant information, selection bounds, adaptive finite hazards, recursive progress, and operation continuation. Exact domains and assertion counts are attached to each group in the two JSON reports. No floating-point tolerance is used as a correctness criterion. Figures convert exact reported quantities to plotting coordinates.

## Failures and corrections actually encountered

1. A preliminary source audit was run before the new figures were created. It correctly failed on missing figure assets, but an inherited diagnostic printed the full figure list rather than only missing paths. The diagnostic was corrected, the assets were generated, and the audit passed afterward.
2. An initial combined validation/build tool call had a 45-second allowance. The unchanged inherited exact suite did not finish before that allowance, so the command timed out. A later long container call returned a transport timeout while the subprocess continued. Its completed JSON and terminated process were checked and showed a passing suite, not a mathematical failure.
3. The final validation wrapper records a 90-second wall limit for that unchanged inherited suite and 45 seconds for each other subprocess. The complete final wrapper passed. This increases the execution allowance, not the mathematical domain or an assertion's acceptance tolerance.
4. The first expanded layout had 40 pages with short continuation pages. Redundant prose was tightened without changing any prior statement/proof pair. The final document has 38 pages.
5. Full-page review found two flowchart labels encroaching on box edges. They were moved into whitespace, the figures were regenerated, and the PDF was rebuilt and re-rendered. Final validation was rerun after the figure-generation code changed, so the execution receipt pins the delivered source.
6. Some literature fetches failed or returned irrelevant material. The records actually obtained and the limits of full-text review are documented in `SOURCE_MAP.md`.

No mathematical assertion failed in the completed suites, and no LaTeX compilation failed during this revision. Invalid inputs deliberately rejected by the tests are negative controls, not execution errors. Earlier draft corrections remain visible in the retained predecessor review.

## Visual review and clean rebuilding

Every final page was rendered and inspected at contact-sheet scale. Physical pages 1, 13, 18, 21, and 25 were inspected at full-page scale, including the cover, the uncertain-sensor diagram, the repaired compiler flowchart, the logarithmic cost plot, and the sequential-audit theorem. Mechanical text bounds, LaTeX diagnostics, and font checks are recorded separately. This is not a claim that every proof was independently re-proved during visual inspection.

A new source copy without its build directory was used for the clean rebuild. It used the shipped vector assets and reran the supplied validation wrapper. `validation/fresh_rebuild.json` records the result and compares every page's extracted PDF text and the scientific JSON outputs after removing only timing/environment fields. PDF binary identity, Windows execution, accessibility tagging, and PDF/A are not certified.

The frozen ZIP's checksum inventory verifies the included snapshot. Verify it before rerunning programs that overwrite timed receipts. Hash equality establishes integrity relative to the shipped inventory, not truth, independent execution, or origin authentication.

## Source and provenance boundary

The source review is targeted rather than exhaustive. Two public references were added, and selected inherited records were checked for the extended use. Some were available only as primary metadata or abstracts. The new conditional proofs are stated in full rather than relying on inaccessible unstated results.

The execution receipt is project-local, not an independently authenticated audit service or plugin-generated proof. It records actual commands, versions, timings, source hashes before and after execution, and result hashes. No separate memory cap, Git revision, OS sandbox, external attestation, or proof-kernel result is claimed. The reference programs do not access the network or external accounts.

The original v0.1 files and other Komorebi manuscripts remain unchanged. The package contains no standalone font file, private conversation transcript, third-party paper full text, neural checkpoint, or external-action integration. The remaining recursive bridge is stated in `NEXT_REVISION.md` rather than hidden behind the expanded version number.
