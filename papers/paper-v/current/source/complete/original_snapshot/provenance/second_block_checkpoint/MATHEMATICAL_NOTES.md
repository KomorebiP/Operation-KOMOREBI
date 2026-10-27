# Mathematical derivations for Paper V, second block

Author: Komorebi P.

These are ordinary mathematical arguments underlying the new source candidates. They are not reports of successful Lean compilation. The Lean statements are scoped in `THEOREM_LEDGER.md`.

## 1. Signed coordinates and delay

Let N be a positive integer. For every integer j, Euclidean division gives unique integers q,r with

\[
j=Nq+r,\qquad 0\le r<N.
\]

Consequently j maps bijectively to `(r,q)` in `{0,...,N-1} x Z`. Define

\[
(A_Nx)_r[q]=x[Nq+r],\qquad
(S_Nc)[j]=c_{j\bmod N}[\lfloor j/N\rfloor].
\]

The division identities immediately give `S_N A_N x=x` and `A_N S_N c=c`. No norm or convergence hypothesis is used in these pointwise equalities.

For an original-sample delay `(D_d x)[j]=x[j-d]`, write `r-d=N b+s` with `0<=s<N`. Then

\[
(A_ND_dx)_r[q]=x[Nq+r-d]=x[N(q+b)+s]=(A_Nx)_s[q+b].
\]

For `d=N a`, this reduces to input phase r at channel index `q-a`. Thus an a-step channel delay corresponds to an N*a-step original-sample delay. For N=2 and d=1, the rows are `c_1[q-1]` and `c_0[q]`.

When `N|M`, reduction of `(j mod M)` modulo N equals `j mod N`. The unique fine residue containing j belongs to exactly one coarse residue. Summing its fine masks within that fiber therefore reproduces the coarse mask, pointwise.

## 2. Exact finite-support FIR transfer

Let h have finite support in Z. For an arbitrary input x and a fixed output phase k,

\[
y_k[n]=\sum_{t\in\operatorname{supp}h}h[t]x[Nn+k-t].
\]

For each tap t, choose the unique `s,m` satisfying

\[
s=(k-t)\bmod N,\quad
m=-\left\lfloor\frac{k-t}{N}\right\rfloor,\quad
t=Nm+k-s.
\]

The reverse map is the displayed formula for t, so this is a bijection, not an approximation or an assumption about filter coefficients. Also,

\[
Nn+k-t=N(n-m)+s.
\]

Let `M_{k,s}` be the finite set of m for which `Nm+k-s` belongs to the support of h. Reindex the original finite sum and partition by s:

\[
y_k[n]
=\sum_{s=0}^{N-1}\sum_{m\in M_{k,s}}
 h[Nm+k-s]x_s[n-m].
\]

With `h_{k,s}[m]=h[Nm+k-s]`, this is the paper's literal time-domain transfer law. Terms outside `M_{k,s}` are zero, so an all-integer summation notation denotes the same finite contribution. Neither causal taps nor nonnegative time indices are required.

This argument does not create a bilateral z-transform for every x. A transform statement must separately specify its analytic or formal meaning.

## 3. Finite trees and exact synthesis

A recursive cut of a finite rooted tree either stops at the root or, at an internal node, chooses one recursive cut in every child subtree. Internal nodes may have any positive finite number of children.

Suppose packet values take values in an additive commutative monoid and every internal node satisfies

\[
p_v=\sum_{w\text{ child of }v}p_w.
\]

Induction on a cut proves that its selected values sum to the root value. Stopping is immediate. In the split case, replace each child's cut sum by its child-root value and apply local conservation. The same argument applies to an additive space of operators; identifying the root operator with the identity then gives synthesis.

Every such recursive cut meets a terminal path exactly once: stopping meets the root, while splitting reduces to the path in its unique chosen child. The Lean source establishes this direction for typed paths.

