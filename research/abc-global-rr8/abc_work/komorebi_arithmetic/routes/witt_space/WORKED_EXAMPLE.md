# The first nontrivial realization at p=3, N=2

Use R_2=Z/9, K_2=F_3. The multiplicative section is

| x in F_3 | t_2(x) in Z/9 |
| --- | --- |
| 0 | 0 |
| 1 | 1 |
| 2 | 8 |

The complete carry table, with values in F_3, is

| C_2(x,y) | y=0 | y=1 | y=2 |
| --- | --- | --- | --- |
| x=0 | 0 | 0 | 0 |
| x=1 | 0 | 1 | 0 |
| x=2 | 0 | 0 | 2 |

For example, 1+1-8=-6, so C_2(1,1)=-2=1 modulo 3.
Also 8+8-1=15, so C_2(2,2)=5=2 modulo 3. These are exact
calculations illustrating the universal proof, not a new finite test suite.

At the addition relation for x=y=1, the zero-carry diagram would require
the protected equality 1+1=8 in Z/9. It fails. In the carry diagram the
relation value is (1,1,1), whose third restriction is

    1+1-3*1 = -1 = 8 modulo 9.

Thus the relation matches t_2(2) exactly. No input value was changed;
the missing carry was retained. The multiplication relation at x=y=2
uses the pair (8,8), and 8*8=1 modulo 9, agreeing with t_2(1).

The protected obstruction cannot be removed by a different value at the
unprotected residue vertex 2. If b(0)=b(1)=0 and b(2)=z, its defects are
(db)(1,1)=-z and (db)(1,2)=z. Trying to kill C_2(1,1) forces z=1,
but then C_2(1,2)+(db)(1,2)=1. Their cyclic sum stays 1.

## Actual local elements in Teichmuller digits

At this precision Psi_2(d_0,d_1)=t_2(d_0)+3d_1 modulo 9:

| d_0 | d_1=0 | d_1=1 | d_1=2 |
| --- | --- | --- | --- |
| 0 | 0 | 3 | 6 |
| 1 | 1 | 4 | 7 |
| 2 | 8 | 2 | 5 |

These are Teichmuller digits, not ordinary positional base-three digits.
For example 1 has digits (1,0), but 1+1 has digits (2,1), not (2,0).
Formula (14) in the proof gives first digit 2 and carry C_2(1,1)=1.
The resulting value is 8+3=2 modulo 9, as required.

The finite coherent operation table and the nine possible element values
are distinct objects. The former has the one normalized multiplicative
realization described in the proof; the latter form the whole ring Z/9.
Neither statement gives a bound on the archimedean height of an integer
from its residue observations.
