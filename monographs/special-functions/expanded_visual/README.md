# Expanded Visual Guide

The current PDF is **../books/Expanded_Visual_Guide.pdf**: 180 pages with 171 complete one-page lessons. The figure mathematics and the 171 original vector plates are retained. The current design uses the same serif typography, plum cover and restrained running headers as the monograph. All contents destinations and lesson blocks are checked by `validate_guide.py`.

Build from the supplied vector figures with `python build.py`, then run `python validate_guide.py`. XeLaTeX is required. The output is `build/Expanded_Visual_Guide.pdf`.

For a complete independent figure rebuild, run `python reproduce_guide.py --output-dir local_rebuild`. The destination must not exist. The command copies the actual source and evidence inputs into an isolated directory, executes eleven figure-script stages, checks for 171 PDF/PNG pairs, builds the guide and validates the lesson/page contract. It does not overwrite this directory's prior evidence.

The previous reading edition's source framing, earlier review records and original directory README are retained under evidence or the root verification directory. Older source receipt names describe their original scope. They do not certify a new Lean build or a fresh independent reproof of all analytic results. See the root release report for current executed checks and remaining limitations.
