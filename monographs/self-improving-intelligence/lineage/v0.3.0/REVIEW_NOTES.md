# Review and validation notes
## Self-Improving Intelligence: Representation, Discovery, and Recursive Revision
**Komorebi P. · Operation Komorebi · v0.3.0 · 8 October 2026**

## Scope

This 47-page, six-part theoretical draft follows the 38-page v0.2.0. It adds five statement/proof pairs, four counterexamples, three analytical figures, two references, and a bounded grammar-synthesized change to an internal compiler decision. It does not describe a neural-agent experiment. No historical internal experimental score is used to establish the complete proposed architecture.

The new arguments, numerical examples, and code received internal review against their stated domains. The retained material was checked for preservation, references, integration, and finite regression behavior, not independently re-proved in full. This is not independent peer review, a comprehensive novelty audit, or Lean/proof-kernel verification.

## Recorded final inventory

| Item | Recorded outcome |
|---|---|
| PDF | 47 pages, including cover, contents, reading guide, six parts, appendices and references |
| Statements with prose proofs | 23: nine theorems and fourteen propositions |
| New statements | Five relative to v0.2, not five mathematical priority claims |
| Definitions and counterexamples | Two definitions and thirteen formal counterexamples |
| Figures | Nine analytical vector figures and nine PNG previews |
| Bibliography | Twenty entries, including four inherited Komorebi sources |
| Exact suites | 48 groups and 207,143 assertions passed |
| Predecessor suites | 34 groups and 162,784 assertions rerun |
| New finite checks | Fourteen groups and 44,359 assertions passed |
| Preservation | Eighteen prior mathematical statements and proofs retained. Seventeen pairs are verbatim and one has a notation-only subscript correction. Six prior core programs are byte-identical. |
| Source audit | No duplicate or missing labels, missing/unused bibliography keys, missing figures, or unpaired proof environments |
| Final PDF preflight | All 47 pages rendered. No out-of-page words, unresolved/replacement text markers, or unembedded font rows detected |
| LaTeX | No final warnings, overfull/underfull boxes, or missing-character diagnostics |
| Fresh rebuild | PASS: identical extracted text on all 47 pages and identical scientific outputs after excluding the listed timing/environment fields |

Counts describe the document and executed finite domains. They are not counts of independent replications, statistical samples, new discoveries, or universally verified theorems.

## Mathematical boundaries and corrections

### 1. A missing search feature is not fixed by more program syntax

The rejection decision depends on partial branch counts and the capacity allowed by remaining depth. The finite feature-fibre criterion proves when a label can be expressed from a feature map. The reference learner detects identical old features with contradictory labels. It then exposes capacity from a supplied feature registry. It does not invent the concept of depth, learn physical semantics, or acquire hidden state through this feature change.

### 2. The learner composes a rule, but its language and teacher are supplied

The grammar has 3,960 ASTs, each containing three or five nodes. Its atoms are the four integer features and constants zero and one. Its arithmetic primitives are addition, minimum and maximum, followed by a comparison. The reference algorithm considers 190 candidates in a fixed order. Three counterexamples precede the fourth teacher call, which certifies agreement on the 198 developmental contexts. The selected expression has five nodes and is serialized before larger cases are evaluated.

The synthesis receipt charges all 3,960 generated ASTs and their 19,440 literal node occurrences, 282 retained-example checks, 210 teacher comparisons, 344 possible completion counts examined by the teacher, and 1,898 interpreter node visits. These are distinct units. They are not silently converted into physical memory bytes or CPU instructions. The learner does not change its own enumerator, candidate order, teacher, grammar, or supplied theorem.

### 3. Finite agreement does not authorize general pruning

The expression `max(a,b)>min(C,4)` agrees with the correct rule on every developmental capacity and fails at a larger capacity. The delivered structural gate rejects that expression. The actual installation is justified by a separate prose proof for all integer prefixes satisfying its scope, plus a deliberately narrow executable check connecting the AST to the proved canonical form.

This gate is not a general arithmetic theorem prover. The supplied correctness theorem is part of the prior information, not something discovered by the learner. No universal claim is inferred from 198 examples or from a successful finite check.

### 4. Capacity completion is weaker than controller existence

The prefix theorem asks whether unread binary reports can possibly fit both child capacities. It does not promise that the installed query library can actually distinguish either child. The compiler continues searching subtrees and checking complete witnesses. A four-case model with only one two-by-two split passes the local capacity test and still has no depth-two identifying tree.

A failed proposal does not normally certify global infeasibility. The specific depth-limited search can return infeasible only after completing its search at the requested depth. At a larger horizon it invokes the unchanged general compiler. Exhausting a record-read limit produces `incomplete`, not `infeasible`.

### 5. The primary comparison isolates one change

Both full-scan and streaming versions use the same query order, row order, initial support, target depth, repair semantics, scope guard, witness verification and fallback. A prefix over capacity can never return below capacity because counts only increase. Rejecting it early therefore skips a suffix that would not change the baseline decision. The primary returned trees are identical, not merely equal in resource totals.

The prior balanced wrapper is a separate comparator. Comparing its counts with the streaming counts alone would combine a change in ordering with a change in pruning. The manuscript does not attribute that combined difference entirely to the synthesized rule.

### 6. Predicate work is retained in the accounting

At 64 cases, full-scan compilation reads 27,744 model records and streaming reads 19,457, including their semantic guards and witness verification. Both separately pay 4,480 common input-shape reads. The streaming implementation adds 14,209 lowered integer comparisons. Its interpreted version visits five AST nodes for each prefix instead.

