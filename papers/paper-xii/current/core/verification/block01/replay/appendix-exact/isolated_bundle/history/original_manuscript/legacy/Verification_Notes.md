# Verification Notes

## Artifact

**Projector-Resolved Seed Calculus XII: Global Seed Completion — Adequate Projectors, Automorphy Lifting, and Final Occupancy**

**Author:** Komorebi P.

## Mathematical and numerical checks

- Automated tests: **34 passed**.
- All finite adequacy calculations use exact arithmetic over `F7`.
- Primary projector calculations use exact symbolic rational arithmetic.
- Group-algebra, compatible-system, and dyadic calculations use exact integer, modular, or symbolic arithmetic.
- Floating-point calculations are confined to figure rendering and finite diagnostic norms.
- All calculations in the release are CPU-based. No GPU result is claimed.

Representative certificates:

| Certificate | Result |
|---|---:|
| Primary projector reconstruction | exact |
| Primary ranks | `(2, 1, 2)` |
| Primary denominators | `(9, 144, 16)` |
| `S3/F7` adequacy | pass |
| `H^1(S3, ad0)` dimension | `0` |
| detected irreducible adjoint packets | `2` |
| odd Taylor-Wiles tower | pass |
| dyadic Taylor-Wiles tower | pass |
| finite occupancy rank sequence | `(7, 4, 3, 2, 1, 1)` |
| inconsistent packet rank | `0` |
| infinite tail intersection dimension | `0` |
| compatible-carrier multiplicities | `(2, 0, 1)` |
| dyadic first separation depth | `2` |

## LaTeX build

- Engine: `pdflatex` through `latexmk`.
- Build mode: `-interaction=nonstopmode -halt-on-error`.
- Final length: **27 pages**.
- Undefined references: none.
- Multiply defined labels: none.
- Overfull boxes: none.
- Underfull boxes: none.
- Paper-local citation commands: none.
- Paper-local bibliography environment: none.

## Figures

- Python-generated figures: **17**.
- Every figure is supplied as PNG and vector PDF.
- `Figure_Contact_Sheet.png` audits the complete figure set.
- `Verification_Render.png` audits all 27 rendered paper pages.
- PNG ancillary metadata was removed by rewriting from pixel data.
- Vector-PDF metadata was rewritten to title, subject, and `Komorebi P.` only.

## PDF metadata

The final paper retains only:

- Title: `Projector-Resolved Seed Calculus XII`
- Subject: `Global seed completion, adequate generalized-eigenspace projectors, Taylor-Wiles packet refinement, R equals T, compatible systems, and final Hecke occupancy`
- Author: `Komorebi P.`

Creator, producer, date, custom metadata, and XMP streams are absent.

## Python package and wheel

- Wheel: `projector_seed_global_completion-1.0.0-py3-none-any.whl`.
- Built with `pip wheel --no-deps --no-build-isolation`.
- Tested by installing into an isolated target directory.
- Import resolved to the installed wheel copy rather than the source directory.
- The installed package reproduced the adequacy verdict and final occupancy rank.

## Archive policy

The complete release archive contains the final PDF, LaTeX source, code, tests, figures, results, tables, wheel, and audit documents.

The source-focused archive omits the compiled main paper and large render audit while retaining all material needed to rerun the finite study and rebuild the PDF.

Archive timestamps are normalized, and a SHA-256 ledger is supplied outside the archives.

Final extraction checks:

- complete release: **103/103** internal SHA-256 entries verified, **34/34** tests passed, final PDF retained 27 pages and 20 hyperlink annotations;
- source-focused release: **77/77** internal SHA-256 entries verified, **34/34** tests passed, all 17 figure pairs regenerated, metadata normalized, and the paper rebuilt successfully to 27 pages.

## Claim boundary

The release proves finite packet theorems and a conditional global implication. It imports the standard automorphy-lifting and patching machinery. It does not claim universal companion existence, universal positive Hecke occupancy, a coefficient-prime-two replacement theorem in full generality, or unrestricted global Langlands reciprocity.
