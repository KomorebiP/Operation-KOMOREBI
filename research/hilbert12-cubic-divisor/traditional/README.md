# Cubic Divisor Transport and Reconstruction

The editable traditional manuscript is `H12_Cubic_Divisor_Traditional.tex`; its mathematical sections are under `sections/`. The PDF and complete mathematical Markdown have the same basename.

Rebuild locally with Python 3, TeX Live (including AMS, geometry, microtype, longtable and hyperref), and Pandoc:

```sh
python build_traditional.py
```

This performs three PDF passes and regenerates Markdown. It does not run archived computations or alter source originals. `assemble_manuscript.py` is a separate explicit authoring tool for three proper-math source sections; it protects and compares mathematical spans before converting prose citations. Manually typeset principal-divisor and reconstruction sections remain editable and are independently audited.

The formal and numerical verification scope is stated in the manuscript and separate companions. The original gamma/class-field identification remains open.
