# B76.2. A nonzero lower direction forces the full second congruence subgroup

This is an elementary closed-subgroup theorem. It is not an invocation of a large-
image theorem with omitted hypotheses.

Let O=Z7[w]/(w^2-5), k=O/7, and H be a CLOSED subgroup of SL2(O). Suppose:
(1) H mod7 is the full group U(k) of upper unipotents;
(2) some h in H with h=I mod7 has nonzero (h21/7) mod7.
Put K_s=ker(SL2(O)->SL2(O/7^s)). Let V_s be the image of H intersect K_s in
K_s/K_(s+1), identified with sl2(k) by I+7^s X |-> X mod7.

This quotient identification follows by determinant expansion. It is surjective:
for a desired traceless leading matrix, choose its top-left, upper and lower
entries at precision7^s, then set the lower-right entry to(1+upper*lower)/top-left.
The top-left is a unit. This gives determinant exactly1 and the prescribed leading
matrix. Every V_s is an F7-linear subspace.

## First layer: four full field directions

V_1 is stable under Ad(U(z)) for every z in k. Take

    X=[[p,q],[b,-p]] in V_1, b!=0.

Then

    Ad(U(z))X = [[p+zb, q-2zp-z^2 b],[b,-p-zb]].          (2)

Adding the z and -z cases and subtracting2X gives -2z^2 b E12. The F7-span of the
squares in k is all k: t=((t+1)/2)^2-((t-1)/2)^2. Since2b is nonzero, V_1 contains
kE12. Subtracting the two cases in(2) gives2zb H0-4zp E12, where H0=diag(1,-1).
Removing the already available upper part gives kH0. Finally subtracting those
two parts from X gives bE21.

Thus V_1 contains kE12, kH0, and at least one nonzero lower direction bE21.
The assertion is over F7: it does not assume V_1 is a k-linear subspace.

## Second layer: all six F7 directions

For x=I+7X and y=I+7Y, irrespective of their next digits,

    x^7=I+49X mod343,
    [x,y]=I+49[X,Y] mod343.                              (3)

The power formula puts kE12 and kH0 into V_2. The bracket

    [aH0,bE21]=-2ab E21

ranges through all kE21 as a ranges through k. Therefore

    V_2=sl2(k),          dim_F7(V_2)=6.                   (4)

In particular every determinant-one last digit modulo343 occurs. Unknown higher
digits in the chosen lifts do not affect(3).

## Closedness gives the whole subgroup, not just its graded image

For each s>=2,

    (I+7^s X)^7=I+7^(s+1)X mod7^(s+2).                  (5)

All binomial error terms have sufficiently high valuation; this is a proof for
EVERY s, not an extrapolation from the sampled s<=6 checks. Inductively, V_s is
sl2(k) for every s>=2. Given any target in K_2, successively multiply elements of
H intersect K_s to correct its next digit. The partial products converge in
SL2(O), since the new errors tend to zero. Closedness of H keeps the limit in H.
Consequently

    BOX: K_2 subseteq H.                                (6)

This inference would be invalid for an arbitrary nonclosed subgroup. For the
actual Galois image closedness follows from compactness and continuity.

If V_1 already equals sl2(k), the same argument starting at s=1 gives K_1 subset H.
The stronger universal conclusion K_1 subset H is FALSE when its lower first-
layer image is only a one-dimensional F7-line; the next note gives that exact case.
