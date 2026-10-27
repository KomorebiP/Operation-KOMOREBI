#!/usr/bin/env python3
"""One content source builds both complete TeX and Markdown companions."""
from pathlib import Path
import json,re,hashlib,csv
ROOT=Path(__file__).resolve().parent
UP=ROOT.parent/'formal'
if not UP.is_dir():
    UP=ROOT.parents[2]/'work/sufficient_inventory/upstream/Komorebi_Sufficient_Resolution_Lean_v0.16.0'
SECTIONS=[]
def sec(title,block,paragraphs,equations=(),figure=None,anchors=()):
    SECTIONS.append(dict(title=title,block=block,paragraphs=list(paragraphs),equations=list(equations),figure=figure,anchors=list(anchors)))

sec('How to read a sufficient resolution',1,[
r'The governing question is operational: what must a representation retain to support a specified observation and every permitted continuation? The answer depends on the observation, the operations, the admissible models, and the metric used for error. A representation can be exact for one contract and insufficient for another.',
r'This guide follows three connected threads. Exact coordinates and hidden-return identities explain when representation commutes with evolution. Behavioral quotients identify the distinctions future observations require. Reconstruction, regularization, discrepancy, and calibration attach quantitative certificates to recovery.',
r'The worked examples use small rational systems. The accompanying generator checks 280 exact assertions with \texttt{fractions.Fraction}. Smooth plotted curves evaluate printed analytic formulas using floating point for illustration. Neither kind of drawing proves an infinite limit or validates an unknown physical operator.',
r'Source anchors identify actual modules and declarations in the frozen v0.16.0 program. The traditional paper supplies consolidated theorem statements and proofs. The Lean guide distinguishes source inspection, archived compilation, and any fresh verification recorded for the final release.'
],figure=('reading_route',r'Representation, evolution, and recovery share one language while retaining distinct proof obligations.'),anchors=[('ExactResolution','decode_encode'),('Behavioral','all_future_observations_preserved')])

sec('Exact representation begins with reconstruction',1,[
r'An analysis map records an object in coordinates; a synthesis map reconstructs it. The essential hypothesis is the split identity below. Coordinates may be redundant, and neither orthogonality nor finite dimension is required in the algebraic result. The scalar setting is a semiring with additive commutative monoids.',
r'The coordinate projector selects precisely the realizable records. Its fixed-point space is the image of analysis. A coordinate vector outside that image is a record the declared synthesis/analysis pair does not recognize as an exact representation.',
r'For two objects, encoding a genuine linear transformation and decoding its kernel returns the original transformation. Decoding and re-encoding an arbitrary coordinate kernel instead sandwiches it between the two realizability projectors. This distinction becomes important whenever the coordinates contain unused directions.'
],equations=[r'a_X:X\to V_X,\quad s_X:V_X\to X,\quad s_Xa_X=I_X,',r'E_X=a_Xs_X,\quad E_X^2=E_X,\quad E_Xv=v\iff v\in\operatorname{Ran}a_X.',r'K(T)=a_YTs_X,\qquad D(K)=s_YKa_X.',r'D(K(T))=T,\qquad K(D(K))=E_YKE_X.'],anchors=[('ExactResolution','projector_idempotent'),('ExactResolution','fixed_iff_realizable'),('ExactResolution','decode_encode'),('ExactResolution','encode_decode')])

sec('Redundancy creates a realizable coordinate space',1,[
r'Take a two-dimensional source and store three coordinates: the two entries and their sum. Synthesis reads the first two entries. These maps reconstruct every original vector, although arbitrary triples need not be realizable.',
r'The stored record $(1,1,0)$ violates its own consistency relation. The coordinate projector returns $(1,1,2)$. The plane in the figure is the set of fixed records. The projection is oblique for the ordinary Euclidean metric; the split algebraic theorem does not assert it is an orthogonal projection.',
r'Redundancy is useful when different operations or measurements have natural coordinate views. It also imposes a compatibility obligation: operations on all coordinate triples must respect the realizable plane before they can be interpreted as transformations of the original object.'
],equations=[r'a(x,y)=(x,y,x+y),\qquad s(u,v,w)=(u,v),',r'E(u,v,w)=(u,v,u+v).'],figure=('redundant_plane',r'The plane $w=u+v$ consists of realizable records. The highlighted correction uses the declared oblique projector.'),anchors=[('ExactResolution','fixed_iff_realizable'),('ExactResolution','compatible_iff_existsUnique')])

sec('Compatible kernels and packet transfer blocks',1,[
r'A coordinate kernel represents one unique source transformation exactly when it satisfies the projector sandwich identity. The compatibility theorem proves both existence and uniqueness. Its content is a correspondence between actual maps and compatible kernels, rather than a convention that every coordinate array is automatically meaningful.',
r'When coordinate spaces have finite direct-sum decompositions, a packet is one component $P_iV_X$. A transfer block $K_{ji}=Q_jKP_i$ is the action from source packet $i$ to target packet $j$. Each block is itself a map, rather than necessarily a scalar weight. The full block array reconstructs $K$. For redundant coordinates, compatibility is a condition on that assembled kernel; individual coordinate blocks need not preserve the realizable subspace by themselves.',
r'Encoded transformations compose by ordinary kernel multiplication. This follows from the split reconstruction identity in the intermediate space. Complete packet coordinates can therefore turn operator composition into transfer-block composition while retaining the original operator.',
r'For redundant coordinates, even the full coordinate identity may fail compatibility. In the three-coordinate example, $EIE=E\ne I$. The appropriate identity on realizable records is $E$. Unused coordinate directions cannot be treated as additional mathematical states merely because the coordinate container includes them.'
],equations=[r'E_YKE_X=K\iff\exists!T:\ K=a_YTs_X,',r'K(ST)=K(S)K(T).'],anchors=[('ExactResolution','compatible_iff_existsUnique'),('ExactResolution','kernelEquiv'),('ExactResolution','encode_comp')])

sec('Compression exposes a hidden-return defect',1,[
r'Compression has a different contract from complete coordinate encoding. Let $C$ retain a coarse state and let $R$ choose a lift with $CR=I$. The retained projector is $P=RC$ and the discarded projector is $Q=I-P$. The commutative-ring hypothesis permits these differences.',
r'The compressed transform $\Phi(T)=CTR$ need not preserve products. Its exact defect is the path that enters the discarded space during the first operation and returns during the second. A zero defect for one pair or one depth only settles that pair or depth.',
r'Complete coarsening that groups full packet contents remains exact. Discarding a component or substituting a statistic is an additional map, with an additional kernel. The hidden-return theorem applies to the specified compression and lift; a smaller number of addresses alone does not establish information loss.'
],equations=[r'\Delta(S,T)=\Phi(ST)-\Phi(S)\Phi(T)=CSQTR,',r'\Phi(T^{m+n})-\Phi(T^m)\Phi(T^n)=CT^mQT^nR.'],anchors=[('Compression','defect_factorization'),('Compression','power_defect'),('Compression','defect_coherence')])

sec('A return can hide beyond the tested depths',2,[
r'Our first worked system rotates three rational coordinates. The visible coordinate is $y$, while $(z_1,z_2)$ are hidden. Preparation places the visible input in $(y,0,0)$. The one-step compressed operator is zero.',
r'The first two positive depths agree with powers of that zero operator. At depth three the hidden path returns the original visible input. This is an exact counterexample to extrapolating shallow closure indefinitely. The discrepancy is an identity map, not a small numerical mismatch.',
r'The figure follows the same input around its three-step cycle. At depth zero both prepared and coarse evolutions are identities. This convention prevents the zero-power case from being silently omitted.'
],equations=[r'L(y,z_1,z_2)=(z_1,z_2,y),\quad C(y,z_1,z_2)=y,\quad R(y)=(y,0,0),',r'E_0=I,\quad E_1=0,\quad E_2=0,\quad E_3=I,\qquad A=CLR=0.'],figure=('delayed_return',r'The prepared operator returns after three full steps, although the coarse operator remains zero at every positive depth.'),anchors=[('Examples','correct_through_depth_two'),('Examples','fails_at_depth_three'),('MemoryExamples','delayed_memory_one')])

