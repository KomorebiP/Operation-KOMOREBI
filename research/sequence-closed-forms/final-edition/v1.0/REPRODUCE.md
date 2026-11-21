# Reproduce final edition 1.0

Extract the source ZIP into a fresh directory. Its prebuilt PAPER.pdf,
standalone PAPER.html, and editable PAPER.md are in this directory.
All mathematical replay commands need only Python 3.10+ and its standard library.

```sh
python -B tools/sequence_final_edition.py
python -B tools/verify_sequence_final_edition.py --output final-edition-checks
python -B -m unittest discover -s tools -p test_sequence_final_edition.py -v
```

The assembly check authenticates the four frozen proof notes against the retained
101-member edition, applies the recorded editorial changes, preserves every
imported mathematical token, and compares the resulting manuscript. The
combined replay runs the six unchanged certificate programs and writes one
JSON report per program, logs, and a combined result.json. Use a new empty
output directory for each run.

The mathematical conclusions depend on the written proofs and the verified
finite leaves under their stated coverage bounds. These commands do not
establish independent review, historical novelty, or Lean formalization.

## Optional PDF regeneration

The prebuilt HTML already contains vector SVG mathematics and needs no network
or JavaScript for reading. PDF regeneration uses Node.js 24, Playwright with a
Chromium browser, and the exact retained MathJax runtime. Frozen rendering
inputs and the runtime license are retained in render-inputs/. These tools
are separate from the standard-library mathematical replay.

From the extracted source-package root, fetch the pinned runtime and serve
the directory locally. The frozen HTML input already contains the manuscript
and its print styles:

```sh
python -B research/sequence-closed-forms/final-edition/v1.0/render-inputs/fetch-mathjax.py --output mathjax-runtime
python -m http.server 8846 --bind 127.0.0.1
```

In another terminal:

```sh
node research/sequence-closed-forms/final-edition/v1.0/render-inputs/build-pdf.cjs http://127.0.0.1:8846/research/sequence-closed-forms/final-edition/v1.0/render-inputs/PRINT_INPUT.html rebuilt-paper
```

The fetcher checks the package's pinned SHA-512 before extracting it.
The builder rejects MathJax errors,
duplicate IDs, missing internal destinations, and page overflow. It emits
PAPER.pdf, a script-free standalone PAPER.html, and render.json. The PDF
contains a creation timestamp and renderer metadata; different browser
versions may change typography or bytes. ARTIFACTS.json records the exact
published files rather than promising cross-engine byte identity.

Keep the existing versioned outputs when experimenting with a rebuild.
Any publication change should receive a fresh edition or an explicit erratum.
