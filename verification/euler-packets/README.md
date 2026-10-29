# Euler packets: reproducibility and review

The maintained worked page is `docs/demonstrations/EULER_PACKETS.md`.
Its standalone exact checker is `examples/euler_packets.py`.

```text
python -B examples/euler_packets.py
python -B examples/euler_packets.py --output a-new-results-directory
```

Python 3.10+ and its standard library are sufficient. No files are written by
the first command. The second creates JSON and exact CSV tables and refuses to
replace existing result files.

`run-003/manifest.json` is the accepted v2 bounded execution record. It identifies
the actual source revision and dirty state at execution, observed source hashes
before/after, Python version, elapsed time, limits and output hashes. These
hashes bind the new source independently of its pre-commit dirty state. The
contract specifies every tested range and what a pass does not establish.

`cross-check-003/manifest.json` binds a separate check of the accepted results,
the page's printed CLI output, Schur reconstruction, and exact agreement with
the pinned mathematical-library source, including 605 reciprocal coefficients
and 1,012 local-chart values, truncations and row weights. The additional
`local-reconstruction.csv` gives every displayed E_8 term, partial sum and error.
`coefficient-matrices.csv` supplies the finite local and Pascal blocks, the
sampling block and the two displayed chart changes. `congruence-ladders.csv`
records the guaranteed moduli, residues and exact errors. The supplementary
checker also verifies complete rows of the infinite sampling-kernel witness
and the stated finite Euler-index supercongruence examples.
To repeat that additional comparison,
use a checkout whose tracked `src/` matches the pin in
`manifests/reader-site-libraries.json`:

```text
python -B tools/check_euler_case.py --math-root PATH_TO_PINNED_KOMOREBI_MATH
```

That optional command also needs the library's declared dependencies. Its source
comparison rejects imported untracked project files and records the actual
imported source hashes before/after. It does not rebuild external dependencies.

The runner used a 60-second wall timeout and a 1 MiB combined-log cap. No hard
POSIX memory, CPU or affinity limit is claimed on Windows. The recorded thread
setting is a conventional environment preference, not a universal enforcement
mechanism. Neither run is a hardware performance benchmark.

The first-edition self-review is in `PROOF_REVIEW.md`, and the added claims and
full-page proofreading are in `PROOF_REVIEW_EXPANSION.md`. The
matrix, base-change and additional congruence arguments are reviewed in
`PROOF_REVIEW_MATRICES.md`. The authenticated
references are in `SOURCES.md`, with the precise new denominator-theorem
application in `LITERATURE_EXTENSION.md`. The target and route checkpoint is
in `TARGET_AND_ROUTES.md`. Written proofs and finite
execution are separate evidence. The local reconstruction and precision
theorems have written proofs. No broader Euler-branch conjecture is certified
by the finite checks, and no Lean run, novelty, exclusive method or speedup is
asserted.

The preceding `run-001`, `cross-check-001`, `run-002`, `cross-check-002` and their contracts are preserved
as historical execution records. Their input hashes describe their respective editions,
not the revised program or page. They are not accepted evidence for the
expanded source. The publication record accepts only the fresh 003 runs.

The publication manifest in `manifests/euler-packets-worked-example-2026-10-29.json`
binds the final manuscript, code, review and execution records. Captured runner
files have newline conversion disabled in `.gitattributes`, preserving their
exact bytes across Windows and Linux checkouts. Original-project terms are in
the repository's `LICENSE.md`; third-party references retain their own terms.
