# Paper III: packet jet norm corollaries, v0.1.0

This companion addresses the separately missing clauses of Proposition 17.3,
**Jet norm bound**: the projector-product estimate on the actual input ranges
and the Hilbert orthogonal-projection specialization. It uses the existing
`continuousPacketJet` and `iteratedPacketJet` definitions.

Four unchanged source modules are copied from the frozen Paper III release,
bound to their original SHA-256 identities, and rebuilt from empty owned
object directories. The new module adds nine theorems. The original
manuscript and statement register remain preserved.

For an order-`n` continuous multilinear map `B`, the new range-jet estimate is

\[
\|J_{\gamma\mid\alpha_1,\ldots,\alpha_n}B\|
\leq \|Q_\gamma\|\,\|B\|\prod_{k=1}^{n}\|P_{\alpha_k}\|.
\]

The proof uses the fact that a vector in a projector's actual range is fixed
by it. It does not assume that every projector is nonzero or that its norm is
one. A zero input projector makes a positive-order jet zero. The nullary case
has no input slot and is checked separately.

The sharper inherited range bound already needs only the output projector's
norm. Consequently a contractive output gives `norm jet <= norm B`, even for
oblique input projectors. In the Hilbert specialization, the output projector
is explicitly identified with Mathlib's actual `V.starProjection`. The
nonzero-subspace hypothesis is retained when proving norm equal to one.
Algebraic annihilation in `System.orthogonal` alone does not imply metric
orthogonality or contractivity.

- [New Lean source](KomorebiPaperIIIJetNorm/Bounds.lean)
- [Exact statement and prerequisite map](CLAIM_MAP.json)
- [Proofreading and mathematical self-review](REVIEW.md)
- [Proofreading receipt](PROOFREAD_RECEIPT.json)
- [Compiler, axiom, kernel and rejection evidence](evidence/run.json)
- [Verification contract](verification.json)
- [Paper III](../../docs/works/paper-iii.md)

## Reproduce

Use official Lean 4.34.0-rc2 and the clean Mathlib checkout and eight dependency
revisions pinned in `lake-manifest.json`, with their compiled caches. From the
collection root:

```sh
python formal/paper-iii-jet-norm-v0.1.0/verify.py \
  --lean /absolute/path/to/lean \
  --mathlib /absolute/path/to/mathlib \
  --output /new/external/evidence-directory
```

Pass `--git /absolute/path/to/git` if necessary. The matching sibling
`leanchecker` is required. No dependency source or cache is modified. The
verifier checks the exact manuscript and source-register identities, all nine
package revisions, and every retained source copy before compiling. It then
audits all declarations owned by the retained and new modules, inventories the
new theorem axioms, kernel-replays the import closure, and runs the controls.

The scalar fixture retains a redundant zero packet and a nonzero nullary jet.
The oblique fixture is a complete pair of idempotents on `ℝ × ℝ` with the
inherited maximum norm; one projector has norm at least three. It is a
counterexample to contractivity of a general algebraic packet projector.
This is distinct from the Hilbert orthogonal-projection case.

No Taylor remainder, new differentiability assertion or whole-paper coverage
is established. Review is self-review; kernel replay uses the same official
Lean kernel, not an independent proof assistant. Original code uses the
collection MIT terms and explanatory writing its CC BY 4.0 terms; see the
[collection license](../../LICENSE.md).