For the converse in ordinary mathematics, take a node set meeting every terminal path exactly once. If it contains the root, it can contain no other node, because every node lies on a terminal path. Otherwise, restrict the set to each child subtree. Each restriction meets every terminal path in that subtree exactly once. Induction gives a child cut in every subtree. This is the missing reverse set-valued bridge that must still be encoded in Lean. The finite Python census tests both definitions independently, but is not a substitute for that encoding.

The cut set is finite: a leaf has one cut and an internal node has one stopping choice plus a finite product of child-cut sets. Hence every real-valued objective on it attains a minimum, even when the objective is not additive.

## 4. Additive optimality and exact envelopes

For an additive node cost c, define

\[
V(v)=\begin{cases}
c_v,&v\text{ a leaf},\\
\min\{c_v,\sum_wV(w)\},&v\text{ internal}.
\end{cases}
\]

Any cut either stops, costing `c_v`, or splits, costing at least the sum of child minima. Choosing the minimizing alternative and recursively optimal child cuts attains V(v). Choose stop when the alternatives tie. This proves global optimality by induction, not by enumerating all cuts.

For per-node error bounds e, define

\[
E(v)=\begin{cases}
e_v,&v\text{ a leaf},\\
\max\{e_v,\sum_wE(w)\},&v\text{ internal}.
\end{cases}
\]

The same stop/split induction proves the stronger identity

\[
E(v)=\max_{L\text{ a cut below }v}\sum_{a\in L}e_a.
\]

The maximum is attained: choose stop when its weight is larger, otherwise split into child maximizers. Thus the envelope is the exact maximum cut weight, not merely an upper bound.

If `|d_a-c_a|<=e_a`, the triangle inequality bounds every cut's objective change by E(root). Evaluate this bound at a minimizer for c and at a minimizer for d to obtain

\[
|V_d(\mathrm{root})-V_c(\mathrm{root})|\le E(\mathrm{root}).
\]

If L* is the unique old optimum and every competitor has old excess at least gamma, then a competitor's new excess is at least `gamma-2E(root)`. Therefore `gamma>2E(root)` preserves the unique selected cut.

The inequality must be strict. On a unary tree, let the old root cost be 2 and the child cost be 0. Change them to `2-epsilon` and `epsilon`. The old choice is the child. At epsilon=1 the costs tie, and stop-on-ties chooses the root. Here the old gap is 2 and the envelope is 1. Equality in the gap test does not guarantee an unchanged selector.

A singleton tree has no competitor at all. Its selector is unchanged under every objective modification. Do not define its real-valued gap as a minimum over an empty set.

## 5. Flat lifting, Haar, and matrix identification

For a flat signal of length 2n, the bijection `j -> (j div 2,j mod 2)` identifies its coordinates with n pairs, including the empty case n=0.

For a pair `(e,o)`, lifting gives

\[
d=o-e,\qquad s=e+d/2.
\]

The inverse gives `e=s-d/2` and `o=d+e`, establishing both inverse laws coordinatewise and therefore on the flat signal.

The normalized real Haar pair map is

\[
H(e,o)=\left(\frac{e+o}{\sqrt2},\frac{e-o}{\sqrt2}\right).
\]

Since `(sqrt(2))^2=2`, direct substitution gives `H(H(e,o))=(e,o)`, and

\[
\left(\frac{e+o}{\sqrt2}\right)^2+
\left(\frac{e-o}{\sqrt2}\right)^2=e^2+o^2.
\]

Summation gives energy equality for finitely many pairs. The test implementation represents each real value in Q(sqrt(2)) by its two rational coefficients, so these identities are checked without numerical tolerance. This does not prove the infinite Hilbert-space extension.

Finally, if two finite matrices M,D act equally on every vector, apply them to the j-th standard basis vector. The i-th output is the `(i,j)` matrix entry, so all entries agree. Taking `M=R*E` gives the abstract matrix-action reconstruction criterion. Connecting the filter-bank operators to these matrices remains a separate formal obligation.
