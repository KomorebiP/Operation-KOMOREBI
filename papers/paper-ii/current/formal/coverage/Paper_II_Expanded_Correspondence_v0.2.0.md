# Paper II — expanded manuscript / formal-source correspondence

Current included traditional/chapters LaTeX, not inherited duplicate manuscripts or atlas repetitions. Manual source-level mathematical correspondence assessment; no Lean elaboration, kernel acceptance or external proof review. Source targets are contextual supporting contracts, not a claim that every referenced declaration individually proves the full statement.

## Counts

81 explicit environments; 53 proof-level records; 50 proof bodies; 3 algorithm listings.

{'whole_statement_source_match': 19, 'partial_restricted_or_unassembled': 21, 'no_statement_level_map_in_selected_tree': 13}

The frozen map includes definitions, the Smith phase identity and three algorithm specifications. It is not a denominator directly comparable with these 53 current theorem/proposition/corollary environments. Several current records repeat or specialize one scoped result.

## Status meanings

**whole_statement_source_match:** The displayed statement and hypotheses match the located formal source at the recorded typed scope; exact wrapper/equivalence not newly compiled. This remains a review assessment, not formal certification.

**partial_restricted_or_unassembled:** Relevant results exist, but an explicit construction, broader generality, domain identification, or final wrapper remains.

**no_statement_level_map_in_selected_tree:** No complete endpoint for the current statement located among the 15 selected project modules. Not a claim that the written statement is false or that no imported theorem exists.

## thm:children_transitivity — Children, parents, and transitivity

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/02_coordinates.tex`, line 45. SHA-256 `c10c5318fa540ed037e4d11941d82d985fd5a40a6a54f1a5b5f8f92f41983407`.

Parent/child absorption in both orders and transitivity have the displayed finite scope.

Related frozen contract rows: 2.

```tex
\label{thm:children_transitivity}\label{thm:nested-refinement}
Suppose that $\Qcal$ refines $\Pcal$ through $\rho$.  Then
\[
P_\alpha Q_\beta
=
Q_\beta P_\alpha
=
\begin{cases}
Q_\beta & \rho(\beta)=\alpha,\\
0 & \rho(\beta)\ne\alpha.
\end{cases}
\]
Hence $Q_\beta X\subseteq P_{\rho(\beta)}X$.  If a third packet system $\Rcal$ refines $\Qcal$, then $\Rcal$ refines $\Pcal$ through the composite parent map.
```

## thm:coordinate_coherence — Exact coordinate change and coherence

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/02_coordinates.tex`, line 95. SHA-256 `c10c5318fa540ed037e4d11941d82d985fd5a40a6a54f1a5b5f8f92f41983407`.

Mutual inverse, cocycle and parent/child component laws are supplied by the mapped coordinate declarations.

Related frozen contract rows: 3, 4.

```tex
\label{thm:coordinate_coherence}\label{prop:perfect-reconstruction}
For any two packet systems on $X$,
\[
C_{\Pcal\leftarrow\Qcal}J_{\Qcal\leftarrow\Pcal}=I_{X^{\Pcal}},
\qquad
J_{\Qcal\leftarrow\Pcal}C_{\Pcal\leftarrow\Qcal}=I_{X^{\Qcal}}.
\]
For three packet systems $\Pcal$, $\Qcal$, and $\Rcal$ on $X$,
\[
J_{\Rcal\leftarrow\Qcal}J_{\Qcal\leftarrow\Pcal}
=
J_{\Rcal\leftarrow\Pcal},
\]
\[
C_{\Pcal\leftarrow\Qcal}C_{\Qcal\leftarrow\Rcal}
=
C_{\Pcal\leftarrow\Rcal}.
\]
If $\Qcal$ refines $\Pcal$ through $\rho$, then
\[
\bigl(J_{\Qcal\leftarrow\Pcal}x\bigr)_\beta
=
Q_\beta x_{\rho(\beta)},
\qquad
\bigl(C_{\Pcal\leftarrow\Qcal}y\bigr)_\alpha
=
\sum_{\rho(\beta)=\alpha}y_\beta.
\]
```

## cor:orthogonal_isometry — Orthogonal Hilbert packets

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/02_coordinates.tex`, line 153. SHA-256 `c10c5318fa540ed037e4d11941d82d985fd5a40a6a54f1a5b5f8f92f41983407`.

Linear equivalence is supplied. The Hilbert direct-sum inner product and unitarity conclusion are not assembled in the selected tree.

Related frozen contract rows: 3, 4.

```tex
\label{cor:orthogonal_isometry}
If $X$ is a Hilbert space and every packet system in the tower consists of orthogonal projections, then analysis and synthesis are unitary.  Every coordinate change in \cref{thm:coordinate_coherence} is unitary.
```

## thm:block_refinement — Refinement of operator blocks

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/02_coordinates.tex`, line 215. SHA-256 `c10c5318fa540ed037e4d11941d82d985fd5a40a6a54f1a5b5f8f92f41983407`.

Independent-source/target block refinement and coordinate naturality give both displayed finite identities.

Related frozen contract rows: 4, 5.

```tex
\label{thm:block_refinement}\label{thm:transfer-block-refinement}
Suppose that $\Qcal$ refines $\Pcal$ through $\rho$.  Then
\[
T^{\Pcal}_{ba}
=
\sum_{\substack{\rho(\beta)=b\\\rho(\alpha)=a}}
T^{\Qcal}_{\beta\alpha}.
\]
The matrix of $T$ in fine coordinates is related to the matrix in coarse coordinates by
\[
[T]_{\Pcal}
=
C_{\Pcal\leftarrow\Qcal}[T]_{\Qcal}J_{\Qcal\leftarrow\Pcal}.
\]
```

