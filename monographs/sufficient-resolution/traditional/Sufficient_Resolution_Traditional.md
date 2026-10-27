# Sufficient Resolution

## Exact Reduction, Hidden Memory, and Certified Reconstruction

**Komorebi P. — Final edition, October 6, 2026**

The complete source ZIP includes the .md files, editable manuscript sources, Lean sources, exact Python companions, example data, and verification records.

### Abstract

A representation is sufficient relative to an observation and a family of permitted continuations. This paper develops that principle through exact analysis and synthesis, hidden-return defects, behavioral quotients, finite certificates, quantitative approximation, and certified inverse problems. Split compression fails to preserve composition by an explicit hidden excursion; for finite-dimensional hidden state, finitely many feedback moments decide all-depth closure. Behavioral reduction retains precisely the distinctions that some permitted future observation can detect. In real Hilbert settings, compatibility, realizability, and source identifiability produce separate obstructions and conditioning requirements. Canonical reconstruction, Tikhonov regularization, discrepancy selection, inexact solves, changing operators, and redundant calibration frames are assembled into a common chain of contracts. Classical linear algebra and analysis provide the foundations. The contribution of the assembled calculus is the explicit relation between these contracts, their reusable certificates, and their sharp boundaries. The paper consolidates sixteen development blocks and maps its principal claims to existing Lean declarations. Finite rational implementations are companion evidence and are not asserted to be formally verified.

# The problem and its mathematical contracts

Sufficiency depends on what a representation must support. A compression that preserves today's observation can lose a distinction needed after a later operation. A coordinate enlargement can be redundant yet exact. A compatible local datum can still fail to have a global source. A small fitting residual can coexist with large source error. These are distinct phenomena with different mathematical witnesses.

The paper follows two connected lines. The first is the reduction of known linear dynamics relative to declared observations. The second is the reconstruction of a source from bounded linear data with explicit error allowances. The first yields an exact semantic state quotient. The second yields metric reconstruction and stability contracts. The present formalization does not yet identify every behaviorally minimal state with a stably recoverable target in an inverse problem. That bridge is an open extension, stated in the final section.

## Conventions and domains

Operator multiplication applies the right factor first: $STx=S(Tx)$. A word $w=[i_1,\ldots,i_n]$ is chronological, so $T_w=T_{i_n}\cdots T_{i_1}$; $T_\varnothing=I$. Concatenating $u$ then $v$ gives $T_{u\mathbin{+\!+}v}=T_vT_u$. Empty sums are zero and empty products are one. All equalities of operators are equalities on the entire stated domain.

The exact redundant-coordinate theory works for modules over a semiring. Subtraction and compression defects use modules over a commutative ring. Dimension and annihilating-polynomial arguments use a field. Norm estimates use bounded linear maps on normed spaces. Continuous flow results use bounded, time-independent real generators on Banach spaces. Reconstruction and regularization use real Hilbert spaces unless a weaker projection hypothesis is printed explicitly. These changes of domain are part of the contracts.

For a subspace $L$ admitting orthogonal projection, $P_L$ denotes that actual projection. On a Hilbert space, closed subspaces admit it. The notation $\mathop{\mathrm{dist}}(v,L)=\inf_{\ell\in L}\left\lVert v-\ell\right\rVert$ always refers to the actual subspace, not a replacement chosen to make a theorem true. Closure is written $\mathop{\mathrm{cl}}L$.

## How to read the formal evidence

The stable identifiers SR-01 through SR-64 label consolidated theorem groups. They are editorial units, with hypotheses and proofs printed here. A separate CSV/JSON concordance records their exact source declarations and source hashes. Several formal lemmas can support one printed theorem, and one source lemma can serve more than one explanatory purpose. The source inventory contains 998 theorem/lemma declarations in 93 production modules, including helper lemmas and examples. It is not a count of independent new mathematical results.

The arguments below reconstruct the mathematics of the supplied Lean sources. Classical inputs such as Cayley--Hamilton, orthogonal projection, the open mapping theorem, Lax--Milgram, and the intermediate value theorem enter through the source's Mathlib dependencies. This paper does not assert a new historical priority assessment for those inputs. The Lean guide records exactly which compilations and kernel replays are archived or freshly performed during this release. Python certificates are tested implementations of mathematical contracts; their parsers and algorithms are not Lean-verified.

# Exact coordinates, compression, and behavioral state

The first contract supplies two maps rather than identifying a coordinate space with the object by convention. Let $a_X:X\to V_X$ and $s_X:V_X\to X$ be linear with $s_Xa_X=I_X$. The ambient space $V_X$ may have redundant coordinates. Define $E_X=a_Xs_X$. For another such resolution of $Y$, put $$\mathcal K(T)=a_YTs_X,\qquad \mathcal D(K)=s_YKa_X.$$ We call a proposed coordinate operator compatible when $E_YKE_X=K$.

**Hypotheses.** Semiring modules; supplied linear analysis/synthesis pairs with s_X a_X=I and s_Y a_Y=I.

**Theorem 1** (SR-01: Exact redundant representation).

*$E_X^2=E_X$, and $E_Xv=v$ exactly when $v\in\mathop{\mathrm{Ran}}a_X$. Moreover $$\mathcal D\mathcal K(T)=T,\qquad
\mathcal K\mathcal D(K)=E_YKE_X.$$ Consequently a compatible $K$ is the encoding of a unique map $T:X\to Y$. Encoding preserves composition. Its identity on resolved coordinates is $E_X$.*

*Proof.* The splitting gives $E_X^2=a_X(s_Xa_X)s_X=a_Xs_X$. If $E_Xv=v$, then $v=a_X(s_Xv)$; conversely $E_Xa_Xx=a_Xx$. Substituting the definitions yields $$s_Y(a_YTs_X)a_X=T,\qquad
a_Y(s_YKa_X)s_X=E_YKE_X.$$ For compatible $K$, take $T=\mathcal D(K)$. If another $T'$ encodes to $K$, decoding proves $T'=\mathcal D(K)$. Finally, an intermediate resolution of $Y$ has $s_Ya_Y=I_Y$, so $\mathcal K(S)\mathcal K(T)=a_ZS(s_Ya_Y)Ts_X=a_ZSTs_X$. Encoding $I_X$ gives $a_Xs_X=E_X$, which acts as identity on compatible kernels. No inverse on all of $V_X$ has been assumed. ◻

**Formal source:** `Komorebi.SufficientResolution.Resolution.projector_idempotent`; `Komorebi.SufficientResolution.Resolution.fixed_iff_realizable`; `Komorebi.SufficientResolution.Resolution.compatible_iff_existsUnique`; `Komorebi.SufficientResolution.Resolution.encode_comp`; `Komorebi.SufficientResolution.Resolution.encode_id`.

**Example 2** (Redundant coordinates). For $X=\mathbb R$ and $V_X=\mathbb R^2$, take $a(x)=(x,x)$ and $s(u,v)=(u+v)/2$. Then $E(u,v)=((u+v)/2,(u+v)/2)$. The encoded scalar transformation $x\mapsto cx$ has matrix $\frac c2\bigl(\begin{smallmatrix}1&1\\1&1\end{smallmatrix}\bigr)$. Its redundant coordinate identity is $E$, while the ambient identity matrix also acts on an unrealizable anti-diagonal sector. The distinction is exact.

**Hypotheses.** Commutative-ring modules; linear $C:X\to Z$, $R:Z\to X$ with $CR=I_Z$; arbitrary endomorphisms $S,T,U$ of $X$.

**Theorem 3** (SR-02: Hidden-return defect and coherence).

*Set $P=RC$, $Q=I-P$, $\Phi(T)=CTR$, and $\Delta(S,T)=\Phi(ST)-\Phi(S)\Phi(T)$. Then $$\Delta(S,T)=CSQTR,$$ and associativity gives $$\Delta(S,T)\Phi(U)+\Delta(ST,U)
=\Phi(S)\Delta(T,U)+\Delta(S,TU).$$ For two successive split compressions, $$\Delta_{21}(S,T)=\Phi_2(\Delta_1(S,T))
+\Delta_2(\Phi_1(S),\Phi_1(T)).$$*

*Proof.* Insert $I=P+Q$ between $S$ and $T$: $CSTR=CS(P+Q)TR=(CSR)(CTR)+CSQTR$. This proves the factorization. Expanding either side of the coherence identity cancels the terms $\Phi(S)\Phi(T)\Phi(U)$ and leaves $\Phi(STU)-\Phi(S)\Phi(TU)$ together with the same compensating term. For the two-stage formula, add and subtract $\Phi_2(\Phi_1(S)\Phi_1(T))$ in the composite defect. Linearity of $\Phi_2$ identifies the first difference with $\Phi_2(\Delta_1(S,T))$; the second is the second-stage defect. Thus a later representation transports the earlier error and can introduce another one. It does not remove the first term by definition. ◻

**Formal source:** `Komorebi.SufficientResolution.SplitCompression.defect_factorization`; `Komorebi.SufficientResolution.SplitCompression.defect_coherence`; `Komorebi.SufficientResolution.SplitCompression.defect_then`.

**Hypotheses.** Commutative-ring modules and a linear presentation $G\xrightarrow{A}V\xrightarrow{\delta}W$ with $\delta A=0$; a compatible vector $v\in\ker\delta$.

**Theorem 4** (SR-03: Actual globalization obstruction).

*For $\delta A=0$, define $K=\ker\delta$, $R=\mathop{\mathrm{Ran}}A\subseteq K$, and $\mathcal H=K/R$. A compatible $v$ has class zero exactly when $v=Ag$ for some $g$. All classes vanish exactly when $R=K$. If $A$ is injective, a zero class has a unique source.*

*Commuting presentation maps $LA=A'F$ and $\delta'L=M\delta$ induce a map $\overline L:\mathcal H\to\mathcal H'$ by $[v]\mapsto[Lv]$. These maps compose and preserve zero classes. Reflection of zero follows when $\overline L$ is injective.*

*Proof.* The chain condition puts the actual range of $A$ inside $K$. The zero class criterion for a quotient is membership in the submodule divided out, giving $[v]=0\iff v\in R\iff\exists g,Ag=v$. Every compatible class is zero exactly when $K\subseteq R$; the reverse inclusion is already known. Injectivity of $A$ gives uniqueness of any preimage.

For transport, if $v\in K$, then $\delta'Lv=M\delta v=0$. If $v=Ag$, then $Lv=A'Fg$ lies in $R'$. Hence $L$ descends to the actual quotients. Evaluating on representatives proves the composition law. A linear map sends zero to zero. If its induced quotient map is injective, $\overline L[v]=0=\overline L[0]$ implies $[v]=0$. The commuting squares alone provide no such injectivity and do not assert that either obstruction quotient vanishes. ◻

**Formal source:** `Komorebi.SufficientResolution.Globalization.obstructionClass_zero_iff`; `Komorebi.SufficientResolution.Globalization.all_obstructions_zero_iff_exact`; `Komorebi.SufficientResolution.Globalization.unique_realization_of_zero`; `Komorebi.SufficientResolution.Globalization.PresentationMap.obstructionMap_compose`; `Komorebi.SufficientResolution.Globalization.PresentationMap.reflects_zero_obstruction`.

**Hypotheses.** Commutative-ring modules; a linear observation $O:X\to Y$ and an arbitrary family of allowed endomorphisms $T_i:X\to X$; every finite chronological word is included.

**Theorem 5** (SR-04: The all-future invisible quotient).

*Let $N=\bigcap_w\ker(OT_w)$. It is the largest submodule contained in $\ker O$ and invariant under every $T_i$. The operations and observation descend to $X/N$, preserving every future observation. In particular, $$[x]=[y]\iff OT_wx=OT_wy\quad\text{for every finite word }w.$$ If $q:X\to Z$ satisfies $qT_i=U_iq$ and $Vq=O$, then $\ker q\subseteq N$.*

*Proof.* An intersection of kernels is a submodule. If $x\in N$, then $OT_wT_ix=OT_{i::w}x=0$, so $T_ix\in N$. If an invariant submodule $L\subseteq\ker O$ contains $x$, induction on word length gives $T_wx\in L$; therefore $x\in N$. This establishes maximality.

Invariance defines quotient operations $[x]\mapsto[T_ix]$; containment in $\ker O$ defines $[x]\mapsto Ox$. Induction gives their all-word fidelity. Equality $[x]=[y]$ means $x-y\in N$, which is precisely equality of the displayed observations by linearity. In an exact competing model, induction gives $qT_w=U_wq$ and hence $OT_w=VU_wq$. If $qx=0$, every future observation of $x$ is zero. Thus a competing model can retain extra distinctions, but cannot erase any distinction visible to the specified future task. ◻

**Formal source:** `Komorebi.SufficientResolution.Behavioral.invisible_invariant`; `Komorebi.SufficientResolution.Behavioral.invariant_submodule_le_invisible`; `Komorebi.SufficientResolution.Behavioral.all_future_observations_preserved`; `Komorebi.SufficientResolution.Behavioral.quotient_eq_iff_same_future`; `Komorebi.SufficientResolution.Behavioral.exact_model_kernel_le`.

# Discrete hidden memory and finite closure

Let $V$ be visible state and $H$ hidden state. Over a commutative ring, specify four maps and form the actual full dynamics $$T(y,z)=(Ay+Bz,Gy+Dz).$$ Put $C(y,z)=y$, $Ry=(y,0)$, $E_n=CT^nR$, and $M_k=BD^kG$. The return $M_k$ contains entry into $H$, $k$ hidden transitions, and return to $V$. Its first effect occurs after $k+2$ full transitions.

**Hypotheses.** Commutative-ring modules; actual powers of T(y,z)=(Ay+Bz,Gy+Dz); arbitrary initial y_0,z_0.

**Theorem 6** (SR-05: Exact hidden elimination).

*For the trajectory $(y_n,z_n)=T^n(y_0,z_0)$, $$z_n=D^nz_0+\sum_{j=0}^{n-1}D^{n-1-j}Gy_j,$$ and $$y_{n+1}=Ay_n+BD^nz_0+\sum_{j=0}^{n-1}M_{n-1-j}y_j.$$ Prepared evolution ($z_0=0$) satisfies $E_0=I$, $E_1=A$, and $$E_{n+1}=AE_n+\sum_{j=0}^{n-1}M_{n-1-j}E_j.$$*

*Proof.* At $n=0$, the first formula is $z_0=z_0$ with an empty sum. If it holds at $n$, the actual recurrence $z_{n+1}=Gy_n+Dz_n$ gives the same formula at $n+1$ after distributing $D$ and appending the newest forcing term. Substituting this expression into $y_{n+1}=Ay_n+Bz_n$ proves the visible memory equation. For a prepared input $y_0$, each $y_j$ equals $E_jy_0$. The pointwise memory equation is therefore an operator identity because it holds for every $y_0$. The equations are derived from powers of $T$; the trajectory recurrence is not an extra certificate assumption. ◻

**Formal source:** `Komorebi.SufficientResolution.BlockDynamics.hidden_elimination`; `Komorebi.SufficientResolution.BlockDynamics.discrete_memory_equation`; `Komorebi.SufficientResolution.BlockDynamics.prepared_recurrence`.

**Hypotheses.** Same block dynamics; no finite-dimensional or orthogonality assumption.

**Theorem 7** (SR-06: Prepared closure and the first return).

*The following conditions are equivalent: $$E_n=A^n\ (\forall n),\qquad M_k=0\ (\forall k),\qquad
E_{m+n}=E_mE_n\ (\forall m,n).$$ More precisely, $$E_n=A^n\ (n\le N+1)\iff M_k=0\ (k<N).$$ If $M_j=0$ for $j<k$, then $E_{k+2}-A^{k+2}=M_k$. Closure for every initial hidden state is equivalent to $B=0$.*

*Proof.* If all memory maps vanish, the recurrence in SR-05 reduces to $E_{n+1}=AE_n$, proving $E_n=A^n$ by induction. Conversely, suppose exact powers hold. Induct on $k$. In the recurrence for $E_{k+2}$, every term except $M_kE_0$ involves a previously vanishing memory map. Thus $E_{k+2}=AE_{k+1}+M_k$, forcing $M_k=0$. The same induction restricted to $k<N$ proves the finite-prefix equivalence and, before setting the last term to zero, the first-return identity.

Exact powers imply the semigroup law. The law conversely gives $E_{n+1}=E_nE_1=E_nA$, so it implies exact powers. For arbitrary hidden initialization, evaluating closure at $n=1$, $y_0=0$ gives $Bz_0=0$ for every $z_0$, hence $B=0$. That condition also suffices directly from the visible recurrence. Vanishing $BD^kG$ imposes a weaker prepared-state requirement. ◻

**Formal source:** `Komorebi.SufficientResolution.BlockDynamics.prepared_powers_iff_memory_zero`; `Komorebi.SufficientResolution.BlockDynamics.prepared_semigroup_iff_memory_zero`; `Komorebi.SufficientResolution.BlockDynamics.first_return_discrepancy`; `Komorebi.SufficientResolution.BlockDynamics.prepared_prefix_iff_memory_prefix`; `Komorebi.SufficientResolution.BlockDynamics.all_state_closure_iff_B_zero`.

**Hypotheses.** Field modules; supplied monic annihilating polynomial p(D)=0, or finite-dimensional hidden H with d=dim H.

**Theorem 8** (SR-07: Finite all-depth closure certificate).

*If a monic polynomial $p$ annihilates $D$, vanishing of $M_k$ for $k<\deg p$ implies vanishing for all $k$. If $\dim H=d<\infty$, then $$E_n=A^n\ (\forall n)
\iff M_k=0\ (0\le k<d)
\iff E_n=A^n\ (0\le n\le d+1).$$ The visible space need not be finite-dimensional. The case $d=0$ is included.*

*Proof.* Divide $X^n$ by the monic $p$ to obtain a remainder $q_n$ of degree below $\deg p$. Evaluation at $D$ gives $D^n=q_n(D)$ because $p(D)=0$. Writing $q_n(D)$ as a finite linear combination of the powers $D^k$ below $\deg p$ shows $BD^nG=0$. For finite-dimensional $H$, Cayley--Hamilton provides the monic characteristic polynomial of $D$ with degree $d$. SR-06 then yields both displayed equivalences. In dimension zero, all maps through $H$ vanish and the empty list of memory tests is sufficient. If exact closure fails, the contrapositive gives a nonzero memory map with index below $d$. These tests concern complete linear maps, not sampled state vectors or approximate floating-point agreement. ◻

**Formal source:** `Komorebi.SufficientResolution.BlockDynamics.memory_zero_of_annihilator`; `Komorebi.SufficientResolution.BlockDynamics.prepared_powers_iff_finrank_memory`; `Komorebi.SufficientResolution.BlockDynamics.prepared_powers_iff_finite_horizon`; `Komorebi.SufficientResolution.BlockDynamics.nonclosure_has_finite_feedback_witness`.

**Hypotheses.** Commutative-ring split C,R with CR=I; hidden H=ker C; finite-H corollary over a field.

**Theorem 9** (SR-08: Canonical hidden state of a split compression).

*For $C:X\to Z$, $R:Z\to X$, $CR=I$, let $Q=I-RC$ and $H=\ker C$. The maps $$x\longmapsto(Cx,Qx),\qquad (y,z)\longmapsto Ry+z$$ are inverse linear maps between $X$ and $Z\times H$. An endomorphism $T$ is conjugate to block dynamics with $$A=CTR,\quad B=CT\iota_H,\quad G=QTR,\quad D=QT\iota_H.$$ Their prepared maps equal $CT^nR$. Hence exact compressed powers are equivalent to zero canonical memory. If $\dim\ker C=d$, complete compressed map tests through $d+1$ decide all depths.*

*Proof.* $CQ=C-CRC=0$, so $Qx$ belongs to $H$. Synthesis after analysis gives $RCx+Qx=x$. Conversely, for $z\in\ker C$, one has $C(Ry+z)=y$ and $Q(Ry+z)=z$, using $QR=0$ and $Qz=z$. Conjugating $T$ by these inverse maps gives the four displayed blocks; in the hidden blocks, $Q$ supplies the required codomain. Induction transports powers under conjugacy. The lift of $y$ is $(y,0)$ in these coordinates, so the prepared visible map is precisely $CT^nR$. Apply SR-06 and SR-07. The construction uses the actual discarded subspace and imposes no orthogonality on the chosen splitting. ◻

**Formal source:** `Komorebi.SufficientResolution.SplitCompression.block_synthesis_analysis`; `Komorebi.SufficientResolution.SplitCompression.block_analysis_synthesis`; `Komorebi.SufficientResolution.SplitCompression.block_powers_eq`; `Komorebi.SufficientResolution.SplitCompression.exact_powers_iff_canonical_memory_zero`; `Komorebi.SufficientResolution.SplitCompression.exact_powers_iff_canonical_finite_horizon`.

**Example 10** (Delayed return and disconnected return). On $\mathbb Q^3$, set $T(y,z_1,z_2)=(z_1,z_2,y)$ and retain $y$. Then $A=0$, $M_0=0$, $M_1=I$, and $E_1=E_2=0$ while $E_3=I$. Two shallow exact checks cannot certify all depths without the dimension budget. For another system, let $A=D=I$, $B(z_1,z_2)=z_1$, and $G(y)=(0,y)$. Both couplings are nonzero but every $BD^kG$ vanishes. Prepared closure is exact, while an arbitrary hidden initial first coordinate affects the next visible state.