sec('Eliminating hidden dynamics produces memory',2,[
r'Write a split linear step as $T(y,z)=(Ay+Bz,Gy+Dz)$. The maps $G$ and $B$ cross the visible/hidden boundary; $D$ evolves hidden content. The source constructs the full operator and derives its trajectories, rather than assuming the recurrence as a separate conclusion.',
r'Iterating the hidden recurrence yields an initial-state term and a finite history convolution. Substitution into the visible recurrence gives an exact memory equation. Each history coefficient $M_k=BD^kG$ is a visible-to-hidden-to-visible return with $k$ internal hidden transitions.',
r'Both equations include $n=0$, where the sum is empty. The initial hidden state cannot be dropped unless preparation sets it to zero or another stated condition removes its effect. These are algebraic module identities over a commutative ring.'
],equations=[r'z_n=D^nz_0+\sum_{j=0}^{n-1}D^{n-1-j}Gy_j,',r'y_{n+1}=Ay_n+BD^nz_0+\sum_{j=0}^{n-1}M_{n-1-j}y_j,\qquad M_k=BD^kG.'],anchors=[('DiscreteMemory','hidden_elimination'),('DiscreteMemory','discrete_memory_equation'),('DiscreteMemory','forced_recurrence_formula')])

sec('A finite certificate can establish every depth',2,[
r'For prepared states, exact visible closure at every natural depth is equivalent to vanishing of every feedback moment. It is also equivalent to the prepared semigroup law. Necessity is proved by successively isolating the feedback coefficients; it does not require the entry or return maps separately to vanish.',
r'Over a field, a supplied monic annihilating polynomial for $D$ reduces the all-depth moment obligation to its first degree-many moments. If the hidden space has finite dimension $d$, Cayley--Hamilton supplies that polynomial. The visible space may remain infinite-dimensional.',
r'The certificate tests equality of whole linear maps. A finite list of sampled states does not satisfy that hypothesis without an independently justified spanning or whole-map argument. The zero-dimensional hidden case is included.'
],equations=[r'\bigl[\forall n,\ E_n=A^n\bigr]\iff\bigl[\forall k,\ BD^kG=0\bigr],',r'\dim H=d\ \Longrightarrow\ \bigl[\forall n,\ E_n=A^n\bigr]\iff\bigl[M_0=\cdots=M_{d-1}=0\bigr],',r'\bigl[\forall n,\ E_n=A^n\bigr]\iff\bigl[E_n=A^n\text{ for }0\le n\le d+1\bigr].'],figure=('moment_delay',r'A return moment indexed by $k$ first contributes at full depth $k+2$. In the worked system $d=2$ and $M_1=I$.'),anchors=[('MemoryClosure','prepared_powers_iff_memory_zero'),('FiniteMemory','prepared_powers_iff_finite_horizon'),('MemoryClosure','first_return_discrepancy')])

sec('Prepared closure and all-state closure differ',2,[
r'Prepared closure describes trajectories whose hidden initial state is zero. All-state closure describes every initial hidden state. The latter holds exactly when the return map $B$ vanishes. Prepared closure only requires every composite $BD^kG$ to vanish.',
r'For example, take $A=I$, $D=I$, $B(z_1,z_2)=z_1$, and $G(y)=(0,y)$. Both boundary maps are nonzero, but their active directions are disconnected: visible inputs enter $z_2$, while $B$ reads only $z_1$. Every prepared feedback moment vanishes. An initial $z_1\ne0$ immediately affects the visible trajectory.',
r'An arbitrary split compression has a canonical hidden space $\ker C$. Its decomposition $x\mapsto(Cx,Qx)$ and reconstruction $(y,z)\mapsto Ry+z$ are actual inverse maps. The corresponding block system is conjugate to the fine dynamics, so these memory criteria apply using the actual discarded dimension.'
],equations=[r'\bigl[\forall n,y_0,z_0,\ y_n=A^ny_0\bigr]\iff B=0,',r'x\longmapsto(Cx,Qx),\qquad(y,z)\longmapsto Ry+z.'],anchors=[('MemoryClosure','all_state_closure_iff_B_zero'),('SplitMemory','block_synthesis_analysis'),('SplitMemory','exact_powers_iff_canonical_finite_horizon')])

sec('Sufficiency depends on every permitted future',1,[
r'Choose an observation $O$ and allowed operations $T_i$. A state difference is behaviorally invisible when no finite permitted word can reveal it. The empty word includes the present observation. Chronological words apply the listed first operation first, so their operator products run in reverse written order.',
r'The invisible submodule is invariant under every allowed operation and is the largest invariant submodule contained in $\ker O$. Consequently, the quotient carries actual induced operations and an actual observation. It preserves every original future observation.',
r'Changing the observation or enlarging the operation alphabet can shrink the invisible submodule and require a larger state representation. The theorem assumes the operators are specified. It does not infer them from finite training data or identify every nonlinear encoding.'
],equations=[r'N=\bigcap_w\ker(OT_w),\qquad T_{i::w}=T_wT_i,',r'[x]=[y]\text{ in }X/N\iff OT_wx=OT_wy\text{ for every finite }w.'],anchors=[('Behavioral','invisible_invariant'),('Behavioral','invariant_submodule_le_invisible'),('Behavioral','quotient_eq_iff_same_future')])

sec('A finite observation horizon can be complete',3,[
r'For finite-dimensional $X$ over a field, let $N_r$ retain the differences invisible through word length $r$. These nested subspaces satisfy the recursion below. A single plateau forces invariance and certifies the all-future invisible space.',
r'The a priori horizon is $k=\dim\ker O$, including $k=0$. Distinct behavioral states therefore have a distinguishing word of length at most $k$. The operations need not commute. An infinite alphabet is allowed in the theorem, although its word family is not then a finite enumeration.',
r'With a finite alphabet, the complete observation table has coordinates $OT_wx$ for words up to that horizon. Its state space is the realizable range of the table map, rather than the product of every arbitrary table. The source constructs dynamics on this range that reproduce observations at every later depth.'
],equations=[r'N_0=\ker O,\quad N_{r+1}=\ker O\cap\bigcap_iT_i^{-1}N_r,',r'N_{r+1}=N_r\Longrightarrow N_r=N,\qquad N_k=N,\quad k=\dim\ker O.',r'H_kx=(OT_wx)_{|w|\le k},\qquad X/N\cong\operatorname{Ran}H_k.'],anchors=[('FiniteHorizon','visibleKernel_stabilizes'),('FiniteHorizon','same_future_iff_bounded'),('FiniteObservableModel','coordinate_all_future_fidelity')])

sec('Minimality concerns the actual model image',3,[
r'An exact linear competitor $q:X\to Z$ must intertwine the specified operations and factor the observation. Its kernel is contained in $N$: it cannot erase a difference that some permitted future reveals. The induced comparison from $\operatorname{Ran}q$ to $X/N$ is surjective.',
r'This yields a minimum dimension among exact linear models of all original states and all specified continuations. Unused coordinates in $Z$ do not count as necessary state. The final comparison with $\dim Z$ requires finite-dimensional $Z$; the model-image theorem does not assume $q$ is onto $Z$.',
r'Minimum dimension is attained exactly when $\ker q=N$. In that case the source constructs an actual linear equivalence from the model image to the behavioral quotient. This is a precise model class, not an unrestricted minimum over nonlinear encodings, positive realizations, or probabilistic states.'
],equations=[r'qT_i=U_iq,\qquad Vq=O,',r'\dim(X/N)\le\dim(\operatorname{Ran}q)\le\dim Z,',r'\dim(\operatorname{Ran}q)=\dim(X/N)\iff\ker q=N.'],anchors=[('BehavioralMinimality','finrank_state_le_image'),('BehavioralMinimality','image_dimension_minimal_iff'),('BehavioralMinimality','minimalImageEquiv')])