## cor:block_support_refinement — Support under refinement

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/02_coordinates.tex`, line 250. SHA-256 `c10c5318fa540ed037e4d11941d82d985fd5a40a6a54f1a5b5f8f92f41983407`.

Block-sum and absorption identities exist. The zero-coarse iff all-zero-descendants equivalence still needs its exact wrapper.

Related frozen contract rows: 2, 5.

```tex
\label{cor:block_support_refinement}
Under the hypotheses of \cref{thm:block_refinement}, a coarse block $T^{\Pcal}_{ba}$ is zero if and only if every fine descendant block
\[
T^{\Qcal}_{\beta\alpha}
\qquad
\bigl(\rho(\beta)=b,\ \rho(\alpha)=a\bigr)
\]
is zero.
```

## thm:common_refinement — Common refinement of commuting packet systems

**Status:** no_statement_level_map_in_selected_tree
**Source:** `editable/traditional/chapters/02_coordinates.tex`, line 279. SHA-256 `c10c5318fa540ed037e4d11941d82d985fd5a40a6a54f1a5b5f8f92f41983407`.

No selected declaration constructs the nonzero commuting product family, its two surjections, or the finite-many-family extension.

Related frozen contract rows: none with a complete endpoint.

```tex
\label{thm:common_refinement}
Let $\Pcal=(P_\alpha)_{\alpha\in I}$ and $\Qcal=(Q_\beta)_{\beta\in J}$ be packet systems on $X$.  Assume
\[
P_\alpha Q_\beta=Q_\beta P_\alpha
\]
for all $\alpha$ and $\beta$.  Remove the zero operators from the family
\[
R_{\alpha\beta}=P_\alpha Q_\beta.
\]
The remaining operators form a packet system that refines both $\Pcal$ and $\Qcal$.  The same statement holds for any finite collection of pairwise commuting packet systems.
```

## prop:coarsest_common_refinement — Coarsest common refinement

**Status:** no_statement_level_map_in_selected_tree
**Source:** `editable/traditional/chapters/02_coordinates.tex`, line 314. SHA-256 `c10c5318fa540ed037e4d11941d82d985fd5a40a6a54f1a5b5f8f92f41983407`.

The universal/coarsest property of the nonzero commuting product construction is not represented as a statement-level endpoint.

Related frozen contract rows: none with a complete endpoint.

```tex
\label{prop:coarsest_common_refinement}
Under the hypotheses of \cref{thm:common_refinement}, let $\Rcal$ be a packet system that refines both $\Pcal$ and $\Qcal$.  Then $\Rcal$ refines the nonzero product family $(P_\alpha Q_\beta)$.  Hence that product family is the coarsest packet system that refines both $\Pcal$ and $\Qcal$.
```

## prop:residue_algebra — Residue packet algebra

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/02_coordinates.tex`, line 369. SHA-256 `c10c5318fa540ed037e4d11941d82d985fd5a40a6a54f1a5b5f8f92f41983407`.

Coefficient idempotence, orthogonality and completeness are proved. Nonzero selectors and the whole packet-system witness on formal power series are not assembled.

Related frozen contract rows: 6.

```tex
\label{prop:residue_algebra}\label{prop:residue-algebra}
For every commutative ring $R$, the operators $(P_{N,j})_{0\leq j<N}$ satisfy the identities below.  If $R$ is nonzero, they form a packet system on $R[[z]]$:
\[
P_{N,i}P_{N,j}=\delta_{ij}P_{N,j},
\qquad
\sum_{j=0}^{N-1}P_{N,j}=I.
\]
```

## thm:root-of-unity — Root-of-unity realization

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/02_coordinates.tex`, line 390. SHA-256 `c10c5318fa540ed037e4d11941d82d985fd5a40a6a54f1a5b5f8f92f41983407`.

The finite semiring Fourier-table hypothesis is explicit; the field primitive-root branch constructs that certificate.

Related frozen contract rows: 7.

```tex
\label{thm:root-of-unity}
Let $R$ be a commutative semiring, let $N>0$, and suppose
$\omega,\omega^\vee,\eta\in R$ satisfy $\omega^N=1$ and the finite
$N\times N$ Fourier orthogonality table
\[
\eta\sum_{k=0}^{N-1}(\omega^\vee)^{jk}\omega^{rk}
=
\begin{cases}
1,&r=j,\\
0,&r\ne j,
\end{cases}
\qquad 0\le j,r<N.
\]
Then
\[
\boxed{
P_{N,j}
=
\eta\sum_{k=0}^{N-1}(\omega^\vee)^{jk}U^k.
}
\]
In particular, if $R$ is a field, $N>0$, and $\omega$ is a primitive
$N$th root of unity, the certificate holds with
$\omega^\vee=\omega^{-1}$ and $\eta=N^{-1}$.
```

## thm:character_realization — Character realization

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/02_coordinates.tex`, line 437. SHA-256 `c10c5318fa540ed037e4d11941d82d985fd5a40a6a54f1a5b5f8f92f41983407`.

Field primitive-root Fourier equality is the stated coefficientwise character-average realization.

Related frozen contract rows: 7.

```tex
\label{thm:character_realization}
Let $\bbk$ be a field, assume that $N$ is nonzero in $\bbk$, and suppose that $\bbk$ contains a primitive $N$th root of unity $\omega$.  Define
\[
(UF)(z)=F(\omega z).
\]
Then
\[
P_{N,j}
=
\frac1N\sum_{k=0}^{N-1}\omega^{-jk}U^k.
\]
```

## thm:residue_refinement — Nested residue refinement

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/02_coordinates.tex`, line 462. SHA-256 `c10c5318fa540ed037e4d11941d82d985fd5a40a6a54f1a5b5f8f92f41983407`.

The N*k selector sum is present. The general divisibility presentation and nonzero formal-power-series Refines witness need assembly.

Related frozen contract rows: 1, 8.

```tex
\label{thm:residue_refinement}\label{thm:polyphase-refinement}
Let $N,M$ be positive integers with $N$ dividing $M$, and let $0\leq j<N$.  Then
\[
P_{N,j}
=
\sum_{\substack{0\leq s<M\\s\equiv j\pmod N}}P_{M,s}.
\]
When $R$ is nonzero, the packet system modulo $M$ refines the packet system modulo $N$.
```

## thm:crt_factorization — Coprime factorization

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/02_coordinates.tex`, line 484. SHA-256 `c10c5318fa540ed037e4d11941d82d985fd5a40a6a54f1a5b5f8f92f41983407`.

The composite selector identity and the residue-label bijection are both present; this is address factorization, not integral spectral separation.

Related frozen contract rows: 9.

```tex
\label{thm:crt_factorization}
Let $A$ and $B$ be coprime positive integers.  For each $j$ modulo $AB$, write
\[
j_A=j\pmod A,
\qquad
j_B=j\pmod B.
\]
Then
\[
P_{AB,j}=P_{A,j_A}P_{B,j_B}.
\]
Every pair $(j_A,j_B)$ occurs for one residue $j$ modulo $AB$.
```

