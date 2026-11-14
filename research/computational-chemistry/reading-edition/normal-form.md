# The 21-parameter molecular normal form

**Komorebi P. · Reviewed reading edition · 13 November 2026**

This note identifies the operator family before attempting recovery. It
separates three objects: the input integrals, the resulting nine-state
Hamiltonian, and its unique normal-form coefficients. The original checked
source remains available through **Source identity and downloads** below.

## Sector, basis and conventions

There are three real orthonormal spatial orbitals, numbered 0, 1 and 2.
The sector contains two alpha electrons and one beta electron. Alpha has
spin projection $+1/2$ and beta has projection $-1/2$, in units with
$\hbar=1$. Thus the total spin projection is $M_s=1/2$.

Order the six spin orbitals as alpha 0, 1, 2, followed by beta 0, 1, 2.
Creation operators in a determinant follow this ascending order. The
nine determinant coordinates used by the probes and code are:

| Row | Occupied alpha orbitals | Occupied beta orbital |
|---|---|---|
| 0 | 0, 1 | 0 |
| 1 | 0, 1 | 1 |
| 2 | 0, 1 | 2 |
| 3 | 0, 2 | 0 |
| 4 | 0, 2 | 1 |
| 5 | 0, 2 | 2 |
| 6 | 1, 2 | 0 |
| 7 | 1, 2 | 1 |
| 8 | 1, 2 | 2 |

All coefficients are real. Define the spin-free one-body operators and
electronic Hamiltonian by

$$
E_{pq}=\sum_{\sigma\in\{\alpha,\beta\}}
a^\dagger_{p\sigma}a_{q\sigma},
$$

$$
H=\sum_{p,q}h_{pq}E_{pq}
+\frac12\sum_{p,q,r,s}g_{pqrs}
\bigl(E_{pq}E_{rs}-\delta_{qr}E_{ps}\bigr).
$$

Every spatial index ranges from 0 to 2. The one-electron matrix $h$ is
symmetric. The two-electron tensor uses chemists' notation and satisfies

$$
g_{pqrs}=g_{qprs}=g_{pqsr}=g_{rspq}.
$$

These symmetries give six independent entries of $h$ and 21 of $g$.
The factor $1/2$ and the subtracted contraction are part of the physical
operator definition. The contraction tensor accepted by some FCI software
interfaces absorbs one-body terms; it must not be confused with this $g$.
The [source comparison](literature.md) explains the PySCF convention.

## Hole/electron coordinates

Let $e_{ij}$ be the 3-by-3 matrix unit. Associate $e_{ij}$ with $(-1)^i$
times the determinant whose alpha orbitals omit $i$ and whose beta orbital
is $j$. Denote the resulting orthogonal signed-permutation matrix by $U_h$.
For a matrix $X$, list its entries by rows:

$$
\operatorname{vec}_r(X)
=(X_{00},X_{01},X_{02},X_{10},\ldots,X_{22})^{\mathsf T}.
$$

The determinant vector is $U_h\operatorname{vec}_r(X)$. In particular,
the matrix of the Hamiltonian in these coordinates is $U_h^{\mathsf T}HU_h$.
For any matrices $A$ and $X$, write $[A,X]=AX-XA$.

On the alpha two-electron space, a one-body matrix $A$ acts as
$\operatorname{tr}(A)X-A^{\mathsf T}X$; the beta electron contributes
$XA^{\mathsf T}$. Their sum gives

$$
E_{pq}X=\delta_{pq}X-[e_{qp},X].
$$

The transpose in this formula is essential. For symmetric $h$, its
one-body contribution is $\operatorname{tr}(h)X-[h,X]$.

## Statement of the normal form

Choose the following basis of traceless symmetric 3-by-3 matrices:

$$
T_1=\operatorname{diag}(1,-1,0),\qquad
T_2=\operatorname{diag}(1,1,-2),
$$

$$
T_3=e_{01}+e_{10},\qquad
T_4=e_{02}+e_{20},\qquad
T_5=e_{12}+e_{21}.
$$

They are orthogonal for the Frobenius inner product
$\langle A,B\rangle_F=\operatorname{tr}(A^{\mathsf T}B)$, with squared
norms $(2,6,2,2,2)$.

**Theorem.** The restricted Hamiltonians are exactly the linear maps

$$
\Phi(X)=tX+[K,X]+\sum_{a,b=1}^{5}C_{ab}[T_a,[T_b,X]],
$$

where $t$ is real, $K$ is traceless real symmetric, and $C$ is real
symmetric. The parameters $(t,K,C)$ are unique. Therefore the operator
family has dimension $1+5+15=21$.

The operator in determinant coordinates is $U_h\Phi U_h^{\mathsf T}$,
where $\Phi$ in this expression denotes its row-vectorized 9-by-9 matrix.
The energy shift $t$ is included in the family.

## Spanning, with an explicit coefficient dictionary

The within-pair symmetries of $g$ make its quadratic commutator contribution
depend only on symmetric matrices. Scalar matrices commute with every
$X$, so only the five traceless directions remain.

The following formulas make that reduction explicit. Put

$$
A_{rs}=\sum_p g_{pprs},\qquad
R_{ps}=\sum_q g_{pqqs},\qquad
s_0=\operatorname{tr}(A),\qquad u_0=\operatorname{tr}(R),
$$

and let $D=\operatorname{diag}(2,6,2,2,2)$. Define

$$
\Gamma_{ab}=\sum_{p,q,r,s}(T_a)_{pq}g_{pqrs}(T_b)_{rs}.
$$

Writing $B_0=B-\operatorname{tr}(B)I_3/3$ for a traceless part gives

