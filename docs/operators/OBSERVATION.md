# Observation and recovery: a worked operator audit

[Operator guide](../OPERATOR_AUDIT.md) · [Recovery and repair](RECOVERY.md) · [Stability](STABILITY.md)

How many readings do you need to reconstruct a hidden state? What does an
extra reading check? How does measurement error change the answer? Follow
one three-coordinate system through all three questions. Each calculation
uses the same transition and observation maps, so the assumptions travel
with the calculation.

The arithmetic examples use rational numbers. The recovery identities also
hold over the real numbers; lengths and error bounds below use real spaces.
There is no unknown forcing in this model. Measurement errors enter the
readings, while the state follows its stated update exactly.

## 1. Specify the state, the update, and the reading

Let the initial state be $x_0=(u,v,w)^{\mathsf T}$. Update by
$x_{n+1}=Tx_n$ and read $y_n=Rx_n$ at integer times $n\ge0$, using

```math
\begin{aligned}
T&=\begin{pmatrix}1&1&0\\0&1&1\\0&0&1\end{pmatrix},\\
R&=\begin{pmatrix}1&0&0\end{pmatrix}.
\end{aligned}
```

Thus $T(u,v,w)=(u+v,v+w,w)$ and $y_n=RT^nx_0$. The full state has three
coordinates, but each reading is a scalar. Time zero is included: $y_0=Rx_0$.

Write $T=I+N$. Since $N^3=0$, the binomial expansion terminates:

```math
\begin{aligned}
T^n&=I+nN+\binom n2N^2,\\
y_n&=u+nv+\binom n2w\quad(n\ge0).
\end{aligned}
```

Here $\binom n2=n(n-1)/2$, including zero at $n=0,1$. The second coordinate
at time $j$ is $v+jw$. Summing those values for $j=0,\ldots,n-1$ gives
the same expression for the first coordinate at time $n$; at $n=0$, the
sum is empty.

For $x_0=(2,3,1)^{\mathsf T}$, keep the state and its reading separate:

| Time | Full state $T^nx_0$ | Reading $y_n$ |
|---|---|---|
| $0$ | $(2,3,1)^{\mathsf T}$ | $2$ |
| $1$ | $(5,4,1)^{\mathsf T}$ | $5$ |
| $2$ | $(9,5,1)^{\mathsf T}$ | $9$ |
| $3$ | $(14,6,1)^{\mathsf T}$ | $14$ |
| $4$ | $(20,7,1)^{\mathsf T}$ | $20$ |

**Audit question:** Are the readings from this same trajectory, at the
declared times? Changing the transition, inserting an unknown input, or
skipping a time changes the observation map.

## 2. Recover the initial state from three readings

Collect the readings at times $0,1,2$ into $Y_3=(y_0,y_1,y_2)^{\mathsf T}$.
The corresponding observation matrix is

```math
\mathcal O_3=\begin{pmatrix}R\\RT\\RT^2\end{pmatrix}
=\begin{pmatrix}1&0&0\\1&1&0\\1&2&1\end{pmatrix}.
```

Recover the coordinates by finite differences:

```math
\begin{aligned}
u&=y_0,\\
v&=y_1-y_0,\\
w&=y_2-2y_1+y_0.
\end{aligned}
```

Equivalently, $x_0=B_3Y_3$, where

```math
\begin{aligned}
B_3&=\begin{pmatrix}1&0&0\\-1&1&0\\1&-2&1\end{pmatrix},\\
B_3\mathcal O_3&=\mathcal O_3B_3=I_3.
\end{aligned}
```

These matrix identities establish recovery for every initial state in this
model. On the example readings $(2,5,9)$, they give $(2,3,1)$.

Two readings do not recover every initial state. The matrix
$\mathcal O_2=\begin{pmatrix}1&0&0\\1&1&0\end{pmatrix}$ kills
$e_3=(0,0,1)^{\mathsf T}$. Initial states zero and $e_3$ both give readings
$(0,0)$ at times $0,1$, but their readings at time $2$ are $0$ and $1$.
This is a collision witness for recovering either the whole initial state
or the next reading from those two values alone.

