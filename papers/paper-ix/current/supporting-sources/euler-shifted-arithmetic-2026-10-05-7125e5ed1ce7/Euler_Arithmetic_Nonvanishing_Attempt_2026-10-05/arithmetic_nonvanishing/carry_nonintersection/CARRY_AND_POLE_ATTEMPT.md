# Attempted arithmetic nonintersection through finite digits

Date: 2026-10-05. Base: `Euler-coupled-stationarity-20261005`.

## Outcome

This attempt does not prove arithmetic nonvanishing. It identifies the exact first failed implication in a finite-binary-support argument and proves a further obstruction to replacing it by a global depleted parameter function: **Bernoulli depletion removes the nonunit exponential discontinuity, but the factorial packet denominators still create dense parameter poles.** The entire fixed-normalization packet family, even restricted to the surviving argument disc, cannot be interpolated analytically on an open multiplier ball while agreeing with its admissible ordinary integer members near any admissible integer parameter.

The true-terminal restriction avoids those poles by deleting explicit open neighborhoods. It does not force every ordinary admissible multiplier to leave the possible singular locus. An all-precision singular parameter obtained from a globally analytic depleted family therefore cannot simply be assumed in a digit-termination proof.

## 1. Exact carry test and the attempted last-bit contradiction

Fix an outer scale \(L\), set \(M=3\cdot2^L\), and assume the lower-wall calculation has already certified the required minimum at \(q=j\). The remaining true-terminal obligation for an odd positive multiplier \(B\) is

\[
Md+s_2(B+d)-s_2(B)>0\qquad(d\ge1).
\tag{1}
\]

Indeed write \(q=j+2^Ld+e\), \(0\le e<2^L\). The excess above the \(j\)-packet is

\[
Md+s_2(B+d)-s_2(B)+3e+s_2(e).
\]

Every new tail minimum has \(e=0\), so (1) is exact.

There is a finite digit criterion for (1). At every zero-bit position \(t\) of \(B\), put \(b_t=B\bmod2^t\). Then

\[
\boxed{s_2(b_t)\le M(2^t-b_t).}
\tag{2}
\]

Only \(t\le\operatorname{bitlength}(B)\) need be checked. To prove equivalence, compare \(B\) with any later integer \(n=B+d\). Their highest changed binary bit is a zero of \(B\) changed to one, say at position \(t\). Among such \(n\), the smallest value of \(M(n-B)+s_2(n)-s_2(B)\) occurs when every lower bit of \(n\) is zero. Its value is

\[
M(2^t-b_t)+1-s_2(b_t),
\]

which is strictly positive exactly when (2) holds. Beyond the top bit, \(b_t=B\) is fixed and the right side only increases.

The proposed last-bit contradiction stops here. Finite binary support imposes (2) at its last zero bit, but it does not reverse that inequality. For example every \(B=1+2^N\), \(N\ge1\), satisfies (1) whenever \(M\ge2\), because \(s_2(B)=2\) and

\[
Md+s_2(B+d)-s_2(B)\ge M+1-2>0.
\]

Thus arbitrarily high last bits, by themselves, remain compatible with true-terminal admissibility. The midpoint Bernoulli identity does not presently supply an identity making the last bit of a *singular* multiplier behave differently.

## 2. Heredity and precisely what a digit obstruction would require

If a finite odd prefix \(b\), \(0<b<2^h\), fails (1), then every ordinary extension \(B=b+Q2^h\) fails as well.

For a failing internal zero bit this follows immediately from (2). If the newly imposed top zero at \(h\) is the failing bit, set \(d=2^h-b\). Then

\[
\begin{aligned}
s_2(B+d)-s_2(B)
&=s_2(Q+1)-s_2(Q)-s_2(b)\\
&=1-v_2(Q+1)-s_2(b)\\
&\le1-s_2(b),
\end{aligned}
\]

so the same strict-tail inequality fails. Consequently ordinary admissibility is hereditary under binary truncation.

Define \(\mathcal E_M\) to be the closed set of odd dyadic integers all of whose positive finite binary prefixes pass (1). Then a hypothetical dyadic singular multiplier can be excluded by carries if **one of its finite prefixes fails (2)**. Conversely, if it belongs to \(\mathcal E_M\), every one of its finite truncations is an admissible ordinary multiplier. Finite support does not itself distinguish that case from an actual ordinary singular multiplier.

