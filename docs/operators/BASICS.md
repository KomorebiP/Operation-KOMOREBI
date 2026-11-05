# Operator basics

[Operator guide](../OPERATOR_AUDIT.md) · [Operator algebra](ALGEBRA.md) · [Collection glossary](../GLOSSARY.md)

Start here to read an operator's type, distinguish linearity from other kinds
of rules, and understand what an inverse or an adjoint promises. Unless a
section says otherwise, the examples use finite-dimensional real vector
spaces, column vectors, and exact arithmetic.

## 1. Typed operators, domains, and codomains

Writing $T:X\to Y$ specifies the allowed inputs and declared output space.
The **image** consists of the outputs actually attained. It can be smaller
than the codomain. In this guide, “operator” can mean a general specified
rule; a linear operator has the additional property in the next section.

For example, $R:\mathbb R^2\to\mathbb R$ given by
$R(x_1,x_2)=x_1+x_2$ takes a pair to a scalar. The map
$B:\mathbb R\to\mathbb R^2$, $B(s)=(s,0)$, takes a scalar back to a pair.
Consequently $RB$ acts on scalars, while $BR$ acts on pairs. Their outputs
cannot be compared as though these were maps of the same type.

**Check:** Write the domain and codomain beside every arrow before composing
maps. A matrix's dimensions are a useful first check, but the declared spaces
and coefficient systems matter too.

[Worked typed paths](../examples/15_TYPED_PATHS.md).

## 2. Linear, affine, and nonlinear rules

A map between vector spaces over a common field is **linear** when

```math
T(au+bv)=aT(u)+bT(v)
```

for all vectors $u,v$ and scalars $a,b$. In particular, $T(0)=0$.
An **affine** map has the form $x\mapsto Lx+c$ with $L$ linear. It is
linear exactly when $c=0$.

The rules $L(x_1,x_2)=2x_1-x_2$, $A(x)=L(x)+3$, and
$f(x_1,x_2)=x_1x_2$ illustrate the three cases. For the nonlinear example,
$f(1,0)+f(0,1)=0$ while $f((1,0)+(0,1))=1$.

