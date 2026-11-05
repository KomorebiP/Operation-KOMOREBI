# Polynomial and difference operators

[Operator guide](../OPERATOR_AUDIT.md) · [Packets and projectors](PACKETS.md) · [Transfer and compression](TRANSFER.md)

A change of polynomial coordinates carries an entire collection of operations
with it. This chapter follows that collection through one example, so that
the coordinate map, derivative, projector, product, and shift can be used
together. The source is the collection's
[roots-of-unity and falling-factorial study](../demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md).

Unless a different ring is named, work with finite polynomials over
$\mathbb Q$. The variables $z$ and $x$ name the source and target descriptions.
All sums below are finite on each input. The
[operator catalog](catalog/README.md) gives the wider reference and pinned
source links.

## 1. Falling-factorial coordinates

Write $b_0(x)=1$ and
$b_k(x)=x(x-1)\cdots(x-k+1)$ for $k\ge1$. Define the linear map

```math
\Phi:\mathbb Q[z]\longrightarrow\mathbb Q[x],\qquad
\Phi(z^k)=b_k(x).
```

Each $b_k$ is monic of degree $k$. The change of basis is therefore
unitriangular and invertible. For example,

```math
\Phi(z^3)=x^3-3x^2+2x,\qquad
\Phi^{-1}(x^3)=z+3z^2+z^3.
```

These equations describe opposite directions. The second follows from
$x^3=b_1+3b_2+b_3$. In general, second-kind Stirling numbers give
$x^n=\sum_k S(n,k)b_k(x)$, and signed first-kind Stirling numbers give
the inverse expansion of each $b_k$ in ordinary powers.

The map is linear, but it does not preserve ordinary multiplication:
$\Phi(z^2)=x(x-1)$ while $\Phi(z)^2=x^2$. A coordinate isomorphism
alone does not identify these two products.

**Use:** Choose $\Phi$ when falling degree is the useful address for an
operation or a packet. Keep the inverse direction explicit when converting
an ordinary polynomial into those coordinates.

## 2. Forward difference as a transported derivative

Let $D_z$ be ordinary differentiation in the source variable. In the target
description define the forward difference
$\Delta f(x)=f(x+1)-f(x)$. The basis identity

```math
\Delta b_k=k b_{k-1}\quad(k\ge1),\qquad \Delta b_0=0
```

proves $\Delta\Phi=\Phi D_z$ by linearity. Equivalently,

```math
\Delta=\Phi D_z\Phi^{-1}.
```

On $f(x)=x^3$, the transported calculation is

```math
D_z(z+3z^2+z^3)=1+6z+3z^2,
\qquad \Delta f=1+6x+3(x^2-x)=3x^2+3x+1.
```

Ordinary differentiation in the target variable gives $D_x f=3x^2$.
Both are valid operations, with different outputs. To transfer a derivative,
carry the operator through the chosen coordinate map.

## 3. Raising and degree operators

Multiplication by $z$ also transports. If $T_{-1}f(x)=f(x-1)$, then

```math
A=\Phi(z\,\cdot)\Phi^{-1},\qquad
(Af)(x)=x f(x-1),\qquad Ab_k=b_{k+1}.
```

Indeed, $x b_k(x-1)=b_{k+1}(x)$. Combining this raising operator with
the lowering operator $\Delta$ gives the degree operator

```math
N=A\Delta,\qquad (Nf)(x)=x\bigl(f(x)-f(x-1)\bigr),
\qquad Nb_k=k b_k.
```

Thus falling degree becomes an eigenvalue. For example, $Nb_3=3b_3$.
On each basis element,
$\Delta A b_k=(k+1)b_k$ and $A\Delta b_k=k b_k$, so

```math
\Delta A-A\Delta=I.
```

These are identities on the full polynomial space. A square matrix obtained
by dropping the highest raised degree has an additional boundary effect.
The raising map sends degree at most $d$ into degree at most $d+1$;
retain that extra degree before checking the commutator.

## 4. Coefficient selectors and roots-of-unity averaging

For an integer $m\ge2$ and $0\le r<m$, define

