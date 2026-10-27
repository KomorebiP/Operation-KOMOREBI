# Machine-Native Reasoning — Lean Block 08
## Binary diagnosis and checked optimality closure

**Komorebi P. · Cumulative formal companion 0.8.0 · Reviewed Core 0.2 · 10 October 2026**

Core **5.3** joins the fourteen preceding formalized results. The new proof uses the unchanged hard-inquiry model and literal trees, deriving leaf counts from actual immutable transitions and singleton repair success. Work includes the final repair. Complete records include redundant unary nodes.

The source contains **591 authored theorem declarations** and **894 authored declarations overall** supporting **15 of 27** selected manuscript results. These are proof-code inventories, not 591 discoveries. Actual completed compiler and axiom inventories are in `evidence/RELEASE_RESULTS_BLOCK08.md` and the current run receipts.

### New modules

- `BinaryStructure`: actual depth, terminal occurrences, binary capacity, exact unary-node accounting.
- `BinaryDiagnosis`: model-derived case/leaf correspondence, work/storage lower bounds and existing-frontier closure.
- `BinaryExecution`: actual execution attaining the scalar worst-case work and its information bound.
- `BinaryCertificate`: finite scope and candidate checks, complete admission and exact budget characterization.
- `BinaryExamples`: eight-case source controller, one-bound near misses, invalid leaves, reset/universal-repair boundaries, constant-report impossibility and edge cases.

The eight-case balanced controller certifies `(4 online units, 15 records)` for every horizon at least three. The same model's equality-first controller costs `(8,15)` and is not an optimality certificate. A three-case controller with a redundant unary query costs `(3,6)` rather than `(3,5)`, showing that minimum work alone is insufficient.

### Reproduce

```bash
python3 scripts/verify_release.py
python3 scripts/verify.py --runtime /absolute/path/Komorebi_Portable_Lean_4.34.0-rc2 --out evidence/my_replay
```

Verify the frozen checksum inventory before generating new evidence. The driver refuses nonempty output directories. It builds **36 production modules**, replays **35 substantive modules**, checks source-facing APIs and transitive axioms, and checks **79 expected negative outcomes**. Only `propext`, `Classical.choice`, and `Quot.sound` are admitted. No placeholder or external proof shortcut is allowed.

Read `docs/BLOCK08_PROOF_GUIDE.md`, `docs/ASSUMPTION_REVIEW_BLOCK08.md`, `docs/THEOREM_MAP.md`, `REVIEW_NOTES.md`, and `PROGRESS_LEDGER.md`. Completed current evidence belongs to `evidence/final08`, `evidence/fresh08`, and `evidence/FRESH_REBUILD_BLOCK08.json`. Earlier receipts are historical and have their own source scope.

No runtime or standalone font is redistributed. No upstream dependency rebuild, independent kernel, physical sensor validation, empirical learning result, efficient synthesis algorithm, processor-time speedup, or host-memory-byte optimum is claimed. The source book remains unchanged.
