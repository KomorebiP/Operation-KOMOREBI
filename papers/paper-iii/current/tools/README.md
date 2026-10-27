# Release build tools

The active manuscript is compiled from `manuscript/Paper_III_Traditional_Final.tex` and its four chapter files. The `checkpoint_v0.3.0` directory is preserved historical evidence. Its publication counts, source manifests, and instructions describe that checkpoint, not the current release.

Run `python BUILD_PDFS.py` from the package root to rebuild the current reader files after installing the documented TeX and Python dependencies. Run `python VERIFY_RELEASE.py` on a fresh extraction to check the final package manifest. Formal verification has its own commands under `formal/` and must be run separately.

The statement register is generated from the actual chapter files used by XeLaTeX. Historical source hashes are retained in the register only as comparison records.