# Finite behavioral models and minimality

Now work over a field and, for dimension statements, assume $\dim X<\infty$. The allowed operations need not commute. Define $$N_r=\bigcap_{|w|\le r}\ker(OT_w),\qquad k=\dim\ker O.$$ A finite horizon means bounded word length. It gives a finite enumeration of constraints only when the operation alphabet is finite.

**Hypotheses.** Finite-dimensional X over a field; arbitrary alphabet; all bounded-length words including empty word.

**Theorem 11** (SR-09: Exact horizon and plateau certificate).

*$N_0=\ker O$ and $$N_{r+1}=\ker O\cap\bigcap_i T_i^{-1}N_r\subseteq N_r.$$ One plateau $N_{r+1}=N_r$ implies $N_r=N$. In all cases $N_k=N$. Thus equality of future observations through word length $k$ is equivalent to equality for every finite word.*

*Proof.* The empty word enforces $Ox=0$. A nonempty word $i::w$ of length at most $r+1$ enforces $OT_wT_ix=0$, yielding the recursion. At a plateau, that recursion shows $N_r$ is invariant under every $T_i$ and lies in $\ker O$. By SR-04, $N_r\subseteq N$, while $N\subseteq N_r$ always holds.

Before reaching $N$, each successive inclusion must be strict, since an equality would already certify the final subspace. Every strict inclusion reduces dimension by at least one. Starting from dimension $k$ allows at most $k$ such reductions; if $N_k$ has dimension zero it is already $N$, and otherwise an earlier plateau has occurred. Applying the kernel identity to $x-y$ proves the all-future comparison. No word-order commutativity is used. ◻

**Formal source:** `Komorebi.SufficientResolution.FiniteHorizon.visibleKernel_succ`; `Komorebi.SufficientResolution.FiniteHorizon.visibleKernel_eq_invisible_of_plateau`; `Komorebi.SufficientResolution.FiniteHorizon.visibleKernel_stabilizes`; `Komorebi.SufficientResolution.FiniteHorizon.same_future_iff_bounded`.

**Hypotheses.** Finite-dimensional X over a field; exact linear competitor q with qT_i=U_iq and Vq=O; finite Z only for final ambient comparison.

**Theorem 12** (SR-10: Minimum exact state dimension).

*The model $X/N$ is observable. Every exact competitor induces a unique surjection $\mathop{\mathrm{Ran}}q\to X/N$, taking $qx$ to $[x]$. Therefore $$\dim(X/N)\le\dim\mathop{\mathrm{Ran}}q,$$ with equality exactly when $\ker q=N$. In that case $\mathop{\mathrm{Ran}}q\cong X/N$. If $Z$ is finite-dimensional, also $\dim\mathop{\mathrm{Ran}}q\le\dim Z$. Surjectivity of $q$ onto $Z$ is not required.*

*Proof.* If $qx=qy$, SR-04 gives $x-y\in N$, so $qx\mapsto[x]$ is well-defined. It is linear and surjective because every class has a representative $x$. Its values on the actual range force uniqueness. Rank-nullity gives $\dim\mathop{\mathrm{Ran}}q=\dim X-\dim\ker q$ and $\dim(X/N)=\dim X-\dim N$. Since $\ker q\subseteq N$, this proves the inequality. Equality of dimensions forces equality of the nested finite-dimensional subspaces; conversely their equality makes the comparison injective and hence an equivalence. In the quotient model, an invisible class $[x]$ has every $OT_wx=0$, so $x\in N$ and $[x]=0$. This establishes observability. Unused coordinates in $Z$ do not change the reachable-image comparison. ◻

**Formal source:** `Komorebi.SufficientResolution.BehavioralMinimality.quotient_is_observable`; `Komorebi.SufficientResolution.BehavioralMinimality.imageComparison`; `Komorebi.SufficientResolution.BehavioralMinimality.finrank_state_le_image`; `Komorebi.SufficientResolution.BehavioralMinimality.image_dimension_minimal_iff`; `Komorebi.SufficientResolution.BehavioralMinimality.minimalImageEquiv`.

**Hypotheses.** Finite-dimensional X over a field; finite operation alphabet; k=dim ker O; target Y can be infinite-dimensional.

**Theorem 13** (SR-11: Realizable finite observation tables).

*Let $H_kx=(OT_wx)_{|w|\le k}$ and $Z_k=\mathop{\mathrm{Ran}}H_k$. Then $\ker H_k=N$ and $X/N\cong Z_k$. The formulas $$U_i(H_kx)=H_kT_ix,\qquad V(H_kx)=Ox$$ define actual linear maps on $Z_k$ and preserve every finite future word. This model has minimum exact dimension.*

*Proof.* The recursively enumerated words are exactly those of length at most $k$. SR-09 identifies the kernel of their combined observation map with $N$. The first isomorphism theorem gives $X/N\cong\mathop{\mathrm{Ran}}H_k$. If $H_kx=H_ky$, then $x-y\in N$; its invariance gives $H_kT_ix=H_kT_iy$, and $N\subseteq\ker O$ gives $Ox=Oy$. Hence the displayed operations and readout are well-defined on realizable tables. Induction proves $U_wH_kx=H_kT_wx$ and $VU_wH_kx=OT_wx$ for words of any length. Apply SR-10 to get minimality. An arbitrary table in the ambient coordinate product need not be realizable and is not part of this constructed state space. ◻

**Formal source:** `Komorebi.SufficientResolution.FiniteObservableModel.mem_wordsUpTo`; `Komorebi.SufficientResolution.FiniteObservableModel.ker_complete_observation`; `Komorebi.SufficientResolution.FiniteObservableModel.observableEquiv`; `Komorebi.SufficientResolution.FiniteObservableModel.coordinate_all_future_fidelity`; `Komorebi.SufficientResolution.FiniteObservableModel.coordinate_dimension_le_exact_model`.

**Hypotheses.** Field modules, not necessarily finite-dimensional; finite operation alphabet and finite horizon observation map H_r; actual maps q=F H_r, qT_i=U_iq, Vq=O.

**Theorem 14** (SR-12: Finite minimality certificate).

*For a finite operation alphabet, suppose a proposed representation satisfies $$q=F H_r,\qquad qT_i=U_iq,\qquad Vq=O.$$ Then $\ker q=N$, regardless of whether $r$ reaches the a priori horizon. If $q$ is surjective, it gives an equivalence $Z\cong X/N$ preserving the observation and intertwining every operation. Without surjectivity, the equivalence applies to $\mathop{\mathrm{Ran}}q$.*

*Proof.* If $x\in N$, then every coordinate of $H_rx$ is zero, so $qx=FH_rx=0$. This gives $N\subseteq\ker q$. Exact intertwining and output give the reverse inclusion by SR-04. The equality makes $qx\mapsto[x]$ injective on the range and surjective onto the quotient. Its inverse is the corresponding quotient map induced by $q$. Evaluating both sides on $qx$ proves that the equivalence intertwines $U_i$ with the quotient operations and preserves the readout. The certificate has two roles: generation by observations prevents retention of invisible distinctions, while exact dynamics and output prevent loss of future-visible distinctions. Finite dimension is needed to guarantee that such a certificate can be found at a bounded depth, not for its soundness. ◻

**Formal source:** `Komorebi.SufficientResolution.FiniteCertificate.certificate_kernel_eq`; `Komorebi.SufficientResolution.FiniteCertificate.certificate_same_future_iff`; `Komorebi.SufficientResolution.FiniteCertificate.certificateEquiv`; `Komorebi.SufficientResolution.FiniteCertificate.certificateEquiv_dynamics`; `Komorebi.SufficientResolution.FiniteCertificate.certificateEquiv_observation`.

**Example 15** (A noncommuting minimal model). On $\mathbb Q^3$, let $O(x,y,h)=x$, $T_A(x,y,h)=(y,0,h)$, and $T_B(x,y,h)=(0,x,h)$. The two operations do not commute: on $(1,0,0)$ their two compositions give $(1,0,0)$ and $(0,0,0)$. The map $q(x,y,h)=(x,y)$ is generated by $O$ and $OT_A$, intertwines both operations, and factors $O$. It therefore has a depth-one certificate. The hidden coordinate $h$ is invisible to every future word, and the minimum exact state dimension is two. The current observation alone has dimension one and misses the distinction between $(0,1,0)$ and zero, which one application of $T_A$ reveals.

# Quantitative discrete sufficiency

Let $q:X\to Z$ be a proposed representation, with true operations $T_i$, reduced operations $U_i$, and readouts $O:X\to Y$, $V:Z\to Y$. Define the step and word defects $$\delta_i=qT_i-U_iq,\qquad E_w=qT_w-U_wq.$$ Algebraic identities require only the stated commutative-ring structure. Quantitative estimates below use continuous linear maps over a nontrivially normed field and their whole-map operator norms.

**Hypotheses.** Commutative-ring modules; arbitrary chronological words and linear operations/representation/readouts.

**Theorem 16** (SR-13: Exact word-defect transport).

*One has $E_\varnothing=0$, $$E_{i::w}=E_wT_i+U_w\delta_i,\qquad
E_{u\mathbin{+\!+}v}=E_vT_u+U_vE_u.$$ For $w=[i_1,\ldots,i_n]$ this yields $$E_w=\sum_{j=1}^n
U_{[i_{j+1},\ldots,i_n]}\delta_{i_j}T_{[i_1,\ldots,i_{j-1}]}.$$ The output defect is $(O-Vq)T_w+VE_w$.*

*Proof.* The recursive identity follows by adding and subtracting $U_wqT_i$ in $qT_wT_i-U_wU_iq$. For concatenation, add and subtract $U_vqT_u$; chronological order gives $T_{u\mathbin{+\!+}v}=T_vT_u$ and the analogous identity for $U$. Inducting on the word expands one term per letter: each step defect is transported by its true prefix and reduced suffix. The empty word contributes no terms. Finally $OT_w-VU_wq=(O-Vq)T_w+V(qT_w-U_wq)$. Neither output mismatch nor accumulated dynamics mismatch is discarded. ◻

**Formal source:** `Komorebi.SufficientResolution.ApproximateAlgebra.wordDefect_cons`; `Komorebi.SufficientResolution.ApproximateAlgebra.wordDefect_append`; `Komorebi.SufficientResolution.ApproximateAlgebra.wordDefect_eq_sum`; `Komorebi.SufficientResolution.ApproximateAlgebra.output_defect_decomposition`.

**Hypotheses.** Normed spaces over nontrivially normed field; bounded maps; nonnegative letter bounds a_i,b_i,epsilon_i and eta$\ge\Vert$O-Vq$\Vert$.

**Theorem 17** (SR-14: Heterogeneous operator budgets).

*Suppose $\left\lVert T_i\right\rVert\le a_i$, $\left\lVert U_i\right\rVert\le b_i$, $\left\lVert \delta_i\right\rVert\le\epsilon_i$. Let $A_w,B_w$ be the products of the respective letter bounds and define $$D_\varnothing=0,\qquad D_{i::w}=D_wa_i+B_w\epsilon_i.$$ Then $\left\lVert T_w\right\rVert\le A_w$, $\left\lVert U_w\right\rVert\le B_w$, $\left\lVert E_w\right\rVert\le D_w$, and $$D_{u\mathbin{+\!+}v}=D_vA_u+B_vD_u.$$ If $\left\lVert O-Vq\right\rVert\le\eta$, then $$\left\lVert OT_w-VU_wq\right\rVert\le\eta A_w+\left\lVert V\right\rVert D_w.$$ For arbitrary initial $x\in X$, $z\in Z$, $\left\lVert qT_wx-U_wz\right\rVert\le D_w\left\lVert x\right\rVert+B_w\left\lVert qx-z\right\rVert$.*

*Proof.* Induction and submultiplicativity bound the two word operators by the products. Apply the triangle inequality and submultiplicativity to the first identity in SR-13 to obtain exactly the recursion for $D_w$. Induction on $u$ proves the displayed scalar concatenation identity; it tracks the same algebra as the exact defect identity, with nonnegative factors preventing an inequality reversal. The output bound follows from its exact decomposition in SR-13. For initialization, write $qT_wx-U_wz=E_wx+U_w(qx-z)$ and bound both terms. These are operator budgets; agreement on a finite set of sample vectors does not supply them. ◻

**Formal source:** `Komorebi.SufficientResolution.ApproximateBounds.norm_wordError_le_budget`; `Komorebi.SufficientResolution.ApproximateBounds.budget_append`; `Komorebi.SufficientResolution.ApproximateBounds.norm_outputError_le`; `Komorebi.SufficientResolution.ApproximateBounds.norm_state_error_le`.

**Hypotheses.** Uniform nonnegative whole-map bounds a,b,epsilon; all finite words with length n; eta bound on output mismatch.

**Theorem 18** (SR-15: Two-rate response and equal-rate limit).

*For $H_0(a,b)=0$ and $H_{n+1}(a,b)=aH_n(a,b)+b^n$, $$H_n(a,b)=\sum_{j=0}^{n-1}a^jb^{n-1-j},\qquad
(a-b)H_n=a^n-b^n.$$ If $a\ne b$, $H_n=(a^n-b^n)/(a-b)$; for equal rates, $H_{n+1}(a,a)=(n+1)a^n$. Uniform step bounds give $$\left\lVert E_w\right\rVert\le\epsilon H_n(a,b),\qquad
\left\lVert OT_w-VU_wq\right\rVert\le\eta a^n+\left\lVert V\right\rVert\epsilon H_n(a,b).$$*

*Proof.* Induction proves the finite-sum formula: multiplying the old sum by $a$ and adjoining $b^n$ generates every term of the new sum. Multiplication by $a-b$ telescopes, leaving $a^n-b^n$. Division is used only when the rates are distinct. If they coincide, all $n+1$ terms of $H_{n+1}$ equal $a^n$, including the zero-rate boundary with the usual $a^0=1$. For uniform bounds, the heterogeneous budget becomes $D_{i::w}=aD_w+b^{|w|}\epsilon$, so induction gives $D_w=\epsilon H_{|w|}(a,b)$. Apply SR-14. The empty word has zero dynamics defect and is handled by $H_0=0$, with no negative exponent required. ◻

**Formal source:** `Komorebi.SufficientResolution.ScalarBudgets.response_eq_sum`; `Komorebi.SufficientResolution.ScalarBudgets.response_mul_sub`; `Komorebi.SufficientResolution.ScalarBudgets.response_of_ne`; `Komorebi.SufficientResolution.ScalarBudgets.response_same_succ`; `Komorebi.SufficientResolution.StableApproximation.norm_wordError_uniform`; `Komorebi.SufficientResolution.StableApproximation.norm_outputError_uniform`.

**Hypotheses.** Bounded maps on the normed spaces of SR-14; $\left\lVert T_i\right\rVert\le1$ for every true operation; $\left\lVert U_i\right\rVert\le1$ in the nonexpansive case or a common $0\le b<1$ with $\left\lVert U_i\right\rVert\le b$ in the contractive case; $\left\lVert qT_i-U_iq\right\rVert\le\epsilon$ and $\left\lVert O-Vq\right\rVert\le\eta$ with $\epsilon,\eta\ge0$.

**Theorem 19** (SR-16: Nonexpansive and contractive continuations).

*If both families are nonexpansive, $\left\lVert E_w\right\rVert\le n\epsilon$ and the output defect is at most $\eta+\left\lVert V\right\rVert n\epsilon$. If the reduced family has a common bound $0\le b<1$, then $$\left\lVert E_w\right\rVert\le\frac\epsilon{1-b},\qquad
\left\lVert OT_w-VU_wq\right\rVert\le\eta+\left\lVert V\right\rVert\frac\epsilon{1-b}.$$ For arbitrary reduced initialization, $$\left\lVert OT_wx-VU_wz\right\rVert
\le\left(\eta+\left\lVert V\right\rVert\frac\epsilon{1-b}\right)\left\lVert x\right\rVert
+\left\lVert V\right\rVert b^n\left\lVert qx-z\right\rVert.$$*

*Proof.* For $a=b=1$, the response sum has $n$ unit terms. For $a=1$ and $b<1$, it is $1+b+\cdots+b^{n-1}\le1/(1-b)$. SR-15 gives the operator estimates. For initialization, add $VU_w(qx-z)$ to the operator output error applied to $x$, and use $\left\lVert U_w\right\rVert\le b^n$. The common bound concerns every allowed operation in the chosen norm. Individual spectral radii do not imply a common product bound for a noncommuting family. The nonexpansive estimate is an upper bound and does not state that every such system accumulates error linearly. ◻

**Formal source:** `Komorebi.SufficientResolution.StableApproximation.norm_wordError_nonexpansive`; `Komorebi.SufficientResolution.StableApproximation.norm_outputError_nonexpansive`; `Komorebi.SufficientResolution.StableApproximation.norm_wordError_contractive`; `Komorebi.SufficientResolution.StableApproximation.norm_output_initial_contractive`.

# Continuous flow and exact hidden memory

Let $L$ be a bounded real operator on a Banach space. Its flow is the actual operator exponential $e^{tL}$. Boundedness allows differentiation of the norm-convergent exponential series and integration of continuous operator curves. Equalities in this section hold for all real $t$, using oriented interval integrals when $t<0$.

**Hypotheses.** Real Banach space; bounded autonomous D; continuous forcing f; differentiable actual z with z${}^{\prime}$=Dz+f at every real time.

**Theorem 20** (SR-17: Actual flow and variation of constants).

*$\frac d{dt}e^{tD}=De^{tD}=e^{tD}D$, $e^{(s+t)D}=e^{sD}e^{tD}$, and $e^{-tD}$ is the inverse flow. Every actual curve satisfying $z'=Dz+f$ with continuous $f$ obeys $$z(t)=e^{tD}z(0)+\int_0^t e^{(t-s)D}f(s)\,ds.$$ The initial value uniquely determines the homogeneous solution; two forced solutions with the same forcing and initial value also agree.*

*Proof.* Termwise differentiation of the exponential series gives both derivative orders, since all powers of $D$ commute with $D$. The exponential addition identity for commuting multiples of one bounded operator gives the flow law and inverse. For fixed $t$, differentiate $e^{(t-s)D}z(s)$. The product rule produces $-De^{(t-s)D}z(s)+e^{(t-s)D}(Dz(s)+f(s))$; commutation cancels the generator terms. The remaining derivative is the continuous integrand $e^{(t-s)D}f(s)$. The fundamental theorem of calculus on the oriented interval gives the displayed identity. Setting $f=0$ yields the homogeneous formula. Subtracting two forced solutions reduces uniqueness to that case. The theorem starts from the differential equation, not from an assumed integral representation. ◻

**Formal source:** `Komorebi.SufficientResolution.ContinuousFlow.hasDerivAt_flow`; `Komorebi.SufficientResolution.ContinuousFlow.flow_add`; `Komorebi.SufficientResolution.ContinuousFlow.variation_of_constants`; `Komorebi.SufficientResolution.ContinuousFlow.homogeneous_unique`; `Komorebi.SufficientResolution.ContinuousFlow.forced_unique`.

**Hypotheses.** Bounded real generator algebras and bounded linear observation maps; norm-convergent exponentials; all real times or all natural powers.

**Theorem 21** (SR-18: Power identities and exponential identities).

*For bounded linear observation maps $K,J$ on bounded generator algebras, $$K(e^{tL})=J(e^{tD})\ (\forall t)
\iff K(L^n)=J(D^n)\ (\forall n).$$ In particular, $Be^{tD}G=0$ for every $t$ exactly when $BD^nG=0$ for every $n$. For $CR=I$, $A=CLR$, one has $$Ce^{tL}R=e^{tA}\ (\forall t)
\iff CL^nR=A^n\ (\forall n),$$ and, with $Q=I-RC$, $$Ce^{(s+t)L}R-(Ce^{sL}R)(Ce^{tL}R)=Ce^{sL}Qe^{tL}R.$$*

*Proof.* The $n$th derivative at zero of $e^{tL}$ is $L^n$. Bounded linear maps commute with these derivatives, so equality for all times implies equality of every observed power. Conversely bounded linear maps commute with the sum of the norm-convergent exponential series: $K(e^{tL})=\sum_n(t^n/n!)K(L^n)$. Equality term by term gives equality of the sums. Sandwiching and compression are bounded linear maps on the corresponding operator spaces, so they give the specializations. For the last identity, use the flow law and insert $I=RC+Q$ between the two flows. The defect factorization itself does not need $CR=I$; that condition makes $Q$ the discarded-state projector and ensures $E(0)=I$. ◻

**Formal source:** `Komorebi.SufficientResolution.ContinuousFlow.mapped_flow_eq_iff_powers_eq`; `Komorebi.SufficientResolution.ContinuousFlow.sandwich_flow_zero_iff`; `Komorebi.SufficientResolution.ContinuousFlow.compressed_flow_iff_powers`; `Komorebi.SufficientResolution.ContinuousFlow.compressed_flow_defect`.

