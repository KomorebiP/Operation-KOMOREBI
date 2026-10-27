# Independent audit of the terminal-129, irregular-address-17, and height followups

Date: 2026-10-05. This supplements `REVIEW.md`; the original report and its `SOURCE_HASHES.json` remain unchanged. The followup revisions are pinned separately in `FOLLOWUP_SOURCE_HASHES.json`.

## Verdict

**The global Euler simplicity target remains incomplete.** The new terminal-129 exclusion theorem, the unconditional terminal-129 and terminal-161 integer-family corollaries, and the irregular-address-17 reduction pass under their stated source hypotheses. The negative height-route conclusion is justified. The minor finite-parameter qualification in its logarithm-height discussion identified below has been corrected; it does not affect any Euler result.

## Terminal 129: complete finite elimination and its exact precision

I independently reconstructed the local coefficients from the saved global `Low` and `High`, removing content 130 from 224 coefficient bits. This leaves 94 bits. I then reconstructed every coefficient of `W=A C'-C A'` using the independent identity that its coefficient contribution from `a_i c_j` is `(j-i)a_i c_j` in degree `i+j-1`.

The four saved balls are disjoint and exhaustive: their exact measures are `1/4, 1/8, 1/8, 1/2`. Independent affine reconstruction recovers the following complete reductions:

| Ball | Certificate |
|---|---|
| `0+4 Z_2` | Constant valuation 3 |
| `1+2 Z_2` | Constant valuation 1 |
| `2+8 Z_2` | Content 6; reduction `1+Z` |
| `6+8 Z_2` | Content 6; reduction `Z` |

Thus each critical branch retains `94-6=88` local digits, or `88+3=91` digits of `Y`. The resulting two residues exactly match the author records. On both branches the complete reductions of `A` and `C` modulo 4 are the constant 2. Hence they have exact valuation one throughout those balls. Dividing by two leaves only 90 safe bits for the ratio from a 91-bit `Y` residue. The statement correctly retains this loss and does not invert an even value.

The independently recovered canonical multiplier residues modulo `2^90` are

`753164624808627572229541837` and `621741425015278698550505213`.

Both exceed `2^89=618970019642690137449562112`. The necessary argument residues modulo `2^91`, the earlier 16-bit multiplier cylinders, and the argument conversion `x=104+128Y` are consistent. All four W leaves have content strictly below the available coefficient precision. The underlying uniform template is only needed on parity balls, and every later substitution preserves that scope.

The lower polynomial reduces coefficientwise to `X` modulo 2, has the recorded unique root `104 mod 256`, and the skeleton derivative there has valuation `128-s2(104)-s2(24)=123`. Together with the earlier address-one theorem, this justifies localization to `L=515` and `x=104+128Y`. There is no unjustified identification of a finite eliminant root with an actual singular Euler member.

The author separately checked 204 scalar coefficients and 224 source coefficients by its alternative arithmetic path. I reviewed that verifier and its output, but did not rerun the original-index coefficient calculation.

## Both unconditional integer-family corollaries

The terminal hypothesis follows uniformly, including the boundary ties.

For label 129, if odd `0<B<2^89` and `L>=392`, then `s2(r)=s2(B)+L-2<=L+87`. The global carry-minimizer cutoff is at most `floor((L+86)/3)`, which is less than `2^L+129`. Before 129, the exact finite lower table has minimum `-3`, only at `q=1`. At 129 the cost is `389-L<=-3`. For every later candidate inside the cutoff, `h=q-129<2^L`, and its excess is `3h+s2(h)>0`. At `L=392` the lower tie precedes 129, so the **last** minimizer is still 129. The root-exclusion theorem therefore gives simplicity at every such depth, with no separate admissibility condition.

For label 161, if odd `0<B<2^932` and `L>=487`, the same proof uses `s2(r)=s2(B)+L-3<=L+929`, cutoff at most `floor((L+928)/3)`, lower minimum `-1` only at `q=1`, and terminal cost `486-L<=-1`. The later excess is again strictly positive before any additional multiple of `2^L` can occur. At `L=487`, selecting the last minimizer resolves the equality tie. This validates the newly added unconditional terminal-161 family corollary.

These are structured families of depths. Neither statement covers all depths below a bound or all positive Euler depths.

## Irregular lower address 17

The exact prefix normalization and its transfer are sound. From `r=-17 mod 2^53`, the involved even Bernoulli indices are congruent to the formal integers `-34,-32,-30 mod 2^54`. Evaluating the **finite congruence polynomial** at these negative integers is legitimate and does not introduce Bernoulli numbers at negative indices. Dividing the falling polynomial by `h!` loses at most `h-1` bits, compensated by the valuation of `2^h B_h`. Stripping the necessary factorial offsets loses at most another five bits, still leaving a margin far beyond the six required bits.

Using only exact fractions and the finite Bernoulli values through `B_6`, my independent reconstruction gives Bernoulli-unit residues `[13,1,21]`, packet residues `[1,55,16]`, source coefficients `[1,34,28,8,48,32]`, and prefix coefficients

`S = 1+13X+40X^2+8X^3+48X^4+32X^5 mod 64`.

