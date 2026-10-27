# Audit notes for v0.2.0

## V0.1.1 retrospective audit

An exhaustive replay showed that v0.1.1 training contained all 10,080 ordered
D4 generator-table pairs and all 1,365 individual D4 generator tables. Exact
full-input reuse within lengths 1–4 was approximately 45.41%, 29.05%, 16.31%,
and 7.42%. V0.2 corrects this with immutable individual-map partitions.

The v0.1.1 state transplant was algebraically the native donor continuation,
and operator replacement was equivalent to changing the visible slot. They are
now labeled splice-consistency tests. V0.2 adds different-context patches and
on-manifold controls.

The prior transport anchors were unbalanced, included repeated h0 embeddings,
and supplied target-native operators. V0.2 uses balanced nonzero depths,
shuffled-fit and random controls, a decode–re-embed baseline, operator
intertwining, and metric pullback diagnostics.

The v0.1.1 source digest accidentally included generated integrity files. V0.2
uses an explicit code whitelist and a separate protocol digest.

## V0.2 development amendment

The initial composition loss collapsed the operator encoder. That negative run
is retained. Before test evaluation, and documented in
`protocols/V0_2_DEVELOPMENT_AMENDMENT.md`, the target branch was stop-gradient
bounded and the relative residual was wrapped in `log1p`. Two additional dev
calibrations selected weights 3.0 and 0.3. No code or thresholds changed after
the primary protocol was written.

## Remaining confounds

- Length-1 training densely teaches primitive transitions.
- Full transition tables make an exact transpose executor trivial in principle.
- Relation loss receives more recurrent forward work per optimizer step.
- Soft local isometry does not guarantee noncontractive long products.
- Cross-context patch accuracy is limited by imperfect native accuracy on the
  independent-random family, but the absolute gate remains validly failed.
- Affine transport does not beat discrete decode–re-embed.

