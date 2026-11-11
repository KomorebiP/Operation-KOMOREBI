# Smith chart research archive and reading

The retained `SmithChart_Complete.zip` is the 172-file research package supplied
for this reading, dated 11 November 2026. Its SHA-256 is
`39fd0d659ef6c006eebb129e08a9b2ced72ce5b857ba846d6481711c951c371e`.
The 170 files named in its `MANIFEST.sha256` matched their recorded hashes;
the manifest itself and `PACKAGE_VALIDATION.json` are outside that list. The
original archive contains the self-contained HTML reading and the complete
research, figures, and reproduction sources. The copy here is byte-identical
to the supplied ZIP.

The website renders the article from that retained HTML, preserving its text,
mathematics, captions, section identifiers, and 42 figures. It replaces the
embedded figure and download data with revision-pinned links to byte-identical
copies in this directory, and uses the reader's MathJax installation. The
source archive remains available for a self-contained offline edition. The
build checks the archive and every retained public figure and download against
the source before it publishes the page.

The [five-node census recount](computations/README.md) independently checks
the finite reactive-placement catalogue and records its limits.
The [continuation checkpoint](CONTINUATION.md) separates that finite evidence
and the new first-order RL formalization from the open six-element question.

For a built or deployed site, the optional Playwright check covers desktop and
phone widths, enlarged text, figure captions and zoom, the contents control,
the supplement, and no-JavaScript reading:

```text
node tools/test_smith_research_browser.cjs <reading-url>
```

Install Playwright and a browser in the test environment; set `SMITH_CHROME`
to an existing Chromium executable if needed.

## Independent replay of the included scripts

On 11 November 2026, a fresh isolated copy of `reproduction/exact_seven` was
run under Windows with Python 3.12.14, SymPy 1.14.0, NumPy 2.3.5, and mpmath
1.3.0. No pickle was read from the archive: the generator produced fresh local
intermediate files before the verifiers ran. The scripts were run in this
order:

1. `src/generate_exact_systems.py`
2. `src/verify_exact.py`
3. `src/check_dark_mode_rank.py`
4. `src/verify_interval_margins.py`
5. `src/verify_nodal.py`

The first four completed successfully, including the stated rational
fixed-point and positivity checks. The nodal test also passed at 165 sampled
points; its largest reported scaled error was approximately `1.46e-83`.
The separate `reproduction/new_order_separation/check_order_gap.py` diagnostic
also passed its included checks. Those finite and floating-point diagnostics
support the examples within their stated ranges; they do not establish a
universal theorem by themselves.

Two source scripts determine their location by checking for a forward slash in
`__file__`. On Windows the scripts were launched through the following small
wrapper so that they received a portable path; their archived bytes were not
changed:

```python
import runpy, sys
from pathlib import Path
script = Path(sys.argv[1]).resolve()
runpy.run_path(script.as_posix(), run_name="__main__")
```

Run the wrapper with one of the paths above after copying the reproduction
directory to a new writable location. The exact source and its manifest remain
in the ZIP. This replay is not an independent audit of every mathematical proof
in the draft or a hardware validation. For the degree-six target, whether a
transformer-free RLC-only realization exists with six reactive elements remains
open. Historical novelty has not been established. The existing Lean companion proves
selected results and does not formalize this entire archive. A separate
[first-order RL companion](formal/README.md) checks the affine limit's circuit
identity and positive component values, without claiming the rest of the
arbitrary-order theorem.
