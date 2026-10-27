# Paper X final package

## Article

**Title:** *Residual Deformation Forests, Companion Systems, and Module Support*

**Author:** Komorebi P.

The package contains the final Annals style manuscript, its complete LaTeX and BibTeX source, fourteen vector figures, deterministic verification, the original Paper X release, and the audit records used during the rewrite.

## Main files

1. `PSC_Paper_X_Strengthened_Annals_Edition.pdf`
2. `PSC_Paper_X_Strengthened_Annals_Edition.tex`
3. `PSC_Paper_X_Strengthened_Annals_Edition.bib`
4. `THEOREM_REGISTER.md`
5. `MIGRATION_AND_EXPANSION_MAP.md`
6. `DEEP_AUDIT.md`
7. `PROOF_AUDIT.md`
8. `LANGUAGE_AND_FORMAT_AUDIT.md`
9. `BUILD_AUDIT.md`
10. `SUBMISSION_CHECKLIST.md`
11. `AI_CONTRIBUTION_DISCLOSURE.md`
12. `SOURCE_AUDIT.json`
13. `MANIFEST.sha256`

## Directories

### `figures`

Contains the figure generation script and fourteen vector PDF figures.

### `verification`

Contains the deterministic verifier, the verification summary, and build comparison records.

### `legacy`

Contains the original Paper X source, PDF, claim map, verification notes, and finite result files. These files preserve provenance and are not part of the journal article.

## Build

A standard build uses

```text
pdflatex PSC_Paper_X_Strengthened_Annals_Edition.tex
bibtex PSC_Paper_X_Strengthened_Annals_Edition
pdflatex PSC_Paper_X_Strengthened_Annals_Edition.tex
pdflatex PSC_Paper_X_Strengthened_Annals_Edition.tex
```

The installed environment used `bibtex.original` because its ordinary `bibtex` link was broken. This is an environment issue rather than a source requirement.

## Verification

The final deterministic suite reports

```text
Paper X verification: 102741/102741 checks passed in 12 groups
```

The checks cover residual fibers, lift forests, singular level counts, cohomology packets, obstruction classes, source components, Frobenius separation, Fitting support, finite occupancy, infinite occupancy, legacy certificates, and package integrity.

## Scope

The manuscript proves conditional completion once local companion branches, one common arithmetic spine, and an occupied carrier component have been supplied. It does not prove universal residual companion existence, universal global occupancy, automorphy, or unrestricted reciprocity.

Internal completion and finite verification do not replace independent specialist review or historical priority analysis.
