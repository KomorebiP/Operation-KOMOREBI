# Complete local 7-primary torsion criterion

Use DIAGONAL_PERIODS.md and the inherited actual model. Let C=q^k C0 with
k>0, C0 a unit, and let Q=#kappa(v). Because q!=5, q is a uniformizer of F=K_v.

## B60.3. All period coordinates reduce to two Kummer coordinates

Fix M=7^j and write [z] for the class of z in F^*/F^{*M}, additively. Principal
units are M-divisible at residue characteristic q!=7, and [-1]=0. Define

    X=[phi],
    Z=7[C]-3[A]-3[3]-5[sqrt5].

The entire marked period matrix in this Kummer group is

    ([Pi_ij]) = [[Z+2X, -4X],[-4X, Z-2X]]
              = Z I + 2X R,   R=[[1,-2],[-2,-1]], R^2=5I.

Indeed kappa_a=-phi^2/(3^3 (sqrt5)^5), kappa_b=phi^-2/(3^3(sqrt5)^5),
and epsilon=C^7/A^3. Since 4 is a unit modulo M, ALL marked period coordinates
vanish if and only if X=Z=0. This is more than the previous single unit test.

R^2=5I is an identity in the marked period calculation. We do NOT identify R
with a global endomorphism, identify the base-field sqrt5 with a coefficient
coordinate, or claim the missing global semilinear lattice comparison.

## Finite torsion and period powers: both directions

For the split uniformization J^an=G_m^2/Lambda, the actual periods are F-rational
and Lambda is a free lattice. The finite exact sequence is

    0 -> mu_M^2 -> J[M] -> Lambda/M Lambda -> 0.

If full J[M] is rational, then mu_M is contained in F. For any lambda in
Lambda choose an Mth root z in the torus. Rationality of its torsion class
implies g(z)/z belongs to Lambda for every g. It also belongs to mu_M^2 because
lambda is rational. The lattice has no torsion, so the intersection is trivial.
Thus z is rational and every period coordinate is an Mth power in F.

Conversely, if mu_M is in F and all coordinates of a period-lattice basis are
Mth powers, choose their Mth roots in the split torus over F. Their classes,
together with mu_M^2, generate all of J[M] by the exact sequence. Hence every
M-torsion point is rational. This is full natural Jacobian torsion, not only
a semisimplification of a rational Tate module.

For q!=7, a unit is an Mth power in F precisely when its residue is: apply
Hensel's lemma, whose derivative M is a unit. For a general nonzero element
one also requires its valuation to be divisible by M. Moreover mu_M is in F
precisely when M divides Q-1.

## B60.4. The general exact local test

It follows that full J^nu[7^j] is F-rational if and only if ALL FOUR conditions
hold:

    7^j | Q-1,
    7^j | 7k,
    phi is a 7^j power in kappa(v)^*,
    Theta=C0^7/(3^3 A^3 (sqrt5)^5) is a 7^j power in kappa(v)^*.

The residue in the last line is well defined because A and C0 are units. The
valuation condition accounts for q^{7k}; it is not silently discarded when
passing from C to C0. The converse is a statement about this local Jacobian
only, not about the global actual depth n or beta.

## B60.5. Particularly simple seventh- and forty-ninth-power forms

The exact multiplicative identities

    Theta=(75 A)^(-3)*(C0 sqrt5)^7,
    Theta=(3*5^9*A/C0^35)^(-3)*(sqrt5/C0^2)^49

give, since gcd(3,7)=1:

    J^nu[7] is F-rational
      iff 7|Q-1, phi is a seventh power, and 75 A is a seventh power.

For M=49, the exact criterion is

    J^nu[49] is F-rational
      iff 49|Q-1, 7|k, phi is a 49th power,
          E=3*5^9*A/C0^35 is a 49th power in kappa(v)^*.

There is no approximation remaining in these power tests: all unknown higher
period terms are principal units and are automatically 7-primary powers at
q!=7. Thus the diagonal-period power calculation is complete at the local
level, even without computing infinitely many coefficients of the periods.

## Application to the opposite extension

At actual beta ramification with n=2, Block 59 supplies full J^nu[49]
rationality. Every such place therefore satisfies the four conditions above,
including the NEW rational-unit restriction on E. It also retains v7(k)=1
from the actual endpoint formula, which is stronger than 7|k.

The reverse inference is invalid: these four conditions do not construct an
actual global nonzero beta. They do not impose the common global Kummer
coefficients, fixed-prime values, or a single global natural lattice.
