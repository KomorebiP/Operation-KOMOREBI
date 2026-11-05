<a id="operator-audit"></a>

# Operator guide

Explore the concepts used to describe operations, split objects into parts,
change coordinates, and recover information from summaries. Use the concept
list as a reference, then follow the worked examples to see how the ideas
fit together in a calculation. Seven reference chapters provide 54 worked
entries. The [operator catalog](operators/catalog/README.md) adds a searchable
reference to 205 entries in twelve families, with formulas, assumptions,
source links, and named finite checks. A complete introductory audit and a
reusable worksheet follow below.

Here, an operator is a specified rule taking inputs to outputs. A packet is
one selected part of a representation; a transfer block records how an input
part contributes to an output part. The examples make those choices explicit
before comparing calculations.

[Start here](START_HERE.md) · [Worked demonstrations](DEMONSTRATIONS.md) · [Collection glossary](GLOSSARY.md)

Start with the matrix example below if this language is new. You can
[change its inputs and switch blocks on and off](https://komorebip.github.io/Operation-KOMOREBI/interactive.html#packets)
in the interactive diagram, or
[run and edit the packet program](https://komorebip.github.io/Operation-KOMOREBI/playground.html#packets).

## Reference chapters

Each chapter combines definitions, hypotheses, exact examples, common mistakes,
and an exercise with its answer. Read them in sequence or jump to one topic.

| Chapter | What it covers | Entries |
|---|---|---|
| [Operator basics](operators/BASICS.md) | Types, linearity, identity and zero maps, kernels, inverses, eigenvectors, and adjoints. | 8 |
| [Operator algebra](operators/ALGEBRA.md) | Composition, polynomials, commutators, intertwiners, similarity, seeds, tensor products, and block elimination. | 8 |
| [Packets and projectors](operators/PACKETS.md) | Complete families, orthogonal and oblique projectors, analysis/synthesis, redundancy, refinement, and spectral packets. | 8 |
| [Transfer and compression](operators/TRANSFER.md) | Source-to-target blocks, composition, coordinate transport, reduced dynamics, leakage, and nonlinear defects. | 7 |
| [Recovery and repair](operators/RECOVERY.md) | Fibers, factorization, row spaces, collision witnesses, minimal added measurements, estimation, and memory. | 7 |
| [Stability and numerical meaning](operators/STABILITY.md) | Norms, error bounds, conditioning, nonnormal growth, infinite convergence, and numerical residuals. | 8 |
| [Polynomial and difference operators](operators/POLYNOMIAL.md) | Falling-factorial coordinates, transported differentiation, raising and degree, residue projectors, multiplication, shifts, and Newton recovery. | 8 |

**Use several operators together:** The [worked composition guide](operators/COMPOSITION.md)
adds six complete calculations. Follow an intermediate coordinate bridge,
compose coarse and metric defects, integrate from a changed polynomial basis,
retain a finite measure's correlations, and continue a recursive filter across
a chunk boundary. Each calculation includes an exact result and a failure control.

**First reading:** Begin with [basics](operators/BASICS.md), continue to
[packets](operators/PACKETS.md), then work through the
[two-coordinate audit](#a-complete-audit-of-a-two-coordinate-operation) below.
For a measurement or machine-state question, begin with
[recovery and repair](operators/RECOVERY.md). For a filter or approximation,
combine [transfer](operators/TRANSFER.md) with [stability](operators/STABILITY.md).
For an exact calculation across polynomial bases, continue with
[polynomial and difference operators](operators/POLYNOMIAL.md).

The [exact check program](../examples/operator_guide.py) runs the finite
examples using Python's standard library. From a repository checkout, run
`python -B examples/operator_guide.py`. The program checks finite identities
and failure witnesses; the general arguments and infinite-dimensional
statements retain the explanations and assumptions given in the text.

## Look up an operator or a composition law

The [operator catalog](operators/catalog/README.md) organizes 205 entries
from the existing compendium into twelve families. Search by name or stable
identifier, then open the entry for its formula, domain, assumptions, related
operations, and pinned sources. On the reading site, you can also filter by
family and whether an entry has a linked finite check.

The catalog covers structural and spectral projectors, coordinate transforms,
prime-power and digit operations, signals, nonlinear correction, dynamics,
quantum operations, finite models, metric transport, and integration.
Its [composition laws](operators/catalog/RELATIONS.md) connect operations
that can be used together under stated hypotheses. Covered laws link directly
to [worked calculations](operators/COMPOSITION.md), and the site's global search
can find individual laws by their `REL` identifiers.

The worked chapters explain selected operations in depth. The catalog is the
broader lookup reference, and the two overlap. Catalog entries include
classical operators, source constructions, derived combinations, and
implementation interfaces. A linked finite check describes a specific
calculation or failure control, not a certification of every assertion about
the operation. For polynomial coordinate transport, the
[Lean companion guide](LEAN_POLYNOMIAL_TRANSPORT.md) identifies the existing
formal statements and their precise scope.

| Your task | A useful route |
|---|---|
| Select coefficients after changing polynomial coordinates | [Polynomial packets](operators/POLYNOMIAL.md#5-transported-projectors-and-a-complete-packet-calculation), then the [coordinate](operators/catalog/C_COORDINATES.md) and [spectral](operators/catalog/B_CYCLIC.md) families. |
| Compose a filter or carry it across scales | [Transfer blocks](operators/TRANSFER.md#3-compose-blocks-through-intermediate-packets), then the [signal and polyphase family](operators/catalog/E_SIGNAL.md). |
| Decide whether a compressed state supports the next update | [Exact reduced dynamics](operators/TRANSFER.md#5-compression-and-exact-reduced-dynamics), then [recovery](operators/RECOVERY.md). |
| Compare an operation in different metrics | [Adjoints](operators/BASICS.md#8-adjoint-and-self-adjoint-operators) and [conditioning](operators/STABILITY.md#4-coordinate-conditioning), then the [metric transport family](operators/catalog/K_METRICS.md). |
| Turn an integral or moment question into a finite functional | [Operator types](operators/BASICS.md#1-typed-operators-domains-and-codomains), then the [finite integration and observation family](operators/catalog/L_INTEGRATION.md). |

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

## Find a concept

- **A–C:** [Adjoint](operators/BASICS.md#8-adjoint-and-self-adjoint-operators) · [Affine map](operators/BASICS.md#2-linear-affine-and-nonlinear-rules) · [Analysis and synthesis](operators/PACKETS.md#4-analysis-and-synthesis) · [Block composition](operators/TRANSFER.md#3-compose-blocks-through-intermediate-packets) · [Block reconstruction](operators/TRANSFER.md#2-reconstruction-from-all-blocks) · [Bounded operator](operators/STABILITY.md#2-sums-and-compositions-of-bounded-operators) · [Codomain](operators/BASICS.md#1-typed-operators-domains-and-codomains) · [Commutator](operators/ALGEBRA.md#3-commutators) · [Composition](operators/ALGEBRA.md#1-composition-and-order) · [Compression](operators/TRANSFER.md#5-compression-and-exact-reduced-dynamics) · [Condition number](operators/STABILITY.md#4-coordinate-conditioning) · [Conditional expectation](operators/RECOVERY.md#6-conditional-expectation-and-estimation) · [Conjugation](operators/ALGEBRA.md#5-similarity-and-conjugation) · [Cyclic vector](operators/ALGEBRA.md#6-operator-algebras-seeds-and-cyclic-vectors).
- **D–I:** [Direct sum](operators/PACKETS.md#2-complete-packet-families-and-direct-sums) · [Domain](operators/BASICS.md#1-typed-operators-domains-and-codomains) · [Eigenvalue](operators/BASICS.md#7-eigenvectors-and-invariant-subspaces) · [Exact recovery](operators/RECOVERY.md#2-exact-recovery-and-factorization) · [Fiber](operators/RECOVERY.md#1-summaries-and-fibers) · [Idempotence](operators/PACKETS.md#1-projectors-and-idempotence) · [Identity](operators/BASICS.md#3-identity-and-zero-maps) · [Image](operators/BASICS.md#4-kernel-image-rank-and-nullity) · [Intertwiner](operators/ALGEBRA.md#4-intertwiners) · [Invariant subspace](operators/BASICS.md#7-eigenvectors-and-invariant-subspaces) · [Inverse](operators/BASICS.md#5-injectivity-surjectivity-and-an-inverse).
- **K–P:** [Kernel](operators/BASICS.md#4-kernel-image-rank-and-nullity) · [Leakage](operators/TRANSFER.md#6-leakage-from-a-retained-packet) · [Left inverse](operators/BASICS.md#6-left-and-right-inverses) · [Linear map](operators/BASICS.md#2-linear-affine-and-nonlinear-rules) · [Minimal repair](operators/RECOVERY.md#5-repair-with-additional-measurements) · [Nilpotent operator](operators/ALGEBRA.md#2-powers-and-polynomials-in-an-operator) · [Nonnormality](operators/STABILITY.md#6-spectrum-and-nonnormal-growth) · [Numerical residual](operators/STABILITY.md#8-numerical-residuals-and-certified-statements) · [Oblique projector](operators/PACKETS.md#3-orthogonal-and-oblique-projectors) · [Operator algebra](operators/ALGEBRA.md#6-operator-algebras-seeds-and-cyclic-vectors) · [Operator norm](operators/STABILITY.md#1-vector-norms-and-induced-operator-norms) · [Orthogonal projector](operators/PACKETS.md#3-orthogonal-and-oblique-projectors) · [Packet](operators/PACKETS.md#2-complete-packet-families-and-direct-sums) · [Polynomial](operators/ALGEBRA.md#2-powers-and-polynomials-in-an-operator) · [Projector](operators/PACKETS.md#1-projectors-and-idempotence).
- **R–Z:** [Rank](operators/BASICS.md#4-kernel-image-rank-and-nullity) · [Redundancy](operators/PACKETS.md#5-redundant-components-versus-projectors) · [Refinement](operators/PACKETS.md#6-refinement-and-coarsening) · [Residual](operators/STABILITY.md#3-operator-residuals-and-input-errors) · [Right inverse](operators/BASICS.md#6-left-and-right-inverses) · [Row space](operators/RECOVERY.md#3-linear-recovery-row-spaces-and-kernels) · [Schur complement](operators/ALGEBRA.md#8-block-elimination-and-the-schur-complement) · [Seed](operators/ALGEBRA.md#6-operator-algebras-seeds-and-cyclic-vectors) · [Similarity](operators/ALGEBRA.md#5-similarity-and-conjugation) · [Spectral projector](operators/PACKETS.md#8-spectral-projectors-and-diagonalizability) · [Stability](operators/STABILITY.md#1-vector-norms-and-induced-operator-norms) · [Strong convergence](operators/STABILITY.md#7-finite-truncation-and-infinite-convergence) · [Summary](operators/RECOVERY.md#1-summaries-and-fibers) · [Tensor product](operators/ALGEBRA.md#7-tensor-products-and-kronecker-matrices) · [Truncation](operators/STABILITY.md#7-finite-truncation-and-infinite-convergence) · [Zero map](operators/BASICS.md#3-identity-and-zero-maps).
- **Polynomial route:** [Falling-factorial coordinates](operators/POLYNOMIAL.md#1-falling-factorial-coordinates) · [Forward difference](operators/POLYNOMIAL.md#2-forward-difference-as-a-transported-derivative) · [Raising and degree](operators/POLYNOMIAL.md#3-raising-and-degree-operators) · [Roots-of-unity projector](operators/POLYNOMIAL.md#4-coefficient-selectors-and-roots-of-unity-averaging) · [Transported packets](operators/POLYNOMIAL.md#5-transported-projectors-and-a-complete-packet-calculation) · [Transported product](operators/POLYNOMIAL.md#6-transported-multiplication-and-its-product-rule) · [Translation](operators/POLYNOMIAL.md#7-translation-carries-information-between-packets) · [Newton recovery](operators/POLYNOMIAL.md#8-recover-coordinates-and-check-the-coefficient-ring).

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
