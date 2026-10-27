# Machine-Native Reasoning — Lean Block 15

## A quotient that preserves legal operations

**Komorebi P. · Cumulative formal companion 0.15.0 · Reviewed Core 0.2 · 15 October 2026 UTC**

Core **8.2** joins the twenty-two preceding selected results. The admission map covers **23 of 27** selected source results. The reviewed source book and all **60 predecessor substantive modules** remain unchanged. Release assurance requires the two completed current-source cold gates and their strict production-object comparison, recorded in `evidence/RELEASE_RESULTS_BLOCK15.md`.

For a surjective state projection, quotient labels, enabled sets and legal successors exist exactly when equal fibres agree on those three pieces of operational data. The construction chooses representatives and proves independence from that choice. Canonical partial transitions make disabled actions explicit; the source's supplied enabled sets and dependent legal successors translate exactly to this representation. The actual partial quotient data are unique.

For every finite action word, execution commutes with projection. Legality is preserved and reflected, and the complete protected-label sequence includes the initial state and all intermediate states. Exact examples show why identical sensor labels do not justify merging different repair permissions, and why quotient uniqueness does not extend to unattained states or arbitrary disabled-action defaults.

## Reading and reproduction

Start with `docs/BLOCK15_PROOF_GUIDE.md`, `docs/ASSUMPTION_REVIEW_BLOCK15.md`, `docs/THEOREM_MAP.md` and the release results. The persistent ledger tracks the four remaining selected results: Core 2.4, 2.5, 3.2 and 8.3.

Check the delivered payload before generating new evidence:

```bash
python3 scripts/verify_release.py
```

With a compatible preserved runtime at the chosen path:

```bash
LD_PRELOAD=/absolute/runtime/compat/app_path.so python3 scripts/verify.py --runtime /absolute/runtime --out evidence/my_replay
```

See `docs/RUNTIME.md` and `evidence/runtime15/recovery.json` for the recovered runtime layout, compiler and dependency identities, failures and limits. The owned facade reuses an unchanged existing toolchain and package cache, with matching adapter and inventory copies. The runtime is external to this package.

The verifier compiles **64 production modules**, replays **63 substantive modules**, checks the source-facing APIs, inspects actual transitive axioms and exercises **152 negative-control contracts**. Actual declaration counts and execution outcomes come from the completed receipts. Supporting lemmas and examples are not additional source results or discoveries.

The complete original Block 14 archive is retained byte-identically under `evidence/history/block14`, including every earlier historical evidence file. Current sources and Block 15 evidence are directly accessible. All 8,258 prior payload hashes were checked before source extraction. This layout avoids duplicating historical proof objects in the current directory tree.

## Scope

Encoded permissions are mathematical application data. This theorem does not establish external moral or legal authority, authenticate a command, or deploy an access-control system. Same-kernel replay is not independent peer review, an independent kernel, or an upstream source rebuild. Core 8.3 is next; the selected-result tally is not a complete-book claim or an estimate of remaining effort.
