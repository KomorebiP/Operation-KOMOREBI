# Block 51 verification status

The exact final new computation passed and reproduced all declared counts.
Six predecessor computations were also replayed successfully, with results
identical to the frozen JSON. Package-wide replay and integrity records
are provided separately so their exact commands and timestamps remain
machine-readable.

## Levels of evidence

**Written proof:** the local matrix theorem, its cup refinement and sharp
families, and the conditional arithmetic bridges and support consequences.
These received fresh self-review by the same assistant. No independent
second-agent/human acceptance or new Lean certification is claimed.

**Exact finite computation:** Python 3.13.5, standard-library integer and
Fraction arithmetic. Final new source hash:
`1961358e3e7cfd720a25e4a0a2d66204ad565564507b94ecfb121f2dedc827a5`.
The initial final-source run exited 0. Its result hash is
`cb785e829622ad6efdce8eca43996c584ff861b0fa4aec88bc3c2214a5b272b6`.
See `verification/development_final_run/manifest.json` for actual command,
start, elapsed time, source-before/after hashes and limits.

Counts: 252 integer sharpness cases; 8640 independent quadratic basis
cases generated with 1530 admissible; 252 additional quadratic sharpness
cases; 17 node identities; 24,000 selector equivalences; the declared
prime/residue computations; all expected negative controls rejected.
The targeted quadratic family includes 72 nonzero upper-endpoint cases.
The original grid's 7110 excluded inputs and zero nonzero-endpoint count
remain visible instead of being silently removed from the report.

**Source verification:** exact primary locators and PDF page inspections
for the quotient-polarization, graph-period and cyclotomic class-number
inputs, plus a precisely delimited node-criterion check. See
`source_records/SOURCE_CHECK.md`. This is not a full review of every
inherited arithmetic source or a novelty survey.

**Recovery/provenance:** 284 Block 49 payload checksums and 12 Block 50
checkpoint checksums matched. The Block 50 base hash equals the actual
recovered Block 49 ZIP hash. Both CRC checks passed. Frozen work
subdirectories and original archives remain unchanged; only the root
README and checksum manifest are intentionally replaced for navigation.

## Reproduction and boundaries

Use `python verify.py --replay-predecessors` from the extracted root.
The report records package integrity before/after, fresh process outputs,
comparison to pinned results, code/fixture hashes, environment and bounds.
Successful finite replay is not a mathematical proof of Beal or the
universal local theorem. There is no hidden Lean build or independent
review behind these status labels.

The failed historical independent-review request and the corrected test
coverage limitation are documented in `DEVELOPMENT_FAILURES.md`.
