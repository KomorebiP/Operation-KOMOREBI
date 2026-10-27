# PR-LASM 2.1.0 release audit

**Audit date:** 2026-08-18

**Project:** Projector-Resolved Large Algebraic Signal Model

**Author:** Komorebi P.

## Repository certificate

- The Git staging audit reports no whitespace errors.
- The repository contains 240 tracked files after this audit record is added.
- `environment_files/README.md` is the only tracked path beneath
  `environment_files/`.
- Runtime outputs, build products, virtual environments, downloaded ARC
  environment files, and common credential files are ignored.
- No obvious private-key, GitHub-token, OpenAI-key, or AWS access-key pattern
  was detected in the tracked text files.
- All Markdown-relative links and required release metadata pass the bundled
  repository checker.

## Automated verification

| Layer | Result |
|---|---:|
| Core tests from the clean public tree | 32 passed |
| Optional local-suite tests | 8 additional tests |
| Full suite after installing the separate 25-environment fixture archive | 40 passed |
| Controlled operator-family identifications | 7 of 7 |
| Controlled atlas identifications | 7 of 7 |
| Deterministic synthetic interactive systems solved | 4 of 4 |
| Median PR-LASM-to-linear state RMSE ratio | 0.2392934954 |

The exactness benchmark tested 24 frames. Its largest reported atlas
reconstruction residual was `2.4868995751603507e-14`, and its largest
mixed-depth best-basis reconstruction residual was
`1.9539925233402755e-14`.

## Packaging certificate

- The source archive contains one top-level `komorebi-pr-lasm/` directory.
- The public source archive contains no downloaded ARC environment source.
- The wheel contains both the stable `komorebi_pr_lasm` API and the retained
  `komorebi_arc3_offline` compatibility namespace.
- The wheel builds under Python 3.13 with no build isolation, installs into an
  isolated target, imports successfully, and reports version `2.1.0`.
- GitHub Actions covers Linux and Windows on Python 3.12 and 3.13.
- A tag-triggered workflow verifies the tag, reruns the core suite, builds the
  wheel and source distribution, generates checksums, and creates the GitHub
  release.

## Manuscript certificate

The canonical manuscript has 38 letter-sized pages, embedded fonts, an
outline, and no encryption. It was rendered successfully for visual
inspection. The PDF, LaTeX source, figure-generation code, and generated
figures are retained in `paper/`.

## Boundary of this audit

The 25 optional environment trees were checked as local fixtures and exercised
by the repository's integration tests. They were not committed to the public
source archive. This audit does not report an official ARC-AGI-3 benchmark
score and does not convert the finite controlled results into a claim of
universal induction, universal planner optimality, or general intelligence.
