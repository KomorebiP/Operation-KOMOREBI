# Komorebi Representation Calculus v0.2

A proof-carrying observation-discovery prototype, with a Lean-checked generic
semantic core and an automatically exported exact finite quotient.

Start with `FORMAL_NOTE.md`, `FORMALIZATION_COVERAGE.md`, and `RESULTS.md`.
The original v0.1 ZIP is preserved in `history/`. This is not p-adic Block 16.

## Reproduce

Python 3.10+ and its standard library suffice for the computation checks:

```sh
python tools/verify_integrity.py
python tools/run_python.py
python tools/validate_manifest.py COMPUTATION_MANIFEST.json --root .
```

To reproduce the Lean audit, supply the binary from Lean 4.34.0-rc2:

```sh
python tools/verify_lean.py --lean /path/to/toolchain/bin/lean
python tools/validate_manifest.py LEAN_MANIFEST.json --root .
```

No Mathlib dependency is used by the five new Lean modules. The runtime/cache is
not bundled. `lean-toolchain` pins the tested version. The audit creates a fresh
local build directory and rejects unexpected axioms and negative controls.
Audits update their result/log/manifest files; the frozen ZIP is unchanged.
Check package integrity before rerunning, since new execution timestamps differ.

## Use the discoverer

```python
from discover import discover, encode, compressed_output
from checks.check_certificate import check

source = {
    "schema": "finite-linear-profile-v1",
    "p": 2, "r": 4, "dimension": 2,
    "actions": [[[1, 4], [0, 1]]],
    "observations": [[1, 0]],
    "initial_interface": "all_states",
    "word_order": "left_to_right",
}
result = discover(source)
certificate = result["certificate"]
check(source, certificate)  # Supply the expected source, not only an untrusted hash.
y = encode(certificate, [7, 3], 16)
assert compressed_output(certificate, y, [0], 0, 16) == 3
```

All initial states are part of the task. The source must be a complete linear
system over the declared prime-power residue ring. The algorithm is not learning
an unknown transition function from partial samples.

## Export one retained instance to Lean

```sh
python tools/export_lean.py \
  certificates/hidden_p2_r2_d4.source.json \
  certificates/hidden_p2_r2_d4.certificate.json \
  formalization/GeneratedProfile.lean
```

The finite exporter is deliberately capped. Large instances use symbolic matrix
certificates and their written proof reduction, not a falsely claimed Lean build.

## Trust boundary

Generic semantics and the explicit generated example are Lean-checked. The Python
programs and the universal new matrix-certificate adapter are not Lean-verified
executables. No autonomous discovery benchmark, historical novelty, or comparison
against another AI system is claimed. See the coverage and failure records.
