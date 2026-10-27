# Terminal 161: both side phases close, and the entire middle phase enters one parameter cylinder

Status: exact finite coefficient certificates plus the inherited uniform finite-template and terminal-skeleton theorems. No new Lean compilation is claimed. The surviving cylinder is a necessary condition, not an exact singular Euler parameter.

## 1. Definitions and hypotheses

Let r=B*2^L-161, B a positive odd integer, and require that 161 is its **actual** terminal label for lambda_r(q)=3q+s2(r+q)-s2(r). The inherited terminal theorem then gives

mu_r=486-L, delta=L-487, and G_r=P_161 U_r+2^delta V_r,

with U_r reducing coefficientwise to 1 modulo 2. The previous address-one derivative theorem excludes a repeated dyadic root unless L is 639, 640, or 641. Its endpoint delta=0 is covered separately there.

The finite parameter theorem, at precision P and qcut=2P, states coefficientwise on each parity ball:

B*G_r = B*Low + High (mod 2^P).

Low and High are the q<161 and q>=161 packet sums computed at r0=2^L-161. Its hypotheses are

2^L>2(161+2P), P<=2r0-1, P<=L+1-ceil(log2(2(161+2P)+1)).

All are checked at (L,P)=(639,180),(640,224),(641,180). The generated base sums use the stronger scalar cutoff qmax=floor((P+s2(r0)+mu_r-2)/3), because all omitted base gamma coefficients vanish mod 2^P before substitution. The uniform theorem, not that scalar cutoff alone, controls remote multiplier-dependent packets.

## 2. The lower polynomial and its single root

At each of the three scales the coefficientwise lower polynomial is

V_r(X) = 2+19X+84X^2+16X^3+32X^4+64X^5 (mod128).

In particular V_r=X+2R_r, so it is a dyadic isometry, V_r' is a unit, and its unique root beta satisfies beta=90 (mod128). Only packets q=0,1,2 contribute at this precision: their coefficients after division by 2^delta are 2,43,16 modulo128; the remaining prefix packet valuations are at least7. The source A is retained exactly modulo128.

The finite-template congruence in Section1 cancels the odd B factor on the lower part. Thus the computation of this lower polynomial is uniform in every admissible B, not a representative multiplier sample.

The canonical P_161 skeleton balls are i+2^h_i Z2, with

h_i=bitlength(max(i,160-i)), d_i=160-s2(i)-s2(160-i), 0<=i<=160.

On each ball P_161' has valuation d_i, while P_161 has valuation at least d_i+h_i. The unit U_r has even derivative because U_r reduces coefficientwise to1. Therefore the P_161*U_r' term has valuation at least d_i+h_i+1>d_i, so (P_161*U_r)' has valuation exactly d_i throughout the ball. If a double root exists, derivative cancellation forces delta=d_i. If beta is outside that ball, V has valuation v2(i-beta)<h_i throughout it, so the lower value term strictly dominates the skeleton value at delta=d_i. Thus a double root must be on beta's ball, namely 90+128Z2. Its derivative valuation is d_90=153. This independently forces delta=153, hence L=640, among the three scales.

## 3. Full, uniform atlases at L=639 and641

For B=1+2T the two polynomials

f0=Low+High, f1=2Low

give B*G_r=f0+T*f1 modulo 2^180 on parity balls. Every leaf in the stored paired atlas is coefficientwise, with no unresolved leaves. The leaves form a disjoint cover of Z2. After dividing each leaf's content, its two reductions are either

[1],[0] (no root), or [a,1],[b] (one simple root for every T in Z2).

The actual coefficient error remains even after all leaf normalizations: the largest content is 158 at L=639 and 160 at L=641, both below 180. Hensel's lemma therefore transfers each leaf to the actual G_r. Odd multiplication by B preserves its roots and derivative valuations.

At L=639 the 33-leaf atlas has exactly one simple root, in 26+64Z2, with derivative valuation 152.

At L=641 the 43-leaf atlas has exactly three simple roots, in 58+128Z2,90+128Z2,122+128Z2, with derivative valuations 152,153,152 respectively.

