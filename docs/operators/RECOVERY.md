# Recovery and repair

[Operator guide](../OPERATOR_AUDIT.md) · [Transfer and compression](TRANSFER.md) · [Stability and numerical meaning](STABILITY.md)

A summary is sufficient relative to a requested answer and an admissible
input set. This chapter develops exact recovery, explicit obstructions,
additional measurements, probabilistic estimation, and retained memory.

## 1. Summaries and fibers

For a map $R:X\to S$, the fiber over a summary value $s$ is
$R^{-1}(s)=\{x\in X:R(x)=s\}$. It groups inputs that the summary
cannot distinguish. A fiber over an unattained value is empty.

For $R(x_1,x_2)=x_1+x_2$, the fiber over $s$ is the line
$\{(t,s-t):t\in\mathbb R\}$. For linear maps, nonempty fibers are
translates of the kernel: the fiber through $x$ is $x+\ker R$.
For nonlinear summaries, fibers can have other shapes.

The requested answer may be constant on these fibers even when the full
input is not recoverable. For example, $2x_1+2x_2$ is always $2s$ on
the sum fiber, while $x_1$ varies along it.

[Kernels and fibers](../examples/10_KERNELS.md).

## 2. Exact recovery and factorization

For maps $R:X\to S$ and $F:X\to Z$, exact recovery on all admissible
inputs means a map $G:R(X)\to Z$ with $F=G\circ R$, regarding $R$
as a map into its image. The criterion is

```math
R(u)=R(v)\ \Longrightarrow\ F(u)=F(v)
\quad\text{for every }u,v\in X.
```

Necessity follows by applying $G$ to the common summary. Conversely, if
the criterion holds, assign to each attained summary the common $F$ value
of its fiber. This gives a well-defined recovery function on $R(X)$.

This set-theoretic statement establishes existence. Continuity, efficient
evaluation, robustness, or a preferred extension outside $R(X)$ are further
questions. Restricting $X$ also changes the fibers: on inputs $(t,t)$,
the sum recovers the first coordinate as $s/2$.

[The elementary recovery demonstration](../demonstrations/RECOVERY.md).

## 3. Linear recovery, row spaces, and kernels

Let $R$ be an $m$ by $n$ real matrix and $F$ a $q$ by $n$ real matrix.
A linear rule using the measured coordinates has the form $B R=F$, where
$B$ is $q$ by $m$. In finite dimensions, the following conditions are
equivalent:

```math
\operatorname{row}(F)\subseteq\operatorname{row}(R),\qquad
\ker R\subseteq\ker F,\qquad
\text{there exists }B\text{ with }BR=F.
```

The row-space condition expresses every requested row as a linear combination
of measured rows. The kernel condition says every erased direction also
leaves the answer unchanged. It defines a linear recovery map on $R(\mathbb R^n)$,
which extends to the measurement space by choosing a basis extension.

For example,

```math
R=\begin{pmatrix}1&1&0\\0&1&1\end{pmatrix},\qquad
F=\begin{pmatrix}1&2&1\end{pmatrix},\qquad
B=\begin{pmatrix}1&1\end{pmatrix}.
```

Adding the two measured values gives the requested answer. Recovery matrices
can have different extensions on inconsistent measurement vectors, even when
their answers on attained summaries agree.

[Try exact matrix recovery in the laboratory](https://komorebip.github.io/Operation-KOMOREBI/recovery-lab.html).

## 4. Collision and kernel witnesses

An obstruction to exact recovery is a pair $u,v$ with the same summary and
different requested answers. For linear maps it is enough to give one
kernel direction $w$ with

```math
Rw=0,\qquad Fw\ne0.
```

For the two-row $R$ above, $w=(1,-1,1)^{\mathsf T}$ is erased.
If the requested answer is instead $F_0=[1\ \ 0\ \ 0]$, then $F_0w=1$.
The inputs $w$ and zero are therefore a collision witness. This excludes
every recovery function of these measurements on all real inputs, including
nonlinear functions.

A witness settles the specified recovery problem. A distributional prior
or restriction on the admissible inputs creates a different problem, whose
assumptions must be stated.

## 5. Repair with additional measurements

For finite real linear measurements, allowing arbitrary additional linear
rows, the minimum number of new independent rows needed to recover $Fx$ is

```math
\operatorname{rank}\begin{pmatrix}R\\F\end{pmatrix}
-\operatorname{rank}R.
```

This is the number of missing row directions modulo the measured row space.
Each added scalar measurement contributes at most one direction. Choosing a
basis of the missing target directions attains the bound.

For $R=[1\ \ 1]$ and $F=[1\ \ 0]$, one additional row suffices.
Choose $D=[1\ \ {-1}]$, giving summaries $s=x_1+x_2$ and $d=x_1-x_2$.
Then $x_1=(s+d)/2$. A target already proportional to $R$ needs no new row.

Restricted menus, costs, integral coefficients, and nonlinear constraints
change the admissible repair problem. The
[repair-menu example](../examples/25_REPAIR_MENUS.md) shows why a minimum
free dimension and a cheapest allowed selection can differ.

## 6. Conditional expectation and estimation

Exact recovery for all inputs and minimum expected error are different
criteria. With a specified finite probability distribution, the best
constant under squared error is the weighted mean.

Suppose a constant summary merges two outcomes whose requested values are
$0$ and $2$, with probabilities $1/4$ and $3/4$. For a constant prediction $c$,

```math
\frac14(0-c)^2+\frac34(2-c)^2
=\frac34+(c-3/2)^2.
```

The optimum is $c=3/2$, with expected squared error $3/4$. It is still
different from both realized answers. For multiple positive-probability
fibers, the same calculation gives a separate conditional mean on each.
The probability model does not prescribe an estimate on a zero-probability
fiber, and it does not by itself establish recovery on every admissible input.

[Weighted conditional averages](../examples/08_WEIGHTED_AVERAGES.md).

## 7. Hidden state and retained memory

Summary sufficiency can fail for the next state even when the current
summary is known exactly. Consider

```math
T(u,v)=(u+v,v),\qquad R(u,v)=u.
```

The full states $(0,0)$ and $(0,1)$ have the same current summary but next
summaries $0$ and $1$. There is no autonomous update depending on $u$ alone
for all initial states.

Retaining $v$ repairs the state description. Another exact description uses
two successive visible values: since $v$ is constant,

```math
u_{n+2}=2u_{n+1}-u_n.
```

The pair $(u_n,u_{n+1})$ determines $v=u_{n+1}-u_n$ and supports a closed
update. The [hidden-memory example](../examples/22_HIDDEN_MEMORY.md)
develops another system whose retained history gives a Fibonacci recurrence.
Both examples require a declared transition rule and initialization scope.

## Try it: recover a difference or a total

Measure $d_1=x_1-x_2$ and $d_2=x_2-x_3$ on $\mathbb R^3$. Can these
measurements recover $x_1-x_3$? Can they recover $x_1+x_2+x_3$ on all inputs?

**Answer.** The difference is $d_1+d_2$. The total is not recoverable:
adding $(1,1,1)^{\mathsf T}$ leaves both measurements fixed but increases
the total by three. One further independent measurement, such as $x_3$,
allows recovery of all three coordinates.

[Previous: Transfer and compression](TRANSFER.md) · [Next: Stability and numerical meaning](STABILITY.md) · [All chapters](../OPERATOR_AUDIT.md#reference-chapters)
