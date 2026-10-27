# AVOC Formal v0.28.0

Cumulative semantic-feedback source release with a new dimension-typed affine domain.

**Start:** FORMAL_THEORY.md, PROOF_BOUNDARY.md, REPRODUCE.md.

The new block has 52 theorem/lemma declarations. The complete library has 1,499, including helpers and examples. Its 156 local compilation targets passed against the exact pinned external caches. The 135 inherited non-audit modules are unchanged. The separate v0.26 rewrite-transfer branch remains separate.

New modules:
- AVOC/AffineSignature.lean
- AVOC/TypedAffineProgram.lean
- AVOC/AffineFusion.lean
- AVOC/AffineExamples.lean
- AVOC/AffineCodec.lean

New read-only runtime: tools/run_affine.py, executing tools/AffineMain.lean.

Example after setup:

    python tools/run_affine.py examples/affine/fusion.json

The returned normal form is proved equivalent on all inputs. Tariff comparisons do not assert that dense normalization always speeds execution up. No arbitrary code is installed or proof-store state changed.

Runtime binaries and external caches are omitted. See the exact pins and trust boundary in REPRODUCE.md.
