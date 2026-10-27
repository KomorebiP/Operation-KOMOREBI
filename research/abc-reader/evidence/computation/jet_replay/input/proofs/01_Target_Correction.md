# The correct ABC defect and a counterexample to the previous target

Throughout, a,b,c are positive integers, a+b=c, gcd(a,b)=1.
Write R=rad(abc), R_u=rad(u), M_u=u/R_u and Q=abc/R.
All three prime supports are pairwise disjoint.

## 1. Exact normalization

The identities are

\[
\frac{Q}{ab}=\frac cR=\frac{M_c}{R_aR_b}.
\]

Consequently ABC is equivalent to either of the following all-epsilon assertions:

\[
Q\le K_\varepsilon\,ab\,R^\varepsilon,
\qquad
M_c\le K_\varepsilon R_aR_bR^\varepsilon.
\]

It is NOT equivalent to Q=R^{o(1)}. That latter statement is false.
The omitted factor ab is load-bearing, not a harmless normalization.
The output-sector formulation is already present in the predecessor ABC papers.

## 2. An unconditional counterexample family

Take

\[
a=1,\qquad b=2^k,\qquad c=2^k+1.
\]

These triples are primitive. Since c is odd,

\[
R=2\operatorname{rad}(c)\le 2c\le3\cdot2^k,
\qquad
Q=2^{k-1}\frac{c}{\operatorname{rad}(c)}\ge2^{k-1}.
\]

For every fixed 0<=eta<1 and A>=0,

\[
\frac{Q}{R^\eta(\log(3c))^A}
\ge \frac{2^{(1-\eta)k-1}}{3^\eta(\log(3(2^k+1)))^A}
\longrightarrow\infty.
\]

Thus no constant K can make Q <= K R^eta (log(3c))^A uniform in the triple.
This refutes the earlier proposed sublinear-cost theorem on its own stated target,
without any assumption about ABC.

## 3. A stronger necessary cost lower bound

Suppose for a fixed positive contact multiplier s there are B>=0, A>=0, C>0 such that

\[
Q^s\le C R^B(\log(3c))^A
\]

for every primitive triple. Then necessarily B>=2s.

Proof. For every fixed integer d>=2, use

\[
a=t^d,\quad b=(t+1)^d,\quad c=t^d+(t+1)^d.
\]

The triple is primitive, and

\[
R\le t(t+1)c,\qquad Q\ge[t(t+1)]^{d-1}.
\]

Taking logarithms, dividing by log(t), and sending t to infinity gives

\[
2s(d-1)\le B(d+2).
\]

This holds for every d. Letting d grow gives B>=2s.
In particular B/s -> 0 is impossible for the previous unbalanced-Q target.

## 4. Retraction boundary

Retract the assertion that a small global comparison cost for Q alone was a
credible sufficient theorem differing from ABC only by bookkeeping. It was an
incorrectly normalized, strictly stronger and false target.
Retain the local jet identities. They do not establish the discarded global claim.