**Hypotheses.** Real Banach visible/hidden spaces; bounded autonomous blocks A,B,G,D; actual exponential full trajectory; arbitrary hidden initial state.

**Theorem 22** (SR-19: Continuous hidden elimination).

*For $L(y,z)=(Ay+Bz,Gy+Dz)$ and $(y(t),z(t))=e^{tL}(y_0,z_0)$, $$z(t)=e^{tD}z_0+\int_0^t e^{(t-s)D}Gy(s)\,ds.$$ Writing $M(t)=Be^{tD}G$, the visible dynamics satisfy $$y'(t)=Ay(t)+Be^{tD}z_0+\int_0^t M(t-s)y(s)\,ds.$$ Prepared initialization removes the term involving $z_0$.*

*Proof.* Projecting the derivative of $e^{tL}$ onto the visible and hidden components gives $y'=Ay+Bz$ and $z'=Gy+Dz$. The visible curve is continuous, so $Gy$ is continuous forcing for the hidden equation. SR-17 yields the hidden elimination formula. Bounded $B$ commutes with the interval integral, giving the memory kernel in the visible equation. Taking $z_0=0$ removes only the initialization term. No converse construction of a full trajectory from an arbitrary Volterra solution is asserted here, and no unbounded generator domain is present. ◻

**Formal source:** `Komorebi.SufficientResolution.ContinuousBlockDynamics.hasDerivAt_visible`; `Komorebi.SufficientResolution.ContinuousBlockDynamics.hidden_elimination`; `Komorebi.SufficientResolution.ContinuousBlockDynamics.continuous_memory_equation`; `Komorebi.SufficientResolution.ContinuousBlockDynamics.prepared_memory_equation`.

**Hypotheses.** Bounded real Banach block system; finite-dimensional hidden H only for finite certificates, or supplied monic annihilator.

**Theorem 23** (SR-20: Continuous closure, finite moments, and jets).

*Let $E(t)=Ce^{tL}R$. The following are equivalent: $$E(t)=e^{tA}\ (\forall t),\quad M(t)=0\ (\forall t),\quad
BD^kG=0\ (\forall k),\quad E(s+t)=E(s)E(t)\ (\forall s,t).$$ If $\dim H=d$, each is equivalent to $BD^kG=0$ for $k<d$, or to $E^{(n)}(0)=A^n$ for $n\le d+1$. If the first $k$ return moments vanish, $$E^{(k+2)}(0)-A^{k+2}=BD^kG.$$*

*Proof.* SR-18 converts prepared flow equality into prepared power equality and memory flow vanishing into memory moment vanishing. SR-06 equates the corresponding algebraic conditions, and SR-07 supplies the finite moment criterion. Exact prepared flow gives its semigroup law. Conversely, if $E$ is a semigroup, differentiating $E(s+t)=E(s)E(t)$ in $s$ at zero gives $E'(t)=AE(t)$ because $E'(0)=CLR=A$ and $E(0)=I$. The bounded-generator uniqueness theorem yields $E(t)=e^{tA}$.

Actual iterated derivatives of the exponential satisfy $E^{(n)}(0)=CL^nR$. Applying the finite algebraic horizon and first-return identity proves the jet statements. The leading Taylor coefficient has the additional denominator $(k+2)!$; the derivative itself does not. The visible Banach space can be infinite-dimensional. The finite tests are whole-operator jet identities, not a finite list of sampled times. ◻

**Formal source:** `Komorebi.SufficientResolution.ContinuousBlockDynamics.prepared_exact_iff_memory_zero`; `Komorebi.SufficientResolution.ContinuousBlockDynamics.prepared_semigroup_iff_memory_zero`; `Komorebi.SufficientResolution.ContinuousBlockDynamics.prepared_exact_iff_finite_memory`; `Komorebi.SufficientResolution.ContinuousBlockDynamics.prepared_exact_iff_finite_derivatives`; `Komorebi.SufficientResolution.ContinuousBlockDynamics.first_return_derivative`.

**Example 24** (A linear continuous memory kernel). Take $V=\mathbb R$, $H=\mathbb R^2$, $A=0$, $B(z_1,z_2)=z_1$, $G(y)=(0,y)$, and $D(z_1,z_2)=(z_2,0)$. Since $D^2=0$, $e^{tD}(z_1,z_2)=(z_1+tz_2,z_2)$ and $M(t)=tI$. The first two prepared jets agree with the reduced generator, while the third derivative differs by $I$. Changing $D$ to zero leaves both boundary couplings nonzero but makes the memory kernel identically zero. Arbitrary hidden initialization still affects the visible initial derivative.

# Continuous approximate sufficiency

For bounded real generators $L$ on $X$ and $A$ on $Z$, and bounded $q:X\to Z$, write $\delta=qL-Aq$ and $E(t)=qe^{tL}-e^{tA}q$. Algebraic evolution identities hold for all real times. Norm bounds in this section restrict to $t\ge0$, with growth assumptions on the nonnegative-time flows.

**Hypotheses.** Real Banach source/reduced spaces; bounded autonomous generators; bounded q and second representation p; all real times.

**Theorem 25** (SR-21: Duhamel transport and composition).

*One has the operator identity $$E(t)=\int_0^t e^{(t-s)A}\delta e^{sL}\,ds,$$ and $\delta=0$ exactly when $E(t)=0$ for every $t$. Also $$E(s+t)=E(s)e^{tL}+e^{sA}E(t).$$ For a second representation $p:Z\to W$ with generator $B$, $$\delta_{pq}=p\delta_q+\delta_pq,\qquad
E_{pq}(t)=pE_q(t)+E_p(t)q.$$*

*Proof.* Differentiate $F(s)=e^{(t-s)A}qe^{sL}$ using the product rule. Its derivative is $e^{(t-s)A}(qL-Aq)e^{sL}$. Integrating from zero to $t$ gives $F(t)-F(0)=E(t)$ and proves the formula. Zero generator defect therefore forces zero evolution defect; differentiating $E$ at zero gives the converse. The addition identity follows by adding and subtracting $e^{sA}qe^{tL}$ and using the two flow laws. For a composite representation, add and subtract $pAq$ in its generator defect and $pe^{tA}q$ in its evolution defect. Both stages' contributions remain explicit. Boundedness guarantees the continuous operator integrand. ◻

**Formal source:** `Komorebi.SufficientResolution.ContinuousDefect.duhamel`; `Komorebi.SufficientResolution.ContinuousDefect.generatorDefect_zero_iff`; `Komorebi.SufficientResolution.ContinuousDefect.evolutionDefect_add`; `Komorebi.SufficientResolution.ContinuousDefect.generatorDefect_composite`; `Komorebi.SufficientResolution.ContinuousDefect.evolutionDefect_composite`.

**Hypotheses.** Real Banach spaces $X,Z$; bounded autonomous real generators $L,A$ and bounded representation/readouts $q,O,V$; real rates $a,b$ of either sign; $t\ge0$ and $M_L,M_A,\epsilon,\eta\ge0$. For every $s\ge0$, $\left\lVert e^{sL}\right\rVert\le M_Le^{as}$ and $\left\lVert e^{sA}\right\rVert\le M_Ae^{bs}$; also $\left\lVert qL-Aq\right\rVert\le\epsilon$ and $\left\lVert O-Vq\right\rVert\le\eta$.

**Theorem 26** (SR-22: Growth envelopes and scalar response).

*For $\left\lVert \delta\right\rVert\le\epsilon$, put $$R(a,b,t)=\int_0^t e^{b(t-s)}e^{as}\,ds
=\begin{cases}(e^{at}-e^{bt})/(a-b),&a\ne b,\\ te^{at},&a=b.\end{cases}$$ Then $$\left\lVert E(t)\right\rVert\le M_LM_A\epsilon R(a,b,t).$$ If $\left\lVert O-Vq\right\rVert\le\eta$, the output defect $F(t)=Oe^{tL}-Ve^{tA}q$ obeys $$\left\lVert F(t)\right\rVert\le\eta M_Le^{at}+\left\lVert V\right\rVert M_LM_A\epsilon R(a,b,t).$$*

*Proof.* Apply the integral norm inequality and submultiplicativity to SR-21. For $0\le s\le t$, the integrand norm is at most $M_Ae^{b(t-s)}\epsilon M_Le^{as}$. Integration gives the first estimate. Factoring $e^{bt}$ and integrating $e^{(a-b)s}$ gives the distinct-rate formula; for equal rates the integrand is constant $e^{at}$. The output decomposition is $F(t)=(O-Vq)e^{tL}+VE(t)$, giving the stated bound. The same argument works with continuous nonnegative envelope functions $u,v$ on the interval, replacing the scalar response by $\int_0^tv(t-s)u(s)\,ds$. In particular these assumptions concern actual flow norms, not just eigenvalues of the generators. ◻

**Formal source:** `Komorebi.SufficientResolution.ExponentialBudgets.response_of_ne`; `Komorebi.SufficientResolution.ExponentialBudgets.response_self`; `Komorebi.SufficientResolution.ContinuousApproximation.norm_evolution_le_response`; `Komorebi.SufficientResolution.ContinuousApproximation.norm_output_le_response`.

**Hypotheses.** True flow bounded by M_L; reduced flow bounded by M_A exp(-rt), r\>0, for t$\ge$`<!-- -->`{=html}0; generator/readout allowances; arbitrary initial reduced z.

**Theorem 27** (SR-23: Uniform continuous stability and initialization).

*If $\left\lVert e^{tL}\right\rVert\le M_L$ and $\left\lVert e^{tA}\right\rVert\le M_Ae^{-rt}$ with $r>0$, then $$\left\lVert E(t)\right\rVert\le\frac{M_LM_A\epsilon}{r},\qquad
\left\lVert F(t)\right\rVert\le\eta M_L+\left\lVert V\right\rVert\frac{M_LM_A\epsilon}{r}.$$ For arbitrary $x,z$, $$\begin{aligned}
\left\lVert Oe^{tL}x-Ve^{tA}z\right\rVert
&\le\left(\eta M_L+\left\lVert V\right\rVert\frac{M_LM_A\epsilon}{r}\right)\left\lVert x\right\rVert\\
&\quad+\left\lVert V\right\rVert M_Ae^{-rt}\left\lVert qx-z\right\rVert.
\end{aligned}$$ Composition through a second representation propagates allowances with its explicit map norm, as in SR-21.*

*Proof.* Use SR-22 with $a=0$, $b=-r$. Its response equals $(1-e^{-rt})/r\le1/r$ for $t\ge0$. This gives the evolution and output operator bounds. The initialization error decomposes into $F(t)x$ plus $Ve^{tA}(qx-z)$, which proves the displayed estimate. The first allowance must be multiplied by $\left\lVert x\right\rVert$ because it is an operator estimate. For another representation $p$ with its own evolution defect, SR-21 gives $\left\lVert E_{pq}(t)\right\rVert\le\left\lVert p\right\rVert\left\lVert E_q(t)\right\rVert+\left\lVert E_p(t)\right\rVert\left\lVert q\right\rVert$. This retains error introduced at both stages, rather than identifying their budgets with a single unqualified small quantity. ◻

**Formal source:** `Komorebi.SufficientResolution.ContinuousStability.norm_evolution_uniform`; `Komorebi.SufficientResolution.ContinuousStability.norm_output_uniform`; `Komorebi.SufficientResolution.ContinuousStability.norm_initialization_uniform`; `Komorebi.SufficientResolution.ContinuousStability.norm_composite_evolution`.

**Hypotheses.** Actual real scalar bounded generators, q=I; t$\ge$`<!-- -->`{=html}0; b$\le$a for equality and epsilon\>0 for counterexample.

**Theorem 28** (SR-24: Sharp response and small-defect failure).

*For scalar generators $a\ge b$, $$|e^{at}-e^{bt}|=(a-b)R(a,b,t),$$ so the response estimate is attained. For every $\epsilon>0$, choosing $L=\epsilon I$, $A=0$, $q=I$ gives $$\left\lVert \delta\right\rVert=\epsilon,\qquad \left\lVert E(t)\right\rVert=e^{\epsilon t}-1\ge\epsilon t.$$ Its evolution defect exceeds every fixed bound at some nonnegative time.*

*Proof.* The scalar exponential is the actual flow by the homogeneous ODE uniqueness theorem. For $a>b$, the response formula immediately gives the equality; for $a=b$, both sides vanish. In the second example, the generator defect is multiplication by $\epsilon$, while the evolution defect is multiplication by $e^{\epsilon t}-1$. The elementary exponential inequality $e^u\ge1+u$ for $u\ge0$ gives the lower bound. Taking $t$ sufficiently large makes it exceed any prescribed real bound. Thus a small generator defect alone does not supply uniform accuracy. The hypothesis of a bounded true flow in SR-23 fails here. ◻

**Formal source:** `Komorebi.SufficientResolution.ContinuousApproxExamples.scalar_response_sharp`; `Komorebi.SufficientResolution.ContinuousApproxExamples.unstable_generator_exact`; `Komorebi.SufficientResolution.ContinuousApproxExamples.unstable_error_exact`; `Komorebi.SufficientResolution.ContinuousApproxExamples.unstable_error_unbounded`.

# Orthogonal globalization and conditioning

Let $R\subseteq K$ be subspaces of a real inner-product space $V$, both admitting orthogonal projections. Define the actual maps $$r(v)=P_Rv,\quad o(v)=(P_K-P_R)v,\quad i(v)=(I-P_K)v.$$ They distinguish realized data, compatible obstruction, and incompatibility. In a globalization presentation use $R=\mathop{\mathrm{Ran}}A$, $K=\ker\delta$ with $\delta A=0$.

**Hypotheses.** Real inner-product V; nested subspaces R$\le$K both with orthogonal projections; arbitrary v and represented candidate u$\in$R.

**Theorem 29** (SR-25: Unique three-component geometry).

*The components lie in $R$, $K\cap R^\perp$, and $K^\perp$, respectively, are pairwise orthogonal, and give the unique decomposition $v=r(v)+o(v)+i(v)$. Furthermore, $$\left\lVert v\right\rVert^2=\left\lVert r\right\rVert^2+\left\lVert o\right\rVert^2+\left\lVert i\right\rVert^2,\qquad
\mathop{\mathrm{dist}}(v,R)^2=\left\lVert o\right\rVert^2+\left\lVert i\right\rVert^2.$$ For any $u\in R$, $$\left\lVert v-u\right\rVert^2=\mathop{\mathrm{dist}}(v,R)^2+\left\lVert r(v)-u\right\rVert^2.$$ Thus $r(v)$ is the unique nearest represented vector.*

*Proof.* Nested projections satisfy $P_RP_K=P_R$. Hence $P_Kv-P_Rv$ lies in $K$ and is orthogonal to $R$; the last component is orthogonal to $K$. Their definitions sum to $v$ and yield pairwise orthogonality. In any competing decomposition, projection onto $R$ selects its first term and projection onto $K$ selects the first two, so all components are forced. Pythagoras gives the norm identities. For $u\in R$, the residual $v-r(v)$ is orthogonal to $r(v)-u$, so the candidate identity follows. It proves optimality and uniqueness, and taking the infimum over actual $u\in R$ proves the distance formula. Each component map is an orthogonal projection onto its displayed sector and consequently is nonexpansive. ◻

**Formal source:** `Komorebi.SufficientResolution.OrthogonalResolution.components_sum`; `Komorebi.SufficientResolution.OrthogonalResolution.unique_components`; `Komorebi.SufficientResolution.OrthogonalResolution.norm_sq_components`; `Komorebi.SufficientResolution.OrthogonalResolution.candidate_error_sq`; `Komorebi.SufficientResolution.OrthogonalResolution.infDist_sq_decomposition`.

**Hypotheses.** Real linear presentation $\delta$A=0; projections on actual R=range A and K=ker$\delta$; source G only needs real module structure.

**Theorem 30** (SR-26: Harmonic realization of the obstruction quotient).

*The same quotient $\mathcal H=K/R$ from SR-03 is linearly equivalent to $K\cap R^\perp$ by $$[v]\longmapsto v-P_Rv\quad(v\in K).$$ It is inverse to the quotient map restricted to the harmonic subspace. For compatible data, the class is zero exactly when $o(v)=0$; equality of classes is equality of harmonic representatives. The best image $P_Rv$ has an actual source under $A$.*

*Proof.* Adding a vector of $R$ leaves $v-P_Rv$ unchanged, so the map descends to $K/R$. Its values lie in $K\cap R^\perp$ by SR-25. For harmonic $h$, $P_Rh=0$, so its class maps back to $h$. For compatible $v$, the difference $v-(v-P_Rv)=P_Rv$ lies in $R$, so the reverse roundtrip returns $[v]$. The inverse laws prove the equivalence and both class criteria. Since $P_Rv$ belongs to the actual range, some $g$ satisfies $Ag=P_Rv$. This is image existence; uniqueness of $g$ requires the separate injectivity condition in SR-03. No norm isometry is inferred from linear equivalence alone; the metric statement is proved in SR-33. ◻

**Formal source:** `Komorebi.SufficientResolution.HilbertGlobalization.obstructionEquivHarmonic`; `Komorebi.SufficientResolution.HilbertGlobalization.class_zero_iff_component_zero`; `Komorebi.SufficientResolution.HilbertGlobalization.same_class_iff_same_harmonic`; `Komorebi.SufficientResolution.HilbertGlobalization.exists_best_global_image`.

**Hypotheses.** Same projection presentation; bounded $\delta$; sigma\>0 with sigma$\Vert$x$\Vert\le\Vert\delta$x$\Vert$ on K$\perp$; arbitrary data.

**Theorem 31** (SR-27: Residual bounds retain conditioning and obstruction).

*If $\sigma\left\lVert x\right\rVert\le\left\lVert \delta x\right\rVert$ for $x\in K^\perp$ and $\sigma>0$, then $$\delta i(v)=\delta v,\qquad
\left\lVert i(v)\right\rVert\le\frac{\left\lVert \delta v\right\rVert}\sigma,$$ and $$\left\lVert o(v)\right\rVert\le\mathop{\mathrm{dist}}(v,R),\qquad
\mathop{\mathrm{dist}}(v,R)^2\le\left\lVert o(v)\right\rVert^2+\left(\frac{\left\lVert \delta v\right\rVert}\sigma\right)^2.$$ For compatible data, $\mathop{\mathrm{dist}}(v,R)=\left\lVert o(v)\right\rVert$.*

*Proof.* The component $P_Kv$ is in $\ker\delta$, so $\delta(v-P_Kv)=\delta v$. Apply coercivity to $i(v)\in K^\perp$ and divide by the positive $\sigma$. SR-25 gives the exact sum of two nonnegative squares, proving both the lower bound and conditioned upper bound. If $\delta v=0$, then $v\in K$ and $i(v)=0$, giving equality. In particular, a compatibility residual bounds only inconsistency. A residual-only global bound needs a vanished obstruction or exactness $R=K$. The condition on $\sigma$ is independent of the size of a particular measured residual and cannot be inferred from that measurement. ◻

**Formal source:** `Komorebi.SufficientResolution.HilbertConditioning.inconsistency_residual`; `Komorebi.SufficientResolution.HilbertConditioning.inconsistency_le_residual`; `Komorebi.SufficientResolution.HilbertConditioning.conditioned_distance_sq`; `Komorebi.SufficientResolution.HilbertConditioning.obstruction_lower_bound`; `Komorebi.SufficientResolution.HilbertConditioning.compatible_distance`.

**Hypotheses.** Finite-dimensional real V for existence/characterization; fixed metric and K with projected R0$\le$R1$\le$K for refinement.

**Theorem 32** (SR-28: Finite conditioning and realizable enlargement).

*In finite dimension some $\sigma>0$ satisfies SR-27. Under $\delta A=0$, $$\exists c>0\ \forall v:\mathop{\mathrm{dist}}(v,\mathop{\mathrm{Ran}}A)\le c\left\lVert \delta v\right\rVert
\iff\mathop{\mathrm{Ran}}A=\ker\delta.$$ For projected $R_0\subseteq R_1\subseteq K$ in a fixed metric, put $g(v)=(P_{R_1}-P_{R_0})v$. Then $$\left\lVert o_0(v)\right\rVert^2=\left\lVert o_1(v)\right\rVert^2+\left\lVert g(v)\right\rVert^2,
\quad
\mathop{\mathrm{dist}}(v,R_0)^2=\mathop{\mathrm{dist}}(v,R_1)^2+\left\lVert g(v)\right\rVert^2.$$ No uniform conditioning constant exists across all nonzero scalar compatibility maps.*

*Proof.* Restrict $\delta$ to $K^\perp$. It is injective: a zero image lies in both $K$ and $K^\perp$. A finite-dimensional injective linear map has a positive lower norm bound, giving $\sigma$; the zero domain is harmless and permits any positive choice. If the residual-only inequality holds, every $v\in K$ has zero distance to $\mathop{\mathrm{Ran}}A$. Finite-dimensional ranges are closed, so $v\in\mathop{\mathrm{Ran}}A$. Conversely exactness removes $o(v)$ in SR-27.

