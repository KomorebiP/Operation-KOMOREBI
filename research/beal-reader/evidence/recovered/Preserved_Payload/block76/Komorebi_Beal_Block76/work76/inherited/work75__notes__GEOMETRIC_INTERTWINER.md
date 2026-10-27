# B75.2. The conjugate curve supplies an actual integral semilinear operator

Retain G1-G3. Let iota(phi)=1-phi. Direct calculation in K gives

    iota(delta)=6+3phi=phi^2 delta,       phi*iota(phi)=-1.

Because A,B are rational, there is a K-ISOMORPHISM of actual curves

    f: C^iota -> C,          (x,y) |-> (x,y/phi).

It induces an integral isomorphism of their Jacobians and Tate lattices. No
Frobenius matching, isogeny replacement, or Tate-isogeny theorem is being used.
Moreover f composed with iota(f) is the hyperelliptic involution y|->-y. On the
Jacobian that involution is [-1]: for points P,Q the degree-two fibers give
P+iota_hyp(P) linearly equivalent to Q+iota_hyp(Q), hence
[iota_hyp(P)-iota_hyp(Q)]=-[P-Q]. Such divisor differences generate the Jacobian.

Choose j in G_Q inducing iota on K and fixing every7-power root of unity, so
chi(j)=1. Existence follows because K and the7-cyclotomic tower are disjoint;
K is ramified at5 and has degree2, whereas that tower is ramified only at7.
Equivalently one may choose j locally at7 as in NORMAL_FORM.md.

On the actual natural Tate module put

    U = f_* composed with j_*.

This is a Z7-linear integral automorphism. Functoriality gives, for g in G_K,

    U rho(g) = rho(j g j^-1) U,          U^2=-rho(j^2).       (1)

The second identity keeps the hyperelliptic minus sign. It is not a descent datum
with square +1, and j itself is NOT assumed to have order two in G_Q.

## Why no ordinary E-linear intertwiner can occur

Write rho^j(g)=rho(j g j^-1). It has exactly the same image and stable-lattice
segment as rho. Suppose A:rho->rho^j is a nonzero E-linear intertwiner. Absolute
irreducibility makes A invertible. By B75.1 it carries the unique oriented natural
endpoint to itself up to homothety. Rescale it to an integral isomorphism there.
Modulo7 it preserves the unique chi-line, so it identifies the natural extension
classes up to ONE nonzero scalar.

The three global Kummer generators are independent: valuations at3 and5 separate
[3] and[sqrt5], while phi is not a seventh power among the units of K. Base
conjugation with chi(j)=1 acts on them as(-[phi],[3],[sqrt5]), because -1 is a
seventh power. The assumed normalized natural class and its conjugate are

    (u,r,1),              (-u,r,1).

Proportionality would have scalar1 from their final coordinates, and then -u=u,
contradicting u!=0. Thus

    Hom_E[G_K](rho,rho^j)=0.                              (2)

This argument does NOT assume the previously proved u^7=-u or semilinearity.
It uses only the retained nonzero unit coefficient and endpoint uniqueness.

## Project the ACTUAL geometric operator, not an invented one

The coefficient endomorphism w commutes with rho and rho^j. For any Q7-linear
intertwiner V define

    V_+ = (V+w^-1 V w)/2,     V_- = (V-w^-1 V w)/2.

V_+ is E-linear. V_- anticommutes with w, hence is sigma-semilinear. Both remain
intertwiners, since the coefficient action commutes with the representations.
Apply this to the actual U. Equation(2) gives U_+=0. Consequently

    U(a x)=sigma(a)U(x),   a in E.

Since U is an integral automorphism of the NATURAL Tate lattice, in any natural
O-basis it is C sigma with C in GL2(O), not merely GL2(E). Therefore

    BOX: rho(j g j^-1)=C sigma(rho(g)) C^-1  for every g,
    BOX: C sigma(C)=-rho(j^2).                            (3)

The operator is induced by the specific curve map f. It is not a semilinear
comparison inferred solely from residual cohomology or characteristic polynomials.
In particular U w U^-1=-w is established on the actual Tate module, without
identifying w with the base-field sqrt5.

## Both endpoints are preserved

sigma fixes the valuations and residual character labels. The sigma-semilinear U
maps the two oriented endpoint homothety classes to themselves. It is unimodular
on L_0, so B75.1 gives U(L_n)=L_n and U(L_i)=L_i for the whole segment. Thus in a
natural endpoint frame

    C21 in7^n O,           C11,C22 units.

On residual graded lines C acts by its two diagonal scalars. Comparing the
normalized[sqrt5] coefficient forces their ratio to be1. The same opposite-endpoint
comparison has the reciprocal ratio, also1. The residual consequences are

    (-u,r,1)=(sigma(u),sigma(r),1),       j[beta]=sigma[beta].

This is a new route to the old cohomological result, and a stronger INTEGRAL
comparison. The numerical C for the eight unknown global realizations has not
been computed.
