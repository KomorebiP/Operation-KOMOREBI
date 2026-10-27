# Valued Shell–Jet Bridge — v0.10.0

The v0.9 shell–jet calculus records which Fourier/jet channels are possible. v0.10 adds the first arithmetic depth layer.

## Primewise shell dynamics

For a raw frequency `ξ`, set `g = gcd(T,ξ)`. For prime `p`, define `a_p=v_p(T)` and `s_p=v_p(g)`. After radix multiplication by `m`,

`v_p(gcd(T,mξ)) = min(a_p, s_p + v_p(m))`.

Thus divisor-shell motion is exactly truncated addition on each local prime-valuation chain.

## Affine jet depths

For integer jet coefficients `a_j`, the contribution to output jet `q` under `X ↦ mX+r` is

`a_j * choose(j,q) * m^q * r^(j-q)` for `q≤j`.

Prime-power divisibility depths add termwise. Summation preserves the minimum certified depth, while cancellations can increase it. v0.10 treats the increase as surplus rather than replacing it by an unjustified equality.

## Standard-window arithmetic

If `p` is prime, `p ∣ N`, and `j<p`, then

`choose(Nn+j,j) ≡ 1 (mod p)`.

Hence this diagonal factor is a p-adic unit. This is the exact local mechanism needed in the earlier factorial-lane standard window.

## Integral denominator defect

For the uniform average denominator `1/N`, define

`L_N = {x : ℤ^N | N ∣ Σx_i}`.

Then the denominator cancels exactly on `L_N`, and

`ℤ^N/L_N ≃ ZMod N`.

This is the prototype for the later p-primary Smith/Fitting shell defect. It also proves the correct boundary: cancellation is a property of a distinguished arithmetic sublattice, not of every integral vector.
