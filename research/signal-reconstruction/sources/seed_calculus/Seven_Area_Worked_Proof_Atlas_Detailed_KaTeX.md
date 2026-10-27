# Projector-Resolved Seed Calculus from Seed to Reconstruction

## Complete seed-to-reconstruction edition with seven retained worked realizations

## KaTeX-friendly full derivation

**Author:** Komorebi P.

# Part I - the calculus from the primitive seed to final reconstruction

The seven domain examples below are now preceded by a complete construction. The master realization uses one cyclic seed in $X=\mathbb C^8$ and follows it through every layer:

$$
\boxed{
\text{seed}
\to
\text{operator grammar}
\to
\text{generated hull}
\to
\text{relations}
\to
\text{addresses}
\to
\text{projectors}
\to
\text{transfer blocks}
\to
\text{refinement}
\to
\text{transform atlases}
\to
\text{nonlinear interactions}
\to
\text{obstructions}
\to
\text{completion}
\to
\text{synthesis}.
}
$$

## 0. The typed seed system

A seed system is the declared tuple

$$
\mathfrak S=(X,S,\mathcal A,\mathcal R,\mathcal P,\tau),
$$

where:

- $X$ is the ambient object type;
- $S\subseteq X$ is the primitive seed family;
- $\mathcal A$ is the fixed operator grammar;
- $\mathcal R$ is the relation system;
- $\mathcal P$ is one or more complete packet atlases;
- $\tau$ is the declared topology, filtration, or inverse-limit structure.

This separation prevents hidden encoding. The target may vary, but the operator grammar and relations must already be declared.

## 1. Generated hull

For a unital algebra $\mathcal A\subseteq\operatorname{End}(X)$, define

$$
\operatorname{Hull}_{\mathcal A}(S)
=
\operatorname{span}\{As:A\in\mathcal A,\ s\in S\}.
$$

This is the smallest $\mathcal A$-invariant subspace containing $S$:

1. $S$ is contained because $I\in\mathcal A$.
2. If $x=\sum_jc_jA_js_j$, then for $B\in\mathcal A$,

$$
Bx=\sum_jc_j(BA_j)s_j
\in\operatorname{Hull}_{\mathcal A}(S).
$$

3. Every invariant subspace containing $S$ must contain every $As$.

## 2. Seed rank and the orbit matrix

For one operator $U$ and one seed $s$ in an $n$-dimensional space, define

$$
\mathcal O_U(s)
=
\begin{bmatrix}
s&Us&U^2s&\cdots&U^{n-1}s
\end{bmatrix}.
$$

By Cayley-Hamilton, every later power is a linear combination of the first $n$ powers. Therefore

$$
\boxed{
\operatorname{Hull}_{\mathbb C[U]}(s)=X
\iff
\operatorname{rank}\mathcal O_U(s)=n.
}
$$

### Master seed

Let

$$
X=\mathbb C^8,
\qquad
s=e_0,
\qquad
Ue_j=e_{j+1\pmod 8}.
$$

Then

$$
s=e_0,
\quad
Us=e_1,
\quad\ldots,\quad
U^7s=e_7,
$$

so

$$
\mathcal O_U(s)=I_8,
\qquad
\boxed{\operatorname{rank}\mathcal O_U(s)=8.}
$$

One seed generates the entire ambient space.

## 3. Relations and quotient normal forms

The free seed module maps to the generated hull by evaluation:

$$
\varepsilon:\mathcal A^{(S)}\to X,
\qquad
\sum_s A_s[s]\mapsto\sum_sA_ss.
$$

The first isomorphism theorem gives

$$
\boxed{
\mathcal A^{(S)}/\ker\varepsilon
\cong
\operatorname{Hull}_{\mathcal A}(S).
}
$$

For the cyclic shift,

$$
U^8=I.
$$

Thus

$$
X\cong\mathbb C[z]/(z^8-1),
$$

with multiplication by $z$ represented by $U$. Every generated object has a unique normal form

$$
p(U)s=\sum_{k=0}^7a_kU^ks.
$$

Choose

$$
p(z)=2-z+3z^2+z^4+4z^5-2z^6+5z^7.
$$

Then

$$
\boxed{
x=p(U)s=(2,-1,3,0,1,4,-2,5)^{\mathsf T}.}
$$

## 4. Addresses and projectors

An address map assigns each elementary coordinate to one packet label. If $a(j)=\alpha$, define

$$
P_\alpha e_j=
\begin{cases}
e_j,&a(j)=\alpha,\\0,&a(j)\ne\alpha.
\end{cases}
$$

Because every $j$ has exactly one label,

$$
P_\alpha P_\beta=\delta_{\alpha\beta}P_\alpha,
\qquad
\sum_\alpha P_\alpha=I.
$$

For the master object, use three nested address levels:

$$
\text{parity}
\prec
\text{residue mod }4
\prec
\text{individual coordinate mod }8.
$$

Let $E_j$ select coordinate $j$, let

$$
R_r=E_r+E_{r+4},
$$

and let

$$
P_{\mathrm e}=E_0+E_2+E_4+E_6,
\qquad
P_{\mathrm o}=E_1+E_3+E_5+E_7.
$$

Then

$$
\boxed{
P_{\mathrm e}=R_0+R_2,
\qquad
P_{\mathrm o}=R_1+R_3,
\qquad
R_r=E_r+E_{r+4}.
}
$$

## 5. Exact object coordinates

Analysis is

$$
\mathcal A_{\mathcal P}x=(P_\alpha x)_\alpha,
$$

and synthesis is

$$
\mathcal S_{\mathcal P}(x_\alpha)_\alpha
=
\sum_\alpha x_\alpha.
$$

Completeness gives

$$
\boxed{
\mathcal S_{\mathcal P}\mathcal A_{\mathcal P}=I_X,
\qquad
x=\sum_\alpha P_\alpha x.
}
$$

For the master coordinate atlas,

$$
x=\sum_{j=0}^7E_jx.
$$

The exact symbolic residual is zero.

## 6. Transfer blocks

For $T\in\operatorname{End}(X)$, define

$$
T_{\beta\alpha}=P_\beta TP_\alpha.
$$

Insert completeness on both sides:

$$
T
=
\left(\sum_\beta P_\beta\right)
T
\left(\sum_\alpha P_\alpha\right)
=
\sum_{\alpha,\beta}P_\beta TP_\alpha.
$$

Therefore

$$
\boxed{T=\sum_{\alpha,\beta}T_{\beta\alpha}.}
$$

The map

$$
T\mapsto(T_{\beta\alpha})_{\beta,\alpha}
$$

is an algebra isomorphism when the block field is multiplied by matrix-style contraction over the intermediate packet.

## 7. Operator paths

For two operators $S,T$,

$$
P_\gamma STP_\alpha
=
\sum_\beta
(P_\gamma SP_\beta)(P_\beta TP_\alpha).
$$

More generally,

