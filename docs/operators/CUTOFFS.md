# Finite cutoffs: boundary defects and safe compositions

A finite matrix can reproduce an operator on its retained inputs and still
give the wrong answer when operations are composed. An intermediate result
may leave the retained space and later return. This study calculates that
boundary effect, derives a sufficient padding rule, and follows the same
cutoff through a change of polynomial coordinates. A final finite-field
example shows why the coefficient field belongs in the audit.

Work over $\mathbb Q$ until section 7. Vectors list coefficients in increasing
degree, starting with the constant term. Composition acts from right to left.
The [polynomial reference](POLYNOMIAL.md) supplies the coordinate-transport
background; the [commutator reference](ALGEBRA.md#3-commutators) supplies the
notation $[A,B]=AB-BA$.

## 1. Define the finite space and its cutoff

Let $V_N$ contain the polynomials of degree at most $N$, where $N\ge0$,
and let $\pi_N$ discard all higher monomials. On the full polynomial space,
write $Df=f'$ and $Mf=zf$. Differentiation preserves $V_N$; multiplication
sends it into $V_{N+1}$. Define square finite operators by

```math
D_N=D|_{V_N},\qquad M_N=\pi_NM|_{V_N}.
```

For $N=3$, their coefficient matrices are

```math
\begin{gathered}
D_3=\begin{pmatrix}0&1&0&0\\0&0&2&0\\0&0&0&3\\0&0&0&0\end{pmatrix},\\
M_3=\begin{pmatrix}0&0&0&0\\1&0&0&0\\0&1&0&0\\0&0&1&0\end{pmatrix}.
\end{gathered}
```

The last column of $M_3$ is zero because multiplication sends $z^3$ to
$z^4$, which the cutoff discards. Record this projection as part of the
operation. The matrix represents multiplication followed by a cutoff.

## 2. Locate the commutator defect exactly

On the full polynomial space, the product rule gives $DM-MD=I$.
For a retained monomial $z^k$ with $k<N$, the same calculation works with
$D_N,M_N$. At $k=N$, however, $D_NM_Nz^N=0$ and
$M_ND_Nz^N=Nz^N$. If $P_N$ selects the coefficient of $z^N$, then

```math
[D_N,M_N]=I_{V_N}-(N+1)P_N.
```

Thus the defect is concentrated in one packet. At $N=3$, the commutator
is $\operatorname{diag}(1,1,1,-3)$.

For $f=1+2z+3z^2+4z^3$, the two finite compositions give

```math
\begin{aligned}
D_3M_3f&=1+4z+9z^2,\\
M_3D_3f&=2z+6z^2+12z^3,\\
[D_3,M_3]f&=1+2z+3z^2-12z^3.
\end{aligned}
```

The difference from $f$ is $-16z^3$, exactly $-4P_3f$.
A trace check catches an impossible matrix identity before a large test run:
finite square commutators have trace zero, while $I_{V_N}$ has nonzero
trace $N+1$ over $\mathbb Q$. The displayed correction has trace
$(N+1)-(N+1)=0$. This extends the reference's
[degree-two example](ALGEBRA.md#test-a-claimed-identity-on-its-actual-space).

## 3. Retain the intermediate degree before lowering

To compute $DM$ on $V_3$, retain degree four after multiplication and
differentiate that result back into $V_3$. The maps have matching rectangular
types $M:V_3\to V_4$ and $D:V_4\to V_3$.
For $MD$, differentiation first lands in $V_2$, and multiplication returns
to $V_3$. These compositions have matrices

```math
\begin{aligned}
(DM)|_{V_3}&=\operatorname{diag}(1,2,3,4),\\
(MD)|_{V_3}&=\operatorname{diag}(0,1,2,3).
\end{aligned}
```

Their difference is exactly $I_{V_3}$. Retaining the raised degree restores
the intended full-space calculation.

For the polynomial above, the intermediate product contains $4z^4$.
Its derivative contributes $16z^3$, explaining the missing term in section 2.
Projecting after the final composition and projecting after every factor
are different algorithms. Their difference is the same kind of
[leave-and-return transfer](TRANSFER.md#two-updates-can-leave-and-return)
seen in compressed dynamics.

## 4. Budget padding for an entire operator word

One extra degree is sufficient for $DM$. For $D^2M^2$, the input can rise
by two degrees before either derivative acts. On $V_3$,

```math
\begin{aligned}
(D^2M^2)|_{V_3}&=\operatorname{diag}(2,6,12,20),\\
D_3^2M_3^2&=\operatorname{diag}(2,6,0,0).
\end{aligned}
```

Keeping only one extra degree still loses the result on $z^3$:
$z^3\mapsto z^4\mapsto z^5$ leaves $V_4$ before the derivatives
return it as $20z^3$. Retaining $V_5$ is sufficient. On the same $f$,
the full result has coefficient vector $(2,12,36,80)^{\mathsf T}$,
while the unpadded result is $(2,12,0,0)^{\mathsf T}$.

For a general finite word in $D$ and $M$, read its factors in application
order, from right to left. Start a running degree change at zero; add one
for $M$ and subtract one for $D$. Let $h$ be the maximum of zero and all
these running changes. Starting from $V_N$, keeping $V_{N+h}$ throughout
is sufficient to compute $\pi_NWf$ exactly, with $\pi_N$ applied only
at the end.

| Word $W$ | Application order | Running changes | Sufficient $h$ |
|---|---|---|---:|
| $DM$ | $M,D$ | $1,0$ | $1$ |
| $MD$ | $D,M$ | $-1,0$ | $0$ |
| $D^2M^2$ | $M,M,D,D$ | $1,2,1,0$ | $2$ |
| $MDMD$ | $D,M,D,M$ | $-1,0,-1,0$ | $0$ |

Each multiplication increases degree by at most one, and each derivative
decreases the degree of a nonconstant polynomial by one. A derivative that
kills the polynomial leaves zero for subsequent factors. These facts prove
the stated bound on every intermediate degree. The rule is sufficient;
annihilation of a particular input can make less storage possible.

## 5. Transport the boundary together with the operators

Let $C$ be the degree-three matrix of the map $\Phi(z^k)=b_k(x)$ from
the [polynomial chapter](POLYNOMIAL.md#1-falling-factorial-coordinates).
Its columns are the ordinary $x$ coefficients of $b_0,b_1,b_2,b_3$:

```math
C=\begin{pmatrix}1&0&0&0\\0&1&-1&2\\0&0&1&-3\\0&0&0&1\end{pmatrix}.
```

Set $\widehat D=CD_3C^{-1}$ and $\widehat M=CM_3C^{-1}$.
The first is forward difference on degree at most three. Conjugating the
commutator carries its defect as well:

```math
\begin{gathered}
\left[\widehat D,\widehat M\right]=I-4\widehat P,\\
\widehat P=CP_3C^{-1},\\
\widehat P=\begin{pmatrix}0&0&0&0\\0&0&0&2\\0&0&0&-3\\0&0&0&1\end{pmatrix}.
\end{gathered}
```

The boundary packet is still rank one, but it is no longer a diagonal
selector in ordinary $x$ coefficients. It sends $x^3$ to
$b_3(x)=x^3-3x^2+2x$.

The truncation itself also has to follow the representation. Full transported
raising sends $x^3$ to $x(x-1)^3$. The operator $\widehat M$ removes its
$b_4$ component and gives $3x^3-8x^2+5x$. Simply deleting its ordinary
$x^4$ term instead gives $-3x^3+3x^2-x$. These are different projections
onto degree at most three. A coordinate change must carry the retained and
discarded packets along with the operator matrix.

## 6. Distinguish an interior identity from a uniform bound

Use the coefficient infinity norm
$\|\sum_{k=0}^N a_kz^k\|_{\mathrm{coeff},\infty}=\max_k|a_k|$.
The defect $E_N=[D_N,M_N]-I$ satisfies

```math
\|E_N\|_{\mathrm{coeff},\infty}=N+1.
```

The upper bound follows from $E_N=-(N+1)P_N$, and the unit input $z^N$
attains it. For a fixed polynomial of degree $d$, the defect vanishes
whenever $N>d$. This eventual agreement on each fixed polynomial coexists
with growing worst-case error over the unit inputs allowed at each cutoff.
The distinction parallels the
[pointwise and uniform convergence discussion](STABILITY.md#7-finite-truncation-and-infinite-convergence).

The coefficient norm also depends on the description. In ordinary $x$
coefficients, the transported defect is $-4\widehat P$, with induced
infinity norm $12$. The unit input $x^3$ attains it, producing
$-4b_3=-4x^3+12x^2-8x$. The original coefficient norm gives defect norm
$4$ at $N=3$. Comparing these numbers requires recording which coordinate
norm is used; the [coordinate-conditioning reference](STABILITY.md#4-coordinate-conditioning)
explains the general norm bound. The boundary's rank and its exact
transport identity remain unchanged.

## 7. Check the coefficient field before using the trace obstruction

Over $\mathbb Q$, ordinary differentiation does not descend to
the quotient $\mathbb Q[z]/(z^4)$: the equal classes of $0$ and $z^4$
would have derivatives $0$ and $4z^3$, which are different classes.
The square matrix $D_3$ differentiates the selected degree-three
representative. This is a well-defined linear map on $V_3$, with the
boundary defect already calculated.

Now let $p$ be prime and work in $\mathbb F_p[z]/(z^p)$, with basis
$1,z,\ldots,z^{p-1}$. Differentiation preserves the defining ideal because

```math
D(z^pq)=p z^{p-1}q+z^pDq=z^pDq.
```

It therefore descends to the quotient, as multiplication does. Reducing the
finite commutator identity modulo $p$ at $N=p-1$ gives

```math
[D_{p-1},M_{p-1}]=I-pP_{p-1}=I.
```

There is no trace contradiction: the trace of this $p$-dimensional identity
is $p=0$ in the field. The field changes the conclusion. For comparison,
over $\mathbb F_3$ at cutoff $N=3$, the boundary coefficient is
$N+1=4=1$, so the commutator is not the four-dimensional identity.
State both the cutoff and the field before interpreting a finite check.

## Try it: find the boundary before testing

1. What does $[D_3,M_3]$ do to $z^2$ and to $z^3$?
2. How much padding does the running-change rule assign to $D^3M^2$?
3. In characteristic five, what happens to the commutator at cutoff four?
   What does the transported boundary packet do to $x^3$?

**Answers.** (1) The outputs are $z^2$ and $-3z^3$.
(2) The application order is $M,M,D,D,D$, whose largest positive change
is two. (3) The boundary coefficient is five, which vanishes, so the
commutator is the identity. The transported packet sends $x^3$ to $b_3$.

## Completed audit record

| Item | Recorded answer |
|---|---|
| Space | $V_N$ over $\mathbb Q$, with the finite-field change named separately. |
| Finite raising | Multiplication followed by the stated cutoff. |
| Commutator defect | $-(N+1)P_N$ relative to the full-space identity. |
| Safe composition | Retain all intermediate degrees using the running-change bound, then project at the end. |
| Coordinate transport | Conjugate the operators and the boundary packet together. |
| Stability statement | The defect vanishes eventually on each fixed polynomial but has coefficient-norm size $N+1$ at cutoff $N$. |
| Evidence | Seven finite exact example groups and the elementary arguments above; no new Lean or infinite-dimensional operator-domain claim. |

Run `python -B examples/operator_cutoffs.py` from a repository checkout.
The [exact check program](../../examples/operator_cutoffs.py) checks the
commutator at cutoffs zero through six. It tests every word of length at
most five at cutoffs zero through five, comparing padded matrix composition
with independent polynomial operations on every retained basis vector.
It also checks the transported example and finite-field controls at primes
$2,3,5,7$. These bounded checks support the stated calculations; the general
padding and characteristic arguments are supplied in the text.

[Algebra reference](ALGEBRA.md) · [Polynomial reference](POLYNOMIAL.md) ·
[Packets reference](PACKETS.md) · [All chapters](../OPERATOR_AUDIT.md#reference-chapters)
