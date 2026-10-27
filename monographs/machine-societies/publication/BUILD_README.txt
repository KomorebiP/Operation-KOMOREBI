Machine Societies: Modern Monograph presentation edition

From the package root:
    python3 publication/build.py

Windows PowerShell:
    python .\publication\build.py

Use XeLaTeX from a TeX Live or MiKTeX installation that supplies fontspec,
unicode-math, geometry, microtype, amsmath, amsthm, mathtools, booktabs,
array, longtable, tabularx, graphicx, tocloft, enumitem, fancyhdr, titlesec,
needspace, setspace, xcolor, caption, etoolbox, tcolorbox, hyperref,
bookmark, and placeins. Bundled font files and included vector figures
allow the manuscript to build without retrieving assets from the network.

The build makes three passes for the contents and cross-references, then
checks for overfull boxes, unresolved references, and missing glyphs.
The output is ../Machine_Societies_v1.0.0.pdf relative to this directory.

The mathematical manuscript retains text edition 1.0.0. This is a
presentation revision, dated 15 October 2026. The original complete source
release is preserved under ../source_release/.

The current delivery was built with XeLaTeX on Linux. The Windows command
is provided for the same portable Python entry point and was not run here.