$$
P_{\alpha_m}T^mP_{\alpha_0}
=
\sum_{\alpha_1,\ldots,\alpha_{m-1}}
(P_{\alpha_m}TP_{\alpha_{m-1}})\cdots
(P_{\alpha_1}TP_{\alpha_0}).
$$

### Master transfer

Set

$$
T=2I-U+3U^2.
$$

Then

$$
(Tx)_j=2x_j-x_{j-1}+3x_{j-2},
$$

with indices modulo eight, and

$$
\boxed{
Tx=(-7,11,13,-6,11,7,-5,24)^{\mathsf T}.}
$$

For example,

$$
(Tx)_0=2(2)-5+3(-2)=-7,
$$

and

$$
(Tx)_7=2(5)-(-2)+3(4)=24.
$$

Let $S=I+U^3$. Then

$$
\sum_{a,b,\gamma}E_bSE_\gamma TE_a=ST
$$

exactly.

## 8. Exact refinement and coarsening

If a fine packet family $\{Q_\rho\}$ refines $\{P_\alpha\}$, then

$$
P_\alpha=\sum_{\rho\succ\alpha}Q_\rho.
$$

Define the coordinate maps

$$
J=\mathcal A_Q\mathcal S_P,
\qquad
C=\mathcal A_P\mathcal S_Q.
$$

Because both coordinate systems are complete,

$$
\boxed{CJ=I,\qquad JC=I.}
$$

For operators,

$$
\boxed{
P_\beta TP_\alpha
=
\sum_{\sigma\succ\beta}
\sum_{\rho\succ\alpha}
Q_\sigma TQ_\rho.
}
$$

Refinement itself is exact. Approximation begins only after a child packet is omitted or replaced.

## 9. Transform atlases

If $V:X\to Y$ is invertible and $E_\alpha$ are coordinate projectors on $Y$, then

$$
P_\alpha=V^{-1}E_\alpha V
$$

is a complete packet family on $X$.

For a cyclic operator $U^N=I$, the Fourier character projectors are

$$
Q_k=
\frac1N
\sum_{m=0}^{N-1}\omega^{-km}U^m.
$$

Character orthogonality gives

$$
Q_kQ_\ell=\delta_{k\ell}Q_k,
\qquad
\sum_kQ_k=I.
$$

For the master transfer,

$$
FTF^*
=
\operatorname{diag}(2-\zeta_k+3\zeta_k^2).
$$

The spatial matrix is cyclically banded, while the Fourier matrix is diagonal.

## 10. Redundant exact multi-atlas coordinates

Let $V_1,\ldots,V_m$ be unitary and let $w_a>0$. Define

$$
\mathcal A x=(w_aV_ax)_a.
$$

Set

$$
W=\sum_aw_a^2,
$$

and

$$
\mathcal S((c_a)_a)
=
\frac1W\sum_aw_aV_a^*c_a.
$$

Then

$$
\boxed{\mathcal S\mathcal A=I.}
$$

For $V_1=I$, $V_2=F$, $V_3=H$ and weights $(1,2,3)$,

$$
W=14,
$$

and the spatial-Fourier-Haar portfolio reconstructs $x$ exactly.

## 11. Nonlinear packet coordinates

For any map $N:X\to Y$, define

$$
\widetilde N
=
\mathcal A_QN\mathcal S_P.
$$

Then

$$
\boxed{
N
=
\mathcal S_Q\widetilde N\mathcal A_P.
}
$$

No linearity assumption is needed.

If $B$ is bilinear,

$$
B(x,x)
=
\sum_{a,c}B(P_ax,P_cx).
$$

The interaction coordinates have three indices:

$$
B_{b;ac}(x)=Q_bB(P_ax,P_cx).
$$

### Master nonlinear operation

Set

$$
N(x)=x+(Ux)\odot(U^3x).
$$

Then

$$
\boxed{
N(x)=(22,-5,-2,6,1,7,-2,3)^{\mathsf T}.}
$$

The bilinear interaction sum over all packet pairs equals the direct coordinatewise product exactly.

## 12. Obstruction packets

For a finite linear correction problem

$$
Lh=d,
$$

let $L^\dagger$ be the Moore-Penrose inverse and define

$$
\Pi_{\mathrm{Obs}}=I-LL^\dagger.
$$

Then

$$
\boxed{
Lh=d\text{ is solvable}
\iff
\Pi_{\mathrm{Obs}}d=0.
}
$$

For

$$
L=
\begin{pmatrix}
1&0\\
0&1\\
1&1
\end{pmatrix},
$$

$$
\Pi_{\mathrm{Obs}}
=
\frac13
\begin{pmatrix}
1&1&-1\\
1&1&-1\\
-1&-1&1
\end{pmatrix}.
$$

The datum $(1,2,3)^{\mathsf T}$ has zero obstruction. The datum $(1,2,4)^{\mathsf T}$ has

$$
\boxed{
\Pi_{\mathrm{Obs}}
\begin{pmatrix}1\\2\\4\end{pmatrix}
=
\begin{pmatrix}-1/3\\-1/3\\1/3\end{pmatrix}\ne0.
}
$$

A working calculus must retain this negative control rather than forcing every residual to vanish.

## 13. Completion

Let $D$ be dense in a normed space $X$, and let $A,B:X\to Y$ be bounded. If $A=B$ on $D$, then for $x_n\in D$ with $x_n\to x$,

$$
Ax=\lim_nAx_n=\lim_nBx_n=Bx.
$$

Thus bounded finite packet identities established on a dense invariant core extend to the completion. An infinite refinement tower still requires explicit compatibility, domain, completeness, and convergence hypotheses.

## 14. Final seed-to-reconstruction theorem

Under a declared seed family, fixed grammar, explicit relation system, complete packet atlases, exact refinement maps, admissible finite maps, and synthesis laws:

1. the generated object is the quotient of a free seed module by the relation kernel;
2. every complete atlas reconstructs the object;
3. every linear operator reconstructs from transfer blocks;
4. products reconstruct from packet paths;
5. complete refinement preserves objects and operators;
6. nonlinear maps possess exact packet-coordinate conjugates;
7. multilinear terms decompose into interaction tensors;
8. finite correction failures are localized by obstruction projectors;
9. bounded identities extend from dense cores to declared completions;
10. every claim returns to object space with an explicit residual.

This is the complete finite calculus used by the seven original realizations retained below.

---

# Part II - the seven complete worked realizations retained in full


This document gives seven complete finite worked examples of the same calculus. Every area follows the same proof protocol:

1. Declare the object space and a complete packet family.
2. Verify idempotence, pairwise annihilation, and completeness.
3. Analyze the object into packet coordinates.
4. Resolve the relevant operator, transform, update, or nonlinear map.
5. Refine or transport coordinates when appropriate.
6. Synthesize the original object or output.
7. Compute an exact residual, including a negative control where useful.

The examples establish the finite calculus under their displayed hypotheses. They do not convert finite examples into an automatic theorem for every infinite-dimensional or physical setting.

---

# 1. The common finite theorem

