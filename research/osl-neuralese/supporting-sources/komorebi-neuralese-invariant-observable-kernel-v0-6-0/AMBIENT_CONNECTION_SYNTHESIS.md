# Ambient space and the flat-connection problem

**Author:** Komorebi P.

## The geometric diagnosis

The v0.4 result separated two failure modes that are easy to conflate.
Hard-polar operators constrain every recurrent update to (O(12)), so hidden
norms remain bounded. They do not force two semantically equivalent paths to
arrive at the same latent transformation. Radial stability is a metric
property; path independence is a connection property.

Write the total latent space as a bundle

\[
K \hookrightarrow H \xrightarrow{\pi} S,
\]

where (S) is the behaviorally identified semantic base and
(K=\ker\pi) is a vertical ambient fiber. A recurrent operator is a lift on
(H) of an action on (S). For two words with the same exact visible action,

\[
\tau(u)=\tau(v),
\qquad
H(u,v)=\rho(v)^{-1}\rho(u)
\]

is their latent holonomy.

There are then two legitimate notions of closure:

1. Full flatness requires (H(u,v)=I_H).
2. Quotient flatness requires only that (H(u,v)) act trivially after
   projection to every relevant downstream consequence.

Full flatness is stronger and easier to certify, but it may erase useful
vertical computation. Quotient flatness allows nontrivial ambient holonomy as
gauge motion, provided that motion cannot unpredictably leak back into the
semantic base.

## Why the first packet loss failed

The first finite packet objective tested a learned observer only over short
suffixes. Its blind subspace was approximately

\[
\mathcal N_m=
\bigcap_{|s|\le m}\ker(JD\rho(s)).
\]

A relation residual could enter (mathcal N_m), appear harmless during the
trained horizon, and later be rotated out by another orthogonal operator.
Because the anchor frame, decoder, and suffix observer also received packet
gradients, the observer could co-adapt around the residual. This explains how
a small local packet loss coexisted with repeated-loop failure.

Version 0.5-v2 removes the easiest evasion by freezing the observer side and
testing repeated holonomy at powers 1, 2, 4, 8, and 16. It is a finite-depth
test, not yet a theorem of quotient closure. It also tests the relative loop

\[
H-I,
\]

whereas the literal difference between the original branches is

\[
L-R=R(H-I).
\]

The two are closely related under exact isometry but are not the same observed
map once a downstream suffix is attached. The held-out diamond and loop assays
therefore remain necessary even if the structural training loss becomes small.

## The exact ambient-aware criterion

Let a registered observability operator be

\[
\mathcal O=
\begin{bmatrix}
JD\\
JD\rho(s_1)\\
\vdots\\
JD\rho(s_m)
\end{bmatrix},
\qquad
K_{obs}=\ker\mathcal O.
\]

Finite packet equality says that relation residue is currently invisible:

\[
\mathcal O(H-I)B=0.
\]

To make that invisibility persistent, the ambient kernel must also be
forward-invariant under every generator:

\[
\rho(g)K_{obs}\subseteq K_{obs}.
\]

If (P_{obs}) and (Q_{obs}) project onto the observed row space and its
kernel, the corresponding leakage condition is

\[
P_{obs}\rho(g)Q_{obs}=0.
\]

The pair of conditions

\[
P_{obs}(H-I)B=0,
\qquad
P_{obs}\rho(g)Q_{obs}=0
\]

is stronger than sampling more suffixes. It says both that a relation defect
lands vertically and that subsequent operators cannot turn that vertical
defect into an observable semantic error. Nonidentity motion entirely inside
(K_{obs}) remains permitted.

In coordinates adapted to (S\oplus K), a general no-leak map has the block
form

\[
\rho(g)=
\begin{bmatrix}
A_g & 0\\
C_g & V_g
\end{bmatrix}.
\]

(A_g) carries the semantic action, (V_g) transports the ambient fiber, and
(C_g) may write semantic information into it. The zero upper-right block is
the no-uncontrolled-leakage condition.

There is a crucial restriction in the present hard-isometric architecture. If
\(\rho(g)\) is orthogonal and the upper-right block is exactly zero, then
orthogonality also forces \(C_g=0\). The operator is block diagonal. Thus an
exact permanently invariant kernel can support harmless ambient rotations but
cannot serve as a scratchpad that receives semantic information and later
returns it. Useful memory needs a typed release map, a time-dependent quotient,
or a controlled departure from strict orthogonality; it cannot be smuggled
into a fixed orthogonal no-leak block.

Under an invertible change of latent coordinates these blocks change, but the
invariant subspace and intertwining relations do not; this is the
coordinate-free object Komorebi transport mathematics should track.

## Useful ambient memory is not gauge noise

The separate ANC-4 construction prevents an overcorrection. Under an exact
rank-eight saturated semantic interface, a continuous online delay-four task
requires four additional state dimensions. Those dimensions store information
that is absent from the current semantic base and must affect a later output.
They are functional memory, not harmless gauge motion.

This means there cannot be one universal instruction to delete or permanently
seal the ambient fiber. The correct distinction is typed and temporal:

- gauge ambient state is invisible to all registered future consumers;
- memory ambient state has a declared future release path and provenance;
- uncontrolled ambient state can leak into behavior without either contract.

For a Markov operator-execution task, no extra history is needed, so a
forward-invariant observational kernel is appropriate. For a delayed-memory
task, the release map is part of the task type and should be audited rather
than prohibited.

## Decision rule for this block

The v0.5-v2 screen distinguishes three outcomes:

- If multiscale packet pressure improves held-out repeated loops while full
  holonomy remains nonzero, the data support a finite behavioral quotient with
  ambient gauge motion.
- If only exact pressure repairs loops, the current learned quotient is too
  weak; full flatness is the supported mechanism in this benchmark.
- If packet training loss falls but held-out loops do not improve, the next
  experiment should replace finite observation matching with the invariant-
  kernel leakage criterion above.

That replacement is substantial enough to be a separate block rather than a
post-outcome amendment to v0.5. A provisional v0.6, **Invariant Observable
Kernel**, would preregister the quotient rank or a stable singular-gap rule,
test projector and principal-angle invariance under coordinate conjugation,
and gate the maximum spectral leakage

\[
\max_g\lVert P_{obs}\rho(g)Q_{obs}\rVert_2
\]

rather than only an average Frobenius loss. If the observer has full numerical
rank, it must honestly report (Q_{obs}=0); a convenient posthoc singular-value
cutoff cannot manufacture an ambient quotient.

None of these outcomes establishes open-ended Neuralese. The aim is narrower:
identify which coordinate-independent geometric conditions make a recurrent
latent computation stable, causally executable, and honestly auditable.
