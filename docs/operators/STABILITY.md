# Stability and numerical meaning

[Operator guide](../OPERATOR_AUDIT.md) · [Recovery and repair](RECOVERY.md) · [Collection glossary](../GLOSSARY.md)

An identity explains exact agreement. Stability explains how errors or
perturbations affect the answer. This chapter distinguishes norm bounds,
conditioning, spectral information, convergence, and numerical evidence.

## 1. Vector norms and induced operator norms

A vector norm is zero exactly at the zero vector, scales by the absolute
value of a scalar, and satisfies the triangle inequality. Once norms on the
domain and codomain are fixed, the induced norm of a
linear operator is

```math
\|T\|=\sup_{x\ne0}\frac{\|Tx\|}{\|x\|}.
```

The examples here have nonzero finite-dimensional domains. On the zero
space the zero operator has norm zero. The basic estimate is
$\|Tx\|\le\|T\|\,\|x\|$.

For a real or complex matrix, the induced $1$-norm is its maximum absolute
column sum, and the induced infinity norm is its maximum absolute row sum.
The Euclidean induced norm is its largest singular value. For

```math
E=\begin{pmatrix}0&2\\3&0\end{pmatrix},\qquad
E^{\mathsf T}E=\begin{pmatrix}9&0\\0&4\end{pmatrix},
```

all three induced norms are $3$. A matrix norm is a statement about the
chosen input/output norms, rather than a coordinate-free numerical label.

## 2. Sums and compositions of bounded operators

For compatible normed spaces and bounded linear maps,

```math
\|UT\|\le\|U\|\,\|T\|,\qquad
\|S+T\|\le\|S\|+\|T\|.
```

The composition bound follows by applying
$\|UTx\|\le\|U\|\,\|Tx\|\le\|U\|\,\|T\|\,\|x\|$.
The sum bound follows from the triangle inequality for every input.
In finite dimensions, linear maps are bounded for the usual vector norms;
in general normed spaces, boundedness is an additional requirement.

These estimates need not be sharp. With
$P=\operatorname{diag}(1,0)$ and $Q=\operatorname{diag}(0,1)$,
$\|P\|_2=\|Q\|_2=1$ but $PQ=0$. The inequality gives an upper bound,
not equality for every composition.

## 3. Operator residuals and input errors

Let $\widetilde T$ approximate $T$, and write $E=T-\widetilde T$.
If the actual input is $x$ but the computation uses $x+\eta$, then

```math
Tx-\widetilde T(x+\eta)=Ex-\widetilde T\eta,
\qquad
\|Tx-\widetilde T(x+\eta)\|
\le\|E\|\,\|x\|+\|\widetilde T\|\,\|\eta\|.
```

A further additive arithmetic error $r$ contributes at most $\|r\|$
to this bound. Operator truncation, input uncertainty, and arithmetic error
therefore have separate terms.

For the guide's diagonal truncation, $E$ is the matrix in entry 1 and
$x=(2,3)^{\mathsf T}$ gives $Ex=(6,6)^{\mathsf T}$. In the Euclidean
norm, $\|Ex\|_2^2=72\le9\cdot13=\|E\|_2^2\|x\|_2^2$.
The bound applies to every input; this particular input need not attain it.
Relative error additionally needs a specified nonzero reference magnitude.

### Budget error over several updates

Let $T$ and $\widetilde T$ be bounded linear endomorphisms of one normed space.
For an integer $n\ge1$, a telescoping identity gives

```math
T^n-\widetilde T^n=
\sum_{k=0}^{n-1}T^{n-1-k}(T-\widetilde T)\widetilde T^k.
```

Consecutive terms cancel after expanding the difference. No commutation
assumption is needed. If $\|T\|,\|\widetilde T\|\le M$, with $M>0$,
and $\|T-\widetilde T\|\le\epsilon$, then

```math
\|T^n-\widetilde T^n\|\le nM^{n-1}\epsilon.
```

The estimate records both the one-step defect and possible amplification
over the requested number of updates. It can be conservative. For
$T=\operatorname{diag}(1,1/2)$ and
$\widetilde T=\operatorname{diag}(1,2/5)$ in Euclidean norm, take
$M=1$ and $\epsilon=1/10$. After three updates,

```math
T^3-\widetilde T^3=\operatorname{diag}(0,61/1000),\qquad
\|T^3-\widetilde T^3\|_2=61/1000\le3/10.
```

If the starting input is also perturbed, compare
$T^nx$ with $\widetilde T^n(x+\eta)$. The corresponding bound is
$nM^{n-1}\epsilon\|x\|+M^n\|\eta\|$. Arithmetic or measurement error
injected at each step must be propagated from that step onward as well.
A tolerance for one update is therefore only one part of a repeated-update
error budget.

