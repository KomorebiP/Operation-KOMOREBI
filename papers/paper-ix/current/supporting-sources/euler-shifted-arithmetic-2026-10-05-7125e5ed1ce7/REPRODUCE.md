# Reproduction

Run these commands from this package's root. Python3 with its standard library
is sufficient. The authoritative current manifests and their roots are listed
in `shifted_obstruction/CURRENT_EVIDENCE.json`; retained superseded development
manifests are explicitly excluded there.

## Validate current execution evidence

```bash
python3 audit_helpers/validate_manifest.py shifted_obstruction/root/certified_run/manifest.json --root .
python3 audit_helpers/validate_manifest.py shifted_obstruction/weighted/certified_run/manifest.json --root .
python3 audit_helpers/validate_manifest.py shifted_obstruction/moment/frozen_run/manifest.json --root shifted_obstruction/moment
python3 audit_helpers/validate_manifest.py shifted_obstruction/critical_arithmetic/certified_run_final/manifest.json --root shifted_obstruction/critical_arithmetic
python3 audit_helpers/validate_manifest.py shifted_obstruction/critical_arithmetic/newton/certified_run/manifest.json --root shifted_obstruction/critical_arithmetic/newton
```

## Replay the five current scientific checks

Create a fresh output directory, then run:

```bash
mkdir replay
python3 shifted_obstruction/root/check_regularized_moments.py --output replay/regularized.json
python3 shifted_obstruction/moment/check_moment_transfer.py replay/moment.json
python3 shifted_obstruction/critical_arithmetic/check_local_certificate.py replay/bezout.json
python3 shifted_obstruction/weighted/check_shifted_commutator.py --out replay/weighted.json
python3 shifted_obstruction/critical_arithmetic/newton/check_contact_wronskian.py replay/contact.json
```

Compare these with their current manifest-declared scientific outputs. The
weighted output records elapsed seconds for each case, so exclude only those
seconds when comparing. Every exact residue, unit, coefficient, and input hash
must match. These checks do not prove the universal theorems; their proofs are
in the accompanying notes and independently reviewed at the pinned revisions.

The prior checkpoint carries its own historical reproduction records. It is
included as an immutable dependency, not recast as fresh execution evidence.