Let $X$ be a finite-dimensional vector space and let

$$
P_0, P_1, \ldots, P_{q-1}\in\operatorname{End}(X)
$$

satisfy

$$
P_\alpha P_\beta=\delta_{\alpha\beta}P_\alpha,
\qquad
\sum_{\alpha=0}^{q-1}P_\alpha=I_X.
$$

The packet spaces are $X_\alpha=P_\alpha X$.

## 1.1 Exact object reconstruction

For every $x\in X$,

$$
x=I_Xx=\left(\sum_\alpha P_\alpha\right)x
=\sum_\alpha P_\alpha x.
$$

The analysis and synthesis maps are

$$
\mathcal A_{\mathcal P}x=(P_0x,\ldots,P_{q-1}x),
$$

and

$$
\mathcal S_{\mathcal P}(x_0,\ldots,x_{q-1})
=\sum_\alpha x_\alpha.
$$

On the complete packet range,

$$
\boxed{\mathcal S_{\mathcal P}\mathcal A_{\mathcal P}=I_X.}
$$

## 1.2 Exact operator reconstruction

For $T\in\operatorname{End}(X)$, define the transfer block

$$
T_{\beta\alpha}=P_\beta T P_\alpha.
$$

Then

$$
T
=I_XTI_X
=\left(\sum_\beta P_\beta\right)
T
\left(\sum_\alpha P_\alpha\right)
=\sum_{\alpha,\beta}P_\beta T P_\alpha.
$$

Hence

$$
\boxed{T=\sum_{\alpha,\beta}T_{\beta\alpha}.}
$$

For two operators $S,T$,

$$
(ST)_{\gamma\alpha}
=P_\gamma STP_\alpha
=\sum_\beta(P_\gamma SP_\beta)(P_\beta TP_\alpha),
$$

so packet blocks multiply by a sum over intermediate packet paths:

$$
\boxed{(ST)_{\gamma\alpha}=\sum_\beta S_{\gamma\beta}T_{\beta\alpha}.}
$$

## 1.3 Exact refinement

Suppose a coarse packet has complete descendants:

$$
P_\alpha=\sum_{\beta\succ\alpha}Q_\beta,
\qquad
Q_\beta Q_\gamma=\delta_{\beta\gamma}Q_\beta.
$$

Then

$$
P_\delta TP_\alpha
=\sum_{\beta\succ\alpha}P_\delta TQ_\beta,
$$

and refining both sides gives

$$
P_\delta TP_\alpha
=\sum_{\gamma\succ\delta}
\sum_{\beta\succ\alpha}
Q_\gamma TQ_\beta.
$$

Refinement changes the address resolution, not the represented object or operator.

## 1.4 Transform atlases

Let $U:X\to Y$ be invertible and let $E_\alpha$ be ordinary coordinate selectors on $Y$ with

$$
E_\alpha E_\beta=\delta_{\alpha\beta}E_\alpha,
\qquad
\sum_\alpha E_\alpha=I_Y.
$$

Define

$$
P_\alpha=U^{-1}E_\alpha U.
$$

Then

$$
P_\alpha P_\beta
=U^{-1}E_\alpha E_\beta U
=\delta_{\alpha\beta}P_\alpha,
$$

and

$$
\sum_\alpha P_\alpha
=U^{-1}\left(\sum_\alpha E_\alpha\right)U
=I_X.
$$

Thus Fourier, wavelet, normal-mode, singular-vector, and other invertible coordinates all become exact packet atlases through the same pullback rule.

---

# 2. Area I - finite linear algebra and transfer blocks

## Step 1: declare the packet spaces

Work in $X=\mathbb Q^6$ and define

$$
X_0=\operatorname{span}(e_1,e_2),\qquad
X_1=\operatorname{span}(e_3,e_4),\qquad
X_2=\operatorname{span}(e_5,e_6).
$$

The projectors are

$$
P_0=\operatorname{diag}(1,1,0,0,0,0),
$$

$$
P_1=\operatorname{diag}(0,0,1,1,0,0),
$$

$$
P_2=\operatorname{diag}(0,0,0,0,1,1).
$$

They satisfy

$$
P_iP_j=\delta_{ij}P_i,
\qquad
P_0+P_1+P_2=I_6.
$$

## Step 2: decompose and reconstruct a vector

Take

$$
x=(2,-1,3,4,-2,5)^{\mathsf T}.
$$

Its packets are

$$
P_0x=(2,-1,0,0,0,0)^{\mathsf T},
$$

$$
P_1x=(0,0,3,4,0,0)^{\mathsf T},
$$

$$
P_2x=(0,0,0,0,-2,5)^{\mathsf T}.
$$

Adding coordinatewise gives

$$
P_0x+P_1x+P_2x
=(2,-1,3,4,-2,5)^{\mathsf T}=x.
$$

The reconstruction residual is exactly

$$
\boxed{\sum_iP_ix-x=0.}
$$

![Linear object packets](figures/20_linear_object_packets.png)

## Step 3: resolve a nontrivial operator

Let

$$
T=
\begin{pmatrix}
1&2&0&0&1&0\\
0&1&1&0&0&1\\
2&0&1&1&0&0\\
0&1&0&2&1&0\\
1&0&0&1&2&1\\
0&0&1&0&0&3
\end{pmatrix}.
$$

The nine transfer blocks are $T_{\beta\alpha}=P_\beta TP_\alpha$. In $2\times2$ packet coordinates they are

$$
[T_{\beta\alpha}]=
\begin{pmatrix}
\begin{pmatrix}1&2\\0&1\end{pmatrix}&
\begin{pmatrix}0&0\\1&0\end{pmatrix}&
\begin{pmatrix}1&0\\0&1\end{pmatrix}\\[6pt]
\begin{pmatrix}2&0\\0&1\end{pmatrix}&
\begin{pmatrix}1&1\\0&2\end{pmatrix}&
\begin{pmatrix}0&0\\1&0\end{pmatrix}\\[6pt]
\begin{pmatrix}1&0\\0&0\end{pmatrix}&
\begin{pmatrix}0&1\\1&0\end{pmatrix}&
\begin{pmatrix}2&1\\0&3\end{pmatrix}
\end{pmatrix}.
$$

Applying $T$ gives

$$
Tx=(-2,7,11,5,7,18)^{\mathsf T}.
$$

For output packet $X_0$, the three input-packet contributions are

$$
T_{00}P_0x=(0,-1,0,0,0,0)^{\mathsf T},
$$

$$
T_{01}P_1x=(0,3,0,0,0,0)^{\mathsf T},
$$

$$
T_{02}P_2x=(-2,5,0,0,0,0)^{\mathsf T}.
$$

Therefore

$$
T_{00}P_0x+T_{01}P_1x+T_{02}P_2x
=(-2,7,0,0,0,0)^{\mathsf T}=P_0Tx.
$$

The remaining output packets similarly satisfy