sec('A certificate can identify the minimal quotient',3,[
r'A finite certificate combines three kinds of information. The model coordinates are generated by finitely many original observations, the operations intertwine, and the readout factors. Generation prevents the model from retaining a distinction invisible to every original observation. Intertwining and readout prevent it from discarding any future-visible distinction.',
r'Together these identities establish $\ker q=N$. This kernel result does not require finite-dimensional $X$ or a predeclared lower bound on the certificate depth. A certificate found early already establishes minimality.',
r'The worked noncommuting system observes $x$ now and $y$ after operation $A$. The hidden coordinate $h$ remains irrelevant under every word. The two-coordinate model is exact and has the smallest dimension, while the current scalar observation alone is insufficient. The rational implementation checks certificates; it is not itself formally verified or extracted from Lean.'
],equations=[r'q=GH_r,\qquad qT_i=U_iq,\qquad Vq=O\quad\Longrightarrow\quad\ker q=N.',r'T_A(x,y,h)=(y,0,h),\quad T_B(x,y,h)=(0,x,h),\quad O(x,y,h)=x.'],figure=('behavioral_model',r'Two depth-one observation coordinates determine the exact minimal behavioral model; the operations remain noncommuting.'),anchors=[('FiniteCertificate','certificate_kernel_eq'),('ObservableExamples','exactCertificate'),('ObservableExamples','operations_do_not_commute')])

sec('Approximate intertwining has an exact error identity',4,[
r'For a candidate representation $q$, define the one-step defect $\delta_i=qT_i-U_iq$ and the word defect $E_w=qT_w-U_wq$. Their transport law is exact before any norm estimate is applied. Each injected one-step defect is propagated by the preceding true operations and subsequent model operations.',
r'Whole-map norms then give a computable envelope when valid operator bounds are available. Readout error has a separate term. Its omission would confuse state-representation fidelity with accuracy of the actual requested output.',
r'The algebraic identity uses commutative-ring modules. The analytic estimates use continuous linear maps over a nontrivially normed field. Finite dimension, completeness, a finite alphabet, and surjectivity of $q$ are not assumed. Sampling finitely many states alone cannot justify the whole-map defect allowance.'
],equations=[r'E_{i::w}=E_wT_i+U_w\delta_i,\qquad E_{u++v}=E_vT_u+U_vE_u,',r'\|OT_w-VU_wq\|\le\eta A_w+\|V\|D_w,\quad\eta\ge\|O-Vq\|.'],anchors=[('ApproximateAlgebra','wordDefect_cons'),('ApproximateAlgebra','wordDefect_eq_sum'),('ApproximateBounds','norm_outputError_le')])

sec('Stability controls the accumulation of defects',4,[
r'With uniform bounds $\|T_i\|\le a$, $\|U_i\|\le b$, and $\|\delta_i\|\le\varepsilon$, the two-rate response below bounds every word of length $n$. Equal rates use the denominator-free sum and do not divide by zero.',
r'If the true operations are nonexpansive and the reduced operations contract with $0\le b<1$, the word defect is uniformly bounded by $\varepsilon/(1-b)$. If both sides are merely nonexpansive, the general estimate is $n\varepsilon$. A common operator-norm bound is essential; individual spectral-radius estimates do not supply it.',
r'The scalar examples in the figure attain the exact response. A small one-step defect with $T=1+\varepsilon$ can grow without bound. This violates the true nonexpansive hypothesis and establishes the boundary of the stable result.'
],equations=[r'H_n(a,b)=\sum_{j=0}^{n-1}a^jb^{n-1-j},\qquad\|E_w\|\le\varepsilon H_n(a,b),',r'(a-b)H_n=a^n-b^n,\qquad H_n(a,a)=na^{n-1}\quad(n\ge1).'],figure=('discrete_stability',r'Exact rational samples contrast a stable scalar pair with an expanding true operator. The displayed curves do not infer stability from data.'),anchors=[('ScalarBudgets','response_mul_sub'),('StableApproximation','norm_wordError_contractive'),('ApproximateExamples','unstable_error_unbounded')])

sec('Representation chains retain both errors and conditioning',4,[
r'Composing two approximate representations propagates both defects. The first is multiplied by the second representation map; the second is multiplied by the first representation map. The corresponding readout mismatch decomposes in the same way.',
r'A split re-encoding $S:Z\to W$, $J:W\to Z$ with $JS=I$ changes coordinate norms and may enlarge operator bounds by $\|S\|\|J\|$. Nevertheless, the actual represented output remains unchanged. A poorly conditioned coordinate choice can worsen a norm certificate without changing the mathematical output.',
r'For arbitrary initialization $z$, the coarse-state mismatch has its own propagated factor. In a contractive model its influence decays geometrically. This term is separate from the defect generated by the dynamics and the mismatch of readout maps.'
],equations=[r'E_w(pq;T,S)=pE_w(q;T,U)+E_w(p;U,S)q,',r'\|E_w(pq)\|\le\|p\|\varepsilon_1+\varepsilon_2\|q\|,',r'\|qT_wx-U_wz\|\le D_w\|x\|+B_w\|qx-z\|.'],anchors=[('ApproximateComposition','wordError_two_stage'),('ApproximateComposition','reencode_outputError'),('ApproximateBounds','norm_state_error_le')])

sec('Continuous hidden elimination gives an actual memory equation',5,[
r'For bounded real generators on Banach spaces, the flow is the actual operator exponential. The block generator $L(y,z)=(Ay+Bz,Gy+Dz)$ yields differentiated visible and hidden trajectories. Variation of constants eliminates the hidden state.',
r'The resulting memory kernel is $M(t)=Be^{tD}G$. The source proves the continuity and interval integrability needed for these formulas. Oriented intervals permit every real time in the identities, although later positive-time norm estimates restrict to $t\ge0$.',
r'The theorem applies to trajectories constructed from the full bounded generator. It does not construct a hidden trajectory from every arbitrary proposed Volterra solution, and it does not extend to unbounded generators with domain obligations.'
],equations=[r'z(t)=e^{tD}z_0+\int_0^te^{(t-s)D}Gy(s)\,ds,',r'y\prime(t)=Ay(t)+Be^{tD}z_0+\int_0^tM(t-s)y(s)\,ds.'],anchors=[('VariationOfConstants','variation_of_constants'),('ContinuousMemory','hidden_elimination'),('ContinuousMemory','continuous_memory_equation')])

sec('Jets link finite algebra to all-time closure',5,[
r'The analytic bridge identifies mapped exponential equality for every real time with equality of all generator powers. Its forward direction uses actual derivatives; its reverse direction transports the norm-convergent exponential series through bounded maps.',
r'For a hidden space of dimension $d$, all-time prepared closure is equivalent to the first $d$ return moments vanishing. It is also equivalent to the prepared derivatives matching $A^n$ through order $d+1$. These test entire operators, rather than a finite selection of times or sampled trajectories.',
r'In the delayed example, $D^2=0$ and $M(t)=tI$. The first return appears in the third derivative. Its Taylor coefficient is $I/3!$. Derivatives and Taylor coefficients therefore carry different factorial conventions.'
],equations=[r'Ce^{tL}R=e^{tA}\text{ for all }t\iff BD^kG=0\text{ for }0\le k<d,',r'E^{(n)}(0)=CL^nR,\qquad M^{(n)}(0)=BD^nG,',r'M(t)=tI,\qquad E^{(3)}(0)-A^3=I.'],anchors=[('ExponentialTransfer','mapped_flow_eq_iff_powers_eq'),('ContinuousClosure','prepared_exact_iff_finite_memory'),('ContinuousJets','first_return_derivative')])

sec('Continuous defects obey a transport integral',6,[
r'For a representation $q$ and bounded generators $L,A$, the generator defect is $\delta=qL-Aq$. The flow defect $E(t)$ is its exact Duhamel transport integral. Vanishing generator defect is equivalent to vanishing flow defect at every real time.',
r'Assumed flow envelopes turn that identity into a whole-operator estimate. With a bounded true flow and a reduced flow decaying at rate $r>0$, the response is uniformly bounded by $1/r$. Readout and initialization errors retain their own factors.',
r'The plots evaluate scalar formulas. Their role is to show why growth assumptions matter. A small generator defect alone permits $e^{\varepsilon t}-1$ growth. Neither eigenvalues alone nor a short sampled trajectory supply the common flow envelopes used by the theorem.'
],equations=[r'E(t)=qe^{tL}-e^{tA}q=\int_0^te^{(t-s)A}\delta e^{sL}\,ds,',r'\|E(t)\|\le M_LM_A\varepsilon R(a,b,t),\quad R(a,b,t)=\int_0^te^{b(t-s)}e^{as}\,ds,',r'R(0,-r,t)=\frac{1-e^{-rt}}r\le\frac1r\quad(t\ge0).'],figure=('continuous_stability',r'Analytic scalar formulas illustrate growing and stable regimes; floating-point plotting provides no additional proof of their limits.'),anchors=[('ContinuousDefect','duhamel'),('ContinuousApproximation','norm_evolution_le_response'),('ContinuousStability','norm_evolution_uniform'),('ContinuousApproxExamples','scalar_response_sharp')])

