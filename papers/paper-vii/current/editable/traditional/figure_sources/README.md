# Inherited figure presentation repairs

Four of the 35 inherited traditional figures were regenerated using Python and
Matplotlib. They keep the original PDF page dimensions, underlying quantum
models, sampled path, charge transitions, and boundary labels. The other 31
figures remain byte-identical to the retrieved edition. No AI images are used.

The repairs correct the Bell-state ket in a title, connect the cyclic charge
arrows to their packet circles, unclutter the genuine 3D Bloch-sphere ticks and
axis labels, and separate the seven proof-boundary stair boxes while fixing
arrow direction and clipping. Historical generators are retained unchanged in
`upstream/` and in the source snapshots.

From the package root, run:

```bash
python3 editable/traditional/figure_sources/repair_existing_figures.py
python3 editable/traditional/figure_sources/render_figure_review.py
python3 editable/traditional/figure_sources/check_existing_figure_repairs.py
```

The scripts also work from any directory when called with their full paths.
The generator accepts `--output-directory` for an isolated rebuild and
`--report` for model metadata. The checker independently captures plotted
models from the retained original code, verifies the Bell probabilities, all
four cyclic transitions, all 150 Bloch coordinates, all wireframe segments,
genuine 3D axes, the seven ordered boundary labels, and the conditional warning.
It replays the generator from an unrelated directory and requires all four
PDFs to be byte-identical. It also checks every inherited asset's source hash,
page dimensions, contained text, PDF page count, and declared repair decision.

`verification/monograph_figure_report.json` records each of the 35 decisions,
input and output hashes, model scope, source pins, replay results, and visual
review evidence. The software-check count includes repeated per-file layout
and integrity checks. It is neither a theorem count nor evidence for a general
continuum claim. The original Matplotlib heatmaps include embedded raster
images; their existing PDF encoding is recorded honestly and retained unchanged.
The four repaired figures are vector-only PDFs.