| Output packet | From $X_0$ | From $X_1$ | From $X_2$ | Exact sum |
|---|---:|---:|---:|---:|
| $X_0$ | $(0,-1)$ | $(0,3)$ | $(-2,5)$ | $(-2,7)$ |
| $X_1$ | $(4,-1)$ | $(7,8)$ | $(0,-2)$ | $(11,5)$ |
| $X_2$ | $(2,0)$ | $(4,3)$ | $(1,15)$ | $(7,18)$ |

Thus

$$
\boxed{\sum_{\alpha,\beta}P_\beta TP_\alpha-T=0.}
$$

![Linear block contributions](figures/21_linear_block_contributions.png)

## Step 4: verify the packet path law

Use

$$
S=
\begin{pmatrix}
2&0&1&0&0&0\\
1&1&0&0&0&1\\
0&1&1&0&1&0\\
0&0&1&1&0&0\\
1&0&0&0&1&1\\
0&1&0&1&0&1
\end{pmatrix}.
$$

For input $X_2$ and output $X_0$,

$$
(P_0STP_2)_{X_0\leftarrow X_2}
=
\begin{pmatrix}2&0\\1&4\end{pmatrix}.
$$

The three intermediate paths give

$$
(P_0SP_0)(P_0TP_2)
=
\begin{pmatrix}2&0\\1&1\end{pmatrix},
$$

$$
(P_0SP_1)(P_1TP_2)
=
\begin{pmatrix}0&0\\0&0\end{pmatrix},
$$

$$
(P_0SP_2)(P_2TP_2)
=
\begin{pmatrix}0&0\\0&3\end{pmatrix}.
$$

Their sum is the direct block:

$$
\begin{pmatrix}2&0\\1&1\end{pmatrix}
+
\begin{pmatrix}0&0\\0&0\end{pmatrix}
+
\begin{pmatrix}0&0\\0&3\end{pmatrix}
=
\begin{pmatrix}2&0\\1&4\end{pmatrix}.
$$

All nine input-output blocks have exact zero residual.

## Step 5: refine a packet

Define

$$
Q_{00}=\operatorname{diag}(1,0,0,0,0,0),
\qquad
Q_{01}=\operatorname{diag}(0,1,0,0,0,0).
$$

Then

$$
P_0=Q_{00}+Q_{01}.
$$

For example,

$$
P_2TP_0=P_2TQ_{00}+P_2TQ_{01},
$$

and

$$
P_0TP_0
=Q_{00}TQ_{00}+Q_{00}TQ_{01}
+Q_{01}TQ_{00}+Q_{01}TQ_{01}.
$$

The coarse operator has not changed; only the address system has become finer.

---

# 3. Area II - polyphase, Haar wavelets, and Fourier space

## Step 1: choose the signal

Take

$$
x=(3,1,4,1,5,9,2,6)^{\mathsf T}.
$$

For order $N$, define the residue projector

$$
(P_{N,r}x)[n]=\mathbf 1_{n\equiv r\pmod N}x[n].
$$

These obey

$$
P_{N,r}P_{N,s}=\delta_{rs}P_{N,r},
\qquad
\sum_{r=0}^{N-1}P_{N,r}=I.
$$

## Step 2: exact order-four polyphase coordinates

The four decimated channels are

$$
x_0=(3,5)^{\mathsf T},\quad
x_1=(1,9)^{\mathsf T},\quad
x_2=(4,2)^{\mathsf T},\quad
x_3=(1,6)^{\mathsf T}.
$$

The address relation is

$$
n=4q+r,
\qquad
x_r[q]=x[4q+r].
$$

Synthesis places every value back at its unique original address:

$$
(\mathcal S_4(x_0,x_1,x_2,x_3))[4q+r]=x_r[q].
$$

Thus

$$
\mathcal S_4\mathcal A_4x
=(3,1,4,1,5,9,2,6)^{\mathsf T}=x.
$$

![Polyphase interleaving](figures/22_signal_polyphase_interleave.png)

## Step 3: nested phase refinement

The order-two packets split into order-four children:

$$
P_{2,0}=P_{4,0}+P_{4,2},
\qquad
P_{2,1}=P_{4,1}+P_{4,3}.
$$

At channel level,

$$
(3,4,5,2)\longleftrightarrow(3,5)\oplus(4,2),
$$

and

$$
(1,1,9,6)\longleftrightarrow(1,9)\oplus(1,6).
$$

This is exact address separation, not interpolation.

## Step 4: one-level Haar analysis and synthesis

For each adjacent pair $(a,b)$, define

$$
\ell=\frac{a+b}{\sqrt2},
\qquad
h=\frac{a-b}{\sqrt2}.
$$

The inverse is

$$
a=\frac{\ell+h}{\sqrt2},
\qquad
b=\frac{\ell-h}{\sqrt2}.
$$

For the first pair $(3,1)$,

$$
(\ell,h)=(2\sqrt2,\sqrt2),
$$

so

$$
\frac{2\sqrt2+\sqrt2}{\sqrt2}=3,
\qquad
\frac{2\sqrt2-\sqrt2}{\sqrt2}=1.
$$

The full coefficient vector is

$$
Hx=
\left(
2\sqrt2,
\sqrt2,
\frac{5\sqrt2}{2},
\frac{3\sqrt2}{2},
7\sqrt2,
-2\sqrt2,
4\sqrt2,
-2\sqrt2
\right)^{\mathsf T}.
$$

Because $H^{\mathsf T}H=I_8$,

$$
\boxed{x=H^{\mathsf T}Hx.}
$$

![Haar butterflies](figures/23_signal_haar_butterfly.png)

## Step 5: Fourier coordinates as pulled-back packets

Let $F_8$ be the unitary DFT:

$$
(F_8)_{jk}=\frac1{\sqrt8}e^{-2\pi ijk/8}.
$$

Then

$$
\widehat x=F_8x,
\qquad
x=F_8^*\widehat x.
$$

Group the frequency indices into

$$
\{0\},\quad\{1,7\},\quad\{2,6\},\quad\{3,5\},\quad\{4\}.
$$

If $E_B$ selects a group $B$, define

$$
Q_B=F_8^*E_BF_8.
$$

Then

$$
Q_BQ_C=\delta_{BC}Q_B,
\qquad
\sum_BQ_B=I_8.
$$

The first and Nyquist coefficients are

$$
\widehat x_0=\frac{31\sqrt2}{4},
\qquad
\widehat x_4=-\frac{3\sqrt2}{4}.
$$

The exact band energies are

| Band $B$ | Energy $\|E_B\widehat x\|_2^2$ |
|---|---:|
| $\{0\}$ | $961/8$ |
| $\{1,7\}$ | $97/4-5\sqrt2$ |
| $\{2,6\}$ | $13/4$ |
| $\{3,5\}$ | $97/4+5\sqrt2$ |
| $\{4\}$ | $9/8$ |

Their sum is

$$
\frac{961}{8}
+\left(\frac{97}{4}-5\sqrt2\right)
+\frac{13}{4}
+\left(\frac{97}{4}+5\sqrt2\right)
+\frac98
=173.
$$