## cor:dyadic_odd_coordinates — Dyadic and odd coordinates

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/02_coordinates.tex`, line 502. SHA-256 `c10c5318fa540ed037e4d11941d82d985fd5a40a6a54f1a5b5f8f92f41983407`.

The power-of-two/odd selector identity is directly included in the CRT declarations.

Related frozen contract rows: 9.

```tex
\label{cor:dyadic_odd_coordinates}\label{thm:dyadic-odd}
Write $N=2^aM$ with $M$ odd.  Every residue packet modulo $N$ is the product of one packet modulo $2^a$ and one packet modulo $M$.
```

## thm:weighted_inverse — Weighted inverse

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/03_weighted.tex`, line 32. SHA-256 `56aeaee491cd3d2d349e53e8ab7e8d10280e51892c5cb682e665a7088fd16988`.

Nilpotent inverse, norm-convergent inverse and finite filtration quotients are present. General separated complete filtered convergence is not supplied.

Related frozen contract rows: 10, 11.

```tex
\label{thm:weighted_inverse}
Let $\Bcal$ be a complete filtered algebra.  Let $D\in\Bcal$ be invertible with
\[
D,D^{-1}\in F^0\Bcal.
\]
Let $E$ be a finite set and suppose
\[
T=D+\sum_{e\in E}N_e,
\qquad
N_e\in F^{w(e)}\Bcal,
\qquad
w(e)\geq1.
\]
Set
\[
A_e=D^{-1}N_e.
\]
For a word $\gamma=(e_1,\ldots,e_r)$, write
\[
A_\gamma=A_{e_r}\cdots A_{e_1},
\qquad
W(\gamma)=\sum_{j=1}^rw(e_j).
\]
The empty word has weight zero and contributes the identity.  Then $T$ is invertible and
\[
T^{-1}
=
\sum_\gamma(-1)^{|\gamma|}A_\gamma D^{-1}.
\]
The series converges in the filtration, and the term indexed by $\gamma$ belongs to $F^{W(\gamma)}\Bcal$.
```

## thm:block_path_formula — Block path formula

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/03_weighted.tex`, line 86. SHA-256 `56aeaee491cd3d2d349e53e8ab7e8d10280e51892c5cb682e665a7088fd16988`.

Block refinement and weighted words are supplied separately. A completed inverse assembled as endpoint-compatible graph paths is not established.

Related frozen contract rows: 5, 10, 11.

```tex
\label{thm:block_path_formula}
Let $\Pcal=(P_\alpha)_{\alpha\in I}$ be a finite packet system in a complete filtered algebra of operators.  Suppose
\[
D=\sum_\alpha P_\alpha D P_\alpha
\]
belongs to $\Bcal$ and is invertible on every packet.  Assume that the assembled inverse
\[
D^{-1}=\sum_\alpha D_\alpha^{-1}P_\alpha\in\Bcal=F^0\Bcal,
\qquad D_\alpha=P_\alpha DP_\alpha,
\]
where each packet inverse is extended by zero to the other packets.  Let the edge set be finite, assume $w(e)\geq1$ for every edge, and write
\[
N=\sum_{e:\alpha\to\beta}N_e,
\qquad
N_e=P_\beta N_eP_\alpha,
\qquad
N_e\in F^{w(e)}\Bcal.
\]
For an edge $e:\alpha\to\beta$, put
\[
A_e=(P_\beta DP_\beta)^{-1}N_e.
\]
Then the block from $P_\alpha X$ to $P_\beta X$ of $(D+N)^{-1}$ is
\[
P_\beta(D+N)^{-1}P_\alpha
=
\sum_{\gamma:\alpha\leadsto\beta}
(-1)^{|\gamma|}A_\gamma D_\alpha^{-1},
\]
where $D_\alpha=P_\alpha DP_\alpha$ and the sum runs over directed paths from $\alpha$ to $\beta$, including the empty path when $\alpha=\beta$.
```

## cor:minimum_path_weight — Minimum path weight

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/03_weighted.tex`, line 126. SHA-256 `56aeaee491cd3d2d349e53e8ab7e8d10280e51892c5cb682e665a7088fd16988`.

Finite word-weight lower bounds are present. The endpoint shortest-path valuation and no-path zero conclusion for the completed inverse are not assembled.

Related frozen contract rows: 11, 12.

```tex
\label{cor:minimum_path_weight}
For packets $\alpha$ and $\beta$, let $d(\alpha,\beta)$ be the least total weight of a directed path from $\alpha$ to $\beta$, with $d=\infty$ when no path exists.  Use the convention $F^\infty\Bcal=\bigcap_{L\geq0}F^L\Bcal=0$.  If $\alpha\ne\beta$, then
\[
P_\beta(D+N)^{-1}P_\alpha
\in
F^{d(\alpha,\beta)}\Bcal.
\]
If there is no path from $\alpha$ to $\beta$, the block is zero.
```

## cor:acyclic_inverse — Acyclic transfer graph

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/03_weighted.tex`, line 154. SHA-256 `56aeaee491cd3d2d349e53e8ab7e8d10280e51892c5cb682e665a7088fd16988`.

The inverse theorem consumes nilpotence. The finite acyclic support argument constructing nilpotence is not a selected endpoint.

Related frozen contract rows: 10, 12.

```tex
\label{cor:acyclic_inverse}
If the packet transfer graph is acyclic, then $D^{-1}N$ is nilpotent.  The inverse in \cref{thm:block_path_formula} is a finite sum and does not require completeness of the filtration.
```

## cor:inverse_stability — Stability of inversion at finite precision

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/03_weighted.tex`, line 162. SHA-256 `56aeaee491cd3d2d349e53e8ab7e8d10280e51892c5cb682e665a7088fd16988`.

An algebraic inverse sandwich identity and filtration primitives exist. Their exact ideal-valued inverse-stability conclusion needs a wrapper.

Related frozen contract rows: 11, 21.

```tex
\label{cor:inverse_stability}
Let $T$ and $\widetilde T$ be invertible elements of $F^0\Bcal$.  If
\[
T-\widetilde T\in F^L\Bcal,
\]
then
\[
T^{-1}-\widetilde T^{-1}\in F^L\Bcal.
\]
```

## cor:finite_precision — Exact finite precision truncation

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/03_weighted.tex`, line 183. SHA-256 `56aeaee491cd3d2d349e53e8ab7e8d10280e51892c5cb682e665a7088fd16988`.

The quotient inverse/pruned finite-word formula is present. The reference to the actual completed inverse and its difference in F^L requires the filtered completion result.

Related frozen contract rows: 10, 11.

```tex
\label{cor:finite_precision}
Under the hypotheses of \cref{thm:weighted_inverse}, define
\[
R_L
=
\sum_{W(\gamma)<L}(-1)^{|\gamma|}A_\gamma D^{-1}.
\]
Then
\[
T^{-1}-R_L\in F^L\Bcal,
\]
\[
TR_L-I\in F^L\Bcal,
\qquad
R_LT-I\in F^L\Bcal.
\]
Thus $R_L$ is the exact inverse in $\Bcal/F^L\Bcal$.
```

## thm:weighted-inverse — Certified weighted inverse

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/03_weighted.tex`, line 269. SHA-256 `56aeaee491cd3d2d349e53e8ab7e8d10280e51892c5cb682e665a7088fd16988`.