For terminal 161 at \(L=640\), \(M=3\cdot2^{640}\). Any multiplier with \(s_2(B)\le M\) automatically passes (1). Therefore the presently recorded hundreds of singular digits are far inside the automatic-admissibility range. Computing additional digits of comparable size cannot discriminate the carry obstruction.

No relation has been proved forcing a hypothetical singular multiplier outside \(\mathcal E_M\). That is the precise missing arithmetic implication in this route.

## 3. The excluded neighborhoods surround negative integers

For every positive odd \(d\), consider multipliers satisfying

\[
B\equiv-d\pmod{2^h},\qquad 2^h>d.
\]

Writing \(B=(Q+1)2^h-d\) gives

\[
s_2(B+d)-s_2(B)
=1-v_2(Q+1)-h+s_2(d-1).
\]

Thus all such ordinary multipliers violate (1) if

\[
\boxed{h\ge Md+s_2(d-1)+1.}
\tag{3}
\]

Every negative odd integer has an explicitly forbidden neighborhood. These neighborhoods in fact exhaust the excluded set. If (2) fails at a zero bit \(t\), put \(d=2^t-b_t\). Then \(d\) is positive and odd, and

\[
s_2(b_t)=t-s_2(d-1)>Md,
\]

so \(t\ge Md+s_2(d-1)+1\). This is exactly membership in one of the forbidden balls (3). Conversely every such ball has already been shown to fail the tail inequality.

Since negative odd integers are dense in the odd dyadic integers, \(\mathcal E_M\) has empty interior. Its complement is nevertheless small in Haar measure: conditional on the odd class, the union bound gives

\[
\operatorname{measure}(\mathbb Z_2^\times\setminus\mathcal E_M)
\le\sum_{d\ge1}2^{-Md-s_2(d-1)}\le\frac{1}{2^M-1}.
\]

This is a bound on a precisely defined arithmetic set, not a probabilistic claim about the actual singular digits.

This topology explains why a globally analytic parameter family is the wrong object to assume without proof. The admissible set can avoid dense singularities while still containing every finite prefix of a possible parameter.

## 4. The depleted Bernoulli function is itself analytic and a unit

Define

\[
D(z)=\sum_{h\ge0}2^hB_h\binom{2z}{h}.
\]

For even \(h=2n\ge2\), the falling product defining \(\binom{2z}{2n}\) contains \(n\) even linear factors. Its Gauss valuation is therefore at least \(n-v_2((2n)!)\). Since \(v_2(2^{2n}B_{2n})=2n-1\), the full summand has Gauss valuation at least

\[
n+s_2(n)-1\longrightarrow\infty.
\]

The \(h=1\) term is \(-2z\), and all odd terms after it vanish. Hence

\[
D\in\mathbb Z_2\langle z\rangle,\qquad D\equiv1\pmod2.
\tag{4}
\]

Thus the new pole obstruction does not come from any zero or discontinuity of \(D\).

At positive integers \(r\), its exact arithmetic value is

\[
D(r)=(1-2^{2r-1})\,2B_{2r}.
\]

The finite midpoint expansion terminates separately at each integer index, but the packet family uses \(D(r+q)\) for unbounded \(q\). Finite binary support of \(r\) does not terminate that packet family.

## 5. Genuine factorial poles survive depletion

For each fixed packet index \(q\), the depleted scalar is

\[
\widehat c_r(q)=
2^{5q}\frac{2r+2q-1}{2r-1}
\frac{D(r+q)}{D(r)}
\left(\prod_{h=1}^{2q}(2r+h)\right)^{-1}.
\tag{5}
\]

It is meromorphic as an individual parameter function. At \(r=-m\), \(m\ge1\), it has a genuine simple pole whenever \(q\ge m\): exactly the factor \(2r+2m\) vanishes, and every other numerator factor, including both \(D\)-values, is a unit.

Let

\[
R_{m,q}=\lim_{r\to-m}(r+m)\widehat c_r(q).
\]

For \(q<m\), this is zero. For \(q\ge m\), stripping the remaining even factorial factors gives the exact valuation

\[
\boxed{v_2(R_{m,q})=4q-v_2((m-1)!)-v_2((q-m)!).}
\tag{6}
\]

Therefore the residue series

\[
\mathcal R_m(X)=\sum_{q\ge m}R_{m,q}P_q(X)\mathscr A(X-q)
\tag{7}
\]

converges in the restricted Tate algebra. It is nonzero: at the ordinary argument \(X=m\), all terms after \(q=m\) vanish, while the \(q=m\) term is nonzero. In fact