Directly,

$$
\|x\|_2^2=3^2+1^2+4^2+1^2+5^2+9^2+2^2+6^2=173.
$$

Thus the Fourier packets exactly partition the signal energy.

![Fourier coefficients](figures/24_signal_fourier_coefficients.png)

![Fourier band packets](figures/25_signal_fourier_band_packets.png)

The polyphase, Haar, and Fourier inverses are algebraically different. Their agreement is therefore a portfolio of independent exact reconstructions, not one repeated numerical check.

---

# 4. Area III - quantum circuit packet paths

## Step 1: parity packets

Use the ordered basis

$$
|00\rangle,|01\rangle,|10\rangle,|11\rangle
$$

of $\mathbb C^2\otimes\mathbb C^2$. Define

$$
P_{\mathrm e}=|00\rangle\langle00|+|11\rangle\langle11|,
$$

$$
P_{\mathrm o}=|01\rangle\langle01|+|10\rangle\langle10|.
$$

Then

$$
P_{\mathrm e}+P_{\mathrm o}=I_4,
\qquad
P_{\mathrm e}P_{\mathrm o}=0.
$$

## Step 2: prepare the Bell state

Start from

$$
\psi_0=|00\rangle.
$$

The gate matrices are

$$
H\otimes I
=\frac1{\sqrt2}
\begin{pmatrix}
1&0&1&0\\
0&1&0&1\\
1&0&-1&0\\
0&1&0&-1
\end{pmatrix},
$$

and

$$
\operatorname{CNOT}
=
\begin{pmatrix}
1&0&0&0\\
0&1&0&0\\
0&0&0&1\\
0&0&1&0
\end{pmatrix}.
$$

Therefore

$$
\begin{pmatrix}1\\0\\0\\0\end{pmatrix}
\xmapsto{H\otimes I}
\frac1{\sqrt2}
\begin{pmatrix}1\\0\\1\\0\end{pmatrix}
\xmapsto{\operatorname{CNOT}}
\frac1{\sqrt2}
\begin{pmatrix}1\\0\\0\\1\end{pmatrix}.
$$

The final state is

$$
|\Phi^+\rangle=\frac{|00\rangle+|11\rangle}{\sqrt2}.
$$

![Quantum state evolution](figures/26_quantum_state_evolution.png)

## Step 3: resolve all four parity paths

The four routes are

| Intermediate parity | Output parity | Path vector |
|---|---|---|
| even | even | $(1,0,0,0)^{\mathsf T}/\sqrt2$ |
| odd | even | $(0,0,0,1)^{\mathsf T}/\sqrt2$ |
| even | odd | $0$ |
| odd | odd | $0$ |

The two nonzero paths are

$$
P_{\mathrm e}\operatorname{CNOT}P_{\mathrm e}(H\otimes I)P_{\mathrm e}|00\rangle
=\frac{|00\rangle}{\sqrt2},
$$

and

$$
P_{\mathrm e}\operatorname{CNOT}P_{\mathrm o}(H\otimes I)P_{\mathrm e}|00\rangle
=\frac{|11\rangle}{\sqrt2}.
$$

Their coherent vector sum is the Bell state:

$$
\frac{|00\rangle}{\sqrt2}
+
\frac{|11\rangle}{\sqrt2}
=|\Phi^+\rangle.
$$

![Quantum path table and measurement](figures/27_quantum_path_and_measurement.png)

## Step 4: density matrix and entanglement

The density matrix is

$$
\rho=|\Phi^+\rangle\langle\Phi^+|
=\frac12
\begin{pmatrix}
1&0&0&1\\
0&0&0&0\\
0&0&0&0\\
1&0&0&1
\end{pmatrix}.
$$

Tracing out the second qubit gives

$$
\rho_A=\operatorname{Tr}_B(\rho)=\frac12I_2.
$$

Its eigenvalues are $(1/2,1/2)$, so

$$
S(\rho_A)
=-\operatorname{Tr}(\rho_A\log_2\rho_A)
=1.
$$

The global state is pure but the reduced state is maximally mixed, proving one ebit of entanglement.

The exact certificates are

$$
\|\Phi^+\|^2-1=0,
$$

$$
P_{\mathrm o}|\Phi^+\rangle=0,
$$

$$
\sum_{\text{four paths}}\text{path}-|\Phi^+\rangle=0,
$$

and

$$
\operatorname{Tr}_B(\rho)-\frac12I_2=0.
$$

---

# 5. Area IV - conditional expectation and Bayesian refinement

## Step 1: conditional expectation as a weighted projector

Use

$$
\mu=\left(\frac1{10},\frac2{10},\frac3{10},\frac4{10}\right)
$$

and the partition

$$
A=\{0,1\},\qquad B=\{2,3\}.
$$

The conditional-expectation matrix is

$$
E_\pi=
\begin{pmatrix}
1/3&2/3&0&0\\
1/3&2/3&0&0\\
0&0&3/7&4/7\\
0&0&3/7&4/7
\end{pmatrix}.
$$

For

$$
f=(1,4,-2,3)^{\mathsf T},
$$

we get

$$
E_\pi f=\left(3,3,\frac67,\frac67\right)^{\mathsf T}.
$$

Direct multiplication gives

$$
E_\pi^2=E_\pi.
$$

With $M=\operatorname{diag}(\mu)$,

$$
ME_\pi=E_\pi^{\mathsf T}M,
$$

so $E_\pi$ is orthogonal for the weighted inner product

$$
\langle u,v\rangle_\mu=u^{\mathsf T}Mv.
$$

The residual is

$$
r=f-E_\pi f
=\left(-2,1,-\frac{20}{7},\frac{15}{7}\right)^{\mathsf T}.
$$

For packet indicators $\mathbf1_A=(1,1,0,0)^{\mathsf T}$ and $\mathbf1_B=(0,0,1,1)^{\mathsf T}$,

$$
\langle r,\mathbf1_A\rangle_\mu
=\frac1{10}(-2)+\frac2{10}(1)=0,
$$

and

$$
\langle r,\mathbf1_B\rangle_\mu
=\frac3{10}\left(-\frac{20}{7}\right)
+\frac4{10}\left(\frac{15}{7}\right)=0.
$$

Thus the residual is orthogonal to the complete packet-constant subspace.

![Weighted conditional expectation](figures/28_bayes_weighted_projection.png)

## Step 2: exact effective coarse likelihood

For prior $p$ and positive likelihood $\lambda$, define

$$
\mathcal B_\lambda(p)_i
=\frac{\lambda_ip_i}{\sum_j\lambda_jp_j}.
$$

Let $P_a=\sum_{i\in I_a}p_i$ and define

$$
r_a(p)=\frac{\sum_{i\in I_a}\lambda_ip_i}{P_a}.
$$

Then the coarse posterior is exactly

$$
\boxed{C_\pi\mathcal B_\lambda(p)=\mathcal B_{r(p)}(C_\pi p).}
$$

