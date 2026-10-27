# B80.2. The fixed-place affine trace target has an explicit cochain formula

At a fixed place v above2,3,5,7, beta is a local coboundary. Use the unique lambda_v
such that

    beta(g)=(chi(g)^-1-1)lambda_v.

Uniqueness follows from an element with chi-1 a unit modulo7. Define

    p_v^fix(g)=lambda_v chi(g)^-1 alpha(g).                (6)

Direct expansion of alpha(gh)=alpha(g)+chi(g)alpha(h) gives

    d p_v^fix(g,h)=-alpha(g)chi(g)^-1 beta(h),
    (chi(g)-1)p_v^fix(g)+alpha(g)beta(g)=0.                 (7)

The second equation is exactly the first-order fixed toric trace condition.
If another local primitive meets it, its difference z is an ordinary character
with (chi(g)-1)z(g)=0. For a separating h, z(h)=z(hg)=0 whenever chi(g)=1;
the other g already give z(g)=0. Thus(6) is the UNIQUE local cochain meeting both
the given primitive and trace equations in this fixed framing.

This is a formula in the actual residual alpha and beta, not a numerical choice
of lambda_v or an assertion that one may assign local p values independently.
For any bare global p0 from B80.1, p_v^fix-p0|_v is an ordinary local character.
That difference, not either inhomogeneous cochain separately, has well-defined
local class-field coordinates used by the affine evaluator.

An exhaustive F7 check of12348 input cases confirms(7). The proof is the displayed
cocycle expansion and works over k. It is not promoted from finite testing.