\[
\boxed{v_2(\mathcal R_m(m))=4m+v_2(m).}
\tag{8}
\]

The residue has a stronger exact factorization. Since

\[
v_2\left(\frac{R_{m,m+h}}{R_{m,m}}\right)
=4h-v_2(h!)=3h+s_2(h),
\]

and \(P_{m+h}(X)=P_m(X)P_h(X-m)\), equation (7) gives

\[
\boxed{\mathcal R_m(X)=R_{m,m}\,P_m(X)\,U_m(X-m),
\qquad U_m\equiv1\pmod2.}
\tag{8a}
\]

Indeed the \(h=0\) summand in \(U_m\) is \(\mathscr A\), and every later scalar is divisible by 16. Thus the residue's only dyadic roots are the simple integer roots \(0,\ldots,m-1\). In particular it is nonzero at every nonnegative ordinary integer \(x\ge m\).

A fixed normalization \(2^{-\mu}\) simply subtracts \(\mu\) from these valuations.

There is a subtlety: individual-packet residues do not automatically prove that the full parameter family is meromorphic on a neighborhood, because further poles are dense. The following explicit sequence supplies the needed whole-family statement instead.

Take ordinary positive indices

\[
r_h=2^h-m>0.
\]

For each fixed \(q\), the scaled scalar \(2^h\widehat c_{r_h}(q)\) tends to \(R_{m,q}\). Moreover

\[
\begin{aligned}
v_2(2^h\widehat c_{r_h}(q))
&=h+3q+s_2(r_h+q)-s_2(r_h)\\
&\ge3q+1+s_2(m-1),
\end{aligned}
\]

because \(s_2(r_h)=h-s_2(m-1)\). This bound is uniform in \(h\), so dominated convergence in the Gauss norm proves

\[
\boxed{2^h\widehat H_{r_h}(X)\longrightarrow\mathcal R_m(X).}
\tag{9}
\]

Since the limit is nonzero, the Gauss valuation of \(\widehat H_{r_h}\) tends to minus infinity. Thus no continuous Tate-valued extension exists at \(r=-m\).

The same obstruction survives restriction to any nonempty affine argument ball, including \(X=10202+2^{15}Z\). Affine substitution by a nonzero scale is injective on the restricted algebra: translation is an automorphism, and multiplication of its Taylor coefficients by nonzero powers of the scale is injective. Hence \(\mathcal R_m(10202+2^{15}Z)\ne0\). Affine substitution is continuous, and (9) proves the corresponding blow-up on the deep chart.

## 6. Consequence in the multiplier variable

For fixed outer scale \(L\) and label \(j\), the negative multiplier \(B=-d\) corresponds to

\[
r=-m,\qquad m=d2^L+j.
\]

The ordinary positive approximants \(B_h=2^h-d\) give

\[
r_h=2^{L+h}-m.
\]

Thus every negative odd multiplier is a genuine pole obstruction for the fixed-normalization depleted packet family. Negative ordinary values occur in every nonempty parameter ball of \(B\), and also of the deep coordinate \(T\) after \(B=17659+2^{18}T\). There can be no global or open-ball analytic interpolation agreeing with all positive ordinary multipliers in the ambient family.

For sufficiently large \(h\), these particular approximants violate the true-terminal condition by (3). Therefore this does **not** contradict the finite templates on admissible actual terminal-161 members.

There is, however, a stronger local obstruction that uses only admissible ordinary multipliers.

### No local analytic family extension from the admissible members

Suppose an analytic map from an open parameter ball into the restricted algebra of the deep argument ball agrees with the fixed-normalization depleted functions for every admissible ordinary multiplier in that parameter ball. Suppose the ball contains one admissible ordinary multiplier \(B_*\).

First, it contains infinitely many admissible multipliers \(B_*+2^N\) converging to \(B_*\). Here is the exact carry argument. Put \(s=s_2(B_*)\), \(D_*=\lfloor s/M\rfloor\), and take \(2^N>B_*+D_*\). For \(1\le d\le D_*\), addition never reaches the new high bit, so the tail cost is exactly the old positive cost at \(B_*\). For \(d>D_*\), the new bit count is \(s+1\), and the universal lower bound gives cost at least \(Md-s>0\). Thus all sufficiently high sparse augmentations are admissible. They also preserve the deep multiplier progression once \(N\ge18\).

Choose a negative odd integer \(B_0=-d\) inside the proposed parameter ball and put \(m=d2^L+j\). At terminal 161 with \(L=640\), take explicitly

