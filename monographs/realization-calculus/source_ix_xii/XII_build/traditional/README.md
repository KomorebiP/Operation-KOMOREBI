# Paper XII reading release 1.0.0

This is a current editable reader, not the historical standalone build folder. From the release root run:

```text
python tools/build_readers.py --output /absolute/path/to/fresh-output
```

All three readers are built together so companion destinations agree. A working TeX Live installation, PyMuPDF and Matplotlib are required. Fonts are installed build dependencies, not bundled files. Consult the root BUILD.md and RELEASE_SCOPE.md. Preserved original instructions and audits are under predecessor/. No PDF build invokes Lean or Lake.
