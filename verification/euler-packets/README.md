# Euler packets: reproducibility and review

The maintained worked page is `docs/demonstrations/EULER_PACKETS.md`.
Its standalone exact checker is `examples/euler_packets.py`.

```text
python -B examples/euler_packets.py
python -B examples/euler_packets.py --output a-new-results-directory
```

Python 3.10 or later and its standard library are sufficient. The first command
prints the expected report without creating result files. The second creates
JSON and exact CSV tables and refuses to replace existing result files.

The accepted final records are [run-007](run-007/manifest.json) and
[cross-check-007](cross-check-007/manifest.json), for **EULER-CASE-007**.
The [final contract](contract-007.json) declares every tested range and its
non-claims. These records cover the full example, including the quartic atlas,
logarithmic coordinates and exact dyadic-tail continuation. Stages 001–006 are
historical editions; they do not bind the current expanded program.

The [completion check of 30 October 2026](COMPLETION_CHECK_2026-10-30.md)
reproduces the final finite output and manuscript report, repeats all 7,442
pinned-library comparisons, checks all six publication safeguards and verifies
the live IO downloads. Its fresh bounded execution record is supplementary;
the original accepted stage 007 evidence remains intact.

To repeat the supplementary comparison, use a checkout whose tracked `src/`
matches the math revision in `manifests/reader-site-libraries.json`:

```text
python -B tools/check_euler_case.py
python -B tools/check_euler_case.py --math-root PATH_TO_PINNED_KOMOREBI_MATH
python -B -m unittest discover -s tools -p test_euler_publication.py -v
```

The first command needs only the standard library. The optional library command
also needs that library's declared dependencies and Git on PATH; `--git` accepts
an explicit Git executable. It rejects mismatched tracked source and imported
untracked project files and records imported source hashes before and after.
It does not rebuild external dependencies.

The accepted runs and fresh bounded completion run use a 60-second wall timeout
and a 1 MiB combined-log cap. No hard POSIX memory, CPU or affinity limit is
claimed on Windows. Recorded thread settings are conventional preferences,
not universal enforcement. These are not hardware performance benchmarks.

The written proofs and their self-reviews remain separate from finite execution:
[initial](PROOF_REVIEW.md), [expansion](PROOF_REVIEW_EXPANSION.md),
[matrices](PROOF_REVIEW_MATRICES.md), [Fibonacci](PROOF_REVIEW_FIBONACCI.md),
[packet/calculus](PROOF_REVIEW_LITERATURE.md), [atlas](PROOF_REVIEW_ATLAS.md)
and [dyadic tails](PROOF_REVIEW_EDGE.md). Exact source identities and translations
are retained in the corresponding literature records and [source notes](SOURCES.md).
The universal root-simplicity problem remains open. No independent proof review,
new Lean execution, global novelty, exclusive method or speedup is asserted.

All preceding run and cross-check directories are preserved. The failed
`cross-check-004` is distinguished from its accepted replacement
`cross-check-004b`; neither is substituted for the final 007 evidence.

The publication manifest in `manifests/euler-packets-worked-example-2026-10-29.json`
binds the manuscript, program, reviews, run evidence and this completion report.
Captured runner files have newline conversion disabled in `.gitattributes`,
preserving their exact bytes across Windows and Linux checkouts. Original-project
terms are in `LICENSE.md`; third-party references retain their own terms.