\[
x=m+10041.
\]

Then \(x\equiv10202\pmod{2^{15}}\), so it lies in the deep argument ball, and (8a) gives \(\mathcal R_m(x)\ne0\). For any other fixed argument ball, one can similarly choose an ordinary integer in that ball at or above \(m\).

At this fixed ordinary argument \(x\), the packet sum terminates at \(q=x\). Its dependence on the multiplier is therefore a *finite* meromorphic function, with a genuine simple pole at \(B_0\). Its residue is a nonzero scalar multiple of \(\mathcal R_m(x)\).

Evaluate the supposed analytic family at this argument \(x\). This gives an analytic scalar function on the parameter ball. It agrees with the finite meromorphic expression at every \(B_*+2^N\). Clear the explicit common denominator

\[
Q_x(r)=(2r-1)D(r)\prod_{h=1}^{2x}(2r+h).
\]

This denominator has exactly one vanishing factor at \(r=-m\). In particular the cleared finite meromorphic expression there equals the nonzero quantity \(Q_x'(-m)\mathcal R_m(x)\), up to the fixed nonzero normalization. The resulting analytic difference has infinitely many zeros accumulating at \(B_*\), so the one-variable analytic identity theorem makes it identically zero. At \(B_0\), however, the cleared analytic-family side is zero while the cleared finite meromorphic expression is nonzero because its pole residue was nonzero. This is a contradiction.

Thus **even a local analytic extension of the full depleted deep family from its admissible ordinary members is impossible on any ball containing an admissible ordinary member**. This assertion concerns the fixed-normalization family of functions in the argument variable. It does not rule out a separately constructed scalar critical-value interpolation in which additional cancellations have been proved, nor an enlarged realization with explicit singular coordinates.

### What simple residues do not yet prove about the scalar critical value

The factorization (8a) shows that every stationary point of \(\mathcal R_m\) has nonzero residue value, since all its zeros are simple. Therefore, along an ambient pole-approach sequence for which the stationary points converge, their critical values blow up after undoing the parameter scaling. This rules out a finite critical-value limit along those ambient approaches.

It does not automatically rule out a scalar analytic interpolation of the critical values on the admissible set. That set avoids a whole neighborhood of the pole, and a varying critical argument is not an ordinary integer at which the packet sum terminates. The finite meromorphic expression needed for the identity-theorem proof above is therefore missing. Reusing that proof for the scalar critical value would be invalid.

Nor does a simple parameter residue by itself exclude a double zero at a positive parameter. For example, let \(b_0,d>0\), let \(P\) be any polynomial with simple roots, and set

\[
F(B,Z)=\left(\frac1{B+d}-\frac1{b_0+d}\right)P(Z)+(Z-z_0)^2.
\]

Its residue at \(B=-d\) is exactly \(P(Z)\), but its member at the ordinary positive parameter \(B=b_0\) is \((Z-z_0)^2\). This is not an Euler counterexample. It proves that the residue theorem must be supplemented by a constraint on the actual regular part before it can give arithmetic nonvanishing.

## 7. Why extending the last bit does not contradict a hypothetical integer zero

Suppose an admissible ordinary multiplier \(B\) actually had zero critical value. The established undepletion theorem would then force its depleted critical value to be nonzero with valuation exactly \(2r-25\).

Admissible sparse high-bit augmentations of that fixed multiplier can tend to \(B\) while their actual functions tend to its depleted function. Their critical values would therefore eventually have that same finite valuation \(2r-25\), rather than tending to the zero actual critical value at \(B\). This is consistent with the proved completion boundary. It supplies no forbidden carry and no contradiction.

The first unsupported implication would be to replace this depleted limit by the actual value at the terminating binary expansion. The nonzero undepletion correction is exactly the obstruction to that replacement.

## Strongest surviving conclusion

A carry-based nonintersection proof must establish that the exact arithmetic singular data force a finite violation of (2), or obtain some different Bernoulli-unit identity proving the independent undepletion singular coordinate is not its prescribed power of two. Neither implication follows from finite binary support, midpoint termination, or the current finite templates.

The new pole calculation prevents treating an analytic depleted packet family, and a critical-value root derived from that family by an analytic implicit-function argument, as already established objects. The exact remaining arithmetic question is still the nonvanishing of the actual fixed-depth critical value, equivalently the previously isolated nonintersection with the specified undepletion coordinate. This attempt sharpens and invalidates particular routes to it; it does not close that question.
