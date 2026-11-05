# Operator algebra

[Operator guide](../OPERATOR_AUDIT.md) · [Basics](BASICS.md) · [Packets and projectors](PACKETS.md)

This chapter explains how operations combine and how the allowed operations
affect what can be generated. The matrices below act on real column vectors.
Products act from right to left; all displayed arithmetic is exact.

## 1. Composition and order

For $T:X\to Y$ and $U:Y\to Z$, the composition $UT:X\to Z$ applies
$T$ first. Matrix multiplication encodes this typed path. Composition is
associative, so $(VU)T=V(UT)$ whenever the types match.

Associativity permits regrouping, while exchanging operators requires a
separate identity. With

```math
T=\begin{pmatrix}1&2\\3&4\end{pmatrix},\quad
U=\begin{pmatrix}2&0\\0&1\end{pmatrix},\quad
x=\begin{pmatrix}2\\3\end{pmatrix},
```

we obtain $UTx=(16,18)^{\mathsf T}$ and $TUx=(10,24)^{\mathsf T}$.
The same two operators perform different tasks in the two orders.

[Follow typed paths](../examples/15_TYPED_PATHS.md).

## 2. Powers and polynomials in an operator

For an endomorphism $T$, powers mean repeated composition, and a scalar
polynomial $p(t)=\sum_{k=0}^m a_kt^k$ gives
$p(T)=\sum_{k=0}^m a_kT^k$. Matrix powers are not entrywise powers.

Take $N=\begin{pmatrix}0&1\\0&0\end{pmatrix}$. Although $N\ne0$,
$N^2=0$; such an operator is **nilpotent**. The polynomial relation gives

```math
(I+2N)(I-2N)=I-4N^2=I.
```

