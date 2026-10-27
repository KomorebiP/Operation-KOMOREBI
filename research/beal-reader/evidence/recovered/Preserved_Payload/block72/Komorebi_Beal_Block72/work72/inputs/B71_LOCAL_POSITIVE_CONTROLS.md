# B71.4. The new local constraint is nonempty

All eight predecessor patterns survive after allowing the necessary A residues.
The two basic types may be represented by

    u=+/-3w: A=1 (q7=0), or A=3 (q7=6);
    u=+/-w:  A=6 (q7=1), or A=9 (q7=5),

always with r=6. Set C=7. For each indicated A, and indeed for every one of the
24 distinct allowed A residues, let B be the unique7-adic fifth root of

    B^5=7^7-A^3

with its unique unit residue B0 modulo7. Fifth powering is a bijection on F7*,
and5*B0^4 is a unit, so Hensel lifting defines an EXACT primitive local triple
(A,B,7) over Q7. Varying A in its fixed residue class modulo49 gives local
families with the same Fermat quotient and the same comparison alternatives.

The executable certificate records B modulo7^18, reconstructed by Newton lifting
and independently by17 one-digit Hensel steps. A finite residue is not asserted
to be an ordinary integer root. B is a7-adic number, not an asserted rational
or integer solution. These families satisfy the stated local equation and period
comparison alternative; they do not realize the global conductor, normalized
alpha at every place, opposite endpoint, fixed-prime data elsewhere, or a common
integer solution.

At seven, F=Q7(sqrt5) does NOT contain mu7. Full natural J[7] rationality is neither
claimed nor possible. The object computed is a Kummer extension class, not a
trivial local representation. The new local natural extension is nonzero because
its X coefficient is nonzero.

## Necessary negative controls

1. Principal unit8 has nonzero seventh-power class. The residue-characteristic7
   argument needs the precise error depth1+7^(7c)O, not arbitrary1+7O.
2. S=[[2,1],[1,-2]] has S^2=5I but is NOT the required commuting action. The
   formal square relation alone is not the missing comparison.
3. The scale c between the marked local extension and globally normalized alpha
   need not be1. For A=1,r=6,v=3, take epsilon=-1 and c=2. Both coordinates match.
4. The orientation sign cannot be fixed from an unrelated prime. The square form
   is retained until the actual embedding is determined.
5. None of the eight patterns is eliminated. A false zero-survivor claim is
   explicitly rejected by the separate arithmetic checker.

Higher depth and unrestricted conductor are not eliminated. This block supplies
one local integral comparison, not a global lattice/period realization theorem.