**Common mistake:** Splitting an input does not automatically split the
output of a nonlinear rule into the sum of its separate outputs. The
[nonlinear transfer entry](TRANSFER.md#7-nonlinear-transfer-defects) makes
the missing interaction explicit.

## 3. Identity and zero maps

The identity $I_X:X\to X$ fixes every input. The zero map $0_{Y,X}:X\to Y$
sends every input to the zero vector in $Y$. For $T:X\to Y$,

```math
TI_X=I_YT=T.
```

The identity is attached to a space. In matrix coordinates, $I_2$ and $I_3$
have different sizes. A zero map can be rectangular, such as a zero map
from three coordinates to two.

For powers of a square linear operator, $T^0=I_X$, including when $T$ is
the zero operator. This convention makes polynomial evaluation and repeated
composition consistent. It is used in the
[seed example](../examples/02_SEEDS.md) and the
[hidden-memory calculation](../examples/22_HIDDEN_MEMORY.md).

## 4. Kernel, image, rank, and nullity

For a linear map, the **kernel** is the set of inputs sent to zero, and the
image is the subspace of attained outputs:

```math
\ker T=\{x:T x=0\},\qquad
\operatorname{im}T=\{Tx:x\in X\}.
```

For $R=[1\ \ 1]$, the kernel is
$\{(t,-t):t\in\mathbb R\}$ and the image is all of $\mathbb R$.
Thus its rank is one and its nullity is one.

When $X$ is finite-dimensional, rank–nullity says
$\dim X=\dim\ker T+\dim\operatorname{im}T$. One way to see this is to
extend a basis of the kernel to a basis of $X$; the images of the added
vectors form a basis of the image. The kernel records erased directions,
not their importance for a particular task.

[Kernels and fibers by hand](../examples/10_KERNELS.md).

## 5. Injectivity, surjectivity, and an inverse

A map is **injective** when equal outputs force equal inputs, and
**surjective onto its codomain** when every declared output is attained.
A two-sided inverse exists exactly when the map is bijective.

The sum map $R:\mathbb R^2\to\mathbb R$ is surjective but not injective.
The insertion $B(s)=(s,0)$ is injective but not surjective onto
$\mathbb R^2$. Its image is only the first coordinate axis.

For finite-dimensional linear maps, injectivity is equivalent to a zero
kernel. For a square matrix, injectivity, surjectivity, and invertibility
are equivalent. For rectangular maps, keep the two questions separate.
Changing the codomain to the image makes a map surjective, but does not
recover inputs it already identifies.

## 6. Left and right inverses

For $R:X\to S$, a map $B:S\to X$ with $RB=I_S$ is a **right inverse**
of $R$. Equivalently, $R$ is a left inverse of $B$. Using the sum and
insertion maps above,

```math
RB=1,\qquad
BR=\begin{pmatrix}1&1\\0&0\end{pmatrix}\ne I_2.
```

Every scalar can be inserted and read back exactly. An arbitrary pair
cannot be recovered by this chosen insertion: $BR(0,1)=(1,0)$.
The round trip $BR$ is nevertheless a projector, since
$(BR)^2=B(RB)R=BR$.

**Check:** An exact round trip on one space proves the corresponding
one-sided identity. It does not supply the other identity on a larger space.
[Redundant coordinates](../examples/06_REDUNDANT_COORDINATES.md) give a
useful three-coordinate version.

## 7. Eigenvectors and invariant subspaces

A nonzero vector $v$ is an eigenvector of an endomorphism $T:X\to X$
when $Tv=\lambda v$. Its eigenvalue is $\lambda$, and the corresponding
eigenspace is $\ker(T-\lambda I)$.

A subspace $W$ is **invariant** when $T(W)\subseteq W$. An eigenvector
spans an invariant line. For $D=\operatorname{diag}(2,3)$, the two coordinate
axes are invariant eigenspaces. A general invariant subspace need not be
one-dimensional, and an operator need not have an eigenbasis over the
chosen field.

For $T=\begin{pmatrix}1&2\\3&4\end{pmatrix}$, the first coordinate
axis is not invariant: $T(1,0)^{\mathsf T}=(1,3)^{\mathsf T}$ leaves it.
The [packet chapter](PACKETS.md#7-invariant-packets-and-block-diagonality)
relates this failure to off-diagonal blocks.

## 8. Adjoint and self-adjoint operators

An adjoint depends on specified inner products. For a linear map
$T:X\to Y$ between finite-dimensional inner-product spaces, the adjoint
$T^*:Y\to X$ is characterized by

```math
\langle Tx,y\rangle_Y=\langle x,T^*y\rangle_X.
```

With standard Euclidean coordinates, it is the transpose. With standard
complex inner products, it is the conjugate transpose. An operator on one
inner-product space is **self-adjoint** when $T^*=T$.

For a real weighted inner product $\langle x,y\rangle_W=x^{\mathsf T}Wy$
with symmetric positive-definite $W$, the adjoint of a square matrix is
$W^{-1}T^{\mathsf T}W$. For instance,

```math
W=\begin{pmatrix}1&0\\0&3\end{pmatrix},\quad
T=\begin{pmatrix}0&1\\1&0\end{pmatrix},\quad
T^*=\begin{pmatrix}0&3\\1/3&0\end{pmatrix}.
```

Thus ordinary matrix symmetry alone does not settle self-adjointness after
changing the inner product. See the
[weighted-average example](../examples/08_WEIGHTED_AVERAGES.md).

## Try it: a rectangular inverse

Let $A=[2\ \ {-1}]$ and $B=(1/2,0)^{\mathsf T}$. Find $AB$, $BA$,
and $\ker A$.

**Answer.** $AB=1$, $BA=\begin{pmatrix}1&-1/2\\0&0\end{pmatrix}$, and
$\ker A=\operatorname{span}\{(1,2)^{\mathsf T}\}$. The matrix $BA$ is
idempotent but is not $I_2$. It selects one representative for each measured
scalar; it does not reconstruct every original input.

[Next: Operator algebra](ALGEBRA.md) · [All operator chapters](../OPERATOR_AUDIT.md#reference-chapters)