sec('Compatibility and realizability have different kernels',1,[
r'A linear presentation has a realization map $A:G\to V$ and a compatibility map $d:V\to W$, with $dA=0$. Thus every realization is compatible. The reverse implication is an additional exactness condition.',
r'The obstruction is an actual quotient of the compatible space by the realized subspace. A compatible record has zero class precisely when an original global source realizes it. The theorem constructs the quotient class and proves this equivalence; it does not declare every quotient zero.',
r'A presentation map needs commuting realization and compatibility squares. It induces a map on obstruction spaces. Forward preservation of a zero obstruction follows. Reflection requires injectivity of the induced obstruction map, and cannot be inferred from forward transport alone.'
],equations=[r'R=\operatorname{Ran}A\subseteq K=\ker d,\qquad\mathcal H=K/R,',r'[v]=0\text{ in }\mathcal H\iff v\in\operatorname{Ran}A\quad(v\in K).'],anchors=[('Globalization','obstructionClass_zero_iff'),('Globalization','all_obstructions_zero_iff_exact'),('ObstructionTransport','reflects_zero_obstruction')])

sec('The geometry separates three kinds of content',7,[
r'Let $R\subseteq K$ admit orthogonal projections in a real inner-product space. The three components below are pairwise orthogonal: realizable content, compatible obstruction, and inconsistency. Closed subspaces of a Hilbert space and finite-dimensional subspaces provide the standard projection hypotheses.',
r'For our rational example, $A(g_1,g_2)=(g_1+g_2,0,0)$ and $d(x,y,z)=2z$. The realized space is the $x$ axis, compatibility is the $xy$ plane, and the remaining axis measures inconsistency.',
r'The datum $(3,4,5)$ has obstruction energy $16$ and inconsistency energy $25$. Its nearest realizable image is $(3,0,0)$, with squared error $41$. A zero compatibility residual would remove the last term only. It would not force the compatible obstruction to vanish.'
],equations=[r'r=P_Rv,\qquad o=(P_K-P_R)v,\qquad i=(I-P_K)v,',r'v=r+o+i,\qquad\operatorname{dist}(v,R)^2=\|o\|^2+\|i\|^2.'],figure=('global_geometry',r'The three orthogonal contributions for $v=(3,4,5)$ preserve the exact error split $41=16+25$.'),anchors=[('OrthogonalResolution','components_sum'),('OrthogonalResolution','infDist_sq_decomposition'),('HilbertGlobalization','obstructionEquivHarmonic')])

sec('Residual size needs a conditioning constant',7,[
r'A compatibility residual measures inconsistency after the compatibility operator acts. To convert it into geometric distance, one needs a positive off-kernel coercivity constant for that operator. The obstruction term remains separate.',
r'In the worked presentation $d(x,y,z)=2z$, the constant $\sigma=2$ gives equality in the conditioned squared-distance estimate. Finite dimension guarantees existence of some positive constant, but does not compute an optimal singular value or a family-wide lower bound.',
r'The scalar family $d_s(x)=sx$ with $s>0$ can have an arbitrarily small residual at a unit-distance point. The needed inverse sensitivity grows as $1/s$. Therefore a residual-only certificate cannot be uniform across changing poorly conditioned presentations. Source conditioning of $A$ is a different obligation.'
],equations=[r'\sigma\|x\|\le\|dx\|\quad(x\in K^\perp),\quad\sigma>0,',r'\operatorname{dist}(v,R)^2\le\|o(v)\|^2+\left(\frac{\|dv\|}{\sigma}\right)^2,',r'41=16+\frac{100}{4}.'],anchors=[('HilbertConditioning','conditioned_distance_sq'),('HilbertConditioning','exists_coercivity_finite'),('GlobalizationExamples','no_uniform_conditioning_over_scalar_family')])

sec('Enlarging realizations transfers obstruction energy',7,[
r'Hold the compatibility space and ambient metric fixed while enlarging $R_0\subseteq R_1\subseteq K$. The newly realizable component is the difference of the two orthogonal projections. The squared reduction in distance is exactly its energy.',
r'In the worked example, enlarging the realized space from the $x$ axis to the entire compatible plane makes $(0,4,0)$ realizable. The obstruction energy $16$ disappears, while the inconsistency energy $25$ remains. The improvement has a precise source.',
r'The later quotient refinement map is a surjective contraction from $K/R_0$ to $K/R_1$. Its norm loss is exactly the newly realizable energy of the original minimum representative. This is a theorem for a fixed metric and compatibility space; an arbitrary change of packetization, tests, or metric has its own obligations.'
],equations=[r'\operatorname{gain}(v)=(P_{R_1}-P_{R_0})v,',r'\operatorname{dist}(v,R_0)^2=\operatorname{dist}(v,R_1)^2+\|\operatorname{gain}(v)\|^2.'],figure=('refinement_energy',r'Enlargement converts obstruction into realizable content without altering the inconsistency term.'),anchors=[('GlobalizationRefinement','distance_refinement_sq'),('MetricRefinement','refinementMap_norm_le'),('MetricRefinement','quotient_refinement_energy')])

sec('The best image can have many source preimages',8,[
r'For a bounded real map between Hilbert spaces with actual closed range, restriction of $A$ to $\ker(A)^\perp$ is bijective onto its range. A continuous inverse and the range projection construct the Moore--Penrose recovery operator $B$. Its existence is proved from the stated range hypothesis.',
r'The selected source is the unique minimum-norm least-squares source. Every other least-squares source differs by a kernel vector. These distinctions concern the global source, whereas the earlier best-image theorem concerned only the realized datum.',
r'For $A(g_1,g_2)=(g_1+g_2,0,0)$ and $v=(3,4,5)$, the selected source is $(3/2,3/2)$ with squared norm $9/2$. The source $(3,0)$ has the same best image and squared norm $9$. Its extra energy lies in the true kernel.'
],equations=[r'AB=P_{\operatorname{Ran}A},\qquad BA=P_{\ker(A)^\perp},',r'g\text{ is least squares}\iff g=Bv+k\text{ for some }k\in\ker A,',r'\|Bv+k\|^2=\|Bv\|^2+\|k\|^2.'],figure=('minimum_source',r'The affine family of best sources intersects the identifiable direction at the unique minimum-norm source.'),anchors=[('MinimumNormReconstruction','image_comp_recover'),('MinimumNormOptimality','all_least_squares_sources'),('MinimumNormOptimality','minimum_norm_unique')])

sec('Source ambiguity survives exact and noisy recovery',8,[
r'Even exact data $Ag$ recover only the identifiable part of $g$. Its kernel component is invisible to the forward map. Noise propagation and source ambiguity appear as orthogonal terms in the exact source-error identity.',
r'A positive source-conditioning constant $\alpha$ bounds $A$ below on $\ker(A)^\perp$, giving an inverse norm at most $1/\alpha$. This constant belongs to $A$. Compatibility conditioning $\sigma$ controls a different map and cannot supply it.',
r'An arbitrary computed candidate needs both a fit tolerance and a kernel-leakage tolerance to certify proximity to $Bv$. A small fit residual alone permits a large added kernel vector. For Hilbert spaces, closed range is equivalent to positive off-kernel coercivity and to existence of bounded recovery of the identifiable source.'
],equations=[r'g-B(Ag)=P_{\ker A}g,',r'\|B(Ag+e)-g\|^2=\|Be\|^2+\|P_{\ker A}g\|^2,',r'\|\widetilde g-Bv\|^2\le\left(\frac{\|A\widetilde g-P_Rv\|}{\alpha}\right)^2+\|P_{\ker A}\widetilde g\|^2.'],anchors=[('MinimumNormOptimality','noisy_source_error_sq'),('SourceConditioning','candidate_source_bound_sq'),('ClosedRangeReconstruction','closed_range_iff_coercivity')])