This constructs an inverse by a finite identity. More generally, if
$N^m=0$, then $(I-N)^{-1}=I+N+\cdots+N^{m-1}$. No convergence claim is
needed for this finite sum. An infinite geometric series requires additional
conditions; see [convergence](STABILITY.md#7-finite-truncation-and-infinite-convergence).

## 3. Commutators

For endomorphisms of the same vector space, the commutator is
$[A,B]=AB-BA$. It vanishes exactly when the two operations commute.

Using the first-coordinate projector $P$ and the matrix $T$ above,

```math
P=\begin{pmatrix}1&0\\0&0\end{pmatrix},\qquad
[P,T]=\begin{pmatrix}0&2\\-3&0\end{pmatrix}.
```

Applied to $(2,3)^{\mathsf T}$, this gives $(6,-6)^{\mathsf T}$.
It is an explicit order-dependence witness. Two different diagonal matrices
commute, so a zero commutator does not force equality of the operators.
Also check types: subtracting $AB$ and $BA$ makes sense only when both
act between the same spaces.

## 4. Intertwiners

An **intertwiner** $R:X\to S$ relates $T:X\to X$ to
$V:S\to S$ through

```math
RT=VR.
```

It says that operating before changing the description agrees with changing
the description first and operating there. It does not require $R$ to be
invertible.

For $R=[1\ \ 1]$ and the coordinate swap
$T=\begin{pmatrix}0&1\\1&0\end{pmatrix}$, we have $RT=R$.
Thus $V=1$ gives an exact evolution of the sum even though the sum loses
the two individual coordinates. Exact transfer of this task can coexist
with loss of other information.

[Exact reduced dynamics](TRANSFER.md#5-compression-and-exact-reduced-dynamics).

## 5. Similarity and conjugation

If an intertwiner $C$ is an isomorphism, the relation $CT=T'C$ is
equivalent to $T'=CTC^{-1}$. The matrices are **similar**: they describe
the same endomorphism in corresponding coordinates.

For example,

```math
C=\begin{pmatrix}1&1\\0&1\end{pmatrix},\quad
D=\begin{pmatrix}2&0\\0&3\end{pmatrix},\quad
CDC^{-1}=\begin{pmatrix}2&1\\0&3\end{pmatrix}.
```

An eigenvector $v$ of $D$ becomes the eigenvector $Cv$ of $CDC^{-1}$
with the same eigenvalue. Similarity preserves eigenvalues, but ordinary
Euclidean lengths can change when $C$ is not orthogonal. The
[conditioning entry](STABILITY.md#4-coordinate-conditioning) keeps track of
that distinction. For maps with different input and output spaces, use the
[two coordinate maps](TRANSFER.md#4-transport-between-different-coordinate-spaces).

## 6. Operator algebras, seeds, and cyclic vectors

An operator algebra specifies which sums, scalar multiples, and compositions
are allowed. A seed generates vectors through that action. A **cyclic vector**
for a linear operator is one whose polynomial orbit spans the whole space.

For the nilpotent $N$ above and $v=e_2$,

```math
v=e_2,\qquad Nv=e_1,\qquad
(aI+bN)v=(b,a)^{\mathsf T}.
```

One seed generates $\mathbb R^2$ under $\mathbb R[N]$. The seed $e_1$
generates only its own line, since $Ne_1=0$. If the allowed algebra consists
only of scalar multiples of the identity, two independent seeds are needed
for this space. Thus a minimum seed count belongs to a declared action as
well as to a space.

[Complete seed calculation and source discussion](../examples/02_SEEDS.md).

## 7. Tensor products and Kronecker matrices

For linear maps $A:X\to X'$ and $B:Y\to Y'$, their tensor product acts
on simple tensors by $(A\otimes B)(x\otimes y)=Ax\otimes By$ and extends
linearly. With fixed bases this gives the Kronecker matrix.

For $A=\operatorname{diag}(2,3)$ and
$B=\begin{pmatrix}0&1\\1&0\end{pmatrix}$,

```math
A\otimes B=
\begin{pmatrix}0&2&0&0\\2&0&0&0\\0&0&0&3\\0&0&3&0\end{pmatrix}.
```

It sends $(1,2,0,0)^{\mathsf T}=e_1\otimes(1,2)^{\mathsf T}$ to
$(4,2,0,0)^{\mathsf T}$. This acts on four coordinates, whereas the
composition $AB$ acts on two. With compatible types,
$(A\otimes B)(C\otimes D)=(AC)\otimes(BD)$.
The [quantum example](../examples/17_QUANTUM_MEASUREMENT.md) provides a
route into composite-state applications.

## 8. Block elimination and the Schur complement

For a block system $Ax+By=f$, $Cx+Dy=g$ with invertible $A$, substitute
$x=A^{-1}(f-By)$ into the second equation. The remaining equation is

```math
(D-CA^{-1}B)y=g-CA^{-1}f.
```

The operator $D-CA^{-1}B$ is the **Schur complement** of $A$.
Its order of multiplication comes from the substitution.

For $2x+y=5$ and $x+3y=5$, the Schur complement is $3-1/2=5/2$,
so $(5/2)y=5/2$, giving $y=1$ and $x=2$. If $A$ is singular, this
particular elimination formula is unavailable. The full block matrix may
still be invertible: the coordinate-swap matrix is a simple example.

[Eliminate a block by hand](../examples/12_BLOCK_ELIMINATION.md).

## Try it: a short operator word

With $N$ as above and $P=\operatorname{diag}(1,0)$, calculate $PN$, $NP$,
and $[P,N]$.

**Answer.** $PN=N$, $NP=0$, and $[P,N]=N$. On $(2,3)^{\mathsf T}$ the difference
is $(3,0)^{\mathsf T}$. The identity $N^2=0$ does not permit exchanging
$N$ with an unrelated projector.

[Previous: Basics](BASICS.md) · [Next: Packets and projectors](PACKETS.md) · [All chapters](../OPERATOR_AUDIT.md#reference-chapters)
