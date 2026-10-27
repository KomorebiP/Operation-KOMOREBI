# Independent review of quadratic compression and its height boundary

**Normalized claim.** Every actual function in the inherited quadratic chart
has a unique unit-times-monic-quadratic factorization with the stated modulo
256 normalization. The prepared reduced discriminant has exactly the same
dyadic valuation as the stationary value. Complete coefficient data modulo
2^P determine that discriminant modulo 2^P without an additional loss for
P>=2. Least integer representatives have a linear height bound of about 2P
bits, which by itself does not prove nonvanishing. The projective small-height
condition in section 5 is sufficient, but is not proved for the Euler input.

**Primary verdict: proved as written.** No correction was required. The
preparation, exact unit relation, sharp fixed rational control, and conditional
height criterion are valid in their stated scopes. They do not close actual
ordinary-index nonintersection.

This independent review by `/root/cross_cartier_review` read the raw proof,
checker, and inherited input record. Author files were read-only. No Lean
compilation or new parameter search was performed. The main proof SHA256 is
`332b85413136026eaed381687dcd727f2b082158ca93dcc0496e4ba971a81f53`.
All reviewed files and replay artifacts are pinned in
`QUADRATIC_COMPRESSION_REVIEW_HASHES.json`.

## Dependencies and obligations

The only Euler-specific input in the universal preparation argument is the
inherited complete coefficient statement
`f=a+2bZ+uZ^2+256Z^3R`, with integral restricted coefficients and u odd.
The rest is an internal polynomial-division lifting argument, an exact
quadratic identity at the stationary point, and elementary rational-height
arithmetic. No unverified algebraicity of the critical point or of the
prepared coefficients is used.

| Obligation | Status | Decisive reason |
|---|---|---|
| Existence of normalized quadratic preparation | Passed | Each binary correction is quotient/remainder division by a monic quadratic over F_2 |
| Tate-algebra convergence and unit cofactor | Passed | Correction norms tend to zero; V remains 1 modulo 256 |
| Uniqueness at every bit | Passed | The difference satisfies `Q W_bar+S=0`, with deg S<2, forcing both parts to vanish |
| Even linear coefficient and full-P discriminant precision | Passed | The linear coefficient remains even; squaring recovers the lost bit for P>=2 |
| Exact stationary discriminant relation | Passed | `delta=W'(c)^2/4-W(c)` and `W'(c)=-(U'/U)(c)W(c)` |
| Unit bracket and equality of valuations, including zero | Passed | U'/U is divisible by 256, so its squared correction divided by 4 is divisible by 2^14 |
| Fixed rational double-root control | Passed | Modular inverses give the stated exact formula and bit length for all even P>=6 |
| Projective height condition | Passed as a sufficient condition | Odd A preserves valuation, and a nonzero integer of absolute value below 2^P has valuation below P |
| Bounded Euler-control implementation | Passed | Independent critical lifting agrees with prepared discriminant valuations at all named precisions |
| Actual nonvanishing or existence of small representatives | Not established | The nonzero small-height discriminant is an additional arithmetic hypothesis |

## Preparation and uniqueness reconstructed

Normalize by the actual quadratic coefficient u. The reduction of g=f/u
modulo 256 is a monic quadratic with even linear coefficient. Suppose the
factorization is correct modulo 2^k. Reducing its complete residual after
division by 2^k gives a finite polynomial over F_2, because g is restricted.
Its unique decomposition `Q_k W_bar+S_k`, with deg S_k<2, is exactly the
linearized correction equation: V_bar=1. Adding 2^k Q_k to V and 2^k S_k
to W removes that residual at the next bit. The product of the two
corrections vanishes at the required next precision.

This argument does not require W_bar to be squarefree. In particular it
does not divide by W_bar' or use a simple-root form of Hensel's lemma.
The quotient/remainder map remains invertible when W_bar has a repeated
root. Corrections have Gauss norm at most 2^-k, so their polynomial sequence
converges in the complete Tate algebra. W stays monic of degree two and
its linear coefficient stays even. V stays 1 modulo 256 and is an analytic
unit. The same quotient/remainder uniqueness applied to the first differing
bit of two factorizations proves the asserted uniqueness in this normalized
class.

For a finite input polynomial of degree d, the residual degree never exceeds
d and the quotient correction has degree at most d-2. Thus the finite
cofactor bound in the note is also valid. The factorization modulo 2^P
depends only on complete input data modulo 2^P.

