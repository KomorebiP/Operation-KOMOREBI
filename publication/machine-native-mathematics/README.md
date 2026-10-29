# Revised reading edition

**The Possibility for a Machine-Native Mathematics**

Komorebi P. · 29 October 2026

This is a new editorial reading edition of the September 2026 essay. The original
v10 PDF remains in `research/machine-native-mathematics-essay/` with its original
bytes and source receipt. The editable manuscript was prepared from that PDF.
It is not a recovered copy of the original v10 TeX source.

## Files

- `docs/essays/MACHINE_NATIVE_MATHEMATICS.md` is the maintained reading text.
- `publication/machine-native-mathematics/main.tex` is its generated monograph source.
- `website/assets/publications/machine-native-mathematics.pdf` is the released PDF.
- `publication/machine-native-mathematics/build-record.json` binds those files by SHA-256.
- `publication/machine-native-mathematics/EDITORIAL_REVIEW.md` records the review scope and mathematical clarifications.
- `tools/build_machine_native_essay.py` converts the manuscript and builds the PDF.

The layout follows the finished Realization Boundaries monograph: 7.5 by 10 inch
pages, Palatino-family text and mathematics, numbered chapters and sections,
running headers, linked contents, and restrained navy and teal accents.

## Rebuild

Tectonic 0.17.0 was used for the released edition. It downloads and caches its
required TeX packages. To compile the supplied TeX from the project root:

```text
tectonic -X compile --untrusted publication/machine-native-mathematics/main.tex
```

After editing the Markdown, regenerate TeX with Python 3.10 or later:

```text
python tools/build_machine_native_essay.py
```

The converter checks every inline and display mathematical expression for exact
preservation. To compile and update the PDF and build record in one step, install
`pypdf` and run:

```text
python tools/build_machine_native_essay.py --tectonic PATH_TO_TECTONIC --output PATH_TO_BUILD_DIRECTORY
```

The `TECTONIC_CACHE_DIR` environment variable can keep the TeX cache in a chosen
workspace directory. Logs belong in the build directory. Re-render and inspect
the PDF after changes.

This is an editorial reading release. Scientific confidence remains unassessed.
The September 2026 accounts of other papers retain their historical scope.