Proof: the $a$th coarse mass is

$$
\sum_{i\in I_a}\frac{\lambda_ip_i}{\sum_j\lambda_jp_j}
=
\frac{P_ar_a(p)}{\sum_bP_br_b(p)}.
$$

## Step 3: characterize sufficient packet likelihoods

A fixed coarse likelihood $\bar\lambda$ satisfies

$$
C_\pi\mathcal B_\lambda(p)
=\mathcal B_{\bar\lambda}(C_\pi p)
$$

for every strictly positive fine prior if and only if there is a global scalar $c>0$ such that

$$
\lambda_i=c\bar\lambda_a
\qquad(i\in I_a).
$$

Thus, after one globally invisible scale is removed, the likelihood must be constant within each packet.

For the sufficient likelihood

$$
\lambda=(2,2,1,1)^{\mathsf T},
$$

the fine posterior is

$$
\mathcal B_\lambda(\mu)
=
\left(\frac2{13},\frac4{13},\frac3{13},\frac4{13}\right)^{\mathsf T},
$$

and coarsening gives

$$
\left(\frac6{13},\frac7{13}\right)^{\mathsf T},
$$

which equals the coarse update of $(3/10,7/10)$ with likelihood $(2,1)$.

## Step 4: give a nonsufficient negative control

Take

$$
\lambda=(1,3,2,4)^{\mathsf T}.
$$

The exact effective packet likelihoods are

$$
r_A=\frac73,
\qquad
r_B=\frac{22}{7}.
$$

The exact coarse posterior is

$$
C_\pi\mathcal B_\lambda(\mu)
=\left(\frac7{29},\frac{22}{29}\right)^{\mathsf T}.
$$

Using the nominal coarse likelihood $\bar\lambda=(2,3)^{\mathsf T}$ instead gives

$$
\mathcal B_{\bar\lambda}(C_\pi\mu)
=\left(\frac29,\frac79\right)^{\mathsf T}.
$$

The exact defect is

$$
\boxed{
\left(\frac7{29},\frac{22}{29}\right)
-
\left(\frac29,\frac79\right)
=
\left(\frac5{261},-\frac5{261}\right).
}
$$

Two different fine priors can have the same coarse masses:

$$
p^{(1)}=\left(\frac1{10},\frac2{10},\frac3{10},\frac4{10}\right),
$$

$$
p^{(2)}=\left(\frac2{10},\frac1{10},\frac4{10},\frac3{10}\right).
$$

Both coarsen to $(3/10,7/10)$, yet

$$
C_\pi\mathcal B_\lambda(p^{(1)})
=\left(\frac7{29},\frac{22}{29}\right),
$$

$$
C_\pi\mathcal B_\lambda(p^{(2)})
=\left(\frac15,\frac45\right).
$$

Their difference is

$$
\left(\frac6{145},-\frac6{145}\right)\ne0.
$$

This proves that the coarse prior alone is not sufficient when likelihoods vary inside a packet.

![Same coarse prior witness](figures/29_bayes_same_coarse_witness.png)

## Step 5: factor the information-loss defect exactly

Let

$$
P=C_\pi p,
\qquad
\delta=r(p)-\bar\lambda,
$$

$$
\bar b=\mathcal B_{\bar\lambda}(P),
\qquad
Z_r=P^{\mathsf T}r(p).
$$

Then

$$
\boxed{
C_\pi\mathcal B_\lambda(p)-\mathcal B_{\bar\lambda}(P)
=
\frac1{Z_r}
\left(\operatorname{diag}(P)-\bar bP^{\mathsf T}\right)\delta.
}
$$

For the example,

$$
P=\begin{pmatrix}3/10\\7/10\end{pmatrix},
\qquad
\delta=\begin{pmatrix}1/3\\1/7\end{pmatrix},
$$

$$
Z_r=\frac{29}{10},
\qquad
\bar b=\begin{pmatrix}2/9\\7/9\end{pmatrix},
$$

and

$$
\operatorname{diag}(P)-\bar bP^{\mathsf T}
=
\begin{pmatrix}
7/30&-7/45\\
-7/30&7/45
\end{pmatrix}.
$$

Multiplication returns

$$
\frac1{Z_r}
\left(\operatorname{diag}(P)-\bar bP^{\mathsf T}\right)\delta
=
\begin{pmatrix}5/261\\-5/261\end{pmatrix},
$$

exactly matching the direct defect.

---

# 6. Area V - closed special-function formulas and an integer sequence candidate

## Step 1: define the signed order-five packet

Define

$$
D_5(z)=\sum_{n\ge0}(-1)^n\frac{z^{5n}}{(5n)!}.
$$

It satisfies

$$
D_5^{(5)}=-D_5.
$$

Let

$$
\eta_k=\exp\left(\frac{(2k+1)\pi i}{5}\right),
\qquad 0\le k<5,
$$

so $\eta_k^5=-1$. Then the roots-of-unity filter gives

$$
\boxed{D_5(z)=\frac15\sum_{k=0}^4e^{\eta_kz}.}
$$

Indeed,

$$
\frac15\sum_{k=0}^4e^{\eta_kz}
=
\sum_{m\ge0}
\left(\frac15\sum_{k=0}^4\eta_k^m\right)
\frac{z^m}{m!}.
$$

The inner character sum is zero unless $5\mid m$. If $m=5n$, it equals $(-1)^n$.

![Signed fifth roots](figures/30_arithmetic_signed_roots.png)

## Step 2: derive two closed forms

Pairing conjugate roots gives

$$
\boxed{
D_5(z)=\frac15\left[e^{-z}+2e^{az}\cos(bz)+2e^{cz}\cos(dz)\right],
}
$$

where

$$
a=\frac{1+\sqrt5}{4},
\qquad
b=\frac{\sqrt{10-2\sqrt5}}4,
$$

$$
c=\frac{1-\sqrt5}{4},
\qquad
d=\frac{\sqrt{10+2\sqrt5}}4.
$$

The factorial multiplication formula

$$
(5n)!=5^{5n}n!
\left(\frac15\right)_n
\left(\frac25\right)_n
\left(\frac35\right)_n
\left(\frac45\right)_n
$$

gives the hypergeometric form

$$
\boxed{
D_5(z)
={}_0F_4\left(
\begin{matrix}-\\1/5,2/5,3/5,4/5\end{matrix};
-\frac{z^5}{5^5}
\right).
}
$$

## Step 3: define the reciprocal-square sequence

Set

$$
S(z)=D_5(z)^{-2}
=\sum_{n\ge0}a_n\frac{z^{5n}}{(5n)!}.
$$

Therefore

$$
\boxed{
S(z)=
\frac{25}{\left[e^{-z}+2e^{az}\cos(bz)+2e^{cz}\cos(dz)\right]^2}.
}
$$

This is a closed analytic generating function for the complete sequence.

## Step 4: derive an exact integer recurrence

From $S=D_5^{-2}$,

