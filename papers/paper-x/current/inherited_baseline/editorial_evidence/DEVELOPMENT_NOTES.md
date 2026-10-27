# Development corrections and limitations

This file records editorial and tooling failures, not new mathematical theorem failures.
The successful designated runs are the records in this directory. Not every transient
draft source/log was retained.

1. The first graphics generator used ordinary Python strings for TeX. Running with
   warnings treated as errors rejected an invalid escape. TeX-containing literals were
   converted to raw strings, avoiding both invalid escapes and accidental control
   characters such as tabs, backspaces, or form feeds. The corrected generator passed.
2. Early TeX builds omitted the mathrsfs and bm packages. The missing commands were
   added through those packages. A negated implication was rewritten using existing
   math commands. An inline table caused a horizontal overflow; explicit paragraph
   separation fixed it. All final appendix box and reference checks are clean.
3. Review corrected a prose capacity-example typo: trace vector (5,3,2) recovers (3,0,1),
   not (3,0,2). The underlying exact model and its displayed table already used (3,0,1).
4. Review enlarged tiny residue nodes, removed an ambiguous decorative arrow, separated
   a precision-plate heading and a Mellin legend, and increased the body type to 12 pt.
   Every final appendix page was rendered and inspected; problem pages were checked at
   individual-page resolution.
5. One build correctly refused stale shipped TikZ after a generator edit. Regenerating
   the authoritative graphic sources and rebuilding produced exact source parity.
   That refused build is not counted as a pass.
6. Original figure recovery initially searched nested Block 27 baselines, which did not
   contain the graphics. The original July source release was then found in the Library;
   all original assets, tests and result records were recovered successfully.
7. The Block 27 amended manuscript had LaTeX but no matching PDF in the recovered
   formal archive. This edition newly typesets that unchanged source with the recovered
   figure files. The 50-page PDF is therefore not described as a preserved preexisting
   Block 27 PDF. Its independent rebuild matched this edition's initially compiled pages.
   One inherited underfull-box warning remains; no overfull or unresolved-reference
   warning occurred in the final manuscript rebuild.
8. The latest continuation retains an older README/replay script but is a source overlay:
   it adds 16 sources/objects to an unchanged 255-source predecessor. The new saved-evidence
   inspector verifies this relationship; it does not claim a standalone full Lean replay.

The appendix's 263 exact positive assertions and 14 deliberate false controls concern
stated finite models, symbolic identities and explicitly bounded calculations. The
infinite-limit, closedness and elementary Mellin discussions carry their prose reasoning;
finite plotting samples are not used as universal proofs. No new Lean build, general
Chebotarev result, attachment comparison, transport theorem, or occupancy theorem is claimed.