sec('The obstruction has its native quotient metric',9,[
r'The obstruction quotient uses Mathlib\textquotesingle s standard quotient seminorm. Under the projection hypotheses, the existing linear equivalence to $K\cap R^\perp$ is proved isometric. The harmonic vector is the unique compatible representative of minimum norm.',
r'Metrics must travel with coordinate changes. With compatible basis $b_1=(1,0,0)$ and $b_2=(1,2,0)$, the Gram matrix below encodes the ambient inner product. The harmonic representative $(0,4,0)$ has basis coefficients $(-2,2)$ and squared Gram norm $16$. After quotienting out $b_1$, treating the remaining quotient coordinate $2$ as unit length would instead give the incorrect value $4$.',
r'Without closedness, zero quotient seminorm detects membership in the closure of the realized subspace, whereas zero quotient class detects actual membership. A nonclosed quotient can therefore contain a nonzero class of zero seminorm. The guide keeps these statements distinct.'
],equations=[r'\Gamma=\begin{pmatrix}1&1\\1&5\end{pmatrix},\qquad(-2,2)\Gamma(-2,2)^\mathsf T=16,',r'\|[v]\|=\operatorname{dist}(v,R)\quad(v\in K),',r'\|[v]\|=0\iff v\in\overline R,\qquad[v]=0\iff v\in R.'],figure=('gram_metric',r'The native quotient metric retains the actual Gram geometry; a unit-coordinate shortcut changes the answer.'),anchors=[('MetricObstruction','obstructionIsometry'),('MetricRepresentatives','unique_minimum_representative'),('QuotientMetricBoundaries','zero_norm_iff_closure')])

sec('Intrinsic classes also handle inconsistent data',9,[
r'An arbitrary datum first projects to compatibility and then acquires an actual obstruction class. This produces a bounded map $c(v)=[P_Kv]$ with norm at most one. Its harmonic representative is the existing obstruction component.',
r'The distance split is intrinsic: quotient-class norm plus inconsistency norm. Zero projected obstruction by itself does not establish realizability. The compatibility residual must vanish as well.',
r'A bounded presentation map induces the same algebraic obstruction map as a continuous linear map, with a corresponding norm bound. A reverse presentation map whose quotient composite is the identity supplies a reverse estimate. That map and its identity are explicit hypotheses, rather than consequences of a forward bound.'
],equations=[r'c(v)=[P_Kv],\qquad\operatorname{dist}(v,R)^2=\|c(v)\|^2+\|i(v)\|^2,',r'v\in R\iff c(v)=0\text{ and }dv=0,',r'\|\overline fz\|\le C\|z\|,\qquad\|z\|\le M\|\overline fz\|\text{ when }\overline g\,\overline f=I.'],anchors=[('IntrinsicGlobalization','intrinsic_distance_sq'),('IntrinsicGlobalization','realizable_iff_class_and_residual_zero'),('MetricObstructionTransport','two_sided_bound')])

sec('Positive regularization constructs a unique source',10,[
r'For a bounded real operator between complete inner-product spaces and $\lambda>0$, the normal operator is coercive. Lax--Milgram constructs its continuous inverse. The resulting Tikhonov source is an actual map, not a variable assumed to satisfy the desired minimum.',
r'The objective increment formula proves uniqueness of the global minimizer and its equivalence with the normal equation. Neither closed range nor finite dimension is needed. Positive $\lambda$ is indispensable; the zero-parameter objective can have many minimizers.',
r'In the worked reconstruction chain, the regularized source is $(3/(2+\lambda),3/(2+\lambda))$. At $\lambda=1$ it becomes $(1,1)$. Its fitting error is $42=16+25+1$ and its objective is $44$. The extra unit is deliberate image bias, alongside the unchanged obstruction and inconsistency.'
],equations=[r'N_\lambda=A^*A+\lambda I,\qquad B_\lambda=N_\lambda^{-1}A^*,',r'F_\lambda(v,x)=\|Ax-v\|^2+\lambda\|x\|^2,',r'F_\lambda(v,x)=F_\lambda(v,x_\lambda)+\|A(x-x_\lambda)\|^2+\lambda\|x-x_\lambda\|^2.'],figure=('regularization_bias',r'Positive regularization trades source size against additional fitting bias; the irreducible geometric errors remain.'),anchors=[('TikhonovConstruction','normal_resolvent'),('TikhonovOptimality','objective_increment'),('TikhonovGlobalization','regularized_intrinsic_error')])

sec('Bias, noise, and kernel ambiguity remain separate',10,[
r'The exact noisy-error identity contains regularization bias and propagated data error. These two contributions need not be orthogonal. Their sum lies in the identifiable subspace and is orthogonal to the true source\textquotesingle s kernel component.',
r'The fixed-parameter noise norm is bounded by $1/(2\sqrt\lambda)$ and is sharp for scalar examples. The normal-residual correction of an arbitrary computed source is bounded by its residual divided by $\lambda$. These are two different scales.',
r'A source-condition rate requires an explicit representation $g=A^*Aw$. Strong convergence later removes that condition by density, but a quantitative uniform rate is not inferred for every identifiable source. Changing the operator at a fixed positive parameter has a proved perturbation estimate; it is not uniform as the parameter tends to zero.'
],equations=[r'B_\lambda(Ag+e)-g=-\lambda N_\lambda^{-1}g+B_\lambda e,',r'\|B_\lambda(Ag+e)-g\|^2=\|-\lambda N_\lambda^{-1}p+B_\lambda e\|^2+\|k\|^2,',r'p=P_{\ker(A)^\perp}g,\quad k=P_{\ker A}g,\qquad\|B_\lambda\|\le\frac1{2\sqrt\lambda}.'],anchors=[('TikhonovBias','noisy_source_error_squared'),('TikhonovBounds','regularized_opNorm_bound'),('TikhonovPerturbation','regularized_operator_difference_bound')])

sec('Strong convergence is different from uniform inversion',11,[
r'For a fixed bounded true operator, positive parameters tending to zero give strong convergence of $B_\lambda Ag$ to the identifiable part of each fixed source. The proof uses the established density of $\operatorname{Ran}(A^*A)$ in $\ker(A)^\perp$. No closed-range assumption is needed for this source-data statement.',
r'Uniform source-filter convergence holds exactly when the actual range is closed. If the range is nonclosed, the operator norm of the source-filter error equals one at every positive parameter, even while every fixed source converges strongly.',
r'The plot shows several finite diagonal modes. Each fixed mode tends to zero as $\lambda$ decreases. A finite collection has a positive smallest singular value and converges uniformly. The general nonclosed-range theorem concerns arbitrarily poorly controlled directions; this finite plot illustrates the distinction without testing that theorem.',
r'Noisy source consistency requires $\|e_i\|/\sqrt{\lambda_i}\to0$ for the stated schedule theorem. An inexact schedule additionally needs its actual normal-residual norm divided by $\lambda_i$ to vanish. Fitted data need only $e_i\to0$, and converge to the projection onto the closure of the range. Those weaker data-space hypotheses do not replace the source-space hypotheses.'
],equations=[r'B_\lambda Ag\longrightarrow P_{\ker(A)^\perp}g,',r'\operatorname{Ran}A\text{ nonclosed}\Longrightarrow\|B_\lambda A-P_{\ker(A)^\perp}\|=1\quad(\lambda>0).'],figure=('strong_uniform_modes',r'Modewise filter errors $λ/(s^2+λ)$ for a finite diagonal family. The plot is illustrative, while the nonclosed-range statement is a separate Lean theorem.'),anchors=[('TikhonovConvergence','tendsto_source'),('UniformRegularization','nonclosed_sourceError_norm'),('RegularizedDataLimit','fitted_data_tendsto'),('NoisyRegularization','noisy_inexact_solver_tendsto')])

