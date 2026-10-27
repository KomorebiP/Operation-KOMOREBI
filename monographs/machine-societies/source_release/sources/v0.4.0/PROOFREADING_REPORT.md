# Proofreading and validation report — v0.4.0

**Work:** Machine Societies: A Theory of Persistent Plural Computational Organization  
**Edition:** 7 October 2026 · Komorebi P. · 49 pages  
**Review type:** in-session authoring, mathematical review, exact finite regression, and rendered-layout inspection. This is not independent peer review.

## Outcome

The requested additions are integrated into the manuscript rather than appended as an unconnected prospectus. The general results have explicit assumptions and prose proofs. The final source compiles cleanly, all cross-references and citations resolve, and all 49 pages have been rendered and inspected through contact sheets, with additional full-page inspection of selected mathematically and visually dense pages.

| Check | Recorded result |
|---|---|
| LaTeX compilation | Successful clean build; 49 pages. |
| Compiler diagnostics | No warnings, overfull/underfull boxes, undefined references, or missing-character diagnostics in the final log. |
| Source consistency | No duplicate labels, unresolved references, or unresolved bibliography keys. |
| Mathematical inventory | 3 theorems, 26 propositions, 5 definitions, 7 counterexamples. |
| Visual inventory | 5 vector figures, including 2 analytical plots. |
| References | 33 entries; all 7 new entries and 2 retained norm-theory entries received targeted external source checking. |
| Exact regression | 28 groups, 173,231 assertions passed using integer/rational arithmetic. |
| PDF geometry/text | No extracted words outside page bounds; no unresolved “??” or replacement-character markers. |
| Execution receipt | The recorded script, manuscript, and result hashes match the final files. |
| Release integrity | File hashes and ZIP integrity are checked by the supplied release verifier and packaging validation. |

## Substantive corrections and qualifications

**Joint information, not marginal information.** The brainstorm's decentralized-safety argument was too easy to read as a claim about individual ignorance. Equal marginal observation laws do not imply equal joint action laws. The corrected theorem uses the law of the entire tuple of local histories and relevant random tapes. A fair-bit parity counterexample shows why the distinction matters. An architecture-level impossibility requires the indistinguishability hypothesis for every admissible protocol, not just one.

**Strict adoption thresholds.** A strictly profitable coalition requires b(m−1)>c, giving floor(c/b)+2 adopters, not the threshold for weak improvement. The four-agent example with b=1 and c=2 distinguishes zero gain from strict gain. The growth argument states its eventual-update assumption, and the hysteresis discussion states its tie rule and effective-cost extension.

**Permission preservation.** An adequate next-output predictor need not preserve enabled amendments. The governance quotient explicitly preserves labels, action availability, and successors. Its policy interpretation does not grant a decentralized office access to an unavailable summary or permission to issue an action.

**Deadline boundaries and succession.** Timely events at a deadline are processed before the clock is advanced beyond it. Unauthorized cancellation is not fulfillment. Monitor preservation under successor translation does not prove that an outstanding obligation will actually be met. Bounded-deadline safety is separated from unbounded eventual service.

**Repair inequalities.** Nonnegativity is now explicit in the general product–sum repair statement. Feasible macro-reset pairs are distinguished from targets that have no admissible implementation. Coalition families are nonempty where a minimum is taken, and nonzero variance is specified for effective-sample-size interpretation.

**Typed residuals.** Each semantic triangle inequality uses a common aligned metric codomain. Different residual units are not aggregated. Small metric state error does not imply exact permission preservation. Evidence-record preservation does not certify truth, and zero residual does not by itself imply injectivity or legitimacy.

**Lifetimes and authority.** The first-exit formula uses a finite substochastic kernel with spectral radius below one. It is not extended by inverting a singular matrix or treated as immortality. Blocking coalitions are derived under a specified monotone approval system; the threshold formula has 1≤q≤n. Hidden administrators must be represented in the effective winning-coalition family.

**Language, numbering, and layout.** Repetition in the introductory realization discussion was reduced. The symmetry discussion now refers to the correct proposition and uses pointwise invariance rather than confusing it with exchangeability. The running example consistently has four offices; an inherited “fourth preference function” phrase was corrected to “additional preference function.” Long displayed predicates were shortened without changing their definitions. The reference layout was adjusted so that a single final entry does not occupy an otherwise empty page.

## Finite checks and their limits

`validation/check_finite_models.py` enumerates exact finite instances: small transition systems and partitions, rational kernels, all specified coalition configurations, majority agendas, deadline-event strings, two-state lifetime models, finite translation maps, binary cycles, and resource/repayment traces. Its precise bounds appear in `validation/finite_checks.json` and `validation/computation_manifest.json`.

The test suite is authored alongside the manuscript. Passing it confirms the implemented finite assertions over those bounds. It is neither an independent audit nor formal verification of the general propositions. Classical external theorems are not reproved by the test suite. No learned-agent or machine-society experiment was run for this edition or inserted into the paper.

## Reference review

All seven newly added references were checked through publisher, journal, or author-hosted records. Two retained norm-theory references were checked for title, authors, venue, and DOI. The other retained entries were checked for source/bibliography consistency but were not all independently refetched. The review is targeted and does not establish an exhaustive literature or priority search. Details and public source locations are in `validation/reference_review.md`.

## Recovered failures

1. **Figure export:** the first plotting process could not write into a root-created directory. File-system permissions were corrected and both figures were regenerated successfully. The failed attempt is not treated as a created artifact.
2. **Compiler launch wrapper:** an interactive execution mode was unavailable. No compiler result was inferred from that launch. An ordinary synchronous LaTeX invocation then completed successfully.
3. **Bulk reference metadata request:** all 16 attempted runtime Crossref requests failed because the runtime could not resolve/reach the service. That output is retained as `validation/reference_metadata_failed_runtime_attempt.json`. It is not verification evidence. Targeted source checking was subsequently performed with the web tool, with the limited scope described above.

## Remaining publication work

The manuscript has not undergone independent peer review, a formal-kernel proof build, an exhaustive priority assessment, or venue-specific editorial review. No target journal's style, anonymity, data, or accessibility policy has been applied. The released PDF is not tagged for full accessibility conformance. The general formation, open-ended governance, normative legitimacy, and real-world implementation questions are not claimed solved by the finite results.
