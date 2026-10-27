# Block 06 — source changes and mathematical boundary

## Exact scope

The original reader baseline contains 1,001 files. Of those, 988 are unchanged. Thirteen existing files were edited and three new `reader_route.tex` files were added. `SOURCE_PRESERVATION.json` contains every preserved path and both hashes for each changed file. `SOURCE_CHANGES.patch` records the exact textual differences.

The edited files are the three top-level reader wrappers, three publication styles, three build entry points, three reader READMEs, and one appendix file. The new files provide separate navigation and scope pages. The source catalogues and every selected `.lean` file are unchanged.

## Appendix D: a missing factor, not a new theorem

The inherited converted appendix contained:

```tex
dimension \href{n−n/p}{k:F\_p}. For k=F\_p, it has dimension n−n/p.~This
```

A Markdown-style dimension expression had been parsed as a link. As a result, the PDF printed only `k:F_p` at the first dimension claim and attempted to open a nonexistent `n−n/p.pdf` file.

The raw source actually says:

```text
For general k, this is a nondegenerate alternating F_p-form of dimension [k:F_p](n−n/p). For k=F_p, it has dimension n−n/p. This proves the theorem.
```

The synchronized appendix now uses:

```tex
dimension \([k:\FF_p](n-n/p)\). For \(k=\FF_p\), it has dimension \(n-n/p\). This
```

The raw note was recovered directly from the verified complete Block 01 archive. Its SHA-256 is `b1e8b64c032e43c4c8e2343493935b4f151dc7e7b2318602b593cf2501d0f5b4`; its exact archive path is in `raw_sources/SOURCE_ORIGIN.txt`. The note itself is unchanged and included in this checkpoint.

The bounded regression checks the elementary cardinality identity `(p^f)^m = p^(fm)` in the displayed dimensions and keeps a negative control for dropping the factor. That check does not reprove the arithmetic leading-layer construction. The repair restores what the original source already stated.

## What was preserved

All 68 explicit main-manuscript `proof` environments remain byte-identical. All 105 main statement-environment bodies remain byte-identical: 14 theorems, 37 propositions, one lemma, 16 corollaries, 13 definitions, seven examples, eight standard facts, eight remarks and one conjecture. These are typesetting-structure counts, not counts of independent new mathematical discoveries.

Fourteen of fifteen appendix TeX files are identical. The fifteenth differs only by the exact correction above. Thus a blanket claim that every appendix byte was preserved would be false.

The 423 selected Lean source modules and 40 teaching excerpts retain their hashes. The 4,342 named lexical declaration records retain their original catalogue; every name was checked in the extracted text of the rebuilt Lean guide. Reversible display escapes in excerpts remain reversible. No theorem binder or formal source was edited.

## Claims and navigation

The revised front matter keeps three separate tasks: finite comparison, actual realization, and H5 for the same realized candidate. Historical obligation 66, historical Theorem 16.2 and all-records row 95 denote the endpoint's lineage; historical register row 66 is a different statement. The 66-row table in the Lean guide now links into the current monograph, without treating a navigation link as a theorem-equivalence certificate.

The corrected full character's scalar test is not occurrence. The actual source-defined and directly type-defined candidates are not identified by notation. The stronger independently prescribed native marking is not added as a premise to the valid transported-marking contract. These distinctions are explained in the current reading routes and point to the separate progress paper and atlas.

The appendix convention note distinguishes Swan conductor, ordinary Artin conductor and a specified additive-character epsilon exponent. It does not retroactively alter a preserved historical construction note or claim a new classical-source audit.

## Publication repairs

The traditional reader's contents page had overlapping section numbers and titles. The AMS/titlesec TOC interaction was corrected, and excess paragraph spacing was removed from contents lists. The visual and Lean build drivers originally omitted the shared publication style. The old monograph wrapper referred to unbundled local font paths. The coordinated builder now stages every include, resolves installed fonts without distributing them, and binds assembly to actual compilation receipts.

A Lean chapter heading overflow was corrected with ragged-right heading layout. The original obligation table's narrow title column now wraps cleanly. Historical reports in source folders remain unchanged and are labeled historical; their old page counts are not the new build's page counts.
