# Paper IX: finite computation evidence

Five accepted bounded runs are preserved here. Every version 2 manifest passed
the bundled validator against the unchanged project inputs and scientific
outputs. These runs provide finite implementation evidence; the universal
proofs and inherited Lean compiler evidence remain separate.

| Evidence | Exact scope | Result |
|---|---|---|
| Independent finite gate | 116,492 assertions in nine explicitly bounded groups | PASS |
| Baseline regression replay | Eleven unchanged standard-library regression `run()` functions from the pinned baseline ZIP | PASS |
| Earlier row exploration | 312 dyadic congruence cases and one odd-prime boundary | Historical stdout reproduced byte for byte |
| Research explorations | 1,088 packet displacements; 861 binary kernel formulas; 41 top edges; four cancellation examples | Scientific result files reproduced byte for byte |
| Recovered hypothesis controls | Three insufficient-hypothesis counterexamples; two example corrections accompany the research replay | All five invalid statements rejected |

The independent gate rejects 19 additional invalid strengthenings. The earlier
row exploration repeats one of its odd-prime boundaries. Counts from baseline
regression files mix cases, rows, families, metadata and invalid-input checks;
they are retained under their original field names and are not added into a
theorem or experiment count.

The independent gate uses Python arbitrary-precision integers and
`fractions.Fraction`, with exact comparisons throughout. Its ranges include
zero dimensions, empty equation lists, zero steps, zero truncation tails,
modulus one, composite-modulus fibers, negative rational valuation bounds and
the strict weighted lifting boundary. Prime-field rank cardinalities are
asserted only over the prime moduli. The original baseline gates use their
literal ranges and deterministic seeds. Some original parameter-validation
helpers use a floating square root to bound trial division on their fixed
small primes; their mathematical coefficient arithmetic and comparisons are
exact.

The weighted finite checks handle the precision loss from a nonunit Jacobian:
there can be `p^s` residue roots modulo `p^N` agreeing modulo `p^(N-s)`. This
does not count distinct completed roots. Finite tower and chart checks do not
construct an infinite p-adic endpoint or establish analytic regularity.

The five recovered-text controls concern the broader historical Annals
exposition. They identify missing positive-depth or integrality hypotheses,
a printed modulo-seven prefix, and an even-subsequence restriction. They do
not refute the scoped consolidated manuscript or an accepted Lean declaration.
The mathematical audit records the corrected statements and source locations.

## Files to read

- `COMPUTATION_AUDIT.json`: final scope and totals, with the inherited compiler frontiers kept separate.
- `exact_finite_run/results.json`: every group’s range and all 19 concrete controls.
- `baseline_regressions_run/results.json`: actual source hashes, seeds, function calls and per-gate counts.
- `BASELINE_ADDITIONAL_COMPARISONS.json`: additional third-block scientific fields and fifth-block fingerprint comparisons.
- `archival_controls_run/results.json` and `research_replay_run/results.json`: the five recovered-text controls.
- `MANIFEST_VALIDATION.json`: successful validation of all five primary version 2 records.
- `development/DEVELOPMENT_NOTES.json`: corrected draft failures and the superseded unpinned dry output. These are not accepted evidence.

The original research files retain their checkpoint wording that a candidate
was not yet formalized. The later preserved Lean frontiers determine the final
proof status; replaying those older files does not change their wording.

## Validate the recorded evidence

From the edition root, for example:

```sh
python3 verification/computation/vendor/validate_manifest.py \
  verification/computation/exact_finite_run/manifest.json --root .
```

Use the same command for `early_rows_run`, `archival_controls_run`,
`research_replay_run` and `baseline_regressions_run`. The validator and bounded
runner are byte-identical copies of the mathbox computation-audit helpers;
their origin and hashes are in `vendor/PROVENANCE.json`.

## Reproduce the computations

Use fresh output paths. These are ordinary Python standard-library commands;
they do not invoke the separately supplied Lean kit.

```sh
python3 verification/computation/scripts/exact_finite_gate.py \
  --output /absolute/path/to/new-independent-results.json

python3 verification/computation/scripts/replay_early_rows.py \
  --source source/consolidated/PRSC_IX_Consolidated_Manuscript/historical/initial_strengthening/reproduce_early_rows.py \
  --recorded-log source/consolidated/PRSC_IX_Consolidated_Manuscript/historical/initial_strengthening/reproduction.log \
  --output /absolute/path/to/new-early-results.json

python3 verification/computation/scripts/archival_hypothesis_controls.py \
  --output /absolute/path/to/new-archival-results.json
```

For the next two wrappers, first create a new empty output directory:

```sh
python3 verification/computation/scripts/replay_research_and_archival_examples.py \
  --source-root source/consolidated/PRSC_IX_Consolidated_Manuscript \
  --output-dir /absolute/path/to/new-research-output

python3 verification/computation/scripts/replay_baseline_regressions.py \
  --archive source/consolidated/PRSC_IX_Consolidated_Manuscript/baseline/PRSC_IX_v0.11.0_Nishibuchi_Completion.zip \
  --output-dir /absolute/path/to/new-baseline-output
```

The research kernel checker writes beside its source, so its wrapper runs a
byte-identical copy inside the new output directory. The baseline wrapper
copies only the eleven reviewed source members and invokes their `run()`
functions. Historical archives and outputs remain unchanged.

To capture another version 2 run, use the bundled `run_experiment.py` with a
copy of the appropriate `*_contract.json`, repeated `--input` paths matching
its `execution_artifacts`, a new project-relative `--output` directory, and
explicit `--result` files beneath it. Each recorded primary manifest retains
the actual child argument vector, software, limits and result paths. Update
the copied contract’s software versions if the new environment differs; keep
the original contracts and records intact.

All primary runs used one CPU core, a cooperative one-thread limit, explicit
wall-clock and log caps, and POSIX memory/CPU caps. The precise effective
limits are recorded in each manifest. No Lean/Lake compiler, SymPy, pytest,
unittest session, hardware benchmark or infinite p-adic construction was run
as part of this computation audit.
