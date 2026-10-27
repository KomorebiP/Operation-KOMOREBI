# The abstract opposite-extension space at eligible primes

Base checkpoint: Block48 archive
`bbf78879d4b5714c818dd1521053dcd6b80c0694799b120b440fa850efec091a`.
Companion to `extension_route.md`. Status: written proof; fresh independent review is recorded in
`extension_audit.md`.
This statement concerns abstract Galois extensions. It does not construct a
Jacobian, an RM Tate module, or a solution to A^3+B^5=C^7.

Let K=Q(sqrt(5)), L=K(zeta_7), Delta=Gal(L/K), and chi the mod-seven
cyclotomic character. Thus Delta is cyclic of order six and chi identifies
it with F_7^*. Let S be a finite set of finite primes v of K, all away from
seven, such that Nv=1 modulo seven. Define H_S to be the subgroup of
H^1(K,F_7(chi^-1)) consisting of classes unramified outside S and seven,
and whose restriction to G_K7 is zero.

Then

    dim_F7 H_S = |S|.

After extension of coefficients,

    dim_F49 H_S(F_49) = |S|,
    dim_F7  H_S(F_49) = 2|S|.

Here S is a set of primes of K. A rational prime q splitting in K can
contribute two such primes, whereas an inert q contributes one.

## Proof

The ordinary ideal class group of L has no seven-primary part. This follows
from h(Q(zeta_35))=1 and the extension/norm argument for the degree-two
extension Q(zeta_35)/L, exactly as in `extension_route.md`.

Every v in S splits completely in L/K, because its cyclotomic Frobenius
is Nv modulo seven. Let m be the product of all primes of L above S.
The ray-class exact sequence is

    O_L^* -> (O_L/m)^* -> Cl_m(L) -> Cl(L) -> 0.

At each v in S, the seven-primary part of the residue-factor group is a
product of six cyclic groups of the same nonzero seven-power order. Delta
acts simply transitively on the six primes above v. Choosing an identification
at one prime and transporting it makes this an induced, hence regular,
Delta-module. Its quotient modulo seven has each F_7-valued character of
Delta with multiplicity one.

We need the chi^-1 eigenspace. The global unit group has no such eigenspace
modulo seventh powers. Indeed L is CM with complex conjugation c in Delta.
For every unit u, u/c(u) has absolute value one in every complex embedding,
so is a root of unity. Indeed its powers are algebraic integers of bounded
degree with all conjugates bounded by one. Their monic minimal polynomials
have bounded integer coefficients, so only finitely many powers occur. Therefore c acts trivially on
units modulo roots of unity. The only possible odd character in the unit
group modulo seventh powers is the character on its seven-primary roots of
unity. This is chi, from mu_7. It is not chi^-1, since chi has order six.
Thus the image of the units has zero chi^-1 component. The exact sequence,
the vanishing ordinary class-group seven-part, and the semisimplicity of the
Delta action (six is prime to seven) give

    dim_F7 Hom_Delta(Cl_m(L), F_7(chi^-1)) = |S|.     (1)

Global class field theory identifies this Hom space with Delta-equivariant
characters of G_L unramified outside m, with tame conductor at most one at
its primes. Conversely, any exponent-seven abelian extension at a prime
of residue characteristic other than seven is tamely ramified, so its
conductor exponent is at most one. Hence no higher conductor is omitted.

There is a unique prime P_7 of L above seven: seven is inert in K, and
L/K is totally ramified of degree six there. Delta fixes P_7 and consequently
fixes its ray ideal class in Cl_m(L). A chi^-1-equivariant homomorphism to
F_7 therefore vanishes on that ideal class. The corresponding unramified
local character at P_7 is zero, since Frobenius is the Artin image of P_7.
Thus all the characters in (1) are split at P_7.

Inflation--restriction is an isomorphism

    H^1(K,F_7(chi^-1))
       = H^1(L,F_7)^Delta,

where the right invariants include the coefficient action chi^-1: H^1 and
H^2 of Delta vanish because its order is prime to seven. This identification
uses the rule h(delta g delta^-1)=chi^-1(delta)h(g), so the ray-class character
in (1) has exactly the required orientation. The analogous local restriction
map at seven is injective for the same reason. Therefore the split condition
at P_7 implies the split condition at K_7. At all other primes, L/K is
unramified and the above construction has exactly the stipulated ramification.
It follows that (1) identifies with H_S, proving the dimension formula.

Tensoring the finite-dimensional cohomology group with F_49 gives the last
two equalities. No coefficient-field restriction is being silently dropped.

## Meaning for the Beal route

When S is empty, this proves precisely the vanishing used in the
additional-prime theorem. Once even one eligible prime is allowed, the
abstract opposite-extension space is nonzero. Therefore the ordinary
class-number obstruction cannot eliminate all candidate C merely by
repeating the same extension argument with more eligible primes present.

Such classes still need not come from the geometric Tate representation.
Their survival identifies the extra geometric information a stronger proof
would need. No Diophantine solution or failure of Beal's conjecture is implied.
