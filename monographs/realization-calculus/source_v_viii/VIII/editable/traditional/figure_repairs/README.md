# Paper VIII figure presentation repairs

This directory provides four narrowly scoped, reproducible repairs. The other
18 inherited traditional figure PDFs are preserved byte for byte.

* Figure 01 wraps the original architecture labels within their existing boxes.
* Figure 17 retains the CPU and GPU prefixes in method names, distinguishing the
  two compressed-product series. The original eight timing values are unchanged.
* Figure 18 places both original reuse annotations inward, below their points.
* Figure 22 displays the same 40 contract counts horizontally so the long timing
  scope remains readable. It still represents the original 154 recorded rows.

The inputs are the unchanged sanitized measurement corpus copied under
`raw_inputs/` and the preserved source generator in `source/strengthened/`.
The corpus contains inherited measurements. No new hardware benchmark is run by
either script. These figures do not establish a universal performance claim.

Python, NumPy, pandas, and Matplotlib are required. From this directory:

```bash
python repair_figures.py
python audit_repairs.py
```

The first command produces `staged/` PDFs and their precise plotted models. The
second compares original and repaired Matplotlib artists, verifies every plotted
numeric value and architecture edge, and checks byte-identical repaired PDF
replay. To deliberately refresh the publication assets:

```bash
python repair_figures.py --output-dir ../figures
```

The package report `verification/monograph_figure_report.json` pins the original
and current hashes for all 22 figure assets. Standalone figures were inspected at
full preview size. Final PDF placement is reviewed separately in the monograph
layout audit.
