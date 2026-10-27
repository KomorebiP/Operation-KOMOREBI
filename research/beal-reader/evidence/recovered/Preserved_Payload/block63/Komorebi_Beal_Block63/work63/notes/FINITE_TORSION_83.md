# B63.1–B63.2. No good Frey reduction at83 has all natural7-torsion rational

## Complete residue coverage

83 is inert in K=Q(sqrt5), and the local residue field has size Q=6889.
The rational seventh-power map on F83^* is bijective, since gcd(7,82)=1.
Thus every good integer solution supplies a pair (a,b) with a^3+b^5 !=0 mod83.
There are6806 such pairs. All are checked for smoothness independently.

For each pair count the COMPLETE smooth projective curve over F83 and F83^2,
including its two untwisted points at infinity. If these counts are N1,N2, put
s=84-N1 and c=(s^2-83^2-1+N2)/2. Its rational Frobenius polynomial is
T^4-sT^3+cT^2-83sT+83^2. The actual delta has norm45 in F83 and is nonsquare
in F83^2, so square the rational Frobenius roots and then negate them.
Milne AV III11.1 and II1.1 give the trace/count and finite-Jacobian-order formulas.
The independent implementation recomputes the power sums by Newton identities.

Full rational geometric J[7] has7^4 points. Consequently2401 must divide the
finite Jacobian order. This filter leaves EXACTLY82 pairs, one orbit:

    (a,b)=(t^5,30*t^3), t in F83^*.

The coordinate transformation x -> t*x, z -> t^3*z identifies these curves
with the representative (1,30), including the same fixed twist. No change of
Tate lattice or merely isogenous variety is substituted. The map on parameters
has82 distinct members. The independent counter enumerates all6806 pairs
without orbit reduction and verifies the entire surviving set is this orbit.

For (1,30) the untwisted counts are N1=84,N2=7146. The rational polynomial is

    T^4+128T^2+6889.

The actual polynomial over F6889 is

    (T^2-128T+6889)^2.

Its group order is

    6762^2=45,724,644=7^4 * 19044, with gcd(19044,7)=1.

The order test ALONE does not exclude this orbit. It is a retained positive
control against substituting cardinality divisibility for full rational torsion.

## Exact group-exponent certificate on the exceptional orbit

Work in F83[phi]/(phi^2-phi-1). For compact data, encode a+b*phi by a+83*b,
with0<=a,b<83. This is the BASE residue field, not the coefficient field k.
The untwisted polynomial for(1,30) is x^6+51x^3+12x+18 and has rational root5.
With x=5+1/t and z=y/t^3 the TWISTED smooth projective curve has an odd model

    y^2 = sum_(i=0)^5 f_i t^i,
    (f_0,...,f_5)=(6649,6329,3126,5529,3446,4166).

Here delta=6649=9+80phi. Smoothness is checked. The odd model has its single
rational point at infinity. The point P=(phi,39+50phi) is rational. Write
D=[P-infinity], in Mumford representation

    D=([6806,1],[4189]).

The coefficient lists are in ascending powers of t. Set E=[19044]D. Exact
reduced-divisor arithmetic gives

    E    = ([4883,1329,1],[2781,5401]),
    [7]E = ([446,4060,1],[5496,3078]),
    [49]E= ([1],[0]).

The representation for[7]E is nonidentity. Uniqueness of the reduced divisor
representative for an odd-degree model therefore makes E an element of exact
order49, not just a nonzero formal polynomial. The77-operation addition
transcript is in verification/jacobian83.json. Every input and output obeys
u monic, deg(v)<deg(u)<=2 and u divides v^2-f.

The primary uses Cantor three-polynomial extended-gcd composition and reduction.
The independent implementation uses F83[sqrt5], polynomial CRT for coprime
composition, Hensel interpolation for doubling, and a different scalar ladder.
Its polynomial inverses are obtained by Gaussian elimination. It independently
replays every primary operation and recomputes E,[7]E,[49]E. Unsupported
nongeneric shared-point compositions are explicit failures; none occurs in
this certificate. It also verifies all6888 field inverses, the6634 odd-curve
points and seven associativity controls. These controls are not a substitute
for the divisor algorithm theorem, audited in Galbraith chapter10.

## Group-theoretic conclusion

Let G be the finite Jacobian group. Its7-primary subgroup has order7^4.
If all geometric J[7] were rational, G[7] would also have order7^4. Hence the
whole7-primary subgroup would equal G[7] and be killed by7. The exhibited
order49 class contradicts that. Thus the exceptional orbit does not have
full rational7-torsion either. This, with complete finite coverage above,
proves the claimed finite assertion. No full group decomposition is asserted.

This is an exact computation for a finite family, with a proof of why that
finite assertion applies to every good reduction at83. It does not validate
the upstream assertion that this is the actual Frey model of every retained
integer solution; that remains an explicit input.