Nested orthogonal projections split $o_0(v)=o_1(v)+g(v)$ into orthogonal sectors, and the inconsistency component stays fixed. Pythagoras gives both refinement identities. For the scalar family $\delta_s(x)=sx$, $s>0$, take $R=0$ and $v=1$. The reconstruction distance is one and the residual is $s$. For any proposed common $c$, choosing $s$ sufficiently small violates $1\le cs$. The theorem guarantees a constant per presentation, not a common constant across degenerating presentations. ◻

**Formal source:** `Komorebi.SufficientResolution.HilbertConditioning.exists_coercivity_finite`; `Komorebi.SufficientResolution.FiniteGlobalization.finite_residual_bound_iff_exact`; `Komorebi.SufficientResolution.GlobalizationRefinement.obstruction_refinement_sq`; `Komorebi.SufficientResolution.GlobalizationRefinement.distance_refinement_sq`; `Komorebi.SufficientResolution.GlobalizationExamples.no_uniform_conditioning_over_scalar_family`.

**Example 33** (A complete error split). For $A(g)=(g,0,0)$, $\delta(x,y,z)=2z$, and $v=(3,4,5)$, the components are $(3,0,0)$, $(0,4,0)$, and $(0,0,5)$. The squared reconstruction distance is $41=16+25$. The compatibility residual has squared norm $100$, and $\sigma=2$ is sharp on $K^\perp$. Thus the conditioned upper bound is attained: $16+100/4=41$.

# Canonical minimum-norm reconstruction

Let $A:G\to V$ be bounded between real Hilbert spaces, with actual closed range $R=\mathop{\mathrm{Ran}}A$. Write $N_A=\ker A$ and $S=N_A^\perp$. Closedness is a substantive hypothesis for a bounded exact inverse. It will be removed for regularized recovery in the following sections.

**Hypotheses.** Bounded real Hilbert operator A with actual closed range; core needs complete source/range and orthogonal projections.

**Theorem 34** (SR-29: Constructed bounded canonical inverse).

*Restriction $A_S:S\to R$ is a bounded linear bijection with bounded inverse. Define $$B=\iota_S A_S^{-1}P_R.$$ Then $AB=P_R$, $BA=P_S$, $ABA=A$, and $BAB=B$. Its two projections are symmetric, $\ker B=R^\perp$, and $\mathop{\mathrm{Ran}}B=S$. The best-image identity $AB=P_R$ and the condition $\mathop{\mathrm{Ran}}B\subseteq S$ uniquely determine $B$.*

*Proof.* The restriction is injective because $S\cap\ker A=0$. Every $Ag\in R$ equals $AP_Sg$, so it is surjective. Closed $R$ and closed $S$ are Banach spaces; the bounded inverse theorem supplies $A_S^{-1}$ as an actual continuous linear inverse. The definition then gives $AB=P_R$. For $g$, $BAg$ is the unique element of $S$ with image $Ag$, namely $P_Sg$. The two inverse identities imply the generalized inverse laws. Orthogonal projections are symmetric, proving the symmetry conditions. The definition and injectivity of $A_S^{-1}$ identify the kernel and range. Finally, if $B'$ has the same best image and values in $S$, then $B'v-Bv\in S\cap\ker A$ for each $v$, hence it is zero. This construction is the classical Moore--Penrose inverse with the actual range and source ambiguity retained. ◻

**Formal source:** `Komorebi.SufficientResolution.MinimumNormReconstruction.restrictionEquiv`; `Komorebi.SufficientResolution.MinimumNormReconstruction.image_comp_recover`; `Komorebi.SufficientResolution.MinimumNormReconstruction.recover_comp_image`; `Komorebi.SufficientResolution.MinimumNormReconstruction.recover_unique`; `Komorebi.SufficientResolution.ClosedRangeReconstruction.closedRecover`.

**Hypotheses.** Same real Hilbert closed-range constructor; arbitrary data v, candidate g and arbitrary deterministic noise e.

**Theorem 35** (SR-30: All least-squares sources and unique minimum norm).

*For every source $g$, $$\left\lVert v-Ag\right\rVert^2=\mathop{\mathrm{dist}}(v,R)^2+\left\lVert A(g-Bv)\right\rVert^2.$$ All least-squares minimizers are $Bv+k$ with $k\in\ker A$. Among them $Bv$ is the unique minimum-norm source. Exact source recovery $BAg=g$ holds exactly for $g\in S$. For data $Ag+e$, $$\left\lVert B(Ag+e)-g\right\rVert^2=\left\lVert Be\right\rVert^2+\left\lVert P_{N_A}g\right\rVert^2.$$*

*Proof.* $ABv=P_Rv$, so SR-25's candidate identity with $u=Ag$ proves the first formula. Equality to the minimum image error is equivalent to $A(g-Bv)=0$, yielding exactly the affine family of minimizers. Since $Bv\in S$ and $k\in N_A$, Pythagoras gives $\left\lVert Bv+k\right\rVert^2=\left\lVert Bv\right\rVert^2+\left\lVert k\right\rVert^2$. It proves minimum norm and uniqueness. The identity $BA=P_S$ proves the exact recovery criterion. For noisy data, linearity gives $B(Ag+e)-g=Be-P_{N_A}g$. The first term belongs to $S$ and the second to $N_A$, so they are orthogonal. This last identity does not assume a statistical noise model. It shows explicitly which source content the operator cannot identify. ◻

**Formal source:** `Komorebi.SufficientResolution.MinimumNormOptimality.candidate_error_decomposition`; `Komorebi.SufficientResolution.MinimumNormOptimality.all_least_squares_sources`; `Komorebi.SufficientResolution.MinimumNormOptimality.unique_minimum_norm_least_squares`; `Komorebi.SufficientResolution.MinimumNormOptimality.exact_source_recovery_iff`; `Komorebi.SufficientResolution.MinimumNormOptimality.noisy_source_error_sq`.

**Hypotheses.** Closed-range A; alpha\>0 with alpha$\Vert$g$\Vert\le\Vert$Ag$\Vert$ on S; computed source h may contain a kernel component.

**Theorem 36** (SR-31: Source conditioning and solver ambiguity).

*Some $\alpha>0$ satisfies $\alpha\left\lVert g\right\rVert\le\left\lVert Ag\right\rVert$ on $S$, and any supplied such constant gives $\left\lVert B\right\rVert\le1/\alpha$. Therefore $$\left\lVert B(Ag+e)-g\right\rVert^2\le(\left\lVert e\right\rVert/\alpha)^2+\left\lVert P_{N_A}g\right\rVert^2.$$ For an arbitrary computed source $h$, $$\left\lVert h-Bv\right\rVert^2
\le\left(\frac{\left\lVert Ah-P_Rv\right\rVert}\alpha\right)^2+\left\lVert P_{N_A}h\right\rVert^2.$$ If also $\delta A=0$, a compatibility constant $\sigma$ bounds the local error as in SR-27. The constants $\alpha$ and $\sigma$ have separate roles.*

*Proof.* The bounded inverse on $S$ gives $\left\lVert g\right\rVert\le\left\lVert B\right\rVert\left\lVert Ag\right\rVert$. Taking, for example, $\alpha=1/(\left\lVert B\right\rVert+1)>0$ handles also the zero complement and proves existence. For a supplied constant, apply it to $Bv\in S$: $\alpha\left\lVert Bv\right\rVert\le\left\lVert ABv\right\rVert=\left\lVert P_Rv\right\rVert\le\left\lVert v\right\rVert$. Take the operator norm and combine with SR-30 for the noisy bound. For a computed $h$, split $h-Bv=(P_Sh-Bv)+P_{N_A}h$ orthogonally. Coercivity bounds the first term by $\left\lVert Ah-P_Rv\right\rVert/\alpha$ because $AP_Sh=Ah$. The compatibility operator bounds distance of local data to realizability; the forward operator bounds source amplification. Neither condition establishes the other. A small fit without control of the computed kernel component does not certify the minimum-norm source. ◻

**Formal source:** `Komorebi.SufficientResolution.SourceConditioning.exists_source_coercivity`; `Komorebi.SufficientResolution.SourceConditioning.recover_opNorm_bound`; `Komorebi.SufficientResolution.SourceConditioning.noisy_source_bound_sq`; `Komorebi.SufficientResolution.SourceConditioning.candidate_source_bound_sq`; `Komorebi.SufficientResolution.ReconstructionGlobalization.two_condition_reconstruction`.

**Hypotheses.** Bounded A between real Hilbert spaces; actual range closedness; bounded recovery BA=P_S or off-kernel coercivity.

**Theorem 37** (SR-32: Closed range is equivalent to bounded recovery).

*The following conditions are equivalent: $$\mathop{\mathrm{Ran}}A\text{ is closed};\qquad
\exists\alpha>0:\alpha\left\lVert g\right\rVert\le\left\lVert Ag\right\rVert\ (g\in S);
\qquad \exists B\text{ bounded}:BA=P_S.$$ Thus a nonclosed range admits no bounded exact identifiable-source recovery. Finite-dimensional source or target supplies closed range. There is no common inverse-sensitivity constant across all nonzero real scalar forward maps.*

*Proof.* Closed range gives the bounded constructor and coercivity by SR-29--SR-31. Conversely suppose coercivity holds. If $Ag_n$ converges in $V$, replace $g_n$ by $P_Sg_n$ without changing its image. Coercivity makes this source sequence Cauchy. Completeness gives a limit $g\in S$, and continuity gives the image limit $Ag\in\mathop{\mathrm{Ran}}A$. Hence the range is closed. If bounded $B$ satisfies $BA=P_S$, then for $g\in S$, $\left\lVert g\right\rVert=\left\lVert BAg\right\rVert\le\left\lVert B\right\rVert\left\lVert Ag\right\rVert$. The same positive choice $1/(\left\lVert B\right\rVert+1)$ gives coercivity. Finite-dimensional image subspaces are closed in a normed space. Finally $A_cg=cg$, $c>0$, has canonical inverse $B_cv=v/c$. At $v=c$, data tend to zero with $c$ while the recovered source remains one, ruling out a common constant as $c\downarrow0$. ◻

**Formal source:** `Komorebi.SufficientResolution.ClosedRangeReconstruction.closed_range_iff_coercivity`; `Komorebi.SufficientResolution.ClosedRangeReconstruction.bounded_recovery_iff_closed_range`; `Komorebi.SufficientResolution.ClosedRangeReconstruction.nonclosed_no_bounded_recovery`; `Komorebi.SufficientResolution.ReconstructionExamples.no_uniform_source_conditioning`.

**Example 38** (Source and image are different optima). Let $A(g_1,g_2)=(g_1+g_2,0,0)$ and $v=(3,4,5)$. The best image is $(3,0,0)$, with the same squared local error $41$. The minimum-norm source is $(3/2,3/2)$ of squared norm $9/2$. The source $(3,0)$ gives the same best image but has squared norm $9$. Their difference $(3/2,-3/2)$ is kernel ambiguity, not local obstruction.

# Intrinsic metric obstruction and transport

Retain the globalization presentation $\delta A=0$, the actual projected subspaces $R=\mathop{\mathrm{Ran}}A\subseteq K=\ker\delta$, and the same algebraic quotient $\mathcal H=K/R$. Its seminorm is the quotient seminorm induced by the ambient metric. We prove the harmonic equivalence respects that preexisting seminorm, rather than defining a new norm to match its answer.

**Hypotheses.** Real inner-product V; R=range A,K=ker$\delta$ both projected; $\delta$ bounded, $\delta$A=0; native quotient seminorm.

**Theorem 39** (SR-33: Native quotient norm and isometry).

*The equivalence $K/R\cong K\cap R^\perp$ in SR-26 is a linear isometry. For compatible $v,w$, $$\left\lVert [v]\right\rVert=\left\lVert o(v)\right\rVert=\mathop{\mathrm{dist}}(v,R),\qquad
\mathop{\mathrm{dist}}([v],[w])=\mathop{\mathrm{dist}}(v-w,R).$$ The quotient norm detects zero classes. Its standard quotient inner product is preserved when the induced projection structure in $K$ is used.*

*Proof.* Let $h$ be the harmonic representative of a class $z$. For any compatible representative $v$ of $z$, its harmonic component is $h$, and the nonexpansive harmonic projection gives $\left\lVert h\right\rVert\le\left\lVert v\right\rVert$. Taking the infimum over representatives proves $\left\lVert h\right\rVert\le\left\lVert z\right\rVert$. Conversely $h$ itself represents $z$, so the quotient map's norm bound gives $\left\lVert z\right\rVert\le\left\lVert h\right\rVert$. This proves isometry against the existing quotient seminorm. The compatible distance formula follows from SR-25, and distances of classes follow by applying it to $v-w$. Zero norm implies zero harmonic vector and hence zero class by the inverse laws. Orthogonal projection onto $R$ restricts to $K$, constructing the quotient inner-product structure there. A real linear isometry preserves its inner product by the polarization identity. ◻

**Formal source:** `Komorebi.SufficientResolution.MetricObstruction.quotientToHarmonic_norm`; `Komorebi.SufficientResolution.MetricObstruction.obstructionIsometry`; `Komorebi.SufficientResolution.MetricObstruction.norm_class_eq_infDist`; `Komorebi.SufficientResolution.MetricObstruction.distance_classes`; `Komorebi.SufficientResolution.MetricObstruction.quotient_inner_preserved`.

**Hypotheses.** Same projected real presentation; arbitrary v for projected class c(v)=\[P_Kv\]; complete/closed source range only when canonical inverse B used.

**Theorem 40** (SR-34: Minimum representatives and intrinsic class of data).

*Every class $z$ has a unique compatible minimum-norm representative $s(z)$, and every compatible representative $v$ satisfies $$\left\lVert v\right\rVert^2=\left\lVert z\right\rVert^2+\left\lVert v-s(z)\right\rVert^2.$$ For arbitrary data define $c(v)=[P_Kv]$. This is nonexpansive and $$\mathop{\mathrm{dist}}(v,R)^2=\left\lVert c(v)\right\rVert^2+\left\lVert i(v)\right\rVert^2.$$ The datum is realizable exactly when both $c(v)=0$ and $\delta v=0$. When the canonical inverse exists, $$\left\lVert v-Ag\right\rVert^2=\left\lVert c(v)\right\rVert^2+\left\lVert i(v)\right\rVert^2+\left\lVert A(g-Bv)\right\rVert^2.$$*

*Proof.* Take $s(z)$ to be its harmonic representative from SR-33. The difference between any other compatible representative and $s(z)$ lies in $R$, which is orthogonal to the harmonic sector. Pythagoras gives the first formula, including unique attainment of the minimum. The composition of $P_K$ and the quotient map is bounded by one; its harmonic representative is $o(v)$. SR-25 and SR-33 give the intrinsic distance identity. If both displayed tests vanish, then $v\in K$ and its obstruction class is zero, so SR-03 supplies a source. Realizability implies both tests directly. Finally combine the candidate identity of SR-30 with the intrinsic distance split. The minimum representative of an obstruction class belongs to local data space; it is a different construction from the minimum-norm global source $Bv$. ◻

**Formal source:** `Komorebi.SufficientResolution.MetricRepresentatives.unique_minimum_representative`; `Komorebi.SufficientResolution.MetricRepresentatives.representative_error_energy`; `Komorebi.SufficientResolution.IntrinsicGlobalization.projectedClass_opNorm_le`; `Komorebi.SufficientResolution.IntrinsicGlobalization.intrinsic_distance_sq`; `Komorebi.SufficientResolution.IntrinsicGlobalization.realizable_iff_class_and_residual_zero`; `Komorebi.SufficientResolution.IntrinsicGlobalization.intrinsic_candidate_total_error`.

**Hypotheses.** Commuting linear presentation maps; whole local-map norm bound C$\ge$`<!-- -->`{=html}0; reverse presentation with bound M\>0 and induced left inverse for two-sided estimate.

**Theorem 41** (SR-35: Bounded quotient transport and reflection).

*A presentation map with $\left\lVert Lv\right\rVert\le C\left\lVert v\right\rVert$ induces the same quotient map as in SR-03, now satisfying $$\left\lVert \overline Lz\right\rVert\le C\left\lVert z\right\rVert.$$ If a reverse presentation has bound $M>0$ and its quotient map is a left inverse of $\overline L$, then $$\frac{\left\lVert z\right\rVert}{M}\le\left\lVert \overline Lz\right\rVert\le C\left\lVert z\right\rVert.$$ The corresponding class distances satisfy the same bounds.*

*Proof.* For any representative $v$ of $z$, the quotient norm of $[Lv]$ is at most $\left\lVert Lv\right\rVert\le C\left\lVert v\right\rVert$. Infimizing over representatives gives the upper bound and supplies a bounded linear map with exactly the algebraic action of SR-03. Alternatively, the minimum representative from SR-34 realizes the infimum and yields it immediately. Apply the reverse bound to $\overline Lz$: the left-inverse identity gives $\left\lVert z\right\rVert\le M\left\lVert \overline Lz\right\rVert$. Division by positive $M$ proves the lower bound. Apply the bounds to $z-w$ for distances. Forward boundedness alone does not prove reflection; the reverse identity is genuine additional data. ◻

**Formal source:** `Komorebi.SufficientResolution.MetricObstructionTransport.obstructionMap_norm_le`; `Komorebi.SufficientResolution.MetricObstructionTransport.boundedObstructionMap_opNorm`; `Komorebi.SufficientResolution.MetricObstructionTransport.reverse_bound`; `Komorebi.SufficientResolution.MetricObstructionTransport.two_sided_bound`.

**Hypotheses.** Projected nested R0$\le$R1$\le$K in fixed real metric for energy; arbitrary submodule R in real normed space for nonclosed seminorm boundary.

**Theorem 42** (SR-36: Metric refinement and nonclosed boundary).

*Range enlargement induces a surjective contraction $F:K/R_0\to K/R_1$. For the old minimum representative $s_0(z)$, $$\left\lVert z\right\rVert^2=\left\lVert Fz\right\rVert^2+\left\lVert (P_{R_1}-P_{R_0})s_0(z)\right\rVert^2.$$ Without a closedness or projection hypothesis, a general quotient instead has $$\left\lVert [v]\right\rVert=0\iff v\in\mathop{\mathrm{cl}}R,\qquad [v]=0\iff v\in R.$$ Thus its seminorm detects zero exactly when $R$ is closed. Nonclosed range can leave a nonzero class of zero seminorm.*

*Proof.* The larger realization submodule contains the smaller, so the identity on $K$ descends to a surjection of quotients. Every old representative is a new representative, proving contraction by the quotient infimum. For the energy identity apply the orthogonal refinement identity in SR-28 to $s_0(z)$, whose old norm is $\left\lVert z\right\rVert$. The new harmonic component represents $Fz$ and has norm $\left\lVert Fz\right\rVert$ by SR-33.

For any submodule, the native quotient seminorm equals distance to that submodule. Zero distance is equivalent to membership in its closure by the metric closure criterion; algebraic quotient zero remains actual membership. If $R$ is nonclosed, choose $v\in\mathop{\mathrm{cl}}R\setminus R$. Its class is nonzero with zero seminorm. Conversely closedness makes zero distance imply membership. This is why the projection hypotheses in the preceding metric theory cannot be discarded silently. ◻

**Formal source:** `Komorebi.SufficientResolution.MetricRefinement.refinementMap_surjective`; `Komorebi.SufficientResolution.MetricRefinement.refinementMap_norm_le`; `Komorebi.SufficientResolution.MetricRefinement.quotient_refinement_energy`; `Komorebi.SufficientResolution.QuotientMetricBoundaries.zero_norm_iff_closure`; `Komorebi.SufficientResolution.QuotientMetricBoundaries.nonclosed_nonzero_zero_norm`; `Komorebi.SufficientResolution.QuotientMetricBoundaries.norm_detects_zero_iff_closed`.

**Example 43** (A metric must survive its coordinate change). For $K=\{(x,y,0)\}$ and $R=\mathop{\mathrm{span}}\{(1,0,0)\}$, take the compatible basis $b_1=(1,0,0)$, $b_2=(1,2,0)$. Its Gram matrix is $\bigl(\begin{smallmatrix}1&1\\1&5\end{smallmatrix}\bigr)$. The vector $(3,4,0)$ has coordinates $(1,2)$; its harmonic representative $(0,4,0)$ has coordinates $(-2,2)$ and squared norm $16$ in that Gram metric. Computing with an untransported coordinate Euclidean metric would change the problem. Redundant or nonorthogonal coordinates do not license such a change.

# Tikhonov construction, bias, and perturbation

Fix a bounded operator $A:G\to V$ between real Hilbert spaces, without assuming closed range. For $\lambda>0$, put $$N_\lambda=A^*A+\lambda I,\qquad R_\lambda=N_\lambda^{-1},\qquad
B_\lambda=R_\lambda A^*.$$ The inverse is constructed from coercivity. It is not supplied as a certificate premise. Here $A^*$ is the actual Hilbert adjoint.

**Hypotheses.** Real Hilbert G,V; actual bounded A and lambda\>0; no finite dimension or closed range.

**Theorem 44** (SR-37: Constructed normal inverse and energy).

