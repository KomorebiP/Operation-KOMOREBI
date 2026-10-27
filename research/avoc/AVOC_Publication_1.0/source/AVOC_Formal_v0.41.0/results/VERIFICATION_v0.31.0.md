# AVOC v0.31.0 — current verification record

## Checked result

- 171/171 current local compilation targets passed, warnings treated as errors.
- 1,656/1,656 exact-name theorem/lemma axiom reports passed.
- 44 new declarations in four new mathematical modules; all 148 inherited
  non-audit modules are byte-identical to the frozen v0.30 archive.
- 152 non-audit modules; 23,806 non-audit Lean source lines.
- 88/88 deliberate negative files were substantively rejected. No import failure
  or timeout is counted as a negative result.
- No proof placeholders, project axioms, native evaluation or unsafe declarations
  were found in positive source.
- Reported axiom union: propext, Classical.choice, Quot.sound.

## Actual execution

2,888 exact differential requests passed. The family includes all 625 two-by-two
GF(5) matrices embedded as a four-by-four linear block, each tested at four probe
credit levels. It also includes dimensions 0..8, sampled rectangular programs,
compositions, repeated selectors, bounded plans, exhausted credit and zero workloads.
There were 1,532 executed probes, 1,038 returned witnesses and 1,014 stronger denials
in this finite suite. Those are test counts, not population or runtime guarantees.

The oracle decides a minor's independence by enumerating its 25 possible column
combinations, not by using the determinant formula. It separately uses homogeneous
matrices and direct AST evaluation. For small dimensions it checks rank by full
column-image enumeration.

Nine malformed wire requests and five wrapper-validation cases were rejected.
Eight actual end-to-end read-only runs called the Lean scanner and, when permitted,
the inherited Python RREF proposer and Lean factor validation/selection. They
include generator-forbidden hooks for denial cases. Full-rank setup was 24 with
the probe versus 648 without. Rank-one setup was 248 versus 240. A missed witness
continued to checked factor generation; a two-probe plan found it and stopped.
No protected store was mutated. This is not an empirical AI research experiment.

## Build and runtime provenance

Input source ZIP SHA-256:

    b0050c6f6a6956997d95ba4699f7b447de413fda1912bf88c2beaaa2c657ac0a

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d;
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine external package HEAD
pins matched the manifest. The seven portable-runtime ZIP chunks passed their
assembly CRC/length/hash checks and the combined archive hash passed before
extraction. No independent compiler/kernel implementation was used.

The input v0.30 payload manifest passed 9,149/9,149 entries before edits.
The new local build directory began empty. The inherited 166 targets were compiled;
then the new targets and affected aggregate/descendant were compiled. Final current
source, direct-import binary, output, and log hashes were checked for all 171 targets.
Pinned external binary caches were retained, not rebuilt from source.

`tools/summarize_v031.py` checks individual records, independently counts positive
source, compares inherited sources against the input ZIP, reconstructs differential
input/output hashes, and checks final test-source records. Its runtime is collector
time, not the duration of all prior proof and test executions.

The legacy computation manifest validator passed. It is the inherited v1-only
adaptation; metadata validity is not mathematical correctness. Current detailed
evidence resides in results/v0.31.0/.

Historical live-store, crash, retry, cache, and agent regressions were retained but
NOT rerun or reclassified as current evidence.