Writing the linear coefficient as 2 beta initially loses one bit in beta,
but not in beta^2. If beta changes by `2^(P-1)t`, its square changes by
`2^P beta t+2^(2P-2)t^2`, which vanishes modulo 2^P for P>=2. Therefore
the prepared reduced discriminant is known through the full P bits.

## Exact discriminant transfer

At the true critical point c, let w=W(c) and tau=U'(c)/U(c). The exact
product derivative gives W'(c)=-tau w. Independently, the monic quadratic
identity gives `delta=W'(c)^2/4-W(c)`. Combining them yields

    delta=-Phi/U(c) * [1-tau^2 Phi/(4U(c))].

Since U is congruent to the constant unit u modulo 256, its derivative is
coefficientwise divisible by 256; evaluation and division by U(c) retain
this divisibility. Also Phi/U(c) is integral. The bracket is therefore 1
modulo 2^14 and is a unit. This proves equality of valuations with the
infinity convention when Phi=0; there is no omitted cofactor derivative.

The least representatives A_P and B_P of alpha and 2 beta give an integer
`d_P=(B_P/2)^2-A_P` representing delta modulo 2^P. A finite nonzero residue
certifies the exact finite valuation. A nonzero integer d_P divisible by
2^P does not certify anything beyond the lower bound.

## Sharp control and height condition

For f_*=(Z-1/3)^2 and even P, put M=2^P. Then M=1 modulo 3 and the required
least representative is `B_P/2=(M-1)/3`. The three cases for C_P are obtained
from M modulo 9; they give `A_P=(1+(C_P-2)M)/9` in the correct range. Direct
substitution yields `d_P=M(M-C_P)/9`. For P>=6, v_2(M-C_P)=v_2(C_P), and
the absolute value lies strictly between M^2/16 and M^2/8. Thus its valuation
and bit length are exactly as stated. This is one fixed rational double
root with zero limiting discriminant, not a varying family or an Euler
counterexample.

For condition (6), an odd integer A allows division in Z_2. The coefficient
congruences give `C/A=alpha mod2^P` and `B/A=beta mod2^(P-1)`. The same
square argument then proves
`(B^2-AC)/A^2=delta mod2^P`. If the numerator is nonzero and its absolute
value is below 2^P, its valuation is below P. Dividing by A^2 changes no
valuation, so delta and Phi are nonzero. The displayed exponent inequality
is precisely what ensures this strict size bound. Nonzero discriminant is
essential and is not implied by bounded coefficient height.

The improvement removes the old degree-times-critical-lift quadratic cost
for these modular representatives. It does not prove an intrinsic minimal
height lower bound for every possible representation. The rational control
establishes that the current approximately-2P-bit bound alone cannot imply
escape, while the note explicitly allows a more selective arithmetic
representation. That is the correct scope of its sharpness claim.

## Input provenance, implementation, and replay

The checker was inspected and independently replayed into
`review/quadratic_compression_replay`; output is byte-identical to the author
result. Both author and replay manifests validate against the project root.
All 14 named actual-control lifts and 62 sharp rational controls pass.

The 94-bit input-file source hash was verified. Its arrays match the eta=0
rows of the original complete inherited coefficient record, with the same
precision and previously recorded valuations. They serve as actual controls
at these precisions through the inherited actual/depleted agreement: the
ordinary undepletion exponent for both fixed indices is far beyond 94.
This finite agreement does not identify the actual and depleted prepared
coefficients at arbitrary precision.

The implementation normalizes by the quadratic coefficient modulo 2^P,
executes the complete polynomial correction lift, and checks the full
coefficientwise product. Its critical-point computation uses the half
derivative through P-1 bits. Stationarity makes that center precision more
than sufficient to evaluate the value through P bits. Independent valuation
comparisons recover the inherited 0 and 30; the zero residues at precisions
16 and 24 for the second record are correctly treated only as lower bounds.

The checked identity involving 4 delta is a finite corroboration of the
quadratic identity; the full precision and exact unit relation rely on the
proof above, not on dividing a modular identity without accounting for its
two-bit loss. No new Euler coefficients or parameter candidates were
constructed in this replay.

## Exact remaining implication

The prepared quadratic replaces the local critical-value problem by an
equivalent reduced-discriminant problem. To conclude actual nonvanishing,
one still needs a nonzero residue, or arithmetic input such as condition
(6) that forces one. Neither the preparation nor the improvement from
quadratic to linear height supplies that input. Applying preparation to
the depleted member additionally requires escape below its actual
undepletion threshold for a separate comparison; applying it directly to
the actual member has no such comparison cap.

Self-review: conservative proofreading covered this report. No
mathematical-token correction or unresolved local notation issue remains.