This explicitly certified statement is exactly the supplied-inverse/nilpotence branch and the separate complete normed-ring branch.

Related frozen contract rows: 10.

```tex
\label{thm:weighted-inverse}
Let $R$ be a possibly noncommutative ring, let $D^{-1}$ be a supplied
two-sided inverse of $D$, and put $A=D^{-1}H$.
\begin{enumerate}[label=(\alph*)]
\item If $A^r=0$, then $D+H$ has the two-sided inverse
\[
\boxed{(D+H)^{-1}=\left(\sum_{k=0}^{r-1}(-A)^k\right)D^{-1}.}
\]
\item If $R$ is a complete normed ring and $\lVert A\rVert<1$, then
$\sum_{k\ge0}(-A)^k$ converges and
\[
\boxed{(D+H)^{-1}=\left(\sum_{k\ge0}(-A)^k\right)D^{-1}.}
\]
\end{enumerate}
```

## cor:finite-precision — Finite precision

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/03_weighted.tex`, line 304. SHA-256 `56aeaee491cd3d2d349e53e8ab7e8d10280e51892c5cb682e665a7088fd16988`.

Finite quotient, weighted pruning, diagonal inverse and improved minimum-weight cutoff are all explicit mapped endpoints.

Related frozen contract rows: 11, 24.

```tex
\label{cor:finite-precision}
Let $F^\bullet R$ be a multiplicative decreasing filtration and let
$q_L:R\to R_L$ be a ring homomorphism that kills $F^L R$. Suppose
\[
H=\sum_{e\in E}H_e,
\qquad D^{-1}H_e\in F^{w(e)}R,
\qquad w(e)\ge1,
\]
with $E$ finite. Then $q_L(D^{-1}H)^L=0$, the finite sum in
\cref{thm:weighted-inverse}(a) is a two-sided inverse after applying $q_L$,
and its word expansion may discard every word of weight at least $L$.
More explicitly, for a length cutoff $N$, define
\[
S^{\mathrm{pr}}_{L,N}
=
\sum_{n=0}^{N-1}(-1)^n
\sum_{\substack{\gamma\in E^n\\W(\gamma)<L}}A_\gamma.
\]
Lean proves directly that $q_L(S^{\mathrm{pr}}_{L,N})$ equals the mapped
geometric inverse whenever $q_L(A^N)=0$, and hence is a two-sided inverse of
$q_L(I+A)$, where $A=\sum_eA_e=D^{-1}H$. With the supplied two-sided
inverse $D^{-1}$ of $D$, this gives the explicit two-sided inverse
\[
\boxed{q_L\!\left(S^{\mathrm{pr}}_{L,N}D^{-1}\right)}
\quad\text{of}\quad q_L(D+H).
\]
If every edge weight is at least $m$ and $L\le mN$, then the nilpotence
condition follows from the filtration data because
$m|\gamma|\le W(\gamma)$. For $m>0$, the executable choice
$N=\lceil L/m\rceil$ satisfies $L\le mN$. This elementary ceiling inequality
is also proved in Lean. The choice $m=1,N=L$ gives the standard cutoff.
In the DVR example $q_L:R\to R/\pi^L R$, this reads
\[
q_L(T)^{-1}
=
q_L\!\left(\sum_{W(\gamma)<L}
(-1)^{|\gamma|}A_\gamma D^{-1}\right).
\]
```

## thm:transfer_rationality — Rationality of the transfer series

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/03_weighted.tex`, line 385. SHA-256 `56aeaee491cd3d2d349e53e8ab7e8d10280e51892c5cb682e665a7088fd16988`.

Automatic integer walk-count rationality is present. General field-valued edge multiplicities and arbitrary u,v are not bundled as the displayed theorem.

Related frozen contract rows: 12.

```tex
\label{thm:transfer_rationality}
The weighted transfer series satisfies
\[
Z_{u,v}(t)
=
u^{\mathsf T}(I-A(t))^{-1}v.
\]
It is a rational function whose denominator divides
\[
\det(I-A(t)).
\]
```

## cor:path_recurrence — Recurrence for path counts

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/03_weighted.tex`, line 412. SHA-256 `56aeaee491cd3d2d349e53e8ab7e8d10280e51892c5cb682e665a7088fd16988`.

Integer walk-series recurrence and an integer rational-certificate recurrence are present. The general field/multiplicity formulation is not mapped in full.

Related frozen contract rows: 13.

```tex
\label{cor:path_recurrence}
Write
\[
Z_{u,v}(t)=\frac{P(t)}{Q(t)},
\qquad
Q(t)=1+q_1t+\cdots+q_dt^d.
\]
Then, for every $n>\deg P$,
\[
a_n+q_1a_{n-1}+\cdots+q_da_{n-d}=0.
\]
```

## cor:multigraded_series — Several independent weights

**Status:** no_statement_level_map_in_selected_tree
**Source:** `editable/traditional/chapters/03_weighted.tex`, line 435. SHA-256 `56aeaee491cd3d2d349e53e8ab7e8d10280e51892c5cb682e665a7088fd16988`.

The selected automatic construction is univariate. No statement-level multivariable transfer-series rationality theorem was located.

Related frozen contract rows: none with a complete endpoint.

```tex
\label{cor:multigraded_series}
Suppose every edge has a weight vector
\[
w(e)=(w_1(e),\ldots,w_r(e))\in\mathbb N^r\setminus\{0\}.
\]
Replace $t^{w(e)}$ by
\[
t_1^{w_1(e)}\cdots t_r^{w_r(e)}.
\]
The resulting multigraded transfer series is rational in $t_1,\ldots,t_r$.
```

## thm:transfer-zeta — Automatic finite-graph transfer-zeta rationality

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/03_weighted.tex`, line 486. SHA-256 `56aeaee491cd3d2d349e53e8ab7e8d10280e51892c5cb682e665a7088fd16988`.

Positive finite multigraph walk enumeration, first-edge recurrence and the canonical integer determinant/adjugate rationality are constructed.

Related frozen contract rows: 12, 25.

