# Machine-Native Reasoning — Lean Block 11
## Selective certificate reuse and topological restoration

**Komorebi P. · Cumulative formal companion 0.11.0 · Reviewed Core 0.2 · 10 October 2026**

Core **7.1** joins the eighteen previous selected source results. The original book is unchanged. The current source map covers **19 of 27** statements. This is not a completed formalization of the book. Acceptance of this release requires completed `final11` and `fresh11` gates and their production-object comparison. Read the generated `evidence/RELEASE_RESULTS_BLOCK11.md` for actual completion, counts, times and exceptions.

The six new modules define exact changed-input propagation, prove semantic preservation outside its forward closure, and implement partial topological restoration with explicit missing/rejected/blocked/accepted outcomes. An old local PASS flag is not an established old claim. Direct dependencies are actual typed input restrictions, and their semantic completeness is a separate proved obligation. External premises are not inferred from checksums.

## Reproduce

```bash
python3 scripts/verify_release.py
python3 scripts/verify.py --runtime /absolute/path/Komorebi_Portable_Lean_4.34.0-rc2 --out evidence/my_replay
```

Check the frozen inventory before generating new evidence. Each full gate builds every local production module from source into an empty object directory, checks source-facing APIs, inventories actual elaborated declarations, audits transitive axioms, replays substantive modules with the same kernel, and runs all expected negative outcomes. Imported dependency objects and compiler artifacts are hash-checked against the retained runtime inventory. The runtime is not included.

## Mathematical route

`DependencyGraph` computes staleness by exactly as many propagation rounds as there are vertices and proves equality with forward reachability. `Revision` separates semantic locality, sound local verification, and prior establishment. `RevisionReplay` implements rank-layer checking, proves every exported witness sound at every intermediate stage, and proves complete restoration when the actual revised witnesses and premises are available. `RevisionAdmission` checks topological order and unchanged external assurances before copying witnesses. `RevisionExamples` proves this contract for the inherited eight-case diagnosis and universal-repair models. `RevisionControls` exposes omitted inputs, circular assurances, unavailable premises, and the difference between procedural failure and falsehood.

The actual example retains the checked arithmetic fact, rejects the obsolete singleton-counting scope, blocks its dependent general leaf bound, and separately rechecks controller validity and its exact profile. A one-record universal-repair controller can be validated, but it cannot inherit an old `(4,15)` profile target. Those are semantic facts about the same inherited `HardInquiry` model and controller types, not unrelated booleans in a graph.

The cumulative source currently contains **814 authored theorem declarations** within **1,252 authored declarations**, adding 74 and 130 respectively. There are **53 production modules**, 52 substantive, and **115 negative-control contracts**. These are source inventories, not independent discoveries. Actual elaborated counts and gate outcomes are recorded after execution.

## Boundaries

The dependency graph, local rules, model and proof obligations are declared. The example proves its own declaration complete. There is no inference of complete dependencies from arbitrary host code, no semantic hash injectivity, no physical validation of supplied premises, and no concurrent mutation during a replay. A changed rule, graph, witness schema or claim language needs its own new correspondence. Rank-layer replay assumes finite ranks; no claim of efficient replay or cost advantage is made. The result is same-kernel checking with pinned upstream caches, not independent peer review or an upstream source rebuild.
