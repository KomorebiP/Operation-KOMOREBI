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

`run-001/manifest.json` is the accepted v2 bounded execution record. It identifies
the actual source revision and dirty state at execution, observed source hashes
before/after, Python version, elapsed time, limits and output hashes. These
hashes bind the new source independently of its pre-commit dirty state. The
contract specifies every tested range and what a pass does not establish.

`cross-check-001/manifest.json` binds a separate check of the accepted results,
the page's printed CLI output, Schur reconstruction, and exact agreement with
the pinned mathematical-library source. To repeat that additional comparison,
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

The mathematical dependency and self-review are in `PROOF_REVIEW.md`, the
authenticated references and notation translation in `SOURCES.md`, and the
target/route checkpoint in `TARGET_AND_ROUTES.md`. Written proofs and finite
execution are separate evidence. No Lean run, novelty, exclusive-method claim,
general Euler congruence or speedup is asserted.

The publication manifest in `manifests/euler-packets-worked-example-2026-10-29.json`
binds the final manuscript, code, review and execution records. Captured runner
files have newline conversion disabled in `.gitattributes`, preserving their
exact bytes across Windows and Linux checkouts. Original-project terms are in
the repository's `LICENSE.md`; third-party references retain their own terms.
