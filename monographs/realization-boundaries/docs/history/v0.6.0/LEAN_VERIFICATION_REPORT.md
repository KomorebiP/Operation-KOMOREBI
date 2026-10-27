# Lean verification report — Realization Boundaries v0.6.0

## Accepted result

**PASS: exact root-fiber parameterization and cardinalities, cyclic Chinese-remainder quotient equivalences and transition laws, the complete finite-quotient target classification, and normalized-root/zero-multiplier boundaries.** This is an incremental checkpoint, not full-book formalization.

Authoritative receipt: `verification/accepted_v0.6.0/run.json`. Five new production modules extend the prior 31-module library. All 31 inherited production modules, the final publication PDF, and the original publication ZIP are byte-for-byte unchanged against the actual parent archive.

| Verification measure | v0.5.0 | v0.6.0 |
|---|---:|---:|
| Production modules cleanly rebuilt | 31 | 36 |
| Root entrypoints rebuilt | 1 | 1 |
| Explicitly named source theorems and lemmas | 311 | 371 |
| Audited declarations, including definitions and generated helpers | 698 | 813 |
| Positive contract declarations | 134 | 173 |
| Intended rejection controls | 33 | 41 |
| Modules passing kernel replay | 31 | 36 |
| Passing command gates | 100 | 118 |

The production modules contain 4313 source lines. The 60 additional named lemmas/theorems are supporting formal statements, not 60 independent discoveries or 60 completed book entries. The named inventory resolves every entry to the actual accepted environment and its unchanged source line.

## Exact mathematical coverage

### Actual roots, kernels, and every solution

For an arbitrary rational subspace W of the actual quotient P/D, `RootFiber W m x` is the subtype of elements y in the original subgroup H_W with m • y = x. For a positive multiplier, `rootKernelEquiv` is an actual additive equivalence from the multiplication kernel to the finite product of prime coordinates dividing m. Its inverse extends coordinates by zero into the infinite ambient group and proves support membership and annihilation.

Given one actual root, `rootFiberTranslation` identifies the entire fiber with a translate of that kernel. It is deliberately an equivalence of sets, not an additive equivalence onto a nonzero fiber. The composed `rootFiberEquiv` and its evaluation law parameterize every solution with both inverse laws checked.

`rootFiber_finite` independently establishes finiteness. The distinct-prime-factor product is derived from the actual coordinate cardinalities. For m > 0, the exact count is rad(m) when the original coordinate obstruction vanishes, and zero otherwise. A solvable p^k equation, k > 0, has p roots rather than p^k roots. The empty product m=1 has one solution. No root-count hypothesis is provided as input.

### Cyclic quotients and genuine transitions

`divisorCrtEquiv` is a ring equivalence from ZMod(rad(m)) to the actual finite divisor-coordinate product, using proved pairwise prime coprimality. `cyclicIntegerQuotientEquiv` composes it with the already proved quotient by mH_W. Its representative and coordinate formulas agree with the original ambient coordinates.

For m dividing n, `quotientRestriction` is the actual quotient map induced by the identity of H_W. The cyclic comparison commutes, on every quotient element, with canonical residue reduction ZMod(rad(n)) -> ZMod(rad(m)). The proof also establishes the literal subgroup equality mH_W = rad(m)H_W. Equal cardinalities are not substituted for these homomorphism identities.

### Every finite quotient target, not only displayed examples

For any finite additive-group target F, no commutativity or cyclicity premise is assumed. Every homomorphism H_W -> F factors through the actual cyclic radical quotient associated with |F|. Under surjectivity, its order is proved squarefree and F is proved cyclic.

The converse constructs a genuine surjective homomorphism to any finite cyclic squarefree F. Thus a finite group is a quotient exactly when it is cyclic and has squarefree order. `finite_surjection_ker` proves the literal equality ker(f) = |F| H_W for every finite surjection, not just equality of indices.

### Unique normalization versus unique solution

`normalizedRoot` uses coordinate division and zero at every divisor prime, without choosing a root by an existence oracle. It is proved to be the unique root subject to those zero-coordinate conditions. A solvable equation has a unique unrestricted root exactly when its positive multiplier is one.

At multiplier zero, the zero-target fiber is equivalent to all of H_W and is proved infinite and nonempty. Its `Nat.card` is zero because Lean's natural cardinal also assigns zero to infinite types; this is explicitly not an emptiness assertion. The zero-multiplier fiber at any nonzero target is separately proved empty.

## Controls

