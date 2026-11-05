# Packets and projectors

[Operator guide](../OPERATOR_AUDIT.md) · [Operator algebra](ALGEBRA.md) · [Transfer and compression](TRANSFER.md)

A decomposition needs more than a list of parts. This chapter separates
projector identities, orthogonality, exact reconstruction, and redundancy.
Examples use real finite-dimensional spaces unless stated otherwise.

## 1. Projectors and idempotence

A linear projector is an endomorphism $P$ satisfying $P^2=P$. Its output
is already fixed by $P$. Every vector has the decomposition
$x=Px+(I-P)x$, with $Px$ in the image and $(I-P)x$ in the kernel.
The image and kernel intersect only at zero, so
$X=\operatorname{im}P\oplus\ker P$.

For example,

```math
P=\begin{pmatrix}1&1\\0&0\end{pmatrix},\qquad
P(x_1,x_2)^{\mathsf T}=(x_1+x_2,0)^{\mathsf T}.
```

The image is the first coordinate axis and the kernel is the line
$\{(t,-t):t\in\mathbb R\}$. These lines are complementary but are not
perpendicular in the Euclidean inner product.

[Split and reconstruct a vector](../examples/01_PACKETS.md).

## 2. Complete packet families and direct sums

For a finite family of linear maps on one space, the identities

```math
P_i^2=P_i,\qquad P_iP_j=0\ (i\ne j),\qquad \sum_iP_i=I
```

give an algebraic packet decomposition. Every vector is the sum of its
$P_i x$ components. Each component lies in a selected range, and the
decomposition into those ranges is unique.

The identity $\sum_iP_i=I$ alone guarantees additive reconstruction, but
does not guarantee projector identities. Over $\mathbb R$, the two maps
$2I$ and $-I$ sum to $I$, although neither is idempotent on a nonzero space.
Check the complete collection of identities before using direct-sum or
projector conclusions.

## 3. Orthogonal and oblique projectors

An **orthogonal projector** on an inner-product space satisfies both
$P^2=P$ and $P^*=P$. Its range and kernel are perpendicular.
A projector with a nonorthogonal range/kernel splitting is often called
**oblique**.

For the oblique $P$ in the first entry, $(2,3)^{\mathsf T}$ splits as
$(5,0)^{\mathsf T}+(-3,3)^{\mathsf T}$. These components reconstruct
the input, but their ordinary squared lengths sum to $25+18=43$, while
the input's squared length is $13$.