The number of readings depends on the requested answer. One reading already
gives $u$; two give $v$; three are needed for $w$ on the full state space.
The [row-space criterion](RECOVERY.md#3-linear-recovery-row-spaces-and-kernels)
applies to each requested row separately.

## 3. Turn observation history into a state

After three readings, the next reading is determined:

```math
y_{n+3}=3y_{n+2}-3y_{n+1}+y_n.
```

The third finite difference vanishes because $y_n$ is quadratic in $n$.
The history vector $H_n=(y_n,y_{n+1},y_{n+2})^{\mathsf T}$ therefore has
an autonomous update

```math
H_{n+1}=KH_n,\qquad
K=\begin{pmatrix}0&1&0\\0&0&1\\1&-3&3\end{pmatrix}.
```

The operator identity $\mathcal O_3T=K\mathcal O_3$ explains why this is
the same dynamics in history coordinates. In this example the history map
is invertible. More general summaries can support an exact update without
being invertible, as the [transfer chapter](TRANSFER.md#5-compression-and-exact-reduced-dynamics)
explains.

The subscript in $H_n$ names the first time in its window. That vector
becomes available after the reading at time $n+2$. The history update uses
three values already collected to predict the next one.

For $(2,5,9)$, the next reading is $3\cdot9-3\cdot5+2=14$. Then
$(5,9,14)$ predicts $20$. An update of the current reading alone would lose
the history needed for these calculations.

## 4. Put a bound on noisy reconstruction

Suppose the measured values are $z_j=y_j+\eta_j$, with a known bound
$|\eta_j|\le\delta$ for each reading, where $\delta\ge0$. No probability distribution or
independence assumption is used. Applying the same reconstruction formulas
gives the following worst-case bounds:

| Requested quantity | Error in the reconstructed quantity | Absolute bound |
|---|---|---|
| $u$ | $\eta_0$ | $\delta$ |
| $v$ | $\eta_1-\eta_0$ | $2\delta$ |
| $w$ | $\eta_2-2\eta_1+\eta_0$ | $4\delta$ |
| Next reading $y_3$ | $\eta_0-3\eta_1+3\eta_2$ | $7\delta$ |

Each bound comes from the sum of the absolute coefficients in its row.
Choosing the error signs to match that row attains its bound. The rows
can also attain all four absolute bounds together in the alternating-error
control below.

For $\delta=1/100$, use errors $(\delta,-\delta,\delta)$ on the example:

```math
(z_0,z_1,z_2)=(201/100,499/100,901/100).
```

The reconstructed initial state is $(201/100,149/50,26/25)^{\mathsf T}$.
Its $w$ coordinate is $1+4\delta$, and the predicted next reading is
$1407/100=14+7\delta$. Exact recovery with noiseless data and sensitivity
to noisy data are both visible in this one calculation.

## 5. Use a fourth reading as a consistency check

A fourth reading adds a compatibility equation for the same trajectory.
Write $Z=(z_0,z_1,z_2,z_3)^{\mathsf T}$ and define

```math
c=\begin{pmatrix}-1&3&-3&1\end{pmatrix},\qquad
\rho=cZ=z_3-3z_2+3z_1-z_0.
```

For exact readings, $\rho=0$. Under the per-reading error bound from
section 4, the triangle inequality gives $|\rho|\le8\delta$. A value
above this threshold is incompatible with the stated transition, sample
times, and error budget taken together.

With errors $(\delta,-\delta,\delta,-\delta)$ and $\delta=1/100$, the four
measured values are $(201/100,499/100,901/100,1399/100)^{\mathsf T}$.
They give $\rho=-2/25=-8\delta$, attaining the bound.

A zero residual does not identify the true state. Adding the same offset
$\delta$ to all four exact readings keeps $\rho=0$ and makes the data
agree with initial state $(u+\delta,v,w)^{\mathsf T}$. The check tests a
relation among readings; the measurement model controls their accuracy.

## 6. Fit all four readings under squared error

To use all four values to estimate the initial state, first state the fitting
criterion. For ordinary, equally weighted squared error, minimize
$\|Z-\mathcal O_4x\|_2^2$ over $x\in\mathbb R^3$, where

```math
\mathcal O_4=\begin{pmatrix}1&0&0\\1&1&0\\1&2&1\\1&3&3\end{pmatrix}.
```

The exact solution is $\widehat x=LZ$, with

```math
L=\begin{pmatrix}
19/20&3/20&-3/20&1/20\\
-4/5&2/5&3/5&-1/5\\
1/2&-1/2&-1/2&1/2
\end{pmatrix}.
```

Here is a direct check of the criterion. Multiplication gives

```math
\begin{aligned}
L\mathcal O_4&=I_3,\\
P=\mathcal O_4L&=I_4-\frac{c^{\mathsf T}c}{20}.
\end{aligned}
```

Since $cc^{\mathsf T}=20$ and $c\mathcal O_4=0$, $P$ is the Euclidean
orthogonal projector onto the attainable observation vectors. The residual
is $r=Z-PZ=c^{\mathsf T}\rho/20$. It is perpendicular to every vector
in the image of $\mathcal O_4$. Consequently, for any candidate $x$,

```math
\|Z-\mathcal O_4x\|_2^2
=\|r\|_2^2+\|\mathcal O_4(\widehat x-x)\|_2^2.
```

The second term is nonnegative and vanishes only at $x=\widehat x$, because
$\mathcal O_4$ is injective. This proves the stated minimization and its
uniqueness. It also gives $\|r\|_2^2=\rho^2/20$.

### Match the fitting criterion to the error budget

The row sums of absolute values in $L$ give a useful comparison under the
same per-reading bound $|\eta_j|\le\delta$:

| Initial coordinate | First-three-reading estimator | Four-reading squared-error estimator |
|---|---|---|
| $u$ | Error at most $\delta$ | Error at most $13\delta/10$ |
| $v$ | Error at most $2\delta$ | Error at most $2\delta$ |
| $w$ | Error at most $4\delta$ | Error at most $2\delta$ |

The fourth reading improves this estimator's worst-case bound for $w$,
while the bound for $u$ increases. A smaller sum of squared residuals does
not automatically optimize every coordinate's error bound.

For the four noisy values in section 5, the fitted initial state is
$(1003/500,749/250,1)^{\mathsf T}$. Its residual vector is
$(1/250,-3/250,3/250,-1/250)^{\mathsf T}$, with squared length $1/3125$.
The middle residuals have absolute value $3/250$, exceeding $\delta=1/100$.
Yet the original state $(2,3,1)$ fits each reading within $\delta$.
Thus minimizing the sum of squared residuals and requiring every residual
to stay within a prescribed interval are different fitting tasks. Choose
the criterion that expresses the actual measurement specification.

## 7. Change the sample times explicitly

Suppose readings are taken at times $0,2,4$. Their observation matrix is

```math
\mathcal O_{0,2,4}=\begin{pmatrix}1&0&0\\1&2&1\\1&4&6\end{pmatrix}.
```

For readings $(a,b,d)=(y_0,y_2,y_4)$, recovery becomes

```math
\begin{aligned}
u&=a,\\
w&=\frac{d-2b+a}{4},\\
v&=\frac{b-a}{2}-\frac{w}{2}.
\end{aligned}
```

For the same initial state, $(a,b,d)=(2,9,20)$ again gives $(u,v,w)=(2,3,1)$.
Under the same absolute error bound on each reading, the corresponding
bounds are $\delta$, $3\delta/2$, and $\delta$ for $u,v,w$.
The reconstruction matrix is

```math
B_{0,2,4}=\begin{pmatrix}1&0&0\\-5/8&3/4&-1/8\\1/4&-1/2&1/4\end{pmatrix}.
```

Its row sums of absolute values explain those bounds. The observations now
extend to time $4$ rather than time $2$. The comparison assumes the same
transition remains valid throughout that longer window and the same error
budget applies to each reading. Sampling times belong in the audit, alongside
the number of measurements.

## Try it: recover, restrict, and challenge the model

**Recover.** Readings at times $0,1,2$ are $(1,3,6)$. Find the initial state
and the next reading. If a fourth reading is $9$ and $\delta=1/10$, does
the four-reading consistency check pass?

**Answer.** The state is $(1,2,1)^{\mathsf T}$ and the predicted next
reading is $10$. The observed residual is $\rho=-1$, whose absolute value
exceeds $8\delta=4/5$. These four values cannot all satisfy the stated
transition and per-reading error bound.

**Restrict.** If the admissible initial states satisfy $w=0$, how many
noiseless readings recover the full admissible state?

**Answer.** Two: $u=y_0$ and $v=y_1-y_0$, with $w$ already specified.
The next reading is $2y_1-y_0$. The earlier two-reading obstruction used a
kernel direction outside this restricted state space.

**Challenge.** Can the fourth-reading check detect a constant offset shared
by every measurement?

**Answer.** No. The coefficients in $c$ sum to zero. Both the three-reading
and four-reading estimators interpret that offset as a change in $u$.

## Record and replay the audit

| Field | This calculation records |
|---|---|
| Admissible states | All real initial triples; the restricted exercise states its additional condition. |
| Dynamics and observations | The displayed $T$, the row $R$, and the declared sample times. |
| Exact reconstruction | $B_3\mathcal O_3=I_3$, with a two-reading kernel witness. |
| Retained memory | Three consecutive readings, updated by $K$. |
| Error model | An absolute bound on each reading; no distributional assumption. |
| Extra observation | A compatibility residual with bound $8\delta$. |
| Estimation criterion | Equally weighted squared error, with its projector identity and separate coordinate bounds. |
| Scope | This finite-dimensional model, its exact identities, and the specified finite check fixtures. |

Run `python -B examples/operator_observation.py` from a repository checkout.
The [exact program](../../examples/operator_observation.py) checks eight
finite example groups, including independent recurrence values, the inverse
and intertwining identities, all sign corners for the displayed noise bounds,
the projection residual, changed sample times, and the exercise controls.
The written derivations above supply the general identities under their
stated assumptions. This study adds no Lean declarations or new formal-review
status.

[Continue with recovery and repair](RECOVERY.md) · [Review stability and error bounds](STABILITY.md) · [Return to the operator guide](../OPERATOR_AUDIT.md)
