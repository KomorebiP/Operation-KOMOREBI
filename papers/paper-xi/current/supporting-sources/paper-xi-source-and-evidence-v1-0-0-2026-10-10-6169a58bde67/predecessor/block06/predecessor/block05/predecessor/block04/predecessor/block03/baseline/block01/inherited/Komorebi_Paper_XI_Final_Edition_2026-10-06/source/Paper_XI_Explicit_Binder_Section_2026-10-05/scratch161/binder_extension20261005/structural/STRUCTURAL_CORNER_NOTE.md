# Exact fifth-coordinate repair and obstruction for the whole corner

This is a read-only continuation of the recovered binder calculation. It does not assert native-action or full-character compatibility. Matrix units use zero-based indices. All assertions concern the original cubic fixture over F_3((t)).

## The exact fifth-coordinate family

Let K=(1+t)e²/t and let

x=t(aE05+bE16+cE27+dE38)+t² h/(1+t) E08.

Every supported column lies outside all supported rows, so x²=0. The old four coordinates have grade 4 and the new coordinate has grade 10, hence x belongs to P^4. The denominator 1+t is a unit of F_3[[t]], so this is an actual F-matrix, not a formal extension of the coefficient field.

Sparse composition and the retained normalized corestriction give exactly

Q01=−cd K+c(a−h)e,
Q12=−ab K+b(d−h)e,
Q20=−bc(e+e/t),

with all other entries zero. In particular the leading cycle (cd,ab,bc) is unchanged. The unit denominator removes the otherwise unwanted factor 1+t on the new higher-order terms.

For nonzero prescribed u,v,w and arbitrary p,q, the equations are cd=u, ab=v, bc=w, c(a−h)=p, b(d−h)=q. Every solution has

a=v/s, b=s, c=w/s, d=us/w,
h=(u s²/w−q)/s,

where s is nonzero and satisfies

s²(p+u)=w(q+v).

Conversely these formulas satisfy all five equations. Thus the complete solvability condition is that this equation admit a nonzero square z=s². If p+u is nonzero this is the ordinary nonzero square-class test for w(q+v)/(p+u). If p+u=0 then solvability requires q+v=0, and any nonzero s works.

Over F_3 one has s²=1, so the necessary and sufficient condition reduces to

p+u=w(q+v).

For u=v=w=1, p=q=2, choose s=1 and h=2. This explicitly repairs the previous four-coordinate failure:

x=t(E05+E16+E27+E38)+2t²/(1+t) E08.

The exact derived matrix has Q01=Q12=−K+2e and Q20=−(e+e/t).

## Why a larger same-corner family cannot solve everything

Consider ANY x supported on rows 0,1,2,3 and columns 5,6,7,8, satisfying x in P^4. For each permitted position write

x_ij=t X_ij(t) if j−i≤5,
x_ij=t² X_ij(t) if j−i>5,

with arbitrary X_ij(t) in F_3[[t]]. This parametrizes the whole corner intersected with P^4, including infinitely many higher t coefficients. It remains square zero identically.

Let a,b,c,d be the residues of X05,X16,X27,X38, and let r be the residue of X08. Direct quadratic composition, now allowing all sixteen coordinates, yields:

[e^−1]Q01=cd,
[e^−1]Q12=ab,
[e^−2]Q20=bc,
[e^1]Q01=ac−cr,
[e^1]Q12=bd−br.

Here the coefficients are the unique Laurent expansion in e, using t=−e³/(1+e). These statements hold for arbitrary X_ij(t), not just residue constants. Terms in Q01 and Q12 other than the displayed contributing monomials either start at e² or at e⁴. The base factor −K=e^−1+1−e² contributes no e¹ term; multiplying it by a t-divisible coefficient starts at e². Thus no omitted higher t coefficient can alter the two displayed e¹ coefficients.

If the three leading coefficients (u,v,w) are nonzero, then a,b,c,d are nonzero and b²=1. Therefore every member of this whole corner necessarily satisfies

[e^1]Q01−w[e^1]Q12=vw−u.

Consequently the fifth-coordinate family reaches every allowable (p,q) projection of the entire square-zero corner: the residual obstruction p+u=w(q+v) cannot be removed merely by adding more entries or higher t coefficients within the same corner. For example u=v=w=1, p=1,q=2 violates it, so cannot occur there. This is an obstruction for this coordinate corner and these specified coefficients only, not a counterexample to the full arithmetic realization problem. A different square-zero support or a nonsquare-zero conjugator could evade it.

The independently generated files full_corner.py and full16_corner.py print exact expressions for all entries of Q for the ten shallow and all sixteen minimally valued corner coordinates. Their arithmetic is inherited from the recovered exact ring implementation. The displayed coefficient argument extends those finite polynomial identities to arbitrary integral power series by continuity and the explicit valuation bounds above.
