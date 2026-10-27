# Paper IX local polyphase Annals edition

## Article

**Title:** Local Arithmetic Packet Calculus for Euler Families, Mahler Transfer, and Polyphase Refinement

**Author:** Komorebi P.

The final article has 52 pages, 184 abstract words, 82 internally proved results, 82 proof environments, 111 numbered mathematical records, 14 referenced vector figures, and 22 cited bibliography entries.

## Primary files

- `PSC_Paper_IX_Local_Polyphase_Annals_Edition.pdf`
- `PSC_Paper_IX_Local_Polyphase_Annals_Edition.tex`
- `PSC_Paper_IX_Local_Polyphase_Annals_Edition.bib`

## Package layout

- `figures/` contains the vector figures used by the article
- `verification/` contains the final verifier, baseline verifier, and figure generators
- `source_extension/` preserves the two selected source modules from the uploaded sequence extension and its independent verification
- `legacy/` preserves the previous Paper IX source, PDF, claim map, and arithmetic tables
- the Markdown audit files record migration, proofs, language, build, and submission status

## Build

```text
pdflatex -interaction=nonstopmode -halt-on-error PSC_Paper_IX_Local_Polyphase_Annals_Edition.tex
/usr/bin/bibtex.original PSC_Paper_IX_Local_Polyphase_Annals_Edition
pdflatex -interaction=nonstopmode -halt-on-error PSC_Paper_IX_Local_Polyphase_Annals_Edition.tex
pdflatex -interaction=nonstopmode -halt-on-error PSC_Paper_IX_Local_Polyphase_Annals_Edition.tex
```

## Verification

```text
python verification/verify_paper_ix_unified.py
python source_extension/verify_sequences.py
```

The final verifier performs 12,240,335 checks. The selected extension verifier independently performs 87,915 checks. Finite checks support the formulas and implementation but do not replace general proofs.