```tex
\label{thm:transfer-zeta}
Assume the vertex and edge sets are finite and every edge has positive integer
weight. For every $n$, exact enumeration of edge tuples of lengths at most
$n$, followed by endpoint and total-weight filtering, returns $a_n(s,t)$.
These coefficients obey the recurrence obtained by removing the first edge
\[
a_n(s,t)
=
\mathbf 1_{s=t,\,n=0}
+\sum_{\substack{e:\,\operatorname{source}(e)=s\\w(e)\le n}}
a_{n-w(e)}(\operatorname{target}(e),t).
\]
Let
\[
T(t)=I-A(t),\qquad
Q(t)=\det T(t),\qquad
P_{s,t}(t)=\operatorname{adj}(T(t))_{s,t}.
\]
Then $Q(0)=1$, hence $Q\ne0$ and $Q$ is a unit in $\Z[[t]]$, and the
independently enumerated walk series satisfies
\[
\boxed{
Z_{s,t}(t)=Q(t)^{-1}P_{s,t}(t),
\qquad
Q(t)Z_{s,t}(t)=P_{s,t}(t)
}
\quad\text{in }\Z[[t]].
\]
```

## cor:zeta-recurrence — Linear recurrence

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/03_weighted.tex`, line 547. SHA-256 `56aeaee491cd3d2d349e53e8ab7e8d10280e51892c5cb682e665a7088fd16988`.

The eventual recurrence for the canonical integer graph series is explicitly mapped.

Related frozen contract rows: 13.

```tex
\label{cor:zeta-recurrence}
With the canonical polynomials from \cref{thm:transfer-zeta}, write
\[
Q(t)=\sum_kq_kt^k,
\qquad
Z_{s,t}(t)=\sum_{n\ge0}a_n(s,t)t^n.
\]
Then the walk counts satisfy the recurrence with constant coefficients determined by
$Q$ after the finite initial range contributed by $P_{s,t}$:
\[
\boxed{
\sum_{k=0}^{n}q_k a_{n-k}(s,t)=0
\qquad\bigl(n>\deg P_{s,t}\bigr).
}
\]
```

## thm:bezout_projector — Bézout spectral projector

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 9. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

Evaluated commuting endomorphism identities construct the projector. Polynomial evaluation/Cayley-Hamilton, the characteristic-factor inputs and lattice instantiation are not assembled.

Related frozen contract rows: 14.

```tex
\label{thm:bezout_projector}
Assume that
\[
\chi_A(x)=f(x)g(x)
\]
with monic polynomials $f,g\in\OO[x]$ that are coprime in $K[x]$.  Choose $u,v\in\OO[x]$ and a nonzero $r\in\OO$ such that
\[
u(x)f(x)+v(x)g(x)=r.
\]
Then
\[
E_f=r^{-1}v(A)g(A)
\]
is the projector of $V$ onto $\Ker f(A)$ along $\Ker g(A)$.  In particular,
\[
E_f^2=E_f,
\qquad
rE_f\in\End_{\OO}(\Lambda).
\]
```

## thm:several_projectors — Several coprime spectral packets

**Status:** no_statement_level_map_in_selected_tree
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 54. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

No selected multi-factor characteristic-polynomial spectral family theorem constructs all projectors with their resultant lattice bounds.

Related frozen contract rows: none with a complete endpoint.

```tex
\label{thm:several_projectors}
Assume
\[
\chi_A(x)=\prod_{i=1}^rf_i(x),
\]
where the monic factors $f_i\in\OO[x]$ are pairwise coprime in $K[x]$.  Put
\[
g_i=\prod_{j\ne i}f_j.
\]
There are complementary projectors $E_i$ with
\[
\im E_i=\Ker f_i(A),
\qquad
\sum_iE_i=I,
\qquad
E_iE_j=0
\quad(i\ne j).
\]
One may choose $E_i$ so that
\[
\Res(f_i,g_i)E_i\in\End_{\OO}(\Lambda)
\]
up to multiplication of the resultant by a unit.
```

## cor:resultant_bound — Resultant denominator bound

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 83. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

Lattice clearing from a supplied evaluated Bezout scalar is present. Constructing that scalar as the general polynomial resultant remains outside the selected endpoint.

Related frozen contract rows: 14, 15.

```tex
\label{cor:resultant_bound}
Under the hypotheses of \cref{thm:bezout_projector}, one may take
\[
r=\Res(f,g)
\]
up to multiplication by a unit.  Therefore
\[
\pi^{\val_\pi(\Res(f,g))}E_f\Lambda\subseteq\Lambda.
\]
```

## thm:bezout-projector — Evaluated B\'ezout spectral projector

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 120. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

The evaluated endomorphism identities and lattice-preservation assumptions are exactly the explicitly narrowed formal contract.

Related frozen contract rows: 14.

```tex
\label{thm:bezout-projector}
Let $F,G,U,V\in\End_K(\Lambda\otimes_\OO K)$ and let $r\in K^\times$.
Suppose
\[
UF+VG=rI,
\qquad FG=0,
\qquad FG=GF,
\qquad GU=UG.
\]
Put $N=VG$. Then
\[
\boxed{N^2=rN.}
\]
Consequently the operator
\[
\boxed{
E=r^{-1}VG
}
\]
is idempotent, acts as the identity on $\ker F$, and acts as zero on
$\ker G$. If $V$ and $G$ preserve $\Lambda$, then
\[
rE=VG\in\End_\OO(\Lambda).
\]
```

## thm:precision-delay — Projector precision delay

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 207. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

The supplied clearing exponent gives the stated sufficient input/output precision implication.

Related frozen contract rows: 16.

```tex
\label{thm:precision-delay}
Let $E$ be a rational projector with $\pi^sE(\Lambda)\subseteq\Lambda$. If
\[
x\equiv y\pmod{\pi^{m+s}\Lambda},
\]
then
\[
Ex\equiv Ey\pmod{\pi^m\Lambda}.
\]
Thus $m+s$ input digits suffice to determine $m$ output digits of the projected packet.
```

## thm:gluing_weight — Gluing module and exact separation weight

**Status:** no_statement_level_map_in_selected_tree
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 265. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

No selected declaration constructs the gluing quotient injection or identifies its torsion exponent with the maximum projector separation weight.

Related frozen contract rows: none with a complete endpoint.

```tex
\label{thm:gluing_weight}
With the notation of \cref{def:lattice_packet}, the map
\[
\Phi:G_{\Lambda,\Pcal}
\longrightarrow
\bigoplus_{\alpha\in I}E_\alpha\Lambda/\Lambda_\alpha,
\qquad
[x]\longmapsto(E_\alpha x+\Lambda_\alpha)_\alpha
\]
is injective, and every coordinate projection of its image is surjective.  We also have
\[
\boxed{
\expn_\pi(G_{\Lambda,\Pcal})
=
s_\Lambda(\Pcal).
}
\]
If
\[
G_{\Lambda,\Pcal}
\cong
\bigoplus_{j=1}^r\OO/\pi^{a_j}\OO
\]
with $a_1\leq\cdots\leq a_r$, then
\[
s_\Lambda(\Pcal)=\max\bigl(\{0\}\cup\{a_j:1\leq j\leq r\}\bigr).
\]
```

## cor:length_and_weight — Total gluing and worst precision

**Status:** no_statement_level_map_in_selected_tree
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 320. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

The actual gluing module length/sum and exponent/maximum statement is not a selected formal endpoint.

Related frozen contract rows: none with a complete endpoint.

```tex
\label{cor:length_and_weight}
If
\[
G_{\Lambda,\Pcal}
\cong
\bigoplus_{j=1}^r\OO/\pi^{a_j}\OO,
\]
then
\[
\length_{\OO}(G_{\Lambda,\Pcal})
=
\sum_{j=1}^ra_j,
\qquad
s_\Lambda(\Pcal)=\max\bigl(\{0\}\cup\{a_j:1\leq j\leq r\}\bigr).
\]
Thus the lattice index measures the total amount of gluing, while the separation weight measures the worst precision loss in one direction.
```

## cor:binary_gluing — Two complementary packets

**Status:** no_statement_level_map_in_selected_tree
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 342. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

The two complementary-packet quotient isomorphisms are not constructed in the selected tree.

Related frozen contract rows: none with a complete endpoint.

```tex
\label{cor:binary_gluing}
Suppose
\[
V=V_1\oplus V_2
\]
with projector $E$ onto $V_1$ and complementary projector $I-E$.  Then
\[
\Lambda/(\Lambda_1\oplus\Lambda_2)
\cong
E\Lambda/\Lambda_1
\cong
(I-E)\Lambda/\Lambda_2.
\]
Consequently
\[
s_\Lambda(E)=s_\Lambda(I-E)
=
\expn_\pi\bigl(\Lambda/(\Lambda_1\oplus\Lambda_2)\bigr).
\]
```

## cor:integral_split — Integral splitting criterion

**Status:** no_statement_level_map_in_selected_tree
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 371. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

The integral split-lattice/gluing-quotient equivalence is not packaged as a selected statement.

Related frozen contract rows: none with a complete endpoint.

```tex
\label{cor:integral_split}
Every packet projector preserves $\Lambda$ if and only if
\[
\Lambda=\bigoplus_\alpha(\Lambda\cap V_\alpha).
\]
Equivalently,
\[
s_\Lambda(\Pcal)=0
\quad\Longleftrightarrow\quad
G_{\Lambda,\Pcal}=0.
\]
```

## thm:gluing_refinement — Gluing exact sequence under refinement

**Status:** no_statement_level_map_in_selected_tree
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 396. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

No actual gluing-module short exact sequence under refinement, with the separation-weight consequence, was located.

Related frozen contract rows: none with a complete endpoint.

```tex
\label{thm:gluing_refinement}
Let $\Qcal=(Q_\beta)$ refine $\Pcal=(P_\alpha)$ on $V$, and let $\Lambda$ be a lattice.  Define
\[
\Lambda_{\Pcal}
=
\bigoplus_\alpha(\Lambda\cap P_\alpha V),
\qquad
\Lambda_{\Qcal}
=
\bigoplus_\beta(\Lambda\cap Q_\beta V).
\]
Then
\[
\Lambda_{\Qcal}\subseteq\Lambda_{\Pcal}\subseteq\Lambda
\]
and there is a short exact sequence
\[
0
\longrightarrow
\Lambda_{\Pcal}/\Lambda_{\Qcal}
\longrightarrow
\Lambda/\Lambda_{\Qcal}
\longrightarrow
\Lambda/\Lambda_{\Pcal}
\longrightarrow0.
\]
In particular,
\[
\boxed{
s_\Lambda(\Pcal)\leq s_\Lambda(\Qcal).
}
\]
```

## thm:precision_delay — Necessary and sufficient precision delay

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 448. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

Sufficiency and least clearing-exponent properties are present. Necessity at every smaller depth, with explicit incongruent witnesses, is not assembled.

Related frozen contract rows: 15, 16.

```tex
\label{thm:precision_delay}
Let $E$ be a rational projector on $V$, let $\Lambda$ be a lattice, and let
\[
s=s_\Lambda(E).
\]
For every $m\geq0$, the rule
\[
[x]_{m+s}\longmapsto[Ex]_m
\]
from $\Lambda/\pi^{m+s}\Lambda$ to $V/\pi^m\Lambda$ is well defined.  Here $m$ is an integer.  If $d$ is an integer with $0\leq d<s$, then for every integer $m\geq0$ there are $x,y\in\Lambda$ such that
\[
x\equiv y\pmod{\pi^{m+d}\Lambda}
\]
but
\[
Ex\not\equiv Ey\pmod{\pi^m\Lambda}.
\]
Thus $s$ extra digits are both sufficient and necessary for a uniform precision guarantee.
```

## prop:sign_projectors — Sign projectors over a lattice

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 551. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

The rational p-local entrywise matrices and exact weights are established. Transport to actual Q_p and Z_p-lattice operators is not a selected declaration.

Related frozen contract rows: 17.

```tex
\label{prop:sign_projectors}
Let
\[
A=
\begin{pmatrix}
1&1\\
0&-1
\end{pmatrix}
\]
act on $\mathbb Z_p^2$.  Over $\mathbb Q_p$, the sign projectors are
\[
E_+=\frac{I+A}{2}
=
\begin{pmatrix}
1&1/2\\
0&0
\end{pmatrix},
\]
\[
E_-=\frac{I-A}{2}
=
\begin{pmatrix}
0&-1/2\\
0&1
\end{pmatrix}.
\]
For every odd prime $p$, both projectors preserve $\mathbb Z_p^2$.  At $p=2$,
\[
s_2(E_+)=s_2(E_-)=1.
\]
The factors $x-1$ and $x+1$ have resultant $2$.
```

## prop:character_integrality — Integral character averages away from the group order

**Status:** no_statement_level_map_in_selected_tree
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 590. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

No selected declaration proves the stated integral character-average preservation for an arbitrary DVR lattice and U-stable module.

Related frozen contract rows: none with a complete endpoint.

```tex
\label{prop:character_integrality}
Let $\OO$ be a discrete valuation ring, let $N$ be a unit in $\OO$, and suppose $\OO$ contains a primitive $N$th root of unity $\omega$.  If an integral operator $U$ satisfies $U^N=I$, then
\[
E_j=\frac1N\sum_{k=0}^{N-1}\omega^{-jk}U^k
\]
preserves every $U$ stable $\OO$ lattice.  At primes dividing $N$, this formula alone gives no integral projector.
```

## prop:dyadic-sign — Odd-adic versus dyadic behavior

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 642. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

The explicitly rational sign-matrix realization, weights and sign-polynomial resultant are the recorded scoped realization.

Related frozen contract rows: 17.

```tex
\label{prop:dyadic-sign}
For every prime $p\ne2$, every entry of $E_+$ and $E_-$ is $p$-integral,
and each projector has exact local denominator weight zero. At $p=2$, each
projector has exact local denominator weight one. Multiplication by $2$ makes
it integral, while the unscaled matrix is not integral:
\[
s_{2,\Z^2}(E_+)=s_{2,\Z^2}(E_-)=1.
\]
The characteristic factors $x-1$ and $x+1$ have resultant $2$. Its $2$-adic
valuation is one, exactly the two local projector weights above, and its
$p$-adic valuation is zero at every prime $p\ne2$.
```

## prop:weight_from_inclusion — Computing a packet weight from an inclusion matrix

**Status:** no_statement_level_map_in_selected_tree
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 720. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

The inclusion-matrix/Smith-exponent identification for the actual gluing lattice is not constructed.

Related frozen contract rows: none with a complete endpoint.

```tex
\label{prop:weight_from_inclusion}
Choose an $\OO$ basis of $\Lambda$ and an $\OO$ basis of $\Lambda_{\mathrm{split}}$.  Let $B$ be the matrix of the inclusion
\[
\Lambda_{\mathrm{split}}\hookrightarrow\Lambda.
\]
If the Smith form of $B$ is
\[
\diag(\pi^{a_1},\ldots,\pi^{a_n}),
\qquad
0\leq a_1\leq\cdots\leq a_n,
\]
then
\[
G_{\Lambda,\Pcal}
\cong
\bigoplus_{j=1}^n\OO/\pi^{a_j}\OO,
\qquad
s_\Lambda(\Pcal)=\max\bigl(\{0\}\cup\{a_j:1\leq j\leq n\}\bigr).
\]
```

## thm:smith_congruence — Smith weighted congruence solve

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 745. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

Concrete diagonal ZMod(p^L) fibres are constructed. Arbitrary DVR residue cardinality q, rectangular kernel terms and Smith transport U,V are additional inputs/assembly.

Related frozen contract rows: 18.

```tex
\label{thm:smith_congruence}
Let $M\in M_{m,n}(\OO)$ have Smith exponents $s_1,\ldots,s_r$.  Let the residue field have size $q$, fix $L\geq1$, and consider
\[
Mx\equiv b\pmod{\pi^L}.
\]
Put
\[
\widetilde b=Ub
\]
for a Smith matrix $U$ as in \cref{fact:smith}.  The congruence is solvable if and only if
\[
\widetilde b_i\equiv0
\pmod{\pi^{\min(s_i,L)}}
\qquad(1\leq i\leq r)
\]
and
\[
\widetilde b_i\equiv0
\pmod{\pi^L}
\qquad(r<i\leq m).
\]
When it is solvable, the number of solutions in $(\OO/\pi^L\OO)^n$ is
\[
\boxed{
q^{(n-r)L+\sum_{i=1}^r\min(s_i,L)}.
}
\]
```

## cor:smith_obstruction — Obstruction and branching data

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 787. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

The diagonal finite obstructions/count are present; the entire arbitrary-DVR rectangular transported system is not a mapped endpoint.

Related frozen contract rows: 18.

```tex
\label{cor:smith_obstruction}
The transformed entries of $\widetilde b$ that fail the stated divisibility conditions are the complete finite congruence obstructions.  When all obstructions vanish, the Smith exponents determine the number of solution branches at depth $L$.
```

## thm:smith-solve — Concrete Smith-weighted congruence solve

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/04_arithmetic.tex`, line 827. SHA-256 `5be0364212d6fad52e176f604adc583eedbd28ad0b9207d59a07c9be4527d497`.

