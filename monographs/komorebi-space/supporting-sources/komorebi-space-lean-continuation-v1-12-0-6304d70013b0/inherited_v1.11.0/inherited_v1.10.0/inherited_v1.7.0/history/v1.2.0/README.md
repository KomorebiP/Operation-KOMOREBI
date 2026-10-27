# Komorebi Space
## Coherent realizations, obstructions, and descent

**Integrated monograph edition 1.2.0 · Komorebi P. · 11 October 2026**

The reader set comprises the monograph, an eighteen-plate visual guide, and a Lean/evidence guide under `publication/`. Editable sources and figure programs are included.

This edition assembles a canonical 138-module Lean source closure with one root, includes the previously separate Hilbert holonomy source, and formalizes the five previously written-only principal items KS54–KS58. Their five modules add 54 explicit named theorems/lemmas and 17 indexed constructions. The entire canonical production library has 1,507 explicit named theorem/lemma declarations. Supporting lemmas and standard constructions are included in these counts; they are not counts of discoveries.

The accepted clean replay, current project-declaration axiom audit, tests, and exact source binding are identified by `audit/formal/release.json`. Historical archives remain unchanged. A failed development or regression attempt is not promoted to a successful release record.

## Start here

- `publication/`: the three final PDFs.
- `formal/`: canonical Lean project, pinned dependency manifest, offline verifier, and tests.
- `data/claim_ledger.json`: all 58 principal exposition items and their exact source correspondence.
- `audit/formal/release.json`: accepted current formal evidence and scope.
- `PROGRESS_LEDGER.md` and `REVIEW_NOTES.md`: completion record, failures, boundaries, and restart instructions.

## Verify and reproduce

```bash
python3 checks/verify_payload.py
python3 formal/scripts/verify.py --runtime /path/to/portable-runtime --label independent1
bash build.sh
```

Run payload verification before making changes. The formal replay requires the pinned Linux portable runtime and mathlib cache, which are not bundled. Choose a new replay label so delivered evidence is not overwritten. The publication build consumes the accepted formal source binding and reruns its own finite checks, figures, and PDF builds. It does not secretly perform another Lean build.

See `BUILD.md` and `formal/README.md` for precise instructions. Local compiler caches are intentionally omitted from the distribution. Original source and evidence archives remain under `evidence/archives/`. Prior publication sources, audits, and ledgers are preserved under `history/`.

## Scope

All five previously identified principal formalization gaps are closed in the stated source closure. This is not a proof of an unrestricted universal view doctrine, an infinity-stack theory, semantic essential surjectivity for arbitrary arithmetic or physical objects, or universal correctness/optimality of the Python solver. Explanatory examples are not all separately formalized. The compiler, kernel, standard axioms, and pinned imported caches remain trusted.