The 39 added positive contracts cover actual parameterizations, fourth roots counted as two rather than four, prime-power kernels, counts at 12/18/60, radical multiple-subgroup equality, quotient transitions, selected-prime obstruction, omitted-prime roots, normalized uniqueness, nonunique unrestricted roots, the infinite zero fiber, arbitrary finite-target kernels, a positive C6 quotient, the trivial quotient, and impossibility of a C4 quotient.

Eight added rejection controls target replacing rad(m) by m, deleting solvability, deleting positivity, replacing normalized uniqueness by unrestricted uniqueness, using the wrong cyclic modulus, dropping squarefreeness, reversing/diverging modulus reduction, and confusing natural cardinal zero with emptiness. All 41 inherited and new controls were required to have their specified diagnostics, a nonzero exit, and no timeout. A separate review excluded missing-import and runtime-startup failures from successful rejections.

## Monograph correspondence

Entries **6.2** and **6.3** are newly COMPLETE in the preserved 45-entry registry. The exact types and proof boundaries are in `docs/EXACT_STATEMENT_REVIEW.md` and `docs/NEW_EXACT_TYPES_v0.6.0.md`.

Entry **6.1 remains CORE_COMPLETE**, not full algorithm verification. The coordinatewise normalized root, obstruction, and full solution set are checked. The specific rational/finite-support implementation, its cost bounds, oracle semantics, and extraction correspondence to the Python engine remain separate obligations. The final book was not edited or silently relabeled as fully formalized.

## Accepted execution and identities

```
Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)
```

Mathlib is pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`; all nine locked dependency revisions matched. The runtime was restored from the user's five archived ZIP chunks. Their concatenated archive SHA-256 is `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`. No download, upgrade, or upstream source rebuild was used.

The accepted run began at `2026-10-23T21:24:29.096345+00:00` and ended at `2026-10-23T21:31:30.440509+00:00`, with recorded duration 421.344 seconds. Its 118 command gates all passed. There were 3663 imported-module inventory entries and 18135 recorded compiler/cache files. These are measured execution records, not estimates.

The compiler/imported-cache baseline was captured before the clean rebuild. The verifier deleted project compiled output, rebuilt all production modules serially, audited their declarations, compiled the positive contracts, checked negative controls, and replayed every production module. Source and recorded cache/compiler endpoint hashes were unchanged. A subsequent check matched every delivered proof input to `source_after.json`.

All 813 audited declarations have transitive axiom dependencies contained in `propext`, `Classical.choice`, and `Quot.sound`. No production axiom, admitted proof, unsafe declaration, or native-decision trust axiom was accepted. Automatic implicit parameters were disabled and warnings were errors.

## Development failures and resolutions

Draft checks exposed strict lint, scoped-decidability parsing, ring-cast APIs, equivalence-inverse rewriting, finite-instance inference, and numerical prime-factor normalization issues. They were fixed using actual proved APIs, explicit equalities and instances, without weakening the printed claims or suppressing the audit policy.

One new rejection control initially failed before its intended diagnostic because a natural-cardinal expression had not been rewritten to its literal value. A prematurely started verification run was stopped and its receipt explicitly marked INTERRUPTED. It is preserved under `verification/development_runs/preacceptance_stop_v0.6.0`, not treated as accepted evidence. After the control was repaired, an immediate check met a missing test object removed by that interrupted clean rebuild; that failure was also not accepted. All modules and tests were rebuilt, all new controls were reviewed, and then the authoritative fresh clean run completed successfully. Full incident details and failed logs remain in the package.

## Trust boundary and remaining work

Replay uses Lean's own kernel, not an independently implemented verifier. The restored compiler and imported caches were not rebuilt from source or independently authenticated against upstream. Their recorded bytes were unchanged at the accepted run endpoints; this does not detect every possible transient alteration restored between snapshots. Standard logical principles, these binaries/caches, runtime and hardware remain trusted.

The general directed-graph theorem, subgroup-spectrum lattice and remaining dimension/finite-generation statements, oracle-copy semantics, infinitely repeated grammar diagonalization, and exact Pro-category/global category interfaces retain their distinct coverage states. No Python extraction theorem, external peer review, or historical-priority certification is claimed.

## Reproduction

```bash
export KOMOREBI_LEAN_KIT=/path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 scripts/verify.py --output ../realization-boundaries-fresh-verification
```

Use a new evidence directory. The ZIP excludes the large runtime, dependency cache, and compiled project outputs. The original publication and historical accepted records are preserved. `SHA256SUMS` identifies every shipped member other than itself.