The explicit square diagonal ZMod(p^L) solvability criterion and conditional exact fibre cardinality are constructed.

Related frozen contract rows: 18.

```tex
\label{thm:smith-solve}
Let $p>1$ and consider the diagonal system over
$(\Z/(p^L)\Z)^d$
\[
\diag(p^{s_1},\ldots,p^{s_d})x=b
\pmod{p^L}.
\]
The system is solvable if and only if
\[
p^{\min(s_i,L)}\mid (b_i)_{\mathrm{val}}
\]
for every $i$, where $(b_i)_{\mathrm{val}}$ is the canonical natural
representative. Conditional on this admissibility condition, the number of
solutions is
\[
\boxed{
p^{\sum_{i=1}^d\min(s_i,L)}.
}
\]
If any coordinate is inadmissible, the solution set is empty and its
cardinality is zero.
```

## thm:power_defect — Power defect identity

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/05_defects.tex`, line 25. SHA-256 `f24d9046e91cd05e04e3b4770859b7c8096c7824f87a33e88454d51ab01e392f`.

The typed finite telescoping identity is directly represented, including its zero-power extension.

Related frozen contract rows: 19.

```tex
\label{thm:power_defect}\label{thm:power-defect}
For every integer $n\geq1$,
\[
CT_f^n-T_c^nC
=
\sum_{k=0}^{n-1}T_c^{n-1-k}\Delta T_f^k.
\]
```

## cor:power_norm — Power norm bound

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/05_defects.tex`, line 44. SHA-256 `f24d9046e91cd05e04e3b4770859b7c8096c7824f87a33e88454d51ab01e392f`.

