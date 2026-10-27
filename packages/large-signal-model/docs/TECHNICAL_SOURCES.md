# Technical reference points

Accessed 9 October 2026. These are primary documentation sources for implementation
conventions and tooling, not external endorsements or validation of PR-LASM.

- NumPy FFT normalization and real-input symmetry:
  https://numpy.org/doc/stable/reference/routines.fft.html
- SciPy stable sigmoid (`expit`):
  https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.expit.html
- Setuptools PEP 517 build backend:
  https://setuptools.pypa.io/en/latest/build_meta.html
- Python packaging tutorial:
  https://packaging.python.org/en/latest/tutorials/packaging-projects/
- Official artifact upload action (`v7`):
  https://github.com/actions/upload-artifact
- Official artifact download action (`v8`):
  https://raw.githubusercontent.com/actions/download-artifact/main/README.md

The algorithms, equations and measured PR-LASM claims in the guide are tied to
this repository's implementation, tests and row-level verification records.
The release does not rely on third-party reports of benchmark performance.