By contrast, the coordinate projectors split the same input into
$(2,0)^{\mathsf T}$ and $(0,3)^{\mathsf T}$, with $4+9=13$.
An energy decomposition therefore needs the appropriate orthogonality and
inner product. See [weighted averaging](../examples/08_WEIGHTED_AVERAGES.md)
and [projector norms](STABILITY.md#5-projector-norms-and-the-zero-case).

## 4. Analysis and synthesis

An analysis map $A:X\to Z$ forms coordinates or measurements. A synthesis
map $S:Z\to X$ reconstructs an object. Exact reconstruction on $X$ means
$SA=I_X$.

The coordinate space can be larger than the original space:

```math
A=\begin{pmatrix}1&0\\0&1\\1&1\end{pmatrix},\qquad
S=\frac13\begin{pmatrix}2&-1&1\\-1&2&1\end{pmatrix},\qquad SA=I_2.
```

For $x=(2,3)^{\mathsf T}$, analysis gives $(2,3,5)^{\mathsf T}$ and
synthesis returns $(2,3)^{\mathsf T}$. In the coordinate space,
$(AS)^2=AS$, but $AS\ne I_3$: it fixes valid analyzed coordinates and
maps other coordinate triples into that valid subspace.

[All matrix products in the redundancy example](../examples/06_REDUNDANT_COORDINATES.md).

## 5. Redundant components versus projectors

Let $E_i$ select coordinate $i$ in the three-coordinate space above.
The maps $C_i=SE_iA$ reconstruct one coordinate contribution at a time.
They sum to $SA=I_2$. However,

```math
C_1=\frac13\begin{pmatrix}2&0\\-1&0\end{pmatrix},\qquad
C_1^2=\frac23C_1\ne C_1.
```

Thus an exact analysis/synthesis system need not produce projector packets
on the original space. On $(2,3)^{\mathsf T}$, the three contributions are
$(4/3,-2/3)^{\mathsf T}$, $(-1,2)^{\mathsf T}$, and
$(5/3,5/3)^{\mathsf T}$; they still sum to the original input.

**Check:** Identify the analysis and synthesis identities before importing
claims about idempotence, independent components, or orthogonal energy.

## 6. Refinement and coarsening

Refinement replaces a packet by smaller packets whose sum equals the parent
projector. For the four-sample vector $x=(3,1,4,2)^{\mathsf T}$, using
zero-based sample indices, the even packet retains positions $0,2$ and the
odd packet retains positions $1,3$.

With singleton coordinate projectors $E_0,\ldots,E_3$,

```math
P_{\mathrm{even}}=E_0+E_2,\qquad
P_{\mathrm{odd}}=E_1+E_3,\qquad
\sum_{k=0}^3E_kx=x.
```

Keeping all children preserves the object. Deleting child $E_2$ instead
leaves $(3,1,0,2)^{\mathsf T}$ and residual $(0,0,4,0)^{\mathsf T}$.
Combining disjoint child packets into their parent and discarding a child
are different operations with different information consequences.

[Refine a signal](../demonstrations/REFINEMENT.md) · [Haar pairs](../examples/14_HAAR_PAIRS.md).

## 7. Invariant packets and block diagonality

For a complete algebraic packet family, a diagonal block $P_iTP_i$ maps
a packet to itself. An off-diagonal block $P_jTP_i$ records a transfer
between different packet ranges.

If $T$ commutes with every $P_i$, all off-diagonal blocks vanish:
$P_jTP_i=P_jP_iT=0$ for $j\ne i$. Conversely, if all off-diagonal
blocks vanish, reconstruction gives $TP_i=P_iT=P_iTP_i$.

Invariance of just one range is a weaker condition than vanishing transfers
in both directions. The upper-triangular matrix
$\begin{pmatrix}1&2\\0&3\end{pmatrix}$ preserves the first coordinate
axis but sends input from the second axis into the first. Its upper-right
block remains nonzero.

[See the transfer blocks](TRANSFER.md#1-source-to-target-blocks).

## 8. Spectral projectors and diagonalizability

For a finite-dimensional operator diagonalizable over the chosen field,
with distinct eigenvalues $\lambda_1,\ldots,\lambda_m$ in that field,
polynomial interpolation gives

```math
P_i=\prod_{j\ne i}\frac{T-\lambda_j I}{\lambda_i-\lambda_j},\qquad
T=\sum_i\lambda_iP_i.
```

The denominators are nonzero scalars. The selectors act as one on their
own eigenspace and zero on the others, giving a complete packet family.
For $T=\begin{pmatrix}2&1\\0&3\end{pmatrix}$,

```math
P_2=3I-T=\begin{pmatrix}1&-1\\0&0\end{pmatrix},\qquad
P_3=T-2I=\begin{pmatrix}0&1\\0&1\end{pmatrix}.
```

These projectors are oblique in the ordinary inner product. The diagonalizable
hypothesis matters: $J=\begin{pmatrix}2&1\\0&2\end{pmatrix}$ has only
eigenvalue $2$ but is not $2I$. Its nonzero nilpotent part carries information
that a scalar eigenvalue alone does not describe.

[Full spectral calculation](../examples/11_SPECTRAL_PROJECTORS.md).

## Try it: exact reconstruction with cancellation

Let $P=\begin{pmatrix}1&2\\0&0\end{pmatrix}$ and $Q=I-P$.
Check the packet identities and split $x=(2,3)^{\mathsf T}$.

**Answer.** $Q=\begin{pmatrix}0&-2\\0&1\end{pmatrix}$,
$P^2=P$, $Q^2=Q$, $PQ=QP=0$, and $P+Q=I$. The contributions
$(8,0)^{\mathsf T}$ and $(-6,3)^{\mathsf T}$ sum to $x$.
Exactness permits cancellation between large components; stability needs
its own estimate.

[Previous: Operator algebra](ALGEBRA.md) · [Next: Transfer and compression](TRANSFER.md) · [All chapters](../OPERATOR_AUDIT.md#reference-chapters)
