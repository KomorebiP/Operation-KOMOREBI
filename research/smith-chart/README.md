# Smith chart research archive and reading

The retained `SmithChart_Complete.zip` is the 172-file research package supplied
for this reading, dated 11 November 2026. Its SHA-256 is
`39fd0d659ef6c006eebb129e08a9b2ced72ce5b857ba846d6481711c951c371e`.
The 170 files named in its `MANIFEST.sha256` matched their recorded hashes;
the manifest itself and `PACKAGE_VALIDATION.json` are outside that list. The
original archive contains the self-contained HTML reading and the complete
research, figures, and reproduction sources. The copy here is byte-identical
to the supplied ZIP.

The website renders an edited reading from that retained HTML. The
[presentation record](edition/README.md) identifies the revised prose and
captions, the 42 vector figures, twelve dedicated mobile layouts, and one
topology-artwork correction. Every archived mathematical expression and stable
section identifier is preserved. Each figure links to its original artwork;
the complete original text and offline reading remain in the archive.
The build checks the archive, retained public sources, and edition manifests
before publishing. The reader uses the site's MathJax installation.

The subsequent schematic pass structurally redraws figures 8, 11, 18, 26, 27,
30, 31 and 37. It separates the three pairwise edges in figure 8, makes circuit
symbols and parallel branches explicit, and preserves the selected mobile
layout in the expanded view. Exact determinant labels have a separate
[fixed-branch check](computations/verification/diagram-labels-002/checks.json).

The [five-node census recount](computations/README.md) independently checks
the finite reactive-placement catalogue and records its limits.
The [continuation checkpoint](CONTINUATION.md) separates that finite evidence
and the new first-order RL formalization from the open six-element question.
The [singular-completion supplement](../../docs/demonstrations/SMITH_SINGULAR_COMPLETION.md)
completes selected rank-deficient prediction and real two-packet feasibility
arguments, with a separate selected Lean companion.

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
