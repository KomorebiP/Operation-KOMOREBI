# Compression and memory: a worked operator audit

Keeping one coordinate can simplify a calculation while losing information
needed for its next update. This study follows a two-coordinate system through
that failure, an exact memory formula, a compact checkpoint, and a controlled
finite-memory approximation. It also shows how block elimination and invariant
packets describe the same calculation from different directions.

Vectors are columns in $\mathbb R^2$, and time is a nonnegative integer.
The displayed numerical examples use rational arithmetic. Begin with
[transfer blocks](TRANSFER.md#1-source-to-target-blocks) or the
[recovery criterion](RECOVERY.md#2-exact-recovery-and-factorization) if those
concepts are new.

## 1. Specify what the summary retains

Let $x_n=(u_n,v_n)^{\mathsf T}$ and define

```math
\begin{gathered}
x_{n+1}=Tx_n,\\
T=\begin{pmatrix}1/2&1/4\\1/4&1/2\end{pmatrix},\\
R=\begin{pmatrix}1&0\end{pmatrix},\qquad
S=\begin{pmatrix}1\\0\end{pmatrix}.
\end{gathered}
```

The summary is $Rx_n=u_n$. The representative $S(s)=(s,0)^{\mathsf T}$
satisfies $RS=1$, while $SR=P=\operatorname{diag}(1,0)$ projects onto
the first coordinate. The other packet is $Q=I-P$.

| Transfer | Coefficient | Meaning |
|---|---:|---|
| $u\to u$ | $a=1/2$ | Retained coordinate contributes to its next value. |
| $v\to u$ | $b=1/4$ | Hidden coordinate returns to the retained coordinate. |
| $u\to v$ | $c=1/4$ | Retained coordinate creates a hidden contribution. |
| $v\to v$ | $d=1/2$ | Hidden contribution persists for another update. |

The compressed candidate is $RTS=1/2$. However, the two states $0$ and
$e_2$ have the same summary and next summaries $0$ and $1/4$.
Thus no rule depending only on the current $u_n$ gives the next retained
value for every state. This collision rules out nonlinear rules as well
as linear ones. Equivalently, $e_2\in\ker R$ but $Te_2\notin\ker R$,
so the [kernel-invariance criterion](TRANSFER.md#5-compression-and-exact-reduced-dynamics)
fails.

## 2. Follow the interaction that leaves and returns

For the rest of the numerical trajectory, start at $x_0=(1,0)^{\mathsf T}$.
Applying the compressed rule repeatedly predicts $\widetilde u_n=2^{-n}$.
The first retained update agrees with the full model. At the next one,
the path $u\to v\to u$ contributes $bc=1/16$:

```math
\begin{gathered}
RT^2S=a^2+bc=\frac5{16},\\
(RTS)^2=\frac14.
\end{gathered}
```

| $n$ | Full $u_n$ | Full $v_n$ | Repeated compression $2^{-n}$ |
|---:|---:|---:|---:|
| $0$ | $1$ | $0$ | $1$ |
| $1$ | $1/2$ | $1/4$ | $1/2$ |
| $2$ | $5/16$ | $1/4$ | $1/4$ |
| $3$ | $7/32$ | $13/64$ | $1/8$ |
| $4$ | $41/256$ | $5/32$ | $1/16$ |
| $5$ | $61/512$ | $121/1024$ | $1/32$ |

For arbitrary initial coordinates, adding and subtracting the scalar update
equations gives the two modes

```math
\begin{gathered}
s_n=(3/4)^n(u_0+v_0),\\
z_n=(1/4)^n(u_0-v_0),\\
u_n=(s_n+z_n)/2,\\
v_n=(s_n-z_n)/2.
\end{gathered}
```

Both modes decay, but their combination differs from $2^{-n}$.
First-step agreement on the chosen representative does not establish a
closed update. The [two-step return identity](TRANSFER.md#two-updates-can-leave-and-return)
identifies the missing path without calculating the whole trajectory.

## 3. Eliminate the hidden coordinate and keep its memory

The scalar equations are $u_{n+1}=au_n+bv_n$ and
$v_{n+1}=cu_n+dv_n$. Repeatedly substituting the second equation gives

```math
\begin{aligned}
v_n&=d^nv_0\\
&\quad+\sum_{j=0}^{n-1}d^{n-1-j}cu_j.
\end{aligned}
```

Substitute this expression into the first equation:

```math
\begin{aligned}
u_{n+1}&=au_n+bd^nv_0\\
&\quad+\sum_{j=0}^{n-1}k_{n-1-j}u_j,
\end{aligned}
```

where the **memory kernel** is

```math
k_\ell=bd^\ell c=\frac1{16\,2^\ell},\qquad \ell\ge0.
```

The order $bd^\ell c$ records the path: enter the hidden coordinate through
$c$, remain there for $\ell$ updates through $d$, and return through $b$.
The first kernel coefficient is the two-step return $bc$.
The sum is empty at $n=0$.

The term $bd^nv_0$ carries the initial hidden state. For the displayed
trajectory it vanishes because $v_0=0$. If $v_0$ is unknown, the formula
still contains that unknown input; eliminating a variable has not supplied
its value. For example, $u_0=0,v_0=1$ gives $u_1=1/4$ entirely from this
initial-state term.

The kernel has infinitely many nonzero coefficients even though the original
state has only two coordinates. Memory length and state dimension answer
different storage questions.

## 4. Save a compact memory state at a checkpoint

Define $r_n=bv_n$. The full history sum can be maintained recursively:

```math
\begin{aligned}
u_{n+1}&=\frac12u_n+r_n,\\
r_{n+1}&=\frac1{16}u_n+\frac12r_n,\\
r_0&=\frac14v_0.
\end{aligned}
```

This stores two real numbers, the same dimension as the original state,
and avoids a growing history list. It is an invertible coordinate change
$(u,v)\mapsto(u,v/4)$; reconstruct $v=4r$.

At time three in the table, the correct checkpoint is
$(u_3,r_3)=(7/32,13/256)$. Continuing from it gives $u_4=41/256$.
Saving only $u_3$ and restarting with $r_3=0$ instead gives $7/64$.
The omitted checkpoint value accounts exactly for the difference $13/256$.

A restart must therefore record the state required by the recurrence it
continues. For a checkpoint that consists of readings instead, the
[observation study](OBSERVATION.md#3-turn-observation-history-into-a-state)
explains how to derive and initialize a history update. Its indexing also
records when the last reading becomes available.

## 5. Truncate memory with an explicit error bound

Return to $u_0=1,v_0=0$. For an integer cutoff $m\ge0$, retain the most
recent $m$ terms of the memory sum and advance the approximate values
recursively:

```math
\begin{aligned}
\widetilde u_0&=1,\\
\widetilde u_{n+1}&=\frac12\widetilde u_n\\
&\quad+\sum_{j=\max(0,n-m)}^{n-1}k_{n-1-j}\widetilde u_j.
\end{aligned}
```

For $m=0$, the sum is empty and this is repeated compression. A cutoff
of two retains $u_{n-1}$ and $u_{n-2}$ when they are available, in addition
to the current value $u_n$.

The induced infinity norm of $T$ is $3/4$, so the full trajectory obeys
$|u_n|\le\|x_n\|_\infty\le(3/4)^n\le1$.
First evaluate the truncated formula on the *full* history. The omitted
tail has absolute value at most

```math
\epsilon_m=\sum_{\ell=m}^{\infty}k_\ell=\frac{2^{-m}}8.
```

This is a bound on one update using the full history. To control a
recursively advanced approximation, also propagate the errors in its
retained values. Their nonnegative coefficients sum to at most

```math
\begin{aligned}
q_m&=\frac12+\sum_{\ell=0}^{m-1}k_\ell\\
&=\frac{5-2^{-m}}8<1.
\end{aligned}
```

If all previous errors have magnitude at most $B$, the next error is at
most $q_mB+\epsilon_m$. Starting from zero error, induction with
$B=\epsilon_m/(1-q_m)$ therefore proves, for every $n\ge0$,

```math
|u_n-\widetilde u_n|\le\frac1{3\,2^m+1}.
```

The bound is conservative. At $m=2$ it is $1/13$; the first discrepancy,
at time four, is only $1/64$. In general, the models agree through time
$m+1$. Their first omitted contribution at time $m+2$ is
$k_mu_0=1/(16\,2^m)$. This provides a useful indexing check.
The proof uses the stated trajectory bound and contraction of the retained
coefficients; a small tail by itself would not control every recursively
advanced model.

## 6. Read the memory term through block elimination

For the same initial state $(1,0)^{\mathsf T}$, introduce formal power
series $U(t)=\sum_{n\ge0}u_nt^n$ and $V(t)=\sum_{n\ge0}v_nt^n$
in $\mathbb Q[[t]]$. Multiplying the scalar recurrences by $t^{n+1}$
and summing gives

```math
\begin{aligned}
(1-t/2)U-(t/4)V&=1,\\
-(t/4)U+(1-t/2)V&=0.
\end{aligned}
```

The constant term of $1-t/2$ is one, so it is invertible as a formal
series. Eliminating $V$ gives the Schur complement equation

```math
\left(1-\frac t2-\frac{t^2}{16(1-t/2)}\right)U=1.
```

The feedback term contains the same kernel series
$\sum_{\ell\ge0}k_\ell t^\ell=1/(16(1-t/2))$.
Simplifying gives

```math
U(t)=\frac{1-t/2}{1-t+3t^2/16}.
```

Equating coefficients yields $u_0=1$, $u_1=1/2$, and
$u_{n+2}=u_{n+1}-(3/16)u_n$ for $n\ge0$.
Thus an exact recurrence using two consecutive values can replace the
history sum once those values are initialized. Setting the feedback term
to zero gives the different series $1/(1-t/2)$, whose coefficients are
the repeated-compression prediction.
These are formal coefficient identities; the derivation uses no analytic
convergence assumption. Compare the [block-elimination reference](ALGEBRA.md#8-block-elimination-and-the-schur-complement).

## 7. Change the summary when the task permits

The sum $s_n=u_n+v_n$ has a closed scalar update
$s_{n+1}=(3/4)s_n$. The difference $z_n=u_n-v_n$ satisfies
$z_{n+1}=z_n/4$. Their projectors are

```math
\begin{gathered}
P_+=\frac12\begin{pmatrix}1&1\\1&1\end{pmatrix},\\
P_-=\frac12\begin{pmatrix}1&-1\\-1&1\end{pmatrix}.
\end{gathered}
```

They sum to $I$, annihilate each other, and commute with $T$; moreover
$T=(3/4)P_++(1/4)P_-$. This derives the trajectory formula in section 2
and illustrates [invariant packets](PACKETS.md#7-invariant-packets-and-block-diagonality).
Keeping both summaries recovers $u=(s+z)/2$ and $v=(s-z)/2$.

Keeping the sum alone answers a different question from retaining the
first coordinate. The states $e_1$ and $e_2$ have the same sum and different
first coordinates. Select a closed summary only after checking that it
retains the answer required by the task.

## Try it: initialize, restart, and bound

1. Starting from $(0,1)^{\mathsf T}$, what is $u_1$? Which term of the
   memory formula supplies it?
2. Restart the displayed trajectory at time three. What error in $u_4$
   results from setting its saved memory to zero?
3. At cutoff $m=2$, state the uniform error bound and the first time of
   disagreement. Can the sum summary recover the first coordinate for
   every initial state?

**Answers.** (1) $u_1=1/4$, supplied by $bv_0$.
(2) The restarted output is too small by $13/256$.
(3) The bound is $1/13$, with first discrepancy $1/64$ at time four.
The sum summary loses the distinction between $e_1$ and $e_2$, so it
cannot recover the first coordinate on the whole state space.

## Completed audit record

| Item | Recorded answer |
|---|---|
| Space and update | $\mathbb R^2$, the displayed $T$, integer time. |
| Summary and representative | $R(u,v)=u$, $S(s)=(s,0)$, with $RS=1$. |
| Closure obstruction | $0$ and $e_2$ share a summary and have different next summaries. |
| Exact replacement | The history kernel plus initial-state term, or the two-coordinate checkpoint $(u,r)$. |
| Approximation | Most recent $m$ memory terms, advanced recursively from $(u_0,v_0)=(1,0)$. |
| Error conclusion | Uniform bound $1/(3\,2^m+1)$ under the hypotheses derived above. |
| Alternative summary | Sum and difference are closed modes; both recover the original state. |
| Evidence | Elementary derivations and seven finite exact example groups; no new Lean or physical-model certification. |

Run `python -B examples/operator_memory.py` from a repository checkout.
The [exact check program](../../examples/operator_memory.py) compares scalar
updates and matrix powers for three initial states at times $0,\ldots,16$.
It checks the memory identity, checkpoint restarts, cutoffs $m=0,\ldots,4$,
the first 17 generating-function coefficients, and the packet identities.
The finite checks support the displayed examples; the general-time and
general-cutoff arguments are given in the text.

[Transfer reference](TRANSFER.md) · [Packets reference](PACKETS.md) ·
[Stability study](DYNAMICS.md) · [All chapters](../OPERATOR_AUDIT.md#reference-chapters)
