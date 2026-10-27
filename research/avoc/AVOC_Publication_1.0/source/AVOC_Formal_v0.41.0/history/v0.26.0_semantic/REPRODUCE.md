# Reproduce AVOC v0.26.0

## Runtime and integrity

Linux x86-64 or WSL, Python 3.10+, the pinned Lean 4.34.0-rc2 toolchain at commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`, and mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Nine exact external pins are in `lake-manifest.json`.

The release excludes the large compiler/runtime bundle, all dependency caches, and local `.olean` files. Set `AVOC_LEAN_KIT` to the portable runtime containing `toolchain/bin/lean` and `workspace/.lake/packages/`.

```bash
export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python tools/check_manifest.py
```

Check the delivered manifest before regenerating any evidence. Rechecks intentionally modify manifest-covered logs. Never repin arbitrary source changes in an existing trusted installation merely to bypass a source-drift error.

## Fresh local proofs

```bash
python tools/inventory_v026.py
python tools/verify_release.py --prepare
python tools/build_parallel.py --seconds 30 --workers 3
```

Repeat the bounded build command until it reports 144/144 current targets. Preparation deletes only local outputs and verifies external pins; do not repeat it between slices. Current imported `.olean` hashes and source hashes must agree before outputs are reused.

```bash
python tools/verify_release.py --audit
python tools/verify_release.py --negative --start 0 --count 10
```

Continue negative slices at starts 10,20,30,40,50,60 (last seven). There are 67 intentionally false files. Import errors, execution timeouts, and unfinished logs are not successful mathematical negative tests. After an outer interruption, ensure prior children stopped and rerun the first unfinished target.

The full audit names all 1,393 current declarations. Only `propext`, `Classical.choice`, and `Quot.sound` may appear.

## Read-only executable synthesis

```bash
python tools/run_semantic_synthesis.py examples/semantic/feedback.json
python tools/run_semantic_synthesis.py examples/semantic/frozen.json
python tools/run_semantic_synthesis.py examples/semantic/budget.json
python tools/run_semantic_synthesis.py examples/semantic/campaign.json
python tools/run_semantic_synthesis.py examples/semantic/all_functions.json
```

`feedback` and `frozen` return built libraries and query diagnostics. `budget` prepays each layer and reports attained depth and remaining search credit. Their diagnostic query fees are explicitly outside search credit. `campaign` funds one query and submits its selected expression through the inherited promotion authority, counting query/evaluation/switch costs in the campaign total.

Unfunded generation returns the reference or no bank without executing the layer. A funded bank with an unaffordable query reports `query_unfunded`; it does not discard the construction charge. The wrapper accepts only the fixed pure AST grammar, exact bounded integer fields, no duplicate/unknown fields, and no injected code paths.

Runtime limits: feedback/budget/campaign depth <=3; frozen depth <=2; references <=256; individual reference nodes <=127; credit <=1,000,000,000; declared calls <=1,000,000. The wrapper's process timeout is separate from the structural credit.

The new command does not alter protected stores, reload banks from files, deploy generated native code, or authorize live actions. Reusing a bank is within one executed build and its subsequent queries.

## Independent tests

The fixed comparison protocol is `checks/semantic/protocol.json`. It compares equal grammar depths and fixed semantics/index rules, with only the source of next-layer operands changed.

```bash
python checks/test_semantic_synthesis.py
python tools/record_semantic_cli.py
python tools/summarize_v026.py --baseline /path/to/AVOC_Formal_v0.25.0.zip
```

Without the optional baseline path, the collector compares retained per-module baseline hashes. The original run additionally verified those hashes directly against the v0.25 ZIP. Semantic regression records all-input bitset oracle results, each actual Lean request/output hash, and before/after test-source pins. The command executes the full regression, including all-256-function queries, budget cases, and three timing repetitions per arm. It is not a production LLM or held-out scientific evaluation.

Final v0.26 counts: 1,792 query cases; 32 budget cases; 512 equivalence cases; 27 campaigns; 12 malformed wire cases; 12 CLI cases. Old live store/crash/SQL tests remain historical and were not rerun.

## Evidence metadata and packaging

```bash
python tools/record_v026_audit.py --baseline /path/to/AVOC_Formal_v0.25.0.zip
python tools/audit/validate_computation_manifest.py results/v0.26.0/computation_manifest.json --root .
python tools/package_v026.py --output /chosen/AVOC_Formal_v0.26.0.zip
python tools/check_manifest.py
```

The optional metadata recorder times the evidence collector, not all earlier proof and test runs. The included validator is the inherited v1-only local adaptation, not the full installed v2 workflow. Its metadata pass does not establish mathematical correctness; the detailed compiler/test records are separate evidence.

Packaging excludes `.lake`, `.git`, bytecode, font files, and compiled Lean outputs. The payload manifest excludes itself. Never overwrite a hashed check log while checking that same manifest.
