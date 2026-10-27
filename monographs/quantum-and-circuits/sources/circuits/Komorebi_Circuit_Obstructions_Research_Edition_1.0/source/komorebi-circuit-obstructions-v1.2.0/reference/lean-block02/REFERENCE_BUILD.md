# Block 02 reference generation

The PDF contains explanatory proofs and every maintained theorem declaration, including inherited Block 01 support. It is not a replacement for the Lean proof terms.

The declaration register is generated from the fresh `#check`/`#print axioms` log and the source inventory. Each statement is retained unchanged in UTF-8 in `signatures_utf8.txt` and `declaration_catalog.json`. For PDF monospace rendering only, logical glyphs are shown in ASCII: forall, exists, ->, <->, <=, !=, /\, in, not. `^^` is Lean's Boolean XOR notation. The PDF ASCII typesetting is not presented as a compilable Lean source file. The unmodified formal sources and elaboration log remain authoritative.

Run `python build.py` in this directory. It uses installed pdflatex without shell escape, twice. No network or font download is required. Font binaries and Lean binaries are not included.

The source edition v1.2.0 is identified by the repository source seal and final Git tag. Historical v1.1.0 evidence is pinned to its predecessor, not silently reused as verification of changed files.
