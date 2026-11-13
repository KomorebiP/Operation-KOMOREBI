# Smith chart and RLC synthesis: current source

Author: Komorebi P.  
Original consolidation base: `3e4090141cc88dac723d87c7c504a9b1076a2caf`.
Current research base: `f88939b267fe6e03af555727a1e770985395bba5` (after PR203).

The maintained reading is now one canonical article at
`read/smith-chart/research.html`. Its single contents structure includes the
current synthesis and lower-bound chapters, the complete earlier supplements,
the companion reference and expandable research history. The old continuation
and supplement URLs preserve section bookmarks and lead into this article.
Search, sitemap and the two-pane catalogue present the canonical reading.

## Current mathematical results

The structural sample-to-physical transfer now has a complete written argument:
every ordinary graph with at most four reactive branches has positive-real
seven-sample error greater than `10^(-10^45)`, for arbitrary finite positive
resistors. A maximum-conductance R spanning forest has at most nine edges after
R-only reduction. Its scale gap, a backbone coefficient floor and exact LC flow
repair handle physical resistor faces and nearly cancelled natural factors.
This is much larger than the retained older bound, but still extremely small.
It does not close the practical-sized global margin. Read
`GLOBAL_BALANCED_TRANSFER.md`, `PHASE8_REVIEW.json` and `current-exact-011`.

The same proof gives a global zero-loss feature chart: endpoint/resonance/jet
data within1/1000 of the target give error>1/300 without assuming a physical
core box. `solver/backbone_transfer.py` independently validates a supplied
physical state, every original node's KCL, LC changes and R opening/shorting
budgets. The worked `physical_transfer_example.json` certifies strict1/400.
Its resource limits are10 labels,49 branches/45 R/two L/two C,256-bit actual
values,8192-bit witness rationals and512KiB JSON; these are execution caps.

`LOW_RESISTOR_MARGINS.md` proves lossless margin1/100000 and whole one-R
margin1e-150 at reactive budget four, including common powers of s. The
earlier exact regular classification, supplied1% regions, internal-mode
theorem, whole one-kind margins and all prior code/evidence stay unchanged.
The retained stronger typed-certificate program still lists1334/2130 and796
balanced placements; the separate uniform structural bound applies to all.

`GENERIC_JOINT_OPTIMALITY.md` proves that almost every real degree-n member
of the open F_n families needs2n+1 total components. The existing n-reactive,
n+1-resistor construction attains that total and the reactive minimum. This
does not certify the resistor count of an individual rational target or rule
out more LC with fewer R. The first-order/Cauer and exact-six results remain.

All new proofs have project self-review. Selected Lean scope stays41, with
no new independent review, complete formal, physical measurement or priority
claim. PROGRAM.md retains the six parent contracts; STATE.json is the one
current status. All predecessor source hashes and evidence are preserved.

## Reproduce from the single current-source download

Extract the source ZIP into a new directory. From its root, run:

```text
python -B replay.py
```

This authenticates six retained authored checkpoints, replays the eleven
portable predecessor commands in isolated copies, and runs the current exact
family, boundary, synthesis/tolerance, topology, mixed-loss, coefficient-box,
coefficient-fiber, series-margin, physical transfer-barrier, stable-fiber,
energy/trade-off, branch-rounding, root-count, endpoint, whole one-kind,
+internal-mode, inversion, positive-real comparison and near-mode certificate checks. It writes a fresh
result directory without changing retained archives.
No network, numerical solver or optional package is needed. Python 3.11+ is the
intended baseline; the current replay uses Python 3.12.14 on Windows.

For the cumulative current checks:

```text
python -B replay.py --current-only
```

For the new physical-state example (the verifier reconstructs the state and
budgets, rather than trusting a solver success flag):

```text
python -B research/smith-chart/unified/solver/backbone_transfer.py research/smith-chart/unified/solver/physical_transfer_example.json --output state-result.json
python -B research/smith-chart/unified/solver/backbone_transfer.py state-result.json --verify
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

For the mixed-loss example, use the same prefix as above:

```text
python -B research/smith-chart/unified/solver/loss_certificate.py research/smith-chart/unified/solver/loss_example.json --output loss-result.json
python -B research/smith-chart/unified/solver/loss_certificate.py loss-result.json --verify
```

For actual formal replay, also run `formal/replay_loss_reduction.py`, which
repeats and authenticates the original core before its new sixteen statements.
For the earlier extensions, run `formal/replay_shunt_formal.py` (which also replays the core) and `formal/replay_cap_shunt_formal.py` with explicit `--lean`,
`--mathlib`, `--git` and a fresh `--output` directory for each command. The dependency lock and
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
numbering remain in the package. The additional diagrams use the same
full-size dialog as the 42 retained figure-edition drawings.

The code and proof review are project self-review. Source tests and computation
replay do not establish whole-book formal coverage, historical priority or
physical hardware performance. The written subclass proofs and explicitly
scoped formal lemmas support the new resistor and ideal-model tolerance results.
