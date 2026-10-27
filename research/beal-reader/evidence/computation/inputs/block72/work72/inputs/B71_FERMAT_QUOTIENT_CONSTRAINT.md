# B71.3. A conductor-independent fixed-seven constraint on actual A

Retain H1-H4. Normalize the global natural class as

    alpha=v*w[phi]+r[3]+[omega], v,r in F7*.

This uses the inherited ALL-DEPTH coefficient theorem, not ordinary descent of beta.
In the independent local Kummer coordinates X=[phi],H=[3], B71.1 gives

    alpha|_F = v*w*X+(r+4)H.

By B71.2 the same class is c*((3*q+5)H+2*epsilon*w*X), where q=q7(A),
epsilon=+/-1 and c in k*. Comparing the X-coefficients yields

    c=v/(2*epsilon) in F7*.

Comparing H-coefficients then gives the exact necessary equation

    2r+1 = epsilon*v*(3q+5) in F7.                  (1)

Since the sign has not been determined, its orientation-independent form is

    BOX: (2r+1)^2 = v^2*(3*q7(A)+5)^2 mod7.        (2)

In characteristic7, equality of squares is equivalent to one of the two signs,
including when both sides are zero. Conversely (2) supplies an epsilon and a
nonzero c making these TWO LOCAL extension classes equal. It is not a converse
for an actual global Frey representation, a prescribed global beta, or an integer
solution.

No bound on the conductor, the size of A,B,C, or the lattice depth is used here.
No numerical A was inferred from an auxiliary prime. A is the actual first
Diophantine coordinate, and7 does not divide A under H1.

## Counts and coefficient directions

There are42 rational unit residues A mod49, six for each value of q7(A).
For q=3, (2) forces r=3 and allows all six v values:6 normalized directions.
For any q!=3, r cannot be3; each of the other five nonzero r gives two v values:
10 normalized directions. Across all36 directions and42 A residues,396 of1512
pairs satisfy(2). These are residue/coefficient pairs, NOT representations.

## What changes for Block70's eight patterns

All eight have r=6. Then:

    u=+/-3w  => q7(A) in{0,6} => A^6 mod49 in{1,43},
    u=+/-w   => q7(A) in{1,5} => A^6 mod49 in{8,36}.

The allowed residues are

    +/-3w: 1,3,5,8,18,19,30,31,41,44,46,48;
    +/-w:  6,9,10,15,16,24,25,33,34,39,40,43.

Each of the eight patterns retains twelve A residues, giving96 augmented
(pattern,A mod49) possibilities. No coefficient/character pattern is removed.
Under the COMPLETE bounded-conductor hypothesis, q7(A) in{2,3,4} is now excluded.
The bounded classification was not proved for an arbitrary larger conductor.

This is information absent from a test that only forces finitely many beta
Frobenius values to zero. It does not contradict Block70's finite-sieve limitation:
that theorem never claimed compatibility with this actual local period extension.
