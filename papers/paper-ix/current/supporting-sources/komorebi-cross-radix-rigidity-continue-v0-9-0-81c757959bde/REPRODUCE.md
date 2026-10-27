# Reproduce v0.9.0

Use the pinned portable Lean runtime for Lean `4.34.0-rc2` and Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

Run:

```bash
bash VERIFY_V090.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The verifier first checks all v0.8 source hashes, then rebuilds the required v0.8 dependency chain and every new v0.9 module under `-DwarningAsError=true`, scans for placeholders/custom axioms, and prints the v0.9 axiom audit.