For errors in a sequence of observations, the
[worked observation study](OBSERVATION.md#4-put-a-bound-on-noisy-reconstruction)
derives sharp bounds for reconstructed coordinates and a predicted reading.
Its [four-reading fit](OBSERVATION.md#6-fit-all-four-readings-under-squared-error)
shows why the estimator minimizing squared residuals need not satisfy a
separate limit on every individual residual.

## 4. Coordinate conditioning

For invertible $C$ on a nonzero finite-dimensional normed space, define
$\kappa(C)=\|C\|\,\|C^{-1}\|$. For the same induced norm on the old
and new coordinate spaces,

```math
\|CTC^{-1}\|\le\kappa(C)\,\|T\|.
```

For $C=\begin{pmatrix}1&10\\0&1\end{pmatrix}$ and its inverse,
both infinity norms are $11$, so $\kappa_\infty(C)=121$.
Conjugating $D=\operatorname{diag}(1,2)$ gives

```math
CDC^{-1}=\begin{pmatrix}1&10\\0&2\end{pmatrix}.
```

The new infinity norm is $11$, compared with $\|D\|_\infty=2$,
although the eigenvalues remain $1$ and $2$. In Euclidean norm, orthogonal
or unitary coordinate changes have condition number one. A poorly
conditioned description can amplify coordinate errors even when the
underlying exact relation remains valid.

## 5. Projector norms and the zero case

An orthogonal projector in Euclidean space satisfies $\|Px\|_2\le\|x\|_2$
by the perpendicular decomposition $x=Px+(I-P)x$. If its range is nonzero,
a unit vector in that range attains equality, so $\|P\|_2=1$.
The zero projector has norm zero.

Algebraic idempotence alone gives no such contractive bound. The oblique
projector

```math
P=\begin{pmatrix}1&10\\0&0\end{pmatrix},\qquad P^2=P,
```

has Euclidean operator norm $\sqrt{101}$: it sends $x$ to the scalar
inner product of $(1,10)$ with $x$, placed in the first coordinate.
Cauchy–Schwarz gives the upper bound, attained by a unit vector parallel
to $(1,10)$. Its only eigenvalues are zero and one.

[Orthogonal and oblique packets](PACKETS.md#3-orthogonal-and-oblique-projectors).

## 6. Spectrum and nonnormal growth

An eigenvalue measures action on an eigendirection. An induced norm measures
the largest one-step amplification over all directions. They need not agree.

For $M>0$, take

```math
N=\begin{pmatrix}0&M\\0&0\end{pmatrix},\qquad N^2=0.
```

Both eigenvalues are zero, yet $\|N\|_2=M$, attained on the second
coordinate vector. Thus the spectrum can coexist with arbitrarily large
one-step gain. The operator is nonnormal when $M\ne0$: $N^*N\ne NN^*$.

For $A=I+N$, all eigenvalues equal one, while $A^n=I+nN$ for
nonnegative integers $n$. A spectral radius of one therefore does not by
itself bound all iterates. Additional structure, such as normality in a
specified inner product, changes what spectral information controls.

The [stable-update study](DYNAMICS.md) follows a matrix with both eigenvalues
equal to $1/2$. Its exact power norm grows before decaying, while a specified
quadratic energy decreases at every unforced update. The study also derives
a sharp [persistent-disturbance bound](DYNAMICS.md#6-propagate-disturbances-from-the-step-where-they-enter)
and compares it with a more conservative contraction estimate.

## 7. Finite truncation and infinite convergence

Finite packet identities use finite sums. An infinite decomposition must
state the space, topology, and meaning of convergence.

On $\ell^2$, let $P_m$ retain the first $m$ coordinates. For every fixed
$x\in\ell^2$,

```math
\|x-P_mx\|_2^2=\sum_{k>m}|x_k|^2\longrightarrow0.
```

Thus $P_m$ converges strongly to the identity: each fixed input is
reconstructed in norm. Nevertheless, $\|I-P_m\|=1$ for every $m$,
because the unit vector $e_{m+1}$ is completely discarded. There is no
operator-norm convergence to the identity.

Pointwise convergence of outputs and uniform control over all unit inputs
are different assertions. A finite successful experiment establishes
neither infinite convergence statement by itself.

## 8. Numerical residuals and certified statements

For an invertible linear system $Ax=b$ and an approximation $\widehat x$,
the equation residual is $r=b-A\widehat x$. With exact $A$ and $b$,

```math
x-\widehat x=A^{-1}r,\qquad
\|x-\widehat x\|\le\|A^{-1}\|\,\|r\|.
```

For $A=\operatorname{diag}(1,1/1000)$ and
$b=(1,1/1000)^{\mathsf T}$, the true solution is $(1,1)^{\mathsf T}$.
The approximation $(1,0)^{\mathsf T}$ has residual
$(0,1/1000)^{\mathsf T}$ but solution error $(0,1)^{\mathsf T}$.
A small residual needs the inverse bound to control forward error.

When reporting numerical evidence, identify the arithmetic model, precision,
tested inputs, tolerance, and the argument connecting a computed residual
to the claimed error. Exact rational identities, bounded floating-point
checks, and formal statements support different conclusions. Use the
[verification guide](../VERIFICATION.md) and the
[binary-rounding example](../examples/09_BINARY_ROUNDING.md) for their scope.

For an iterative solver, the
[worked fixed-point calculation](DYNAMICS.md#7-turn-an-iteration-residual-into-a-solution-error-bound)
turns a next-iterate difference into a sufficient stopping condition. It
computes the inverse bound and shows a residual smaller than the actual
solution error.

## Try it: attain an operator bound

For $E=\begin{pmatrix}0&2\\3&0\end{pmatrix}$, which coordinate unit
vector attains its Euclidean operator norm? What happens to the other one?

**Answer.** $Ee_1=(0,3)^{\mathsf T}$ has length three and attains the
norm. $Ee_2=(2,0)^{\mathsf T}$ has length two. A bound can be sharp
without being attained on every test input.

[Previous: Recovery and repair](RECOVERY.md) · [Next: Polynomial and difference operators](POLYNOMIAL.md) · [All chapters](../OPERATOR_AUDIT.md#reference-chapters)
