Paper II strict final verification

Run only after the production source tree and semantic coverage are frozen.
The development baseline and its object files are not reused by this driver.

1. Freeze all local .lean source files and their dependency order:

python3 verify_release.py --root /absolute/formal/current --kit /absolute/runtime \
  --out /absolute/new-final-output --freeze-manifest /absolute/release_modules.json

2. Run the exact frozen closure:

python3 verify_release.py --root /absolute/formal/current --kit /absolute/runtime \
  --out /absolute/new-final-output --manifest /absolute/release_modules.json

Use --lock-file to select the shared Lean serialization lock when moving this
directory. The working default is paper2_work/lean_serial.lock. No simultaneous
Lean subprocesses are started by this driver. Each process has a wall deadline,
-j1 and strict warning/implicit flags. The actual container memory bound is
recorded. A virtual-address cap is not imposed because Lean maps cache files
larger than its resident memory use.

The audit authenticates pinned runtime files, the executable-discovery adapter,
and exact clean dependency revisions. It compiles every local production module
fresh, snapshots every source and audit input, and records commands, logs,
object hashes, timing and memory. The complete source-owned declaration set is
identified by module ownership, including declarations outside project names.
Custom axioms, opaque declarations, unsafe definitions, placeholders and
unreviewed generated partial helpers are rejected. Reviewed helpers must match
their exact source files, declaration types, proof-independent runtime bodies,
universe parameters and axiom inventories. Logical declarations cannot refer
to those helpers. Final kernel replay checks every remaining owned declaration
starting from upstream imports alone, with no project modules preloaded.

The runtime-helper review must have status REVIEWED after independent root
review. Merely generating the review file does not authorize an exception.
Any new helper or upstream overlap fails closed and requires a separate review.

Standalone infrastructure controls:
python3 verify_release.py --root /absolute/formal/current --kit /absolute/runtime \
  --out /absolute/new-controls-output --controls-only --timeout 120

Eight negative controls cover injected axioms, placeholders, opaque constants,
unsafe code, a false equality, missing positivity, warning-as-error rejection,
and a corrupted theorem body submitted to the kernel. Positive controls verify
that an outside-namespace owned theorem is inventoried and replays successfully.

This verifies formal source closure against the pinned Lean kernel and existing
upstream cache. It is not an independent kernel, an upstream cache rebuild, or
a proof that the manuscript has exactly the same hypotheses and conclusion.
The semantic coverage audit is a separate required release record.