$$
D_5S'+2D_5'S=0.
$$

Extracting the coefficient of $z^{5n-1}/(5n-1)!$ yields

$$
\boxed{
\begin{aligned}
a_n={}&-
\sum_{k=1}^{n-1}(-1)^k
\binom{5n-1}{5k}a_{n-k}\\
&-2\sum_{k=1}^{n}(-1)^k
\binom{5n-1}{5k-1}a_{n-k},
\qquad a_0=1.
\end{aligned}
}
$$

All recurrence coefficients are integers, so induction proves

$$
\boxed{a_n\in\mathbb Z\quad(n\ge0).}
$$

The first rows split into two exact contributions:

| $n$ | First convolution | Derivative contribution | $a_n$ |
|---:|---:|---:|---:|
| 1 | 0 | 2 | 2 |
| 2 | 252 | 502 | 754 |
| 3 | 1,507,506 | 1,501,502 | 3,009,008 |
| 4 | 34,919,099,764 | 23,186,570,502 | 58,105,670,266 |

The initial terms are

$$
1, 2, 754, 3009008, 58105670266, 3690819041733782,
$$

$$
611297487195595912564,
$$

$$
225925381294863591587930378,
$$

$$
166595785020134064487394817914506, \ldots
$$

![Recurrence contributions](figures/31_arithmetic_recurrence_contributions.png)

![Digit growth](figures/32_arithmetic_digit_growth.png)

## Step 5: derive an independent composition formula

Write

$$
D_5(z)=1+u(z),
\qquad
u(z)=\sum_{k\ge1}(-1)^k\frac{z^{5k}}{(5k)!}.
$$

Because

$$
(1+u)^{-2}=\sum_{m\ge0}(-1)^m(m+1)u^m,
$$

we get, for $n\ge1$,

$$
\boxed{
a_n
=(5n)!
\sum_{m=1}^n(-1)^{n+m}(m+1)
\sum_{\substack{k_1+\cdots+k_m=n\\k_i\ge1}}
\prod_{i=1}^m\frac1{(5k_i)!}.
}
$$

This formula is independent of the logarithmic-derivative recurrence. Exact agreement between the two derivations is a separate symbolic audit.

## Step 6: embed the sequence in a polynomial semigroup

Define

$$
D_5(z)^{-r}
=\sum_{n\ge0}P_{5,n}(r)\frac{z^{5n}}{(5n)!}.
$$

The first polynomials are

$$
P_{5,0}(r)=1,
\qquad
P_{5,1}(r)=r,
$$

$$
P_{5,2}(r)=r(126r+125),
$$

$$
P_{5,3}(r)=r(126126r^2+375375r+249250).
$$

They satisfy

$$
\boxed{
P_{5,n}(r+s)
=\sum_{q=0}^n
\binom{5n}{5q}P_{5,q}(r)P_{5,n-q}(s).
}
$$

The candidate sequence is the row

$$
a_n=P_{5,n}(2).
$$

The exact mathematics is established regardless of whether a database later identifies an equivalent transformed sequence. No priority claim is needed for the proof.

---

# 7. Area VI - coupled-oscillator physics

## Step 1: write the physical system

Consider

$$
q''(t)+Kq(t)=0,
\qquad
K=\begin{pmatrix}2&-1\\-1&2\end{pmatrix}.
$$

The characteristic polynomial is

$$
\det(K-\lambda I)
=(2-\lambda)^2-1
=(\lambda-1)(\lambda-3).
$$

Normalized eigenvectors are

$$
e_s=\frac1{\sqrt2}\begin{pmatrix}1\\1\end{pmatrix},
\qquad
 e_a=\frac1{\sqrt2}\begin{pmatrix}1\\-1\end{pmatrix}.
$$

The spectral projectors are

$$
P_s=e_se_s^{\mathsf T}
=\frac12\begin{pmatrix}1&1\\1&1\end{pmatrix},
$$

$$
P_a=e_ae_a^{\mathsf T}
=\frac12\begin{pmatrix}1&-1\\-1&1\end{pmatrix}.
$$

They obey

$$
P_sP_a=0,
\qquad
P_s+P_a=I_2,
$$

and the stiffness matrix reconstructs as

$$
\boxed{K=P_s+3P_a.}
$$

Thus the mode frequencies are

$$
\omega_s=1,
\qquad
\omega_a=\sqrt3.
$$

![Normal-mode shapes](figures/33_physics_mode_shapes.png)

## Step 2: derive the exact modal solution

For initial position $q_0$ and velocity $v_0$,

$$
\boxed{
\begin{aligned}
q(t)={}&\cos(t)P_sq_0+\sin(t)P_sv_0\\
&+\cos(\sqrt3t)P_aq_0
+\frac{\sin(\sqrt3t)}{\sqrt3}P_av_0.
\end{aligned}
}
$$

Choose

$$
q_0=(1,0)^{\mathsf T},
\qquad
v_0=(0,0)^{\mathsf T}.
$$

Then

$$
P_sq_0=\frac12\begin{pmatrix}1\\1\end{pmatrix},
\qquad
P_aq_0=\frac12\begin{pmatrix}1\\-1\end{pmatrix}.
$$

Hence

$$
\boxed{
q_1(t)=\frac{\cos t+\cos(\sqrt3t)}2,
\qquad
q_2(t)=\frac{\cos t-\cos(\sqrt3t)}2.
}
$$

![Modal reconstruction](figures/34_physics_modal_reconstruction.png)

## Step 3: verify the differential equation

At $t=0$,

$$
q(0)=(P_s+P_a)q_0=q_0,
$$

and

$$
q'(0)=(P_s+P_a)v_0=v_0.
$$

Since

$$
KP_s=P_s,
\qquad
KP_a=3P_a,
$$

differentiating twice gives

$$
q''(t)=-P_sq(t)-3P_aq(t)=-Kq(t).
$$

Therefore

$$
\boxed{q''(t)+Kq(t)=0.}
$$

## Step 4: decompose and conserve energy

The total energy is

$$
E(t)=\frac12\|q'(t)\|^2+\frac12q(t)^{\mathsf T}Kq(t).
$$

Orthogonality and $K=P_s+3P_a$ give

$$
E=E_s+E_a,
$$

where

$$
E_s=\frac12\|P_sq'\|^2+\frac12\|P_sq\|^2,
$$

and

$$
E_a=\frac12\|P_aq'\|^2+\frac32\|P_aq\|^2.
$$

At $t=0$,

$$
E_s=\frac12\left\|\frac12(1,1)^{\mathsf T}\right\|^2
=\frac14,
$$

and

$$
E_a=\frac32\left\|\frac12(1,-1)^{\mathsf T}\right\|^2
=\frac34.
$$

Thus

$$
\boxed{E_s=\frac14,
\qquad E_a=\frac34,
\qquad E=1.}
$$

Symbolic differentiation proves $dE/dt=0$ identically, not only at selected time samples.

---

# 8. Area VII - nonlinear signal packets and holonomy

