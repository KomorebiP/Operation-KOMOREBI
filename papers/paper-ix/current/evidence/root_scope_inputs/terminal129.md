# Terminal 129: the entire critical scale has two necessary multiplier classes

This certificate closes every multiplier phase outside two explicit residue classes. It does not prove nonvanishing inside those classes or identify an exact singular Euler parameter. It uses the inherited finite-template, skeleton, and address-one derivative theorems, with fresh exact coefficient calculations. No new Lean compilation is claimed.

Let r=B*2^L-129 for positive odd B, with actual terminal label129. The preceding structural theorem proves that a multiple dyadic root can occur only at L=515. At that scale mu=-126 and delta=123.

## Uniform finite model and root localization

At precision P=224, the inherited finite-template theorem gives on each parity ball

B*G_r = B*Low+High (mod2^224),

where Low and High are the exact base packet sums at r0=2^515-129, split at q=129. The arithmetic program checks the complete scalar cutoff for the base model and the uniform parity cutoff q<448. Its precision budget is

516-ceil(log2(2(129+448)+1))=505>224.

The normalized lower polynomial is

V_r(X)=8+219X+236X^2+192X^3+64X^4 (mod256).

It reduces coefficientwise toX modulo2, so V_r is a global dyadic isometry with unique root beta=104 (mod256).

For the original129-skeleton, i=104 has radius exponent7 and derivative valuation

d_104=128-s2(104)-s2(24)=123.

Derivative cancellation at a multiple root forces delta=d_i. If beta is outside the corresponding skeleton ball, the lower value term has valuation strictly less than the skeleton term, so it cannot be a root. Thus every multiple root lies on x=104+128Y. The usual skeleton derivative equality holds because the P_129*U_r' term has valuation strictly greater than the P_129'*U_r term.

## Parameter elimination, with the nonunit loss included

Define, coefficientwise modulo2^94,

A(Y)=Low(104+128Y)/2^130,
C(Y)=High(104+128Y)/2^130,
W(Y)=A(Y)C'(Y)-C(Y)A'(Y).

The divisions are integral and verified coefficientwise. Since the actual normalized G agrees with B*A+C modulo2^94, an actual repeated root forces W(Y)=0 modulo2^94.

The exact W atlas partitions all of Z2 into four disjoint balls:

| Y ball | W certificate |
| --- | --- |
| 0+4Z2 | v2(W)=3 |
| 1+2Z2 | v2(W)=1 |
| 2+8Z2 | after dividing by2^6, affine reduction1+Z |
| 6+8Z2 | after dividing by2^6, affine reductionZ |

On each of the last two balls the normalized function is an isometry. Hence W=0 modulo2^94 forces one residue modulo2^91. These are

Y1=2396339231341800909354051642,
Y2=1709272731386384844146492182.

The factor2^6 is the local content and the substitution has radius exponent3, so the net derivative valuation loss is3: 94-6+3=91 bits inY.

A and C both have valuation exactly1 throughout each of these two balls. This is checked coefficientwise after the substitutionsY=2+8Z andY=6+8Z. They cannot be inverted before stripping that factor2. Evaluating at the forced Y residue modulo2^91 and dividing both A and C by2 gives the necessary parameter equation modulo2^90:

B=-(C/2)*(A/2)^(-1) (mod2^90).

Thus every actual multiple root requires exactly one of the following pairs:

| B modulo2^90 | Y modulo2^91 | Earlier cylinder |
| --- | --- | --- |
| 753164624808627572229541837 | 2396339231341800909354051642 | B=4045 mod65536, x=7528 mod32768 |
| 621741425015278698550505213 | 1709272731386384844146492182 | B=44797 mod65536, x=2920 mod32768 |

The full necessary x congruence is x=104+128Y_i modulo2^98. Only necessary finite congruences are asserted. A root of the finite eliminant is not promoted to an exact singular member of the undepleted Euler family.

## Exclusion consequence

Both canonical B residues exceed

2^89=618970019642690137449562112.

Therefore every admissible positive odd B<2^89 gives a simple Euler residual on every actual terminal129 scale. The sharper common bound is B<621741425015278698550505213. In addition, all larger admissible multipliers outside the two classes modulo2^90 are excluded from singularity.

The explicit range also has an unconditional formulation: for every odd integer0<B<2^89 and every L>=392, all dyadic roots at r=B*2^L-129 are simple. Here s2(B)<=89 and s2(r)=s2(B)+L-2. Thus the global minimizer cutoff floor((s2(r)-1)/3) is less than2^L+129. The least lower-prefix cost is-3, while the cost at129 is389-L<=-3. Every later candidate q in the cutoff has positive excess3(q-129)+s2(q-129). At the boundary L=392, all lower ties precede129. Therefore129 is the true terminal throughout this integer family.

The historical v24 certificate checked two fixed original representatives, B=4045 and44797. The new assertion is universal over each excluded parameter class, by the coefficientwise template theorem. It does not rely on testing more representatives.

## Reproduction and scope

Run `python build_phase129.py`, then `python verify_phase129.py`. These use the sibling `critical_phases` package for inherited engines. The independent verifier checks all source and gamma coefficients with a separate Bernoulli/source implementation, the disjoint exhaustive cover with exact rational masses, direct-binomial leaf reductions, and the unit reductions after division by2. It separately lifts the two critical residues and computes the two parameter residues.
