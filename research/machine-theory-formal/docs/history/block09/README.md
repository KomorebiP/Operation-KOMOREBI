# Machine-Native Reasoning — Lean Block 09
## Finite synthesis and evidence-preserving semantic compression

**Komorebi P. · Cumulative formal companion 0.9.0 · Reviewed Core 0.2 · 10 October 2026**

Core **6.1** and **6.2** join fifteen earlier source results. The source book remains unchanged. Current coverage is **17 of 27** selected source statements, conditional on the completed current-source receipts in `evidence/final09`, `evidence/fresh09`, and `evidence/FRESH_REBUILD_BLOCK09.json`. Their post-execution summary is `evidence/RELEASE_RESULTS_BLOCK09.md`. Older passing receipts apply only to their own source bytes.

The six new modules construct a finite teacher and persistent-example learner, prove the scan realizes the restart-earliest protocol, permit arbitrary truthful replies in the general call bound, preserve exact traces under a sound ordered quotient, support explicit suspension/resumption, and check a small arithmetic example and failure boundaries.

The authored source inventory is **669 theorem declarations** within **1,014 authored declarations**. This adds 78 supporting theorem declarations for two manuscript results, not 78 discoveries. Production comprises 42 modules, 41 substantive, with 91 negative-control contracts. Actual elaborated counts and execution times belong to the terminated receipts.

### Run the checks

```bash
python3 scripts/verify_release.py
python3 scripts/verify.py --runtime /absolute/path/Komorebi_Portable_Lean_4.34.0-rc2 --out evidence/my_replay
```

Check the frozen inventory before creating new evidence. The driver refuses nonempty output directories. It builds every local production module from source into empty local objects, checks source-facing APIs, audits actual transitive axioms, replays substantive modules with `leanchecker`, tests deliberate failures, and checks imported caches against the saved runtime manifest. Warnings are errors. Only `propext`, `Classical.choice`, and `Quot.sound` are allowed.

### Read in dependency order

`docs/BLOCK09_PROOF_GUIDE.md` follows the mathematics. `docs/ASSUMPTION_REVIEW_BLOCK09.md` records its scope. `docs/THEOREM_MAP.md` binds all 27 source results, including the ten still outside formal coverage. `REVIEW_NOTES.md` records authoring failures and the exact assurance boundary. `PROGRESS_LEDGER.md` specifies the next restart.

The arithmetic example uses eight supplied expression candidates and three declared contexts. Both learners make four teacher calls, receive the same three counterexamples, and return the identical original expression. Retained-example comparisons are nine versus six. The unchanged teacher performs nine comparisons on either side. Building the simple list-backed index adds ten key-equality comparisons, with key computation, storage and dispatch still separate. No universal speedup is claimed.

The normalizer and semantics are supplied; their one-way soundness is proved, not learned from the three contexts. A finite fit does not justify deleting solutions outside the declared semantic domain. The result does not discover a general language, supply a physical model, or establish open-ended self-improvement.

The predecessor's 35 substantive source modules remain byte-identical. No runtime, standalone font, third-party full paper, or private conversation is distributed. Same-kernel replay is not an independent verifier, upstream source rebuild, or external peer review.
