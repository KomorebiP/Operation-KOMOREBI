# Komorebi Representation Calculus v0.1

A task-indexed, proof-carrying architecture proposal with written propositions and exact finite reference audits.

Start with `FORMAL_NOTE.md`. Run:

```sh
python tools/run_audit.py
python tools/validate_manifest.py COMPUTATION_MANIFEST.json --root .
```

Python 3.10+ and the standard library suffice. The retained execution used the Python version recorded in the manifest. No downloads are needed by these commands.

`results/AUDIT.json` records all finite ranges and outcomes. The finite system uses all 64 admissible states, not a single initial-state orbit. The modulo-64 predicate search rediscovers the known Block15 relation from independently generated transition matrices; it is not a new all-precision classification or a learned discovery benchmark.

No Lean build was run in this branch. It does not supersede or modify any p-adic release, and it does not contain the complete p-adic corpus. The two Block15 source notes are preserved only as provenance anchors. `REVIEW.md` records a separate self-review of the written mathematics. `SOURCES.md` identifies inspected project content and primary public sources.
