<a id="operator-audit"></a>

# Operator guide

Explore the concepts used to describe operations, split objects into parts,
change coordinates, and recover information from summaries. Use the concept
list as a reference, then follow the worked examples to see how the ideas
fit together in a calculation.

Here, an operator is a specified rule taking inputs to outputs. A packet is
one selected part of a representation; a transfer block records how an input
part contributes to an output part. The examples make those choices explicit
before comparing calculations.

[Start here](START_HERE.md) · [Worked demonstrations](DEMONSTRATIONS.md) · [Collection glossary](GLOSSARY.md)

Start with the matrix example below if this language is new. You can
[change its inputs and switch blocks on and off](https://komorebip.github.io/Operation-KOMOREBI/interactive.html#packets)
in the interactive diagram, or
[run and edit the packet program](https://komorebip.github.io/Operation-KOMOREBI/playground.html#packets).

## Operator concepts at a glance

| Concept | Meaning | See it in use |
|---|---|---|
| Operator | A specified rule taking admissible inputs to outputs. | [A two-coordinate operation](#a-complete-audit-of-a-two-coordinate-operation). |
| Domain and codomain | The allowed input space and the declared output space. | [Operations with matching types](examples/15_TYPED_PATHS.md). |
| Composition | Applying operations in sequence. In a product $AB$, apply $B$ first and then $A$. | [Order of operations](#check-the-order-of-operations). |
| Projector | A linear map $P$ satisfying $P^2=P$: applying it again leaves its output unchanged. | [Coordinate projectors](#specify-the-operation-and-the-packets). |
| Packet | A selected part of a representation, with the stated decomposition and reconstruction rules. | [Splitting the input](#specify-the-operation-and-the-packets). |
| Transfer block | The part of an operation carrying one input packet to one output packet. | [All four transfers](#account-for-all-four-transfers). |
| Coordinate transport | Describing the same operation in a different coordinate system. | [The transported matrix](#carry-the-operator-through-a-coordinate-change). |
| Residual | The difference between the desired operation or output and the retained approximation. | [Omitted interactions](#delete-interactions-and-identify-the-residual). |
| Commutator | For linear operators $A$ and $B$ on one space, the difference $AB-BA$, which tests whether their orders agree. | [A noncommutation witness](#check-the-order-of-operations). |
| Fiber | All admissible inputs that share one summary value. | [The general recovery test](#a-general-recovery-test). |
| Recovery | Obtaining a requested answer from the information retained in a summary. | [Sufficient and insufficient summaries](#ask-whether-the-retained-information-is-sufficient). |
| Stability | Control of how perturbations affect an answer, under specified norms or an error model. | [Exactness, stability, and evidence](#keep-exactness-stability-and-evidence-separate). |

## The audit in six questions

An operator audit is a practical way to use these concepts. It follows an
operation through a change of description, checking which interactions are
retained and what explains any difference in the result.

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

<a id="delete-an-interaction-and-identify-the-residual"></a>

### Delete interactions and identify the residual

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

## Check an identity beyond one successful input

Agreement on one vector can conceal a missing block. For example, omit only
$P_2TP_2$ and call the resulting operator $T_{\mathrm{trial}}$:

```math
T_{\mathrm{trial}}=\begin{pmatrix}1&2\\3&0\end{pmatrix},\qquad
z=\begin{pmatrix}2\\0\end{pmatrix},\qquad
T_{\mathrm{trial}}z=Tz=\begin{pmatrix}2\\6\end{pmatrix}.
```

This input has no second-coordinate contribution, so it does not expose the
omitted block. On the original input $x=(2,3)^{\mathsf T}$, however,
$T_{\mathrm{trial}}x=(8,6)^{\mathsf T}$ while $Tx=(8,18)^{\mathsf T}$.

For linear maps with the same finite-dimensional domain and the same codomain,
exact agreement on every vector of a basis proves agreement everywhere:
linearity extends the equality to each linear combination. Checking both
coordinate basis vectors in this example would detect the omission.
For nonlinear maps, basis values alone
do not determine the operation. With floating-point calculations, also state
the precision, tolerance, and justification for any broader error claim.

## Carry the operator through a coordinate change

If $y=Cx$ with an invertible coordinate map $C$, the same operation in the
new coordinates has matrix $T_y=CTC^{-1}$. The audit compares two routes for
every input $x$:

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

## Check the order of operations

Even when two compositions have matching types, their order can change the
answer. Let $P=P_1$ be the first-coordinate projector above. Compare applying
$T$ and then projecting with projecting first:

```math
PTx=\begin{pmatrix}8\\0\end{pmatrix},\qquad
TPx=\begin{pmatrix}2\\6\end{pmatrix}.
```

The second expression projects the input first and then applies $T$.
Their difference, $PTx-TPx=(6,-6)^{\mathsf T}$, is a witness that these
operations do not commute. Reading products from right to left keeps the
two tasks distinct. The [typed-path example](examples/15_TYPED_PATHS.md#compare-orders-only-on-one-space)
develops this test through the commutator $PT-TP$; the
[wavelet study](demonstrations/WAVELET_POLYPHASE.md) applies the same question
to filtering and coarsening.

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

### A general recovery test

A fiber of a summary is the set of inputs with one shared summary value.
For maps of sets $R:X\to S$ and $F:X\to Z$, a recovery rule
$G:R(X)\to Z$ with $F=G\circ R$ exists exactly when $F$ is constant on
every fiber:

```math
R(u)=R(v)\ \Longrightarrow\ F(u)=F(v)
\qquad\text{for all }u,v\in X.
```

Here, regard $R$ as a map $X\to R(X)$ when composing it with $G$.

Necessity follows because both inputs would receive the same value from $G$.
Conversely, when the condition holds, define $G(r)$ as the common value of
$F$ on the fiber over $r$. Each $r\in R(X)$ has such a fiber, and the
condition makes its answer unambiguous. This defines a recovery function;
it gives no automatic continuity, stability, or efficient evaluation guarantee.
The admissible input set matters: a restriction on $X$ can change its fibers
and the resulting recovery question.

[Open the Recovery Laboratory](https://komorebip.github.io/Operation-KOMOREBI/recovery-lab.html)
to try finite linear measurements, change the requested answer, inspect recovery rules
or collision witnesses, and add missing information. The
[recovery demonstration](demonstrations/RECOVERY.md) supplies the elementary
argument and its exact program.

## Keep exactness, stability, and evidence separate

The block identity above is a finite linear-algebra calculation. More
generally, let $X$ and $Y$ be vector spaces over the same field and
$T:X\to Y$ be linear, with finite packet families of linear maps
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
Control input or altered operation expected to expose a failure:
Norms, approximation, and convergence assumptions, if used:
Argument, program, source revision, and tested scope:
Conclusion and remaining obligations:
```

Make the conclusion specific to the task. For this example, the complete
block calculation reconstructs $T$ on every vector; the diagonal truncation
has residual $E$; and the sum alone cannot recover the first coordinate on
all of $\mathbb R^2$. Record an unresolved assumption beside the conclusion
that depends on it.

[Project map](PROJECT_MAP.md) · [All demonstrations](DEMONSTRATIONS.md) · [How to interpret verification](VERIFICATION.md)
