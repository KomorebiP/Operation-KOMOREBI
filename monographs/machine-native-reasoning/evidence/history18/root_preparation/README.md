# Machine-Native Reasoning — positive packet mixtures

Formal companion 0.18.0. Author: Komorebi P.

This cumulative project targets Core 2.5 of the unchanged Reviewed Core 0.2. The
previous accepted correspondence is 25/27. The configured map has 26 explicit
source targets, including both sectors of Core 2.5. This preparation record is not
an admission receipt: acceptance requires the completed current-source and
separately extracted-source gates and their comparison. See `release/` for any
subsequently generated acceptance record, report and exact continuation ledger.

## Mathematical entry points

* `Komorebi.MachineTheory.PositivePackets.source_core25`: finite positive-cone
  mixture, strict mass, zero-packet equivalence and positive-only normalization.
* `Komorebi.MachineTheory.PositivePackets.Coordinate.source_core25_coordinate`:
  positive complete idempotents on the coordinate cone are disjoint selectors.
* `Komorebi.MachineTheory.PositivePackets.Coordinate.classification_iff`: the
  converse characterizes exactly these coordinate-selector families.
* `Komorebi.MachineTheory.PositivePackets.Transport.source_coordinate_change`:
  simultaneous transport of cone, mass and operators through a linear equivalence.

The general mixture theorem requires neither idempotence nor finite dimension.
The classification has finite coordinates and assumes the standard nonnegative
cone. Signed coordinates may represent valid probabilities in a transported cone.
The positive-index type prevents a zero-weight packet from becoming a unit-mass
state through Lean's totalized inverse. Empty indices and zero-dimensional
coordinate spaces are not silently excluded.

## Reproduction

Use the stored portable Lean 4.34.0-rc2 runtime and pinned nine repositories.
Do not substitute an online newest toolchain. Set the runtime location and run:

```sh
export KOMOREBI_LEAN_RUNTIME=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python scripts/supervise.py --runtime "$KOMOREBI_LEAN_RUNTIME" --out evidence/local18 --whole-timeout 1800
```

The output directory must be new. Each Lean command has a 45-second wall limit,
one worker, a 4096 MiB internal limit, and warnings treated as errors. The verifier
cold-builds every production module, checks the actual source-facing interfaces,
audits transitive axioms, replays substantive modules through Lean's own kernel,
checks the complete rejection manifest, and hashes actually imported dependencies.
It does not rebuild Mathlib or independently authenticate the origin of its cache.

`python scripts/check_positive_packets.py --out /tmp/positive-packets.json`
runs the separate exact rational regression. Finite checks do not replace proofs.
Runtime recovery tools and installation receipts are supplied without binaries.

## Preservation and delivery

All 71 predecessor substantive modules and five original source-book files are
pinned in `PREDECESSOR.json`. The complete prior archive was intact and verified.
Earlier Core 8.3 historical recovery gaps remain documented in predecessor history;
they are not a new loss of the current formal source. The original monograph is
not rebuilt in this proof task. Core 3.2 remains the next selected target.

Source code and machine-readable original material retain MIT licensing, and
original prose retains CC BY 4.0, with upstream terms and exceptions preserved.
No runtime or standalone font binaries are included. See the retained notices.
