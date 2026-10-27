# B73.1. The actual nontriangular modulo-49 deformation

Put R=O/49 and k=O/7. Choose a continuous upper Kummer cocycle b0 over R lifting
the actual residual alpha, with the same actual cyclotomic chi. Such a REFERENCE
exists: lift the three coefficients in alpha, take Kummer classes of the SAME
phi,3,sqrt5 in K*/K*49, and choose compatible cocycle representatives. Adjusting a
coboundary makes the reference reduction equal to the fixed residual matrix.

    rho0(g)=[[chi(g),b0(g)],[0,1]].

The reference has determinant chi and no [7] valuation coordinate at seven.
It is NOT identified with the actual rho. Every actual rho with this residual
matrix and determinant has a unique framed expression

    rho(g)=(I+7X(g))*rho0(g),
    X(g)=[[p(g),q(g)],[beta(g),-p(g)]] in sl2(k).

This follows from rho*rho0^-1=I mod7; determinant equality gives tr X=0.
The lower entry is 7 chi(g) beta(g), so beta is exactly the pinned opposite
cocycle, not an unrelated class. Multiplication gives

    X(gh)=X(g)+Ad(rhobar(g)) X(h).                         (1)

For rhobar(g)=[[x,a],[0,1]], direct conjugation sends (p,q,b) to

    (p+a*x^-1*b, x*q-2*a*p-a^2*x^-1*b, x^-1*b).           (2)

Writing a=alpha(g), x=bar chi(g), equations (1)-(2) are

    beta(gh)=beta(g)+x^-1 beta(h),
    p(gh)=p(g)+p(h)+a*x^-1 beta(h),
    q(gh)=q(g)+x*q(h)-2*a*p(h)-a^2*x^-1 beta(h).           (3)

There are no hidden characteristic-7 carry assumptions: rho0 is an actual
R-valued representation, and only X is computed over k. Conversely any continuous
X satisfying (1), with trace zero, gives an R-valued determinant-chi representation.
Strict conjugation by I+7Y changes X by Y-Ad(rhobar)Y.

## The global equations that a proposed beta must satisfy

With the inhomogeneous differential convention d p(g,h)=p(g)+p(h)-p(gh),

    d p(g,h)=-alpha(g)*chi(g)^-1*beta(h).                  (4)

Thus the known cup-zero theorem permits a primitive p, but it does not choose
its ACTUAL value. After p is fixed, the remaining upper equation is

    d_chi q(g,h)=2 alpha(g)p(h)+alpha(g)^2 chi(g)^-1 beta(h).
                                                               (5)

The right-hand side is a 2-cocycle: substitute the two 1-cocycle laws and (4)
into its 2-coboundary, and every term cancels. The primary and separate programs
check the explicit identity. A q solving (5), with the actual local conditions,
is still needed. We do not claim that this cohomological obstruction is nonzero
for any of the eight patterns, or that an unrestricted q produces a Frey Jacobian.

## Traces and the missing term

The actual trace is

    tr rho(g)=chi(g)+1+7*((chi(g)-1)p(g)+alpha(g)beta(g)) mod49.

On chi(g)=1 this reduces to the recorded product alpha(g)beta(g). The upper
cochain q is invisible to the trace at this order. That is precisely why a
trace sieve does not specify the entire actual first-order representation.