```math
P_r^{(m)}\!\left(\sum_k a_kz^k\right)
=\sum_{k\equiv r\pmod m}a_kz^k.
```

This is a coefficient selector. It satisfies
$P_rP_s=0$ for $r\ne s$, $P_r^2=P_r$, and $\sum_rP_r=I$.
Here the products equal to zero express algebraic disjointness, with no
inner product required.

Over a field containing a primitive $m$th root $\zeta_m$, with $m$ invertible,
the same selector can be realized by

```math
P_r^{(m)}g(z)=\frac1m\sum_{\ell=0}^{m-1}
\zeta_m^{-r\ell}g(\zeta_m^\ell z).
```

On $z^k$ the sum is one times $z^k$ when $k\equiv r\pmod m$,
and zero otherwise. This verifies the formula on every polynomial.
For parity, $P_0g=(g(z)+g(-z))/2$ and $P_1g=(g(z)-g(-z))/2$.
Applied to $g=z+3z^2+z^3$, these return $3z^2$ and $z+z^3$.

The coefficient selector is defined over any commutative ring. A particular
averaging formula additionally needs its roots of unity and denominators.

## 5. Transported projectors and a complete packet calculation

Transport the selector along with the coordinates:

```math
Q_r^{(m)}=\Phi P_r^{(m)}\Phi^{-1}.
```

Conjugation preserves the projector identities and reconstruction. Each
$Q_r$ selects falling degrees, so applying the ordinary-power selector
directly to the target polynomial performs a different task.

For $f=x^3$ and $m=2$, the complete calculation is

| Falling-degree packet | Polynomial | Value at $x=4$ |
|---|---|---|
| $Q_0f$ | $3b_2=3x^2-3x$ | $36$ |
| $Q_1f$ | $b_1+b_3=x^3-3x^2+3x$ | $28$ |
| Sum | $x^3$ | $64$ |

The ordinary even-power selector sends $x^3$ to zero. That is a useful
control for detecting a projector used in the wrong coordinates.

Refinement keeps the same meaning of degree. For example,
$Q_0^{(2)}=Q_0^{(4)}+Q_2^{(4)}$. Splitting a packet into all its finer
residue classes preserves the sum. Omitting a child leaves its explicit
polynomial as a residual.

## 6. Transported multiplication and its product rule

To retain source multiplication, define the target product

```math
f\star g=\Phi\bigl(\Phi^{-1}f\;\Phi^{-1}g\bigr).
```

It is associative, commutative, bilinear, and has unit $1$, because the
source product has those properties. In particular,
$b_a\star b_b=b_{a+b}$ and $x\star x=x(x-1)$.

Transporting the ordinary derivative's product rule gives

```math
\Delta(f\star g)=(\Delta f)\star g+f\star(\Delta g).
```

For $f=g=x$, both sides are $2x$. Ordinary multiplication has a different
rule:

```math
\Delta(fg)=(\Delta f)g+(T_1f)(\Delta g),\qquad
T_1f(x)=f(x+1).
```

In particular, $\Delta(x^2)=2x+1$. The extra term comes from the shift,
so the product must be named whenever a derivative rule is transferred.

The transported product also routes residue packets by addition:

```math
Q_r^{(m)}(f\star g)=
\sum_{\substack{0\le a,b<m\\a+b\equiv r\pmod m}}
(Q_a^{(m)}f)\star(Q_b^{(m)}g).
```

This follows by multiplying the source monomials: their degrees add.
It does not assert the same routing for ordinary target multiplication.

## 7. Translation carries information between packets

Since $T_1=I+\Delta$, a one-step shift has two kinds of transfer:
it retains a falling degree or lowers it by one. With residue subscripts
read modulo $m$,

```math
\Delta Q_s=Q_{s-1}\Delta,\qquad
Q_rT_1f=Q_rf+\Delta Q_{r+1}f.
```

For the two packets of $f=x^3$, their forward differences at four are
$\Delta Q_0f(4)=24$ and $\Delta Q_1f(4)=37$. Hence

| Order of operations | Even falling packet at four | Odd falling packet at four |
|---|---|---|
| Shift first, then project: $Q_rT_1f$ | $36+37=73$ | $28+24=52$ |
| Project first, then shift: $T_1Q_rf$ | $36+24=60$ | $28+37=65$ |

