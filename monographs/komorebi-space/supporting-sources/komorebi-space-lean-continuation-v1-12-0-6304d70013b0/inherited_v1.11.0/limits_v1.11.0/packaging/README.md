# Lean continuation packaging

`package_release.py` uses only the Python standard library. It packages a frozen,
accepted continuation; it does not update the formal sources, status, manuscript,
or acceptance evidence. The final build must wait until the release ledger is
accepted and all independently reviewed evidence is frozen.

From the workspace root, validate the pinned predecessor without creating output:

```sh
python limits_v1.11.0/packaging/package_release.py --parent-only
```

After final acceptance, validate the complete proposed release without writing
output:

```sh
python limits_v1.11.0/packaging/package_release.py --check-only
```

Then create the release once:

```sh
python limits_v1.11.0/packaging/package_release.py
```

Default inputs are `integration/runs/clean_limits_01` and
`reviews/WR08_WR09_WR16_MATH_AUDIT.md`, relative to this continuation. Explicit
`--run` and `--type-audit` options accept another frozen run/review within the same
continuation. `--parent-archive`, `--parent-expanded`, and `--output-dir` permit
explicit filesystem locations. The predecessor hash and release names are fixed.

Outputs are the expanded `Komorebi_Space_Lean_Continuation_v1.11.0` directory, its
ZIP, `Komorebi_Space_Lean_Progress_v1.11.0.md`, and the separate
`Komorebi_Space_Lean_Delivery_Verification_v1.11.0.json`, all under `output/` by
default. Existing destinations are never overwritten. A failed build may leave
partial new destinations for diagnosis; it never modifies accepted history.

The release contains:

- `formal/`: the complete accepted source-only project snapshot, including pins,
  entrypoints, controls, and audit inputs.
- `limits_v1.11.0/`: current proof sources, every development attempt source/log/
  receipt, records, final reviews, and integrated evidence.
- `inherited_v1.10.0/`: every one of the predecessor's 4,827 payload files plus
  its checksum manifest, preserved byte for byte after comparison against the
  pinned predecessor ZIP itself.
- Current root README, progress records, verification summary, coverage, and next
  research block, copied from the accepted release files.
- `SHA256SUMS.txt`: hashes of every file except that manifest itself.

Compiled project objects, `build` directories, Python caches, and portable runtime
binaries are excluded. The preceding PDF remains historical under the inherited
tree. No updated PDF is created or claimed by this Lean-only continuation.

Acceptance checks bind the run receipt, postflight, source snapshot, assembly,
overlay, verifier helpers, axiom export, command logs, complete new type exports,
ledger, and acceptance reviews. The final type audit must contain the receipt,
axiom-export, and every new production-source hash. The package checks all ZIP
paths, rejects symlinks and duplicate members, verifies CRC and every payload hash,
and derives production-module and compilation-target counts from the actual
accepted sources. Historical recorded absolute paths remain evidence of the
original run; they are not rewritten into a claim that an old run occurred at a
new location.

Focused adverse-input checks are reproducible with:

```sh
python limits_v1.11.0/packaging/test_package_release.py
```

The final package is subject to a separate independent archive review. This helper
does not substitute its own payload checks for that review.
