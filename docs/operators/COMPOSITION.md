# Worked operator compositions

[Operator guide](../OPERATOR_AUDIT.md) · [Operator catalog](catalog/README.md) · [Composition laws](catalog/RELATIONS.md)

A complete calculation often uses several operators and more than one
description of an intermediate object. These six worked routes show how to
carry the needed information from one stage to the next. Each route specifies
the maps, calculates an exact result, and changes one assumption or retained
quantity to expose a failure.

The examples use rational matrices, finite polynomials, finite measures, and
finite input sequences. The identities are explained alongside the calculations.
The [exact example program](../../examples/operator_compositions.py) checks the
displayed cases and their failure controls using rational arithmetic.

| What are you trying to calculate? | What must travel with the calculation? | Worked route |
|---|---|---|
| Compose maps stored in different coordinates | A bridge between the two middle descriptions | [Intermediate coordinates](#middle-chart-bridge) |
| Predict an observation after two operations | Each defect, carried through the appropriate map | [Coarse defects](#coarse-defect) |
| Measure the change in squared norm along a path | The metric and the vector at each stage | [Metric defects](#metric-defect) |
| Integrate a polynomial stored in another basis | The integration covector in that basis | [Moment coordinates](#moment-covector) |
| Change finite observations and integrate a product | The actual measure, including its correlations | [Finite measures](#finite-pushforward) |
| Process a signal in consecutive chunks | The complete continuation state | [Recursive filter state](#filter-state) |

For the individual definitions, use the seven [reference chapters](../OPERATOR_AUDIT.md#reference-chapters).
These calculations combine those definitions with the catalog laws.

<a id="middle-chart-bridge"></a>

## 1. Bridge the intermediate coordinates

**Task.** Compose two linear operations when the first operation's output
coordinates differ from the coordinates expected by the second.

Work with column vectors in $X=Y=Z=\mathbb Q^2$. The physical operations and
input are

```math
T=\begin{pmatrix}1&2\\0&1\end{pmatrix},\qquad
U=\begin{pmatrix}1&0\\1&1\end{pmatrix},\qquad
x=\begin{pmatrix}1\\2\end{pmatrix}.
```

In the physical coordinates, $Tx=(5,2)^{\mathsf T}$ and
$UTx=(5,7)^{\mathsf T}$. Keep the initial and final coordinates unchanged.
The first stored map describes its output by $y_C=Cy$, while the second
expects $y_D=Dy$, with

```math
C=\begin{pmatrix}2&0\\0&1\end{pmatrix},\qquad
D=\begin{pmatrix}1&1\\0&1\end{pmatrix}.
```

Both coordinate maps are invertible. The stored matrices are therefore

```math
\widehat T=CT=\begin{pmatrix}2&4\\0&1\end{pmatrix},\qquad
\widehat U=UD^{-1}=\begin{pmatrix}1&-1\\1&0\end{pmatrix}.
```

The necessary middle bridge converts $C$ coordinates to $D$ coordinates:

```math
R=DC^{-1}=\begin{pmatrix}1/2&1\\0&1\end{pmatrix}.
```

| Step | Meaning | Value |
|---|---|---|
| $\widehat T x$ | First output, stored in $C$ coordinates | $(10,2)^{\mathsf T}$ |
| $R\widehat T x$ | The same intermediate vector, in $D$ coordinates | $(7,2)^{\mathsf T}$ |
| $\widehat U R\widehat T x$ | Final physical output | $(5,7)^{\mathsf T}$ |

The agreement holds for every input because

```math
\widehat U R\widehat T
=UD^{-1}(DC^{-1})CT
=UT
=\begin{pmatrix}1&2\\1&3\end{pmatrix}.
```

**Failure control.** Omitting $R$ gives
$\widehat U\widehat T x=(8,10)^{\mathsf T}$. Every matrix is $2$ by $2$,
so matrix dimensions alone do not expose the mismatch. The two intermediate
coordinate systems describe the same physical space, but assign different
vectors of coefficients to its elements.

When both stored maps use the same middle chart, $D=C$ and the bridge is the
identity. More general analysis and synthesis presentations have their own
bridge, as described in the catalog.

**Continue with:** [Presentation bridge, REL-02](catalog/RELATIONS.md#rel-02) ·
[Coordinate transport, REL-03](catalog/RELATIONS.md#rel-03) ·
[OP-020](catalog/A_STRUCTURAL.md#op-020) ·
[OP-171](catalog/A_STRUCTURAL.md#op-171) ·
[Transfer and compression](TRANSFER.md#4-transport-between-different-coordinate-spaces).

<a id="coarse-defect"></a>

## 2. Carry coarse defects through a composition

**Task.** Compare a two-stage operation with a proposed rule on retained
observations, and account for the difference at each stage.

Let $q:\mathbb Q^2\to\mathbb Q$ retain the coordinate sum. Choose

```math
q=\begin{pmatrix}1&1\end{pmatrix},\qquad
T=\operatorname{diag}(2,3),\qquad
U=\operatorname{diag}(3,2),\qquad
\overline T=2,\quad \overline U=3.
```

The bars name proposed scalar rules on the observations. Define their defects
as maps on the full input space:

```math
E_T=qT-\overline Tq=\begin{pmatrix}0&1\end{pmatrix},\qquad
E_U=qU-\overline Uq=\begin{pmatrix}0&-1\end{pmatrix}.
```

For the composed scalar candidate $\overline U\overline T$, insert and subtract
$\overline UqT$ to obtain

```math
\begin{aligned}
E_{UT}
&=qUT-\overline U\overline Tq\\
&=(qU-\overline Uq)T+\overline U(qT-\overline Tq)\\
&=(E_U)T+\overline U E_T.
\end{aligned}
```

The two contributions are

```math
(E_U)T=\begin{pmatrix}0&-3\end{pmatrix},\qquad
\overline U E_T=\begin{pmatrix}0&3\end{pmatrix}.
```

They cancel, giving $E_{UT}=0$. The full composite is $UT=6I$, so scalar
multiplication by $6$ gives its exact observation for every input.

For $x=(1,2)^{\mathsf T}$, the cancellation is visible in the complete path:

| Stage | Full state | Actual coordinate sum | Candidate scalar path | Actual minus candidate |
|---|---|---:|---:|---:|
| Initial | $(1,2)^{\mathsf T}$ | $3$ | $3$ | $0$ |
| After $T$ | $(2,6)^{\mathsf T}$ | $8$ | $6$ | $2$ |
| After $UT$ | $(6,12)^{\mathsf T}$ | $18$ | $18$ | $0$ |

**Failure control.** Exactness of the composite does not establish exactness
of the individual stages. The vector $w=(1,-1)^{\mathsf T}$ lies in
$\ker q$, but $qTw=-1$ and $qUw=1$. Neither $T$ nor $U$ preserves that
kernel, so neither has an exact update depending only on $q(x)$ for every
input. Their composite does.

The transport factors in the defect formula are also necessary. Replace $U$
by $U'=\operatorname{diag}(3,4)$ and retain $\overline U'=3$. Now

```math
E_{U'}=\begin{pmatrix}0&1\end{pmatrix},\qquad
E_{U'T}=E_{U'}T+3E_T=\begin{pmatrix}0&6\end{pmatrix}.
```

The actual composite defect at $x$ is $12$. Plainly adding $E_{U'}+E_T$
would give $4$ at that input, because it omits where the second defect is
evaluated and how the first defect propagates.

An independently chosen scalar rule for the full composite needs a further
term. If the original $UT=6I$ is assigned the candidate $\overline{UT}=5$,
then

```math
qUT-\overline{UT}q
=(E_U)T+\overline U E_T+
(\overline U\overline T-\overline{UT})q=q.
```

Its defect at $x$ is $3$. Always specify whether the coarse composite is the
product of the stage candidates or a separately proposed rule.

**Continue with:** [Coarse defect composition, REL-10](catalog/RELATIONS.md#rel-10) ·
[Coarse descent, REL-09](catalog/RELATIONS.md#rel-09) ·
[OP-121](catalog/G_DYNAMICS.md#op-121) ·
[OP-184](catalog/I_COMPUTATIONAL.md#op-184) ·
[Recovery and repair](RECOVERY.md).

<a id="metric-defect"></a>

## 3. Pull a metric defect back to the input

**Task.** Account for the change in squared norm after two operations.

For real finite-dimensional spaces with positive-definite metric matrices
$Q_X,Q_Y,Q_Z$, define

```math
\mathcal E(T)=T^{\mathsf T}Q_YT-Q_X,\qquad
\mathcal E(U)=U^{\mathsf T}Q_ZU-Q_Y.
```

The scalar $v^{\mathsf T}\mathcal E(T)v$ is the change in squared norm
from $v$ to $Tv$. Use the same $Q_Y$ in both expressions. Expanding the
composite gives

```math
\begin{aligned}
\mathcal E(UT)
&=T^{\mathsf T}U^{\mathsf T}Q_ZUT-Q_X\\
&=(T^{\mathsf T}Q_YT-Q_X)
 +T^{\mathsf T}(U^{\mathsf T}Q_ZU-Q_Y)T\\
&=\mathcal E(T)+T^{\mathsf T}\mathcal E(U)T.
\end{aligned}
```

The pullback places the second defect in the initial input space. Its
contribution is evaluated at $Tv$:
$v^{\mathsf T}T^{\mathsf T}\mathcal E(U)Tv
=(Tv)^{\mathsf T}\mathcal E(U)(Tv)$.

Take Euclidean metrics $Q_X=Q_Y=Q_Z=I$ and

```math
T=\operatorname{diag}(2,1),\qquad
U=\operatorname{diag}(1/2,3),\qquad
v=\begin{pmatrix}1\\1\end{pmatrix}.
```

The matrices in the identity are

```math
\begin{aligned}
\mathcal E(T)&=\operatorname{diag}(3,0),\\
\mathcal E(U)&=\operatorname{diag}(-3/4,8),\\
T^{\mathsf T}\mathcal E(U)T&=\operatorname{diag}(-3,8),\\
\mathcal E(UT)&=\operatorname{diag}(0,8).
\end{aligned}
```

| Stage | Vector | Squared norm | Change from the previous stage |
|---|---|---:|---:|
| Initial | $(1,1)^{\mathsf T}$ | $2$ | — |
| After $T$ | $(2,1)^{\mathsf T}$ | $5$ | $3$ |
| After $UT$ | $(1,3)^{\mathsf T}$ | $10$ | $5$ |

The total change is $3+5=8$, also given by
$v^{\mathsf T}\mathcal E(UT)v=8$. In the first coordinate, the expansion
by $2$ and contraction by $1/2$ cancel exactly.

**Failure control.** Adding the residual matrices without the pullback gives
$\mathcal E(T)+\mathcal E(U)=\operatorname{diag}(9/4,8)$.
At $v$ this predicts $41/4$, rather than $8$. It evaluates the second change
at the original vector instead of the intermediate vector.

These defects are signed changes of squared norm. Their matrices need not
be positive-definite or positive-semidefinite. A zero composite defect can
include cancellation between expansion and contraction.

**Continue with:** [Quadratic metric defect, REL-14](catalog/RELATIONS.md#rel-14) ·
[OP-189](catalog/K_METRICS.md#op-189) ·
[OP-192](catalog/K_METRICS.md#op-192) ·
[Stability and numerical meaning](STABILITY.md).

<a id="moment-covector"></a>

## 4. Carry an integration covector into another basis

**Task.** Integrate a polynomial from its falling-factorial coefficients.

Let $p\in\mathbb Q[x]$ have degree at most $3$. Use the ordered bases
$(1,x,x^2,x^3)$ and $(b_0,b_1,b_2,b_3)$, where

```math
b_0=1,\qquad b_1=x,\qquad
b_2=x^2-x,\qquad b_3=x^3-3x^2+2x.
```

Let $a$ be the falling-basis coefficient column and $c$ the ordinary-power
coefficient column for the same polynomial. Then $c=Ba$, where each column
of $B$ contains one $b_j$ in ordinary powers:

```math
B=\begin{pmatrix}
1&0&0&0\\
0&1&-1&2\\
0&0&1&-3\\
0&0&0&1
\end{pmatrix}.
```

On the interval $[0,1]$ with constant density $1$, the integration covector
for ordinary coefficients is

```math
m=\begin{pmatrix}1&1/2&1/3&1/4\end{pmatrix},\qquad
\int_0^1p(x)\,dx=mc.
```

Substitute $c=Ba$. The correct integration row for falling coefficients is

```math
mB=\begin{pmatrix}1&1/2&-1/6&1/4\end{pmatrix},\qquad
\int_0^1p(x)\,dx=(mB)a.
```

Each entry is the exact integral of its corresponding basis polynomial:

| Basis polynomial | Integral on $[0,1]$ |
|---|---:|
| $b_0=1$ | $1$ |
| $b_1=x$ | $1/2$ |
| $b_2=x^2-x$ | $1/3-1/2=-1/6$ |
| $b_3=x^3-3x^2+2x$ | $1/4-1+1=1/4$ |

The four basis values determine the functional on the entire declared
degree-at-most-$3$ space by linearity.

For the same $p=x^3$ used in the [polynomial chapter](POLYNOMIAL.md),

```math
a=\begin{pmatrix}0\\1\\3\\1\end{pmatrix},\qquad
Ba=\begin{pmatrix}0\\0\\0\\1\end{pmatrix},\qquad
(mB)a=\frac12-\frac12+\frac14=\frac14.
```

**Failure control.** Applying the unchanged ordinary-power row to the falling
coefficients gives $ma=1/2+1+1/4=7/4$. The polynomial and its coefficients
were specified correctly; the functional was expressed in the wrong basis.

The direction of the matrix matters. Because $B$ maps the stored coefficients
$a$ to the coefficients expected by $m$, the required row is $mB$.
It is the same rule as the covector identity $(\ell A)x=\ell(Ax)$.

**Continue with:** [Covector pullback, REL-08](catalog/RELATIONS.md#rel-08) ·
[OP-172](catalog/C_COORDINATES.md#op-172) ·
[OP-194](catalog/L_INTEGRATION.md#op-194) ·
[Falling-factorial coordinates](POLYNOMIAL.md#1-falling-factorial-coordinates).

<a id="finite-pushforward"></a>

## 5. Push forward a measure and retain its correlations

**Task.** Change a finite observation map, then calculate an integral involving
two observations.

Let $\delta_t$ denote a unit point mass at $t$. Start with

```math
\mu=\frac12\delta_0+\frac12\delta_1,\qquad
\phi(t)=1+2t,\qquad
\nu=\phi_*\mu=\frac12\delta_1+\frac12\delta_3.
```

The pushforward moves the atoms through $\phi$ and keeps their weights.
For $p(y)=y^2$, calculate on either side:

```math
I_\nu p=\frac12(1^2+3^2)=5,
\qquad
I_\mu(p\circ\phi)
=\frac12\bigl((1+2\cdot0)^2+(1+2\cdot1)^2\bigr)=5.
```

For a finite atomic measure $\mu=\sum_iw_i\delta_{t_i}$, the reason is simply
that both sides of $I_{\phi_*\mu}p=I_\mu(p\circ\phi)$ equal
$\sum_iw_i p(\phi(t_i))$. Injectivity is unnecessary: when images coincide,
their weights add at the same target atom.

Now explicitly choose the product measure $\nu\otimes\nu$ on pairs $(y,z)$.
It has four atoms, each with weight $1/4$:

| Atom | $yz$ | Weighted contribution |
|---|---:|---:|
| $(1,1)$ | $1$ | $1/4$ |
| $(1,3)$ | $3$ | $3/4$ |
| $(3,1)$ | $3$ | $3/4$ |
| $(3,3)$ | $9$ | $9/4$ |

Thus $I_{\nu\otimes\nu}(yz)=4$. Partial integration retains the remaining
variable:

```math
(I_\nu^{(z)}(yz))(y)=\frac12(y+3y)=2y,
\qquad I_\nu^{(y)}(2y)=\frac12(2+6)=4.
```

This finite product identity follows by summing the weighted rows of the
four-atom table. There is no infinite interchange of limits in this example.

**Failure control.** Observe the same original point twice instead:

```math
\gamma=(\phi,\phi)_*\mu
=\frac12\delta_{(1,1)}+\frac12\delta_{(3,3)}.
```

Both marginals of $\gamma$ are still $\nu$, but

```math
I_\gamma(yz)=\frac12(1+9)=5.
```

Replacing $\gamma$ by the product of its marginals would change the answer
from $5$ to $4$. The product calculation models two independent draws;
$\gamma$ models two observations of the same draw. The marginals alone do
not retain that relationship.

**Continue with:** [Pushforward duality, REL-23](catalog/RELATIONS.md#rel-23) ·
[Finite Fubini, REL-27](catalog/RELATIONS.md#rel-27) ·
[OP-193](catalog/L_INTEGRATION.md#op-193) ·
[OP-195](catalog/L_INTEGRATION.md#op-195) ·
[OP-196](catalog/L_INTEGRATION.md#op-196).

<a id="filter-state"></a>

## 6. Continue a recursive filter across a chunk boundary

**Task.** Process a finite input stream in chunks while preserving the output
of one uninterrupted run.

Use the fixed rational recurrence

```math
y_n=x_n+\frac12x_{n-1}+\frac13y_{n-1},\qquad
x_{-1}=y_{-1}=0,
```

with input $(x_0,x_1,x_2,x_3)=(2,1,0,0)$. Its complete calculation is

| $n$ | $x_n$ | $x_{n-1}$ | $y_{n-1}$ | $y_n$ |
|---:|---:|---:|---:|---:|
| $0$ | $2$ | $0$ | $0$ | $2$ |
| $1$ | $1$ | $2$ | $2$ | $8/3$ |
| $2$ | $0$ | $1$ | $8/3$ | $25/18$ |
| $3$ | $0$ | $0$ | $25/18$ | $25/54$ |

For a chunk beginning at index $n$, the continuation state is
$s_{n-1}=(x_{n-1},y_{n-1})^{\mathsf T}$. Processing the next input uses

```math
s_n=
\begin{pmatrix}0&0\\1/2&1/3\end{pmatrix}s_{n-1}
+\begin{pmatrix}1\\1\end{pmatrix}x_n.
```

The second state component is the output. This update is linear in the pair
consisting of the old state and the new input. For a fixed nonzero old state,
the next output is an affine function of the new input.

Split the input after $(2,1)$. The first chunk returns outputs $(2,8/3)$
and state $(1,8/3)^{\mathsf T}$. Starting the second chunk $(0,0)$ with
that state gives $(25/18,25/54)$. Concatenating the outputs reproduces the
uninterrupted run.

| State supplied to the second chunk | Its two outputs |
|---|---|
| Complete: $(1,8/3)^{\mathsf T}$ | $(25/18,25/54)$ |
| Output history only: $(0,8/3)^{\mathsf T}$ | $(8/9,8/27)$ |
| Input history only: $(1,0)^{\mathsf T}$ | $(1/2,1/6)$ |
| Reset: $(0,0)^{\mathsf T}$ | $(0,0)$ |

**Failure control.** Either component of the retained history contributes
to the first output after the boundary. Keeping only the previous output
loses the delayed input term. Keeping only the previous input loses the
recursive term. Resetting the state changes the problem being calculated.

For any finite input list, splitting and resuming with the full state agrees
with uninterrupted execution: at the boundary the state is identical, and
the recurrence produces the same next output and state at every subsequent
step. An empty chunk produces no output and preserves its supplied state.
The example program checks all five split positions of this four-input list,
including empty first and last chunks.

These are statements about exact finite execution with fixed coefficients
and declared initial state. Numerical error and long-run stability require
their own analysis.

**Continue with:** [Recursive filter continuation, REL-28](catalog/RELATIONS.md#rel-28) ·
[OP-063](catalog/C_COORDINATES.md#op-063) ·
[OP-205](catalog/E_SIGNAL.md#op-205) ·
[Retained memory](RECOVERY.md#7-hidden-state-and-retained-memory).

## Run the exact calculations

From a repository checkout, run:

```text
python -B examples/operator_compositions.py
```

The program checks the six displayed calculations, their matrix or functional
identities in the stated finite spaces, and the named failure controls. Its
checks use Python's standard library and exact fractions. The original
[164 catalog fixtures](catalog/CHECKS.md) remain a separate collection of
examples with their own identifiers and scope.

The worked inputs here specialize the catalog laws. For the earlier source
fixtures behind those constructions, see
[L08](catalog/CHECKS.md#l08),
[R03–R04](catalog/CHECKS.md#r03),
[R37–R38](catalog/CHECKS.md#r37),
[R53–R54](catalog/CHECKS.md#r53),
[R57–R61](catalog/CHECKS.md#r57),
[R73–R77](catalog/CHECKS.md#r73), and
[R83–R84](catalog/CHECKS.md#r83).
The [source register](catalog/SOURCES.md) identifies the pinned revisions.

[All reference chapters](../OPERATOR_AUDIT.md#reference-chapters) · [Operator catalog](catalog/README.md) · [Composition laws](catalog/RELATIONS.md)
