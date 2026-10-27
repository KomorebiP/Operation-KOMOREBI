# The fixed-depth residual has no finite linear polynomial recurrence

Base: `Euler-coupled-stationarity-20261005`.
Source: `sources/euler_v4.md`, equations (1.1), (1.2), (2.2).

## The attempted implication

One proposed way to prove arithmetic nonvanishing was to resum the residual
into a finite linear system, then use an algebraic resultant or a nonzero
forcing term. There is a rigorous obstruction to one precise version of this
route. For each fixed ordinary integer r>=1, the ordinary value sequence

    g_n=G_r(n), n>=0,

satisfies no nonzero eventual linear recurrence with coefficients polynomial
in n over Q, or over Q_2. In particular, it is not a finite exponential-polynomial sequence
and does not satisfy a constant-coefficient recurrence.

This does not rule out nonlinear identities, functional equations with
rescaling, or a useful finite system involving additional transcendental
functions. It does not prove nonvanishing.

## Proof

First, all g_n are rational because their defining packet sums terminate at
ordinary n. Any proposed recurrence of fixed order and fixed coefficient
degrees imposes a system of homogeneous linear equations with rational
entries on finitely many unknown recurrence coefficients. Its row space is
finite-dimensional, hence spanned by finitely many of these rational rows.
If that system has a nonzero solution over Q_2, its rational matrix has
deficient rank and therefore also a nonzero solution over Q. It suffices to
exclude recurrences over Q.

Set A_N=(3^(2N+2)-1)/(4(2N+1)(2N+2)) and

    C_r(t)=sum_{m=0}^{r-1} kappa_m t^(2m)/(2m)!.

The exact even exponential generating function of the omitted tail is

    F_r(t)=sum_{N>=0} T_(r-1)(N) t^(2N)/(2N)!
          =sech(t)-C_r(t) A_egf(t),

where

    A_egf(t)=sinh(2t)sinh(t)/(2t^2)
           =(cosh(3t)-cosh(t))/(4t^2).

The apparent singularity at t=0 is removable, so A_egf is entire over C.
Consequently C_r A_egf is entire. The meromorphic function F_r therefore
retains every pole of sech(t), namely

    t=i*pi*(k+1/2), k in Z.

Each is a genuine simple pole: an entire summand cannot cancel its principal
part. Thus F_r has infinitely many distinct finite complex singularities.

Suppose g_n satisfied an eventual polynomial-coefficient linear recurrence.
The exact factorization of the tail gives

    T_(r-1)(n+r)=kappa_r * 2^mu_r * binom(2n+2r,2r) * g_n.

The binomial factor is a nonzero polynomial in n with rational coefficients.
Multiplying a sequence by such a polynomial preserves the recurrence
property: substitute g_(n+j)=h_(n+j)/p(n+j) into its recurrence and clear
the finitely many denominators. Shifting the index and adjoining finitely
many initial values also preserves an eventual recurrence. Hence the tail
sequence b_N=T_(r-1)(N) would satisfy one.

The sequence a_N=b_N/(2N)! would also satisfy a polynomial-coefficient
recurrence. Indeed (2N+2j)!/(2N)! is a polynomial in N for each fixed j, so
factorial division in the recurrence can be cleared by the same operation.

For completeness, the elementary recurrence-to-differential-equation step is
as follows. In an ordinary generating series A(y)=sum a_N y^N, the operator
theta=y*d/dy acts on its N-th coefficient as multiplication by N. A finite
polynomial recurrence therefore becomes, after multiplying by a sufficient
power of y, a linear differential equation with polynomial coefficients and
a polynomial right side accounting for the finitely many initial terms.
Differentiating enough times annihilates that right side and gives a
nonzero homogeneous linear differential equation. Thus A(y) is D-finite.

The series F_r(t)=A(t^2) is then D-finite as well. One can see this without
invoking a closure theorem: repeated t-derivatives of A(t^2) lie in the
finite-dimensional C(t)-span of the finitely many derivatives of A needed
by its differential equation, evaluated at t^2. A linear dependence gives
a differential equation with rational coefficients; clear denominators.

Finally, a solution germ of a nonzero linear differential equation with
polynomial coefficients can have finite singularities only at zeros of the
leading coefficient. Away from those finitely many points, the equation is
an ordinary analytic first-order system after adjoining its lower
derivatives, and its solutions analytically continue locally without poles.
This contradicts the infinitely many poles of F_r. The proposed recurrence
does not exist.

## Consequence for the current arithmetic target

The stationary-value problem cannot be reduced by claiming that the entire
fixed-r residual sequence is a finite exponential polynomial or a sequence
with a finite linear polynomial recurrence. In particular, general decision
results about zeros of finite exponential polynomials require a missing
representation here, and the representation just ruled out cannot supply
it.

The exact Bernoulli convolution and doubling identities pursued in the
parallel unit-identity route are nonlinear or involve rescaling. This proof
does not obstruct them. Their cutoff defects must be tracked explicitly.

No computation or imported transcendence conjecture is used in this proof.
No historical novelty claim is made.
