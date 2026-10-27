# Discovery research sources

The current reading edition is **../books/Special_Functions.pdf**. Its production LaTeX is in **../monograph/**. The current visual companion is **../books/Resolution_and_Coupled_Atlas.pdf**, with production source in **../coupled_atlas/**.

This directory preserves the research laboratories, proof routes, code, original figure scripts, examples and execution evidence. Its older manuscript/build scripts and `historical/` documents are provenance, not the current publication entry point. Use the package's root README for current commands.

From the package root, run `python verify_research.py foundation --output-dir local_checks/foundation` or `python verify_research.py coupled --output-dir local_checks/coupled`. Both commands require fresh output paths under this directory. Run without `-O`.

The former directory README is preserved under `../verification/release/replaced_readmes/`. No mathematical API or test tolerance was changed for this packaging pass. No new reuse license is applied.
