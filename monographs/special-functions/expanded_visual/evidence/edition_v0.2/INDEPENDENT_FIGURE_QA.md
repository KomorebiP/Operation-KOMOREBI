# Independent figure QA

Complete: all 110 expected PNGs inspected. Every reported visual issue is corrected and the affected final figures have been rechecked. Exact reviewed filenames and SHA256 checkpoint hashes are listed in `INDEPENDENT_FIGURE_QA.json`.

## Concrete findings

- `F03_carry_matrix.png`: Dark 1 labels on the darkest matrix cells. **corrected and independently rechecked: white labels readable**.
- `I02_carry_matrix.png`: Dark 1 labels on darkest matrix cells. **corrected and independently rechecked at full size**.
- `I07_unitary_details.png`: W3 overlaps title; W2 and W0 annotation labels overlap. **corrected and independently rechecked at full size**.
- `III02_generalized_minors.png`: Dark labels on dark-blue cells and white labels on pale-yellow cells. **corrected and independently rechecked at full size**.
- `VI10_coherent_frame.png`: Right xlabel ending clipped at image edge. **corrected and independently rechecked at full size: shortened xlabel fully visible**.
- `IV04_positive_gram.png`: Left title ends essentially against the colorbar top (about 3 px gap). **corrected and independently rechecked at full size: shortened title separated from colorbar**.

- `vii_03_lowest_plane.png`: The 3D z-axis label x_001 overlaps the right-panel degree-one target ylabel; lower 3D ticks are dense. **corrected with explicit vertical-axis caption and independently rechecked at full size; gutter clear**.
- `vii_10_tree_addresses.png`: Side tree and short-address labels touch the node circles. **corrected and independently rechecked at full size**.
- `viii_10_q_trees.png`: Shared side tree and short-address labels touch the node circles. **corrected and independently rechecked at full size**.
- `viii_03_lowest_seed.png`: Unicode closing ket appears as a missing-glyph square in both xlabels. **corrected and independently rechecked at full size**.
- `viii_07_nonmonotone.png`: Delta-H text touches/crosses the upper-left entropy curve. **corrected and independently rechecked at full size**.

- `I04_exponential_system.png`: Root final-page review found the panel titles crowded on physical page 17. **Shortened titles independently rechecked at full size; clear separation and labels.**

- `V03_phase_space.pdf` and `VI03_cross_ambiguity.pdf`: Root final-page review found white crosshatching from tiled vector mesh rendering. **Author rasterized mesh layers; independent 170-dpi PDF renders rechecked at full size, with crosshatching absent. Original PNG hashes unchanged.**

## Review scope

Contact sheets use 1400 px width with three figures stacked. I07 and VI10 were enlarged to full size. Corrected F03, I02, I07, and III02 were also inspected at full size. VI01–VI12 were rechecked after the latest regeneration. V01–V12 were inspected in four additional contact sheets; VI03 also received a full-size final-version recheck. IV01–IV12 were inspected in four contact sheets; IV04, IV05, and IV12 were checked at full size. The six final synthesis figures were included as final-version checks. VII01–VII12 and VIII01–VIII12 were inspected individually at full original PNG resolution. The regenerated V12 reference xlabel was also rechecked at full size. VII03 introduced a 3D z-label collision, reported above; the final explicit axis caption was rechecked and leaves the center gutter clear. Final VIII12 and the revised VII10, VII12, VIII03, VIII07, VIII10 were inspected individually at full size.

Diagram/formula consistency was checked from plotted labels and values, the corrected local source core, and selected chapter/code formulas including arithmetic addresses, Gamma shape maps, positive-moment spectra, VI cumulants, the coherent strip example, and the V ambiguity, Fourier phase, Wigner marginal, ladder, fractional-depth formulas, and the IV carrier, Gamma envelope, log-Gamma law, actual-modulus characters, Borel coordinate, and Padé contract. VII/VIII checks covered the displayed ladder, simplex/kernel dimensions, pair spectra, exact amplitudes, phase/dephasing comparison, recurrence gauge, bistochastic concentration, joint tree addresses, Givens count, ordered q-routing, seed ratio, exact beam/gap, finite entropy decrease, skew tangent, matched-gauge limit, tree diagnostics, collapsed scalar lattice, and shifted Askey-Wilson eigenvalue. This is a bounded mathematical consistency review, not a fresh proof audit or universal numerical validation. Other source computations were not rerun in this visual check. The six synthesis figures have separate exact/numerical computations and a separate verification-agent review; their author self-review is not independent authorship.

After the full default reproduction, 109 PNGs matched the stored hashes. The changed `IV11_resolvent_borel.png` was independently inspected at full size; its titles, legends, axes, and formulas are clear. Its hash was refreshed, so all 110 current PNGs match the final checkpoint.

I04 was subsequently rechecked after its final-page title fix; its new hash is recorded. V03/VI03 original PNG hashes are unchanged. Their modified figure PDFs were independently rendered at 170 dpi and inspected at full size; the white mesh crosshatching is absent, and the fields, axes, labels, and colorbars are clear.

Final assembled-page layout is a separate review by root.

The final master PDF (`3334d18814f2752ebd9a76ec965bf3165ea77119534b04896132d4ebabf4d530`) was checked on individual 110-dpi physical pages 64 and 76. Both mesh fields are clear with crosshatching absent. All 110 PNG hashes were verified again at final sealing.