The lowering uses an explicit invariant: the previous prefix passed, and one count increases by one. Under that invariant only the updated count needs comparison with capacity. It does not claim that one comparison evaluates an arbitrary program.

In the conservative two-unit model, where a row costs `w` and a new comparison costs one, the 64-case saving is `8287*w-14209`. It is negative when `w=1`. At two cases, zero model reads are saved and the extra comparisons remain. There is no universal wall-clock speedup claim, and search-language construction, theorem discovery and physical model acquisition are not included in the model-read metric.

### 7. A changed repair language changes the pruning premises

When one repair succeeds in several cases, a controller need not identify each case. The repair-cover proposition gives an appropriate general lower bound but does not provide a cheap incremental cover algorithm. The guard rejects the singleton shortcut if a universal repair is added. The general fallback then returns the valid cost-one, one-record repair. Reusing the old cardinality premise would be unsound.

### 8. A bounded discovery improvement is not indefinite recursive improvement

The retained object is now an internal discovery decision generated from primitive syntax. That changes later compiler behavior, not merely the controller returned for one developmental case. But the candidate grammar, finite teacher and verification method remain supplied. The next recursive claim would concern a better method for acquiring those rules or their representations from fresh comparable starting conditions. It is not established by reusing the same fixed enumerator.

## Exact implementation domains

The new suite checks every generated AST, all 198 training prefixes, literal binary completions on supports through eight, every ordered pair of total binary query tables through four cases, capacity-lowering transitions through capacity 32, repair-cover examples through three cases, guard mutations, unsafe finite-consistent expressions, input caps, all nonempty supports of an eight-case model, deliberately malformed witnesses, 256 cold relabeling/report/order variants, and primary comparisons through 64 cases. Detailed per-group bounds and counts are in `synthesis_checks.json`.

All mathematical acceptance checks use integers, finite sets, or `fractions.Fraction`. Figures convert exact output quantities to coordinates only for plotting. Separate code paths compare the optimized search against the unchanged exact frontier compiler on small domains. These paths were authored in the same project and are not independent external validation.

## Actual execution and editorial corrections

1. Source review found a broken subscript in the inherited shortcut-cost formula. The statement displayed an unintended line break in `R_...`. It was corrected to `R_{\mathrm{shortcut}}`. Its bound, assumptions and proof were not changed. The preservation checker records this single allowed typesetting correction instead of falsely reporting all eighteen pairs as verbatim.
2. Early layouts placed one new diagram on a nearly empty float page. The pipeline was moved beside its introductory discussion, the count-prefix figure was allowed to share a page with text, and figure labels were enlarged. Repeated nonmathematical conclusion paragraphs were removed, and bibliography typography was compacted without changing the body font or deleting any proof. The final length is 47 pages rather than the first layout's 49.
3. The attempted interactive execution session returned `StreamingExecNotEnabledContainerError`. A subsequent short orchestration call returned a tool timeout even though its subprocess completed. Its exit record, terminated process and complete logs were inspected before treating it as successful.
4. Another 45-second combined render/validation call timed out before the wrapper completed. Its old receipt was not treated as validation of the new source. The final wrapper was launched with detached standard streams within this interaction and polled to actual completion. It returned zero and produced a new matching-input receipt. The large inherited suite retained its 90-second subprocess wall limit and other commands their 45-second limits.
5. Failed source fetches and irrelevant searches were not counted as full-text review. The primary alternatives and actual review depth are recorded in `SOURCE_MAP.md`.

No mathematical assertion or LaTeX compilation failed in the completed v0.3 runs. The execution-time and orchestration failures above remain failures and are not erased by later successful reruns. Deliberately rejected bad rules, scopes and certificates are negative controls, not unexpected assertion failures.

## Visual review and clean rebuilding

Every final page was rendered with PyMuPDF. All pages were inspected in contact sheets, and the cover, new section diagrams, representative new proof pages, conclusion and bibliography were inspected at full-page scale. The final changed pages were rechecked after the float and reference-spacing corrections. `validation/pdf_preflight.json` records geometry, fonts and build diagnostics. Mechanical bounds checks do not establish that every formula or argument is correct.

The clean rebuild uses a new source copy without the build directory, the supplied vector figures, and the provided Bash build. It reruns all suites, demonstrations, preservation, source checks and local receipt checks. `validation/fresh_rebuild.json` records the actual page-by-page extracted-text comparison and scientific JSON comparisons. Only the explicitly listed timing/environment fields are omitted from JSON equality. PDF binary identity, Windows behavior, accessibility tagging, and PDF/A are not certified.

The final ZIP contains a checksum inventory. Verify the frozen snapshot before running commands that overwrite timed receipts. Equality with the inventory establishes integrity relative to that inventory, not truth or independent authentication of its origin.

## Sources and provenance

Two primary references were added. The syntax-guided synthesis specification was available as readable primary text. The invariant-learning reference was reviewed through publisher/university metadata and abstracts, not a complete proof audit. Selected inherited current-paper records were rechecked. The bibliography is not an exhaustive novelty review and not every inherited full text was independently re-read.

The computation manifest follows the available legacy-v1 template. The checker supplied here is project-authored and was executed. It is not claimed to be an independently authenticated copy of the plugin validator. A separate local execution receipt pins source, code and figure inputs before and after running and hashes scientific outputs. No Git revision, external attestation, independent process-memory cap, OS sandbox, or proof-kernel result is claimed.

Original v0.2 deliverables and other Komorebi manuscripts remain unchanged. The package contains no standalone font files, private conversation transcripts, third-party full papers, neural checkpoints, or external-action integration.
