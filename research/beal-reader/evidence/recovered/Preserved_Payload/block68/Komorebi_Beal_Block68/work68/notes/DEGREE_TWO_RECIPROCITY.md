# B68.1. Frobenius-orbit conductor columns for the inverse cyclotomic twist

Let M=Q(zeta7). In the stipulated all-inert bounded regime, the actual opposite
class descends to gamma in H1(Q,F7(chi^-1)). Its restriction lambda to G_M is
additive and satisfies lambda(delta_a g delta_a^-1)=a^-1 lambda(g).
The class-group, unit-eigenspace and fixed-prime inputs remain inherited.

For a rational conductor prime q=1 mod7, M has six degree-one primes.
For q=-1 mod7, it has THREE degree-two primes. Write k_q=F_(q^f), f=1 or2,
choose primitive g_q, put z_q=g_q^((q^f-1)/7), and let ell_q be the logarithm
modulo7 in this generator. Embeddings zeta7 -> z_q^b are indexed by b=1,...,6.
The chi^-1 residue functional in that coordinate is b*s_q*ell_q.

If f=2, b and -b define the same prime. Frobenius changes x to x^q, and
ell_q(x^q)=q ell_q(x)=-ell_q(x) modulo7. Therefore

    (-b)*ell_q(x^q)=b*ell_q(x).

The functional is well defined on a PRIME IDEAL, not just an embedding.
Choose representatives {1,2,3} of the three pairs {1,6},{2,5},{3,4}.
For an integral generator pi_l of a test prime l outside the conductor,
principal-idele reciprocity gives

    R_(l,q)=-sum_(b in reps) b*ell_q(pi_l(z_q^b)).

Equivalently, for f in{1,2},

    R_(l,q)= -f^(-1) sum_(b=1)^6 b*ell_q(pi_l(z_q^b)) mod7.

The inverse f exists modulo7. Using the unadjusted six-embedding sum at f=2
counts each prime twice. That would rescale an entire unknown conductor column,
not magically prove emptiness, but it would be the wrong declared normalization.
Changing pi_l by delta_a scales its row by a^-1. This is the chi^-1 twist;
constant weights and inverse-b weights are different problems.

## Concrete finite fields

The primary uses phi^2=phi+1. Its chosen primitive generators and seventh roots:

    q307:  g=5+phi, z=175+224phi;
    q797:  g=4+phi, z=573+85phi;
    q1483: g=3+phi, z=887+1044phi.

The factorizations of Phi7(T), with coefficients reduced modulo q, are

    307:  (T^2+40T+1)(T^2+244T+1)(T^2+24T+1);
    797:  (T^2+363T+1)(T^2+535T+1)(T^2+697T+1);
    1483: (T^2+148T+1)(T^2+343T+1)(T^2+993T+1).

Every factor has nonsquare discriminant. The product is exactly Phi7.
At all three primes the natural Kummer row (phi,3,sqrt5) is(0,0,0).
Thus these new columns are permitted for every nonzero ratio r. They cannot
be discarded by the old ratio filters.

The full row table, every residue evaluation and the generator norms are in
verification/columns_extended68.json. The separate checker uses theta^2=d,
weighted residue PRODUCTS instead of sums of individual logarithms, all six
Galois conjugations, and all eight choices of degree-two orbit representatives.
It also checks that the cyclotomic units have zero chi^-1 projection.

The shared residue field at an inert prime does not identify its phi with
coefficient-field w. These are different roles throughout the calculation.