*$N_\lambda$ is a bounded bijection with bounded inverse $R_\lambda$. For $x_\lambda=B_\lambda v$, $$N_\lambda x_\lambda=A^*v,\qquad
A^*(Ax_\lambda-v)+\lambda x_\lambda=0,$$ and $$\left\lVert Ax_\lambda\right\rVert^2+\lambda\left\lVert x_\lambda\right\rVert^2
=\left\langle v,Ax_\lambda\right\rangle.$$*

*Proof.* The bilinear form $b(x,y)=\left\langle Ax,Ay\right\rangle+\lambda\left\langle x,y\right\rangle$ is bounded and satisfies $b(x,x)\ge\lambda\left\lVert x\right\rVert^2$. Lax--Milgram gives a continuous linear equivalence from the source to itself under the Riesz identification. The adjoint identity identifies its map with $A^*A+\lambda I$. The two inverse laws give an actual resolvent. Applying one inverse law to $A^*v$ yields the normal equation. Taking its inner product with $x_\lambda$ and using $\left\langle A^*v,x_\lambda\right\rangle=\left\langle v,Ax_\lambda\right\rangle$ gives the energy identity. Strictly positive $\lambda$ supplies coercivity even if $A$ has a nontrivial kernel or a nonclosed range. ◻

**Formal source:** `Komorebi.SufficientResolution.TikhonovConstruction.normalForm_coercive`; `Komorebi.SufficientResolution.TikhonovConstruction.normalEquiv_apply`; `Komorebi.SufficientResolution.TikhonovConstruction.normal_resolvent`; `Komorebi.SufficientResolution.TikhonovConstruction.resolvent_normal`; `Komorebi.SufficientResolution.TikhonovConstruction.normal_equation`; `Komorebi.SufficientResolution.TikhonovConstruction.solution_energy`.

**Hypotheses.** Same real Hilbert bounded A with lambda\>0; arbitrary source candidate x and data v; actual normal residual.

**Theorem 45** (SR-38: Objective optimality and sharp fixed-parameter bounds).

*For $F_\lambda(v,x)=\left\lVert Ax-v\right\rVert^2+\lambda\left\lVert x\right\rVert^2$, $$F_\lambda(v,x)=F_\lambda(v,x_\lambda)
+\left\lVert A(x-x_\lambda)\right\rVert^2+\lambda\left\lVert x-x_\lambda\right\rVert^2.$$ Thus $x_\lambda$ is the unique minimizer and lies in $(\ker A)^\perp$. The whole-map bounds are $$\left\lVert R_\lambda\right\rVert\le1/\lambda,\qquad
\left\lVert B_\lambda\right\rVert\le\frac1{2\sqrt\lambda},\qquad
\left\lVert AB_\lambda v\right\rVert\le\left\lVert v\right\rVert,\quad\left\lVert AB_\lambda v-v\right\rVert\le\left\lVert v\right\rVert.$$ For $r=N_\lambda x-A^*v$, one has $x-x_\lambda=R_\lambda r$ and $\left\lVert x-x_\lambda\right\rVert\le\left\lVert r\right\rVert/\lambda$.*

*Proof.* Expand both squared norms around $x_\lambda$. Their cross terms combine to $$2\left\langle A^*(Ax_\lambda-v)+\lambda x_\lambda,x-x_\lambda\right\rangle,$$ which vanishes by SR-37. The remaining positive terms prove the increment identity and uniqueness. Taking the normal equation against a kernel vector $k$ yields $\lambda\left\langle x_\lambda,k\right\rangle=0$, proving source orthogonality.

For $y=R_\lambda r$, its energy gives $\lambda\left\lVert y\right\rVert^2\le\left\langle r,y\right\rangle\le\left\lVert r\right\rVert\left\lVert y\right\rVert$, hence the resolvent bound. For $x_\lambda$, set $u=\left\lVert Ax_\lambda\right\rVert$. The energy gives $u^2+\lambda\left\lVert x_\lambda\right\rVert^2\le\left\lVert v\right\rVert\,u$. Completing the square in $u$ yields $4\lambda\left\lVert x_\lambda\right\rVert^2\le\left\lVert v\right\rVert^2$ and also $u\le\left\lVert v\right\rVert$. Comparing the minimum objective with $F_\lambda(v,0)=\left\lVert v\right\rVert^2$ bounds the fitting residual. Subtract the exact normal equation from the computed one and apply the resolvent for the correction identity. ◻

**Formal source:** `Komorebi.SufficientResolution.TikhonovOptimality.objective_increment`; `Komorebi.SufficientResolution.TikhonovOptimality.unique_minimizer`; `Komorebi.SufficientResolution.TikhonovBounds.resolvent_opNorm_bound`; `Komorebi.SufficientResolution.TikhonovBounds.regularized_opNorm_bound`; `Komorebi.SufficientResolution.TikhonovBounds.approximate_solver_bound`; `Komorebi.SufficientResolution.TikhonovBounds.source_kernel_orthogonal`.

**Hypotheses.** Same positive Tikhonov construction; arbitrary g,e; source-coercivity alpha\>0 only for conditioned bound; g=A\*Aw only for source-condition rate.

**Theorem 46** (SR-39: Bias, noise, and kernel content).

*Write $p=P_{(\ker A)^\perp}g$, $k=P_{\ker A}g$. Then $$B_\lambda Ag+\lambda R_\lambda g=g,
\quad B_\lambda(Ag+e)-g=-\lambda R_\lambda g+B_\lambda e,$$ and $$\left\lVert B_\lambda(Ag+e)-g\right\rVert^2
=\left\lVert -\lambda R_\lambda p+B_\lambda e\right\rVert^2+\left\lVert k\right\rVert^2.$$ If $A$ has source coercivity $\alpha>0$, this is at most $$\left(\frac\lambda{\alpha^2+\lambda}\left\lVert p\right\rVert
+\frac{\left\lVert e\right\rVert}{2\sqrt\lambda}\right)^2+\left\lVert k\right\rVert^2.$$ For a supplied source condition $g=A^*Aw$, $\left\lVert B_\lambda Ag-g\right\rVert\le\lambda\left\lVert w\right\rVert$ without requiring closed range.*

*Proof.* The inverse identity $R_\lambda(A^*A+\lambda I)=I$ gives the filter decomposition. Linearity adds the propagated noise. On $\ker A$, $N_\lambda$ acts as $\lambda I$, so $\lambda R_\lambda k=k$. The resolvent preserves the orthogonal complement: pairing its normal equation with every kernel vector proves this directly. Thus the combined identifiable error is orthogonal to $k$, giving the exact squared formula. Bias and noise inside that first term need not be orthogonal to each other.

For $y=R_\lambda p\in(\ker A)^\perp$, source coercivity and its energy give $(\alpha^2+\lambda)\left\lVert y\right\rVert^2\le\left\lVert p\right\rVert\left\lVert y\right\rVert$. Multiply by $\lambda$ and combine with the noise bound in SR-38. For $g=A^*Aw$, the normal-range source filter is a contraction, so $\left\lVert R_\lambda A^*Aw\right\rVert\le\left\lVert w\right\rVert$. Multiplication by $\lambda$ proves the source-condition bias rate. The representation by $w$ is supplied; no controlled $w$ is asserted for every identifiable source. ◻

**Formal source:** `Komorebi.SufficientResolution.TikhonovBias.filter_decomposition`; `Komorebi.SufficientResolution.TikhonovBias.noisy_source_error_squared`; `Komorebi.SufficientResolution.TikhonovBias.full_conditioned_error_squared`; `Komorebi.SufficientResolution.TikhonovBias.source_condition_bias_bound`.

**Hypotheses.** Real Hilbert bounded A,C; positive lambda,mu; actual closed range only for B=A-dagger and intrinsic globalization formulas.

**Theorem 47** (SR-40: Resolvent sensitivity and irreducible local error).

*For two operators and parameters, $$R_{A,\lambda}-R_{C,\mu}
=R_{A,\lambda}(N_{C,\mu}-N_{A,\lambda})R_{C,\mu}.$$ At fixed positive $\lambda$, with $\epsilon=\left\lVert A-C\right\rVert$, $$\left\lVert B_{A,\lambda}-B_{C,\lambda}\right\rVert
\le\frac\epsilon\lambda+
\frac{(\left\lVert A\right\rVert+\left\lVert C\right\rVert)\epsilon\left\lVert C\right\rVert}{\lambda^2}.$$ If $A$ has closed range and canonical inverse $B$, then $B_\lambda v-Bv=-\lambda R_\lambda Bv$. For $\delta A=0$, $$\left\lVert v-AB_\lambda v\right\rVert^2
=\left\lVert c(v)\right\rVert^2+\left\lVert i(v)\right\rVert^2+\left\lVert A(B_\lambda v-Bv)\right\rVert^2.$$*

*Proof.* Multiply the difference of inverses on the left and right by their normal operators, or insert their inverse laws, to obtain the resolvent identity. SR-38 bounds its norm by $\left\lVert N_{C,\mu}-N_{A,\lambda}\right\rVert/(\lambda\mu)$. At equal parameters, $C^*C-A^*A=(C^*-A^*)C+A^*(C-A)$, whose norm is at most $(\left\lVert A\right\rVert+\left\lVert C\right\rVert)\epsilon$. Splitting $R_AA^*-R_CC^*=R_A(A^*-C^*)+(R_A-R_C)C^*$ proves the stated bound. It permits rank changes and is not uniform as $\lambda$ vanishes.

Under closed range, $A^*$ ignores the part of data orthogonal to $\mathop{\mathrm{Ran}}A$, so $B_\lambda v=B_\lambda ABv$. Apply the filter identity to $Bv$ for its bias. The intrinsic candidate identity SR-34 with $g=B_\lambda v$ yields the local error split. Regularization introduces image bias while retaining the same obstruction and inconsistency. ◻

**Formal source:** `Komorebi.SufficientResolution.TikhonovPerturbation.resolvent_difference`; `Komorebi.SufficientResolution.TikhonovPerturbation.regularized_operator_difference_bound`; `Komorebi.SufficientResolution.TikhonovGlobalization.regularized_pseudoinverse_bias`; `Komorebi.SufficientResolution.TikhonovGlobalization.regularized_intrinsic_error`.

**Example 48** (Exact scalar response and a two-coordinate example). For $A_cx=cx$, $B_\lambda v=cv/(c^2+\lambda)$. At $c>0$, $\lambda=c^2$, the value is $v/(2c)$, attaining the noise bound. For $A(g_1,g_2)=(g_1+g_2,0,0)$, $v=(3,4,5)$, and $\lambda=1$, the source is $(1,1)$. Its squared fit is $42=16+25+1$, separating obstruction, inconsistency, and regularization image bias. Its objective is $44$, whereas the unregularized source $(3/2,3/2)$ has penalized objective $91/2$. Positive regularization solves its own stated objective.

# Strong limits and the uniform boundary

The following limits fix one bounded $A$ between real Hilbert spaces. Statements can be indexed by an arbitrary filter. When uniqueness of limits or a converse is used, the filter is required to be nontrivial. Closed range is unnecessary for strong convergence on each fixed source.

**Hypotheses.** Fixed bounded real Hilbert A; positive lambda_i$\to$`<!-- -->`{=html}0 along a filter; arbitrary fixed g; nontrivial filter for exact-limit iff identifiability.

**Theorem 49** (SR-41: Density and strong identifiable-source convergence).

*One has $\mathop{\mathrm{cl}}\mathop{\mathrm{Ran}}(A^*A)=(\ker A)^\perp$, and for every $g,w$, $$\left\lVert B_\lambda Ag-g\right\rVert\le\left\lVert g-A^*Aw\right\rVert+\lambda\left\lVert w\right\rVert.$$ As $\lambda\downarrow0$, $$B_\lambda Ag\longrightarrow P_{(\ker A)^\perp}g,
\qquad \left\lVert B_\lambda Ag-g\right\rVert\longrightarrow\left\lVert P_{\ker A}g\right\rVert.$$ For a nontrivial parameter filter, convergence to $g$ itself holds exactly when $g\in(\ker A)^\perp$.*

*Proof.* If $x$ is orthogonal to $\mathop{\mathrm{Ran}}(A^*A)$, pairing with $A^*Ax$ gives $\left\lVert Ax\right\rVert^2=0$. Conversely a kernel vector is orthogonal to every $A^*Aw$ by the adjoint identity. Thus $(\mathop{\mathrm{Ran}}(A^*A))^\perp=\ker A$, and taking orthogonal complements gives the closure identity. Decompose the bias into the bias of $g-A^*Aw$ and of $A^*Aw$. The first is bounded by its input norm because $\lambda R_\lambda$ is contractive; the second is bounded by $\lambda\left\lVert w\right\rVert$ from SR-39.

For identifiable $p$, density lets us choose $w$ making the first term arbitrarily small, independently of $\lambda$. Then let $\lambda$ tend to zero to remove the second. For arbitrary $g$, $Ag=Ap$ with $p=P_{(\ker A)^\perp}g$, yielding the claimed source limit. Subtracting $g$ and taking norms gives the kernel-error limit. Uniqueness of limits on a nontrivial filter gives the final equivalence. ◻

**Formal source:** `Komorebi.SufficientResolution.TikhonovDensity.gram_range_closure`; `Komorebi.SufficientResolution.TikhonovDensity.source_approximation_bound`; `Komorebi.SufficientResolution.TikhonovConvergence.tendsto_source`; `Komorebi.SufficientResolution.TikhonovConvergence.exact_limit_iff_identifiable`; `Komorebi.SufficientResolution.TikhonovConvergence.tendsto_error_norm`.

**Hypotheses.** Fixed real Hilbert bounded A; lambda_i\>0$\to$`<!-- -->`{=html}0; deterministic noise with $\Vert$e_i$\Vert$/sqrt(lambda_i)$\to$`<!-- -->`{=html}0; actual normal residual scale vanishes for computed sources.

**Theorem 50** (SR-42: Noise schedules and inexact strong limits).

*If $\lambda_i>0$ tends to zero and $\left\lVert e_i\right\rVert/\sqrt{\lambda_i}\to0$, then $$B_{\lambda_i}(Ag+e_i)\longrightarrow P_{(\ker A)^\perp}g.$$ The same limit holds for computed $x_i$ when additionally $$\frac{\left\lVert (A^*A+\lambda_iI)x_i-A^*(Ag+e_i)\right\rVert}{\lambda_i}\to0.$$ For example, $\lambda_i=s_i^2$, $s_i>0\to0$, and $\left\lVert e_i\right\rVert\le s_i^2$ give the exact-solve consistency condition.*

*Proof.* The source difference between noisy and exact-data reconstruction is $B_{\lambda_i}e_i$, whose norm is at most $\left\lVert e_i\right\rVert/(2\sqrt{\lambda_i})$ by SR-38. Combine its vanishing with the exact-source limit in SR-41. For computed sources, the normal-residual correction in SR-38 bounds their difference from the actual regularized source by precisely the second displayed scale. The triangle inequality then proves the same limit. In the square schedule, the noise ratio is at most $s_i$, hence vanishes. These schedules are sufficient conditions; they are not asserted necessary for every favorable operator or noise direction. ◻

**Formal source:** `Komorebi.SufficientResolution.NoisyRegularization.noisy_source_tendsto`; `Komorebi.SufficientResolution.NoisyRegularization.noisy_inexact_solver_tendsto`; `Komorebi.SufficientResolution.NoisyRegularization.square_schedule_consistent`.

**Hypotheses.** Fixed real Hilbert bounded A; positive parameter family$\to$`<!-- -->`{=html}0; nontrivial filter for iff; source conditioning alpha only for positive estimate.

**Theorem 51** (SR-43: Operator-norm convergence exactly at closed range).

*Let $E_\lambda=B_\lambda A-P_{(\ker A)^\perp}$. Always $\left\lVert E_\lambda\right\rVert\le1$. If $\mathop{\mathrm{Ran}}A$ is nonclosed, then $\left\lVert E_\lambda\right\rVert=1$ for every positive parameter. For a positive family tending to zero along a nontrivial filter, $$E_\lambda\to0\text{ in operator norm}\iff\mathop{\mathrm{Ran}}A\text{ is closed}.$$ Under source coercivity $\alpha>0$, $\left\lVert E_\lambda\right\rVert\le\lambda/(\alpha^2+\lambda)$.*

*Proof.* The projected bias bound from SR-39 gives the universal upper bound one. Suppose any bounded $B'$ satisfies $c=\left\lVert B'A-P_S\right\rVert<1$, where $S=(\ker A)^\perp$. For $x\in S$, $$\left\lVert x\right\rVert\le\left\lVert x-B'Ax\right\rVert+\left\lVert B'Ax\right\rVert
\le c\left\lVert x\right\rVert+\left\lVert B'\right\rVert\left\lVert Ax\right\rVert.$$ Therefore $\alpha=(1-c)/(\left\lVert B'\right\rVert+1)>0$ supplies off-kernel coercivity, forcing closed range by SR-32. A nonclosed range thus cannot have $\left\lVert E_\lambda\right\rVert<1$, proving equality. For closed range, source coercivity exists and the conditioned bias bound yields the displayed quantity tending to zero. Conversely convergence to zero contradicts the constant norm one on any nontrivial filter. Strong convergence in SR-41 remains valid in the nonclosed case because it fixes a source before taking the limit. ◻

**Formal source:** `Komorebi.SufficientResolution.UniformRegularization.closed_range_of_approximate_recovery`; `Komorebi.SufficientResolution.UniformRegularization.nonclosed_sourceError_norm`; `Komorebi.SufficientResolution.UniformRegularization.conditioned_sourceError_norm`; `Komorebi.SufficientResolution.UniformRegularization.uniform_convergence_iff_closed_range`.

**Hypotheses.** Fixed real Hilbert bounded A; positive lambda_i$\to$`<!-- -->`{=html}0; data noise$\to$`<!-- -->`{=html}0 for fitted limit; nontrivial filter for impossible source limit.

**Theorem 52** (SR-44: Fitted-data limit and absent source limit).

*For arbitrary data $v$, $$AB_\lambda^Av=B_\lambda^{A^*}A^*v
\longrightarrow P_{\mathop{\mathrm{cl}}\mathop{\mathrm{Ran}}A}v.$$ Adding data noise $e_i\to0$ preserves this fitted-data limit. If $v\in\mathop{\mathrm{cl}}\mathop{\mathrm{Ran}}A\setminus\mathop{\mathrm{Ran}}A$, fitted data converge to $v$ but the corresponding reconstructed source family has no norm limit in $G$.*

*Proof.* The identity $(AA^*+\lambda I)A=A(A^*A+\lambda I)$ and uniqueness of the positive normal inverse prove the dual formula. Apply SR-41 to the bounded operator $A^*$ with source $v$. Its identifiable space is $(\ker A^*)^\perp=\mathop{\mathrm{cl}}\mathop{\mathrm{Ran}}A$, yielding the fitted limit. SR-38 shows $AB_\lambda$ is contractive, so changing data by $e_i$ changes the fitted value by at most $\left\lVert e_i\right\rVert$. If reconstructed sources converged in norm to some $g$, continuity of $A$ would make their images converge to $Ag$. On a nontrivial filter, the already established image limit $v$ would force $Ag=v$, contrary to $v\notin\mathop{\mathrm{Ran}}A$. This proves absence of a source norm limit without adding an unproved assertion that source norms diverge. ◻

**Formal source:** `Komorebi.SufficientResolution.RegularizedDataLimit.fitted_adjoint_identity`; `Komorebi.SufficientResolution.RegularizedDataLimit.fitted_data_tendsto`; `Komorebi.SufficientResolution.RegularizedDataLimit.noisy_fitted_data_tendsto`; `Komorebi.SufficientResolution.RegularizedDataLimit.unrealizable_no_source_limit`.

# Discrepancy selection and strong consistency

Still fix a known bounded $A$ between real Hilbert spaces. Define the actual residual curve on positive parameters $r_v(\lambda)=\left\lVert AB_\lambda v-v\right\rVert$. Its parameter is mathematical data, not an assumed noise estimate. Let $\eta$ be a justified true-data allowance and $\tau>1$ a band multiplier. A total rule must include a small-data branch.

**Hypotheses.** Real Hilbert bounded A; lambda\>0; strict floor dist(v,range A)\<rho\<$\Vert$v$\Vert$ for existence; actual positive parameter only.

**Theorem 53** (SR-45: Actual residual curve and unique interior root).

*The residual is continuous and nondecreasing on positive parameters; the source norm is nonincreasing. It is strictly increasing when $A^*v\ne0$, and constant at $\left\lVert v\right\rVert$ when $A^*v=0$. For $$\mathop{\mathrm{dist}}(v,\mathop{\mathrm{Ran}}A)<\rho<\left\lVert v\right\rVert,$$ there is exactly one $\lambda>0$ with $r_v(\lambda)=\rho$. The resulting exact real parameter is a noncomputable choice with a proved specification.*

*Proof.* Compare the minimum objectives at $0<\lambda<\mu$ using each minimizer as a competitor for the other. Adding the two inequalities gives $(\mu-\lambda)(\left\lVert x_\mu\right\rVert^2-\left\lVert x_\lambda\right\rVert^2)\le0$, so source norms are antitone. Substitution back into the smaller-parameter comparison shows residual monotonicity. If the two residuals were equal, both norms and objective values would be equal, and unique minimization would give $x_\lambda=x_\mu$. Subtracting their normal equations gives $(\mu-\lambda)x_\lambda=0$, hence $x_\lambda=0$ and $A^*v=0$. This proves strictness and the constant case.

