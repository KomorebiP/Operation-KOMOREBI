# PDF renderer diagnostic

Some full-page preview presentations appeared to omit the leading glyph of repeated spread numbers. Extracted PDF text and glyph bounds were intact. Subsequent enlarged crops and direct pixel inspection of explicit system Poppler output showed the complete heading. This observation did not establish a missing-glyph defect in the final PDF or saved raster.

The runtime PATH points to a `pdftoppm` override reporting version 26.05.0. Final quality assurance explicitly uses `/usr/bin/pdftoppm` version 24.02.0 and an immutable PDF snapshot at 150 dpi. The fixed renderer and snapshot make review provenance explicit. Actual figure clipping and overlaps found earlier were corrected in the figure sources and rechecked separately.
