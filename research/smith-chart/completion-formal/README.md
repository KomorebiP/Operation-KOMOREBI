# Selected Lean checks for singular completion

`SmithCompletion.lean` checks six declarations for the
[singular-completion supplement](../../../docs/demonstrations/SMITH_SINGULAR_COMPLETION.md):

- `zero_corner`: a real nonnegative quadratic form with a zero corner must
  have zero cross coefficient;
- `determinant_factorization` and `saturated_determinant`: the displayed
  two-real-packet determinant identities;
- `saturated_iff`: retaining the odd packet at `1/2` forces the real even
  packet to be zero;
- `incorrect_packet_rejected`: the determinant at `(1/10,1/2)` is
  `-1328/46875`;
- `inward_packet_feasible`: all three principal-minor conditions are
  nonnegative at `(1/10,49/100)`.

`Feasible` means the two diagonal entries and the determinant are nonnegative.
The bridge from these scalar conditions to positive semidefiniteness of a
two-by-two Hermitian matrix, and then to Schur interpolation, is a written
mathematical argument. The general pseudoinverse lemma, the full square-root
boundary, and the complex example are outside this selected formalization.

The replay uses Lean `4.34.0-rc2` and Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, with the existing pinned
dependency lock. It checks six axiom reports and rejects two false controls:
feasibility at `(1/10,1/2)` and a zero determinant there. It binds the
retained source archive and the exact supplement bytes. The source mapping
and mathematical review are self-review.

```text
python -B research/smith-chart/completion-formal/replay.py \
  --lean <pinned-lean-executable> --mathlib <pinned-mathlib-checkout> \
  --git <git-executable> --repo . --output <new-replay-directory>
```

The recorded logs and receipt are in `verification/run04/`. Imported cached
objects are hashed directly; transitive dependencies are not rebuilt or all
individually hashed. Earlier circuit proof receipts are retained separately.