The continuous-linear-map norm estimate is an explicit mapped endpoint.

Related frozen contract rows: 20.

```tex
\label{cor:power_norm}
For bounded operators between Banach spaces,
\[
\|CT_f^n-T_c^nC\|
\leq
\|\Delta\|
\sum_{k=0}^{n-1}
\|T_c\|^{n-1-k}\|T_f\|^k.
\]
```

## cor:defect-norm — Norm bound

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/05_defects.tex`, line 59. SHA-256 `f24d9046e91cd05e04e3b4770859b7c8096c7824f87a33e88454d51ab01e392f`.

Both the sum norm bound and geometric majorant are mapped at the displayed operator scope.

Related frozen contract rows: 20.

```tex
\label{cor:defect-norm}
For a submultiplicative operator norm,
\[
\|CT_f^n-T_c^nC\|
\le
\|\Delta\|
\sum_{k=0}^{n-1}
\|T_c\|^{n-1-k}\|T_f\|^k.
\]
If $\|T_f\|,\|T_c\|\le\rho$, then
\[
\boxed{
\|CT_f^n-T_c^nC\|
\le n\rho^{n-1}\|\Delta\|.
}
\]
```

## cor:polynomial_defect — Polynomial defect

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/05_defects.tex`, line 77. SHA-256 `f24d9046e91cd05e04e3b4770859b7c8096c7824f87a33e88454d51ab01e392f`.

