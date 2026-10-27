# AVOC Formal v0.13.0 — dependency-safe research scheduling

This block connects a fixed prerequisite structure to admissible forward research work. It does not identify a legal plan with proof success.

## 1. Completed task states

Let P be a finite partial order. Write y < x when y is a strict prerequisite of x.

A finite completed set K is an ideal when

\[
x\in K,\quad y\le x\quad\Longrightarrow\quad y\in K.
\]

Define

\[
\operatorname{Ready}(K,x)\iff x\notin K\ \land\ \forall y<x,\ y\in K,
\qquad
\partial K=\{x:\operatorname{Ready}(K,x)\}.
\]

For a fresh x and an ideal K,

\[
\operatorname{Ready}(K,x)\iff K\cup\{x\}\text{ is an ideal}.
\]

This says exactly which one-task transitions preserve prerequisite closure.

## 2. Parallel batches

If two ready tasks x,y satisfy x <= y, then x = y. Otherwise y's readiness would require x already to be complete, contradicting x's freshness. Thus the frontier is an antichain.

More strongly, for an ideal K,

\[
\boxed{
B\subseteq\partial K
\iff
K\cap B=\varnothing\ \land\ B\text{ is an antichain}\ \land\ K\cup B\text{ is an ideal}.
}
\]

The closure condition cannot be dropped: a singleton terminal task is an antichain even if all its prerequisites are missing.

A ready batch has no internally required prerequisite edges. Its tasks may be serialized in any duplicate-free order, and completing one member does not invalidate the readiness of the others.

\[
|K\cup B|=|K|+|B|.
\]

## 3. Complete schedules

Define sequential legality recursively:

\[
\operatorname{Legal}(K,[]) = \top,
\]

\[
\operatorname{Legal}(K,x::xs)
\iff
\operatorname{Ready}(K,x)\land\operatorname{Legal}(K\cup\{x\},xs).
\]

An independent characterization says a list is legal exactly when it has no repeated tasks, avoids K, finishes in an ideal, and never places a strict prerequisite after its dependent.

Consequently, lists containing every task exactly once are legal from the empty set iff they are linear extensions of the partial order.

Every nonempty finite residual has a minimal remaining task. Removing a ready task strictly decreases residual cardinality, proving existence of a structural completion from every ideal. Any complete legal list xs satisfies

\[
|xs|=|P|-|K|.
\]

The word *structural* is essential: this theorem supplies a dependency-respecting order, not proofs of the task propositions.

## 4. Parallelism and time bounds

Define width(P) as the maximum cardinality of a finite antichain. For every ready batch,

\[
|B|\le |\partial K|\le\operatorname{width}(P).
\]

An injective assignment of active workers to distinct ready tasks satisfies the same bounds. This is not an upper bound on agents cooperating on one task or on independent verifier activity.

For a unit-time schedule tau with x < y implying tau(x) < tau(y), tasks before any time t form an ideal; tasks in slot t belong to its frontier.

If every task finishes in T slots, every dependency chain C satisfies

\[
|C|\le T.
\]

If p workers each execute at most one task per slot, an injective task-to-(slot,worker) map gives

\[
|P|\le Tp.
\]

Together these are work and critical-path lower bounds, not a claimed optimal scheduler.

## 5. Certificate-gated admission

Let claim : P -> Prop. Define

\[
\operatorname{Certified}(K)\iff\forall x\in K,\operatorname{claim}(x),
\]

and a local proof rule for x by

\[
\left(\forall y<x,\operatorname{claim}(y)\right)\Rightarrow\operatorname{claim}(x).
\]

A ready task plus certified prerequisites and its local proof rule yields a proof of claim(x). Both ideal closure and certified truth survive a checked insertion or checked ready batch.

A legal schedule equipped with actual local proof rules preserves certification throughout. In contrast, a one-task plan can be ready while its assigned proposition is False. Therefore scheduling metadata never supplies the missing certificate.

## 6. Diamond witness

Use the product order on Fin(2) x Fin(2):

\[
r=(0,0),\quad l=(0,1),\quad q=(1,0),\quad t=(1,1).
\]

After completing r,

\[
\partial\{r\}=\{l,q\},\qquad\operatorname{width}(P)=2.
\]

Both [r,l,q,t] and [r,q,l,t] are legal. The ordering [t,r,l,q] is not. A three-task total chain requires at least three unit-time rounds regardless of spare worker count.

The executable Python example emits the structural batches [root], [left,right], [conclusion] with two workers. It does not mark them as proved.

## 7. Integration boundary and next theorem

This block supplies the admissible forward-action set and certificate-preserving transitions. A later controller can rank ready nodes by Bayesian value, cost, or downstream benefit, while separate actions perform verification, falsification, or infrastructure work. We have not yet proved optimality for that joint controller.

The inherited context-compression and Q-signature theorems remain unchanged. Neither DAG width nor structural legality estimates real proof-search success probabilities.
