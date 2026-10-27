# AVOC v0.33.0 — verification record

## Result

**PASS within the declared theorem and bounded executable scopes.**

- 60 new theorem/lemma declarations in five modules.
- Complete cumulative inventory: **1,752** theorem/lemma declarations.
- **182/182** current local compilation targets passed from an empty local
  project build directory.
- **1,752/1,752** exact-name axiom reports passed.
- **94/94** deliberately invalid Lean files were substantively rejected.
- **156/156** inherited non-audit Lean modules were byte-for-byte identical to
  the frozen v0.32 source archive.

Counts include helper lemmas and concrete examples; they are not counts of
mathematically independent discoveries.

## Toolchain and build scope

- Lean `4.34.0-rc2`, commit
  `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- All nine dependency revisions in `lake-manifest.json` matched their pinned
  checkouts.
- The local `.lake/build` directory was deleted before the final rebuild.
- External dependency caches were retained.  This was **not** a source rebuild
  of mathlib and was not an independent implementation of Lean's kernel.

The complete axiom union is:

```text
propext
Classical.choice
Quot.sound
```

The comment/string-aware source scan found no `sorry`, proof `admit`,
`native_decide`, project-defined `axiom`, or unsafe theorem-like declaration in
positive AVOC sources.

## New executable regression

The actual Lean entrypoint `tools/MultiLevelMain.lean` was compared with a
separately implemented exact Python oracle.

The oracle independently:

- evaluated entries and two-by-two minors modulo five;
- computed matrix ranks by Gaussian elimination;
- performed finite-horizon dynamic programming with `Fraction` arithmetic;
- reproduced the evaluator's state/action/observation work convention; and
- checked every retained rank floor against every retained matrix.

Final bounded results:

| Check | Result |
|---|---:|
| Valid randomized requests | **320 passed** |
| Invalid wire requests | **8 rejected** |
| Hand-audited executable examples | **4 passed** |
| Probe choices | 10 |
| Warm-reuse choices | 29 |
| Cold-generation choices | 174 |
| Stop choices | 107 |

The randomized generator seed was `20260914`.  The runtime tests are bounded
implementation evidence.  The universal Bellman-optimality and rank-invariant
claims are established separately in Lean.

## New concrete examples

The four-world example produced the following exact results:

| State / horizon | Returned action | Value | Retained rank floor |
|---|---|---:|---:|
| Initial, horizon 1 | cold | `19/4` | 0 |
| Initial, horizon 2 | level-two probe | `9` | 0 |
| After positive level-two report | reuse | `4` | 2 |
| After negative level-two report | cold | `16` | 0 |

The corresponding evaluator work counts were 26, 136, 21, and 21.

## Negative-test execution note

The first attempted 25-file negative batch reached the host's outer execution
limit after 14 completed rejections.  Those completed records were retained.
The suite resumed at the first unfinished file in bounded groups.  Every one of
the final 94 records has a current source hash, a non-timeout nonzero return
code, a substantive Lean error, and current imported-output hashes.

## Evidence files

Current machine-readable records are under `results/v0.33.0/`, including:

- `build_order.json` and one clean compilation record per local target;
- `declaration_inventory.json`, `new_declarations.json`, and
  `source_counts.json`;
- `full_axiom_audit.log`, `full_axiom_audit.json`, and
  `axiom_audit_summary.json`;
- one negative-test record and log per invalid file;
- `multi_level_tests/` request, output, invocation, source-hash, and summary
  records;
- `verification_summary.json`; and
- `computation_manifest.json`.

The local v1 evidence-manifest validator accepted the final computation
manifest and printed its documented legacy provenance limitations.
