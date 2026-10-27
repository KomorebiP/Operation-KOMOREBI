# Lean verification report — Realization Boundaries v0.3.0

## Accepted result

**PASS: tail signature, unmarked and marked classification, finite-change coordinate transport, torsion-image obstruction, and explicit canonical-completion reconstruction obstructions.** This is an incremental formalization checkpoint, not full-book completion.

The authoritative receipt is `verification/accepted_v0.3.0/run.json`. All fifteen inherited production modules are byte-for-byte unchanged from the actual v0.2.0 checked archive. Five new production modules have been added.

| Verification measure | v0.2.0 | v0.3.0 |
|---|---:|---:|
| Production modules rebuilt cleanly | 15 | 20 |
| Import entrypoints rebuilt | 1 | 1 |
| Explicitly named source theorems and lemmas | 146 | 193 |
| Audited project declarations, including definitions and generated helpers | 391 | 459 |
| Positive contract proofs | 36 | 66 |
| Intended rejection controls | 14 | 20 |
| Production modules passing kernel replay | 15 | 20 |

The current production modules contain 2291 source lines. The accepted run passed all 65 command gates. It recorded 3478 imported modules and checked 17290 compiler/imported-cache files at both endpoints. Both proof-source identity and recorded compiler/dependency endpoint identity passed. These measures count different things. None is presented as a number of original discoveries or a percentage of monograph completion.

## Mathematical results now checked

### Tail-divisibility signature

For every actual nontorsion element of a selector group, the prime-root signature agrees with the omitted-prime selector outside a finite set. The exception set includes numerator primes, denominator primes, and finite-correction support. The root predicate quantifies over actual elements of the original group. Its preservation by arbitrary additive homomorphisms is proved independently.

### Exact unmarked and marked classification

`pairedGroup_isomorphic_iff` proves

    Nonempty (G_a ≃+ G_b) iff {n | a n != b n} is finite.

Both directions are checked. Finite selector changes give literal equality of the subgroups in the fixed ambient product, with an additive equivalence that leaves every ambient point unchanged. Requiring the original marked indicator to map to the target marked indicator gives literal equality a=b. A one-bit toggle formally witnesses why the unmarked conclusion cannot be strengthened.

### Coordinate transport

The explicit transformation `(r,d) -> (r,d+s_a(r)-s_b(r))` is proved to have finite correction, to fix the ambient realization, and to be the actual additive equivalence between the twisted normal-form groups. The usual split-product addition is not silently substituted.

### Arbitrary homomorphisms

If any element under any additive homomorphism G_a -> G_b has nontorsion image, then the selectors differ finitely. This proof requires neither continuity nor an assumed diagonal formula. If the selectors differ infinitely, every image element lies in D and has a positive annihilator. The map factors uniquely through D. No embedding or surjection exists. Conversely finite disagreement gives an isomorphism, so all three existence criteria coincide for this family.

Torsion image is not zero image. The positive suite constructs a nonzero one-coordinate map between the constant-false and constant-true groups. The full classification of diagonal homomorphisms remains a separate next block.

### Completion and reconstruction

The constant-false and constant-true groups are proved nonisomorphic, while their actual canonical profinite completions are continuously additively equivalent. An arbitrary group-valued assignment invariant under those completion isomorphisms cannot recover every original paired group. No computability assumption is used. The canonical comparison of completions has no group-homomorphism lift compatible with the original eta maps when the selectors differ infinitely.

The no-reconstruction theorem currently uses the canonical completion interface. The monograph's separately stated Pro-object decoder interface is not newly formalized. Similarly, the explicit no-lift witness is not yet packaged as a full categorical faithfulness/nonfullness theorem on all residually finite groups. The source map retains these boundaries.

## Monograph mapping

Four additional numbered entries are COMPLETE: **7.1, 7.2, 7.3, and 7.6**. Entries **9.1 and 9.3** now have explicit partial coverage with the precise interface restrictions above. All 45 original numbered entries remain in `docs/MONOGRAPH_COVERAGE.json`. No printed mathematical statement or publication file was changed.

## Compiler, dependencies and accepted run

```text
Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)
```

Mathlib remains pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine locked dependency revisions matched. The portable runtime was restored from the archived five-part kit, whose concatenated archive SHA-256 again matched `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`.

The run began at `2026-10-23T18:48:00.989309+00:00` and ended at `2026-10-23T18:51:42.368052+00:00`. Its measured duration was 221.379 seconds. Individual command return codes, durations, hashes and logs are retained in the receipt, not inferred from this summary. The preflight snapshot was taken before the clean rebuild. All project compiled output was deleted before the final serial production rebuild.

## Audit and controls

Every audited production declaration has transitive axiom dependencies contained in `propext`, `Classical.choice`, and `Quot.sound`. No production axiom, admitted proof, unsafe declaration, or native-decision trust axiom was accepted. Automatic implicit parameters were disabled and warnings were treated as errors.

The six new diagnostic controls reject zero-rational finite exceptions, an all-prime rather than eventual signature, literal equality from unmarked isomorphism, automatic preservation of a marked point after finite changes, a zero-image conclusion from torsion-image information, and confusing source groups with their completions. Each rejection was required to have its intended diagnostic and a nonzero compiler exit without timeout. The positive suite supplies the corresponding actual mathematical counterexamples.

## What failed during development

An initial missing-import check ran before its inherited dependency had compiled. An early long elaboration exceeded a container call window, and a repeated development run exited 137 while attempting direct definitional reduction of subgroup-equality transport. A proved congruence-evaluation lemma replaced that `rfl` attempt and resolved the compilation problem. The external cause of signal 137 was not independently established. Additional type-annotation, rewrite and warning-policy errors were corrected. Rational denominator tests required explicit normalization rather than raw reduction.

These failed attempts are not counted as evidence. Detailed incidents and preserved logs are under `docs/DEVELOPMENT_INCIDENTS_v0.3.0.md` and `verification/development`. No monograph theorem had to be weakened or corrected in this tranche. The accepted run has no failed gate.

## Trust and remaining scope

Kernel replay uses Lean's own kernel, not an independent implementation. The restored compiler, imported compiled dependencies, standard logical principles, runtime and hardware remain trusted. The compiler and caches were not rebuilt from source or independently authenticated against upstream. Endpoint equality does not detect a transient change restored between endpoints.

The all-homomorphism diagonal formula, endomorphism ring, automorphism criterion, seed ranks, root-fiber counts, CRT cyclic identifications, dimension-language statements, oracle-presentation semantics and grammar diagonalization remain unfinished formalization tasks. A noncomputable construction is not a proof of the oracle theorem. No Python extraction verification, external peer review, or historical-priority certification is claimed.

## Reproduce

```bash
export KOMOREBI_LEAN_KIT=/path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 scripts/verify.py --output ../realization-boundaries-fresh-audit
```

Use a new output directory. The source ZIP excludes the multi-gigabyte runtime and cache. Publication materials and previous accepted evidence remain preserved.
