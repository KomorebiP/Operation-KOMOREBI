# Stable updates and transient growth: a worked operator audit

A repeated update can eventually send every initial state to zero while
amplifying some states during its first few steps. This study follows one
two-coordinate system through that distinction, a change of norm, an energy
identity, a discarded interaction, and disturbances added at every update.
It ends with a stopping test for an affine iteration.

Start with [operator norms](STABILITY.md#1-vector-norms-and-induced-operator-norms)
and [source-to-target blocks](TRANSFER.md#1-source-to-target-blocks) if those terms
are new. Every matrix below is real; vectors are columns; time is a
nonnegative integer. The calculations use exact rational arithmetic.

## 1. Specify the update and the question

Let

```math
\begin{gathered}
x_{n+1}=Ax_n,\\
A=\begin{pmatrix}1/2&2\\0&1/2\end{pmatrix},\\
x_0=e_2=\begin{pmatrix}0\\1\end{pmatrix}.
\end{gathered}
```

In scalar coordinates, the rule is
$u_{n+1}=u_n/2+2v_n$ and $v_{n+1}=v_n/2$.
The second coordinate decays at each step but also feeds the first.
Both eigenvalues are $1/2$. The matrix is nonnormal in the Euclidean
inner product: $A^{\mathsf T}A\ne AA^{\mathsf T}$.

There are several separate questions to answer:

| Question | Quantity to inspect |
|---|---|
| Does every unforced trajectory tend to zero? | $A^nx$ as $n\to\infty$. |
| Can an initial perturbation grow before it decays? | $\|A^n\|$ in the specified norm. |
| What happens to errors injected repeatedly? | A sum of propagated disturbances. |
| Does a small iteration residual imply a small solution error? | The inverse of the fixed-point equation. |

An eigenvalue calculation alone does not answer all four. In this example,
the power formula below proves the first assertion and quantifies the second.

## 2. Calculate the whole trajectory

Write $A=I/2+N$, where
$N=\begin{pmatrix}0&2\\0&0\end{pmatrix}$ and $N^2=0$.
The binomial expansion therefore terminates:

```math
\begin{gathered}
A^n=2^{-n}\begin{pmatrix}1&4n\\0&1\end{pmatrix},\\
x_n=2^{-n}\begin{pmatrix}4n\\1\end{pmatrix}.
\end{gathered}
```

The formula includes $n=0$. Since $n2^{-n}\to0$, every entry of $A^n$
tends to zero, so every fixed initial state decays. That limit is a
consequence of the formula, beyond the finite checks accompanying this page.

| $n$ | $x_n$ | $\|x_n\|_\infty$ | $\|x_n\|_2^2$ |
|---:|---|---:|---:|
| $0$ | $(0,1)^{\mathsf T}$ | $1$ | $1$ |
| $1$ | $(2,1/2)^{\mathsf T}$ | $2$ | $17/4$ |
| $2$ | $(2,1/4)^{\mathsf T}$ | $2$ | $65/16$ |
| $3$ | $(3/2,1/8)^{\mathsf T}$ | $3/2$ | $145/64$ |
| $4$ | $(1,1/16)^{\mathsf T}$ | $1$ | $257/256$ |
| $5$ | $(5/8,1/32)^{\mathsf T}$ | $5/8$ | $401/1024$ |

For the induced infinity norm, the largest absolute row sum gives the exact
answer for every $n\ge0$:

```math
\|A^n\|_\infty=\frac{1+4n}{2^n}.
```

The vector $(1,1)^{\mathsf T}$ attains that row sum. The norm is $1$ at
time zero, reaches $5/2$ at time one, and then decreases: for $n\ge1$,
the ratio of successive values is $(4n+5)/(8n+2)<1$.
Thus the largest possible amplification over all times in this norm is
$5/2$, even though every trajectory eventually decays.

## 3. Choose a norm that makes contraction visible

Set $y=Cx$, with

```math
\begin{gathered}
C=\operatorname{diag}(1,8),\\
B=CAC^{-1}=\begin{pmatrix}1/2&1/4\\0&1/2\end{pmatrix}.
\end{gathered}
```

The induced infinity norm of $B$ is $3/4$. Equivalently, the weighted
maximum norm $\|x\|_C=\|Cx\|_\infty=\max(|u|,8|v|)$ satisfies

```math
\begin{gathered}
\|Ax\|_C\le\frac34\|x\|_C,\\
\|A^nx\|_\infty\le8(3/4)^n\|x\|_\infty.
\end{gathered}
```

The second bound follows from
$\|x\|_\infty\le\|x\|_C\le8\|x\|_\infty$.
It proves decay, but is less sharp than the exact power norm. At $n=1$
it gives an upper bound of $6$ where the exact norm is $5/2$.

This norm measures a different quantity from the original Euclidean length.
For $x_0=e_2$, the weighted maximum decreases from $8$ to $4$ in one
step while the Euclidean length increases. If the task is to express the
*same* Euclidean geometry in $y$ coordinates, its metric must instead be
$C^{-\mathsf T}C^{-1}=\operatorname{diag}(1,1/64)$, as in the
[coordinate-and-metric rule](BASICS.md#carry-the-inner-product-with-the-coordinates).
State which quantity the task actually bounds.

Disturbances also change coordinates: an added vector $d$ becomes $Cd$.
A smaller update norm does not permit keeping an untransformed disturbance
budget. Section 6 compares the resulting bounds explicitly.

## 4. Account for a decreasing quadratic energy

Another useful norm comes from the symmetric matrix

```math
\begin{gathered}
W=\begin{pmatrix}4/3&16/9\\16/9&356/27\end{pmatrix},\\
E(x)=x^{\mathsf T}Wx.
\end{gathered}
```

Completing the square shows that it is positive-definite:

```math
\begin{aligned}
E(u,v)&=\frac43\left(u+\frac43v\right)^2\\
&\quad+\frac{292}{27}v^2.
\end{aligned}
```

To find this matrix, substitute
$W=\begin{pmatrix}a&b\\b&c\end{pmatrix}$ into
$W-A^{\mathsf T}WA=I$. The three scalar equations are
$3a/4=1$, $3b/4=a$, and $3c/4=4a+2b+1$.
They give the displayed entries. Direct multiplication then gives

```math
\begin{gathered}
W-A^{\mathsf T}WA=I,\\
E(Ax)=E(x)-\|x\|_2^2.
\end{gathered}
```

Every nonzero unforced state therefore loses energy at the next step.
For $e_2$, the first two energies are $356/27$ and $329/27$:
the energy falls by one while the Euclidean squared length rises from
$1$ to $17/4$. These facts describe two different measurements of the
same trajectory.

Summing the identity along the trajectory gives, for every integer $m\ge1$,

```math
E(x_m)+\sum_{k=0}^{m-1}\|x_k\|_2^2=E(x_0).
```

The explicit power formula gives $E(x_m)\to0$. Consequently the total
sum of squared Euclidean lengths for the stated initial state is
$\sum_{k=0}^{\infty}\|x_k\|_2^2=356/27$.
The matrix $W$ supplies an analytical energy; identifying it with energy
of a physical system would require a separate model.
This is the [metric-defect identity](COMPOSITION.md#metric-defect) with
defect $A^{\mathsf T}WA-W=-I$.

## 5. Track a discarded transfer through repeated updates

Use the two coordinate packets and discard the transfer from the second
coordinate into the first. The retained matrix is $D=I/2$.
Its eigenvalues agree with those of $A$, but its powers omit an interaction:

```math
\begin{gathered}
A^n-D^n=\begin{pmatrix}0&4n/2^n\\0&0\end{pmatrix},\\
\|A^n-D^n\|_\infty=\frac{4n}{2^n}.
\end{gathered}
```

On $e_2$, this discrepancy has size $2$ at both times one and two,
then $3/2$ at time three. Both models tend to zero, but their predictions
differ throughout the transient.

The mechanism is visible in the finite telescoping identity, for $n\ge1$:

```math
A^n-D^n=\sum_{k=0}^{n-1}A^{n-1-k}(A-D)D^k.
```

Here $A-D=N$ and $N^2=0$, so each summand equals
$2^{-(n-1)}N$. There are $n$ such contributions. This derives the
factor $n$ in the exact discrepancy and connects it to the
[repeated-update error budget](STABILITY.md#budget-error-over-several-updates).
Matching eigenvalues or matching the final zero limit does not control
the error at a specified intermediate time.

## 6. Propagate disturbances from the step where they enter

Now let $\widehat x_{n+1}=A\widehat x_n+d_n$, with
$\widehat x_0=x_0$, and define $e_n=\widehat x_n-x_n$.
Assume the deterministic bound $\|d_n\|_\infty\le\delta$ at every
step, where $\delta\ge0$. No independence or probability distribution is
assumed. Repeated substitution gives

```math
e_n=\sum_{j=0}^{n-1}A^{n-1-j}d_j.
```

Consequently,

```math
\begin{aligned}
\|e_n\|_\infty&\le\delta\left(10-\frac{8n+10}{2^n}\right)\\
&\le10\delta.
\end{aligned}
```

The sum is empty at $n=0$. The factor multiplying $\delta$ in the bound
equals the sum of the exact power norms: both start at zero and increase
by $(1+4n)2^{-n}$ from time $n$ to time $n+1$.
This bound is sharp at every time: choose all the disturbances to be
$d_j=(\delta,\delta)^{\mathsf T}$. Since all entries of the powers
are nonnegative, their first-row contributions add with the same sign.
For $\delta=1/100$, the error at time four is
$(59/800,3/160)^{\mathsf T}$, and the limiting error is
$(1/10,1/50)^{\mathsf T}$.

The weighted maximum norm from section 3 gives a valid, simpler estimate:
$\|d_j\|_C\le8\delta$, so
$\|e_n\|_\infty\le\|e_n\|_C\le32\delta(1-(3/4)^n)$.
Its uniform bound is $32\delta$, compared with the sharp $10\delta$.
A convenient contraction estimate can be conservative. Converting the
input and output budgets back to the requested norm reveals that cost.

If the starting states also differ, add $A^ne_0$ to the error formula.
The initial-error contribution decays, while persistent disturbances can
maintain a nonzero error. An unforced stability conclusion must therefore
state what forcing or arithmetic errors it excludes.

## 7. Turn an iteration residual into a solution-error bound

Consider the affine iteration $x_{n+1}=Ax_n+b$ with
$b=(1,1)^{\mathsf T}$. Its fixed point satisfies
$(I-A)x_*=b$, and

```math
\begin{gathered}
(I-A)^{-1}=\begin{pmatrix}2&8\\0&2\end{pmatrix},\\
x_*=\begin{pmatrix}10\\2\end{pmatrix}.
\end{gathered}
```

For a proposed answer $\widehat x$, define the residual by
$r=b-(I-A)\widehat x$. It is also the next-iterate change
$A\widehat x+b-\widehat x$. With exact $A$ and $b$,

```math
\begin{gathered}
x_*-\widehat x=(I-A)^{-1}r,\\
\|x_*-\widehat x\|_\infty\le10\|r\|_\infty.
\end{gathered}
```

For $\widehat x=(248/25,99/50)^{\mathsf T}$, the residual is
$(0,1/100)^{\mathsf T}$ while the solution error is
$(2/25,1/50)^{\mathsf T}$. The error is eight times the residual in
infinity norm. The factor ten in the bound is attained by a residual
with two equal positive coordinates.

A target solution error $\varepsilon$ can therefore use the sufficient
stopping condition $\|r\|_\infty\le\varepsilon/10$ for this exact
problem. A residual computed with rounded coefficients or rounded arithmetic
needs those errors included in its budget. Subtracting the fixed point from
the affine recurrence also gives $x_n-x_*=A^n(x_0-x_*)$, so the same
transient analysis applies to its convergence.

## Try it: distinguish three stability questions

1. For $x_0=(1,1)^{\mathsf T}$, find $Ax_0$ and its infinity norm.
2. With $e_0=0$ and disturbances bounded by $1/100$ per coordinate,
   what is the sharp infinity-norm error bound at time two?
3. If a fixed-point residual has infinity norm at most $1/1000$,
   what solution-error bound follows? Does the energy identity remain
   unchanged when disturbances are added?

**Answers.** (1) The output is $(5/2,1/2)^{\mathsf T}$, with norm
$5/2$. (2) The bound is $7/200$, attained by two disturbances equal to
$(1/100,1/100)^{\mathsf T}$. (3) The solution error is at most $1/100$.
With an added disturbance $d$, the energy update instead contains
$2(Ax)^{\mathsf T}Wd+d^{\mathsf T}Wd$ in addition to
$E(x)-\|x\|_2^2$. Unforced energy decrease cannot simply be copied to
the disturbed recurrence.

## Completed audit record

| Item | Recorded answer |
|---|---|
| Space and update | $\mathbb R^2$, the displayed $A$, integer time. |
| Representation | Coordinate packets; $y=Cx$ is an invertible change. |
| Retained approximation | $D=I/2$ discards the transfer $2v$ into the first coordinate. |
| Unforced conclusion | Every initial state decays; the largest induced infinity-norm gain over time is $5/2$. |
| Disturbed conclusion | Under the stated per-step budget, the sharp uniform error bound from equal starting states is $10\delta$. |
| Residual interpretation | The specified fixed-point equation has inverse infinity norm ten. |
| Evidence | Elementary derivations above and eight finite exact example groups below; no new Lean or physical-model certification. |

Run `python -B examples/operator_dynamics.py` from a repository checkout.
The [exact check program](../../examples/operator_dynamics.py) compares
matrix powers with scalar updates for three initial states at times
$0,\ldots,16$. It checks the coordinate and energy identities, the omitted
transfer, every disturbance sign sequence through four updates, and the
fixed-point examples. These finite checks support the displayed calculations;
the general-time arguments and infinite limits are given in the text.

[Stability reference](STABILITY.md) · [Worked compositions](COMPOSITION.md) ·
[Observation and recovery study](OBSERVATION.md) · [All chapters](../OPERATOR_AUDIT.md#reference-chapters)
