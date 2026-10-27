# Reproduce AVOC v0.29.0

Linux x86-64/WSL; Python 3.10+; Lean 4.34.0-rc2 (6a10ac8c22beadecabdbb0919c2b50214762f91d), mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Nine dependency revisions are frozen in lake-manifest.json. Runtime and compiled caches are excluded from this source release.

```
export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python tools/check_manifest.py
```

Check the original payload manifest before regenerating records.

## Build the new checker only

```
python tools/lean_one.py AVOC/AffineSignature.lean
python tools/lean_one.py AVOC/TypedAffineProgram.lean
python tools/lean_one.py AVOC/AffineFusion.lean
python tools/lean_one.py AVOC/AffineCodec.lean
python tools/lean_one.py AVOC/AffineFactorization.lean
python tools/lean_one.py AVOC/AffineFactorChoice.lean
python tools/lean_one.py AVOC/AffineFactorCodec.lean
python tools/lean_one.py tools/AffineFactorMain.lean
```

## Generate, check and compare

```
python tools/factor_affine.py examples/factorization/rank_one.json
python tools/factor_affine.py examples/factorization/rank_one_short.json
python tools/factor_affine.py examples/factorization/fusion.json
python tools/factor_affine.py examples/factorization/bottleneck.json
python tools/factor_affine.py examples/factorization/identity.json
```

Config: `program` is the inherited affine AST; `calls` is a declared integer deployment count; `credit` bounds nominal exploration/checking tariffs; optional `inputs` are exact vectors. Dimensions 0..8, coefficients 0..4, source depth <=24 and <=256 nodes; calls <=1,000,000; credit <=100,000,000. The wrapper does not permit an input generation-charge override. Source/compiled-output fingerprints are checked, not treated as remote attestation.

`--certificate-out /new/path.json` explicitly exports the checker request, without overwriting an existing file. Raw checker wire:

```
["affine-factor-f5-v1", referenceAST,
 [width, firstMatrix, firstBias, secondMatrix, secondBias, U, V],
 calls, declaredGenerationCharge, credit, inputVectors]
```

Run the Lean entrypoint directly only after satisfying its field/shape/source and cost-input contracts. A failed certificate does not establish that no factorization exists.

## Full local release audit

```
python tools/inventory_v029.py
python tools/verify_release.py --prepare
python tools/build_parallel.py --seconds 15 --workers 3
```

Repeat the last bounded build until 161/161 current targets pass. Do not prepare again between slices. Dependencies are retained. Then:

```
python tools/verify_release.py --audit
python tools/verify_release.py --negative
python checks/test_affine_factorization.py
python tools/summarize_v029.py /path/to/AVOC_Formal_v0.28.0.zip
python tools/audit/validate_computation_manifest.py results/v0.29.0/computation_manifest.json --root .
```

There are 80 negative tests; import failures/timeouts are not substantive rejections. The exact regression uses seed 20260913, exhaustive 2x2 linear matrices and bounded structured/random affine cases. Logs/current source/import hashes are retained. The metadata validator is the inherited local v1-only adaptation, not a proof of mathematical interpretation. Its collector timing covers evidence collection only, not the earlier builds or tests.

`tools/package_v029.py` regenerates the payload hashes and ZIP after an audited run. Generated test evidence changes manifest-covered bytes. The package excludes `.lake`, `.git`, Python caches, compiled outputs, runtime and transient PID files.