Both rows sum to $f(5)=125$, but their individual packet values differ.
Equality of the total does not establish equality of the component operators.
The commutator $(Q_rT_1-T_1Q_r)f$ has values $13$ and $-13$.

For a general rational shift $h$, the exact connection coefficients are

```math
T_hb_k(x)=\sum_{j=0}^k\binom{k}{j}b_{k-j}(h)b_j(x).
```

This is still finite on each polynomial. A nonnegative integer $h$ makes
$b_{k-j}(h)=0$ for $k-j>h$, giving a bounded number of allowed degree
shifts. Fractional or negative shifts need not have that same bandwidth.

## 8. Recover coordinates and check the coefficient ring

For $f=\sum_{k=0}^d a_kb_k$ over $\mathbb Q$, the Newton formula is

```math
a_k=\frac{\Delta^k f(0)}{k!}.
```

The identity follows by repeatedly applying
$\Delta b_j=j b_{j-1}$ and evaluating at zero. Terms with $j>k$
still contain a positive falling degree and vanish at zero; the term
$j=k$ contributes $k!$, while terms with $j<k$ have already been annihilated.

For $f=x^3$, the samples at $0,1,2,3$ are $0,1,8,27$. The difference
table starts as follows:

| Order | Difference row | First value divided by the factorial |
|---|---|---|
| $0$ | $0,1,8,27$ | $0$ |
| $1$ | $1,7,19$ | $1$ |
| $2$ | $6,12$ | $3$ |
| $3$ | $6$ | $1$ |

This recovers $\Phi^{-1}f=z+3z^2+z^3$.

Division by $k!$ is a condition on this formula. The integral, unitriangular
Stirling basis change remains invertible over any commutative ring. In
$\mathbb F_3[x]$, however, $b_3=x^3-x$ is a nonzero polynomial that
vanishes at all three field elements, and $\Delta^3=0$. Sampling those
three elements or dividing by $3!$ cannot recover every polynomial
coefficient.

There is also a spectral boundary. Over $\mathbb F_3$,
$Nb_0=0$ and $Nb_3=0$. Yet the even falling-degree selector satisfies
$Q_0^{(2)}b_0=b_0$ and $Q_0^{(2)}b_3=0$. A polynomial in $N$ acts
by the same scalar on both zero-eigenvalue vectors, so it cannot realize
that selector on degree at most three. The coefficient projector remains
defined while this proposed spectral realization fails.

## Try it: identify the incoming packet

Let $f=x^2$, use parity packets, and evaluate at $x=3$. Compute
$Q_0T_1f(3)$ and $T_1Q_0f(3)$.

**Answer.** Since $x^2=b_2+b_1$, the packets have values $6$ and $3$.
Their differences have values $6$ and $1$. Therefore
$Q_0T_1f(3)=6+1=7$, while $T_1Q_0f(3)=6+6=12$.
The incoming difference for the even output comes from the odd input packet.

## Sources and checks

For a scalar question about the same polynomial, continue with the
[worked integration covector](COMPOSITION.md#moment-covector). It carries
the integral of $x^3$ into falling-factorial coordinates and identifies the
error from pairing those coefficients with an unchanged monomial moment row.

The [full worked study](../demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md)
provides the longer derivations, exact transfer tables, refinement examples,
and characteristic-three obstruction. Run
`python -B examples/operator_guide.py` from the repository root for this
chapter's eight finite example groups, or run
`python -B examples/roots_unity_falling_factorial.py` for the broader study.

The [polynomial Lean companion](../LEAN_POLYNOMIAL_TRANSPORT.md) constructs
the rational falling-factorial equivalence and proves its concrete projector
laws, finite complex roots-of-unity average, transported product, and cyclic
packet convolution. Its existing scope does not include the concrete
difference, raising, translation, spectral, or characteristic-three arguments
given here. This chapter adds no Lean declarations.

[Back to the operator guide](../OPERATOR_AUDIT.md) · [Browse the operator catalog](catalog/README.md) · [Full polynomial study](../demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md)
