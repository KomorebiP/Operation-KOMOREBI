# Paper IV — complete sources with a visual appendix

**Komorebi P.**

Reading source: **Cyclic Analytic Functions, Reciprocal Families, and Spectral Zero Data**,
formal v1.0.0 plus the later 39-page proofread draft. The original formal release,
proofreading review, and independent audit are preserved separately, byte-for-byte.

## Read

- `pdf/Paper_IV_With_Visual_Appendix.pdf`: 65 pages, original 39 followed by V-1 through V-26.
- `pdf/Paper_IV_Visual_Appendix.pdf`: the 26-page appendix alone.
- `pdf/Paper_IV_Proofread_v1.0.0.pdf`: the unchanged selected manuscript.

The appendix contains 24 editable vector plates, exact worked coefficient and matrix
models, and four rationally certified local zero brackets. Each appendix source line
links to the relevant original page in the combined edition. The original document
is not relabeled as a new formal release.

## Verify or rebuild

From this extracted directory, with Python 3.10 or later:

```powershell
python Run-PaperIV.py verify
python Run-PaperIV.py build --output-dir rebuilt
python Run-PaperIV.py original --output-dir rebuilt
```

`verify` checks bundle hashes, reruns all 147 exact/symbolic/enclosure tests and five
invalid controls, checks inherited SHA manifests, and regenerates the original
95-record manuscript register in a temporary copy. It compares the saved audit with
the declaration contract. **It does not invoke Lean or authenticate proof checking.**

`build` needs pdflatex, the LaTeX packages listed in `visual_appendix/README.md`, and
Python dependencies from `visual_appendix/requirements.txt`. It works in a temporary
directory, regenerates all plates, compiles the appendix, appends the original PDF,
adds navigation, and compares every output page with its input text and 72-dpi render.

`original` retypesets the unmodified proofread LaTeX in isolation. It uses a working
`bibtex` or `bibtex.original`; when neither exists it uses the supplied matching `.bbl`.
It reports any differences rather than silently replacing the source PDF.

## Find the source

| Folder | Contents |
|---|---|
| `original_snapshot/lean_release/PRSC_IV` | Original v1.0.0: 119 Lean files, LaTeX/PDF, bibliography, theorem maps, pins, saved audits, scripts and license status. |
| `original_snapshot/proofread_review/PRSC_IV_Review` | Later selected PDF, editable proofread LaTeX, prose patch and review evidence. |
| `original_snapshot/independent_audit` | Retained independent static audit and its stated failure to run a fresh Lean build. |
| `visual_appendix` | New LaTeX, 24 TikZ plates, Python models/generator, exact-check script and certificates. |
| `tools` | Source-integrity checker, isolated original rebuild helper, and matching bibliography output. |
| `provenance` | New build/replay records, preservation checks, visual review and documented corrections. |

## Evidence and scope

No new Lean verification was attempted for this editorial addition. The original
release reports 68 scoped manuscript results; its saved formal evidence remains
inherited evidence. The proofread review did not rerun Lean. The independent audit
also records that its fresh proof build could not run. These records are not merged
into an invented new certification.

The new finite tests are exact within their declared bounds. The four cubic brackets
prove a unique root in each stated real interval through endpoint signs, derivative
bounds and the analytic alternating-series remainder. They do not enumerate all real
or complex zeros. Curves and asymptotic diagnostics are numerical illustrations.
Fixed logarithms, simple-nearest-zero assumptions, multiplicities, the imported
standard fact and the paper's open questions remain explicit.

The Lean compiler and Mathlib cache, TeX installation, and installed Python packages
are **not** included. Formal toolchain pins and original verification procedures are
retained. To replay Lean, use a disposable copy of the original formal release and its
`VERIFY.sh`/README with the exact toolchain installed. Do not point that release gate
at this editorial wrapper ZIP as though it were the original formal-release archive.
