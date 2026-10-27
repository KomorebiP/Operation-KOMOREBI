# AVOC v0.26.0 — exact proof and experimental boundary

## Kernel-checked

1. Full eight-input signatures characterize equivalence for the inherited three-input Boolean language.
2. Cached signatures and sizes have proofs of correspondence to the retained expression.
3. Semantic compaction preserves an equivalent no-larger representative for every input candidate, retains only input-origin candidates, and has unique signatures.
4. A unique library has at most 256 semantic representatives.
5. Recursive expansion from representatives covers every full-grammar candidate at the same depth, never needing a larger equivalent representative, and retained codes belong to the full grammar.
6. Every reference has the same minimum attainable node count in feedback and frozen search at each full depth, including its original incumbent. This does not promise identical tie-selected syntax.
7. Instrumented compaction corresponds to the specification; probe and structural-charge bounds hold. Budget preflight prevents unaffordable layer generation and conserves its declared credit.
8. Returned budgeted libraries retain coverage and optimality at their attained depth, not automatically the requested depth.
9. Search plus funded query plus promotion/evaluation/switching charges remain inside the campaign envelope. Existing promotion semantics and in-memory journal replay are preserved.
10. Counterexamples distinguish semantic identity from equal size or single-sample agreement, and show why an arbitrary larger representative is not adequate for node-minimum preservation.

## Executed checks

- Actual Lean runtime versus an independent Python truth-bitset/dictionary oracle.
- 1,792 query cases; 32 budget cases; 512 equivalence cases; 27 campaigns; 12 malformed wire cases; 12 CLI cases.
- Matched frozen/feedback depths 0,1,2, with complete query-function coverage. A separately reported feedback-only depth-3 extension reaches all 256 behaviors.
- Fixed timing order with three process-inclusive repetitions per arm; no random search or seed selection.
- 144/144 current local compilation targets, 1,393/1,393 axiom reports, and 67/67 substantive negative rejections. All 123 inherited non-audit modules are unchanged.

## Assumptions and exclusions

1. Fixed pure grammar and only three Boolean inputs. No arbitrary Lean/Python programs, effectful operations, concurrency semantics, quantifiers, or LLM generation.
2. Exhaustive eight-input behavior is exact here. Partial testing or approximate signatures do not inherit these equivalence guarantees.
3. Minimum preservation relies on congruent constructors and monotone additive node cost. It does not automatically hold for context-dependent cost, side effects, memory sharing, floating point, or other languages.
4. A 256-entry bound is not a peak-byte or AST-storage bound. Expanded lists, cached expressions, serialization, and transient allocation still consume memory.
5. The declared tariff omits general allocation/list costs, proof erasure/runtime behavior, operating-system time, parsing, IO, and memory management. No exact physical speedup or net-cost-optimal search theorem is claimed.
6. Preflight reservations are conservative. Returned depth can be less than requested even when a hindsight actual-cost run might fit. Query costs are separate from uncharged diagnostic queries in build/budget modes. Campaign mode checks and includes its selected query fee.
7. Exact full-depth optimum is relative to the bounded grammar plus the reference incumbent. Observing all 256 behaviors at depth 3 does not prove their retained representatives globally minimum over unrestricted programs.
8. The frozen comparator uses the same checking/indexing backend without feeding compacted output into the generator. This is an ablation, not proof of superiority over all synthesizers, BDDs, e-graphs, or the best target-specific search.
9. The measured timing sample is three runs per arm on one host, includes process startup/output, and is descriptive. No significant real research-productivity claim is made.
10. The new CLI is read-only/in-memory. It does not reload a durable semantic library, install source, update an earlier SQLite campaign, authorize retries, or prove persistent cache authenticity. Older durable machinery is preserved but its physical tests are not rerun here.
11. Candidate libraries improve later search state under a fixed supplied algorithm. No autonomous self-editing, improved proposer generation, general recursive self-improvement, or novel Boolean-identity discovery is established.
12. Lean kernel/compiler/Std, pinned cached mathlib, Python, serialization, and the host remain trusted. A source proof does not independently verify the executing machine.
13. Current local source is rebuilt and audited against cached external dependencies. External mathlib sources are not all rebuilt. Old versioned evidence remains historical.
14. Declaration counts include helper lemmas and examples. No historical novelty inference follows from the count.
