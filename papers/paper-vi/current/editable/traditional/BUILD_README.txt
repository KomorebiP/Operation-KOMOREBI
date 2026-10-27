Current authored monograph build

Run python build.py from this directory. The full source tree is copied to a temporary directory and compiled with4 XeLaTeX passes and BibTeX. Relative assets are retained. Font dependencies are installed URW P052 and Nimbus Sans, and Latin Modern mono and math; the Lean guide additionally uses DejaVu Sans Mono. Font files are resolved locally with kpsewhich and standard system locations, then copied only into the private build stage. No font binaries are bundled or downloaded. --check-only preserves delivered files. --output-directory PATH writes compiled products to that destination. No historical assembly or scientific/figure regeneration is run.

Final delivered PDF152 pages. Root packaged replay compares pages and extracted text, recording binary hash identity separately. Two harmless unicode-math/mathtools command-coordination notes remain. No overfull box, missing glyph, undefined citation or undefined reference remains.
