# Machine-Native Reasoning — Lean Block 10
## Capacity-prefix exclusion and the ordered diagnostic compiler

**Komorebi P. · Cumulative companion 0.10.0 · Reviewed Core 0.2 · 10 October 2026**

Core **6.4** joins seventeen preceding source results. The manuscript is unchanged. The cumulative map covers **18 of 27** selected statements, not 100% of the book or the machine program. Release acceptance requires the terminated current-source `final10` and `fresh10` receipts and `FRESH_REBUILD_BLOCK10.json`. The post-execution summary is `evidence/RELEASE_RESULTS_BLOCK10.md`.

Five new modules prove the numerical completion iff, implement full and streaming scans, construct an ordered depth-first compiler using the inherited `Tree` and `Valid`, prove literal answer preservation and nonincreasing report reads, establish correctness and finite-depth completeness, and supply an explicit scope/menu/no-duplicate admission gate.

There are 740 authored theorem declarations within 1122 authored declarations, including 71 new supporting theorems. Production comprises 47 modules, 46 substantive, with 103 negative-control contracts. These are proof-code inventories, not additional mathematical discoveries. Actual elaborated counts and execution results are in the terminated receipts.

## Reproduce

```bash
python3 scripts/verify_release.py
python3 scripts/verify.py --runtime /absolute/path/Komorebi_Portable_Lean_4.34.0-rc2 --out evidence/my_replay
```

Check the frozen inventory before creating new evidence. The gate cold-builds all local modules, restates APIs, audits transitive axioms, replays local modules with the same Lean kernel, checks all intended rejection outcomes and verifies imported-object hashes. The pinned runtime is supplied separately, not redistributed. No network or external account is used.

## The mathematical progression

`PrefixScan` proves the source integer statement and the literal scan's success/output and cost properties. `OrderedCompiler` composes those properties through actual left-before-right recursive calls and ordered backtracking. `PrefixSemantics` derives capacity necessity from the earlier binary leaf bound and connects search to actual model validity. `PrefixAdmission` separates scope rejection from completed failure and connects failure to the unchanged Pareto recurrence. `PrefixExamples` supplies exact examples and the independent authorization of Block09's acquired expression.

For the eight-case example, full versus streaming compilation uses **184 versus 153 report-table reads** and **45 versus 198 capacity tests**. Both return the same literal controller with online work4 and15 installed records. Equal prices make the combined counter total worse by122 units. A declared read price of5 and test price1 gives a saving of2 units in those coordinates only. Scope checks, permissions, terminal checking, allocation and host execution are not included in these counters.

The compiler is a new source-faithful formal reference built on the unchanged controller semantics. It is not a claim that the older 3,960-expression Python study or its historical timing/counter tables were rerun. Finding a formula, certifying its meaning, and rechecking its deployment scope remain different achievements.

All41 predecessor substantive source modules are unchanged. The same-kernel replays reuse the pinned dependency cache, not an independently built kernel or upstream source rebuild. There is no claim of physical-model accuracy, efficient general synthesis, host-cost refinement, neural training or independent peer review.
