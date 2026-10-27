# What the prescribed Bernoulli structure now proves

Checkpoint and assessment: `Euler-Bernoulli-structure-20261005`, 2026-10-05.
The immutable parent is identified in [README.md](README.md). There is no
Git revision or executable research ledger for this workspace; file hashes,
computation manifests, and the final archive identify the evidence instead.

## Outcome against the original target

The target was not proved and no actual counterexample was found. In the
focused admitted family

\[
r=(17659+2^{18}T)2^{640}-161,\qquad T\in\mathbb Z_{\ge0},
\]

with true terminal 161, the remaining assertion is still

\[
\Phi_r(2^{2r-25})\ne0.
\]

The inherited exact Morse reduction makes this equivalent to exclusion of
a double zero on the specified quadratic chart. Proving this family would
still leave the higher-address obligations of universal residual simplicity.
This checkpoint deliberately preserves that distinction.

## New structural theorems

Define

\[
D(z)=\sum_{h\ge0}2^hB_h\binom{2z}{h},\quad
D(n)=(2-4^n)B_{2n}\quad(n\ge0),\quad D(0)=1.
\]

For every dyadic starting point \(x\), nonzero dyadic step \(q\), and
matrix size \(m\ge1\), the reviewed proof establishes

\[
v_2\det[D(x+(i+j)q)]_{0\le i,j<m}
=m(m-1)(2+v_2q)+4\sum_{k<m}v_2(k!).
\]

The mechanism is a normalized Bernoulli orthogonal recurrence, its bounded
dyadic power operator, and a unique odd exterior coordinate after factorial
normalization. It gives exact nonvanishing, beyond a finite table.

For **actual undepleted moments**, the unit-step determinant
\(\det[2B_{2(r+i+j)}]\) has the same valuation whenever

\[
2r-1>4(m-1)+4v_2((m-1)!).
\]

This transfer is unit-step only. The all-step depleted theorem must not be
silently promoted to an all-step undepleted assertion.

The same lattice yields a sharp norm statement. For \(L_x(U^n)=D(x+n)\),
every nonzero polynomial in \(\mathbb Q_2[U]\) of degree at most three has nonzero norm
\(L_x(p^2)\), but a nonzero degree-four isotropic polynomial exists for
every \(x\in\mathbb Z_2\). The corresponding actual moment statements hold
for \(r\ge10\) and \(r\ge16\), respectively. Hence nonsingular Hankel
matrices do not imply that every nonzero polynomial has nonzero norm.

## The exact bridge, and the failed square argument

Up to its fixed nonzero normalization, the actual Euler residual is the
exact linear pairing \(L_r(W_r(x,U))\).
Its derivative is a second linear pairing. No identity has converted these
two vanishings into a controlled Gram determinant or a low-degree norm.

For the literal normalized kernel \(\Xi\), uniformly at every point of
the actual terminal-161 chart, the new proof gives

\[
\Xi(U)\equiv1+U\pmod2,\qquad
\Xi(1+8V)/4\equiv1+2V\pmod4.
\]

In particular \(\Xi(9)/\Xi(1)\equiv3\pmod4\). This excludes one constant
times squares even at these two odd-square arguments. It closes that literal
bridge. Different weights or other determinant identities remain separate,
unproved possibilities; no such representation is assumed.

## Actual carry-adapted Padé approximation

Keep packets 0 through 160 exactly and start the rational tail model at
the actual carry reset \(M=r+161=B2^{640}\), with \(B\) odd. For
\(a_n=4^nB_{2n}/(2n)!\), the normalized actual moments satisfy

\[
t_0=1,\qquad v_2(t_j)=s_2(j)\quad(0<j<2^{640}),\qquad
t_j=a_{M+j}/a_M.
\]

After one factor of two is removed, their parity is exactly the indicator
of powers of two. An even/odd block recursion proves the relevant binary
Hankel determinants are units. Consequently every actual rank
\(d\le2^{639}\) has defining determinant valuation \(d-1\), integral
Padé denominator coefficients, and last denominator coefficient valuation
one. The first omitted moment error has valuation one when
\(d<2^{639}\). These statements are proofs over the full stated range.

For ranks 2 through 10, reinserting the complete source and derivative gives
the uniform, exact critical-value errors

| Rank | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Error valuation | -1 | 7 | 14 | 24 | 31 | 39 | 46 | 55 | 62 |

The derivative estimate controls the motion of the critical point; the
table is not merely a comparison at a frozen center. For the already fixed
index \(T=718787533\), rank six has model critical valuation 30 and error
valuation 31, providing a strict noncancellation certificate. Rank three
similarly certifies \(T=0\), with value valuation zero and error seven.

These recover known fixed-index nonvanishing by a newly justified mechanism.
They do not settle all indices. At the previously fixed index with actual
critical valuation 91, all ranks in this table have model valuation equal
to their error valuation. No new multiplier digits were searched.

An exact zero would be compatible with this equality at every rank. Thus
the all-rank determinant theorem removes a denominator/convergence obstacle,
but does not provide the missing critical-value separation.

## A second safe approximation, and the height boundary

Truncating the shifted Bernoulli Jacobi matrix to dimension \(m\) gives
unit model moments matching the first \(2m\) moments of
\(d_q=D(r+q)/D(r)\) and satisfying, for every later index as well,

\[
v_2(d_q-d_q^{[m]})\ge4m+4v_2(m!).
\]

The bound is exact at \(q=2m\): the only omitted shortest walk ascends to
the boundary and returns. With factorial and source factors retained, this
gives complete depleted stationary-value precision, provided \(L\ge9\),

\[
L=8m-4s_2(m)-178.
\]

A sufficient route to actual nonvanishing would be a model critical value
of valuation below \(\min(L,2r-25)\). No such inequality uniform in ordinary
\(r\) is proved. Uniform approximation alone permits an exactly zero limit.

The orthogonal conditioning acts in the moment variable \(U\); it does not
lower the approximation degree in the critical coordinate \(Z\). The
previous direct rational-height estimate still has a quadratic precision
term. Even the actual unit moment \(D(r)\) has rational height exceeding
\(2^{2r}\) for \(r\ge40\). Good dyadic conditioning is not a small-height
theorem.

## Recurrence route and review boundary

The Bernoulli Riccati recurrence allows only coefficient scaling among its
one-parameter normalized solutions. The computed nonzero transverse jets
do not exclude zero at the prescribed scale. The independently rebuilt
adjacent-cutoff identity gives a logarithmic mismatch of valuation
\(25+v_2\Phi_r\), so a bound on that mismatch is the original obligation
again, without a new arithmetic estimate.

Independent reviews are linked in [ROUTE_INDEX.md](ROUTE_INDEX.md). They
check the new proofs, exact normalization, complete tails, derivative
losses, and current computation revisions. Inherited chart and packet
theorems remain explicitly identified dependencies. No Lean compilation,
universal simplicity claim, or global novelty claim is made.
