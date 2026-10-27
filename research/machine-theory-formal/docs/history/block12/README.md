# Machine-Native Reasoning — Lean Block 12
## Resource prices, complete workloads, and accountable repricing

**Komorebi P. · Cumulative formal companion 0.12.0 · Reviewed Core 0.2 · 10 October 2026**

Core **7.3** joins nineteen preceding selected results. The source book is unchanged. The current admission map covers **20 of 27** results, not the complete book. Delivery as a checked release requires both terminated `final12` and `fresh12` gates and their comparison. Actual results and any exceptions are in `evidence/RELEASE_RESULTS_BLOCK12.md`, generated after execution.

Four new modules prove nonnegative-price robustness, attainment of a finite convex-hull minimum, explicit preparation and workload accounting, and a source-bound repricing example using the actual Block 10 compiler counters and the actual Block 11 replay. The same correct controller can be more expensive after repricing. A correct negative quotation and a nonnegative-benefit claim have different witnesses and dependency status.

## Reproduction

```bash
python3 scripts/verify_release.py
python3 scripts/verify.py --runtime /absolute/path/Komorebi_Portable_Lean_4.34.0-rc2 --out evidence/my_replay
```

Check the frozen inventory before generating new evidence. The full verifier builds every local production module into an empty directory, checks independent source-facing APIs, inspects the actual Lean environment, audits transitive axioms, replays every substantive module with `leanchecker`, and runs expected-rejection fixtures. The exact pinned runtime is external and is not distributed. It is Lean 4.34.0-rc2, mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

## Mathematical route

`ResourcePrices` treats the old-minus-new event vector as a signed real vector and its price as a finite linear sum. It proves the source's orthant duality and the exact minimum on Mathlib's actual convex hull, reusing the earlier finite-minimum constructor. `WorkloadPricing` connects this result to natural event totals, setup, workload multiplicities and strict amortization. `PriceExamples` binds the ledger to the unchanged full/streaming code: (184 reads,45 tests) versus (153 reads,198 tests). `PriceRevision` proves a complete dependency declaration and uses the unchanged replay to separate a still-valid controller, a stale quote, a corrected negative quote and a rejected benefit claim.

The isolated per-use saving at read price r and test price t is 31r-153t. At (5,1) it is 2, and at (1,1) it is -122. Over the convex hull of (5,1) and (8,1), the exact minimum is 2. An explicitly hypothetical extra setup of 200 test units gives the full-workload minimum 2N-200 and strict uniform improvement exactly when N>100. This setup is an illustrative charge, not a measurement of the real discovery or admission procedure.

The current authored source has 882 theorem declarations within 1,352 declarations, adding 68 and 100 respectively. There are 57 production modules, 56 substantive, and 127 negative-control contracts. These are proof-code inventories, not counts of discoveries. Actual elaborated constants and axiom totals are reported only after the gates run.

## Boundaries

One common additive price map applies to both routes in a comparison. Independently changing per-use prices requires an expanded ledger, not cancellation before pricing. Preparation, acquisition, checking, dispatch, retained storage, peak memory and wall time are not inferred from two instrumented counters. Coordinate changes require compensating prices. Complete model/event declarations, semantic fidelity and external validity remain separate obligations.

The generic real minimum is a mathematical construction, not an efficient finite-precision optimizer. No probability experiment, neural training, measured speedup, verified host execution, upstream dependency rebuild, independent proof kernel, Windows run or hosted change is claimed. All 52 predecessor substantive modules remain byte-identical.
