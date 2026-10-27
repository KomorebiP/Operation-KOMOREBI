# Invalidated source dictionary and corrected scope

The first draft of `NEWTON_SOURCE_PRODUCT.md`, SHA256
`9e47cb2d1fdefd1f56f5b8ef243a2f615c74b92ce541e4648b183d00b7349648`,
incorrectly asserted

\[
\mathcal T(k)=\mathcal U(S(z)k(4z^2)),\qquad
S(z)=\frac{\sinh(2z)\sinh z}{2z^2},\qquad
\mathcal U(z^m)(2s)=(2s)_{\underline m}.
\]

The parent reviewer caught the contradiction already at `k=1`, `s=1`:
`S(z)=1+(5/6)z^2+...` gives `U(S)(2)=8/3`, whereas the actual source
has `A(1)=5/3`. Exponential-generating coefficient extraction was confused
with a falling-factorial substitution. The claimed sourced star conjugation
by `S`, source logarithmic derivative `eta`, and formula
`delta F = NF - (NA) star F` therefore have no proof and are withdrawn.
The earlier message describing that draft as frozen is superseded.

The corrected note defines the actual sourced star product directly through
the exact operator identity `T_a T_b = T_(ab)`, and defines `delta` only as
the transported coefficient Euler derivation. The full transformed beta
cubic is then valid by definition and the operator product identity. The
low coefficient cancellation and the exact source-specific double-contact
example do not use the erroneous dictionary and are retained with their
displayed proofs. The unsourced Newton product is stated separately, with
no asserted dictionary to the actual source.

This was a substantive derivation error, not a typographical correction.
It was detected before the corrected note was included in the reviewed
delivery. No universal nonvanishing result depends on either draft.
