# Paper III: Stirling composition-term count, v0.1.0

This separate companion formalizes Proposition 17.6, **Number of labeled
composition terms**, in the frozen Paper III reading edition. The original
manuscript, its statement register and its accepted sixteen-module formal core
are preserved.

For a finite type `J` of intermediate packet labels, the actual composition
index is

```lean
(c : OrderedFinpartition n) × (Fin c.length → J)
```

The two factors are exactly the outer and inner indices in the existing
`iteratedPacketJet_comp` theorem. The new theorem `card_decoratedPartition_pos`
proves, for every positive order, that this type has cardinality

\[
\sum_{k=1}^{n} S(n,k)\,|J|^k.
\]

The proof identifies the length distribution of Mathlib's actual partitions
with `Nat.stirlingSecond` by their extension recurrence. It then counts the
label functions. The Stirling polynomial is not used as a definition of the
cardinality being proved. Blocks have one canonical ordering, so no additional
factorial appears. Empty packet-label types are allowed. At order zero there
is one empty decorated partition; orders one and two are also proved explicitly.

These are syntactic terms before zero jets or cancellation are removed.
The count is classical; this companion makes no novelty claim.

- [Lean source](KomorebiPaperIIIStirling/CompositionTermCount.lean)
- [Exact statement correspondence](CLAIM_MAP.json)
- [Focused proofreading and proof review](REVIEW.md)
- [Verification contract](verification.json)
- [Recorded execution](evidence/run.json)
- [Paper III work page](../../docs/works/paper-iii.md)

## Reproduce

Use the official Lean 4.34.0-rc2 executable and a clean Mathlib checkout at
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, with its eight locked dependencies
and compiled cache. All nine revisions are checked before compilation. From
the collection root, run:

```sh
python formal/paper-iii-stirling-v0.1.0/verify.py \
  --lean /absolute/path/to/lean \
  --mathlib /absolute/path/to/mathlib \
  --output /new/external/evidence-directory
```

Pass `--git /absolute/path/to/git` when Git is not on `PATH`. The sibling
`leanchecker` executable is required. The verifier never modifies dependency
checkouts or their caches. It starts with empty companion object directories,
copies the checked sources, rejects warnings and admissions, records the axiom
dependencies, kernel-replays the new modules, and runs the positive and negative
controls. A timeout or missing import does not qualify as a successful rejection.

The recorded run covers this companion. It does not repeat the frozen
sixteen-module core or certify the packet Taylor remainder, additional norm
corollaries, or the later expanded sections. Review provenance is self-review.

Original code uses the collection's MIT terms; explanatory writing uses its
CC BY 4.0 terms. See the [collection license](../../LICENSE.md).
