# Reproduce AVOC v0.28.0

## Exact environment

Linux x86-64 or WSL, Python 3.10+, Lean 4.34.0-rc2 commit 6a10ac8c22beadecabdbb0919c2b50214762f91d; mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Nine dependency revisions are recorded in lake-manifest.json. Runtime and compiled caches are omitted from the ZIP.

    export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
    python tools/check_manifest.py

Check the original manifest BEFORE rebuilding or changing evidence.

## Full local build

    python tools/inventory_v028.py
    python tools/verify_release.py --prepare
    python tools/build_parallel.py --seconds 15 --workers 3

Repeat only the last command until it reports 156/156 current targets. Do not prepare between slices. A host interruption is not success: stop any leftover child and rerun unfinished targets. Local import output hashes are checked. External sources/caches are not rebuilt.

    python tools/verify_release.py --audit
    python tools/check_all_negative.py
    python checks/test_affine.py
    python tools/summarize_v028.py --baseline /path/to/AVOC_Formal_v0.27.0.zip

The negative helper resumes already-current records within the v0.28 result directory. The final collector independently checks their current import/output/source/log hashes. For an entirely new negative run, remove only results/v0.28.0/negative_* before invoking the helper.

## Minimal new-domain build

The following five source modules and entrypoint are sufficient for the new CLI; the rest of AVOC need not be rebuilt for these read-only commands:

    python tools/lean_one.py AVOC/AffineSignature.lean
    python tools/lean_one.py AVOC/TypedAffineProgram.lean
    python tools/lean_one.py AVOC/AffineFusion.lean
    python tools/lean_one.py AVOC/AffineExamples.lean
    python tools/lean_one.py AVOC/AffineCodec.lean
    python tools/lean_one.py tools/AffineMain.lean

    python tools/run_affine.py examples/affine/fusion.json
    python tools/run_affine.py examples/affine/bottleneck.json
    python tools/run_affine.py examples/affine/compare.json

`examples/affine/bad_dimensions.json` is intentionally rejected. Exit 2 means malformed/unsupported input or execution failure, not a proved mathematical theorem.

The wrapper checks source and output compilation fingerprints to reject stale local builds. This is not authenticated provenance against a malicious host. It runs the actual Lean normalizer, not the Python oracle.

## Wire schema

Programs are arrays:

    ["map", inputDim, outputDim, rowMajorMatrix, bias]
    ["id", dimension]
    ["seq", firstProgram, secondProgram]
    ["sum", firstProgram, secondProgram]

Coefficients are canonical GF(5) residues 0..4. Composite shapes must agree. Requests:

    ["affine-normalize-f5-v1", program, deploymentCalls, inputVectors]
    ["affine-compare-f5-v1", program1, program2]

Bounds: dimensions <=8 (including zero), parse depth 24, AST nodes <=256, deployment calls <=1,000,000, vectors <=128, file size <=4 MiB, batched requests <=256. `--batch` reads an array of requests and prints JSON lines. No arbitrary source, file writes or deployment is requested by this interface.

## Evidence scope

The seeded regression uses Python homogeneous augmented-matrix semantics and an independent direct AST evaluator. Low-dimensional sampled programs are evaluated at all inputs. The seeded program family is not every possible syntax tree. The soundness/completeness theorems are separately proved in Lean.

The final local rebuild, full axiom audit and complete negative suite were rerun. Historical runtime crash/store/retry suites were not rerun. The present executable testing is exact GF(5), not floating-point or empirical AI performance.

## Packaging

    python tools/package_v028.py
    python tools/check_manifest.py

Regenerating evidence changes manifest-covered bytes. Do not write a manifest's own check log into a file that it already hashes. Historical root documents are preserved under history/v0.27.0_release_top, and their old hashes are not current evidence.