The resolvent parameter identity gives, for $s,t\ge a>0$, $$|r_v(s)-r_v(t)|\le
\frac{\left\lVert A\right\rVert\left\lVert A^*v\right\rVert}{a^2}|s-t|,$$ proving continuity on positive compact intervals. The strict floor permits a comparator $g$ with $\left\lVert Ag-v\right\rVert<\rho$; objective minimization at sufficiently small positive $\lambda$ gives a lower residual bracket. For large $\lambda$, $\left\lVert B_\lambda v\right\rVert\le\left\lVert A^*v\right\rVert/\lambda$, so the residual approaches $\left\lVert v\right\rVert>\rho$ and gives an upper bracket. The intermediate value theorem provides a root; strictness gives uniqueness. The floor condition itself excludes the constant orthogonal-data case. ◻

**Formal source:** `Komorebi.SufficientResolution.DiscrepancyResidual.source_norm_antitone`; `Komorebi.SufficientResolution.DiscrepancyResidual.residual_strictMono`; `Komorebi.SufficientResolution.DiscrepancyResidual.residual_constant_of_adjoint_zero`; `Komorebi.SufficientResolution.DiscrepancyResidual.residual_difference_bound`; `Komorebi.SufficientResolution.DiscrepancySelection.exists_unique_parameter_of_distance`.

**Hypotheses.** Fixed bounded real Hilbert A; p$\in$(ker A)$\perp$; family norm bounds $\Vert$x_i$\Vert\le\Vert$p$\Vert$ and true residual $\Vert$Ax_i-Ap$\Vert\to$`<!-- -->`{=html}0.

**Theorem 54** (SR-46: Norm domination converts residual convergence to source convergence).

*If $\left\lVert Ag-v\right\rVert\le r_v(\lambda)$, then $\left\lVert B_\lambda v\right\rVert\le\left\lVert g\right\rVert$. For any $x,p,w$ with $\left\lVert x\right\rVert\le\left\lVert p\right\rVert$, $$\left\lVert x-p\right\rVert^2\le4\left\lVert p\right\rVert\left\lVert p-A^*w\right\rVert+2\left\lVert w\right\rVert\left\lVert Ax-Ap\right\rVert.$$ Consequently, for identifiable fixed $p$, the conditions $\left\lVert x_i\right\rVert\le\left\lVert p\right\rVert$ and $\left\lVert Ax_i-Ap\right\rVert\to0$ imply $x_i\to p$ strongly, without assuming closed range.*

*Proof.* Objective minimality gives $r_v(\lambda)^2+\lambda\left\lVert B_\lambda v\right\rVert^2
\le\left\lVert Ag-v\right\rVert^2+\lambda\left\lVert g\right\rVert^2$. The residual ordering and positive $\lambda$ imply norm domination. For the source estimate, expand $\left\lVert x-p\right\rVert^2$ and use $\left\lVert x\right\rVert\le\left\lVert p\right\rVert$ to obtain $\left\lVert x-p\right\rVert^2\le2\left\langle p,p-x\right\rangle$. Write $p=(p-A^*w)+A^*w$. The first pairing is at most $\left\lVert p-A^*w\right\rVert\left\lVert p-x\right\rVert\le2\left\lVert p\right\rVert\left\lVert p-A^*w\right\rVert$; the adjoint identity bounds the second by $\left\lVert w\right\rVert\left\lVert Ap-Ax\right\rVert$. This yields the displayed estimate. For identifiable $p$, the density in SR-41 permits $w$ with $p-A^*w$ arbitrarily small (take $w=A u$ from the normal range). Fixing this $w$, the residual term tends to zero. An epsilon argument then proves norm convergence. No common inverse bound is invoked. ◻

**Formal source:** `Komorebi.SufficientResolution.DiscrepancyConvergence.norm_domination_of_residual`; `Komorebi.SufficientResolution.DiscrepancyConvergence.source_distance_estimate`; `Komorebi.SufficientResolution.DiscrepancyConvergence.norm_control_residual_tendsto`.

**Hypotheses.** Known bounded $A:G\to V$ between real Hilbert spaces and a fixed true source $g$; a valid pointwise allowance $\left\lVert Ag-v\right\rVert\le\eta$. Accepted-source consistency uses a fixed $\tau\ge1$ and genuine bounds $\left\lVert Ag-v_i\right\rVert\le\eta_i$ with $\eta_i\to0$. Total selector existence additionally requires $\eta>0$ and $\tau>1$.

**Theorem 55** (SR-47: Accepted bands and the total small-data rule).

*Call $x$ accepted when either $$\left\lVert v\right\rVert\le\tau\eta,\quad x=0,$$ or $x=B_\lambda v$ for some $\lambda>0$ with $\eta\le r_v(\lambda)\le\tau\eta$. With a valid noise allowance, every accepted source satisfies $$\left\lVert x\right\rVert\le\left\lVert P_{(\ker A)^\perp}g\right\rVert,\qquad
\left\lVert Ax-Ag\right\rVert\le(\tau+1)\eta.$$ For accepted families with $\eta_i\to0$, $$x_i\to P_{(\ker A)^\perp}g,
\qquad \left\lVert x_i-g\right\rVert\to\left\lVert P_{\ker A}g\right\rVert.$$ With $\eta>0$, $\tau>1$, the total selector chooses zero on small data and otherwise the root $r_v(\lambda)=\tau\eta$. If $g=A^*w$, accepted sources obey $\left\lVert x-g\right\rVert^2\le2\left\lVert w\right\rVert(\tau+1)\eta$.*

*Proof.* Let $p=P_{(\ker A)^\perp}g$, so $Ap=Ag$. In the positive branch, $\left\lVert Ap-v\right\rVert\le\eta\le r_v(\lambda)$ gives norm domination by SR-46; the triangle inequality gives the true residual. In the zero branch, norm domination is immediate and $\left\lVert Ag\right\rVert\le\left\lVert Ag-v\right\rVert+\left\lVert v\right\rVert\le(\tau+1)\eta$. SR-46 now gives strong convergence to $p$, and continuity of the error norm gives the kernel limit. For large data, feasibility supplies $\mathop{\mathrm{dist}}(v,\mathop{\mathrm{Ran}}A)\le\eta<\tau\eta<\left\lVert v\right\rVert$, so SR-45 provides the exact root. For $g=A^*w$, the approximation term in SR-46 is zero, and the residual bound proves the squared source-condition rate. General identifiable sources have no asserted common rate. The rule controls actual Tikhonov sources; numerical solve errors require the additional certificates below. ◻

**Formal source:** `Komorebi.SufficientResolution.DiscrepancyRule.selectedSource_accepted`; `Komorebi.SufficientResolution.DiscrepancyRule.accepted_consistent`; `Komorebi.SufficientResolution.DiscrepancyRule.selectedSource_consistent`; `Komorebi.SufficientResolution.DiscrepancyRule.accepted_error_norm_limit`; `Komorebi.SufficientResolution.DiscrepancyRule.accepted_source_rate`.

**Hypotheses.** Known bounded real Hilbert A and positive lambda; real scalar identity case 0\<rho\<v.

**Theorem 56** (SR-48: Discrepancy endpoints and scalar formulas).

*No positive parameter has residual larger than $\left\lVert v\right\rVert$. When $A^*v\ne0$, none has residual equal to $\left\lVert v\right\rVert$. For every positive parameter, $r_v(\lambda)=0$ exactly when $v=0$. For the real scalar identity model and $0<\rho<v$, $$\lambda=\frac\rho{v-\rho},\qquad B_\lambda v=v-\rho$$ is the unique root at residual $\rho$.*

*Proof.* The first assertion is the residual contraction in SR-38. Equality at $\left\lVert v\right\rVert$ would give $F_\lambda(v,x_\lambda)\le F_\lambda(v,0)=\left\lVert v\right\rVert^2$ while its fit term already equals $\left\lVert v\right\rVert^2$. Hence $x_\lambda=0$, forcing $A^*v=0$. If the residual is zero, then $Ax_\lambda=v$, and the normal equation reduces to $\lambda x_\lambda=0$. Thus $x_\lambda=0$ and $v=0$. The converse is direct. For $A=I$, the normal equation gives $B_\lambda v=v/(1+\lambda)$ and residual $\lambda v/(1+\lambda)$ for $v>0$. Substitution proves the formula and SR-45 supplies uniqueness. These endpoints explain the strict root inequalities and the separate small-data branch. ◻

**Formal source:** `Komorebi.SufficientResolution.DiscrepancyBoundaries.no_parameter_above_data`; `Komorebi.SufficientResolution.DiscrepancyBoundaries.no_parameter_at_data_norm`; `Komorebi.SufficientResolution.DiscrepancyBoundaries.zero_residual_iff_zero_data`; `Komorebi.SufficientResolution.DiscrepancyBoundaries.identity_parameter_formula`.

# Reliable discrepancy with inexact solves

The discrepancy rule of the preceding section selects an actual regularized source. A computed vector need not equal that source, and a displayed residual need not equal its exact norm. Those two errors require separate allowances. The normal equation provides the connection without assuming the computation has already solved the inverse problem.

Throughout this section $A:G\to V$ is bounded between real Hilbert spaces, $N_A=\ker A$, $S_A=N_A^\perp$, and $\lambda>0$. Write $$N_\lambda=A^*A+\lambda I,\qquad
x_\lambda=N_\lambda^{-1}A^*v,\qquad
r_\lambda(x)=N_\lambda x-A^*v .$$ The inverse is the actual positive-parameter constructor already established. The vector $r_\lambda(x)$ is the normal-equation residual of the computed source $x$. Its size measures source correction and image correction on different scales. A fitting residual $\left\lVert Ax-v\right\rVert$ alone does not supply either correction.

**Hypotheses.** Real Hilbert spaces; bounded A; lambda\>0; actual normal residual.

**Theorem 57** (SR-49: Normal residual, two correction scales).

*For every computed source $x$, $$x-x_\lambda=N_\lambda^{-1}r_\lambda(x),\qquad
\left\lVert x-x_\lambda\right\rVert\le\frac{\left\lVert r_\lambda(x)\right\rVert}{\lambda},
\qquad
\left\lVert Ax-Ax_\lambda\right\rVert\le
\frac{\left\lVert r_\lambda(x)\right\rVert}{2\sqrt\lambda}.$$ Consequently $$\left|\left\lVert Ax-v\right\rVert-\left\lVert Ax_\lambda-v\right\rVert\right|
\le\frac{\left\lVert r_\lambda(x)\right\rVert}{2\sqrt\lambda}.$$ The bounds use the same actual residual and the existing Hilbert norms.*

*Proof.* Subtract $N_\lambda x_\lambda=A^*v$ from the definition of the normal residual and apply the inverse. For $u=N_\lambda^{-1}r$, the energy identity gives $$\left\lVert Au\right\rVert^2+\lambda\left\lVert u\right\rVert^2=\left\langle r,u\right\rangle
\le\left\lVert r\right\rVert\,\left\lVert u\right\rVert .$$ Dropping the first term shows $\left\lVert u\right\rVert\le\left\lVert r\right\rVert/\lambda$, including $u=0$. To control the image, complete the scalar square: $$\left\lVert Au\right\rVert^2\le\left\lVert r\right\rVert\,\left\lVert u\right\rVert-\lambda\left\lVert u\right\rVert^2
\le\frac{\left\lVert r\right\rVert^2}{4\lambda}.$$ Both sides of the desired norm inequality are nonnegative, so taking square roots gives the image bound. Set $r=r_\lambda(x)$ and use linearity of $A$. Finally the reverse triangle inequality bounds the difference of the two fitting norms by $\left\lVert A(x-x_\lambda)\right\rVert$.

The distinction matters when $\lambda$ is small. A normal residual sufficient for a prescribed image tolerance may be insufficient for a prescribed source tolerance. If source correction must be at most $\kappa$ and image correction at most $\xi$, a sound pair of conditions is $\left\lVert r_\lambda(x)\right\rVert\le\lambda\kappa$ and $\left\lVert r_\lambda(x)\right\rVert\le2\sqrt\lambda\,\xi$. These are parameter-dependent requirements, not a uniform inverse bound as $\lambda$ tends to zero. ◻

**Formal source:** `Komorebi.SufficientResolution.InexactResidual.correction_identity`; `Komorebi.SufficientResolution.InexactResidual.correction_bound`; `Komorebi.SufficientResolution.InexactResidual.image_correction_bound`; `Komorebi.SufficientResolution.InexactResidual.fitting_residual_difference`.

**Hypotheses.** Same Hilbert setting; nonnegative source/image/evaluation budgets; positive parameter; genuine measurement enclosure.

**Theorem 58** (SR-50: Protected measured discrepancy margins).

*Suppose $m$ is a measured fitting norm with $$|m-\left\lVert Ax-v\right\rVert|\le\omega,\quad
\left\lVert r_\lambda(x)\right\rVert\le\lambda\kappa,\quad
\left\lVert r_\lambda(x)\right\rVert\le2\sqrt\lambda\,\xi .$$ If $$\eta+\omega+\xi\le m\le\tau\eta-\omega-\xi,$$ then the actual exact source $x_\lambda$ has discrepancy in $[\eta,\tau\eta]$, and $\left\lVert x-x_\lambda\right\rVert\le\kappa$. A protected scalar window exists exactly when $$2(\omega+\xi)\le(\tau-1)\eta .$$ Its midpoint $(\tau+1)\eta/2$ is then admissible.*

*Proof.* SR-49 and the measurement enclosure imply $$|m-\left\lVert Ax_\lambda-v\right\rVert|
\le |m-\left\lVert Ax-v\right\rVert|+
|\left\lVert Ax-v\right\rVert-\left\lVert Ax_\lambda-v\right\rVert|
\le\omega+\xi .$$ Subtracting this total allowance from the lower protected inequality gives $\eta\le\left\lVert Ax_\lambda-v\right\rVert$. Adding it to the upper inequality gives $\left\lVert Ax_\lambda-v\right\rVert\le\tau\eta$. The source-correction bound follows from the other residual condition in SR-49. Hence the computed source is within $\kappa$ of an actual accepted discrepancy source.

The scalar window is nonempty exactly when its lower endpoint is at most its upper endpoint. Rearrangement gives the displayed condition. The proposed midpoint is the mean of the endpoints; direct substitution gives both inequalities. No property of an approximate solver is hidden in this scalar calculation: its residual, measurement enclosure and correction allowance have already been supplied.

For example, let $\eta=1/10$, $\tau=2$, and $\omega=\xi=1/100$. The total protected margin is $1/50$, and the interval is $[3/25,9/50]$. Its midpoint is $3/20$. This allocation proves room for the measurement and image-correction errors; it does not prove that a particular computed source attains the interval or that $1/10$ is a true data-noise allowance. ◻

**Formal source:** `Komorebi.SufficientResolution.InexactResidual.measured_band_transfer`; `Komorebi.SufficientResolution.InexactDiscrepancy.measured_certificate`; `Komorebi.SufficientResolution.InexactToleranceCertificates.protected_window_exists_iff`; `Komorebi.SufficientResolution.InexactToleranceCertificates.protected_midpoint`.

**Hypotheses.** Fixed bounded real Hilbert A; actual noise bounds; fixed tau; NearAccepted with source budget tending to zero.

**Theorem 59** (SR-51: Near-accepted consistency and kernel leakage).

*Call $x$ near accepted with budget $\kappa$ when some exact accepted source $y$ satisfies $\left\lVert x-y\right\rVert\le\kappa$. If $\left\lVert Ag-v_i\right\rVert\le\eta_i$, $\eta_i\to0$, and near-accepted $x_i$ have $\kappa_i\to0$, then $$x_i\longrightarrow P_{S_A}g,\qquad
\left\lVert x_i-g\right\rVert\longrightarrow\left\lVert P_{N_A}g\right\rVert.$$ At every index $\left\lVert P_{N_A}x_i\right\rVert\le\kappa_i$; therefore the computed true-kernel component tends to zero. No separate parameter schedule is assumed.*

*Proof.* Choose accepted comparison sources $y_i$ from the definition. Exact accepted consistency gives $y_i\to p=P_{S_A}g$, while $\left\lVert x_i-y_i\right\rVert\le\kappa_i\to0$ gives $x_i-y_i\to0$. Adding the two limits proves $x_i\to p$. Continuity of the norm gives the source-error limit, because $p-g=-P_{N_A}g$.

The exact accepted source belongs to $S_A$, including the small-data zero branch. Orthogonal projection is nonexpansive, so $$\left\lVert P_{N_A}x_i\right\rVert
=\left\lVert P_{N_A}(x_i-y_i)\right\rVert
\le\left\lVert x_i-y_i\right\rVert\le\kappa_i .$$ This pointwise estimate only needs near acceptance, not a truth-noise premise. Source consistency additionally needs the stated true-noise allowance tending to zero.

The underlying exact consistency theorem has substantive content even for a nonclosed range. Accepted sources satisfy norm domination $\left\lVert y_i\right\rVert\le\left\lVert p\right\rVert$ and $\left\lVert Ay_i-Ap\right\rVert\to0$. Since $p\in S_A=\mathop{\mathrm{cl}}\mathop{\mathrm{Ran}}A^*$, approximate $p$ by $A^*w$ and use $$\left\lVert y_i-p\right\rVert^2
\le2\left\langle p,p-y_i\right\rangle
\le2\left\lVert p-A^*w\right\rVert\left\lVert p-y_i\right\rVert
+2\left\lVert w\right\rVert\,\left\lVert A(p-y_i)\right\rVert .$$ The first factor $\left\lVert p-y_i\right\rVert$ is bounded by $2\left\lVert p\right\rVert$. First choose the approximation accurately, then let $i$ tend along the filter. This proves strong convergence without a bounded inverse. ◻

**Formal source:** `Komorebi.SufficientResolution.InexactDiscrepancy.NearAccepted`; `Komorebi.SufficientResolution.InexactDiscrepancy.near_kernel_leakage`; `Komorebi.SufficientResolution.InexactConsistency.near_consistent`; `Komorebi.SufficientResolution.InexactConsistency.near_error_norm_limit`; `Komorebi.SufficientResolution.InexactConsistency.near_kernel_tendsto_zero`.

**Hypotheses.** Real Hilbert spaces; positive lambda; nonnegative scalar certificate fields; squared inequalities against actual norms.

**Theorem 60** (SR-52: Squared proof-carrying discrepancy certificate).

*Suppose a record supplies $\lambda>0$, nonnegative $\rho,\xi,\kappa,m,\omega$, and $$\left\lVert r_\lambda(x)\right\rVert^2\le\rho^2,\quad
\rho^2\le(\lambda\kappa)^2,\quad
\rho^2\le4\lambda\xi^2,$$ $$\max(0,m-\omega)^2\le\left\lVert Ax-v\right\rVert^2\le(m+\omega)^2,
\qquad
\eta+\omega+\xi\le m\le\tau\eta-\omega-\xi .$$ Then $x$ is near accepted with source budget $\kappa$. Families of such records give SR-51 when the genuine data allowances and source budgets tend to zero.*

*Proof.* All quantities whose squares are compared are nonnegative. The first two inequalities therefore give $\left\lVert r_\lambda(x)\right\rVert\le\rho\le\lambda\kappa$. The third gives $\rho\le2\sqrt\lambda\,\xi$ because $(2\sqrt\lambda\,\xi)^2=4\lambda\xi^2$.

Put $d=\left\lVert Ax-v\right\rVert\ge0$. The squared fitting enclosure is equivalent to the unsquared enclosure $\max(0,m-\omega)\le d\le m+\omega$. Since $d\ge0$, its lower part is equivalent to $m-\omega\le d$. Together these say $|m-d|\le\omega$. Thus every premise of SR-50 has been obtained from the supplied record, and its conclusion proves soundness. Apply SR-51 pointwise for the family statement.

The record does not establish the truth of the data-noise allowance. It establishes a relation between the computed source, actual normal residual and actual fitting norm. An implementation may check rational squared inequalities without numerical square roots, but that requires a faithful enclosure of these actual quantities. The generic Lean structure is proof-carrying; a serialized Python record and its parser are separate implementation evidence.

If the normal residual itself is evaluated approximately as $\widehat r$, the distinct assumptions $\left\lVert r_\lambda(x)-\widehat r\right\rVert\le\nu$ and $\left\lVert \widehat r\right\rVert\le\widehat\rho$ give the allowance $\widehat\rho+\nu$. Substituting that sum into both correction tests retains the evaluation error rather than silently identifying it with zero. ◻

**Formal source:** `Komorebi.SufficientResolution.InexactToleranceCertificates.squared_enclosure_iff`; `Komorebi.SufficientResolution.InexactToleranceCertificates.squared_image_budget`; `Komorebi.SufficientResolution.InexactToleranceCertificates.PositiveCertificate`; `Komorebi.SufficientResolution.InexactToleranceCertificates.certificate_sound`; `Komorebi.SufficientResolution.InexactToleranceCertificates.certificate_consistent`.

