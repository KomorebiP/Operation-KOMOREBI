# Reproduction

Required environment:

- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`;
- Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`;
- compiled dependency closure restored from the three archives under `history/`.

The retained verifier is `work/scripts/verify_final.py`.  Its absolute paths
reflect the original execution workspace and should be adjusted after extraction.
It performs two clean source builds, byte comparison, source scan, axiom audit,
negative controls, and frozen-input checks.

Payload integrity alone can be checked with:

```bash
python3 verify_payload.py
```
