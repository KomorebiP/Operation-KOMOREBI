# Lean verification report — v0.2.0

## Accepted result

**PASS: pure-subgroup correspondence, countability, topology and the actual profinite completion.** This is a substantive continuation, not a full-book formalization.

The authoritative receipt is `verification/accepted_v0.2.0/run.json`. The preceding nine production modules are byte-for-byte identical to the parent checked archive. Six production modules have been added.

| Gate | Observed result |
|---|---:|
| Production modules rebuilt from clean project output | 15 |
| Import entrypoints rebuilt | 1 |
| Explicit source theorem/lemma declarations | 146 |
| New explicit source theorem/lemma declarations | 56 |
| Audited project declarations, including generated helpers and instances | 391 |
| Production source lines | 1706 |
| Positive contract proofs | 36 |
| Intended rejection controls | 14 |
| Production modules passing kernel replay | 15 |
| Successful verification gates | 49 |
| Imported modules recorded | 3473 |
| Dependency/cache/compiler files hashed at both endpoints | 17290 |
| Proof-source endpoint identity | PASS |
| Imported-cache/compiler endpoint identity | PASS |

These counts measure different things. Generated declarations are not counted as independent mathematical results. Earlier Python test counts are not rerun or added to the Lean counts.

## Mathematical endpoints now checked

1. An order equivalence between rational subspaces of the actual P/D and pure intermediate subgroups D ≤ H ≤ P. The rational image is constructed and its scalar closure is proved.
2. Countability of D and every selector group, countable infinitude for every paired group, and Countable(H_W) iff Countable(W).
3. The genuine product topology, density, canonical open congruence kernels, and continuous finite-target extensions.
4. Natural equivalence of Hom(H_W,F) and Hom(D,F) for every finite group target, with literal restriction identified.
5. A continuous additive equivalence from Mathlib's all-finite-quotients profinite completion of every H_W to P. Both comparison maps, inverse laws, and compatibility with the canonical map are proved.
6. Equality of the full profinite topology and the induced product topology; residual finiteness using Mathlib's official predicate.
7. The D and paired-group specializations, including the nonsurjective inclusion D → G_a whose canonical completion extension is an isomorphism.

Eight printed entries moved to complete coverage: 2.1, 2.5, 4.2, 4.4, 4.5, 5.1, 6.4 and 9.2. Exact clauses and remaining boundaries are recorded for all 45 entries in `docs/MONOGRAPH_COVERAGE.json`. The canonical quotient result 6.3 remains partial because the separate cyclic Chinese-remainder identification is not yet formalized.

## Compiler and dependency identity

```text
Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)
```

Mathlib remains pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine locked dependency revisions matched. The restored concatenated runtime archive has SHA-256 `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`, matching the predecessor's record. The current restoration and parent-source identities are retained under `provenance`.

The accepted run began at `2026-10-23T18:02:23.191425+00:00` and ended at `2026-10-23T18:05:43.358476+00:00`. Raw command durations, return codes, hashes and diagnostics are retained, rather than inferred from a narrative summary.

## Audit and rejection policy

The production inventory was selected by defining module or project namespace and exported with exact types. Every declaration has transitive axiom dependencies contained in `propext`, `Classical.choice`, and `Quot.sound`. No production axiom, unsafe declaration, admitted proof, or native-decision trust axiom was accepted. Compilation used automatic implicit parameters disabled and warnings treated as errors.

The four added negative controls reject: dropping D-containment from purity classification, assuming countability of an arbitrary rational preimage, confusing density with surjectivity, and applying the completion equivalence to the original group. Positive proofs show that the zero subgroup is pure but not any rational preimage, and that the actual D inclusion is not surjective. Each negative test had to fail with its intended diagnostic, not a timeout or missing import.

## Development failures and their resolution

The shell's interactive-session interface was unavailable, so restoration and verification used ordinary process execution with persistent logs. An initial restoration launch referenced a script that the rejected session had not written; no compiler evidence came from that attempt. The script was then written and the archived runtime restored successfully.

Several intermediate Lean attempts failed on current API names, countability imports, type inference, and warnings promoted to errors. One continuity proof initially inferred the quotient topology rather than the discrete finite-quotient topology used by the canonical completion diagram. The proof now explicitly installs that discrete topology at each finite target. A class-valued topology definition was marked instance-reducible to satisfy the compiler's warning policy.

A dependent module once compiled after a failed Countability edit by importing an older compiled Countability object. That intermediate compilation is not the accepted evidence. Countability was corrected, and the accepted verifier deleted all project output and rebuilt all fifteen production modules before auditing or replaying them. The failed compilation logs remain in `verification/development`.

None of these incidents required changing a monograph theorem. The accepted run contains no failed gate. Intentional negative controls remain intentionally invalid test sources and are not imported by production.

## Trust and scope

Kernel replay uses Lean's own kernel, not a second implementation. The compiler, runtime, hardware, standard logical principles and pinned imported compiled dependencies remain trusted. The compiler and Mathlib caches were restored, not rebuilt from source or independently authenticated against upstream. Endpoint hashes show unchanged recorded bytes, not original provenance or immunity to transient modification.

The full monograph is not yet formalized. Remaining work includes topological cyclicity and CRT, full root-fiber counts, the rational-dimension reformulation of countability, unmarked classification, arbitrary-homomorphism and endomorphism structure, seed-rank results, computability/oracle semantics, and repeated grammar diagonalization. No Python extraction verification, external peer review, or historical-priority certification is claimed.

## Reproduction

```bash
export KOMOREBI_LEAN_KIT=/path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 scripts/verify.py --output ../realization-boundaries-new-audit
```

Use a new output directory. The verifier performs actual serial compilation, declaration auditing, positive and negative tests, and kernel replay. The source ZIP does not duplicate the multi-gigabyte portable runtime. The printed book and original final publication ZIP remain unchanged as publication provenance.
