# Realization Calculus

## A twin-volume edition by Komorebi P.

This edition pairs two independently readable monographs around one question: which data and admissible operations determine a mathematical realization?

- **Volume I — Komorebi Space:** *Coherent Realizations, Obstructions, and Descent*. It develops coherent families, extension obstructions, transport, symmetry, descent, and quantitative repair.
- **Volume II — Realization Boundaries:** *Finite Grammar, Infinite Groups, and the Limits of Reconstruction*. It classifies a family of countable abelian groups with one common profinite completion and measures the information retained by their algebraic and effective presentations.

The volumes have matched presentation, shared introductory material, and a cross-volume reading route. Their mathematical numbering remains independent. The pairing does not assert one universal realization space or an object outside every possible system of views. The grammar escape theorem is relative to a fixed countable grammar and its semantics.

## Read the books

![The paired monograph covers](books/Twin_Volume_Covers.png)

- [Volume I: Komorebi Space](books/Realization_Calculus_Volume_I_Komorebi_Space.pdf)
- [Volume II: Realization Boundaries](books/Realization_Calculus_Volume_II_Realization_Boundaries.pdf)

The shared opening pages explain the relation between compatible ambient data and an intended source image. Begin with Volume I for the realization framework, or Volume II for the common-completion group construction.

## Package map

| Path | Contents |
|---|---|
| `books/` | The two paired-edition PDFs |
| `publication/volume_i/source/` | Paired Volume I TeX source |
| `publication/volume_ii/manuscript/` | Paired Volume II TeX source |
| `publication/shared/` | Shared editorial material |
| `companions/komorebi-space-v1.15.0/` | Original accepted Komorebi Space publication package |
| `companions/realization-boundaries-v1.0.0/` | Original accepted Realization Boundaries GitHub source package |
| `supplements/komorebi-space-worked-proofs-v4/` | Later worked-proofs supplement, retained separately |
| `evidence/space-technical-current/` | Selected current Komorebi Space process records, reviews, and logs |
| `verification/` | Input provenance, identity comparisons, and paired-edition quality checks |
| `tools/` | Book build and integrity verification scripts |

The separately preserved [full Komorebi Space Technical Record](https://chatgpt.com/library?file_id=libfile_983f36b8fa6c8191bd5e2a685743657b&account_id=personal) has SHA-256 `2cc2a0291669781e3c5bb6608cc4f3c86cce513ec686c2b17031d35278d353db`. Its complete historical payload is not duplicated here.

## Formal scope and verification

Volume I retains the accepted Komorebi Space v1.15.0 development: 162 production modules, four import entrypoints, and formal counterparts for all sixteen principal theorem groups. This scope does not assign a separate Lean theorem to every illustration or every printed proof route.

Volume II retains the accepted Realization Boundaries v1.0.0 development: 66 production modules and all forty-five registered contracts complete. Its effective statements use explicit oracle and presentation semantics.

This editorial pairing is **not a new joint Lean replay**. The accepted proof records remain attached to their original developments. See [PROOF_AND_TEXT_IDENTITY.json](verification/PROOF_AND_TEXT_IDENTITY.json) for source and mathematical-text comparisons, [INPUT_SOURCE_AUDIT.json](verification/INPUT_SOURCE_AUDIT.json) for input provenance, and [TWIN_EDITION_QA.json](verification/TWIN_EDITION_QA.json) for checks on the paired publication. Each formal appendix states its own dependency and trust boundary.

## Rebuild and inspect

Run from the package root:

```sh
python3 tools/verify_integrity.py
python3 tools/build_twin_volumes.py
```

Check integrity before rebuilding. A rebuild can change PDF metadata and therefore its checksum. Book production requires Python 3 and a TeX installation providing `latexmk` and the packages declared in the sources. For Lean reproduction, follow each companion's own pinned-toolchain instructions and accepted audit records. The publication build does not rerun Lean.

## Reuse and citation

The two works retain distinct reuse terms. Komorebi Space has no new public license grant in its accepted edition; Realization Boundaries retains its MIT license. This package does not relicense either work. See [REUSE.md](REUSE.md) and the preserved companion notices.

Citation metadata is in [CITATION.cff](CITATION.cff). The twin edition is version 1.0.0, dated 24 October 2026. See [EDITORIAL_CHANGES.md](EDITORIAL_CHANGES.md) for its scope and rebuilding history.