# Uncertain operators and changing identifiable models

Data noise, solver error and model error are different inputs. Let $A$ be the true forward operator and $C$ the available operator, acting between the same real Hilbert spaces. The premise $\left\lVert C-A\right\rVert\le\delta$ is a whole-operator allowance. A small residual for one source does not establish it. This section first uses a fixed cap $M$ on a true comparison source. The next section removes that cap from the acceptance rule by making the allowance depend on the candidate itself.

**Hypotheses.** Same normed source/target; bounded A,C; whole operator allowance; genuine data allowance and source cap.

**Theorem 61** (SR-53: Effective model-noise allowance).

*If $\left\lVert C-A\right\rVert\le\delta$, $\left\lVert p\right\rVert\le M$ and $\left\lVert Ap-v\right\rVert\le\eta$, then $$\left\lVert Cp-v\right\rVert\le\epsilon:=\eta+\delta M.$$ For every candidate $x$, $$|\left\lVert Ax-v\right\rVert-\left\lVert Cx-v\right\rVert|\le\delta\left\lVert x\right\rVert.$$ If $|m-\left\lVert Cx-v\right\rVert|\le\omega$, then $|m-\left\lVert Ax-v\right\rVert|\le\omega+\delta\left\lVert x\right\rVert$. The effective-noise allowance is sharp in scalar examples.*

*Proof.* The definition of operator norm gives $\left\lVert Cp-Ap\right\rVert\le\delta\left\lVert p\right\rVert$. Because a norm bound implies $\delta\ge0$, the source cap gives $$\left\lVert Cp-v\right\rVert\le\left\lVert Cp-Ap\right\rVert+\left\lVert Ap-v\right\rVert
\le\delta M+\eta .$$ For the fitting-norm comparison, apply the reverse triangle inequality to $Ax-v$ and $Cx-v$, whose difference is $(A-C)x$. Combining this with the measurement enclosure gives the last claim.

To see the possible equality, take real scalar maps $A=1$, $C=1+\delta$, $p=M$ and $v=M-\eta$, with $\eta,\delta,M\ge0$. Then $Cp-v=\delta M+\eta\ge0$, so its absolute value is exactly $\epsilon$. The source-size factor cannot generally be omitted: for fixed $\delta>0$, the action difference $\delta|p|$ grows without bound as $|p|$ grows. Thus replacing $\delta M$ by an operator-only constant would strengthen the contract incorrectly. ◻

**Formal source:** `Komorebi.SufficientResolution.OperatorUncertainty.action_error`; `Komorebi.SufficientResolution.OperatorUncertainty.effective_data_noise`; `Komorebi.SufficientResolution.OperatorUncertainty.fitting_norm_difference`; `Komorebi.SufficientResolution.OperatorUncertainty.measured_true_fitting_envelope`; `Komorebi.SufficientResolution.OperatorUncertaintyExamples.inflated_noise_sharp`.

**Hypotheses.** Same real Hilbert spaces; bounded A,C; positive or arbitrary common normal parameter; whole norm error delta.

**Theorem 62** (SR-54: Transport of actual normal residuals).

*For the normal residuals formed with the same parameter, $$r^A_\lambda(x)-r^C_\lambda(x)
=(A^*-C^*)(Cx-v)+A^*(A-C)x .$$ If $\left\lVert C-A\right\rVert\le\delta$, then $$\left\lVert r^A_\lambda(x)-r^C_\lambda(x)\right\rVert
\le\delta\bigl(\left\lVert Cx-v\right\rVert+(\left\lVert C\right\rVert+\delta)\left\lVert x\right\rVert\bigr).$$ Hence a computed-model normal allowance $\left\lVert r^C_\lambda(x)\right\rVert\le\rho$ gives the corresponding true normal allowance by adding this expression.*

*Proof.* Expand the two residuals. The $\lambda x$ terms cancel. Insert and subtract $A^*Cx$ to obtain the displayed identity. Adjoint isometry gives $\left\lVert A^*-C^*\right\rVert=\left\lVert A-C\right\rVert\le\delta$ and $\left\lVert A^*\right\rVert=\left\lVert A\right\rVert$. Submultiplicativity therefore bounds its two terms by $\delta\left\lVert Cx-v\right\rVert$ and $\left\lVert A\right\rVert\,\delta\left\lVert x\right\rVert$. The triangle inequality gives $\left\lVert A\right\rVert\le\left\lVert C\right\rVert+\delta$, yielding a bound written in terms of available-model quantities and the allowance. Finally apply $\left\lVert r^A\right\rVert\le\left\lVert r^C\right\rVert+\left\lVert r^A-r^C\right\rVert$.

The identity itself does not require a positive parameter; positivity is needed when this transported residual is used in SR-49 to control an inverse correction. The model error remains distinct from the solver's normal residual. Both contributions are amplified by the corresponding positive-parameter correction scale. A small fixed model allowance is therefore not a uniform guarantee when $\lambda$ tends to zero. ◻

**Formal source:** `Komorebi.SufficientResolution.OperatorResidualTransport.normal_residual_difference`; `Komorebi.SufficientResolution.OperatorResidualTransport.normal_residual_available_bound`; `Komorebi.SufficientResolution.OperatorResidualTransport.true_normal_residual_bound`.

**Hypotheses.** Same real Hilbert spaces; fixed true bounded A, fixed real tau and fixed identifiable p; source cap M; true bounds and exact/near accepted uncertain-model sources; vanishing allowances.

**Theorem 63** (SR-55: Strong consistency without matching model kernels).

*Suppose $p\in S_A$, $\left\lVert p\right\rVert\le M$, and $$\left\lVert C_i-A\right\rVert\le\delta_i,\qquad
\left\lVert Ap-v_i\right\rVert\le\eta_i .$$ If $x_i$ lies within $\kappa_i$ of an exact accepted source for $C_i,v_i$ with allowance $\epsilon_i=\eta_i+\delta_iM$, and $\eta_i,\delta_i,\kappa_i\to0$, then $x_i\to p$. The model kernels and ranks may change. For arbitrary $g$, using $p=P_{S_A}g$ yields $\left\lVert x_i-g\right\rVert\to\left\lVert P_{N_A}g\right\rVert$ and $P_{N_A}x_i\to0$.*

*Proof.* Let $y_i$ be the exact accepted comparison. SR-53 makes $p$ feasible for the available model at allowance $\epsilon_i$. In the positive branch, regularized optimality and the lower discrepancy bound give $\left\lVert y_i\right\rVert\le\left\lVert p\right\rVert$: compare the objective at $y_i$ and $p$, then cancel the fitting terms using $\left\lVert C_ip-v_i\right\rVert\le\epsilon_i\le\left\lVert C_iy_i-v_i\right\rVert$. The small-data branch is zero and satisfies the same domination.

The upper discrepancy bound gives $\left\lVert C_iy_i-v_i\right\rVert\le\tau\epsilon_i$. Returning to the true operator, $$\left\lVert Ay_i-Ap\right\rVert
\le\delta_i\left\lVert y_i\right\rVert+\tau\epsilon_i+\eta_i
\le(\tau+1)\epsilon_i .$$ Thus $y_i$ is norm dominated by the fixed identifiable $p$ and has true image residual tending to zero. The density argument printed in SR-51 proves $y_i\to p$ without projecting onto the changing model kernels. The near-source difference then tends to zero, proving $x_i\to p$.

For arbitrary $g$, $AP_{S_A}g=Ag$, so the same true-data bound applies to $p=P_{S_A}g$. Continuity of norm and true-kernel projection gives the remaining limits. The fixed cap concerns this limiting identifiable source. It is not a claim that the minimum-norm sources for unrelated models have already converged. ◻

**Formal source:** `Komorebi.SufficientResolution.ChangingDiscrepancy.norm_control`; `Komorebi.SufficientResolution.ChangingDiscrepancy.near_true_residual`; `Komorebi.SufficientResolution.ChangingConsistency.projected_consistent`; `Komorebi.SufficientResolution.ChangingConsistency.source_error_limit`; `Komorebi.SufficientResolution.ChangingConsistency.true_kernel_leakage_tendsto_zero`.

**Hypotheses.** Real Hilbert setting; operational checks use C; external true allowances and source cap; positive effective allowance and tau\>1 for selection.

**Theorem 64** (SR-56: Available-model certificate and selected-source soundness).

*A source is certified using $C$ when either $\left\lVert v\right\rVert\le\tau\epsilon$ and $\left\lVert x\right\rVert\le\kappa$, or it has an SR-52 positive certificate for $C$ with allowance $\epsilon=\eta+\delta M$. Such a source is near accepted for the available model. With the external truth premises of SR-55 and vanishing allowances, certified sources converge to the true identifiable source.*

*If $\epsilon>0$ and $\tau>1$, those truth premises also give feasibility of the total exact discrepancy selector for $C$; the selected exact sources are consistent under the same vanishing data/operator bounds.*

*Proof.* In the small-data branch compare $x$ with the accepted zero source: $\left\lVert x-0\right\rVert\le\kappa$. In the positive branch, SR-52 supplies an actual accepted comparison source at distance at most $\kappa$. This proves operational soundness without using $A$.

For the true conclusion, separately supply $\left\lVert C-A\right\rVert\le\delta$, the true-data bound, and $\left\lVert p\right\rVert\le M$. These hypotheses are not fields established by an observed fitting certificate. They allow SR-55 to be applied to every certified source.

SR-53 gives the feasible witness $p$ for the available model. A positive effective allowance and $\tau>1$ ensure a strict residual target above its attainable floor in the non-small-data case; the total discrepancy construction chooses an actual positive-parameter source there and zero in the other branch. Each selected source is exact accepted, so SR-55 applies with $\kappa=0$. This selected object is noncomputable in the generic formalization. Its existence theorem and soundness are distinct from a finite numerical search implementation. ◻

**Formal source:** `Komorebi.SufficientResolution.OperatorCertificates.Certified`; `Komorebi.SufficientResolution.OperatorCertificates.certified_near`; `Komorebi.SufficientResolution.OperatorCertificates.certified_consistent`; `Komorebi.SufficientResolution.OperatorCertificates.inflated_feasibility`; `Komorebi.SufficientResolution.OperatorCertificates.selected_from_allowances_consistent`.

# Candidate-dependent discrepancy without a supplied source cap

The acceptance rule can avoid an externally supplied number $M$ by using the candidate itself in the uncertainty allowance. Put $$c_{\eta,\delta}(x)=\eta+\delta\left\lVert x\right\rVert .$$ A generalized accepted source is either zero in the small-data branch $\left\lVert v\right\rVert\le\tau\eta$, or an actual Tikhonov source whose residual lies between $c_{\eta,\delta}(x)$ and $\tau c_{\eta,\delta}(x)$. This definition contains $C,v,\eta,\delta,\tau,x$ and the positive parameter; it does not contain a true-source cap. Feasibility remains a separate question and retains a quantitative relation between model accuracy and the true noise scale.

**Hypotheses.** Real Hilbert spaces; bounded C; lambda\>0; delta$\ge$`<!-- -->`{=html}0; feasible comparison p for candidate noise; actual regularized candidate.

**Theorem 65** (SR-57: Candidate-dependent self-bounding).

*Let $x$ be the actual regularized source for $C,v,\lambda$. If $$\left\lVert Cp-v\right\rVert\le c_{\eta,\delta}(p),\qquad
c_{\eta,\delta}(x)\le\left\lVert Cx-v\right\rVert,$$ then $\left\lVert x\right\rVert\le\left\lVert p\right\rVert$. In particular, if $\left\lVert C-A\right\rVert\le\delta$ and $\left\lVert Ap-v\right\rVert\le\eta$, every generalized accepted source satisfies $\left\lVert x\right\rVert\le\left\lVert p\right\rVert$.*

*Proof.* Suppose instead $\left\lVert x\right\rVert>\left\lVert p\right\rVert$. Since $\delta\ge0$, candidate noise is monotone in source norm: $c_{\eta,\delta}(p)\le c_{\eta,\delta}(x)$. The two displayed hypotheses imply $\left\lVert Cp-v\right\rVert\le\left\lVert Cx-v\right\rVert$. Comparing Tikhonov objectives, the fitting-square term at $p$ is no larger, whereas its positive weighted source-square term is strictly smaller. The total objective at $p$ is strictly smaller than the objective at its actual unique minimizer $x$, a contradiction.

With true operator bounds, SR-53 applied using $M=\left\lVert p\right\rVert$ gives the required candidate-noise feasibility. The operator allowance implies $\delta\ge0$. The positive accepted branch therefore satisfies the lemma; the small-data branch $x=0$ satisfies the norm conclusion directly.

The lower discrepancy inequality is decisive. An upper residual bound alone can allow overly large regularized source norms. Here the lower bound grows with the candidate norm, and objective minimality prevents that growth from exceeding a feasible comparison source. The comparison source enters the proof of soundness, while the acceptance definition continues to have no externally supplied source cap. ◻

**Formal source:** `Komorebi.SufficientResolution.GeneralizedDiscrepancy.regularized_norm_domination`; `Komorebi.SufficientResolution.GeneralizedDiscrepancy.accepted_norm_control`.

**Hypotheses.** Real Hilbert spaces; true whole-operator/data bounds; tau$\ge$`<!-- -->`{=html}0; generalized accepted or near-accepted sources; vanishing allowances.

**Theorem 66** (SR-58: Generalized true residual and strong consistency).

*A generalized accepted $x$ obeys $$\left\lVert Ax-Ap\right\rVert\le(\tau+1)c_{\eta,\delta}(p).$$ A source within $\kappa$ of such an $x$ obeys the same bound with $\left\lVert A\right\rVert\,\kappa$ added. For $p\in S_A$, vanishing data/operator allowances and near-source budgets imply strong convergence to $p$. If $p=A^*w$, an inexact accepted candidate also satisfies $$\left\lVert x-p\right\rVert^2\le
2\kappa^2+4\left\lVert w\right\rVert(\tau+1)c_{\eta,\delta}(p).$$*

*Proof.* SR-57 gives $\left\lVert x\right\rVert\le\left\lVert p\right\rVert$, so $c_{\eta,\delta}(x)\le c_{\eta,\delta}(p)$. The upper generalized discrepancy bound and $\tau\ge0$ yield $\left\lVert Cx-v\right\rVert\le\tau c_{\eta,\delta}(p)$. Insert $Cx$ and $v$ into the true residual: $$\left\lVert Ax-Ap\right\rVert\le
\delta\left\lVert x\right\rVert+\left\lVert Cx-v\right\rVert+\eta
\le(\tau+1)c_{\eta,\delta}(p).$$ For a near candidate, split its image difference through the exact accepted comparison and apply the operator norm bound to the correction.

As $\eta_i,\delta_i\to0$, the comparison-source noise $\eta_i+\delta_i\left\lVert p\right\rVert$ tends to zero. Exact candidates are norm dominated by $p$ and have true image error tending to zero; the same density argument as SR-51 proves their strong convergence. Add a vanishing near-source difference for inexact candidates. No relative feasibility condition is needed in this implication once accepted candidates have been supplied.

For the source-condition rate, norm domination and $p=A^*w$ give $$\left\lVert y-p\right\rVert^2\le2\left\langle p,p-y\right\rangle\le2\left\lVert w\right\rVert\,\left\lVert A(p-y)\right\rVert$$ for an exact comparison $y$. Bound its image by the first conclusion. Then $\left\lVert x-p\right\rVert\le\left\lVert x-y\right\rVert+\left\lVert y-p\right\rVert$ and $(a+b)^2\le2a^2+2b^2$ prove the stated inexact rate. ◻

**Formal source:** `Komorebi.SufficientResolution.GeneralizedDiscrepancy.accepted_true_residual`; `Komorebi.SufficientResolution.GeneralizedDiscrepancy.accepted_consistent`; `Komorebi.SufficientResolution.GeneralizedInexact.near_true_residual`; `Komorebi.SufficientResolution.GeneralizedInexact.near_consistent`; `Komorebi.SufficientResolution.GeneralizedInexact.near_source_condition_rate`.

**Hypotheses.** Real Hilbert spaces; eta\>0,tau\>1; true operator/data bounds; delta$\Vert$p$\Vert$\<(tau-1)eta.

**Theorem 67** (SR-59: Relative feasibility and noncomputable selection).

*If $\left\lVert C-A\right\rVert\le\delta$, $\left\lVert Ap-v\right\rVert\le\eta$ and $$\delta\left\lVert p\right\rVert<(\tau-1)\eta,$$ then an accepted source exists with norm at most $\left\lVert p\right\rVert$. In the large-data case one can choose a positive parameter whose residual is exactly $\tau\eta$. A sufficient ratio condition is $\delta\le\gamma\eta$ and $\gamma\left\lVert p\right\rVert<\tau-1$. Noncomputably selected families converge to $p\in S_A$ when the data/operator allowances vanish and the pointwise feasibility conditions hold.*

*Proof.* The true bounds imply $\left\lVert Cp-v\right\rVert\le\eta+\delta\left\lVert p\right\rVert<\tau\eta$. If $\left\lVert v\right\rVert\le\tau\eta$, the zero source is accepted. Otherwise the strict attainable-floor bound and $\tau\eta<\left\lVert v\right\rVert$ give a positive exact discrepancy root for $C$ with residual $\tau\eta$. Let $x$ be its actual Tikhonov source. Objective comparison, or the fixed-noise domination lemma, gives $\left\lVert x\right\rVert\le\left\lVert p\right\rVert$. Consequently $$c_{\eta,\delta}(x)\le\eta+\delta\left\lVert p\right\rVert<\tau\eta
=\left\lVert Cx-v\right\rVert.$$ Because $\delta\ge0$ and $\tau>1$, $\tau\eta\le\tau c_{\eta,\delta}(x)$. Thus both generalized band inequalities hold.

Multiplying $\delta\le\gamma\eta$ by $\left\lVert p\right\rVert\ge0$ and the strict margin $\gamma\left\lVert p\right\rVert<\tau-1$ by $\eta>0$ proves the ratio specialization. The chosen source is defined by classical choice from the existence theorem. Its raw definition takes $A,p$ and the truth/feasibility proofs as arguments; it is a theorem-level witness rather than an extracted algorithm using only available measurements. Each chosen source is accepted, so SR-58 proves the family convergence. The selection theorem retains the feasibility premises even though the acceptance predicate has no supplied scalar source cap. ◻

**Formal source:** `Komorebi.SufficientResolution.GeneralizedDiscrepancySelection.positive_parameter_source`; `Komorebi.SufficientResolution.GeneralizedDiscrepancySelection.exists_accepted`; `Komorebi.SufficientResolution.GeneralizedDiscrepancySelection.selectedSource`; `Komorebi.SufficientResolution.GeneralizedFeasibility.relative_accuracy_of_scaled_error`; `Komorebi.SufficientResolution.GeneralizedDiscrepancyConsistency.selected_consistent`.

**Hypotheses.** Same Hilbert setting; near exact generalized acceptance with vanishing correction budget; scalar boundary uses valid but nonvanishing model allowance.

**Theorem 68** (SR-60: Inexact generalized sources and the zero-model boundary).

*Near-generalized acceptance is preserved by enlarging a source-correction budget and gives the consistency conclusion of SR-58 when that budget tends to zero. Nevertheless valid true-noise and operator allowances alone do not ensure generalized feasibility. With $A=1$, $C=0$, $p=v=1$, $\eta=1/10$, $\delta=1$ and $\tau=2$, no source is generalized accepted.*

*Proof.* Near acceptance means there exists an exact generalized accepted comparison $y$ with $\left\lVert x-y\right\rVert\le\kappa$. Increasing $\kappa$ preserves that inequality. Along a family, choosing the comparisons and adding the vanishing difference proves consistency by SR-58.

For the scalar boundary, the true data error is zero and $\left\lVert C-A\right\rVert=1\le\delta$, so both stated truth allowances are valid. The small-data branch would require $1\le2/10$, which is false. For every positive parameter, the actual regularized source of $C=0$ is zero and its fitting residual is one. Its candidate noise is $1/10+1\cdot0=1/10$, so the upper generalized band would again require $1\le2/10$. Every branch fails. The relative feasibility condition also fails, since $1<(2-1)/10$ is false. Thus the boundary refutes an unconditional existence interpretation, not the conditional theorem.

For comparison, take $A=C=1$, $v=1$, $\eta=1/10$, $\delta=0$, $\tau=2$ and $\lambda=1/4$. Then $x_\lambda=4/5$ and the residual is $1/5$. It lies in $[1/10,2/10]$, so the candidate is accepted, and $0<(2-1)/10$ verifies the strict feasibility margin. These examples use the actual scalar normal inverse and exact norms, not a substituted approximate residual. ◻

**Formal source:** `Komorebi.SufficientResolution.GeneralizedInexact.NearAccepted`; `Komorebi.SufficientResolution.GeneralizedInexact.near_consistent`; `Komorebi.SufficientResolution.GeneralizedDiscrepancyExamples.identity_candidate_accepted`; `Komorebi.SufficientResolution.GeneralizedDiscrepancyExamples.zero_model_not_accepted`; `Komorebi.SufficientResolution.GeneralizedDiscrepancyExamples.zero_model_valid_true_bounds`; `Komorebi.SufficientResolution.GeneralizedDiscrepancyExamples.zero_model_relative_accuracy_fails`.

