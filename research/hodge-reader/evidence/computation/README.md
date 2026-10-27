# Series 06 computation evidence

All recorded scientific runs completed. Their mathematical scope is finite and
stated separately from the geometric arguments. The 18 original projector
illustrations use floating arithmetic. They are identified as numerical toys.

Use `verifieddata.json` for the publication's exact count and range mapping.
Use `COMPUTATION_AUDIT.md` for interpretation and limitations. Raw results,
stdout, stderr and schema-version 2 provenance manifests are in `runs/`.
Every manifest was validated with input and output hashes against this directory.
The combined record is `validation.json`.
The portable driver was also run end to end in a separate fresh destination.
All 15 runs completed and their scientific outputs matched after excluding
timestamps, elapsed times and displayed commands. See `portable_validation.json`.

Run the reviewed commands in a new destination from any working directory:

```bash
python3 /absolute/path/to/computation/replay_all.py --destination /absolute/path/to/new-hodge-replay
```

The destination must not exist. The driver copies reviewed code and inputs,
runs a fixed list of argv commands, applies bounded resource limits and validates
each new manifest. It never executes commands read from manifests. Python 3.12.14,
SymPy 1.14.0, NumPy and Matplotlib were available for this edition. The original
sources declare Python 3.10 or later where applicable.
The copied contracts record the versions installed in the replay environment.

Validate the shipped evidence directly:

```bash
python3 helpers/validate_manifest.py runs/carrier70/manifest.json --root .
```

Repeat for each `runs/*/manifest.json` while working in this directory.
For an individual experiment, take its reviewed fixed command from
`replay_all.py`, supply the matching contract and inputs, and choose a new
runner output directory. Existing scientific results are never overwritten.

Legacy August code is copied unchanged in `work/legacy/`.
`checks/replay_legacy.py` remaps three historical absolute output paths in the
execution AST and directly invokes the odd-prime audit function. No mathematical
expression is changed. `checks/replay_toys.py` invokes only the original numerical
checks and does not generate the historical figures.

The K23 archived verifier only asserts stored JSON flags. The new independent
`checks/regenerate_k23.py` reconstructs all 364 certificates from seven recorded
representatives and checks their exact finite identities. This improves the
finite evidence without supplying the missing Chow correspondence.

The 89,478,480 weighted dyadic identities through 2^14 are historical data.
This edition independently verifies87,376 coefficient identities through 2^9
and replays the complete implemented dyadic packet enumeration through 128.
The historical general balanced-packet census through degree100 is preserved
and was not independently re-enumerated.
