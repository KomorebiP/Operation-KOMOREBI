# Actual local families survive at all four remaining primes

This note distinguishes local solutions of the Diophantine equation from global
integer solutions, and local torsion splitting from realization of global beta.

## B60.6. Exact residue conditions at the four primes

At q in S={197,883,1373,1667}, q is inert, q=1 mod49, and phi^(q+1)=-1. Hence
phi has order prime to seven and is a 7^j power for every j. The quadratic
residue extension has degree two, prime to 49. For a rational residue unit,
being a 49th power in F_(q^2) is equivalent to being one in F_q: the map
F_q^*/F_q^{*49} -> F_(q^2)^*/F_(q^2)^{*49} is injective, by the norm and
invertibility of two modulo 49.

At fixed k=7, the full torsion condition therefore reduces to

    E=3*5^9*A/C0^35 in (F_q^*)^49.

For each C0 in F_q^*, multiplication by 3*5^9/C0^35 permutes F_q^*. Exactly
(q-1)/49 values of A pass. Also gcd(5,q-1)=1 for all four primes, so for any
unit A there is a unique B0 with B0^5=-A^3 modq; its derivative is a unit.
There is no extra equation-admissibility omission in these residue counts.

|q|All (A,C0) unit pairs|Full 7-torsion pairs|Full 49-torsion pairs|A per C0 at level49|
|---|---:|---:|---:|---:|
|197|38416|5488|784|4|
|883|777924|111132|15876|18|
|1373|1882384|268912|38416|28|
|1667|2775556|396508|56644|34|

These are complete residue-pair counts at k=7, not counts of global solutions,
representations or stable lattices. Both implementations enumerate all 5,474,280
pairs and agree on the accepted-pair hashes, not only the totals.

## B60.7. Four explicit genuine local positive families

This construction uses only the local model and split uniformization inputs.
It does not assume or realize the global finite-depth, common Kummer-vector
or opposite-endpoint hypotheses.

Take C0=1, C=q^7, and choose A=A0=(3*5^9)^(-1) modq in {1,...,q-1}:

|q|A0|B0 modq|C|
|---|---:|---:|---|
|197|148|81|197^7|
|883|228|27|883^7|
|1373|1028|497|1373^7|
|1667|1449|984|1667^7|

For each row let B be the unique element of Z_q congruent to B0 satisfying

    B^5=q^49-A0^3.

Existence and uniqueness follow from Hensel's lemma because 5B0^4 is a unit.
Then (A0,B,q^7) is primitive at q and satisfies A0^3+B^5=C^7 EXACTLY in Q_q.
The resulting Frey curve is a smooth local deformation of the actual split
nodal model. E has residue one, so the COMPLETE criterion proves full local
J^nu[49] rationality over K_v. Its node thickness is 49 and natural monodromy
content is t=1+v7(7)=2, compatible with the depth-two necessary content.

More generally any A in A0+q Z_q and C=q^7 C0 with C0 in 1+q Z_q gives the
same torsion conclusion, with the unique fifth root B near B0. These are
families, not isolated modular coincidences.

The certificate computes B modulo q^52 by quadratic Newton lifting, and the
independent implementation reproduces the SAME residue by 51 single-digit
Hensel steps. The exact root is defined by Hensel's theorem, not by claiming
a finite residue is an integer root. A and C in the table are integers;
B is a q-adic root, not asserted to be an ordinary integer or a rational number.

No common global representation, actual global beta, common global alpha,
fixed-prime data, or simultaneous global integer solution is constructed.
These local positive controls refute an attempted exclusion based ONLY on
full local 49-torsion and the three nodal period coordinates. They do not
show that additional global or endpoint constraints are satisfiable.

## B60.8. The new smoothing condition is genuinely stronger

Let g be a primitive root modulo q. Replace A0 by A0*g^7 modulo q while retaining
C=q^7, and lift B as above. Then E has residue g^7. It is a seventh power but
not a forty-ninth power. Phi passes both tests as before. Consequently this
local Frey family has full local J[7] rationality but NOT full local J[49]
rationality, under the actual period criterion.

There is one such control at every prime in S. Replacing A0 by A0*g gives a
second control failing even the seventh-power diagonal condition. Thus the
off-diagonal success by itself is insufficient, even at all four retained
positive primes. Both sorts of failure concern local torsion, not Beal.

## Impact on the current global branch

For COMPLETE H(C) subset U, n<=2 remains unchanged, and at n2 beta can still
ramify only over S. The retained common-ratio restrictions remain:

    q=197: a3/a5=6;
    q=1373 or1667: a3/a5=1;
    q=883: the previous residual rows alone impose no ratio restriction.

All actual support still has v7(v_q(C))=1 and nonzero a_phi. Now it must ALSO
satisfy E a49th power. In particular, at883 and a specified C0 there are only
18 allowed A residues rather than 882, and only one seventh of the 126 residues
that pass the natural residual torsion test. This is new arithmetic information,
not a contradiction. NO ONE of the four primes has been eliminated in Block60.
