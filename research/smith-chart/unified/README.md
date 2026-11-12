# Smith chart and RLC synthesis: current source

Author: Komorebi P.  
Base: `3e4090141cc88dac723d87c7c504a9b1076a2caf`.

The maintained reading is now one canonical article at
`read/smith-chart/research.html`. Its single contents structure includes the
current synthesis and lower-bound chapters, the complete earlier supplements,
the companion reference and expandable research history. The old continuation
and supplement URLs preserve section bookmarks and lead into this article.
Search, sitemap and the two-pane catalogue present the canonical reading.

## Mathematical progress

The systematic phase now adds complete first-order synthesis, global
first-order resistor minima and the Hughes base's two-resistor minimum;
positive rational RC/RL Cauer construction through degree fifteen; seventeen
selected kernel-checked graph/shape statements; usable pure-type margins and
one exact mixed-model refutation; and a uniform ideal RC/RL component-tolerance
theorem. See `LOW_ORDER_SYNTHESIS.md`, `FORMAL_CORE.md`, `TYPED_MARGINS.md` and
`TOLERANCE.md`. `PROGRAM.md` fixes the six remaining contracts and `STATE.json`
is their single current status view. Classical overlap is recorded explicitly.

`DETERMINISTIC_FAMILY.md` proves and implements exact recognition of the specified
uniformly certified cubic family and its endpoint lifts. This removes numerical
rediscovery from that known constructive route. Every accepted rational target
receives a target-bound physical composition certificate replayed by unchanged
acceptance kernels. The implementation covers degrees 3–16 within its declared
arithmetic and consumer caps. Nonmembership and resource limits are distinct
from global RLC nonrealizability.

`COMPACT_MODEL_AUDIT.md` records a fresh adversarial project self-review of
unbounded resistor elimination, physical boundaries, current elimination,
seven-sample identity, effective-minimum hypotheses and the finite packet-family
chain. `SOURCE_AUDIT.json` identifies exact primary versions and inspected pages.
This is self-review, not independent peer review or Lean verification. The
effective margin remains impractical; general minimum synthesis remains open.

The new known-family regression has 38 exact members through degree 16 and
fifteen additional controls. The separate boundary experiment performs 1,458
exact comparisons on all 243 open/finite/short assignments of one specified
five-edge graph. These are different experimental units and must not be added
as a theorem or global topology count. See the single current verification
record for commands, hashes, versions, raw logs and declared scopes.

## Reproduce from the single current-source download

Extract the source ZIP into a new directory. From its root, run:

```text
python -B replay.py
```

This authenticates six retained authored checkpoints, replays the eleven
portable predecessor commands in isolated copies, and runs the current exact
family, boundary, synthesis/tolerance and topology checks. It writes a fresh
result directory without changing retained archives.
No network, numerical solver or optional package is needed. Python 3.11+ is the
intended baseline; the current replay uses Python 3.12.14 on Windows.

For just the new checks:

```text
python -B replay.py --current-only
```

For an individual exact target:

```text
python -B research/smith-chart/unified/solver/deterministic_family.py target.json --output result.json
```

Use `solver/first_order.py target.json` for the complete first-order class, or
`solver/cauer.py target.json --kind RC` (or `RL`) for the corresponding Cauer
class, with the same repository-relative prefix shown above.

The optional mixed-NRA probe uses the separately pinned `z3-solver` backend.
It is excluded from the standard-library replay. Its UNKNOWN results are
resource-inconclusive and its UNSAT reports are not independent refutation
certificates. The shunt-RLC rational refutation has a separate unchanged-kernel
replay in the standard-library checks. No solver runtime or third-party PDF is
included in the source archive.

For actual formal replay, run `formal/replay_shunt_formal.py` (which also replays the core) with explicit `--lean`,
`--mathlib`, `--git` and a fresh `--output` directory. The dependency lock and
compiler hash are the same pinned environment as the earlier Smith companions.
The portable Python command checks its own declared computations; it does not
pretend to execute Lean when that toolchain is absent.

Targets use exact integers or rational strings in ascending powers of $s$.
Floating-point input is rejected. The certificate's center is not an exact
component-value substitution. The original root box and the physical graph
define the exact realization. A successful result contains the portable
composition certificate in its `certificate` field; the surrounding result
report is not itself the consumer's certificate format.

The archive contains the current proof sources, six retained checkpoint ZIPs,
the original research reading, selected Lean sources/receipts and the figure
edition records. It is a mathematical source/check package, not a complete
monorepo checkout or bundled Lean/website runtime. Rebuilding the whole website
uses the full repository's maintained build. Full third-party PDFs remain local
reference material and are not redistributed. No new license is selected.

## Presentation bindings

The original mathematical archives, figures, guide Markdown and Lean receipts
remain byte-identical. The canonical reader merges their HTML content, moves
superseded sections into history, reconciles obsolete checkpoint-status prose,
namespaces section anchors and gives formerly separate explicit equation tags
short chapter prefixes. The retained mathematical expressions are preserved
apart from this equation-label presentation. Source Markdown and original
numbering remain in the package. The three additional diagrams use the same
full-size dialog as the 42 retained figure-edition drawings.

The code and proof review are project self-review. Source tests and computation
replay do not establish whole-book formal coverage, historical priority or
physical hardware performance. The written subclass proofs and explicitly
scoped formal lemmas support the new resistor and ideal-model tolerance results.
