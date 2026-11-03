# SF-LEAN-B05: analytic-germ parameter recovery

This block closes the analytic-germ parameter-recovery implication of Theorem
G.2 for the labeled canonical coupled pair. For positive real scale tuples
`s,t`, with every scale strictly below one and `s.defect ≠ 0`, equality near
zero of `s.U` with `t.U` and of `s.V` with `t.V` implies `s=t`.

The new source contains **13 named theorem declarations**, including supporting
lemmas. The registered source scope is **137 names**: 39 in the inherited
finite core, 29 in Block01, 21 in Block02, 19 in Block03, 16 in Block04, and
13 here. This does not establish full analytic coverage of the monograph.

## Exact coefficient bridge

For real coefficients `c`, define the complex dense sequence

\[
d_{2n+1}=c_n,\qquad d_{2n}=0.
\]

The Lean definition `denseOdd c k` uses `k % 2` and `k / 2`. The map
`n ↦ 2n+1` is injective. Every dense term outside its range is zero, so
`Function.Injective.hasSum_iff` transports the original odd-series `HasSum`
to the dense series without rearranging a conditionally convergent series.

Mathlib's `FormalMultilinearSeries.ofScalars ℂ (denseOdd c)` has scalar
coefficient `denseOdd c k` at each degree `k`. The exact local `HasSum`
characterization `hasFPowerSeriesAt_iff` therefore supplies a
`HasFPowerSeriesAt` representation at zero. Uniqueness of such representations
under equality of germs gives equality at every odd coefficient; injectivity
of the real-to-complex embedding gives equality of the real coefficient
sequences.

These are **ordinary coefficients**. Degrees three, five and seven correspond
to sequence indices one, two and three. There is no factorial division in
the dense sequence. The kth derivative would be k! times the ordinary
degree-k coefficient; a general iterated-derivative formula is not asserted
by this block.

The existing entire-convergence result supplies the local `HasSum` premise
for both canonical components. Consequently equality of both germs gives
equality of the entire paired recurrence sequence and, in particular, the
six coefficients in the degree-seven jet. Block01's
`parameters_of_formal_pair_eq` supplies the final inverse under positivity
and the nonzero-defect guard.

## Interfaces and manuscript correspondence

- `odd_series_hasFPowerSeriesAt` constructs the dense scalar Taylor object
  from an actual local odd-series expansion.
- `odd_coefficients_eq_of_germ_eq` extracts all coefficients from equality
  of two such germs, without any scale or positivity premise.
- `coefficients_eq_of_analytic_germs` and `sameJet_of_analytic_germs` apply
  this to the canonical pair.
- `parameters_of_analytic_germs` is the guarded labeled-parameter inverse;
  `parameters_of_entire_pair_eq` gives its global function-equality corollary.
- `analytic_solution_Taylor_coefficients` identifies every coefficient of
  arbitrary supplied Taylor objects for a normalized analytic solution germ.
  Even degrees are zero and odd degrees are the canonical recurrence values.
- `parameters_of_shared_solution_germ` recovers the tuple when the same
  normalized analytic germ pair solves both parameterized equation pairs.

The manuscript locator is
`monograph/sections_v11/coupled_inverse_full.tex`, the degree-seven generic
inverse statement in Appendix G.2. The finite inverse and the exact defect
factorization were already checked in Block01; this block supplies the
analytic comparison that remained open. Ordered U and V labels are retained.
It does not prove an inverse modulo component permutations or a stable
finite-precision reconstruction near the exceptional locus.

## Verification

The source-bound [receipt](evidence/receipt.json) records a fresh replay:
nine pinned dependency revision checks; warning-as-error compilation and exact
axiom inventories for all five coupled modules; same-kernel replay of all
five modules against the cached imports; four rejection fixtures and one
positive interface fixture. There are **30 replay steps**. The freshly
audited coupled scope is 98 declarations; the 39-name finite core retains its
earlier evidence. Only `propext`, `Classical.choice`, and `Quot.sound` are
allowed logical axioms. Imported Mathlib is not rebuilt or freshly replayed.

The negative controls reject the wrong degree index, factorial normalization
of an ordinary coefficient, a call omitting the defect hypothesis, and a
placeholder proof. The missing-defect fixture is an interface check, not a
counterexample to an unguarded germ theorem. The positive fixture checks all
three jet addresses, even-degree zeros, recovery of the preserved rational
example, coefficient transport at degree seven, and the preserved finite-jet
collision on the exceptional locus. That collision is not relabeled as a
proved collision of full analytic germs.

```text
python tools/verify_coupled_germ_inverse.py --toolchain /path/to/toolchain --mathlib /path/to/mathlib --work /path/to/new/sf-block05
```

Use a fresh work directory outside the release. The environment remains Lean
4.34.0-rc2 and Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
The replay installs nothing and downloads nothing. The proof has no
load-bearing numerical experiment. Review is [self-review](SELF_REVIEW.md),
not independent review.

## Checkpoint and continuation

The base revision is `ee59ff257a74fc046981e5ca633476148fe2e1a4`.
[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) binds immutable records, the
dated guide and every replay input. Live continuation/release guidance and
the generated catalogue are excluded from that immutable snapshot. Earlier
blocks, their evidence, guides, manuscript sources and reading PDFs are
preserved. No new complete archive release is claimed.

The scalar-series route succeeded. Iterated differentiation and leading-term
tail estimates remain deferred alternative methods, not failed mathematics.
The coefficient-object transport obligation left by Block04 is resolved.
Next: formulate the full component-rescaling equivalence of Appendix G.1
against the exact definitions, preserving both exceptional surfaces and
normalization. Perron order/type growth remains a separate larger obligation.