## Part A: nonlinear signal packets

Consider the periodic filter

$$
y[n]=x[n]+\frac12x[n-1]^2
$$

with

$$
x=(1,2,0,-1,3,1,-2,2)^{\mathsf T}.
$$

Define

$$
e[k]=x[2k],
\qquad
o[k]=x[2k+1].
$$

Then

$$
e=(1,0,3,-2)^{\mathsf T},
\qquad
o=(2,-1,1,2)^{\mathsf T}.
$$

At an even address $n=2k$, the previous sample lies in the odd channel at index $k-1$. At an odd address $n=2k+1$, the previous sample lies in the even channel at index $k$. Hence

$$
\boxed{y_e[k]=e[k]+\frac12o[k-1]^2,}
$$

$$
\boxed{y_o[k]=o[k]+\frac12e[k]^2.}
$$

Evaluating gives

$$
y_e=\left(3,2,\frac72,-\frac32\right)^{\mathsf T},
$$

$$
y_o=\left(\frac52,-1,\frac{11}{2},4\right)^{\mathsf T}.
$$

For example,

$$
y_e[0]=1+\frac12(2)^2=3,
$$

and

$$
y_o[2]=1+\frac12(3)^2=\frac{11}{2}.
$$

Interleaving gives

$$
y=\left(3,\frac52,2,-1,\frac72,\frac{11}{2},-\frac32,4\right)^{\mathsf T},
$$

which equals direct nonlinear filtering exactly.

![Nonlinear channel values](figures/35_nonlinear_channel_values.png)

## Part B: finite gauge gluing and holonomy

Let the square graph have vertices $v_0,v_1,v_2,v_3$. Choose

$$
U_0=I,
\qquad
U_1=\begin{pmatrix}3/5&-4/5\\4/5&3/5\end{pmatrix},
$$

$$
U_2=\begin{pmatrix}5/13&-12/13\\12/13&5/13\end{pmatrix},
$$

$$
U_3=\begin{pmatrix}7/25&-24/25\\24/25&7/25\end{pmatrix}.
$$

Define edge transports by

$$
B_{vu}=U_vU_u^{-1}.
$$

The four exact edges are

$$
B_{10}=\begin{pmatrix}3/5&-4/5\\4/5&3/5\end{pmatrix},
$$

$$
B_{21}=\begin{pmatrix}63/65&-16/65\\16/65&63/65\end{pmatrix},
$$

$$
B_{32}=\begin{pmatrix}323/325&-36/325\\36/325&323/325\end{pmatrix},
$$

$$
B_{03}=\begin{pmatrix}7/25&24/25\\-24/25&7/25\end{pmatrix}.
$$

The cycle holonomy is

$$
H=B_{03}B_{32}B_{21}B_{10}.
$$

By telescoping,

$$
H
=U_0U_3^{-1}U_3U_2^{-1}U_2U_1^{-1}U_1U_0^{-1}
=I.
$$

Thus the flat system glues exactly.

![Holonomy edge matrices](figures/36_holonomy_edge_matrices.png)

## Negative control

Perturb the closing edge by

$$
Q=\begin{pmatrix}3/5&-4/5\\4/5&3/5\end{pmatrix},
\qquad
B_{03}^{\mathrm{bad}}=QB_{03}.
$$

Then

$$
H_{\mathrm{bad}}
=B_{03}^{\mathrm{bad}}B_{32}B_{21}B_{10}
=QH=Q.
$$

The obstruction is

$$
H_{\mathrm{bad}}-I
=
\begin{pmatrix}-2/5&-4/5\\4/5&-2/5\end{pmatrix}.
$$

Its squared Frobenius norm is

$$
\begin{aligned}
\|H_{\mathrm{bad}}-I\|_F^2
&=\left(-\frac25\right)^2
+\left(-\frac45\right)^2
+\left(\frac45\right)^2
+\left(-\frac25\right)^2\\
&=\frac4{25}+\frac{16}{25}+\frac{16}{25}+\frac4{25}\\
&=\boxed{\frac85}.
\end{aligned}
$$

The nonzero obstruction proves that the perturbed cycle cannot be globally glued with the chosen root normalization.

---

# 9. Cross-domain proof matrix

| Area | Packet object | Operation or transfer | Exact synthesis certificate | Independent negative control or second derivation |
|---|---|---|---|---|
| Linear algebra | coordinate subspaces | matrix transfer blocks | $\sum_{\alpha,\beta}P_\beta TP_\alpha=T$ | second-operator path law |
| Signals | residue, Haar, Fourier packets | interleaving and inverse transforms | three exact inverse calculations | incomplete bands would leave a residual |
| Quantum | parity sectors | gate path expansion | four-path sum equals Bell state | two paths vanish exactly |
| Probability | partition-constant observables | conditional expectation and Bayes update | projector and sufficient-coarsening identities | nonsufficient likelihood defect |
| Special functions | residue-zero exponential packet | reciprocal and parameter convolution | recurrence and composition formula agree | separate hypergeometric coefficient check |
| Physics | normal-mode eigenspaces | spectral evolution | modal sum solves the original ODE | energy partition and direct ODE residual |
| Nonlinear/geometry | even-odd channels and transport edges | nonlinear memory and cycle product | interleaving and flat holonomy | perturbed cycle obstruction $8/5$ |

![Cross-domain proof matrix](figures/37_cross_domain_proof_matrix.png)

The common finite mechanism is therefore not merely verbal:

$$
\boxed{
\text{declare packets}
\longrightarrow
\text{analyze}
\longrightarrow
\text{operate or transfer}
\longrightarrow
\text{refine or transport}
\longrightarrow
\text{synthesize}
\longrightarrow
\text{compute the residual}.
}
$$

Across the seven examples, the exact residuals are zero whenever the complete compatible packet data are retained. The deliberately incompatible or insufficient examples produce explicit nonzero residual packets rather than being hidden by the notation.

---

# 10. Verification architecture

The accompanying source release contains a foundational layer plus the three retained domain-audit layers:

1. **Eleven seed-to-reconstruction tests:** generation, relations, packet completeness, transfer reconstruction, path multiplication, multi-atlas synthesis, nonlinear reconstruction, and obstruction localization.
2. **Seven primary certificate tests:** one for each mathematical area.
3. **Seven independent re-derivation tests:** the same domain results are rebuilt from the displayed definitions rather than by calling the primary certificate functions.
4. **Seven detailed intermediate audits:** step-level block contributions, packet paths, recurrence splits, same-coarse-prior witnesses, modal coordinates, and exact edge products are checked separately.

The final test result is

$$
\boxed{32/32\text{ tests passed}.}
$$

The release contains 61 vector-PDF figures and 61 matching PNG figures: 23 foundational figures plus the retained 38 domain figures. The final PDF has 140 pages. Legends are placed outside crowded data regions, long labels are wrapped or resized, colorbars use separate axes, and every page was rendered to check for clipping, overlap, broken glyphs, and misalignment.

