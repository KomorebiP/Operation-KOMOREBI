# Komorebi Hodge continuation v0.2.0

**Start with `PROOF.md`.** This release does not prove the general Hodge conjecture.

It provides a global optimization certificate for the preceding degree-70 matrix, an all-parameter obstruction to making that matrix method universal, and explicit complete-intersection cycles with exact nonzero periods for the known Aoki five-phase standard family. Neither the special-case geometry nor the universal proof in the note has been checked in Lean or independently reviewed.

## Reproduce the exact computations

Use Python 3.10 or newer and SymPy. The recorded run used Python 3.13.5 and SymPy 1.14.0. From this directory:

```sh
python checks/verify_all.py
```

Expected result: 137 grouped assertions pass. The verifier overwrites the three result JSON files and records a fresh timestamp and runtime. It does not require SciPy, internet access, GPUs, or the historical discovery environment. A passing run is not a formal verification of the geometric proof.

The script verifies the preserved predecessor ZIP hash but does not rerun its separate verifier. That separate 24-check run was completed in this session; its output is retained under `results/predecessor_replay/`.

## Contents

- `PROOF.md`: complete manuscript argument, conventions, and limits.
- `checks/`: exact verifier and frozen capacity inputs.
- `results/`: exact primal/dual certificates, cycle examples, run reports, and predecessor replay.
- `SOURCES.md`: verified external theorem contracts and known-family attribution.
- `AUDIT.md`: execution scope, proof boundaries, failures, and excluded exploratory input.
- `MANIFEST.json` and `SHA256SUMS.txt`: provenance and file-integrity records.
- `predecessor/`: unchanged v0.1.0 ZIP.
- `experiments/`: discovery evidence. These are not the authoritative replay and include one explicitly rejected non-Hodge input.

No universal result is inferred from the finite range q=2 through 64. The universal no-go and determinant identities have separate proofs in `PROOF.md`.
