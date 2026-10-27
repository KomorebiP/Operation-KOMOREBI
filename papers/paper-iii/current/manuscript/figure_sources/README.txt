PAPER III EXACT MATPLOTLIB FIGURES

From the publication bundle root:
  python3 editable/traditional/figure_sources/generate_figures.py

Requires Python 3, Matplotlib, NumPy, SymPy and FontTools (a Matplotlib
dependency). The generator does not download
or install packages. It uses the adjacent bundled Nimbus Sans fonts. The local
convert_fonts.py script produces a deterministic TrueType cache, preserving
Unicode maps and horizontal metrics exactly and converting cubic outlines
with maximum error 0.0005 em. The cache family has a distinct name so Matplotlib
does not accidentally select a same-named system CFF font. Math labels use the
bundled Matplotlib DejaVu math fonts. Every PDF is vector-based with embedded
fonts; every PNG is 300 dpi. Figure page boxes are exactly 6.7 inches wide.

Files and responsibilities:
  common.py            fixed page box, palette, font registration, atomic save
  convert_fonts.py     portable Nimbus outline conversion and cache provenance
  models.py            exact models and the twenty finite checks
  model_data.json      explicit model conventions and displayed finite data
  generate_figures.py  plotting and non-overlapping text-layout checks
  fonts/               derived TrueType fonts and source/output checksums

Outputs are written to ../figures as stable PDF/PNG pairs. Replacement is
atomic, and each output mtime is max(current time, previous mtime + 2 seconds).
PDF creation timestamps are omitted so an unchanged environment and unchanged
source produce deterministic content. No random values are used.

The three retained source figures preserve all original map directions and
support conventions. The new figures are finite illustrative models, not
proof certificates for the manuscript's universal results. The polar formula
uses the positive branch cos(delta)>0, i.e. abs(delta)<pi/2; its displayed
meshes 2,4,8 have increments pi/6,pi/12,pi/24. The correction figure uses the
standard Euclidean inner product and a displayed scalar identification of the
cokernel. Jet coefficients are Hessian responses; the Taylor factor 1/2 and
both ordered mixed input slots are retained.

Run evidence and rendering QA are recorded under ../tmp/figure_qa. Exact
identities use symbolic noncommuting coefficients, SymPy, and Fraction;
floating point values are used only for drawing geometry after checks pass.
