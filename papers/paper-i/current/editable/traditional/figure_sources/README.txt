Main figure sources

From editable/traditional, run:
    python3 figure_sources/rebuild_figures.py

This optional rebuild needs Python, NumPy and Matplotlib. It uses the bundled
Nimbus Sans fonts and writes both vector PDFs and 300 dpi PNGs. The paper build
uses the included PDFs and does not require the plotting dependencies.

The ten figures preserve the data and finite ranges of the original visuals.
The original generation code is retained at:
    source/traditional_v1.3.1/code/python/seed_calculus/visuals.py

The Krylov profiles are checked with exact rational elimination. The
semisimple grid uses exact integer arithmetic. The finite shift support is
checked from its 24 coordinate permutation and six residue packets.
Path and cycle ranks use numerical symmetric adjacency spectra with a
grouping tolerance of 1e-7. These finite plots illustrate the proofs in the
paper rather than extending the tested range.

The sampled transfer and coordinate illustrations retain random seeds 23
and 91, respectively. Their norms and residuals are numerical data. They
are written to figures/numeric_figure_data.json. Rank data are written to
figure_sources/figure_data_ranks.json.

The elliptic diagram displays the exact weighted matrix in the ordered
packets (k[x], yk[x]). The schematic diagrams are reading aids.

The common drawing helper uses fixed page boxes, separate heading bands and
atomic asset replacement. This also protects the finished figures in shared
workspaces whose file timestamps differ.
