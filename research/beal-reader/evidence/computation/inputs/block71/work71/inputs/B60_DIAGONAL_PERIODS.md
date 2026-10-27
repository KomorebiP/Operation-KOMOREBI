# The two diagonal Jacobian periods

All actual arithmetic applications retain TARGET_CONTRACT.md. Put

    phi=(1+sqrt5)/2, omega=sqrt5=2phi-1,
    delta=3(5-omega)/2=9-3phi,
    a=phi-1, b=-phi.

Let F=K_v at q outside {2,3,5,7}, with maximal ideal m and residue field kappa.
The periods below are multiplicative Jacobian periods in the marked node-cycle
basis, not a freely chosen torus lattice. We write Pi_ij to avoid confusing a
period coordinate with the rational residue characteristic q.

## B60.1. The actual one-parameter normalization

Take u=A^2/B^3. Substituting x=uX, z=u^3 Z gives A'=A/u^5=zeta^3 and
B'=B/u^3=zeta^2, with zeta=B^5/A^3. The equation gives zeta=-1+epsilon,
epsilon=C^7/A^3. Thus the normalized twisted family is

    Z^2=delta f_epsilon(X),
    f_epsilon=X^6+10(epsilon-1)^2 X^3
              +12(epsilon-1)^3 X+5(epsilon-1)^4.

At epsilon=0,

    f_0=g^2 h,  g=X^2+X-1, h=X^2-2X+5.

The first variation is

    R(X)=partial_epsilon f_epsilon|_0=-20X^3+36X-20,
    R mod g=-4X.

In particular the two smoothing directions are R(a)=-4a, R(b)=-4b; both are
units. Each node has thickness v(epsilon)=7 v_q(C). The scaling is by a unit,
so it does not change the natural Jacobian or introduce a new ramified twist.

## Marked normalization and branch coordinates

The normalized central conic is Y^2=delta h(X). Use

    lambda=(Y-delta)/(X-a),  A0=phi-2.

Its inverse X-coordinate is

    X(lambda)=a+2delta(A0-lambda)/(lambda^2-delta).

The marked branch values are

    node a: lambda=A0 and infinity,
    node b: lambda=B+=3phi-6 and B-=3phi.

At node a choose w_a=lambda-A0 near the plus branch, with 1/w_a near the minus
branch. At node b use w_b=(lambda-B+)/(lambda-B-) and its reciprocal. If x=X-k
at a node k, write their first derivatives as C_k^+ x and C_k^- x. Explicitly,

    C_a^+=2/delta,           C_a^-=-1/(2delta),
    C_b^+=(4phi-7)/15,       C_b^-=(phi+2)/15.

Hence

    C_a^+ C_a^-=-phi^2/45,
    C_b^+ C_b^-=-phi^(-2)/45.

These factors are invariant under scaling w_k by a unit and its reciprocal by
the inverse unit. They are calculated from the actual paired branches, not
from an arbitrary repartition of four points.

## B60.2. Smoothing to the diagonal multiplier

Here is the local comparison, including its sign. Around node k, set x=X-k.
The analytic square root H(X)=sqrt(delta h(X)) g(X)/(X-k) exists over F, since
both branch values are rational and 2 is a unit. Its value H_k satisfies

    H_k^2=delta h(k)g'(k)^2.

Put U=Z+H(X)x and V=Z-H(X)x. Then

    UV=delta(f_epsilon-f_0).

On the central plus branch U=2H_k x+O(x^2); on the central minus branch
V=-2H_k x+O(x^2). Consequently the first-order smoothing parameter in the
marked branch coordinates w_k and 1/w_k is

    y_k = - C_k^+ C_k^- delta R(k)/(4 H_k^2) * epsilon + O(epsilon^2)
        = C_k^+ C_k^- k/(h(k)g'(k)^2) * epsilon + O(epsilon^2).

Terms proportional to x*epsilon vanish in the node's first-order smoothing
space. Moving the component's marked positions changes only higher terms in
y_k, since y_k=0 on the central fiber.

Why is this y_k the Schottky multiplier rather than an unspecified node unit?
For fixed branch points P+,P-, put w=(lambda-P+)/(lambda-P-). The standard
Schottky generator has w(gamma(lambda))=y_k w(lambda). Gluing the two branch
charts therefore gives w_plus*(1/w)_minus=y_k. This follows directly from the
matrix formula in Ichikawa 1909.10149v4, section 2.3. Its universal deformation
statement identifies this gluing with the given split stable family. We have
computed the derivative of that very marked gluing parameter.

The diagonal case of the period product in Ichikawa (1993), section 1.2 and
sections 2.4-2.7, gives Pi_kk/y_k in 1+(y_a,y_b). In particular, after
specialization, all other factors are principal units. Combining with the
computed smoothing derivative proves

    Pi_aa = epsilon*kappa_a*(1+m),
    Pi_bb = epsilon*kappa_b*(1+m),

where the constants are EXACTLY

    kappa_a=-phi^2/(675*sqrt5)=-(1+3phi)/3375,
    kappa_b= phi^(-2)/(675*sqrt5)=(-4+3phi)/3375.

The notation means the quotient by the displayed leading term belongs to
1+m. It is not an equality discarding an uncontrolled residue unit. All
branch separations and denominators used here are units at q outside
{2,3,5,7}. The universal product has integral coefficients after inverting
these separations, so higher terms remain principal units in the specialization.

Together with the retained off-diagonal calculation, choose orientations with

    Pi_ab=Pi_ba=(-phi^(-4))*(1+m).

The constants satisfy

    kappa_b/kappa_a=-phi^(-4),
    kappa_a*kappa_b=-1/(3^6*5^5).

Reversing a node orientation can invert an off-diagonal period; every torsion
power condition below is invariant under the corresponding integral change
of period/torus bases. No merely isogenous lattice is substituted.

## Sanity check of the smoothing normalization

For the one-node elliptic family y^2=x^3+x^2+e, the central normalization is
x=t^2-1, y=x t, with paired points t=1,-1. The analogous normalized derivatives
are 1/4,1/4, and R(0)=H_0^2=1. The same smoothing formula gives y=-e/64+O(e^2).
The Weierstrass invariants have c4=16 and discriminant -64e-432e^2, so 1/j has
the same leading coefficient -1/64. This checks the factor of four and sign;
it is not the proof of the genus-two comparison.

## Evidence level

The algebraic constants are checked over Q(phi) and all 445 residue fields at
primes 11<=q<=2000, including both split places. The independent program uses
the inverse-conic derivative in a sqrt5 basis and evaluates R(k) directly.
These computations do not certify the analytic universal-deformation theorem.
The latter and the source-to-family comparison above remain a written proof,
conditional on the inherited actual model and split uniformization.