sec('Discrepancy selection uses the observed fitting curve',12,[
r'The actual residual curve $r_v(\lambda)=\|AB_\lambda v-v\|$ is continuous on positive intervals and monotone. It is strictly increasing when $A^*v\ne0$; orthogonal data instead give a constant curve.',
r'A unique positive parameter hits a target strictly between the distance to the actual range and $\|v\|$. The source proves bracketing, uses the intermediate value theorem, and records a noncomputable exact real root. This is distinct from the rational companion\textquotesingle s bounded numerical search.',
r'Given a valid positive noise allowance and $\tau>1$, the small-data branch returns zero when $\|v\|\le\tau\eta$. Otherwise the selector targets $\tau\eta$. A residual band may allow approximate targeting, but the source must still be the actual Tikhonov solution at the chosen parameter.'
],equations=[r'\operatorname{dist}(v,\operatorname{Ran}A)<\rho<\|v\|\Longrightarrow\exists!\lambda>0:\ r_v(\lambda)=\rho,',r'A=I,\quad v=4:\qquad r_v(\lambda)=\frac{4\lambda}{1+\lambda}.'],figure=('discrepancy_curve',r'For $η=1$ and $τ=3$, $λ=1$ gives source $2$ and fitting residual $2$ within the accepted band.'),anchors=[('DiscrepancySelection','exists_unique_parameter_of_distance'),('DiscrepancyRule','selectedSource_accepted'),('DiscrepancyBoundaries','identity_parameter_formula')])

sec('Accepted discrepancy gives a direct consistency route',12,[
r'An accepted exact output has no larger norm than the identifiable true source and has a true-data residual bounded by $(\tau+1)\eta$. These two controls yield strong source consistency as a valid noise allowance tends to zero.',
r'The proof does not first assume selected parameters tend to zero or impose $\eta/\sqrt\lambda\to0$. The acceptance rule supplies a different route to convergence. This does not license arbitrary parameter choices: the actual minimizer and discrepancy conditions are essential.',
r'For an arbitrary true source, the limit is its projection off the true kernel and the error norm tends to the kernel norm. An explicit source condition $g=A^*w$ yields a squared rate. A common rate for every identifiable source, an inferred noise level, and verification of the Python search remain outside the contract.'
],equations=[r'\|x_\eta\|\le\|P_{\ker(A)^\perp}g\|,\qquad\|Ax_\eta-Ag\|\le(\tau+1)\eta,',r'\eta_i\to0\Longrightarrow x_i\to P_{\ker(A)^\perp}g,',r'\|x_i-g\|\to\|P_{\ker A}g\|.'],anchors=[('DiscrepancyConvergence','norm_control_residual_tendsto'),('DiscrepancyRule','selectedSource_consistent'),('DiscrepancyRule','accepted_error_norm_limit')])

sec('Inexact solves require two residual budgets',13,[
r'A computed source need not satisfy its normal equation. Its actual normal residual $r$ controls the source correction at scale $1/\lambda$ and the image correction at the sharper scale $1/(2\sqrt\lambda)$. A reported fitting norm may also have a justified measurement enclosure.',
r'The protected band below ensures that the exact companion satisfies the original discrepancy band. The scalar margin is nonempty exactly when $2(\omega+\xi)\le(\tau-1)\eta$. This condition concerns available margin; it does not manufacture a candidate meeting all fields.',
r'The worked source $201/100$ is genuinely different from its exact companion $2$. Its normal residual is $1/50$, its actual fitting norm is $199/100$, and the reported norm $2$ has enclosure $1/100$. The squared-certificate implementation checks actual inequalities without relying on floating square roots.'
],equations=[r'\|x-x_\lambda\|\le\frac{\|r\|}{\lambda},\qquad\|A(x-x_\lambda)\|\le\frac{\|r\|}{2\sqrt\lambda},',r'\eta+\omega+\xi\le m\le\tau\eta-\omega-\xi.'],figure=('protected_band',r'The measured band reserves both solver and measurement error. Its exact companion is therefore accepted.'),anchors=[('InexactResidual','correction_bound'),('InexactResidual','image_resolvent_bound'),('InexactDiscrepancy','measured_certificate')])

sec('Vanishing raw residuals can still certify the wrong source',13,[
r'Near acceptance supplies an actual accepted companion within source distance $\kappa$. For families with valid noise allowance $\eta_i\to0$ and correction allowance $\kappa_i\to0$, the computed sources converge strongly to the identifiable true source. Numerical kernel leakage is at most $\kappa$.',
r'The zero-operator counterexample is decisive: let $A=0$, $\lambda=s>0$, datum $v=s$, and computed source $x=1$. Both its normal-residual norm and fitting norm equal $s$ and vanish as $s\to0$. Its source error remains one. The scaled normal residual $\|r\|/\lambda=1$ exposes the failure.',
r'A squared positive certificate records positivity, nonnegative error budgets, a normal-residual envelope, a fitting enclosure, and the protected interval. Its soundness theorem supplies the near-accepted witness. An arbitrary solver output without those fields is not covered merely because its raw residual is small.'
],equations=[r'\|x\|\le\|P_{\ker(A)^\perp}g\|+\kappa,\qquad\|P_{\ker A}x\|\le\kappa,',r'A=0,\ \lambda=s,\ v=s,\ x=1:\qquad\|r\|=s,\quad\frac{\|r\|}{\lambda}=1.'],anchors=[('InexactConsistency','near_consistent'),('InexactToleranceCertificates','certificate_sound'),('InexactExamples','small_raw_residuals_do_not_force_convergence')])

sec('An uncertain operator inflates the data allowance',14,[
r'Let $A$ be the fixed true operator and $C$ the available model on the same real Hilbert spaces. A true-data allowance $\eta$, whole-operator allowance $\delta$, and source norm cap $M$ imply a model-data allowance $\eta+\delta M$. The source proves this transfer; it does not infer the allowances from a fit.',
r'Operational certificates can use $C$, observed data, allowances, and normal-residual measurements without receiving $A$. Their consistency conclusion still depends on the external true bounds. For changing models, vanishing data, operator, and source-correction allowances give convergence under the stated certificate and feasibility conditions. Agreement of model and true kernels is not required; the source ambiguity always belongs to the fixed true operator.',
r'If model error persists, a model fit can converge to the wrong source. The checked scalar example $A=1$, $C=2$, and true datum/source $1$ produces accepted model sources tending to $1/2$. It violates the vanishing operator-error hypothesis rather than contradicting the consistency theorem.'
],equations=[r'\|Ag-v\|\le\eta,\quad\|C-A\|\le\delta,\quad\|g\|\le M',r'\Longrightarrow\quad\|Cg-v\|\le\eta+\delta M.'],anchors=[('OperatorUncertainty','effective_data_noise'),('OperatorCertificates','certified_consistent'),('OperatorUncertaintyExamples','biased_model_wrong_limit'),('ChangingConsistency','projected_consistent')])

sec('Model residuals need transport to the true operator',14,[
r'A numerical solve and an imperfect forward model create different errors. For a bounded operator $D$, define its actual normal residual $r_D=(D^*D+\lambda I)x-D^*v$. The two residuals for $A$ and $C$ have an exact difference identity. Their regularization terms cancel because the same parameter and source are used.',
r'A valid whole-operator allowance $\|C-A\|\le\delta$ converts this identity into the available-operator bound below. It uses only the model fitting norm, model norm, source norm, and the justified allowance on its right-hand side.',
r'If the computed model residual is bounded by $\rho$, adding $\rho$ to that envelope bounds the true normal residual. A small model solve error cannot erase model uncertainty. The identity and its norm estimate do not require $\lambda>0$; inverse correction and regularization certificates do.',
r'This is an a posteriori transfer theorem for an actual computed source. It complements inflated-noise discrepancy selection. Its external operator allowance remains essential, and a raw fit on sampled vectors does not establish that whole-map allowance.'
],equations=[r'r_A-r_C=(A^*-C^*)(Cx-v)+A^*(A-C)x,',r'\|r_A-r_C\|\le\delta\bigl(\|Cx-v\|+(\|C\|+\delta)\|x\|\bigr).'],anchors=[('OperatorResidualTransport','normal_residual_difference'),('OperatorResidualTransport','true_normal_residual_bound')])

