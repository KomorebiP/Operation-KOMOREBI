# A theoretical atlas of the Large Signal Model

The current visual companion uses precise mathematical diagrams, commuting maps, geometric obstructions and exact rational examples to explain the theory. It is designed to accompany the full monograph and its unchanged Lean proof companion.

- `build/Realization_Calculus_Large_Signal_Model_Theoretical_Atlas.pdf`: finished publication.
- `atlas.tex`: editable manuscript.
- `generate_figures.py`: Python source for all mathematical vector figures.
- `figures/exact_example.json`: rational running-example calculation receipt.
- `PROOF_MAP.json`: plate-by-plate propositions, exact scopes and actual Lean modules from the accepted coverage register.
- `build_atlas.py`: rebuild and layout diagnostics.

From this directory, run `python3 build_atlas.py`. It requires NumPy, Matplotlib, PyMuPDF, an installed XeLaTeX and its fontspec, unicode-math, geometry, graphicx, xcolor, amsmath, booktabs, enumitem, fancyhdr, hyperref and microtype packages. The publication uses the P052 fonts already included and licensed under `Monograph/assets/fonts/`, plus Latin Modern Math from TeX. The PDF embeds its fonts.

All illustrations are generated from formulas or declared finite examples. No learned checkpoint, empirical performance result or new Lean execution is asserted. A finite plotted orbit does not replace the proof of density; a bound curve is not an observed error curve.

The current atlas supersedes older visual companions as the main reader entry point. Those documents remain preserved in the reference laboratory with their original edition context.
