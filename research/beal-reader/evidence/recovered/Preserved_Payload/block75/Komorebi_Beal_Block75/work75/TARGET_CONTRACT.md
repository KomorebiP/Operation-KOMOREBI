# Block 75 target contract

Execution predecessor: Block74 v7.4.0, SHA256
`d294e834ee2cec382139d217e8ad6b4405602b38612a2e294da4b19d0638c5b6`.
Its clean default verifier was run in this interaction and returned
PASS_DECLARED_CHECKS in 11.392 seconds. This is not a full historical replay.

## Requested goal and attained scope

Continue the SAME global integral deformation and labelled mixed-trace problem.
The new argument establishes an actual global integral semilinear comparison of
both endpoint lattices, induced by an explicit isomorphism of conjugate curves.
It does not compute the mixed trace, solve the global adjoint equations, or exclude
any of the eight residual patterns. The existence and normal form of the comparison
must not be confused with constructing a candidate global Galois representation.

## Exact hypotheses

G1. K=Q(sqrt5), phi=(1+sqrt5)/2, delta=9-3phi. The ACTUAL Jacobian J is that of the
smooth projective model of y^2=delta*(x^6+10B*x^3+12A*x+5B^2), with A,B rational.
This global model, not only a list of finite reductions, is required.
G2. L=T_7(J) is the actual natural lattice, free of rank two over
O=Z_7[w]/(w^2-5), with G_K-commuting integral O-action. E=Frac(O), k=F49,
sigma(w)=-w. Base phi and coefficient w are NOT identified.
G3. In a natural frame rho has lower-left entries in 7^n O, n>=1; its natural
residual extension is nonsplit, with class
alpha=u[phi]+r[3]+[sqrt5], u!=0, r!=0, last coefficient 1. The opposite residual
class beta is nonzero, so n is a finite actual endpoint depth. The mod7 cyclotomic
character is nontrivial and distinct from 1. Independence of the three displayed
Kummer generators is retained (and recalled in the proof).
G4. Only for the normalized local choice of j and the normal form: at F=K_(7),
J has the actual split toric uniformization with F-rational period lattice. Use
Block74's full local Kummer basis phi,3,7 and its all-level independence. This is
inherited geometry, not inferred from the new finite matrix examples.
G5. Only the nonclosure illustrations refer to the exact eight Block70 tuples,
whose complete conductor bound is unchanged. No new bound on C or its conductor.

The main integral intertwiner and its square identity need G1-G3, not G4, no
finite conductor bound, no Chebotarev construction of mixed traces, and no assumed
cohomological semilinearity. Nonzero u is an inherited arithmetic input. Thus the
argument is also a separate proof of the old all-depth cohomological conclusion,
conditional on that nonvanishing and the actual global curve model.

## Executed routes

1. Direct labelled trace evaluation: still unavailable from the eight residual
   tuples. No unrelated Frobenius values are relabelled as a product.
2. Global conjugate-curve route: explicit curve isomorphism, endpoint uniqueness,
   exclusion of an ordinary E-linear intertwiner, and the resulting INTEGRAL
   sigma-semilinear operator are proved in this block.
3. Stronger automatic realization/exclusion: refuted at the matrix-constraint
   level by exact positive packets. New comparison equations do not choose a
   global adjoint class or fix a numerical defect by themselves.

Proof status: written proofs conditional on G1-G4 where indicated; two separate
finite arithmetic implementations; same-assistant adversarial self-review only.
No new Lean, point counts, external referee, global signature or Beal proof.