# Calibration generates an operator allowance

The final link connects justified calibration measurements with the whole-operator premise used above. It does not infer the calibration truth allowance from the model's own fit. Let $K$ be a real normed calibration coordinate space, $G$ a real normed source space and $V$ a real normed response space. A split frame has bounded synthesis $U:K\to G$ and analysis $R:G\to K$ with $UR=I_G$. Its coordinates may be redundant: $U$ need not be injective or square. The reconstruction identity requires coverage of every source direction.

The observed response $Y:K\to V$ is an operator, and the assumptions $\left\lVert Y-AU\right\rVert\le\eta_{\rm cal}$ and $\left\lVert Y-CU\right\rVert\le f$ are operator-norm enclosures. Individual calibration samples do not automatically give these enclosures. A mathematical or experimental justification of $\eta_{\rm cal}$ remains a separate input.

**Hypotheses.** Real normed spaces; bounded U,R with UR=I; whole calibration truth/model-fit operator bounds.

**Theorem 69** (SR-61: Redundant split calibration identifies the operator).

*Every bounded source operator $T$ factors as $T=(TU)R$. Therefore $$C-A=((CU)-(AU))R,\qquad
\left\lVert C-A\right\rVert\le(\eta_{\rm cal}+f)\left\lVert R\right\rVert .$$ If a supplied analysis bound is $\left\lVert R\right\rVert\le k$, the allowance is at most $(\eta_{\rm cal}+f)k$. Exact calibration $Y=AU=CU$ forces $A=C$.*

*Proof.* For every source $g$, $URg=g$, so $Tg=TU(Rg)$. This proves the actual factorization, including its application to $C-A$. The triangle inequality through the common measured operator gives $$\left\lVert CU-AU\right\rVert\le\left\lVert CU-Y\right\rVert+\left\lVert Y-AU\right\rVert
\le f+\eta_{\rm cal}.$$ Submultiplicativity then yields the displayed allowance. Both measured bounds imply their scalar allowances are nonnegative; hence replacing $\left\lVert R\right\rVert$ by a larger $k$ preserves the inequality. With exact calibration, $CU-AU=0$ and the factorization gives $C-A=0$.

Redundancy causes no logical problem. For instance, let $K=\mathbb R^2$, $G=\mathbb R$, $U(k_1,k_2)=k_1$ and $Rg=(g,0)$, with the standard product norm. Then $UR=I$, $\left\lVert U\right\rVert=\left\lVert R\right\rVert=1$, but $U$ has a nontrivial kernel. The frame spans the source even though it has an unused coordinate. A true scalar map $A=a$ and model $C=c$ with measured row $Y(k_1,k_2)=yk_1$ give $|y-a|\le\eta_{\rm cal}$ and $|y-c|\le f$, hence $|c-a|\le\eta_{\rm cal}+f$. The same estimate comes from the general factorization rather than assuming the coordinates are square and invertible. ◻

**Formal source:** `Komorebi.SufficientResolution.CalibrationFrame.Frame.factor_through_frame`; `Komorebi.SufficientResolution.CalibrationFrame.Frame.difference_factorization`; `Komorebi.SufficientResolution.CalibrationFrame.Frame.measured_operator_bound`; `Komorebi.SufficientResolution.CalibrationFrame.Frame.measured_operator_bound_of_analysis_bound`; `Komorebi.SufficientResolution.CalibrationFrame.Frame.exact_calibration_identifies`.

**Hypotheses.** Fixed split calibration frame; real Hilbert G,V; fixed bounded true A and tau$\ge$`<!-- -->`{=html}0; fixed identifiable p; whole calibration truth/model fit and true data allowances; generalized acceptance; relative feasibility for choice.

**Theorem 70** (SR-62: Calibrated recovery and conditional selected sources).

*For recovery assume $G,V$ are real Hilbert spaces, $A$ is a fixed bounded true operator, $\tau\ge0$ is fixed, and $p\in(\ker A)^\perp$ is fixed. Retain the whole calibration bounds and the true data bounds $\left\lVert Ap-v_i\right\rVert\le\eta_i$. Put $\delta_i=(\eta_{{\rm cal},i}+f_i)\left\lVert R\right\rVert$. If the true data, calibration-truth and model-fit allowances tend to zero, then $\delta_i\to0$. Generalized accepted sources using this generated allowance converge to a fixed identifiable true source $p$. For an arbitrary true source $g$, apply this with $p=P_{S_A}g$ and genuine data bounds $\left\lVert Ag-v_i\right\rVert\le\eta_i$; then the source-error norm tends to $\left\lVert P_{N_A}g\right\rVert$.*

*If additionally $\eta_i>0$, $\tau>1$ and $\delta_i\left\lVert p\right\rVert<(\tau-1)\eta_i$ pointwise, accepted sources exist and the noncomputable selected sources have the same limit.*

*Proof.* Apply SR-61 at every index to obtain the actual operator bound $\left\lVert C_i-A\right\rVert\le\delta_i$. Because the frame is fixed, its finite norm $\left\lVert R\right\rVert$ is a constant. The sum of the two vanishing calibration allowances tends to zero, so multiplying by that constant proves $\delta_i\to0$. With the genuine data-noise bounds, every premise of the accepted-source consistency theorem SR-58 is now available.

For arbitrary $g$, use $p=P_{S_A}g$. Its forward image is $Ag$, so the same data bounds hold. The strong source limit is $p$, and continuity gives $\left\lVert x_i-g\right\rVert\to\left\lVert p-g\right\rVert=\left\lVert P_{N_A}g\right\rVert$. No calibration can remove source ambiguity in the true forward kernel without an additional identifying condition.

The relative margin feeds the generated allowance into SR-59 and proves pointwise existence and norm domination. Its chosen sources are accepted, so the first conclusion applies to them. The raw selection is still noncomputable and proof-dependent. Calibration has generated the operator-error premise; it has not eliminated the distinct truth, data, feasibility or selection obligations.

In particular, declining observed model-calibration fit alone is insufficient: the calibration-truth allowance must also vanish. If the reconstruction frame changes with the index, a growing analysis norm would require additional control. The printed family theorem uses the fixed frame it actually assumes. ◻

**Formal source:** `Komorebi.SufficientResolution.CalibrationRecovery.generated_operator_bound`; `Komorebi.SufficientResolution.CalibrationRecovery.generatedDelta_tendsto_zero`; `Komorebi.SufficientResolution.CalibrationRecovery.calibrated_consistent`; `Komorebi.SufficientResolution.CalibrationRecovery.calibrated_error_norm_limit`; `Komorebi.SufficientResolution.CalibrationSelection.exists_accepted_from_calibration`; `Komorebi.SufficientResolution.CalibrationSelection.calibrated_selected_consistent`.

**Hypotheses.** Real normed spaces; bounded split stage frames; or bounded U,R with whole reconstruction defect at most rho\<1.

**Theorem 71** (SR-63: Hierarchical and approximate reconstruction frames).

*For split frames $(U_E,R_E):J\rightleftarrows K$ and $(U_F,R_F):K\rightleftarrows G$, the composite is split, with analysis $R_ER_F$ and $\left\lVert R_ER_F\right\rVert\le\left\lVert R_E\right\rVert\left\lVert R_F\right\rVert$. The corresponding calibration allowance is at most $(\eta_{\rm cal}+f)\left\lVert R_E\right\rVert\left\lVert R_F\right\rVert$.*

*More generally, if $\left\lVert I-UR\right\rVert\le\rho<1$, then $$\left\lVert T\right\rVert\le\frac{\left\lVert TU\right\rVert\left\lVert R\right\rVert}{1-\rho},\qquad
\left\lVert C-A\right\rVert\le\frac{(\eta_{\rm cal}+f)\left\lVert R\right\rVert}{1-\rho}.$$*

*Proof.* The composite synthesis is $U_FU_E$ and analysis is $R_ER_F$. Their product is $U_F(U_ER_E)R_F=U_FR_F=I_G$. Submultiplicativity bounds the composite analysis norm; applying SR-61 and that bound proves the hierarchical allowance. There is no requirement that either synthesis be square or injective.

For the approximate frame, use the exact identity $T=(TU)R+T(I-UR)$. It gives $$\left\lVert T\right\rVert\le\left\lVert TU\right\rVert\left\lVert R\right\rVert+\left\lVert T\right\rVert\,\left\lVert I-UR\right\rVert
\le\left\lVert TU\right\rVert\left\lVert R\right\rVert+\rho\left\lVert T\right\rVert .$$ Since $1-\rho>0$, absorb the final term and divide. For $T=C-A$, the measured calibration bounds give $\left\lVert TU\right\rVert\le\eta_{\rm cal}+f$, producing the operator allowance. This argument only uses norm inequalities; it does not substitute an assumed exact inverse for the approximate reconstruction.

The denominator records the loss of control. At $\rho=0$ the exact frame estimate is recovered. At $\rho=1$ the absorption step gives no bound, and it is not legitimate to reuse the formula by division. Likewise the product of hierarchical analysis norms is a valid conservative bound, not generally an equality or the optimal sensitivity of the composite. These conditioning factors belong in the certificate. ◻

**Formal source:** `Komorebi.SufficientResolution.CalibrationHierarchy.comp`; `Komorebi.SufficientResolution.CalibrationHierarchy.comp_analysis_norm_le`; `Komorebi.SufficientResolution.CalibrationHierarchy.hierarchical_operator_bound`; `Komorebi.SufficientResolution.ApproximateCalibration.approximate_factorization`; `Komorebi.SufficientResolution.ApproximateCalibration.approximate_frame_bound`; `Komorebi.SufficientResolution.ApproximateCalibration.measured_approximate_operator_bound`.

**Hypotheses.** Actual partial calibration from R to R${}^2$ with product norm; bounded unseen scalar operators; arbitrary real norm threshold.

**Theorem 72** (SR-64: A missed calibration direction permits unbounded error).

*Let $U(t)=(t,0)$ and $C_s(x,y)=sy$. Then $C_sU=0$ and $\left\lVert C_s\right\rVert=|s|$. For every real $M$ there is an operator agreeing perfectly with zero on the entire calibration subspace yet satisfying $\left\lVert C_s\right\rVert>M$. The calibration synthesis is not surjective. Thus perfect agreement on a proper source subspace does not control whole-source operator accuracy.*

*Proof.* Direct substitution gives $C_sU(t)=s\cdot0=0$. The second-coordinate projection has norm one, so scalar multiplication gives $\left\lVert C_s\right\rVert=|s|$; the vector $(0,1)$ also verifies the lower bound. Choose $s=|M|+1>0$. Then $\left\lVert C_s\right\rVert=|M|+1>M$ while its calibrated response remains zero. Taking the true operator and measured response both zero shows that both calibration residuals vanish, even though the whole operator discrepancy exceeds $M$.

The vector $(0,1)$ is outside the range of $U$, proving nonsurjectivity. A split reconstruction $UR=I_{\mathbb R^2}$ would make every source a range vector, so no such reconstruction exists here. Nor can any approximate reconstruction for this synthesis have whole defect below one: the range of $UR$ has second coordinate zero, and therefore $(I-UR)(0,1)$ has second coordinate one and norm at least one. This last observation explains the direction-coverage role of the strict absorption threshold in SR-63.

The positive redundant example and this negative partial example differ in coverage, not coordinate count. Extra coordinates can coexist with complete reconstruction of every source. Calibration of fewer source directions leaves an operator component that all tested calibration responses fail to see. The theorem makes that obstruction explicit without claiming that an externally supplied truth allowance can be inferred from those responses. ◻

**Formal source:** `Komorebi.SufficientResolution.CalibrationExamples.partial_not_surjective`; `Komorebi.SufficientResolution.CalibrationExamples.unseen_comp_partial`; `Komorebi.SufficientResolution.CalibrationExamples.unseen_norm`; `Komorebi.SufficientResolution.CalibrationExamples.arbitrarily_large_unseen_error`; `Komorebi.SufficientResolution.CalibrationExamples.perfect_partial_calibration_unbounded`.

# What the assembled calculus establishes

The results support a precise progression. Exact resolutions identify which coordinate vectors and coordinate kernels describe actual objects and operations. Split compression identifies the excursion through discarded state that prevents preservation of composition. Memory maps characterize prepared closure; finite hidden dimension turns their universal vanishing into a finite whole-map certificate. Behavioral quotients retain exactly the distinctions accessible to the declared future task. Normed defect budgets determine how approximate representations propagate their errors.

In inverse problems, compatibility, realizability, and source identifiability remain distinct. The local obstruction quotient measures compatible data that have no global source. The compatibility residual measures the inconsistent sector, with its own conditioning constant. A global source has separate kernel ambiguity and inverse sensitivity. Regularization controls an actual penalized objective. Its strong limits recover each fixed identifiable source, while uniform source convergence requires closed range. Discrepancy rules and calibrated changing models add operational acceptance contracts whose true error allowances remain visible.

The common theme is that changing a representation changes the obligations needed to use it. A certificate can discharge an obligation from concrete maps and inequalities. A residual can expose the remaining defect. An obstruction theorem can prove that an obligation is impossible under the available structure. These outcomes have different mathematical meanings.

## Exact representation and information loss

A redundant exact coordinate space need not lose any information about its object, because synthesis after analysis is identity. Coarsening a packet address family can also remain exact if the entire contents of the merged packets are retained. Information loss is supplied by a separate map and its kernel. In the behavioral setting, only the largest invariant invisible subspace can be quotiented without changing any declared future observation. In source reconstruction, the unavoidable ambiguity is the true forward operator's kernel. Neither coordinate count nor packet count alone decides sufficiency.

## Relations to established mathematics

The mathematics deliberately uses established foundations. Split idempotents, quotients, observability, block elimination, operator exponentials, orthogonal geometry, Moore--Penrose inversion, Tikhonov regularization, and discrepancy principles each contribute concrete constructions. The paper's organizing claim is that their interfaces can be written together, with exact transport, obstruction, approximation, and certificate obligations. Historical novelty of each component is a separate question. The formal inventory and finite test totals do not answer it.

## Open bridges and extensions

The following problems specify further research beyond the printed contracts.

1.  **Stable target-only recovery from behavioral minimality.** The exact quotient $X/N$ preserves all specified future observations. The Hilbert theory stably recovers an identifiable source under its reconstruction or regularization assumptions. A general theorem connecting these two constructions must identify a task target, its quotient metric, the relevant forward map, and sufficient conditioning. It should recover that target without requiring reconstruction of the full original source. No such unrestricted bridge is asserted in this edition.

2.  **Calibration truth allowances from individual samples.** The calibration theorems start from the whole-operator inequality $\left\lVert Y-AU\right\rVert\le\eta_{\rm cal}$. Deriving it from individual noisy probes requires a specified sample model, a justified aggregation bound, and control of untested directions. A measured model fit supplies neither the true operator nor that truth allowance by itself.

3.  **Verified numerical procedures.** The formalization proves the certificate contracts. The rational Python implementations compute and check records under explicit input limits. Their parsers, arithmetic helpers, row-space saturation, parameter bracketing, and stopping procedures are not formally verified. Verified extraction or an independent formal certificate importer would add a new layer of assurance.

4.  **Additional admissible categories.** Minimum linear dimension does not establish a minimum positive, stochastic, integral, geometric, or nonlinear realization. Bounded autonomous generators do not settle unbounded-domain or time-dependent flow problems. Such extensions must print the additional admissibility and domain hypotheses rather than importing them through terminology.

# Source distribution and verification boundaries

This edition contains a traditional paper, a visual guide, a Lean guide, and a complete source ZIP. The `.md` files are included in that ZIP, alongside editable `.tex`, the 93 production Lean modules, theorem guides, exact Python companions, example data, source inventories, and verification records. The original v0.16.0 archive is preserved separately for provenance. Publication sources and reconciliation records are additional files, not silent replacements of the mathematical source history.

The principal concordance uses SR-01 through SR-64 with explicit hypotheses, dependencies, exact declaration names, and hashes of the source files read for this assembly. These are consolidated theorem groups. The declaration inventory comprises 998 theorem/lemma declarations and 1159 enumerated named declarations in 93 production modules. Supporting identities, classical specializations, definitions, and checked examples contribute to these totals.

The archived v0.16.0 final verification includes two runs of the latest block's 31-module project dependency closure and audits of its 52 new named declarations. It does not record a fresh simultaneous compilation of every one of the 93 modules at that final checkpoint. The complete release verification record distinguishes archived Lean evidence, fresh compilation if any, source inspections, finite Python replay, document builds, and archive integrity. This manuscript makes no fresh Lean compilation claim merely from the existence of those archives.

The exact-rational companions cover observation saturation, discrete memory, quantitative budgets, orthogonal globalization, quotient metrics, reconstruction, positive-parameter regularization, discrepancy, inexact solves, changing operators, generalized feasibility, and calibration. Their finite checks are implementation evidence in the tested dimensions and inputs. They are not universal proofs and do not infer external truth allowances. The current release's exact run ranges and counts belong in its machine-readable verification records so that archived and fresh results cannot be conflated.

## Rebuilding the reading set

The supplied build scripts invoke pdfLaTeX three times for stable cross-references and table-of-contents entries. This rebuild creates the documents. It does not compile Lean, rerun scientific checks, infer a noise allowance, or authenticate a physical calibration experiment. Separate scripts and instructions address those activities.

The standalone Markdown manuscript preserves the same statements and proofs for readers and tools that work directly with text. The concordance CSV/JSON provides a structured route from a mathematical claim to its formal declarations. The visual guide illustrates the same contracts with exact vector figures and checked rational examples. The Lean guide explains the production modules, the formal domains, and the evidence needed to reproduce the recorded builds.

# Coverage of the sixteen development blocks

The block numbers below preserve the development history; they are not the section numbers of the reorganized paper. Each row identifies four consolidated theorem groups and the principal mathematical contract.

  Block   Stable claims   Contract
  ------- --------------- --------------------------------------------------------------------------------------------------------------------------------------
  1       SR-01--SR-04    Exact redundant representation; compression defects; actual globalization obstruction; behavioral quotient.
  2       SR-05--SR-08    Discrete hidden elimination; closure equivalence; finite feedback certificate; canonical hidden-space construction.
  3       SR-09--SR-12    Finite observation horizon; minimal image dimension; realizable observation tables; finite certificate soundness.
  4       SR-13--SR-16    Exact word-defect transport; heterogeneous budgets; two-rate response; stable initialization bounds.
  5       SR-17--SR-20    Actual bounded flows; powers-to-exponentials bridge; continuous memory; finite moment and jet certificates.
  6       SR-21--SR-24    Duhamel defect transport; flow growth envelopes; uniform stability; scalar sharpness and instability boundary.
  7       SR-25--SR-28    Unique orthogonal error split; harmonic obstruction; compatibility conditioning; finite exactness and refinement.
  8       SR-29--SR-32    Constructed canonical inverse; minimum-norm source; source sensitivity; closed-range characterization.
  9       SR-33--SR-36    Native quotient metric; minimum representatives; bounded obstruction transport; refinement and nonclosed seminorm boundary.
  10      SR-37--SR-40    Coercive Tikhonov construction; objective optimality; bias/noise/kernel accounting; perturbation and globalization.
  11      SR-41--SR-44    Normal-range density; strong source limits; noisy and inexact consistency; uniform boundary and fitted-data limits.
  12      SR-45--SR-48    Actual residual curve; noncomputable root existence; norm-controlled strong consistency; accepted rule and endpoints.
  13      SR-49--SR-52    Source/image solver scales; protected measurements; near-accepted consistency; squared certificate soundness.
  14      SR-53--SR-56    Whole-operator uncertainty; model residual transport; changing-model consistency; operational certificates.
  15      SR-57--SR-60    Candidate-dependent self-bounding; source-cap-free acceptance; feasibility-aware selection; inexact and impossible-model boundaries.
  16      SR-61--SR-64    Redundant calibration frames; generated uncertainty and recovery; hierarchical/approximate frames; unseen-direction obstruction.

# Principal dependency paths

The exact-coordinate path is SR-01 to SR-02. The hidden-memory path is SR-05 to SR-06 to SR-07, with SR-08 supplying the canonical bridge from an arbitrary split compression. The behavioral path starts at SR-04 and passes through SR-09--SR-12. Quantitative discrete transport is SR-13--SR-16. Bounded analytic flow converts the algebraic memory path through SR-17--SR-20 and provides approximate transport in SR-21--SR-24.

The globalization path begins with the actual quotient SR-03 and its projected geometry SR-25--SR-28. Its intrinsic metric is proved in SR-33--SR-36. Canonical source reconstruction SR-29--SR-32 needs the additional source-space and closed-range hypotheses. Regularization SR-37--SR-40 relaxes closed range at positive parameter. Density and norm domination in SR-41 and SR-46 provide the common strong-consistency engine for the discrepancy rules and changing-model extensions.

Calibration SR-61--SR-63 supplies operator-error allowances from its own externally justified truth bounds and conditioning. The recovery chain then uses generalized acceptance and explicit parameter feasibility. The negative control SR-64 explains why source-direction coverage is part of that contract.