These assertions hold for every positive odd B whose actual terminal is161. They include, without any upper bound on exponent m, B=1+2^m (m>=1), and B=1. More generally s2(B)<=2^L is a sufficient terminal condition here: s2(r)=s2(B)+L-3 makes the global minimizer cutoff less than 2^L+161; between q=161 and that cutoff the cost increment is 3(q-161)+s2(q-161)>0, and the lower prefix has larger cost than mu.

## 4. Entire L=640 phase: elimination without nonunit division

Every possible multiple root lies on x=90+128Y. At P224 let

A(Y)=Low(90+128Y)/2^160,
C(Y)=High(90+128Y)/2^160.

The coefficientwise divisions are exact. Put F_B=B*A+C. The actual normalized function agrees with F_B modulo 2^64, including its derivative with respect toY. This derivative assertion follows by differentiating the coefficientwise congruence after the ball substitution, so no additional seven-bit loss occurs.

Define

W=A*C'-C*A'.

If the actual G_r and G_r' vanish, then F_B=F_B'=0 modulo 2^64, hence W=0 modulo 2^64. The stored exact finite coefficient certificate gives:

- W(2Z)/16 = 1 (mod 2), coefficientwise;
- W(1+2Z)/16 = 1+Z (mod 2), coefficientwise.

Thus evenY is impossible. On oddY there is a unique formal root of the finite template W, and the derivative valuation is3. More specifically the normalized W(1+2Z)/16 is an isometry modulo every retained modulus. Its unique residue modulo 2^60 forces

Y = 1875189377982927951 (mod 2^61).

We do **not** identify this finite-template root with an exact singular point of the actual family. It is only a necessary congruence.

The local lower polynomial satisfies A(Y)=Y (mod 2). Therefore A is odd at every remainingY and may safely be inverted. Evaluating B=-C/A modulo 2^61 gives

B = 606767000650532091 (mod 2^61).

In particular,

B=17659 (mod 2^18), Y=79 (mod 256), x=10202 (mod32768).

There are no other multiplier phases left outside this progression. The argument uses neither sampled B nor division by a nonunit.

## 5. Composition with the inherited 917-bit recenter certificate

Let tau917 and zeta917 be the exact residues in local_parameter/recenter_1096.json, with the inherited proof in local_parameter/RECENTER_PROOF.md. That certificate applies to B=17659+2^18 T and x=10202+2^15 Z, and proves that an actual multiple root requires (T,Z)=(tau917,zeta917) modulo 2^917.

The new whole-phase theorem supplies precisely its entry hypotheses. Therefore every multiple root on any actual terminal161 wall must satisfy

L=640,
B=Bstar=17659+2^18*tau917 (mod 2^935),
x=Xstar=10202+2^15*zeta917 (mod 2^932).

The full integers and hexadecimal representations are in combined_frontier.json. Bstar has bitlength933 and is the canonical residue modulo 2^935. Consequently every admissible positive odd B<2^932 is simple at every terminal161 scale. The sharper exact interval is0<B<Bstar. This conclusion composes the new finite certificates with the previously established recenter certificate; it does not extend its precision.

An unconditional integer-family corollary follows: for every odd integer0<B<2^932 and every L>=487, the residual at r=B*2^L-161 is simple. Indeed s2(B)<=932 and s2(r)=s2(B)+L-3. The global minimizer cutoff floor((s2(r)-1)/3) is less than2^L+161. For q<161 the least cost is-1, while the cost at161 is486-L<=-1. For161<q in the cutoff the excess over the cost at161 is3(q-161)+s2(q-161)>0. At L=487 any lower ties precede161, so the largest minimizing address remains161. Thus the terminal hypothesis is automatically satisfied throughout this explicit family.

The original global Euler simplicity problem remains open at this one surviving terminal161 class, at terminal129, and at higher addresses.

## Reproduction

Run `python build_phase_certificates.py`, then `python verify_phase_certificates.py`. The vendor directory contains unchanged copies of the inherited arithmetic and atlas engines. Source hashes and exact modular coefficients are embedded in each phase file. Verification uses direct binomial substitution for each leaf and a separate Bernoulli/source implementation for the generator inputs.
