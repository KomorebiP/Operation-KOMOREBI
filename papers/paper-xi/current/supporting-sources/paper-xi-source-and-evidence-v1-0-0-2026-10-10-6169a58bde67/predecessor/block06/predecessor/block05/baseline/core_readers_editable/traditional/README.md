# Paper XI: traditional final edition

**Tame and Wild Packet Geometry for Local Langlands**  
Komorebi P. · October 6, 2026

`Paper_XI_Traditional_Final.pdf` is the standalone traditional paper.
`Paper_XI_Traditional_Final.tex`, its bibliography, the fifteen construction
appendices, the original vector figures, and the licensed bundled fonts are
the editable source.

The general arithmetic realization endpoint is **Conjecture 66**. It isolates
the missing realization step from historical Theorem 16.2, which was proof
obligation 66 and row 95 in the historical all-records register. The paper
separately proves the comparison of one actual realized candidate under H5
for that same candidate and the applicable local-factor characterization.
Blocks 166 and 167 contribute detailed ordinary proofs within their displayed
restricted arithmetic and marked assembly scope. No new Lean certificate for
these arithmetic constructions or Conjecture 66 is claimed.

The accompanying release includes Markdown (.md) files containing detailed
proofs, construction notes, proof audits, and research records. These distinguish
established results, conditional results, and the remaining obligations
associated with Conjecture 66. The source-level construction references in
the appendices point to those retained records.

## Rebuild

Use Python 3 and a TeX installation providing XeLaTeX, BibTeX, AMS article,
fontspec, geometry, microtype, mathtools, bm, aliascnt, enumitem, graphicx,
booktabs, longtable, cleveref, hyperref, xurl, newunicodechar, and fvextra.
The fonts needed by this edition are included with their licenses.

```sh
python build.py --output-dir ./rebuilt
```

The command writes the PDF and final compiler log into the requested directory.
Add `--keep-build` to retain individual compiler passes and intermediate files.
Building uses the existing editable LaTeX and does not require Pandoc, network
access, the historical archives, or the manuscript preparation script.
The preparation script records the original conversion workflow and is not
needed for normal rebuilding.

The PDF creation date and trailer identifier are fixed for reproducible builds.
Root-level release checks independently validate the portable builder.

## Editorial corrections and scope

- The former general endpoint and its unsupported “resulting atom” proof are
  replaced by the conjecture and the explicit same-candidate conditional
  proposition.
- The tame-projector proof now consistently uses geometric Frobenius:
  `Phi^-1 t Phi = t^q`. Equivalently, conjugation by `Phi` raises `t` to the
  inverse of `q` modulo the tame quotient order. The displayed projector law
  `Phi P_j Phi^-1 = P_(qj)` is unchanged and agrees with the retained Lean
  covariance theorem.
- All other original mathematical environment blocks are preserved verbatim.
  Full current construction proofs are added, rather than substituted for the
  historical finite theory.
- The low-rank enlarged dyadic pairs are arithmetic assembly carriers. They
  are not renamed as the original maximal-simple-character quotients.
  Independently prescribed native markings, nontrivial symplectic actions,
  general transports, and any required numerical layer placement retain their
  separate obligations.

The full source-preservation and rendering reports are in the release audit.
