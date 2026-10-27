# H12 principal divisor transport, v0.13.0

Start with PROOF.md, then FORMALIZATION_SCOPE.md. The main gamma special-value
identity is still unproved. This release supplies the actual principal
correction's full divisor, finite theta transition equations, exact zero
normalization and a divisor-level obstruction to naive conjugation cancellation.

Reproduction requires Python with SymPy and mpmath and the user's pinned
Lean 4.34.0-rc2 runtime. The multi-gigabyte runtime is NOT included.

```bash
python checks/validate_manifest.py MANIFEST.json --root .
python checks/exact_checks.py
python checks/verify_lean.py --lean /path/to/pinned/toolchain/bin/lean
for digits in 40 70; do
  for stage in anchor first second divisor; do
    python checks/numerical_checks.py --digits "$digits" --stage "$stage"
  done
done
```

Validate shipped hashes BEFORE reproduction: runs overwrite their own evidence
files and change timestamps. A rerun is not expected to retain the shipped
manifest's output hashes. The validator is the retained, disclosed version-one
adaptation from the preceding archive; it authenticates files and provenance
structure, not mathematical claims.

Only the new 20-theorem core is freshly built. The predecessor archive preserves
all earlier sources and their historical evidence without asserting a fresh
full replay. No numerical comparison with U_alg is included.
