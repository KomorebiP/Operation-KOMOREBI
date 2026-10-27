# Reproduce AVOC v0.40.0

Use Linux x86-64 or WSL and Python 3.10+. The archive excludes compiled project
objects, the Lean runtime, and external dependency caches. Use the separately
preserved portable Lean kit with all nine revisions in lake-manifest.json.

- Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
- mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

Check the delivered payload before regenerating evidence. The baseline ZIP is
needed only to independently repeat the inherited-byte comparison.

```bash
export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python3 tools/check_manifest.py
python3 tools/check_inherited_v040.py /absolute/path/AVOC_Formal_v0.39.0.zip
python3 tools/inventory_v040.py
python3 tools/verify_v040.py --prepare
python3 tools/build_v040_parallel.py --seconds 45 --workers 3 --per-target-seconds 180
```

Repeat the final build command, waiting for each invocation to exit, until it
prints CURRENT 217 / 217 REMAINING 0 FAILED []. Do not repeat --prepare between
slices: it removes local build objects. A file lock prevents overlapping release
build invocations. Resumption accepts only current source/import/output/log hashes.
The external dependency caches are retained and their exact revisions checked.

```bash
python3 tools/verify_v040.py --audit --seconds 600
python3 tools/run_negative_v040.py --seconds 45 --workers 2 --per-file-seconds 90
python3 tools/source_scan_v040.py
```

Repeat the negative command until CURRENT 126 / 126. Every negative must exit
with an ordinary Lean proof rejection, not a crash, timeout, or recognized
setup/parser/resource failure. Expected axiom reports are exactly 2,199 named
theorem/lemma declarations, including inherited private helpers; only propext,
Classical.choice, and Quot.sound are allowed. The five new modules add 77 names.

The release includes the completed exact oracle and its source-pinned bounded
execution manifest. To repeat the calculation while retaining the release's
original bounded-run provenance, write a separate result:

```bash
python3 checks/test_observation_process.py --output results/v0.40.0/oracle_replay.json
python3 tools/run_inherited_regression_v040.py --case all
```

The oracle has no random sampling or external service calls. Its 100 finite cases
compare exact latent-table and attempt-tree distributions, prefix counts,
scheduled calibration, and the actual parser. See OBSERVATION_EXECUTABLE.md for
the precise range and counterexamples. Its result is independent of run timing.

The inherited runner replays five checks: robust quote oracle, selected artifact
workflows, recovery, lazy staged execution, and calibration with actual Lean
cross-checks. Evidence and selected fixture paths are relocated into a unique
v0.40 run directory; original check/runtime sources and historical evidence stay
unchanged. Both original and adapted check source hashes are recorded.

```bash
python3 tools/release_check_v040.py
python3 tools/package_v040.py --output /chosen/AVOC_Formal_v0.40.0.zip
python3 tools/check_manifest.py
```

The final gate recomputes membership and freshness of positive builds, named
axiom reports, negative failures, forbidden-source scan, inherited identities,
finite oracle, bounded-run manifest, independent review, and fresh inherited
regressions. Empty/malformed required evidence does not pass. Changes to reviewed
mathematical or oracle source require renewed review, not just edited hashes.
Packaging reruns that gate, writes the complete SHA256SUMS.txt, and checks archive
CRC, unique exact file membership, every payload digest, and source stability.
The ZIP receives a separate SHA-256 file and package-verification report.

The supported calibration command remains:

```bash
python3 tools/calibrate_quote.py examples/calibration/n500_k400_grid1000.json \
  --plan examples/robust_quote/uncertain_plan.json
```

This evaluates a new plan without running external warm/cold operations or
mutating an active durable checkpoint. The existing schema is documented in
examples/calibration/README.md; new observation fixtures are under
examples/observation_process. Read PROOF_BOUNDARY.md before interpreting any
statistical or controller guarantee.