$$
t=\operatorname{tr}(h)+\frac{s_0-u_0}{2},\qquad
K=\left(-h-A+\frac R2\right)_0,\qquad
C=\frac12D^{-1}\Gamma D^{-1}.
$$

To obtain these formulas, expand each $E_{pq}$ as
$\delta_{pq}I-\operatorname{ad}(e_{qp})$. The constant terms from the
two-electron part are $(s_0-u_0)I/2$. Its linear commutator has coefficient
$-A+R/2$. Projecting the two symmetric index pairs onto the orthogonal
$T_a$ basis gives the displayed $C$. This accounts for the constant,
linear and quadratic terms separately.

Conversely, for arbitrary allowed $(t,K,C)$, set

$$
g_{pqrs}=2\sum_{a,b}C_{ab}(T_a)_{pq}(T_b)_{rs},
\qquad R_{ps}=\sum_qg_{pqqs},
\qquad h=-K+\frac R2+\frac t3I_3.
$$

The tensor has all the required symmetries, and $A=0$ because each $T_a$
is traceless. Substituting into the dictionary gives exactly $(t,K,C)$.
Thus every normal-form operator occurs.

## Uniqueness and direct extraction from an operator

For a map on 3-by-3 matrices, define its Choi matrix to have $(i,j)$ block
$\Phi(e_{ij})$. Let $v=\operatorname{vec}_r(I_3)$ and let

$$
P_0=I_9-\frac{vv^{\mathsf T}}3,\qquad
W=\begin{pmatrix}\operatorname{vec}_r(T_1)&\cdots&
\operatorname{vec}_r(T_5)\end{pmatrix}.
$$

Here $W^{\mathsf T}W=D$. Reshuffling the normal-form terms yields

$$
P_0\operatorname{Choi}(\Phi)P_0=-2WCW^{\mathsf T}.
$$

Scalar, one-body and anticommutator terms have a factor $v$ on at least
one side and disappear under the compression. The two sandwich terms
in the double commutator give the remaining expression. Symmetry of
$C$ combines them into the factor $-2$.

The columns of $W$ are independent, so a zero operator forces $C=0$.
Then $\Phi(I_3)=tI_3$ forces $t=0$. Finally, a matrix commuting with
every $X$ is scalar; the traceless condition forces $K=0$. This proves
uniqueness.

It also gives a direct recovery dictionary when the full operator is known:

$$
C=-\frac12D^{-1}W^{\mathsf T}\operatorname{Choi}(\Phi)WD^{-1},
\qquad t=\frac{v^{\mathsf T}\Phi v}{3}.
$$

Subtract $tI_9$ and the reconstructed double-commutator part to obtain
$\Psi=K\otimes I_3-I_3\otimes K^{\mathsf T}$. Then
$K=\operatorname{Tr}_2(\Psi)/3$, where
$[\operatorname{Tr}_2(\Psi)]_{ik}=\sum_j\Psi_{3i+j,3k+j}$.
These formulas apply after changing from determinant to hole/electron
coordinates. Applying the Choi reshuffling directly to the determinant
matrix would use the wrong coordinates.

## Integral nonuniqueness and positivity

The 27 integral coefficients contain a six-dimensional redundancy. For
any symmetric $h$, define

$$
g^h_{pqrs}=\frac{h_{pq}\delta_{rs}+\delta_{pq}h_{rs}}2.
$$

On a fixed three-electron sector, this tensor contributes the same operator
as the one-body $h$. More generally, its two-electron contribution on an
$N$-electron sector is $(N-1)\sum_{pq}h_{pq}E_{pq}/2$: the number
operator supplies $N$ and the contraction subtracts one. For $N=3$,
the coefficient is one. Thus $(h,g)$ and
$(0,g+g^h)$ agree. The six independent choices of $h$ account for the
entire kernel, since the input dimension is 27 and the output dimension
is 21. Recovering the operator cannot recover an original integral
decomposition uniquely.

Call an integral tensor positive if

$$
\sum_{p,q,r,s}g_{pqrs}X_{pq}X_{rs}\ge0
\quad\text{for every real symmetric }X.
$$

True real Coulomb integrals satisfy this necessary condition through the
nonnegative Coulomb self-energy of the orbital-product density. With
unrestricted symmetric $h$, the existence of a positive-integral
representative is **equivalent to $C\succeq0$**. Necessity follows from
$C=D^{-1}\Gamma D^{-1}/2$. Sufficiency follows from the explicit tensor
$g=2\sum C_{ab}T_a\otimes T_b$ above.

This equivalence concerns a positive-Gram relaxation. It does not establish
that every such tensor is realizable by common orbitals and a Coulomb
potential, or that the original molecular $h$ and $g$ were identified.

## Coefficient errors and total spin

The coordinate change and Choi reshuffling preserve Frobenius norm;
orthogonal compression cannot increase it. Since every diagonal entry of
$D$ is at least 2,

$$
\|WCW^{\mathsf T}\|_F^2
=\sum_{a,b}D_{aa}D_{bb}C_{ab}^2\ge4\|C\|_F^2.
$$

Consequently, for two family members,

$$
\|\Delta C\|_F\le\frac14\|\Delta H\|_F.
$$

Every operator in the family preserves total spin. In determinant
coordinates, put $q=(0,0,1,0,-1,0,1,0,0)^{\mathsf T}$. Then
$S^2=3I_9/4+qq^{\mathsf T}$: the eight-dimensional doublet subspace has
eigenvalue $3/4$, and the quartet direction $q=U_hv$ has eigenvalue
$15/4$. Spin conservation alone permits a larger operator family.

The [three-query theorem](three-queries.md) identifies this particular
21-dimensional family and quantifies the effect of action errors.