The unique root is `sigma=43 mod 64`; its distance from 11 has valuation five. The explicit prefix valuation table shows all omitted prefix packets have valuation at least seven. Since `S=1+X mod 2`, degree-one preparation gives `S=(x-sigma)V`, where `V` is a restricted analytic unit reducing to 1.

The resulting exact normalized equation

`G_r/V = q(x)F(x-17)+2^delta(x-sigma)`, with `q=uP_17/V`,

is valid even at `x=sigma`. A lower skeleton integer cannot be a root of this equation because `sigma mod 64` differs from every integer `0,...,16`. At a root with `x!=sigma`, both `q` and `F` are nonzero. These observations justify the finite valuations before equation (12).

For the crucial inequality, let `s=v(x-ell)`, `w=v(x-sigma)`, and `g=g_ell`. Then

`v((x-sigma)q'-q) >= g+min(s,w)`.

The derivative elimination therefore gives `z<=max(s,w)`, with the direction exactly as stated. If the difference vanishes, its competing derivative term is nonzero and a tangency is already impossible. Since an emerged complement branch has `z>=H_i>=53`, one of `s,w` must be that large; both cannot be because `v(sigma-ell)<=5`.

If `w>=H_i`, the special lower ball forces `ell=11`, `s=5`, and `v(q)=16`. The root and derivative equations would give `delta-d_i=16`, contradicting emergence. If `s>=H_i`, the equations give `z=s` and `delta-d_i>H_i`; the integer center difference is exactly `2^H_i`, and dyadic parity contradicts `z=s`. At the exceptional simultaneous root `x=sigma`, necessarily `F=0`; direct differentiation gives the uniquely smallest term `q(sigma)F'` of valuation `16+d_i<delta`. Thus that root is simple too.

On root-free complement balls, the prefix geometry forces `v(x-11)=5` and `v(x-sigma)=16`. The derivative terms have valuations `delta+11`, `16+v(F')`, and `delta`. If `d_i>delta`, the last term dominates. Otherwise the skeleton derivative dominates the even correction in `F'`, giving the sole possible cancellation `delta=d_i+16`. The factorial digit-sum identity then yields

`L=4k+16-v2(binomial(c-1,b))`.

For `k=2^53`, this reduces to the single possible scale `L=4*2^53+16`. At equality `delta=0`, the complement is unit-valued with even derivative; the constant derivative term has valuation zero while the other two terms have valuations at least 11 and 17. The equality wall is therefore simple.

The added neighboring-depth identities also pass directly by the packet cocycle. The adjacent actual depth `r+1` has true terminal `k+16`, last lower address 16, and regular complement `k`. Its lower prefix is a unit. Since `Theta(16)=53` and `v2(16!)=15`, it lies inside the already-proved factorial-width band. This proves simplicity for the adjacent function while correctly retaining the remote complement in the split; it does not propagate that simplicity across the added address-one term without the preceding argument.

## Height-route negative conclusion and bounded source check

The epsilon isometry gives exactly the stated alternatives for excluding a repeated root. A quadratic over `Z_2` has no implied rational or bounded-height coefficient field, and the examples `Z^2+2^M` demonstrate that its analytic quadratic class does not bound critical-value valuation. Rational termination at nonnegative integer arguments does not make the critical point algebraic, and differentiation removes that termination. The rational-approximation criterion requires both nonzero approximants and a height strictly below the certified error precision; no such family has been established here.

I checked the introduction and hypothesis setup on printed pages 241–244 of Kunrui Yu, *Linear forms in p-adic logarithms III*, Compositio Mathematica 91 (1994), 241–276, at the published primary source `https://www.numdam.org/article/CM_1994__91_3_241_0.pdf`, on 2026-10-05. The requested applicability check passes: the setup uses nonzero algebraic bases in a number field, ordinary integer exponents, and a nonzero product-minus-one expression. The Euler obstruction supplies neither algebraicity/height for its evaluated unit ratio nor an ordinary integer exponent at its dyadic critical point. No explicit Yu constant or nonvanishing result is imported. This is a bounded source-applicability check, not a survey of all possible transcendence estimates; no local PDF was retained.

One minor qualification was identified and corrected before this followup was frozen. For the displayed logarithm partial sum, at `M=1` the height bound is 3 while the stated error precision is 5. The final text now restricts the comparison to `M>=2` and says the bound is at least the error precision: equality at 2, worse thereafter. This does not improve the critical-value argument or undermine its negative conclusion.

## Evidence and remaining gap

The independent followup run is `followup_run/FOLLOWUP_OUTPUT_CHECKS.json`, produced by `check_followup_outputs.py`. It uses exact integer/fraction arithmetic, independently reconstructs the four terminal-129 leaves and their roots, checks the one-bit ratio loss, checks the two boundary carry tables, and reconstructs the six-bit prefix-17 certificate. Its manifest validated successfully with the project root. No new broad original-index calculation was performed.

The new results leave two terminal-129 classes, one terminal-161 class, the explicitly isolated address-17 critical strata, and other untreated higher-address cases. Their exact Euler unit cancellations are still unproved. The height attempt identifies missing hypotheses but supplies no replacement theorem. The global verdict is therefore unchanged.
