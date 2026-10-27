PAPER III COMPUTATIONAL REPLAY | 8 October 2026

Current run: run_2026-10-08/COMPUTATIONAL_REPLAY_REPORT.json and .md.
The finite offline suite passes 34-file integrity with 33 hash checks, 41 formal
rows and 143 mapped targets. It reconciles historical evidence without invoking Lean.
All 11 strengthened finite/numerical groups pass on the frozen strengthened source.
All 124 visual exact checks pass. All 4 deliberately false controls are rejected.
Current 22 editable/embedded TikZ sources match fresh regeneration. The six main
figures have 20 exact assertions and deterministic vector/raster regeneration.

These checks support their displayed finite ranges and stated numerical tolerances.
They do not certify the 95 ordinary proofs or extend the finite formal contract.
The earlier run_2026-10-05 is preserved as a historical partial replay. Its SymPy
limitation does not describe this current run. No package was installed here.

Use an environment with Python 3.12, NumPy, SymPy, Matplotlib, Pillow and FontTools.
From the package root, in temporary copies where a checker writes reports:
  bash source/finite/VERIFY.sh
  python source/expanded/verification/verify_strengthened.py
  python editable/visual_guide/checks/verify_examples.py
From editable/visual_guide/: python source/generate_graphics.py
From editable/traditional/: python figure_sources/generate_figures.py
All commands are offline. No script automatically installs dependencies.
