# B61.3. The chi^-1 Frobenius matrix, with its nonzero kernel

Let M=Q(zeta), zeta^7=1, zeta!=1. Restrict the descended class gamma of
TWISTED_DESCENT.md to M. It is a k-valued additive character lambda, satisfying

    lambda(delta_a g delta_a^-1)=a^-1 lambda(g),
    delta_a(zeta)=zeta^a, a in F7^*.

It is unramified outside primes over S={197,883,1373,1667}, and locally zero
at seven. This is NOT the ordinary ray-character problem for eta.

## Ray-class presentation and the absence of hidden classes

The no-seven class-group input for L=K(zeta7) implies Cl(M)[7]=0 as well:
extension of ideals followed by norm for L/M acts as2, so a seven-primary
class killed on extension was zero already. The ray sequence therefore
presents every exponent-seven character by its residue inertia factors.

All support primes q split completely in M. Since q!=7, an exponent-seven
ramified character is tame and has conductor exponent at most1. No higher
conductor variables are omitted. The chi^-1 projection of global units is
zero: complex conjugation is +1 on units modulo roots of unity, while their
only possible odd seven-primary root-of-unity component has character chi,
not chi^-1. The quotient action has order6, prime to7, so eigenspace projection
is exact. In particular an inertia vector in this eigenspace has no unknown
unramified class-group correction.

The prime over7 is fixed by Gal(M/Q), so any chi^-1-equivariant unramified
character kills its ideal class and is locally zero there. These statements
also follow from the inherited Block49 argument with M in place of L. We use
the ray exact sequence checked in Milne CFT V, Theorem1.7, not ordinary eta rows.

## Choice of prime ideals and the twist orientation

For each q choose an integral generator pi_q of norm q. Let r_q be the unique
primitive seventh root modulo q at which pi_q vanishes. Index primes by

    p_(q,b): zeta -> r_q^b,     b=1,...,6.

Under delta_a, prime b moves to b/a. Identifying all rational residue fields
by their rational elements makes the residue character at b equal to

    b*s_q * ell_q,    ell_q=log_base_2 mod7.            (3)

Indeed the coefficient relation at b/a is a^-1 times that at b. The primitive
root2 is verified at each support prime. Constant weights would belong to
the ordinary character, and inverse weights would give the opposite
cyclotomic orientation. Both replacements are unjustified here.

## Exact integral generators

Coefficient vectors below are in the basis 1,zeta,...,zeta^5:

| norm | coefficient vector |
|---|---|
|197|(1,-1,-1,-1,1,-1)|
|883|(0,0,1,-2,1,2)|
|1373|(0,2,-2,-1,-2,-2)|
|1667|(1,-2,1,2,1,2)|
|29|(0,0,0,1,-1,-1)|
|71|(0,1,-1,-1,1,-1)|
|491|(0,1,-2,2,0,2)|

Their exact norms are the positive primes in the first column, so each
principal ideal is a single prime ideal of that norm, not a product needing
an unrecorded class-group choice. The four r_q values are191,199,333,502.

## Frobenius values from principal ideles

For ell=29,71,491, use the indicated pi_ell. Its components at all conductor
places are units. Global reciprocity on the principal idele pi_ell gives

    lambda(Frob_(pi_ell))
       = -sum_(q in S) s_q sum_(b=1)^6 b*ell_q(pi_ell(r_q^b)).       (4)

The sign convention is immaterial for the homogeneous zero equations, but
is kept consistently in the data. Full local gamma-zero at ell, proved in
OPPOSITE_FROBENIUS.md and descended in TWISTED_DESCENT.md, makes (4) zero.
Conjugate test primes yield scalar multiples a^-1 of the same equation.

With rows29,71,491 and columns197,883,1373,1667, the exact matrix is

    R=[[4,2,6,1],
       [6,2,0,5],
       [3,6,1,6]]  over F7.

Column-deletion integer determinants are100,-140,-84,176, reducing to2,0,0,1.
Hence rank(R)=3 and, over k=F49 as well,

    ker R = k*(1,0,0,3).                              (5)

The matrix does NOT have rank4, and reciprocity alone does NOT give beta=0.
The nonzero abstract character line is retained as a mandatory control. It
is incompatible with the common natural Kummer class only in the next proof.

## Normalization and completeness checks

The primary implementation uses multiplication determinants and complete
rational discrete-log tables. The separate checker uses theta=zeta^-1,
cyclic group-ring norm products, direct seventh-power symbols, determinant
expansion, and Cramer's rule. It verifies the prime permutation yielding
(3), changes the primitive generator to its inverse, and recomputes all
72 residue symbols and all6 split phi tests. The primary also tests all
6^4=1296 independent base-prime reindexings; support of the kernel is invariant.

The ray-class calculation is for beta's stipulated complete ramification
support, not the complete set of divisors of C. A new prime dividing C without
beta ramification adds no residue factor to this character. A new ramified
prime does add a column and is not silently omitted by this theorem.
