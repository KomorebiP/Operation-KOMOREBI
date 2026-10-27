# Reproduce the v0.11.0 multiverse branch

The branch uses the same pinned Lean 4.34.0-rc2 and Mathlib revision as v0.10.0.

Set the portable kit path and run:

```bash
export KOMOREBI_LEAN_KIT=/absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
/usr/bin/python3 scripts/verify_multiverse.py
/usr/bin/python3 scripts/validate_manifest.py verification_v0.11.0/computation_manifest.json --root .
```

`verify_multiverse.py` deliberately calls the pinned `lean` executable directly and constructs
`LEAN_PATH` from the portable dependency cache.  It does not invoke Lake.  The recorded v0.11
run is incremental: all 49 `Komorebi/Foundation/*.lean` files are hash-checked against the verified
v0.10.0 checkpoint, while all 11 new `Komorebi/Multiverse/*.lean` modules and the root module are
re-elaborated with warnings as errors.

The direct branch verifier assumes the predecessor project oleans remain available in
`.lake/build/lib/lean/Komorebi/Foundation`.  For a fully clean rebuild, first reproduce the v0.10
checkpoint using its retained instructions, then run this branch verifier.