sec('Generalized acceptance generates its own source bound',15,[
r'The generalized discrepancy predicate replaces the external source cap by a candidate-dependent allowance. Acceptance requires either its small-data zero branch or an actual positive-parameter Tikhonov source whose model residual lies in the generalized band.',
r'A feasible comparison source $p$ obeys $\|Cp-v\|\le\eta+\delta\|p\|$. Comparing literal Tikhonov objectives proves that a candidate satisfying the lower generalized discrepancy bound has $\|x\|\le\|p\|$. Otherwise the comparison source would have no larger fitting term and a strictly smaller positive penalty.',
r'The true bounds then yield a true-operator residual estimate. With a fixed true identifiable source/operator and valid allowances tending to zero, accepted candidates converge strongly. A near-accepted computed source adds its separate source allowance. External truth of data and operator allowances remains essential.'
],equations=[r'\operatorname{candidateNoise}(\eta,\delta,x)=\eta+\delta\|x\|,',r'\eta+\delta\|x\|\le\|Cx-v\|\le\tau(\eta+\delta\|x\|),',r'\|x\|\le\|p\|,\qquad\|Ax-Ap\|\le(\tau+1)(\eta+\delta\|p\|).'],figure=('uncertainty_allowance',r'The acceptance rule uses a candidate-dependent allowance; it does not validate its own true-data or true-operator assumptions.'),anchors=[('GeneralizedDiscrepancy','regularized_norm_domination'),('GeneralizedDiscrepancy','accepted_true_residual'),('GeneralizedInexact','near_consistent')])

sec('Acceptance and parameter feasibility remain separate',15,[
r'Self-bounding acceptance does not imply an acceptable parameter exists for every available model. A sufficient pointwise condition is the relative model-accuracy inequality below, alongside $\eta>0$, $\tau>1$, and the true bounds. It lets the existing discrepancy selector find a root and proves the resulting generalized acceptance.',
r'The exact true model $A=I$ and zero available model $C=0$ provide a nonfeasibility boundary. For $p=v=1$, $\eta=1/10$, $\delta=1$, and $\tau=2$, the true allowances are valid. Every positive-parameter model source is zero and has residual one, exceeding its upper candidate allowance $1/5$.',
r'The generic selection uses a noncomputable real root and choice. A finite rational checker can search under explicit caps and verify its output; that algorithm and parser are separate implementation evidence. Recovery does not follow from merely declaring a large operator-error allowance.'
],equations=[r'\delta\|p\|<(\tau-1)\eta,',r'\delta\le\gamma\eta,\quad\gamma\|p\|<\tau-1\quad\Longrightarrow\quad\delta\|p\|<(\tau-1)\eta.',r'C=0:\quad x_\lambda=0,\quad\|Cx_\lambda-v\|=1>\tfrac15.'],anchors=[('GeneralizedDiscrepancySelection','exists_accepted'),('GeneralizedFeasibility','relative_accuracy_of_scaled_error'),('GeneralizedDiscrepancyExamples','zero_model_not_accepted')])

sec('Spanning calibration controls the whole operator',16,[
r'Calibration synthesis $U:K\to G$ may be redundant. A bounded analysis $R:G\to K$ with $UR=I$ ensures that the calibration directions span the source in a controlled way. Every bounded source operator factors through this frame.',
r'A measured response operator $Y$ has two different comparisons: justified calibration truth error relative to $AU$, and measured model fit relative to $CU$. Their sum controls the response difference, and the reconstruction norm converts it into whole-operator uncertainty.',
r'The calibration-truth allowance is an external justified input. The theorem converts it; it does not estimate it from individual noisy samples or a physical instrument. Exact agreement identifies the whole operator only with the frame condition. The redundant scalar example $U(u,v)=u+v$, $Rx=(x/2,x/2)$ satisfies that condition.'
],equations=[r'UR=I,\qquad T=(TU)R,',r'\|Y-AU\|\le\eta_{\rm cal},\quad\|Y-CU\|\le\operatorname{fit}',r'\Longrightarrow\quad\|C-A\|\le(\eta_{\rm cal}+\operatorname{fit})\|R\|.'],anchors=[('CalibrationFrame','factor_through_frame'),('CalibrationFrame','measured_operator_bound'),('CalibrationFrame','exact_calibration_identifies')])

sec('Approximate frames expose conditioning and unseen directions',16,[
r'An approximate reconstruction frame satisfies $\|I-UR\|\le\rho<1$. The exact decomposition of $T$ below permits the residual term to be absorbed, giving a whole-operator bound with amplification $1/(1-\rho)$. At $\rho=0$ it reduces to the split-frame estimate.',
r'The amplification is meaningful only below one. Partial calibration $U(t)=(t,0)$ on a two-dimensional source leaves the $y$ direction unseen. Operators $C_s(x,y)=sy$ agree perfectly on every calibration input while their norms are unbounded as $s$ grows.',
r'The two panels show why a good fit needs a spanning/conditioning contract. Hierarchical split frames compose with a reconstruction-norm product bound. This permits genuine multistage calibration, while retaining sensitivity from each stage.'
],equations=[r'T=(TU)R+T(I-UR),\qquad\|T\|\le\frac{\|TU\|\|R\|}{1-\rho},',r'\|C-A\|\le\frac{(\eta_{\rm cal}+\operatorname{fit})\|R\|}{1-\rho}.'],figure=('calibration_boundary',r'Nonspanning calibration leaves an uncontrolled direction. Approximate reconstruction frames carry explicit amplification.'),anchors=[('ApproximateCalibration','approximate_frame_bound'),('CalibrationExamples','perfect_partial_calibration_unbounded'),('CalibrationHierarchy','hierarchical_operator_bound')])

sec('The completed calibration-to-recovery chain',16,[
r'A fixed split frame supplies generated operator allowance $\delta_{\rm gen}=(\eta_{\rm cal}+\operatorname{fit})\|R\|$. The frame theorem proves that this allowance bounds the whole model error. Vanishing calibration truth error and measured fit make the generated allowance vanish.',
r'Accepted source-bound-free outputs using that allowance converge strongly to a fixed identifiable true source when the true-data allowance also vanishes. This consistency theorem fixes the real Hilbert spaces, the bounded true operator $A$, the source $p\in\ker(A)^\perp$, and the band constant $\tau\ge0$. A feasible selector additionally requires $\eta>0$, $\tau>1$, and the pointwise relative-accuracy margin. The parameter construction remains noncomputable; it is not a Lean-extracted numerical search.',
r'This closes the established contract from justified operator-level calibration data to certified recovery. Two significant bridges remain open: deriving the calibration-truth allowance from individual noisy samples, and connecting behavioral minimality directly to stable target-only prediction without full-source recovery. Neither bridge is supplied by a small residual alone.'
],equations=[r'\delta_{\rm gen}=(\eta_{\rm cal}+\operatorname{fit})\|R\|,',r'\delta_{\rm gen}\|p\|<(\tau-1)\eta\quad\text{for the stated feasible selection route}.'],figure=('calibration_recovery',r'The chain separates justified calibration truth, model fit, whole-operator uncertainty, acceptance, and parameter feasibility.'),anchors=[('CalibrationRecovery','generated_operator_bound'),('CalibrationRecovery','calibrated_consistent'),('CalibrationSelection','calibrated_selected_consistent')])

sec('Evidence and reusable source',16,[
r'The visual companion contains 18 original vector figures and 280 exact rational assertions about its finite worked examples. Assertion labels and figure hashes are recorded in \texttt{validation/visual\_example\_checks.json}. The complete Markdown preserves every displayed equation, figure caption, and source anchor. Editable TeX and the figure generator are included.',
r'The frozen v0.16.0 source contains 998 theorem/lemma declarations in 93 production modules. These include supporting lemmas, examples, and classical specializations. They are not 998 independent discoveries. The final Lean guide and release records specify which source closure was compiled, which evidence is inherited, and whether any fresh replay succeeded.',
r'The core contracts cover specified linear operations, bounded analytic generators, real Hilbert recovery, and justified whole-operator/noise allowances. Python parsers, elimination routines, certificate searches, and instrumentation are not formally verified by those mathematical declarations.',
r'Packets and transfer blocks provide a working language. The completed sufficient-resolution results explain when a representation supports all declared futures, how failure returns as memory or obstruction, and what quantitative evidence permits recovery. Further nonlinear, positive, integral, arithmetic, and physical realization claims require their own proofs.'
],anchors=[('FiniteCertificate','certificate_kernel_eq'),('GeneralizedDiscrepancy','accepted_consistent'),('CalibrationRecovery','calibrated_consistent')])

