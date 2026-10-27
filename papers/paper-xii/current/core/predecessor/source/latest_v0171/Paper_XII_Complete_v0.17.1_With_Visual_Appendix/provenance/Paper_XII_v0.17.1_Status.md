# Paper XII — final two claims reverified, v0.17.1

Verified September 11, 2026 (America/Chicago). Exact UTC times are in the audit.

**Revised manuscript: 49/49 internal claims complete, 0 partial, 0 unchecked.**
**Original wording: 41 complete, 7 partial, 1 unchecked.**

Claims 3.1 and 3.3 are verified on actual completed objects, with their topologies,
canonical factor maps, coefficient-algebra structure, locality, and point naturality.
There are no remaining internal obligations in the revised contract. The eight
inherited amendments and all external arithmetic inputs remain separate.

## Correction of the conflicting conversation status

The later 47/49 retraction was incorrect: it overlooked the full saved v0.17.0
archive. This release recovers those existing proofs and independently rechecks
them. It does not count the already-written 146-theorem completion block as new
work in this run. All 96 production sources are unchanged.

## Fresh evidence

- 96 production modules rebuilt with warnings as errors.
- 1,229 production named declarations passed transitive axiom audits.
- All three deliberate invalid-proof controls were rejected as expected.
- All 96 regenerated compiled-object hashes match the earlier successful release.
- All 291 unique targets in the 49-claim map occur in the fresh audit.
- Three supplementary contract theorems passed against the fresh objects: exact
  completed kernel, full tensor-quotient interface, and the Noetherian local
  coefficient-algebra point-factorization interface.

Only propext, Classical.choice, and Quot.sound occur in the audited dependencies.
The pinned Mathlib cache was used, not rebuilt. The source census remains
748 own named theorem declarations plus 81 reused Paper X theorems. The
three supplementary release checks are reported separately, not added to the
manuscript count.

## Reproduce

```bash
bash Run-Reverified.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

This cleans and rebuilds the cumulative project, then runs the supplementary
checks. The kit is separate. Native Windows behavior is not claimed; the
provided toolchain is Linux/WSL oriented.

## Retained boundary

Representability, residual automorphic occupancy, applicable arithmetic patching
and classicality results, attached representations, Frobenius density,
semisimplification, and general Brauer–Nesbitt inputs remain external. This is
not an unconditional universal companion or unrestricted Langlands theorem.
The manuscript and its existing graphics are unchanged in this evidence release.
