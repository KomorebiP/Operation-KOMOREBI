# Operator audit

An operator audit follows an operation through a change of description. It asks
whether the new calculation performs the same task, which interactions it
retains, and what evidence explains any difference. Use it when splitting an
object into packets, changing coordinates, filtering a signal, or working from
a summary.

[Start here](START_HERE.md) · [Worked demonstrations](DEMONSTRATIONS.md) · [Glossary](GLOSSARY.md)

Start with the matrix example below if this language is new. You can
[change its inputs and switch blocks on and off](https://komorebip.github.io/Operation-KOMOREBI/interactive.html#packets)
in the existing interactive diagram, or
[run and edit the packet program](https://komorebip.github.io/Operation-KOMOREBI/playground.html#packets).

## The audit in six questions

| Question | What to write down | What can go wrong |
|---|---|---|
| What acts on what? | The input and output spaces, coefficient system, admissible inputs, and operation. | A composition uses incompatible spaces or silently changes the domain. |
| How is the object represented? | The analysis and reconstruction maps, or the packet projectors and their identities. | A round trip is mistaken for an inverse on the whole space. |
| How does the operation transfer? | The transported operator or every required source-to-target block. | The coordinates change while the operator matrix stays fixed. |
| Which interactions are retained? | The blocks used, their composition order, and any truncation. | Couplings are deleted without accounting for their contribution. |
| What is lost or recoverable? | A residual, a recovery rule, or two indistinguishable inputs with different answers. | A summary is assumed sufficient for every question. |
| What supports the conclusion? | The identity or argument, tested inputs, source revision, and any separate stability assumptions. | One successful calculation is treated as an unrestricted theorem. |

The answer can be exact agreement, a quantified difference, or an obstruction
to the proposed task. Each is useful when its assumptions are explicit.

## A complete audit of a two-coordinate operation

### Specify the operation and the packets

Work with column vectors in $\mathbb R^2$. Let

```math
T=\begin{pmatrix}1&2\\3&4\end{pmatrix},\qquad
x=\begin{pmatrix}2\\3\end{pmatrix},\qquad
P_1=\begin{pmatrix}1&0\\0&0\end{pmatrix},\qquad
P_2=\begin{pmatrix}0&0\\0&1\end{pmatrix}.
```

The two packets retain the first and second coordinates. They satisfy
$P_i^2=P_i$, $P_1P_2=P_2P_1=0$, and $P_1+P_2=I$. Thus
$x=P_1x+P_2x$. Direct multiplication gives $Tx=(8,18)^{\mathsf T}$.

### Account for all four transfers

The block $P_jTP_i$ takes input from packet $i$ to output packet $j$.
Rows name targets; columns name sources. Both diagonal and off-diagonal
blocks belong to the operation.

| Target | From packet 1 | From packet 2 | Total output |
|---|---|---|---|
| Packet 1 | $P_1TP_1x=(2,0)^{\mathsf T}$ | $P_1TP_2x=(6,0)^{\mathsf T}$ | $(8,0)^{\mathsf T}$ |
| Packet 2 | $P_2TP_1x=(0,6)^{\mathsf T}$ | $P_2TP_2x=(0,12)^{\mathsf T}$ | $(0,18)^{\mathsf T}$ |

Adding these contributions reproduces $(8,18)^{\mathsf T}$. The reason it
works for every vector, beyond this particular input, is the operator identity

```math
\sum_{j=1}^2\sum_{i=1}^2 P_jTP_i
=(P_1+P_2)T(P_1+P_2)=T.
```

The [packet demonstration](demonstrations/PACKETS.md) gives the complete
program, expected output, written-proof route, and recorded formal coverage.

### Delete an interaction and identify the residual

Keep only the diagonal blocks. The resulting operation is

```math
\widetilde T=P_1TP_1+P_2TP_2
=\begin{pmatrix}1&0\\0&4\end{pmatrix},\qquad
\widetilde T x=\begin{pmatrix}2\\12\end{pmatrix}.
```

The omitted contribution is explicit:

```math
E=T-\widetilde T=P_1TP_2+P_2TP_1
=\begin{pmatrix}0&2\\3&0\end{pmatrix},\qquad
Ex=\begin{pmatrix}6\\6\end{pmatrix}.
```

Hence $Tx=\widetilde T x+Ex$. The packets still reconstruct the input
exactly; deleting their interactions changes the operation. In the
[interactive diagram](https://komorebip.github.io/Operation-KOMOREBI/interactive.html#packets),
switch off the two off-diagonal blocks to reproduce this control. Switch them
back on to restore the complete calculation.

## Carry the operator through a coordinate change

If $y=Cx$ with an invertible coordinate map $C$, the same operation in the
new coordinates has matrix $T_y=CTC^{-1}$. The audit compares two routes:

```math
T_y(Cx)=C(Tx),\qquad\text{equivalently}\qquad T_yC=CT.
```

For the same $T$ and $x$ above, choose

```math
C=\begin{pmatrix}1&1\\0&1\end{pmatrix},\qquad
C^{-1}=\begin{pmatrix}1&-1\\0&1\end{pmatrix},\qquad
T_y=\begin{pmatrix}4&2\\3&1\end{pmatrix}.
```

Then $y=(5,3)^{\mathsf T}$ and both routes give
$T_y y=C(Tx)=(26,18)^{\mathsf T}$. Reusing the old matrix on $y$ instead
gives $Ty=(11,27)^{\mathsf T}$, which fails this comparison.
The [coordinate walkthrough](examples/03_COORDINATES.md) develops another
example with every matrix product shown.

Invertibility matters here. When a representation discards information,
there may be no $C^{-1}$; a recovery question replaces this conjugation rule.
For operations between different spaces, use the corresponding input and
output coordinate maps. Check that every composition has matching types.
The [typed-path example](examples/15_TYPED_PATHS.md) explains why a
one-sided inverse does not make both round trips identities.

## Ask whether the retained information is sufficient

Suppose the available summary is $R(x_1,x_2)=x_1+x_2$, while the requested
answer is $F(x_1,x_2)=x_1$. Exact recovery for every input would require
a function $G$ on the attainable summaries such that $F=G\circ R$.

But $u=(1,0)$ and $v=(0,1)$ have $R(u)=R(v)=1$, while $F(u)=1$ and
$F(v)=0$. A single value $G(1)$ cannot give both answers. This is an
obstruction to every recovery function using that summary alone.

The same summary does recover $H(x_1,x_2)=2x_1+2x_2$, using $G_H(s)=2s$.
Sufficiency depends on the question. Adding the measurement $x_1-x_2$
also repairs the original task: if $s=x_1+x_2$ and $d=x_1-x_2$, then
$x_1=(s+d)/2$.

[Open the Recovery Laboratory](https://komorebip.github.io/Operation-KOMOREBI/recovery-lab.html)
to change the measurement and the requested answer, inspect recovery rules
or collision witnesses, and add missing information. The
[recovery demonstration](demonstrations/RECOVERY.md) supplies the elementary
argument and its exact program.

## Keep exactness, stability, and evidence separate

The block identity above is a finite linear-algebra calculation. More
generally, let $T:X\to Y$ be linear, with finite packet families
$P_i:X\to X$ and $Q_j:Y\to Y$ whose sums are $I_X$ and $I_Y$.
Then $\sum_{j,i}Q_jTP_i=T$. The reconstruction follows by expanding
$(\sum_jQ_j)T(\sum_iP_i)$.

When calling these maps packet projectors, also check their idempotence and
the vanishing products within each family. Algebraic packet projectors can
be oblique; these identities alone imply no norm-one or numerical-stability
claim. Specify the norms, conditioning, and error model when those matter.
Infinite decompositions additionally need a justified meaning for the sums
and their convergence. Nonlinear operations require their own transfer laws.

An exact program can check a stated matrix identity or exhibit a failure
witness. A finite sample of matching outputs alone establishes agreement on
those inputs. For each broader conclusion, follow its written argument and
retain its hypotheses. A linked Lean file or compilation record supports the
formal statement and revision it actually checks.

These introductory calculations use classical linear algebra and the
collection's existing examples. This guide adds an explanatory reading route;
it does not change the recorded review or formal-verification status of a work.

## Use the audit across the collection

| Follow this question | Continue with |
|---|---|
| How do packet blocks reconstruct a linear operation? | [Paper I](works/paper-i.md), [transfer-block example](examples/04_TRANSFER.md), and [packet demonstration](demonstrations/PACKETS.md). |
| What changes under refinement or nonlinear transfer? | [Paper III](works/paper-iii.md) and [signal refinement](demonstrations/REFINEMENT.md). |
| Which cross-scale interactions does a filter need? | [Wavelets and polyphase transfer](demonstrations/WAVELET_POLYPHASE.md). |
| What happens when a filter is applied in the wrong basis? | [Roots of unity and falling-factorial coordinates](demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md). |
| Which coherence does a measurement remove? | [Quantum phase and measurement](demonstrations/QUANTUM_PHASE_MEASUREMENT.md). |
| Which answers survive a summary, and how can it be repaired? | [Realization Boundaries](works/realization-boundaries.md), [hidden memory](examples/22_HIDDEN_MEMORY.md), and [repair directions](examples/25_REPAIR_MENUS.md). |

## A worksheet for your own operation

Copy these fields into your notes, then fill them for one concrete task:

```text
Task and admissible inputs:
Input/output spaces and coefficients:
Operation and order of composition:
Representation and reconstruction maps:
Identity needed for the two routes to agree:
Retained blocks or measurements:
Residual, recovery rule, or failure witness:
Norms, approximation, and convergence assumptions, if used:
Argument, program, source revision, and tested scope:
Conclusion and remaining obligations:
```

[Project map](PROJECT_MAP.md) · [All demonstrations](DEMONSTRATIONS.md) · [How to interpret verification](VERIFICATION.md)