def mdtext(s):
    s=s.replace(r'\textquotesingle ',"'").replace(r'\textquotesingle',"'")
    s=re.sub(r'\\texttt\{([^{}]*)\}',lambda m:'`'+m.group(1).replace(r'\_','_')+'`',s)
    s=re.sub(r'\\emph\{([^{}]*)\}',r'*\1*',s)
    return s.replace('Cayley--Hamilton','Cayley–Hamilton').replace('Moore--Penrose','Moore–Penrose')

def build():
    concordance_file=ROOT.parent/'traditional/Claim_Lean_Concordance.json'
    concordance=json.loads(concordance_file.read_text())['claims']
    crosswalk=[]
    for i,s in enumerate(SECTIONS,1):
        matched=[]
        for claim in concordance:
            if any(any(a['file'].endswith('/'+mod+'.lean') and a['name'].endswith('.'+name)
                       for mod,name in s['anchors']) for a in claim['anchors']):
                matched.append(claim['claim_id'])
        s['traditional_claims']=matched
        crosswalk.append({'visual_section':i,'title':s['title'],'historical_block':s['block'],
                          'traditional_claims':';'.join(matched),
                          'relation':'exact source declaration intersection' if matched else 'illustrative control with direct raw-source anchors'})
    covered={cid for s in SECTIONS for cid in s['traditional_claims']}
    if covered!={c['claim_id'] for c in concordance}:
        raise ValueError('Traditional claim groups missing from visual crosswalk: '+str({c['claim_id'] for c in concordance}-covered))
    # Source correspondence is verified by actual declaration name, not prose mention.
    anchor_records=[]
    for i,s in enumerate(SECTIONS,1):
        for mod,name in s['anchors']:
            f=UP/'Komorebi/SufficientResolution'/f'{mod}.lean'
            if not f.exists():raise ValueError(f'Absent source module: {mod}')
            pat=rf'\b(?:theorem|lemma|def|abbrev|structure)\s+(?:[A-Za-z0-9_]+\.)*{re.escape(name)}\b'
            hits=list(re.finditer(pat,f.read_text()))
            if not hits:raise ValueError(f'Absent source declaration: {mod}.{name}')
            line=f.read_text()[:hits[0].start()].count('\n')+1
            anchor_records.append(dict(section=i,module=mod,name=name,line=line,block=s['block'],source_sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
    preamble=r'''\documentclass[11pt]{article}
\usepackage[T1]{fontenc}\usepackage{lmodern}
\usepackage[letterpaper,margin=.82in,headheight=14pt]{geometry}
\usepackage{amsmath,amssymb,mathtools,graphicx,booktabs,tabularx,array}
\usepackage{microtype,xcolor,enumitem,fancyhdr,hyperref,xurl,textcomp}
\definecolor{navy}{HTML}{183345}\definecolor{teal}{HTML}{168A89}
\hypersetup{colorlinks=true,linkcolor=navy,urlcolor=teal,pdftitle={Sufficient Resolution: Visual Guide},pdfauthor={Komorebi P.}}
\graphicspath{{figures/}}
\setlength{\parindent}{0pt}\setlength{\parskip}{.60em}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small\textsc{Sufficient Resolution}}\fancyhead[R]{\small Visual Guide}\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{.3pt}
\newcommand{\src}[1]{\par\smallskip{\footnotesize\color{navy}\textbf{Source anchors:}\ \path{#1}}\par}
\newcommand{\claimsrc}[1]{{\footnotesize\color{navy}\textbf{Traditional theorem groups:}\ #1}\par}
\newcommand{\guidefig}[2]{\begin{center}\includegraphics[width=.94\linewidth,height=2.95in,keepaspectratio]{#1.pdf}\par\smallskip{\small #2}\end{center}}
\begin{document}
\thispagestyle{empty}\vspace*{.7in}
{\color{teal}\Large\textsc{Operation Komorebi}}\par\vspace{.45in}
{\color{navy}\Huge\bfseries Sufficient\\[.18em]Resolution}\par\vspace{.3in}
{\LARGE Visual Guide}\par\vspace{.25in}
{\large Exact reduction, hidden memory,\\and certified reconstruction}\par\vspace{.7in}
\guidefig{reading_route}{The working route: represent, evolve, and recover with explicit contracts.}
\vfill{\large Komorebi P.}\par
Final companion edition\quad 6 October 2026\par
\small Based on the complete v0.16.0 source program. Full Markdown, editable TeX, vector figures, exact example checks, and declaration correspondence are included.
\clearpage\tableofcontents\clearpage
'''
    tex=[preamble]
    md=['# Sufficient Resolution: Visual Guide','', '**Exact reduction, hidden memory, and certified reconstruction**','', 'Komorebi P. · Final companion edition · 6 October 2026','', 'Based on the complete v0.16.0 source program. Full Markdown, editable TeX, vector figures, exact example checks, and declaration correspondence are included.','']
    for i,s in enumerate(SECTIONS,1):
        tex.append(r'\section{'+s['title']+r'}\label{vis:'+str(i)+'}\n')
        md.extend([f'## {i}. {s["title"]}',''])
        for para in s['paragraphs']:
            tex.append(para+'\n\n');md.extend([mdtext(para),''])
        for eq in s['equations']:
            tex.append('\\[\n'+eq+'\n\\]\n');md.extend(['$$',eq,'$$',''])
        if s['figure']:
            name,caption=s['figure'];caption=caption.replace('λ',r'\lambda').replace('η',r'\eta').replace('τ',r'\tau')
            tex.append(r'\guidefig{'+name+'}{'+caption+'}\n')
            md.extend([f'![{s["title"]}](figures/{name}.png)','',mdtext(caption),''])
        guide='THEOREM_GUIDE.md' if s['block']==1 else f'BLOCK_{s["block"]:02}_THEOREMS.md'
        anchors='; '.join(f'{m}.lean: {n}' for m,n in s['anchors'])
        if s['traditional_claims']:
            ids=', '.join(s['traditional_claims'])
            tex.append(r'\claimsrc{'+ids+'}\n')
            md.extend(['**Traditional theorem groups:** '+ids,''])
        tex.append(r'\src{'+guide+'; '+anchors+'}\n')
        md.extend(['**Source anchors:** '+guide+'; '+'; '.join(f'`{m}.lean: {n}`' for m,n in s['anchors']),''])
        if i<len(SECTIONS):tex.append('\\clearpage\n')
    tex.append('\\end{document}\n')
    # Python raw suffixes above intentionally use literal newline escapes; normalize outside math.
    texout=''.join(tex).replace('}\\n','}\n')
    (ROOT/'Sufficient_Resolution_Visual_Guide.tex').write_text(texout)
    (ROOT/'Sufficient_Resolution_Visual_Guide.md').write_text('\n'.join(md))
    (ROOT/'guide_content.json').write_text(json.dumps(SECTIONS,indent=2)+'\n')
    (ROOT/'validation/source_anchors.json').write_text(json.dumps(anchor_records,indent=2)+'\n')
    with (ROOT/'Visual_Traditional_Claim_Crosswalk.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(crosswalk[0]));writer.writeheader();writer.writerows(crosswalk)
    anchor_contract=[{'claim_id':c['claim_id'],'anchors':c['anchors']} for c in concordance]
    anchor_digest=hashlib.sha256(json.dumps(anchor_contract,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    (ROOT/'validation/claim_crosswalk.json').write_text(json.dumps({'source_concordance':'traditional/Claim_Lean_Concordance.json','source_concordance_anchor_sha256':anchor_digest,'hash_scope':'Canonical claim IDs and exact declaration anchor records; manuscript prose excluded because the crosswalk depends on declaration intersections.','traditional_groups_covered':sorted(covered),'rows':crosswalk},indent=2)+'\n')
    print(json.dumps({'sections':len(SECTIONS),'source_anchor_occurrences':len(anchor_records),'unique_source_declarations':len({(x['module'],x['name']) for x in anchor_records}),'equations':sum(len(s['equations']) for s in SECTIONS),'figure_occurrences':sum(s['figure'] is not None for s in SECTIONS)}))

if __name__=='__main__':build()
