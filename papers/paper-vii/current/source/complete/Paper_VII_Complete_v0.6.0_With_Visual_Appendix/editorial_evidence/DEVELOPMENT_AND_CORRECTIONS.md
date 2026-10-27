# Editorial development and corrections

No production Lean source or manuscript page was edited.

1. The original numerical companion was missing from the selected formal ZIP.
   It was recovered through Library metadata under `Projector_Seed_Calculus_VII_Release.zip`.
   Its original PDF is byte-identical to the formal checkpoint's original PDF.
2. The first numerical replay used unittest discovery on a pytest function suite.
   It found zero tests and failed; it was not counted as a pass. The correct pytest
   replay ran all 22 tests successfully. The failed log is retained.
3. Two original LaTeX passes left stale page numbers in the contents/list pages.
   A third pass reproduced all 25 source pages in text and rendered appearance.
   The initial comparison is retained separately from the successful report.
4. Initial TeX label literals in the new figure generator needed raw Python
   strings. The first `-W error` invocation rejected invalid escape sequences.
   The labels were repaired and the strict-warning invocation passed.
5. Two new tables were initially placed in the preceding paragraph, producing
   overfull boxes. Explicit paragraph boundaries fixed the table placement.
6. The seed-rank figure's narrow labels caused awkward hyphenation, then a small
   overlap after removing the fixed width. The labels were shortened and moved.
   The bit-address drawing was changed to an offset-cube layout so edges do not
   falsely run through intermediate vertices. The logical-error reference matrix
   displays a symbolic scalar c on both diagonals. Dispersion decimals are explicitly
   labeled approximate rather than appearing to be exact interval endpoints.
7. The final appendix was recompiled, inspected, and checked for zero overfull/
   underfull boxes, valid internal destinations, no raster images, and page preservation.

The exact-example results, original numerical regression, original TeX replay,
and recorded Lean evidence remain separate. None of the failed invocations is
represented as a successful proof or verification run.
