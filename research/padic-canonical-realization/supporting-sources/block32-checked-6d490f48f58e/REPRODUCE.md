# Reproduce Block 32

## Retained evidence (does not execute Lean)
From this extracted directory:

```bash
PYTHONDONTWRITEBYTECODE=1 python verify_release.py
python validate_manifest.py COMPUTATION_MANIFEST.json --root .
```

The first command is read-only and checks every final command receipt, unchanged
source snapshots, expected negative diagnostics, predecessor source preservation,
complete declared and environment axiom coverage, compiled artifact counts, the
finite audit, and the checksum ledger. It is not a fresh formal compilation.

## Fresh exact-pinned compilation
A matching Lean4.34.0-rc2 portable runtime and matching dependency cache are required.
The toolchain/cache itself is not included in this archive. Its recovered archive
SHA256 is f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7.

On a Linux environment containing that runtime:

```bash
export KOMOREBI_LEAN_RUNTIME=/absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
export PATH="$KOMOREBI_LEAN_RUNTIME/toolchain/bin:$PATH"
export PYTHONDONTWRITEBYTECODE=1
python verification/prepare_offline.py "$KOMOREBI_LEAN_RUNTIME"
python verification/run_final.py
```

prepare_offline checks the Lean identity and every manifest dependency's git revision,
then links the cache. It never replaces a real package directory. run_final removes
only this project's .lake/build, not the dependency cache. Its expected negative
controls have nonzero exits by design. Do not label any unrelated nonzero exit a
successful control. The per-process limit defaults to 900 seconds and is configurable
with JOB_TIMEOUT. It is an execution limit, not a mathematical complexity theorem.

Fresh runs overwrite the retained results and break the old sealed checksum ledger.
Work in a separate extracted copy. Do not reseal or promote unless every phase has
passed, input hashes are unchanged, and the evidence aggregator covers all theorem
names. Source manifest, final plan, and theorem inventory are frozen execution inputs.

## Numerical reference
Python3.13.5 and SymPy1.14.0 were used. Run:

```bash
python verification/audit_presentation.py
```

The exact reference uses integer HNF/Smith proposals and explicit certificate checks.
Full stress-case matrices are saved in results/audit_presentation.json. This reference
is not a proved executable refinement of Lean's noncomputable coordinate choice.
