# B75.3. A compatible local lift of conjugation and an endpoint-preserving normal form

This section additionally uses the inherited split toric uniformization at seven
and Block74's all-level local Kummer basis. It is not needed for the general
integral comparison C sigma(C)=-rho(j^2).

## Choosing j with rho(j^2)=I, without giving G_Q an involution

Put F=Q7(sqrt5), F_j=F(mu_(7^j)), and

    Omega_j=F_j(phi^(1/7^j),3^(1/7^j),7^(1/7^j)).

Choose compatible radicals. Block74 proves that their Kummer classes are
independent at each full7^j level. On Omega_j define a Q7-automorphism s_j by

    phi |-> 1-phi,       zeta_(7^j) |-> zeta_(7^j),
    phi^(1/7^j) |-> -phi^(-1/7^j),
    3^(1/7^j) |-> 3^(1/7^j),    7^(1/7^j) |-> 7^(1/7^j).

The power relations are respected, since7^j is odd and iota(phi)=-phi^-1.
Kummer independence supplies the presentation of Omega_j over F_j, so these
assignments give an automorphism, not merely formal substitutions. It has square1.
The assignments commute with the transition maps of radicals, hence define an
involution s of Omega=infinity-union Omega_j over Q7(mu_(7^infinity)).

Lift s to an element j of G_Q7, embedded in G_Q. It induces iota on F and has
chi(j)=1. Its square fixes Omega, but need NOT equal1 in the absolute Galois group.

Every element a in F* is, modulo7^j-th powers, a product of powers of phi,3,7.
Thus Omega_j contains its7^j-th roots. The actual split toric torsion sequence
shows J[7^j] is rational over Omega_j: the torus roots and the roots of all actual
F-rational period coordinates lie there. Hence

    rho(j^2)=I on T7(J).

For this one compatible choice, the ACTUAL operator in B75.2 satisfies

    U^2=-I,          C sigma(C)=-I.                         (4)

No actual integer solution, new period formula, or numerical Galois generator is
constructed. This is a compatible existence statement based on the inherited
local uniformization and explicitly defined Kummer tower.

## Integral semilinear descent of the lattice and of its endpoint chain

Use a COEFFICIENT-ring unit

    eta=(1+w)/2,        eta sigma(eta)=-1.

It is distinct from the base element phi, despite the same quadratic polynomial.
Define V=eta^-1 U. It is sigma-semilinear and V^2=I. Since2 is a unit in Z7,

    L=L^+ direct-sum L^-,     L^+=ker(V-I), L^-=ker(V+I).

Multiplication by w interchanges the two summands because V(wx)=-wV(x). It is
invertible, so both summands have Z7-rank2, and L^-=w L^+. Consequently any Z7-basis
of L^+ is an O-basis of L.

The same argument applies to every endpoint lattice L_i, which V preserves.
In particular L_n is the O-extension of L_n^+=L_n intersect L^+. Smith form for
the pair of Z7-lattices L_n^+ subset L^+ has elementary exponents0,n, since scalar
extension has the already known elementary exponents0,n. Choose a Z7-basis of L^+
adapted to this pair. In its induced O-frame, the entire chain is standard and

    V=coordinatewise sigma,       U=eta sigma.

The comparison formula becomes

    BOX: rho(j g j^-1)=sigma(rho(g))  exactly in one global integral frame. (5)

This frame is not numerically known for the eight candidates. It exists, preserves
BOTH actual endpoints, and works at every7-power precision. It is not a selection
of unrelated local frames. The residual[sqrt5] coefficient in this frame is in
F7*, so a Z7-diagonal rescaling can restore its normalization to1 without losing(5).

## What does NOT descend

L^+ is not asserted stable under rho(G_K). Equation(5) does not force rho(g) to
have Q7 entries. It is a SEMILINEAR base-conjugation relation, not an ordinary
rank-two Q7 representation or ordinary descent of beta. An explicit nonrational
trace control appears in NONCLOSURE.md.

The curve map f alone still has cocycle[-1]. Multiplying a TATE operator by eta
is a legitimate coefficient action on the stated lattice; this section does not
claim an algebraic endomorphism realizing eta or descent of the polarized curve
or Jacobian to Q.