Power identities and zero-defect polynomial compatibility are supplied. The full nonzero-defect polynomial sum is not exposed as a selected endpoint.

Related frozen contract rows: 19.

```tex
\label{cor:polynomial_defect}
For
\[
p(z)=\sum_{n=0}^Na_nz^n,
\]
we have
\[
Cp(T_f)-p(T_c)C
=
\sum_{n=1}^Na_n
\sum_{k=0}^{n-1}T_c^{n-1-k}\Delta T_f^k.
\]
```

## thm:resolvent_defect — Resolvent defect identity

**Status:** whole_statement_source_match
**Source:** `editable/traditional/chapters/05_defects.tex`, line 95. SHA-256 `f24d9046e91cd05e04e3b4770859b7c8096c7824f87a33e88454d51ab01e392f`.

Typed scalar-shift inverse identities prove the displayed equation once the two inverse witnesses are supplied, as the manuscript assumes.

Related frozen contract rows: 21.

```tex
\label{thm:resolvent_defect}\label{thm:resolvent-defect}
If $z-T_f$ and $z-T_c$ are invertible, then
\[
C(z-T_f)^{-1}-(z-T_c)^{-1}C
=
(z-T_c)^{-1}\Delta(z-T_f)^{-1}.
\]
```

## thm:holomorphic_defect — Holomorphic functional calculus defect

**Status:** no_statement_level_map_in_selected_tree
**Source:** `editable/traditional/chapters/05_defects.tex`, line 146. SHA-256 `f24d9046e91cd05e04e3b4770859b7c8096c7824f87a33e88454d51ab01e392f`.

The selected tree has resolvent algebra and norm bounds, not the contour functional calculus, integral exchange and Cauchy-cycle estimate.

Related frozen contract rows: none with a complete endpoint.

```tex
\label{thm:holomorphic_defect}
Let $X_f$ and $X_c$ be complex Banach spaces, and let $C:X_f\to X_c$, $T_f$, and $T_c$ be bounded complex-linear maps.  Let $h$ be holomorphic on an open set $U$ containing both spectra.  Let $\Gamma$ be an admissible finite rectifiable Cauchy cycle in $U$ and in both resolvent sets, with winding number one on the union of the spectra and zero outside $U$.  The length of a cycle counts multiplicities.  Then
\[
Ch(T_f)-h(T_c)C
=
\frac{1}{2\pi i}
\int_\Gamma
h(z)(z-T_c)^{-1}\Delta(z-T_f)^{-1}\,dz.
\]
Consequently,
\begin{align*}
\|Ch(T_f)-h(T_c)C\|
&\leq
\frac{\operatorname{length}(\Gamma)}{2\pi}
\sup_{z\in\Gamma}|h(z)|\,\|\Delta\|\\
&\quad\times
\sup_{z\in\Gamma}\|(z-T_c)^{-1}\|
\sup_{z\in\Gamma}\|(z-T_f)^{-1}\|.
\end{align*}
```

## thm:exponential_defect — Exponential defect identity

**Status:** no_statement_level_map_in_selected_tree
**Source:** `editable/traditional/chapters/05_defects.tex`, line 178. SHA-256 `f24d9046e91cd05e04e3b4770859b7c8096c7824f87a33e88454d51ab01e392f`.

No selected Banach exponential/segment-integral Duhamel defect theorem was located.

Related frozen contract rows: none with a complete endpoint.

```tex
\label{thm:exponential_defect}
Let $C:X_f\to X_c$, $T_f$, and $T_c$ be bounded linear maps between Banach spaces over a common field.  For real $t$, use real or complex spaces. For complex $t$, use complex spaces and complex-linear maps.  Then
\[
Ce^{tT_f}-e^{tT_c}C
=
\int_0^t e^{(t-s)T_c}\Delta e^{sT_f}\,ds,
\]
where the integral is taken along the straight segment from $0$ to $t$ when $t$ is complex.  For real $t\geq0$,
\[
\|Ce^{tT_f}-e^{tT_c}C\|
\leq
\|\Delta\|
\int_0^t
\|e^{(t-s)T_c}\|
\|e^{sT_f}\|\,ds.
\]
```

## thm:multilevel_defect — Multilevel defect decomposition

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/05_defects.tex`, line 224. SHA-256 `f24d9046e91cd05e04e3b4770859b7c8096c7824f87a33e88454d51ab01e392f`.

Single-level algebraic and norm ingredients exist. The variable-length typed tower telescoping identity and norm assembly remain unmapped.

Related frozen contract rows: 19, 21.

```tex
\label{thm:multilevel_defect}
The total defect from level $L$ to level zero is
\[
C_{0,L}T_L-T_0C_{0,L}
=
\sum_{\ell=0}^{L-1}
C_{0,\ell}\Delta_\ell C_{\ell+1,L}.
\]
For bounded maps,
\[
\|C_{0,L}T_L-T_0C_{0,L}\|
\leq
\sum_{\ell=0}^{L-1}
\|C_{0,\ell}\|
\|\Delta_\ell\|
\|C_{\ell+1,L}\|.
\]
```

## cor:exact_compatibility — Exact compatibility

**Status:** partial_restricted_or_unassembled
**Source:** `editable/traditional/chapters/05_defects.tex`, line 281. SHA-256 `f24d9046e91cd05e04e3b4770859b7c8096c7824f87a33e88454d51ab01e392f`.

Single-level polynomial/resolvent compatibility is present. The multilevel and holomorphic/exponential branches are not all represented.

Related frozen contract rows: 19, 21.

```tex
\label{cor:exact_compatibility}
If every one step defect $\Delta_\ell$ vanishes, then
\[
C_{0,L}p(T_L)=p(T_0)C_{0,L}
\]
for every polynomial $p$.  The analogous resolvent, holomorphic, and exponential identities also hold whenever the relevant expressions are defined.
```

