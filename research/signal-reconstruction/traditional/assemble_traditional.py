#!/usr/bin/env python3
"""Assemble the Signal paper and a proof/source concordance. No formal execution."""
from pathlib import Path
import hashlib,json,csv,re,subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SOURCES={
 'seed':'sources/seed_calculus/Projector_Resolved_Seed_Calculus_From_Seed_to_Reconstruction.tex',
 'unknown':'sources/unknown_edge/Universal_Unknown_Edge_Recovery.tex',
 'self':'sources/self_calibration/Self_Calibrating_Polyphase_Gibbs_Reconstruction.tex',
 'gibbs':'sources/gibbs_case/Projector_Resolved_Gibbs_Case_Study.tex',
 'singularity':'sources/singularity_dictionary/Singularity_Exact_Gibbs_Circumvention.tex',
 'complex':'sources/complex_benchmark/Complex_Signal_Image_Gibbs_Benchmark.tex',
 'infinite':'sources/infinite_packet/infinite_packet_gibbs_reconstruction_spd.py',
}
parts=[];claims=[]
def section(title,text=''):
 parts.append('\\section{'+title+'}\n'+text+'\n')
def sub(title,text=''):
 parts.append('\\subsection{'+title+'}\n'+text+'\n')
def prose(text):parts.append(text+'\n')
def claim(i,title,domain,hypotheses,statement,proof,anchors=(),dependencies=(),status='proved_under_printed_hypotheses',evidence='manuscript_proof',repair=None):
 cid=f'SG-{i:02d}'; aa=[]
 for key,loc in anchors:
  p=ROOT/SOURCES[key]
  aa.append({'file':SOURCES[key],'path':SOURCES[key],'label':loc,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'kind':'inherited_source_section'})
 record={'claim_id':cid,'title':title,'domain':domain,'hypotheses':hypotheses,'hypotheses_tex':hypotheses,'document_label':cid,'status':status,'evidence':evidence,'dependencies':list(dependencies),'anchors':aa,'statement_tex':statement,'proof_tex':proof,'scope_repair':repair,'lean_status':'not_Signal_specific_Lean_certified'}
 claims.append(record)
 parts.append(r'\par{\small\textbf{Domain and hypotheses.} '+domain+'. '+hypotheses+r'}\par'+'\n'+r'\begin{theorem}['+cid+r'\quad '+title+r']\label{'+cid+'}\n'+statement+'\n'+r'\end{theorem}'+'\n'+r'\begin{proof}'+'\n'+proof+'\n'+r'\end{proof}'+'\n')
 if aa:parts.append(r'\par{\small\color{Teal}\textit{Source lineage:} '+ '; '.join(r'\textit{'+key.replace('_',' ')+r'}, '+loc.replace('_',r'\_') for key,loc in anchors)+r'.}\par'+'\n')
 if repair:parts.append(r'\par{\small\textbf{Publication correction.} '+repair+r'}\par'+'\n')

section('The reconstruction problem',r'''
A measured signal is an object seen through a declared observation map. A
reconstruction theorem therefore has two obligations: identify the object
within a stated class and synthesize it in a representation suited to that
class. These obligations differ. A Fourier series can determine a jump signal
uniquely while its finite partial sums still ring near the jump. Conversely,
a native edge representation can reproduce a known discontinuity exactly
while supplying no method to discover an unknown edge.

We treat both obligations. First we organize signals and operators by complete
packet systems. We then derive known-edge cancellation, recovery in finite
geometric dictionaries, exact off-grid Prony recovery, and self-calibration of
polyphase aliases from adjacent offsets. Quantitative conclusions retain their
rank, conditioning, separation, and branch hypotheses. The final synthesis
error is split into the smooth approximation error and the recovered edge error.

The default periodic domain is $\mathbb T=\mathbb R/(2\pi\mathbb Z)$, with
\[
 \widehat f(n)=\frac1{2\pi}\int_0^{2\pi}f(x)e^{-inx}\,dx.
\]
Signal identities inferred from Fourier coefficients are identities of
$L^1$ classes. For a piecewise-constant edge we select the right-continuous
representative. This convention fixes the values at jumps, which Fourier
integrals alone cannot determine. When an $L^1$ norm occurs it is the
unnormalized integral over a period. On the unit circle we use chord distance
$|z-w|$ and circular angular distance $d_{\mathbb T}(\tau,\sigma)$.

\subsection{What belongs to this edition}
The inherited unknown-edge and self-calibration manuscripts are consolidated
here with full proofs and corrected contracts. The Gibbs case studies explain
the operator choice. The complex signal/image experiments probe model
mismatch. The seed calculus supplies the finite packet language. The infinite
packet program supplies a separate adaptive approximation experiment.
The raw sources remain unchanged in the bundle. The claim concordance records
which source each published result develops and where a printed contract is
narrower or corrected.

Prony systems, finite-rate sampling, polyphase decomposition, Fourier Gibbs
asymptotics, sparse secant injectivity, and shifted exponential coefficients
have established histories. In particular the shifted-coefficient phase
relation used below occurs in VEXPA \cite{vexpa}. Our presentation makes those
ingredients explicit within one packet analysis, recovery, validation, and
synthesis chain. It does not assert that these ingredients were first
discovered here.
''')
section('Packets, transfer blocks, and polyphase coordinates',r'''
A packet is a component specified by a projector and its image. Complete
packets keep every distinction in the declared object space. A transfer block
records how an operation sends one packet to another. These definitions are
structural: they do not themselves promise that measurements recover the
packets. Recovery is established by the later injectivity and conditioning
contracts.
''')
claim(1,'Complete packet analysis and synthesis','Vector spaces over a field',r'Let $P_1,\ldots,P_m\in\operatorname{End}(X)$ satisfy $P_aP_b=\delta_{ab}P_a$ and $\sum_aP_a=I_X$. Set $X_a=P_aX$.',r'''
The maps
\[
 \mathcal A x=(P_ax)_a,\qquad
 \mathcal S(x_a)_a=\sum_ax_a
\]
are inverse isomorphisms between $X$ and $\bigoplus_aX_a$. In particular,
$x=\sum_aP_ax$ uniquely.
''',r'''
Completeness gives $\mathcal S\mathcal A x=x$. If $x_a\in X_a$, then
$P_ax_a=x_a$ and $P_bx_a=0$ for $b\ne a$. Thus the $b$th component of
$\mathcal A\mathcal S(x_a)_a$ is $P_b\sum_ax_a=x_b$.
Both inverse identities follow. For uniqueness, apply $P_b$ to any proposed
sum of components. This proof uses pairwise annihilation, not orthogonality;
the packet projections can be oblique.
''',[('seed','thm:object-reconstruction')])
claim(2,'Transfer algebra and packet paths','The packet space of SG-01',r'Let $S,T\in\operatorname{End}(X)$. Set $T_{ba}=P_bTP_a$, viewed as a map $X_a\to X_b$.',r'''
\[
 T=\sum_{a,b}P_bTP_a,\qquad
 (ST)_{ca}=\sum_bS_{cb}T_{ba}.
\]
The block representation is an algebra isomorphism to
$\operatorname{End}(\bigoplus_aX_a)$, with multiplication by contraction of
intermediate packets. For every integer $k\ge1$, iterating the product gives
\[
 P_{a_k}T^kP_{a_0}
 =\sum_{a_1,\ldots,a_{k-1}}
 (P_{a_k}TP_{a_{k-1}})\cdots(P_{a_1}TP_{a_0}).
\]
''',r'''
Insert $I=\sum_aP_a$ on both sides of $T$ to obtain reconstruction. Insert
that identity between $S$ and $T$ to obtain the product formula. Equivalently,
the block map is $T\mapsto\mathcal A T\mathcal S$; SG-01 shows that its
inverse is $B\mapsto\mathcal S B\mathcal A$ and that it preserves multiplication.
The path formula follows by inserting the same identity between every
successive pair of operators. These are finite sums, so no convergence
hypothesis is hidden in the insertion.
''',[('seed','thm:operator-reconstruction; thm:block-product; thm:path-power')],['SG-01'])
claim(3,'Refinement preserves represented operators','Finite complete packet systems',r'Let $(Q_\rho)$ refine $(P_a)$, with a partition of fine labels into $F_a$ and $P_a=\sum_{\rho\in F_a}Q_\rho$.',r'''
\[
 P_bTP_a=\sum_{\sigma\in F_b}\sum_{\rho\in F_a}Q_\sigma TQ_\rho.
\]
The coordinate changes $J=\mathcal A_Q\mathcal S_P$ and
$C=\mathcal A_P\mathcal S_Q$ satisfy $CJ=I$ and $JC=I$ on their packet
coordinate spaces. Refinement is exact before any child packet is discarded.
''',r'''
Expand the two finite projector sums to obtain the block formula. Apply
SG-01 twice to compute
$CJ=\mathcal A_P\mathcal S_Q\mathcal A_Q\mathcal S_P
=\mathcal A_P\mathcal S_P=I$, and similarly $JC=I$.
The identities concern the direct sums of packet images, not an unrestricted
product with duplicated arbitrary ambient components.
''',[('seed','prop:block-refinement; thm:coordinate-refinement')],['SG-01','SG-02'])
claim(4,'Pulled-back transform packets','Vector spaces with an invertible transform',r'Let $V:X\to Y$ be an isomorphism and $(E_a)$ a finite complete packet family on $Y$.',r'''
The operators $P_a=V^{-1}E_aV$ are a complete packet family on $X$.
For a unitary $V$ and orthogonal coordinate selectors $E_a$ in a Hilbert space,
\[
 \|x\|^2=\sum_a\|P_ax\|^2.
\]
''',r'''
Compute $P_aP_b=V^{-1}E_aE_bV=\delta_{ab}P_a$ and
$\sum_aP_a=V^{-1}IV=I$. In the unitary case the pulled-back projections are
orthogonal: $P_a^*=P_a$. Their images are mutually orthogonal, and SG-01
writes $x$ as their finite orthogonal sum. The Pythagorean identity gives the
energy formula. Without unitarity and orthogonality the algebraic identities
remain valid while that norm identity need not hold.
''',[('seed','thm:transform-atlas; Area II Fourier analysis')],['SG-01'])
claim(5,'Polyphase analysis and convolution kernels',r'Absolutely summable sequences on $\mathbb Z$',r'Fix an integer $N\ge1$. Let $h,x\in\ell^1(\mathbb Z)$ and $y=h*x$. Define $x_a[q]=x[Nq+a]$ and $y_b[q]=y[Nq+b]$, for $0\le a,b<N$.',r'''
Interleaving the $N$ channels recovers $x$ exactly. With
\[
 h_{ba}[k]=h[Nk+b-a],
\]
the output channels satisfy
\[
 y_b[q]=\sum_{a=0}^{N-1}\sum_{t\in\mathbb Z}h_{ba}[q-t]x_a[t].
\]
Thus convolution becomes an $N\times N$ transfer-kernel system.
''',r'''
Every integer has a unique Euclidean decomposition $Nt+a$, so the analysis
and interleaving maps are inverse. In the convolution sum for $y[Nq+b]$, split
the input index $m$ as $Nt+a$. Then the kernel index becomes
$Nq+b-m=N(q-t)+b-a$, which is precisely $h_{ba}[q-t]$.
Absolute summability permits the regrouping: the total absolute double sum
is bounded by the corresponding convolution of $|h|$ and $|x|$.
The formula also holds for finitely supported sequences directly. It is the
sequence version of SG-02, with the residue projectors selecting addresses.
''',[('seed','Area II exact polyphase analysis and synthesis')],['SG-02'],evidence='reconstructed_prose_proof')
claim(6,'The arithmetic of residual alias ambiguity','Unit-modulus exponential nodes',r'Let $z\in\mathbb C$, $|z|=1$, and suppose $u=z^N$ and $w_j=z^{r_j}$ are known, with $N\ge1$ and integer offsets $r_j$. Let $d=\gcd(N,r_1,\ldots,r_k)$.',r'''
Exactly $d$ unit-modulus nodes satisfy the same data. Hence the physical node
is unique precisely when $d=1$. If integers $c,b_1,\ldots,b_k$ obey
$Nc+\sum_jr_jb_j=d$, then
\[
 u^c\prod_jw_j^{b_j}=z^d.
\]
For $d=1$ this is an explicit exact de-aliasing formula.
''',r'''
If $z'$ gives the same data, the quotient $v=z'/z$ satisfies
$v^N=v^{r_1}=\cdots=v^{r_k}=1$. Bezout's identity gives $v^d=1$.
Conversely $d$ divides every supplied exponent, so every $d$th root of unity
has all those powers equal to one. Therefore the fiber consists exactly of
$z$ multiplied by the $d$ distinct $d$th roots of unity. Applying the Bezout
identity directly to the measured powers gives the displayed formula.
Negative integer powers are legitimate because the data are nonzero.
''',[('self','Why decimation helps and why it aliases; Offset coefficients and internal phase recovery')],['SG-05'],evidence='reconstructed_prose_proof')
prose(r'''
The offset data in SG-06 must be actual powers of the same node. In the
multi-edge problem they are obtained only after matching coefficient vectors
to common aliased nodes. A gcd computation does not bypass that matching or
undo a collision of two edges in a single decimated channel. Adjacent offsets
supply the exponent $1$, so they remove the scalar branch ambiguity once the
individual coefficient progressions have been resolved.
''')
section('Identifiability and its unavoidable boundaries')
claim(7,'Measurement and decomposition obstructions','An arbitrary measurement model and linear packet classes',r'Let $M:X\to Y$ be any map and let an edge assignment $J:X\to\mathcal J$ be specified. Separately, let $\mathcal S,\mathcal J$ be linear subspaces of a common vector space.',r'''
If $Mf_0=Mf_1$ but $J(f_0)\ne J(f_1)$, no map $R:Y\to\mathcal J$ recovers
the correct edge for both. If $\mathcal S\cap\mathcal J\ne\{0\}$, the
sum decomposition $f=s+j$ is not unique. In particular, finitely many point
samples on a periodic interval cannot recover every arbitrary interval packet.
''',r'''
A recovery map has one value at the common datum, so it cannot equal the two
different required edges. For the decomposition obstruction take nonzero
$h\in\mathcal S\cap\mathcal J$: the pairs $(s,j)$ and $(s+h,j-h)$ have the
same sum. Finally, the complement of a finite sample set contains a nonempty
open interval. A nonzero indicator supported inside that interval vanishes at
every sample point. Compare it with the zero signal to obtain the first
obstruction concretely.
''',[('unknown','The measurement obstruction; The decomposition obstruction')])
claim(8,'No uniform location stability without separation','Two-jump periodic packets of fixed known amplitudes',r'Fix a finite set $F\subset\mathbb Z$ of derivative-moment indices. For $0<\delta<\pi/4$, compare locations $(0,\delta)$ and $(\pi,\pi+\delta)$, both with amplitudes $(1,-1)$.',r'''
Their unordered location sets have permutation-matched bottleneck distance at
least $\pi-\delta$, while their measured derivative moments satisfy
\[
 |m_n-\widetilde m_n|
 =|(1-e^{-in\pi})(1-e^{-in\delta})|
 \le2|n|\delta\qquad(n\in F).
\]
There is no Lipschitz inverse for locations with one constant on all distinct
two-jump configurations, even at this fixed order and with known amplitudes.
''',r'''
Every circular distance from a point of $\{0,\delta\}$ to a point of
$\{\pi,\pi+\delta\}$ is at least $\pi-\delta$. This bounds every matching.
The moments of the first packet are $1-e^{-in\delta}$; translating by $\pi$
multiplies them by $e^{-in\pi}$. Subtraction gives the formula.
The elementary inequality $|1-e^{-it}|\le|t|$ proves the bound. Every fixed
finite norm of the measurement difference tends to zero as $\delta\to0$,
whereas the location distance stays bounded away from zero. A common finite
Lipschitz constant is therefore impossible. This argument compares two
admissible fixed-order packets; it does not require assigning location
parameters to the zero-edge signal.
''',[('unknown','A collapsing pair of jumps; Collision is the unavoidable hard boundary')],repair='The original collision argument compared an edge parameter vector with the zero packet. The published proof compares two fixed-order configurations and specifies a permutation-invariant location metric.')
section('Known edges and the source of Gibbs ringing',r'''
The simplest reconstruction problem already separates discovery from
synthesis. Suppose a singular packet is known, but its amplitude and the
smooth background are not. A high-frequency functional can identify the
amplitude exactly on a bandlimited background. The recovered singular packet
then has its own synthesis route.
''')
claim(9,'Out-of-band matched identification','Periodic integrable signals with one known edge shape',r'Let $\mathcal S_K$ be the trigonometric polynomials of degree at most $K$. Let $m\in L^1(\mathbb T)$ and a finite nonempty set $F\subset\{n:|n|>K\}$ satisfy $D_F=\sum_{n\in F}|\widehat m(n)|^2>0$.',r'''
On $X=\mathcal S_K+\operatorname{span}\{m\}$, the functional
\[
 \ell_F(g)=D_F^{-1}\sum_{n\in F}\overline{\widehat m(n)}\widehat g(n)
\]
satisfies $\ell_F(s+am)=a$. The decomposition is direct. If the measured
coefficients have errors $\eta_n$, then
\[
 |\widetilde a-a|\le D_F^{-1/2}\Bigl(\sum_{n\in F}|\eta_n|^2\Bigr)^{1/2}.
\]
''',r'''
The coefficients of $s\in\mathcal S_K$ vanish on $F$. Substituting $s+am$
into the functional leaves $aD_F/D_F=a$. If $m$ belonged to $\mathcal S_K$,
all its coefficients on $F$ would vanish, contradicting $D_F>0$; hence the
sum is direct. The amplitude error is the inner product of the coefficient
error with the known coefficient vector divided by its squared norm.
Cauchy--Schwarz gives the displayed bound. The frequencies must actually see
the edge: an all-zero identifying set makes the formula undefined.
''',[('singularity','An edge functional from out-of-band modes')])
claim(10,'The singularity-exact block operator','The model space of SG-09',r'Let $P_Jg=\ell_F(g)m$, $P_S=I-P_J$, and let $S_M$ be Fourier truncation of degree $M\ge K$.',r'''
\[
 P_J^2=P_J,\quad P_S^2=P_S,\quad P_SP_J=P_JP_S=0,
 \quad P_S+P_J=I_X,
\]
and the resolved reconstruction obeys
\[
 \mathcal R_M=S_MP_S+P_J=I_X.
\]
''',r'''
For $g=s+am$, SG-09 gives $P_Jg=am$ and $P_Sg=s$.
These coordinate formulas immediately imply idempotence and pairwise
annihilation. Since $s$ is bandlimited and $M\ge K$, $S_Ms=s$.
Thus $\mathcal R_Mg=s+am=g$. The equality is in the declared signal class;
for a selected right-continuous packet it also reproduces that representative.
This is a known-packet theorem. An unknown interval still needs the discovery
step proved later.
''',[('singularity','The singularity projector; The singularity-exact reconstruction theorem'),('gibbs','The first exact packet decomposition')],['SG-09'])
claim(11,'Resolved error for an analytic background','Periodic signals with a supplied exact edge packet',r'Let $f=s+j$ with $|\widehat s(n)|\le Ce^{-\rho|n|}$, where $C\ge0$ and $\rho>0$. Use the canonical uniformly convergent Fourier-series representative of $s$. Set $\mathcal R_Mf=S_Ms+j$.',r'''
The reconstruction error is exactly $f-\mathcal R_Mf=s-S_Ms$, and
\[
 \|f-\mathcal R_Mf\|_\infty
 \le\frac{2Ce^{-\rho(M+1)}}{1-e^{-\rho}}.
\]
The bound is uniform across the jumps of $j$.
''',r'''
Cancel $j$ from the defining identity. Absolute summability of the Fourier
coefficients gives an everywhere uniformly convergent series for $s$.
The omitted positive and negative frequencies are bounded by
$2C\sum_{n>M}e^{-\rho n}$, which is the displayed geometric series.
No limiting trigonometric approximation of $j$ occurs in this estimate.
''',[('gibbs','Analytic smooth background')])
claim(12,'The scaled interval-edge Gibbs profile',r'The interval packet $j=\mathbf1_{[-a,a)}$ on $\mathbb T$',r'Assume $0<a<\pi$, let $\lambda_M=M+1/2$, and use the right edge coordinate $x_M(z)=a-z/\lambda_M$.',r'''
Uniformly for $z$ in compact real intervals,
\[
 S_Mj(x_M(z))\longrightarrow\frac12+\frac1\pi\operatorname{Si}(z),
 \qquad \operatorname{Si}(z)=\int_0^z\frac{\sin t}{t}\,dt.
\]
The first positive maximum of the limiting profile is $1+G$, where
\[
 G=\frac{\operatorname{Si}(\pi)}\pi-\frac12
   =0.089489872236\ldots.
\]
''',r'''
Direct integration gives $\widehat j(0)=a/\pi$ and
$\widehat j(n)=\sin(na)/(\pi n)$ for $n\ne0$. The Dirichlet kernel
$D_M(t)=\sin(\lambda_Mt)/\sin(t/2)$ yields
\[
 S_Mj(x)=\frac1{2\pi}\int_{-a}^{a}D_M(x-t)\,dt,
 \qquad (S_Mj)'(x)=\frac{D_M(x+a)-D_M(x-a)}{2\pi}.
\]
At $x=a$, the coefficient formula gives
\[
 S_Mj(a)=\frac a\pi+\frac1\pi\sum_{n=1}^M\frac{\sin(2na)}n
 \longrightarrow\frac12.
\]
For completeness, the sine-series limit follows by summation by parts from
bounded partial sums of $e^{2ina}$ and by taking radial limits in
$\sum_{n\ge1}r^ne^{2ina}/n=-\log(1-re^{2ia})$; its imaginary part tends to
$(\pi-2a)/2$ for $0<2a<2\pi$.
Now differentiate the scaled function:
\[
 \frac d{dz}S_Mj(x_M(z))=
 \frac{D_M(-z/\lambda_M)-D_M(2a-z/\lambda_M)}{2\pi\lambda_M}.
\]
The first term converges uniformly on compact $z$ sets to
$\sin z/(\pi z)$, with its continuous value at zero. The second tends
uniformly to zero because $\sin(a-z/(2\lambda_M))$ stays bounded away from
zero there. Integrate from $0$ to $z$ and use the base-point limit.
The derivative of the limiting profile is $\sin z/(\pi z)$, positive on
$(0,\pi)$ and negative on $(\pi,2\pi)$, so its first positive maximum is at
$z=\pi$. Substitution gives $G$. The constant is relative to a unit jump;
scaling a packet scales its overshoot by the jump amplitude.
''',[('gibbs','The scaled Gibbs limit'),('singularity','Detailed proof of the local scaling limit')],evidence='manuscript_proof_with_classical_Fourier_series_input')
claim(13,'Positive Fourier averaging preserves range','Periodic bounded real signals',r'Let $\sigma_M=(M+1)^{-1}\sum_{k=0}^MS_k$ be the Fejer mean. Suppose $0\le j\le1$ almost everywhere.',r'''
Then $0\le\sigma_Mj\le1$ everywhere. For an interval packet, this suppresses
overshoot while retaining a continuous transition rather than an exact jump.
''',r'''
The averaging kernel is
\[
 F_M(t)=\frac1{M+1}\left|\sum_{k=0}^Me^{ikt}\right|^2\ge0,
 \qquad\frac1{2\pi}\int_0^{2\pi}F_M(t)\,dt=1.
\]
Its convolution with $j$ is therefore a weighted mean of numbers in $[0,1]$.
The resulting finite trigonometric polynomial is continuous. A nonconstant
interval indicator is discontinuous, so the mean cannot equal its selected
representative at all points or have its exact one-sided jump.
''',[('gibbs','Fejer averaging')])
section('Finite dictionaries and residualized geometric discovery',r'''
In a finite dictionary model the unknown is a coefficient vector. The smooth
background is eliminated before testing the edge dictionary. This removal is
exact only for a declared background subspace. A residualized dictionary can
lose distinctions that the original dictionary had, so its kernel is the
correct object to inspect.
''')
claim(14,'Residualized sparse injectivity','Finite real or complex Euclidean spaces',r'Let $\mathcal S\subseteq\mathbb F^m$ be a subspace, $P$ its orthogonal projector, $R=I-P$, $D\in\mathbb F^{m\times d}$, and $A=RD$. Let $s\ge0$ be an integer.',r'''
Every vector $\alpha$ with $\|\alpha\|_0\le s$ is uniquely determined by
$A\alpha$ if and only if
\[
 \ker A\cap\{h:\|h\|_0\le\min(2s,d)\}=\{0\}.
\]
Equivalently every set of at most $\min(2s,d)$ columns is independent.
With the convention $\operatorname{spark}(A)=d+1$ when all $d$ columns are
independent, the equivalent condition is
$\operatorname{spark}(A)>\min(2s,d)$.
For $s=0$ uniqueness is automatic.
''',r'''
The difference of two $s$-sparse vectors has support of size at most $2s$
and at most $d$. Thus the kernel condition implies uniqueness.
Conversely, if a nonzero kernel vector $h$ has support size at most $2s$,
partition that support into two sets of at most $s$ indices. Let $\alpha$
equal $h$ on the first set and zero elsewhere; let $\beta$ equal $-h$ on
the second set. Then $h=\alpha-\beta$, and $A\alpha=A\beta$ contradicts
uniqueness. Column dependence is exactly the existence of a nonzero kernel
vector supported on the selected columns. The spark convention then gives
the stated capped inequality, including a fully independent matrix when
$2s>d$. When $s=0$, the only admissible vector is zero and the kernel test
concerns only zero. If $y=s_0+D\alpha$ with $s_0\in\mathcal S$, then
$Ry=A\alpha$, so the same theorem applies after background elimination.
''',[('unknown','The residualized secant theorem'),('complex','Two-dimensional finite dictionary model')],repair='The uncapped inequality spark(A)>2s is replaced by the kernel-secant condition, or its capped spark equivalent. This also covers full-column-rank dictionaries with 2s greater than the number of columns.')
claim(15,'Sparse noise stability and support thresholding','The Euclidean model of SG-14',r'Assume $s\ge1$, $d\ge1$, and the injectivity condition of SG-14. Let $y=s_0+D\alpha_0+\eta$, $s_0\in\mathcal S$, $\|\alpha_0\|_0\le s$, and $\|R\eta\|_2\le\epsilon$. Let $\widehat\alpha$ be $s$-sparse with $\|A\widehat\alpha-Ry\|_2\le\epsilon$.',r'''
Define
\[
 \gamma=\min_{\substack{\|h\|_2=1\\\|h\|_0\le\min(2s,d)}}\|Ah\|_2>0.
\]
Then
\[
 \|\widehat\alpha-\alpha_0\|_2\le2\epsilon/\gamma,
 \qquad\|D(\widehat\alpha-\alpha_0)\|_2
 \le2\|D\|_2\epsilon/\gamma.
\]
If every nonzero true coefficient has magnitude greater than $4\epsilon/\gamma$,
thresholding at $2\epsilon/\gamma$ with a strict greater-than rule recovers
the true support.
''',r'''
The admissible unit vectors form a finite union of compact coordinate
spheres. The continuous function $\|Ah\|_2$ attains its minimum. A zero
minimum would contradict SG-14, hence $\gamma>0$.
For $h=\widehat\alpha-\alpha_0$, subtract the two residuals to obtain
\[
 \|Ah\|_2\le\|A\widehat\alpha-Ry\|_2+\|R\eta\|_2\le2\epsilon.
\]
Its support is admissible, so homogeneity gives
$\gamma\|h\|_2\le\|Ah\|_2$. Apply $D$ for the packet bound.
Every coordinate error is at most $2\epsilon/\gamma$. A true zero therefore
never passes the strict threshold, while a true coefficient larger than twice
that threshold remains strictly above it. For $s=0$ both vectors vanish and
no restricted constant is required.
''',[('unknown','A deterministic stability theorem')],['SG-14'])
claim(16,'Profiled one-packet discovery and its finite gap','Finite real dictionaries with positive amplitudes',r'Let $B$ have full column rank, $P$ be the orthogonal projector onto its range, $R=I-P$, and let $\mathcal Q$ be a finite mask library with $Rq\ne0$ for every $q$. Suppose $y=B\theta_*+a_*q_*$, with $a_*>0$ and $q_*\in\mathcal Q$.',r'''
For an unrestricted scalar amplitude the least-squares profile is
\[
 \widehat a(q)=\frac{\langle Rq,Ry\rangle}{\|Rq\|_2^2},
 \qquad J(q)=\|Ry-\widehat a(q)Rq\|_2^2.
\]
The true mask has $\widehat a(q_*)=a_*$ and $J(q_*)=0$.
It is the unique zero-residual positive-amplitude mask exactly when no other
residualized mask lies on its positive ray. Define the closed rays
$C_q=\{aRq:a\ge0\}$. If
\[
 \Gamma=\inf_{q\ne q_*}\operatorname{dist}(Ry,C_q)>0,
\]
with the convention $\inf\varnothing=+\infty$, then every perturbed residualized datum $Ry+e$ with $\|e\|_2<\Gamma/2$
selects $q_*$ uniquely by nearest-ray distance.
''',r'''
Differentiate the quadratic function $\|Ry-aRq\|_2^2$ with respect to $a$.
Its unique stationary point is the profile formula and is the global
minimum. At the true mask $Ry=a_*Rq_*$, giving the stated values.
A wrong mask gives an admissible zero residual precisely when
$Ry=aRq$ for some $a>0$. This is the positive-ray condition.
For the noise statement, the distance to any nonempty closed set is
1-Lipschitz by the triangle inequality. The true ray has perturbed distance
at most $\|e\|_2$, and every wrong ray has distance at least
$\Gamma-\|e\|_2>\|e\|_2$. Thus the true ray wins strictly.
A squared objective gap must be square-rooted before it is used in this
norm-distance condition. For positive constraints the optimum on a closed
ray uses $\max(0,\widehat a(q))$, rather than an unconditionally signed
amplitude.
''',[('gibbs','Profile least squares over interval packets; The finite identifiability gap'),('singularity','Noise stability of finite packet discovery')])
claim(17,'Mask error is a support geometry calculation','Finite binary masks',r'Let $q,\widetilde q\in\{0,1\}^m$ and $a,\widetilde a\in\mathbb R$.',r'''
\begin{align*}
 \|aq-\widetilde a\widetilde q\|_2^2
 &=|a-\widetilde a|^2|\operatorname{supp}q\cap\operatorname{supp}\widetilde q|\\
 &\quad+|a|^2|\operatorname{supp}q\setminus\operatorname{supp}\widetilde q|
 +|\widetilde a|^2|\operatorname{supp}\widetilde q\setminus\operatorname{supp}q|.
\end{align*}
For $a=\widetilde a=1$ the squared norm is the cardinality of the symmetric
support difference.
''',r'''
Partition the coordinates into common support, first-only support,
second-only support, and neither. The difference equals respectively
$a-\widetilde a$, $a$, $-\widetilde a$, and zero. Sum the squared values.
The same pointwise partition gives a continuous-measure formula when support
cardinalities are replaced by support measures.
''',[('gibbs','Packet perturbation identity')],evidence='reconstructed_prose_proof')
section('Exact off-grid recovery from finitely many Fourier coefficients',r'''
Let $\mathcal U_{K,L}$ consist of real periodic signals $f=s+j$, where
$s\in\mathcal S_K$ and $j$ is right-continuous, piecewise constant, mean zero,
and has at most $L$ distinct active jumps. An active jump has nonzero amplitude.
For an actual jump count $r$, write
\[
 Dj=\sum_{\ell=1}^r a_\ell\delta_{\tau_\ell},\quad
 z_\ell=e^{-i\tau_\ell},\quad\sum_\ell a_\ell=0.
\]
The sum-zero condition is required by periodicity. A single nonzero active
jump cannot occur, so the nonconstant real class starts at $r=2$. The case
$r=0$ is allowed and will be handled explicitly. The smooth-edge
representation is unique with this normalization: a piecewise-constant
trigonometric polynomial is constant, and mean zero fixes that constant.
''')
claim(18,'Differentiation isolates an exponential moment packet',r'The class $\mathcal U_{K,L}$',r'Use the Fourier convention in Section 1. Let $n>K$ and $z_\ell=e^{-i\tau_\ell}$.',r'''
\[
 Dj=\sum_\ell a_\ell\delta_{\tau_\ell},\qquad
 m_n:=2\pi in\widehat f(n)=\sum_{\ell=1}^ra_\ell z_\ell^n.
\]
For a non-bandlimited integrable background the same formula holds with
an additive defect $e_n=2\pi in\widehat s(n)$.
''',r'''
For a smooth periodic test function $\varphi$, integrate by parts over each
constant segment of $j$. Boundary terms telescope at each jump to
$a_\ell\varphi(\tau_\ell)$, which is exactly the displayed distribution.
Evaluate the distribution on $e^{-inx}$:
\[
 \langle Dj,e^{-inx}\rangle
 =-\int j(x)(-in)e^{-inx}\,dx
 =2\pi in\widehat j(n).
\]
The Dirac sum gives $\sum_\ell a_\ell e^{-in\tau_\ell}$.
For $n>K$, the smooth polynomial contributes zero. Without bandlimiting it
contributes the stated defect. At $n=0$ the derivative moment is zero, in
agreement with $\sum a_\ell=0$; it cannot determine the signal mean.
''',[('unknown','The derivative packet; Removing the unknown smooth background'),('self','Signal class and Fourier convention')])
claim(19,'Hankel rank detects the actual order',r'Finite exponential moments over $\mathbb C$',r'Let $m_{n_0+k}=\sum_{\ell=1}^r c_\ell z_\ell^k$, with distinct nonzero nodes and nonzero coefficients. Let $H_{h,w}=(m_{n_0+i+j})_{0\le i<h,\ 0\le j<w}$, with $h,w\ge r$.',r'''
Writing $V_h=(z_\ell^i)_{i,\ell}$ and $V_w=(z_\ell^j)_{j,\ell}$,
\[
 H_{h,w}=V_h\operatorname{diag}(c_\ell)V_w^{\mathsf T},
 \qquad\operatorname{rank}H_{h,w}=r.
\]
For $r=0$ the Hankel matrix is zero. The transpose is algebraic and is not
a conjugate transpose.
''',r'''
Expand a matrix entry to obtain the factorization. The leading $r\times r$
Vandermonde submatrix has determinant
$\prod_{\ell<k}(z_k-z_\ell)$, which is nonzero. Thus both rectangular
Vandermonde factors have full column rank, and their transposes have full
row rank. The diagonal factor is invertible. Its product with $V_w^T$ is
surjective onto $\mathbb C^r$, and subsequent multiplication by the injective
$V_h$ has image dimension $r$. For an empty exponential sum every entry is
zero and the rank is zero.
''',[('unknown','The Hankel packet and its rank'),('self','Unknown jump count from a Hankel gap')])
claim(20,'Exact Prony annihilation and location recovery','The nonzero-order moment model of SG-19',r'Assume $r\ge1$ and $2r$ consecutive moments $m_{n_0},\ldots,m_{n_0+2r-1}$ are known.',r'''
The unique monic annihilator
\[
 Q(z)=\prod_{\ell=1}^r(z-z_\ell)=\sum_{k=0}^{r-1}q_kz^k+z^r
\]
is recovered from
\[
 H_{r,r}q=-v,\qquad v=(m_{n_0+r+i})_{i=0}^{r-1}.
\]
Its roots are exactly the nodes. Once the nodes are known, $r$ consecutive
moments determine the coefficients uniquely by a Vandermonde solve.
For unit-modulus nodes the corresponding locations are
$\tau_\ell=-\arg z_\ell\pmod{2\pi}$.
''',r'''
For every available recurrence index,
\[
 \sum_{k=0}^rq_km_{n+k}
 =\sum_\ell c_\ell z_\ell^{n-n_0}Q(z_\ell)=0,
 \qquad q_r=1.
\]
SG-19 makes $H_{r,r}$ invertible. Thus the system has one solution and the
true polynomial supplies it. Factoring the resulting polynomial recovers the
distinct nodes up to a permutation. The amplitude matrix for consecutive
moments is a square Vandermonde multiplied by an invertible diagonal node
power matrix, so it too is invertible. The argument convention identifies
locations modulo a period, as required. Polynomial root extraction is a
finite algebraic step; the theorem does not claim that arbitrary real
locations have rational closed forms.
''',[('unknown','The annihilating polynomial; Recovering jump amplitudes and the edge packet')],['SG-19'])
claim(21,'Canonical periodic integration of jump data','A period of length $T>0$',r'Let distinct locations $\tau_\ell\in\mathbb R/(T\mathbb Z)$ and real amplitudes $a_\ell$ satisfy $\sum_\ell a_\ell=0$. Define the mean-zero periodic sawtooth $G_T(x)=1/2-x/T$ for $0<x<T$, with the right-continuous endpoint value.',r'''
\[
 j(x)=\sum_\ell a_\ell G_T(x-\tau_\ell)
\]
is the unique mean-zero right-continuous piecewise-constant packet with those
jumps. Its distributional derivative is $\sum_\ell a_\ell\delta_{\tau_\ell}$.
''',r'''
The sawtooth derivative is $DG_T=\delta_0-T^{-1}dx$: its slope is $-1/T$
away from the endpoint and its endpoint jump is one. Summing translated
copies gives the prescribed Dirac masses and a constant-density term
$-T^{-1}\sum a_\ell$, which vanishes. Consequently $j$ is constant between
the jump points. Each translated sawtooth has mean zero, so $j$ does too.
Any other packet with the same jumps has distributional derivative difference
zero. Since both are piecewise constant, their difference is the same
constant on every segment and across every jump. The mean-zero condition
sets it to zero almost everywhere, and right continuity fixes the endpoint
values. This explicit formula also supplies the perturbation estimate later.
''',[('unknown','Periodic integration')],['SG-18'],evidence='reconstructed_prose_proof')
claim(22,'Finite exact unknown-order reconstruction',r'The real class $\mathcal U_{K,L}$',r'Let $K\ge0$ and $L\ge1$ be known integers. Assume exact Fourier coefficients for $-K\le n\le K$ and $K+1\le n\le K+2L$.',r'''
Those data uniquely determine the actual active order $r$, every jump
location and amplitude up to permutation, the canonical edge packet $j$,
the smooth coefficients of $s$, and the complete signal $f$ as an $L^1$ class
and as its selected right-continuous representative. The high-frequency
budget is $2L$ complex coefficients. The low budget is $2K+1$ coefficients,
with conjugate symmetry redundancy for a real signal.
''',r'''
Use SG-18 to form $2L$ exact high derivative moments. With $n_0=K+1$,
form $H_{L,L}$ using the first $2L-1$ of them. SG-19 says its rank is the
actual $r$. If $r=0$, $j=0$ and the low coefficients directly give $s$.
Otherwise the first $2r$ moments are available. SG-20 recovers the nodes and
amplitudes. SG-21 constructs the unique normalized edge.
For each $|n|\le K$, subtract its coefficient from $\widehat f(n)$ to obtain
$\widehat s(n)$; all other smooth coefficients are zero by the model.
Their finite trigonometric sum gives $s$. Every step is uniquely determined,
so another signal in the class with those data must have the same edge and
background. Finally add $s+j$. Values at jump points are selected by the
stated convention, rather than inferred from measure-zero Fourier data.
''',[('unknown','The universal off-grid recovery theorem')],['SG-18','SG-19','SG-20','SG-21'],repair='Exactness from Fourier data is stated for the L1 class and its declared right-continuous representative. Arbitrarily assigned point values at discontinuities are not recoverable from Fourier integrals.')
prose(r'''
The measurement bound is a sufficient budget for this construction, not a
minimal sample theorem. Exact order is an algebraic rank. A floating-point
rank threshold requires a quantitative gap, addressed below. Distinct nodes
need not have a prescribed minimum separation for exact uniqueness, but
stability constants deteriorate as nodes approach one another.
''')
section('Perturbation contracts for the finite recovery steps')
claim(23,'Hankel perturbation from Fourier noise','A rectangular Hankel matrix of derivative moments',r'Let measured Fourier coefficients have errors $\eta_n$ and moment errors $\epsilon_n=2\pi in\eta_n$. Let $E=(\epsilon_{n_0+i+j})$ have $h\ge1$ rows and $w\ge1$ columns.',r'''
\[
 \|E\|_2\le\|E\|_F
 \le\sqrt{hw}\max_{0\le i<h,\ 0\le j<w}|\epsilon_{n_0+i+j}|.
\]
In particular, an error bound $|\eta_n|\le\eta$ implies
\[
 \|E\|_2\le2\pi\sqrt{hw}\eta\max_{i,j}|n_0+i+j|.
\]
''',r'''
Differentiate the noisy Fourier coefficients to obtain the exact moment
error identity. The spectral norm is at most the Frobenius norm. Its square
is the sum of $hw$ squared entry magnitudes, each bounded by the squared
maximum. Substitute $|\epsilon_n|=2\pi|n||\eta_n|$.
Repeated moments occur at multiple matrix entries; the Frobenius bound
correctly includes those repetitions. Smooth background tails can be included
in $\epsilon_n$ by the same calculation.
''',[('unknown','Fourier noise becomes derivative-moment noise; Hankel perturbation')])
claim(24,'Annihilator coefficient perturbation','The invertible square Prony system of SG-20',r'Write $Hq=-v$, and suppose $\widetilde H=H+E$, $\widetilde v=v+e$. Assume $\|H^{-1}\|_2\|E\|_2<1$.',r'''
The perturbed system is invertible, and its solution satisfies
\[
 \|\widetilde q-q\|_2
 \le\frac{\|H^{-1}\|_2}{1-\|H^{-1}\|_2\|E\|_2}
       (\|e\|_2+\|E\|_2\|q\|_2).
\]
''',r'''
Factor $\widetilde H=H(I+H^{-1}E)$. The Neumann series converges in operator
norm under the supplied inequality, so
$\|\widetilde H^{-1}\|_2\le
\|H^{-1}\|_2/(1-\|H^{-1}\|_2\|E\|_2)$.
Subtract the equations to obtain
$\widetilde H(\widetilde q-q)=-e-Eq$. Apply the inverse bound and the
triangle inequality. The estimate assumes that the same true order is used;
it does not itself choose the order from noisy data.
''',[('unknown','Hankel perturbation; Root localization by Rouche theorem')],['SG-20','SG-23'],evidence='reconstructed_prose_proof')
claim(25,'Conditional simple-root disk localization','Monic complex polynomials of the same degree',r'Let $r\ge1$ and $Q(z)=\prod_{\ell=1}^r(z-z_\ell)$ have distinct roots and $\widetilde Q=Q+E_Q$. Choose $0<\rho<\tfrac12\min_{\ell\ne k}|z_\ell-z_k|$ when $r\ge2$, or any $\rho>0$ when $r=1$.',r'''
If for every $\ell$
\[
 \sup_{|z-z_\ell|=\rho}|E_Q(z)|
 <\min_{|z-z_\ell|=\rho}|Q(z)|,
\]
then $\widetilde Q$ has exactly one root, counted with multiplicity, in each
disk $|z-z_\ell|<\rho$. All its roots are thereby matched with error less
than $\rho$. A sufficient explicit bound on each circle is
\[
 \sum_{k=0}^{r-1}|\widetilde q_k-q_k|(|z_\ell|+\rho)^k
 <\rho\prod_{j\ne\ell}(|z_\ell-z_j|-\rho).
\]
''',r'''
Each disk contains exactly one root of $Q$. The strict boundary inequality
is the hypothesis of Rouche's theorem, which preserves the number of zeros
inside. There are $r$ disjoint disks, each containing one zero of the degree
$r$ perturbed polynomial, so they account for every zero.
For the explicit version, apply the triangle inequality to the coefficient
error polynomial and use $|z|\le|z_\ell|+\rho$. On the circle,
$|z-z_\ell|=\rho$ and
$|z-z_j|\ge|z_\ell-z_j|-\rho$, giving the lower product bound.
For unit true nodes and a recovered root inside a disk with $\rho<1$, radial
normalization changes its chord error to at most $2\rho$ by the triangle
inequality. Its angular location error is then at most $2\arcsin\rho$.
The disk radius is a complex-root error, not directly an angular error.
''',[('unknown','Root localization by Rouche theorem')],['SG-24'],evidence='manuscript_proof_using_classical_Rouche_theorem',repair='This is a conditional stability theorem involving true root centers and true coefficient errors. It is not a certificate computable from noisy data alone, and a complex disk radius is not asserted to equal the angular location error.')
claim(26,'Amplitude stability with perturbed nodes','A square or overdetermined Vandermonde amplitude fit',r'Let $V$ have full column rank, $m=Va$, $\widetilde V=V+\Delta V$, and $\widetilde m=m+e$. Assume $\sigma_{\min}(V)>\|\Delta V\|_2$. Let $\widehat a$ minimize $\|\widetilde Vb-\widetilde m\|_2$.',r'''
\[
 \|\widehat a-a\|_2
 \le\frac{\|e\|_2+\|\Delta V\|_2\|a\|_2}
 {\sigma_{\min}(V)-\|\Delta V\|_2}.
\]
For unit nodes in rows with nonnegative powers $n$, matched chord error
$|\widehat z_\ell-z_\ell|\le\delta$ gives the entry bound
$|\widehat z_\ell^n-z_\ell^n|\le n\delta$.
''',r'''
The minimum singular value of $\widetilde V$ is at least
$\sigma_{\min}(V)-\|\Delta V\|_2>0$. Thus its least-squares inverse exists.
Since $\widetilde V a=m+\Delta V a$,
\[
 \widehat a-a=\widetilde V^\dagger(e-\Delta V a).
\]
Apply $\|\widetilde V^\dagger\|_2=1/\sigma_{\min}(\widetilde V)$.
The power bound follows by factoring
$\widehat z^n-z^n=(\widehat z-z)\sum_{k=0}^{n-1}\widehat z^{n-1-k}z^k$;
each summand has modulus one. The statement assumes aligned nodes and unit
normalization. Arbitrary unnormalized roots require extra modulus factors.
''',[('unknown','Amplitude stability')],['SG-25'],evidence='reconstructed_prose_proof_with_classical_singular_value_bound')
section('Self-calibration of polyphase aliases',r'''
Decimation reorganizes the differentiated moments, and it also maps each
physical node $z$ to $z^N$. This can improve a selected geometry or create a
collision. The physical phase is retained in the offset coefficients. The
central recovery step uses those coefficients rather than choosing a principal
root by convention. The shifted-exponential ingredient is classical
\cite{vexpa}; the contracts below specify what is sufficient for its use in
the complete unknown-order pipeline.
''')
claim(27,'Shared-node offset channels','Derivative moments with an additive defect',r'Fix integers $N\ge2$, $q_0\ge1$, and an offset $r\ge0$. Suppose $m_n=\sum_\ell a_\ell z_\ell^n+e_n$, with $|z_\ell|=1$.',r'''
\[
 m_{(q_0+q)N+r}=\sum_\ell b_{\ell,r}u_\ell^q+e_{(q_0+q)N+r},
 \quad u_\ell=z_\ell^N,\quad b_{\ell,r}=a_\ell u_\ell^{q_0}z_\ell^r.
\]
For each matched edge $b_{\ell,r+1}=z_\ell b_{\ell,r}$.
If $|\widehat s(n)|\le C_s(1+|n|)^{-p-2}$ with $p\ge0$, then for
nonnegative $q,r$
\[
 |e_{(q_0+q)N+r}|\le2\pi C_s(q_0N)^{-p-1}.
\]
''',r'''
Split the exponent as $(q_0+q)N+r=q_0N+r+qN$ to obtain the channel
identity. Incrementing the offset multiplies only $z_\ell^r$ by $z_\ell$.
For the tail bound, use
$|e_n|=2\pi|n||\widehat s(n)|\le2\pi C_s(1+|n|)^{-p-1}$ and
$n\ge q_0N>0$. The channel identity is valid even when aliased nodes collide,
but a Prony solve on that channel then observes combined coefficients and
cannot separate those nodes using the simple distinct-node theorem.
''',[('self','Why decimation helps and why it aliases'),('complex','One-dimensional finite-rate packet model')],['SG-18'],evidence='manuscript_proof_of_classical_shifted_exponential_identity')
claim(28,'Order recovery with a supplied singular threshold','Finite rectangular complex matrices',r'Let $H=H_0+E$, with $H_0$ of rank $r\ge1$, $k=\min(h,w)\ge r$, and $\epsilon=\|E\|_2<\sigma_r(H_0)/2$. Supply a threshold $t$ with $\epsilon<t<\sigma_r(H_0)-\epsilon$.',r'''
Exactly $r$ singular values of $H$ exceed $t$. If $r=0$, a supplied
threshold $t>\|E\|_2$ selects zero. If $r=k$, all $k$ singular values exceed
the threshold and no nonexistent $\sigma_{k+1}$ is used.
''',r'''
The singular-value perturbation inequality \cite{stewart} gives
$|\sigma_j(H)-\sigma_j(H_0)|\le\|E\|_2$ for $1\le j\le k$.
It holds equally over the complex field: in the min--max characterization
\[
 \sigma_j(A)=\min_{\dim V=w-j+1}\max_{x\in V,\,\|x\|=1}\|Ax\|.
\]
the triangle inequality bounds each restricted maximum for $A+E$ by that
for $A$ plus $\|E\|_2$. Minimize and then interchange the two matrices.
For $j\le r$ this yields $\sigma_j(H)\ge\sigma_r(H_0)-\epsilon>t$.
For $j>r$, when such indices exist, it gives $\sigma_j(H)\le\epsilon<t$.
For rank zero the same upper bound applies to every singular value. For full
rectangular rank the lower bound already accounts for every singular value.
The theorem assumes a threshold satisfying the inequalities; it does not
prove that every heuristic gap selector finds it.
''',[('self','Unknown jump count from a Hankel gap')],['SG-19','SG-23'],evidence='manuscript_proof_using_classical_Weyl_singular_value_inequality')
sub('Why an empirical rank rule is a separate algorithm',r'''
The native implementation estimates order from singular-value ratios and
validation heuristics. A largest adjacent ratio is not implied to select the
true order by SG-28. An exact witness makes the distinction concrete. Take
four-by-four Hankel matrices of moments beginning at $n_0=4$ from the nodes
$(1,i,-1)$ and real amplitudes $(100,-99,-1)$. The four-point Fourier columns
are orthogonal, so the true singular values are $(400,396,4,0)$. Add the
moment perturbation $0.1(-i)^n$. It contributes a fourth orthogonal column and
produces singular values $(400,396,4,0.4)$ with perturbation norm $0.4$.
The hypothesis $0.4<4/2$ holds. A threshold in $(0.4,3.6)$ selects the true
order three, while the largest adjacent ratio $396/4=99$ selects order two.
Thus a valid quantitative threshold theorem and a successful practical
heuristic remain different claims.
''')
claim(29,'Exact phase from adjacent offset products','One matched unit-circle coefficient progression',r'Let $R\ge1$ be an integer counting adjacent products, and let $c_r=bz^r$ for $0\le r\le R$, with $b\ne0$ and $|z|=1$. Define $S(c)=\sum_{r=0}^{R-1}\overline{c_r}c_{r+1}$.',r'''
\[
 S(c)=R|b|^2z\ne0,\qquad\Phi(c):=S(c)/|S(c)|=z.
\]
Two channels already give $z=c_1/c_0$ exactly. More channels provide repeated
adjacent relations, without an unconditional deterministic averaging gain.
''',r'''
Each summand is
$\overline{bz^r}\,bz^{r+1}=|b|^2z$ because $|z|=1$.
There are $R$ summands and $R\ge1$, so normalization returns $z$.
For two channels direct division cancels $b$. No statistical independence is
assumed, so one cannot improve a worst-case noise order merely by increasing
$R$; the next bound shows the cancellation of the number of products.
''',[('self','Offset coefficients and internal phase recovery')],['SG-27'],repair='R denotes the number of adjacent products, so R+1 offset channels are used and R is at least one. An empty sum has no phase.')
claim(30,'Deterministic offset-phase perturbation','A noisy progression as in SG-29',r'Let $c_r=bz^r+e_r$ for $0\le r\le R$, with $R\ge1$, $b\ne0$, $|z|=1$, and $|e_r|\le\epsilon$. Put $A=R|b|^2$ and $\Delta=R(2|b|\epsilon+\epsilon^2)$. Assume $\Delta<A$.',r'''
The phase sum is nonzero and
\[
 |\Phi(c)-z|\le\frac{2\Delta}{A}
 =\frac{4\epsilon}{|b|}+2\left(\frac\epsilon{|b|}\right)^2.
\]
''',r'''
Expand each product:
\[
 \overline{c_r}c_{r+1}=|b|^2z
 +\overline{bz^r}e_{r+1}+\overline{e_r}bz^{r+1}
 +\overline{e_r}e_{r+1}.
\]
The three error terms have total magnitude at most
$2|b|\epsilon+\epsilon^2$. Summing gives $S(c)=Az+E$ with $|E|\le\Delta$.
Therefore $|S(c)|\ge A-\Delta>0$.
For any nonzero $v$ and unit $z$,
\[
 \left|\frac v{|v|}-z\right|
 \le\left|\frac v{|v|}-\frac vA\right|+\left|\frac vA-z\right|
 =\frac{\bigl|A-|v|\bigr|}{A}+\frac{|v-Az|}{A}
 \le\frac{2|v-Az|}{A}.
\]
Apply this inequality to $v=S(c)$ and substitute the definitions.
The number of products cancels, as appropriate for coherent adversarial errors.
''',[('self','Deterministic phase perturbation; Detailed algebra for the multi-offset estimator')],['SG-29'])
claim(31,'A zero offset residual tests a progression','Finite complex offset data',r'Let $R\ge1$, $c_0\ne0$, and $|\zeta|=1$. Define $\nu(c,\zeta)=\bigl(\sum_{r=0}^{R-1}|c_{r+1}-\zeta c_r|^2\bigr)^{1/2}/\bigl(\sum_{r=0}^{R-1}|c_r|^2\bigr)^{1/2}$.',r'''
Then $\nu(c,\zeta)=0$ if and only if $c_r=c_0\zeta^r$ for
$0\le r\le R$.
''',r'''
The denominator is positive because it includes $|c_0|^2$.
A sum of nonnegative squared magnitudes is zero precisely when each recurrence
$c_{r+1}=\zeta c_r$ holds. Induction gives the progression. The reverse
implication follows by substitution. This is a consistency check for the
fitted offsets. Another physical model or structured background could produce
the same progression; zero residual alone does not certify the true edge
model or a true-location error bound. Unused offset channels provide a
stronger practical check because they are not part of the fit, but no
universal probability guarantee is asserted here.
''',[('self','A posteriori phase validation')],['SG-29'])
claim(32,'Unique branch selection under a strict margin','Nth roots of a unit-modulus estimate',r'Let $N\ge2$, $|z|=1$, $u=z^N$, and $\overline u=\widehat u/|\widehat u|$ with $\widehat u\ne0$. Let $\rho$ be a root of $\overline u$ continuously associated with $z$, and $\widetilde z$ a coarse phase estimate.',r'''
If
\[
 |\widetilde z-z|+|\rho-z|<\sin(\pi/N),
\]
then $\rho$ is the unique root of $\overline u$ nearest to $\widetilde z$.
It equals the branch an oracle chooses by the true-node neighborhood.
''',r'''
The $N$ candidates lie on the unit circle at angles spaced by $2\pi/N$.
The smallest distance between distinct candidates is $2\sin(\pi/N)$.
The triangle inequality gives
$|\widetilde z-\rho|\le|\widetilde z-z|+|z-\rho|<\sin(\pi/N)$.
For any other candidate $\rho'$,
$|\widetilde z-\rho'|\ge|\rho'-\rho|-|\rho-\widetilde z|
>\sin(\pi/N)$. Thus the nearest candidate is unique. The same spacing
argument places every wrong root farther from the true node than the
associated root under the given margin. The oracle and data-based choices
therefore coincide. This is conditional on the margin; the true-node terms
are not available directly to the algorithm.
''',[('self','Branch lifting from aliased nodes')],['SG-30'],repair='The candidate-spacing and branch-margin statement explicitly assumes N at least two.')
claim(33,'Associated roots divide the angular error','Unit-modulus nodes and their associated root branches',r'Let $N\ge1$, $z^N=u$, $|z|=|u|=|\overline u|=1$, and $|\overline u-u|\le\eta<2$. Let $\rho$ be the associated root along the shortest angular perturbation.',r'''
\[
 |\rho-z|\le2\sin\left(\frac1N\arcsin\frac\eta2\right)
 \le\frac2N\arcsin\frac\eta2.
\]
For a nonzero raw estimate, $|\widehat u-u|\le\epsilon$ implies
$|\widehat u/|\widehat u|-u|\le2\epsilon$. Thus when the raw error tends to
zero, correct lifting gains a factor $1/N$ in chord and angular accuracy.
''',r'''
If $\theta\in(-\pi,\pi)$ is the shortest angular difference, the unit-circle
chord identity gives $|\overline u-u|=2\sin(|\theta|/2)$.
Hence $|\theta|\le2\arcsin(\eta/2)$. On the associated branch the root
angle changes by $\theta/N$. Convert to chord distance and use $\sin t\le t$.
For normalization, add and subtract $\widehat u$:
\[
 |\widehat u/|\widehat u|-u|
 \le|1-|\widehat u||+|\widehat u-u|
 \le2|\widehat u-u|.
\]
The shortest-angle ambiguity at an antipodal estimate is excluded by
$\eta<2$. The gain applies to an associated branch, so a branch-selection
argument such as SG-32 is needed to transfer it to an estimator.
''',[('self','One-order root gain; Detailed algebra for the branch lift')],['SG-32'])
claim(34,'An explicit exact self-calibration budget','Bandlimited background with a bounded number of jumps',r'Let $f\in\mathcal U_{K,L_{\max}}$, with $L_{\max}\ge1$. Supply $N\ge2$, $q_0\ge1$ with $q_0N>K$, and assume the active aliased nodes $u_\ell=z_\ell^N$ are distinct.',r'''
The Fourier coefficients at the high indices
\[
 \mathcal I_0=\{(q_0+q)N:0\le q\le2L_{\max}\},\qquad
 \mathcal I_1=\{(q_0+q)N+1:0\le q<L_{\max}\}
\]
determine the unknown edge order, every physical node, and every jump amplitude
exactly. The high-frequency budget is $3L_{\max}+1$. Low modes
$-K\le n\le K$ then give the complete signal. No supplied jump neighborhood
is required.
''',r'''
All high indices exceed $K$, so the derivative moments have no smooth defect.
The base channel is an exponential sum in the distinct $u_\ell$ with
coefficients $b_{\ell,0}=a_\ell u_\ell^{q_0}\ne0$.
Its $2L_{\max}+1$ moments form an $(L_{\max}+1)$ square Hankel matrix;
SG-19 gives its rank $r$. If $r=0$, the edge is zero and the low modes finish
the recovery. Otherwise SG-20 recovers the $u_\ell$ and then the base
coefficients. The adjacent channel supplies at least $r$ moments of
$\sum_\ell b_{\ell,0}z_\ell u_\ell^q$. Using the same recovered nodes, its
Vandermonde system recovers $b_{\ell,1}=b_{\ell,0}z_\ell$.
Division gives $z_\ell=b_{\ell,1}/b_{\ell,0}$, and
$a_\ell=b_{\ell,0}u_\ell^{-q_0}$.
SG-21 constructs $j$, and subtraction from the low modes constructs $s$.
The two index sets are disjoint because $N\ge2$ and their residues are zero
and one. Their sizes add to $3L_{\max}+1$. This is an upper bound for the
construction and excludes the low reconstruction coefficients.
''',[('self','Self-calibrating reconstruction theorem; Explicit finite innovation budget')],['SG-19','SG-20','SG-21','SG-27'],repair='The budget is conditional on one supplied noncolliding decimation. A finite search over candidate decimations is not guaranteed to contain such a decimation without an additional existence hypothesis.')
claim(35,'Conditional asymptotic rates after calibrated lifting','A selected sequence of decimation scales',r'Let $p\ge0$, fix $q_0$ and the finite number of channel samples and offsets, and take a sequence $N\to\infty$. Assume distinct aliased nodes, uniform rank-threshold gaps/local inverse bounds for the aligned Prony and coefficient fits, $|b_{\ell,0}|\ge b_{\min}>0$, uniformly bounded amplitudes, and the strict branch margin of SG-32. Suppose the moment defect is $O(N^{-p-1})$.',r'''
The threshold-selected order is eventually correct. The aligned lifted nodes
and locations satisfy
\[
 |\widehat z_\ell-z_\ell|=O(N^{-p-2}),\qquad
 d_{\mathbb T}(\widehat\tau_\ell,\tau_\ell)=O(N^{-p-2}).
\]
The recovered amplitudes satisfy
$|\widehat a_\ell-a_\ell|=O(N^{-p-1})$.
''',r'''
Uniform local inverse bounds transfer the moment error to aliased node and
matched coefficient errors of order $N^{-p-1}$. The supplied rank gap and
threshold select the correct order by SG-28. Nonvanishing base coefficients
allow SG-30 to give the same order for the coarse phase error.
The strict branch margin selects the associated root by SG-32. Normalize the
aliased estimate and use SG-33: its root error is $N^{-1}$ times an error of
order $N^{-p-1}$, giving $N^{-p-2}$. On the unit circle,
$d_{\mathbb T}=2\arcsin(|\widehat z-z|/2)$, which has the same order for
small errors. For the amplitude use
$\widehat a=\widehat b_0\,\overline u^{-q_0}$ and $a=b_0u^{-q_0}$.
Since $q_0$ is fixed and both powers have unit modulus, SG-26's telescoping
power estimate bounds the power error by $q_0|\overline u-u|$.
Together with the coefficient error this gives the stated amplitude order.
The smooth-tail assumption in SG-27 supplies the moment defect.
The conclusion is uniform only on the selected scales and parameter families
for which the inverse, rank, and branch bounds are uniform.
''',[('self','Rate-preserving polyphase lifting; Perturbed self-calibration for a non-bandlimited background')],['SG-27','SG-28','SG-30','SG-32','SG-33'],repair='For p=0 the coarse phase error and root spacing are both of order 1/N, so the branch margin is retained as an explicit hypothesis. Physical separation alone does not imply uniform aliased separation for every N; rates are asserted only along admissible selected scales.')
prose(r'''
The native pipeline does not receive the true order or jump neighborhoods.
It tests several decimations, fits common nodes, uses offsets for branch
selection, and performs validation and optional nonlinear refinement.
Those algorithmic choices are supported by the displayed conditional
contracts and finite experiments. The rate theorem does not assert that a
largest-gap heuristic, every decimation, or every non-bandlimited signal
satisfies its hypotheses.
''')
section('Native edge synthesis and a corrected perturbation estimate')
claim(36,'Resolved synthesis splits the two error sources','A normed signal space',r'Let $f=s+j$, let $\widehat j$ belong to the same space, and let $A_M$ be a bounded linear operator with norm at most $C_M$. Define $\widehat f_M=A_M(f-\widehat j)+\widehat j$.',r'''
\[
 f-\widehat f_M=(s-A_Ms)+(I-A_M)(j-\widehat j),
\]
and therefore
\[
 \|f-\widehat f_M\|\le\|s-A_Ms\|+(1+C_M)\|j-\widehat j\|.
\]
If $\widehat j=j$, the complete error equals the smooth approximation error.
''',r'''
Substitute $f=s+j$ into the definition and collect the two terms. Linearity
of $A_M$ is used in that collection. The triangle inequality and
$\|I-A_M\|\le1+\|A_M\|$ give the estimate. With the exact edge, its error
term vanishes as an object identity. The theorem holds for the declared norm;
a misplaced discontinuity need not be small in supremum norm even when its
location error is small. In $L^1$, the next theorem quantifies that error.
A nonlinear clipping operator is not an instance of this linear identity.
''',[('self','A stable synthesis theorem'),('complex','Resolved synthesis')],['SG-10','SG-22'])
claim(37,'Sharp additive L1 control for normalized jump packets','Mean-zero periodic packets of period $T>0$',r'Let $j,\widehat j$ have matched real jump data $(a_\ell,\tau_\ell)$ and $(\widehat a_\ell,\widehat\tau_\ell)$, with both amplitude sums zero. Use their canonical representatives and let $d_\ell=d_T(\tau_\ell,\widehat\tau_\ell)\le T/2$.',r'''
\[
 \|j-\widehat j\|_1
 \le\frac T4\sum_\ell|a_\ell-\widehat a_\ell|
 +2\sum_\ell|\widehat a_\ell|d_\ell(1-d_\ell/T).
\]
In particular the simpler location term $2\sum_\ell|\widehat a_\ell|d_\ell$
is valid. The printed location coefficient one in the inherited
self-calibration manuscript is not valid for mean-zero normalization.
''',r'''
SG-21 writes both packets as translated sawtooth sums. Subtract in the form
\[
 j-\widehat j=
 \sum_\ell(a_\ell-\widehat a_\ell)G_T(\cdot-\tau_\ell)
 +\sum_\ell\widehat a_\ell
 [G_T(\cdot-\tau_\ell)-G_T(\cdot-\widehat\tau_\ell)].
\]
Direct integration gives $\|G_T\|_1=T/4$.
For a shift by $d\in[0,T/2]$, on an interval of length $T-d$ the difference
has magnitude $d/T$, and on an interval of length $d$ it has magnitude
$1-d/T$. Hence its $L^1$ norm is
$(T-d)d/T+d(1-d/T)=2d(1-d/T)$.
Apply the triangle inequality term by term. Periodic translation invariance
makes the calculation depend only on circular shift distance.
To refute coefficient one, take
\[
 j=\mathbf1_{[0,T/2)}-\tfrac12,\qquad
 \widehat j=\mathbf1_{[T/4,T/2)}-\tfrac14.
\]
Both have jumps $(1,-1)$, with one jump shifted by $T/4$. Their norm
difference is $3T/8$, while the inherited bound gives $T/4$.
The sharper location term is attained in this example. The amplitude
coefficient $T/4$ is also attained by changing opposite antipodal jump
amplitudes: the difference packet has constant magnitude half the amplitude
change on the two half-periods.
''',[('self','A stable synthesis theorem')],['SG-21','SG-36'],evidence='repaired_prose_theorem_with_direct_integration',repair='The old L1 estimate is refuted by two mean-zero interval packets. The published bound includes the normalization-induced constant shift and uses the exact translated-sawtooth norm.')
claim(38,'A conditional global L1 reconstruction rate',r'The rate family of SG-35 with $T=2\pi$',r'Assume a fixed finite jump count, bounded jump amplitudes, the hypotheses of SG-35, and a bounded linear smooth reconstruction $A_M$ acting on $L^1(\mathbb T)$. Require $\widehat j$ to be the canonical packet of real matched estimated amplitudes whose sum is zero. Let $b_M=\|s-A_Ms\|_1$ and $C_M=\|A_M\|_{L^1\to L^1}$.',r'''
\[
 \|j-\widehat j\|_1=O(N^{-p-1}),\qquad
 \|f-\widehat f_M\|_1\le b_M+O((1+C_M)N^{-p-1}).
\]
For Fourier truncation, $C_M=O(1+\log(M+1))$. If also
$|\widehat s(n)|\le C_s(1+|n|)^{-p-2}$, its smooth remainder satisfies
$b_M=O(M^{-p-1})$. Taking $M$ comparable to $N$ yields
$O((1+\log N)N^{-p-1})$.
''',r'''
SG-35 gives an amplitude error of order $N^{-p-1}$ and a location error of
order $N^{-p-2}$. If the fitted amplitudes are complex or do not sum to zero,
take their real parts and subtract their common arithmetic mean. Since the
true real amplitudes sum to zero, this changes each amplitude error by at
most another maximum amplitude error, preserving its order. Apply SG-21 to
the resulting real zero-sum data to define $\widehat j$. Insert these errors into SG-37, with finitely many bounded
amplitudes, to obtain the edge norm bound. SG-36 then gives the general
synthesis estimate.
For Fourier truncation, its convolution norm is bounded by the normalized
$L^1$ norm of $D_M$. On $[-\pi,\pi]$ use
$|D_M(t)|\le\min(2M+1,\pi/|t|)$, with the removable value at zero.
Split the integral at $1/(M+1)$ to obtain the logarithmic bound.
The smooth Fourier tail has supremum bound
$2C_s\sum_{n>M}(1+n)^{-p-2}=O(M^{-p-1})$ by an integral comparison;
multiplication by $2\pi$ gives the $L^1$ estimate.
This conclusion accounts for the norm growth of partial sums instead of
assuming a uniformly bounded Fourier truncation operator on $L^1$.
''',[('self','A stable synthesis theorem; Limitations and next theorem')],['SG-35','SG-36','SG-37'],evidence='reconstructed_prose_proof')
section('Shared edges, jump jets, and geometric image models')
claim(39,'Shared-location multichannel recovery','A finite collection of exponential moment channels',r'Let $m_n^{(c)}=\sum_{\ell=1}^ra_{c\ell}z_\ell^n$, with distinct common unit-modulus nodes. At each node at least one channel amplitude is nonzero. Form the stacked linear recurrence system for a monic polynomial of degree $r$ and assume its coefficient matrix has column rank $r$.',r'''
The stacked system uniquely recovers the common annihilator
$Q(z)=\prod_\ell(z-z_\ell)$. Its roots recover the common locations.
With $r$ consecutive moments per channel, a channelwise Vandermonde solve
recovers every amplitude, including amplitudes that vanish in that channel.
''',r'''
The polynomial $Q$ annihilates every exponential term and therefore every
channel, as in SG-20. Full column rank of the stacked recurrence matrix means
that a consistent coefficient vector is unique; the true $Q$ provides one.
Its distinct roots give the nodes. Once known, the same nonsingular
Vandermonde system solves each channel independently. No individual channel
has to see all nodes, but the stated stacked rank is essential. Merely
collecting channels does not prove that rank condition automatically.
''',[('unknown','Several channels with shared edge locations')],['SG-20'])
claim(40,'Confluent annihilation and the leading offset phase','Polynomial-exponential sequences',r'Let $m_n=\sum_{\ell=1}^rz_\ell^nP_\ell(n)$ with distinct nonzero nodes and $\deg P_\ell\le d$. Let $E$ be the forward shift. For an offset ratio assume $N\ge1$ and the leading coefficient of $P_\ell$ at degree $d$ is nonzero.',r'''
\[
 \prod_{\ell=1}^r(E-z_\ell)^{d+1}m=0.
\]
For offset $v\ge0$, writing a decimated channel as
\[
 m_{(q_0+q)N+v}=\sum_\ell u_\ell^q
                   \sum_{h=0}^d\gamma_{\ell,v,h}q^h,
 \qquad u_\ell=z_\ell^N,
\]
the highest-degree coefficients satisfy
$\gamma_{\ell,1,d}/\gamma_{\ell,0,d}=z_\ell$.
This ratio applies to separated, matched confluent terms with nonzero leading
coefficient. The displayed annihilator is not asserted to have minimal order
when leading coefficients vanish.
''',r'''
For one term, $(E-z)(z^nP(n))=z^{n+1}(P(n+1)-P(n))$.
A finite difference lowers a nonconstant polynomial's degree by one, and
annihilates a constant. After $d+1$ differences the term vanishes. The shift
factors commute, so the product annihilates every term in the sum.
If $P_\ell(n)$ has leading coefficient $c_\ell\ne0$ at degree $d$, substitution
of $(q_0+q)N+v$ has leading $q$ coefficient $c_\ell N^d$.
The remaining exponential prefactor is $z_\ell^{q_0N+v}$; hence
$\gamma_{\ell,v,d}=c_\ell N^dz_\ell^{q_0N+v}$ and the ratio is $z_\ell$.
Repeated roots require confluent recovery and stability arguments; the
simple-root disk theorem SG-25 cannot be used to claim one perturbed root
per physical node or a Lipschitz individual-root bound at a multiple root.
''',[('unknown','Piecewise-polynomial packets'),('self','Higher jump jets and confluent Prony systems')],['SG-27'],repair='Annihilation is proved without a minimal-order assertion. Phase division requires a nonzero highest-degree coefficient, and simple-root perturbation claims are not transferred to repeated roots.')
claim(41,'Model mismatch enters the same sparse stability bound','A finite-dimensional background-edge model',r'Use $A=RD$ from SG-14 and assume $s\ge1$, $d\ge1$, and its restricted constant $\gamma>0$. Suppose $y=s_0+D\alpha_0+e+\eta$, with $s_0\in\mathcal S$, $\|\alpha_0\|_0\le s$, and $\|R(e+\eta)\|_2\le\epsilon$. Let $\widehat\alpha$ be $s$-sparse with $\|A\widehat\alpha-Ry\|_2\le\epsilon$.',r'''
\[
 \|\widehat\alpha-\alpha_0\|_2\le2\epsilon/\gamma.
\]
If an actual edge $j$ obeys $\|j-D\alpha_0\|_2\le\delta$, then
\[
 \|j-D\widehat\alpha\|_2\le\delta+2\|D\|_2\epsilon/\gamma.
\]
The theorem applies to finite image dictionaries under these printed
sparsity, residual, and restricted-injectivity hypotheses.
''',r'''
The nuisance $e+\eta$ has exactly the role of the residualized noise in
SG-15, so its proof gives the coefficient bound. Add and subtract
$D\alpha_0$ in the edge difference and apply the operator norm bound to the
coefficient error. A best approximation can be substituted when it exists;
otherwise any admissible approximate minimizer gives the same statement.
The theorem does not show that a greedy finite dictionary selector outputs
an $s$-sparse vector with the specified tolerance. Nor does it establish
restricted injectivity for every geometric dictionary; both remain
hypotheses to verify for a concrete model.
''',[('complex','Two-dimensional finite dictionary model; A theorem for model mismatch')],['SG-14','SG-15'],evidence='reconstructed_prose_proof')
sub('What the image experiments test',r'''
The complex benchmark uses a low-frequency DCT background and 318 geometric
atoms: rectangles, disks, ellipses, and horizontal and vertical bars.
The named exact-model images and forty archived random dictionary cases select
the intended supports under their deterministic settings. Those are finite
results. SG-14 and SG-41 explain the contract a universal statement about
such a library would require; the benchmark does not establish all its
restricted singular values or make a greedy selector universally exact.

The seven-point star, text over a gradient, and nested rings lie outside the
fixed dictionary. Their comparisons are retained as model-mismatch tests.
Four natural images are exploratory examples, not instances of a finite-rate
exact edge theorem. In the natural-background hybrid the selector returns
five atoms for three true overlays. Background structure outside the chosen
DCT space is being explained as extra geometry. This exposes a background
model failure rather than just an edge-library failure.
''')
section('Countable packet grammars and finite image approximation',r'''
A countable grammar can describe an unlimited ideal family while a program
uses a finite prefix or a finite store. The infinite packet code in this
bundle performs adaptive approximation of an available pixel image. Its
constructor receives the full image, and residual seeds are generated from
that image minus the current reconstruction. This is a different observation
model from the finitely measured Fourier recovery theorem.
The exact statements below specify what survives in the ideal mathematical
model and what changes under the native ridge and clipping operations.
''')
claim(42,'Ideal nested-span refitting decreases residual','A Hilbert space with finite selected packet spans',r'Let $V_1\subseteq V_2\subseteq\cdots$ be finite-dimensional subspaces. Let $P_k$ be the orthogonal projector onto $V_k$.',r'''
\[
 \|f-P_{k+1}f\|\le\|f-P_kf\|,
 \qquad f-P_kf\perp V_k.
\]
If $\bigcup_kV_k$ is dense, then $P_kf\to f$ in norm.
''',r'''
Orthogonal projection minimizes distance to its subspace. Since $P_kf$
belongs to the larger subspace $V_{k+1}$, its residual is a feasible upper
bound on the next minimum. Orthogonality follows from the defining projection
identity, or by varying the quadratic norm along every vector in $V_k$.
For convergence, fix $\epsilon>0$ and choose $v\in V_K$ within $\epsilon$
of $f$ by density. For all $k\ge K$, minimum distance is at most
$\|f-v\|<\epsilon$. Thus the residual converges to zero.
This theorem assumes dense actual selected spans. A countably dense candidate
pool alone does not show that a particular greedy selection sequence becomes
dense.
''',[('infinite','InfinitePacketReconstructor._refit; InfinitePacketGenerator')],evidence='reconstructed_prose_proof_for_ideal_unregularized_model')
claim(43,'Ridge refitting has a different stationarity law','Finite-dimensional real packet designs',r'Let $M\in\mathbb R^{m\times d}$, $y\in\mathbb R^m$, and $\lambda>0$. Let $c$ minimize $\|y-Mc\|_2^2+\lambda\|c\|_2^2$ and set $r=y-Mc$.',r'''
The minimizer is unique and
\[
 (M^{\mathsf T}M+\lambda I)c=M^{\mathsf T}y,
 \qquad M^{\mathsf T}r=\lambda c.
\]
Adding candidate columns cannot increase the minimized ridge objective,
but exact orthogonality $M^{\mathsf T}r=0$ is not the ridge stationarity law.
Even a complete pixel basis need not give zero residual when $\lambda>0$.
''',r'''
The Hessian is twice $M^TM+\lambda I$, which is positive definite because
$v^T(M^TM+\lambda I)v=\|Mv\|^2+\lambda\|v\|^2>0$ for nonzero $v$.
Setting the gradient to zero gives the unique minimizer and rearrangement gives
$M^Tr=\lambda c$. When columns are added, extending the previous coefficient
vector by zero is a feasible point with exactly the previous objective, so the
new optimum is no larger. This concerns the ridge objective, not an automatic
monotonicity theorem for the unpenalized residual alone.
For the full pixel basis $M=I$, $c=y/(1+\lambda)$ and
$r=\lambda y/(1+\lambda)$, which is nonzero for $y\ne0$.
The native default $\lambda=10^{-9}$ makes this residual small, not
mathematically zero. Numerical tolerances must remain numerical tolerances.
''',[('infinite','InfinitePacketReconstructor._refit; default ridge=1e-9')],evidence='reconstructed_prose_proof_for_native_ridge_contract',repair='Claims of exact unregularized refitting are separated from the implemented positive-ridge solve. The native normal-equation law includes the ridge term.')
claim(44,'Clipping is nonexpansive toward a bounded truth','Real pixel arrays with Euclidean norms',r'Define $C(x)$ coordinatewise by $C(t)=\min(1,\max(0,t))$. Suppose the truth $f$ has every coordinate in $[0,1]$.',r'''
\[
 \|C(x)-C(y)\|_2\le\|x-y\|_2,\qquad
 \|C(x)-f\|_2\le\|x-f\|_2.
\]
Clipping is nonlinear; it is not the bounded linear synthesis operator in
SG-36. Its truth-error guarantee depends on the stated box constraint.
''',r'''
For real scalars the clipping function is nondecreasing with slope between
zero and one on each of its three affine pieces. A direct case split at zero
and one gives $|C(x)-C(y)|\le|x-y|$ for every pair.
Square and sum the scalar inequalities. Since $C(f)=f$, substitute $y=f$ to
obtain the second estimate. Nonlinearity is explicit: $C(1+1)=1$ whereas
$C(1)+C(1)=2$. If the truth lies outside the box, clipping can increase its
error; for instance $x=f=2$ becomes $C(x)=1$.
''',[('infinite','bounded_synthesis')],evidence='reconstructed_prose_proof')
claim(45,'An exact residual archive preserves the object','Any normed signal space',r'Let an approximation $q$ to an available object $f$ be supplied, and retain the complete residual $r=f-q$.',r'''
The synthesis $q+r=f$ is exact. This identity supplies no sparsity, compression,
or recovery-from-fewer-measurements conclusion. In finite pixel space the
full pixel basis likewise spans every image in the ideal unregularized model.
''',r'''
The first statement is the defining subtraction identity. Retaining $r$
can carry every component omitted from $q$, so its data cost is not bounded by
a small number of packet coefficients. For an image $f\in\mathbb R^m$, the
standard pixel vectors satisfy $f=\sum_{j=1}^mf_je_j$ and form a complete
finite basis. Those coefficients are all the pixels themselves.
A program using the truth residual thus certifies faithful storage of its
available input, rather than uniqueness under a smaller measurement map.
''',[('infinite','exact_archive_residual; benchmark_case')],evidence='reconstructed_prose_proof')
claim(46,'Bounded identities extend from a dense core','Normed spaces and bounded linear maps',r'Let $D$ be a dense linear subspace of $X$, and let $A,B:X\to Y$ be bounded linear operators agreeing on $D$.',r'''
Then $A=B$ on $X$. Consequently a finite packet identity established on a
dense core extends to a completion when both represented operators have
bounded extensions. An infinite projector sum additionally requires a
specified convergent synthesis; bounded finite identities alone do not
supply that convergence.
''',r'''
For $x\in X$ choose $x_n\in D$ with $x_n\to x$.
Continuity gives $Ax=\lim_nAx_n=\lim_nBx_n=Bx$.
This proves uniqueness of bounded extensions. For an infinite packet sum one
would need partial sums to converge to the declared operator, in a stated
operator or strong topology. Neither density nor the finite identity by
itself proves such a limit. In SG-42 density of the actual selected spans
provides a specific strong convergence theorem; a capped dictionary store or
an arbitrary greedy prefix does not inherit it automatically.
''',[('seed','thm:dense-extension; cor:packet-completion')],evidence='manuscript_proof')
prose(r'''
The native infinite-packet generator uses finite stores, including mask caps
of 120 or 180 in reported settings. Its discrete masks, quadtree refinements,
and residual-based seeds are a finite adaptive realization, not an
implemented unbounded continuous atlas. The code's clipping stage should be
interpreted through SG-44 and its ridge refit through SG-43. Case-level
wall time is meaningful in the existing benchmark record; per-method runtime
fields that remain zero because of method-key bookkeeping do not supply
valid method timing comparisons.
''')
section('A closed four-jump calculation',r'''
Take a bandlimited background
\[
 s(x)=\frac14+\frac25\cos(2x)-\frac13\sin(3x)+\frac15\cos(5x)
\]
and a mean-zero edge with locations and jumps
\[
 (\tau_\ell)=(0,\pi/2,\pi,3\pi/2),\qquad
 (a_\ell)=(1,-2,-1,2).
\]
The physical nodes are $(1,-i,-1,i)$. Their derivative moments are
\[
 m_n=1-2(-i)^n-(-1)^n+2i^n,
\]
so in residues modulo four they are
\[
 m_{4q}=0,\quad m_{4q+1}=2+4i,\quad
 m_{4q+2}=0,\quad m_{4q+3}=2-4i.
\]
Since the smooth degree is five, the first clean consecutive moment is
$n_0=6$. With an order bound four, coefficients at $n=6,\ldots,13$ determine
the edge. The Hankel factorization has four distinct nodes and four nonzero
amplitudes, hence rank four. Its recurrence is
$m_{n+4}-m_n=0$, with monic polynomial $Q(z)=z^4-1$.
Recovering those roots and solving the Vandermonde system returns the displayed
jumps. SG-21 then constructs the edge, and coefficients at $-5,\ldots,5$
return the smooth background.

The same object demonstrates internal phase recovery. Choose $N=3$ and
$q_0=2$. The nodes are permuted by cubing, so the aliased nodes remain distinct.
The sufficient self-calibration sets for $L_{\max}=4$ are
\[
 \mathcal I_0=\{6,9,12,15,18,21,24,27,30\},\qquad
 \mathcal I_1=\{7,10,13,16\}.
\]
For each matched term the base coefficient is
$b_{\ell,0}=a_\ell z_\ell^6$, and the adjacent coefficient is
$b_{\ell,1}=b_{\ell,0}z_\ell$. Their ratio is the original physical node,
not the principal cube root. The total high budget is thirteen, agreeing with
$3L_{\max}+1$. The un-decimated construction uses eight high coefficients;
the polyphase construction trades additional channel information for its
chosen decimation geometry and branch recovery. Neither budget is claimed
minimal. Both reconstruct the same canonical object exactly.
''')
section('Evidence, implementations, and unresolved scope',r'''
\subsection{Current finite checks}
The current release replay contains ten bounded suites with 288 recorded
checks. After excluding the seven repeated checks in the SPD variant of the
same infinite-packet tests, the count is 281 distinct recorded checks under
the stated counting convention. A named check can compare a whole vector or
family; these numbers are neither theorem counts nor claims of independent
proofs. The manifests include source hashes, fixed seeds or deterministic
inputs, tolerances, resource limits, and scientific result records.

\begin{center}\small
\begin{tabular}{lrr}
\toprule Suite & Recorded checks & Counted distinct checks\\\midrule
Exact invariants & 134 & 134\\
Unknown edge & 24 & 24\\
Self-calibration & 31 & 31\\
Singularity dictionary & 26 & 26\\
Gibbs case & 8 & 8\\
Complex benchmark & 23 & 23\\
Infinite packet & 7 & 7\\
Infinite packet SPD & 7 & 0\\
Rank-aware execution copy & 16 & 16\\
Rank-ratio boundary & 12 & 12\\\midrule
Total & 288 & 281\\\bottomrule
\end{tabular}\normalsize\end{center}

The controlled finite-recovery checks pass in their printed ranges and
tolerances. The replay also reproduces two recovery failures, and its status
explicitly includes them. In the localized-burst signal the true order six
is inferred as nine. Location and jump comparison errors are nonfinite
because there is no same-cardinality match, while reconstructed waveform
RMSE remains finite and improved. Improved waveform error therefore does not
establish correct edge identification. The rank-ratio witness in Section 7
returns order two rather than three under the native heuristic, although the
supplied-threshold rule returns three.

An initial replay check mistakenly required every complex stress example to
have correct order and finite parameter errors. It failed on the burst case.
That failed record is retained. The follow-up uses the actual scientific
scope: controlled examples pass their recovery criteria and stress failures
are reported as failures. The scientific claim was narrowed; the burst
outcome was not changed or hidden.

The self-calibration replay includes one hundred deterministic separated
random cases with correct order in the tested settings. The archived wider
benchmark figures and natural-image comparisons remain historical finite
evidence unless their particular experiment is covered by a fresh manifest.
A bounded current replay is not a universal probability statement and does
not formalize the Python implementation.

\subsection{Executable boundaries and a separate repaired copy}
The original unknown-edge implementation's generic background projector uses
an unpivoted reduced QR construction. Its usual full-column-rank design is
appropriate, but dependent background columns need numerical-rank handling.
The original restricted-singular-value helper also needs an explicit zero
case for supports wider than the number of residual rows. A separate
rank-aware execution copy supplies those two local repairs and has sixteen
finite regression controls. The immutable source payload is preserved;
the repair provenance records the changed copy and its hashes.

The zero-edge signal is a valid trivial branch of SG-22 and SG-34. The
nonconstant native edge-model interface does not thereby acquire a zero-edge
wrapper. Exact model assertions and accepted input domains of a program are
listed separately. Floating-point root, rank, and amplitude tolerances are
finite checks, not exact kernel certificates.

\subsection{Formal coverage}
The included related Paper V checkpoint contains 225 theorem declarations
in twenty-three theorem-bearing modules. It supports packet, mask, polyphase,
finite transfer, and known-edge reconstruction infrastructure under its own
printed types. It is an earlier intact checkpoint, and its inherited logs
belong to that checkpoint. It does not certify the July unknown-edge and
self-calibration claims of this paper. The Lean guide maps each SG result to
related infrastructure or an explicit uncovered formalization obligation.
No Signal-specific Lean proof or fresh Lean compilation is claimed in this
edition. The manuscript proofs and the finite numerical evidence remain
separate from that formal coverage.

\subsection{What the paper closes}
For a bandlimited periodic background plus finitely many distinct off-grid
jumps, finitely many exact Fourier coefficients recover the complete canonical
signal. Under a supplied noncolliding decimation, adjacent offsets internally
recover physical phase with a stated finite budget. Under uniform local
conditioning and a strict branch margin, smooth Fourier tails yield the
printed conditional location and amplitude rates. Native edge synthesis
removes the edge's global-truncation error, and SG-37 supplies a valid
mean-zero periodic $L^1$ perturbation estimate.

\subsection{What remains open here}
The paper does not provide model-free unknown-edge recovery, a universal
noise bound without conditioning, an automatic proof that an empirical order
heuristic meets the rank-threshold gate, or a data-only root enclosure from
arbitrary noisy Fourier coefficients. It does not guarantee that every finite
decimation search contains a noncolliding candidate. General piecewise-smooth
backgrounds can imitate extra edges. Continuous arbitrary two-dimensional
boundaries need a geometry-adaptive identifiability and approximation theorem.
A sparse convergent adaptive infinite grammar needs a selection theorem,
not just a dense candidate description or a truth-residual archive.

These boundaries are mathematical distinctions exposed by the proofs and
negative controls. They guide the next work: robust unknown-order selection,
validated root enclosures, model-mismatch control, and adaptive geometry with
a measured-data observation model.
''')
parts.append(r'''
\appendix
\section{Reading the source and claim concordance}
Every SG result has a stable identifier, a domain, printed hypotheses,
a statement and proof, dependency identifiers, and hash-pinned source
lineage in \texttt{Claim\_Concordance.json}. Source-section labels identify
the inherited mathematical material; a lineage anchor is not an assertion
that every sentence of the new proof appeared verbatim in that source.
The CSV is a compact index of the same results. Reconstructed proofs and
publication corrections are marked explicitly. All SG results are
manuscript results rather than Signal-specific Lean-certified declarations.

The bundle includes the full \texttt{.md} manuscript files, editable
\LaTeX{} sources, Python implementations and figure generators, original
source archives, related Lean sources, fresh and inherited verification
records, and the two companion guides. The raw inherited manuscripts are
retained alongside the corrected edition so that changes remain reviewable.

\section{Principal proof dependencies}
SG-01--SG-06 supply exact finite coordinates, transfer multiplication,
polyphase kernels, and alias arithmetic. SG-07--SG-08 state the
identifiability boundaries. Known-edge reconstruction SG-09--SG-11 precedes
the Gibbs profile SG-12 and positive averaging SG-13. Finite dictionary
recovery follows the kernel-secant path SG-14 to SG-15; SG-16 gives the
one-packet profiled search and its independent finite gap.

The off-grid chain is differentiation SG-18, Hankel rank SG-19,
annihilation SG-20, canonical integration SG-21, and complete recovery
SG-22. SG-23--SG-26 quantify its perturbed linear and root steps.
Self-calibration uses SG-27's offset identity and SG-28's supplied threshold,
then SG-29--SG-33 for phase and branch control. SG-34 is the exact finite
budget; SG-35 is the conditional asymptotic theorem. SG-36--SG-38 return
those parameters to a normed signal with the corrected mean-zero edge bound.
SG-39--SG-41 extend only the declared shared-edge, confluent, and dictionary
contracts. SG-42--SG-46 keep ideal projection, ridge, clipping, residual
storage, and completion as separate operations.

\clearpage
\begin{thebibliography}{9}
\bibitem{stewart} G. W. Stewart.
Perturbation Theory for the Singular Value Decomposition.
UMIACS-TR-90-124 / CS-TR-2539, September 1990, Section 2, Theorem 1.
\url{https://drum.lib.umd.edu/bitstreams/a38cc6db-9bb7-4f3b-ae43-55b5827bb9d4/download}.
\bibitem{vexpa} M. Briani, A. Cuyt, F. Knaepkens, and W.-s. Lee.
VEXPA: Validated EXPonential Analysis through regular sub-sampling.
\emph{Signal Processing} 177 (2020), 107722.
\url{https://doi.org/10.1016/j.sigpro.2020.107722}.
\bibitem{batenkov} D. Batenkov.
Complete algebraic reconstruction of piecewise-smooth functions from Fourier data.
\emph{Mathematics of Computation} 84 (2015), 2329--2350.
\url{https://doi.org/10.1090/S0025-5718-2015-02948-2}.
\bibitem{sparse} D. L. Donoho and M. Elad.
Optimally sparse representation in general (nonorthogonal) dictionaries
via $\ell^1$ minimization. \emph{PNAS} 100 (2003), 2197--2202.
\url{https://doi.org/10.1073/pnas.0437847100}.
\bibitem{rouche} J. Lebl. \emph{Guide to Cultivating Complex Analysis:
Working the Complex Field}, version 1.9, July 11, 2026,
Section 5.4.2. \url{https://www.jirka.org/ca/ca.pdf}.
\bibitem{fri} M. Vetterli, P. Marziliano, and T. Blu.
Sampling Signals with Finite Rate of Innovation.
\emph{IEEE Transactions on Signal Processing} 50 (2002), 1417--1428.
\url{https://doi.org/10.1109/TSP.2002.1003065}.
\end{thebibliography}
The finite-rate paper is cited for historical attribution. Exact sampling
hypotheses from it are not imported: the consecutive-moment theorem is
proved directly in this manuscript. The literature review records the
checked versions and the limits of the source search. No global novelty
claim follows from that search.
''')

PREAMBLE=r'''\documentclass[11pt]{article}
\usepackage[letterpaper,margin=0.9in,headheight=15pt]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amsthm,amssymb,mathtools}
\IfFileExists{newtxtext.sty}{\usepackage{newtxtext,newtxmath}}{\usepackage{lmodern}}
\usepackage{microtype,booktabs,longtable,tabularx,array,enumitem,xcolor,fancyhdr,titlesec,xurl}
\usepackage{hyperref}
\definecolor{Navy}{HTML}{17324D}\definecolor{Teal}{HTML}{2F7A78}
\hypersetup{colorlinks=true,linkcolor=Navy,urlcolor=Teal,citecolor=Teal,
pdfauthor={Komorebi P.},pdftitle={Signal Reconstruction: Polyphase Sampling, Unknown Edges, and Self-Calibration}}
\setlength{\parindent}{0pt}\setlength{\parskip}{4.5pt}
\setlist{itemsep=2pt,topsep=3pt,leftmargin=1.7em}
\allowdisplaybreaks\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small\textsc{Signal Reconstruction}}
\fancyhead[R]{\small Komorebi P.}\fancyfoot[C]{\thepage}
\titleformat{\section}{\Large\bfseries\color{Navy}}{\thesection}{0.7em}{}
\titleformat{\subsection}{\large\bfseries\color{Navy}}{\thesubsection}{0.6em}{}
\newtheorem{theorem}{Theorem}[section]
\theoremstyle{definition}\newtheorem{definition}[theorem]{Definition}
\theoremstyle{remark}\newtheorem{remark}[theorem]{Remark}
\begin{document}\hypersetup{pageanchor=false}
\begin{titlepage}\vspace*{0.8in}
{\color{Teal}\large\textsc{Komorebi\quad Realization Calculus}\par}
\vspace{0.35in}{\color{Navy}\Huge\bfseries Signal Reconstruction\par}
\vspace{0.25in}{\LARGE Polyphase Sampling, Unknown Edges,\\[5pt] and Self-Calibration\par}
\vspace{0.6in}{\Large Komorebi P.\par}
\vspace{0.15in}{\large Final edition\quad October 6, 2026\par}
\vfill\begin{minipage}{0.92\textwidth}
\textbf{Reading set.} Traditional paper, visual guide, Lean guide, and complete
source bundle. The bundle includes the \texttt{.md} files, editable manuscript
sources, Python implementations, exact figure generators, related Lean
sources, and verification records.\par\medskip
\textbf{Scope.} Exact finite-rate edge recovery and native synthesis;
conditional noisy and smooth-tail recovery; finite geometric dictionaries;
and explicitly separated adaptive image approximation.
\end{minipage}\end{titlepage}
\hypersetup{pageanchor=true}\pagenumbering{arabic}
\begin{abstract}
Finite signal reconstruction depends on a declared model and an injective
observation. This paper develops a packet-based reconstruction chain from
complete projector coordinates and transfer kernels to exact off-grid jump
recovery, polyphase alias calibration, and native singularity synthesis.
Consecutive differentiated Fourier moments determine an unknown finite jump
count through Hankel rank, followed by an annihilating polynomial and
Vandermonde recovery. Matched adjacent offsets recover the physical phase
lost by decimation. Noisy order, root, and branch conclusions retain explicit
conditioning and margin gates, with conditional asymptotic rates.
A corrected periodic mean-zero jump estimate controls edge synthesis in
$L^1$. Classical Gibbs ringing is derived and localized to the globally
truncated edge block. Finite dictionaries and adaptive image experiments are
kept distinct from universal continuous-edge recovery. The current numerical
replay includes successful controlled checks and reproduced identification
failures. Related Lean infrastructure is mapped without claiming a formal
certificate for the new recovery chain.
\end{abstract}
\tableofcontents\newpage
'''

def assemble():
 if [r['claim_id'] for r in claims]!=[f'SG-{i:02d}' for i in range(1,len(claims)+1)]:raise ValueError('noncontiguous IDs')
 ids={r['claim_id'] for r in claims}
 for row in claims:
  for dep in row['dependencies']:
   if dep not in ids:raise ValueError(dep)
  row['source_anchors']=row['anchors']
 tex=PREAMBLE+'\n'.join(parts)+'\n\\end{document}\n'
 (HERE/'Signal_Reconstruction_Traditional.tex').write_text(tex)
 payload={'schema':'komorebi.signal_claim_concordance.v1','edition':'2026-10-06','title':'Signal Reconstruction: Polyphase Sampling, Unknown Edges, and Self-Calibration','interpretation':'Principal manuscript result groups. These are not independent novelty claims or Signal-specific Lean-certified declarations.','claims':claims}
 (HERE/'Claim_Concordance.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
 fields=['claim_id','title','domain','hypotheses','status','evidence','document_label','lean_status','dependencies','source_files','source_labels','source_hashes','scope_repair']
 with (HERE/'Claim_Concordance.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for row in claims:
   out={k:row[k] for k in fields if k in row}
   out.update(dependencies=';'.join(row['dependencies']),source_files=';'.join(a['file'] for a in row['anchors']),source_labels=';'.join(a['label'] for a in row['anchors']),source_hashes=';'.join(a['source_sha256'] for a in row['anchors']))
   w.writerow(out)
 # Pandoc receives the same substantive body, with theorem/proof wrappers
 # changed to ordinary headings so no custom environment is dropped.
 mdtex='\n'.join(parts)
 mdtex=re.sub(r'\\begin\{theorem\}\[(SG-\d+)\\quad ([^\]]+)\]\\label\{[^}]+\}',lambda m:r'\subsection*{'+m[1]+': '+m[2]+'}',mdtex)
 mdtex=mdtex.replace(r'\end{theorem}','').replace(r'\begin{proof}',r'\paragraph{Proof.}').replace(r'\end{proof}','')
 mdtex=mdtex.replace(r'\begin{thebibliography}{9}',r'\section*{References}').replace(r'\end{thebibliography}','')
 mdtex=re.sub(r'\\bibitem\{([^}]+)\}',lambda m:r'\paragraph{['+m[1]+']}',mdtex)
 mdtex=r'\documentclass{article}\usepackage{amsmath,amssymb,hyperref,xurl,xcolor,booktabs}\begin{document}'+mdtex+r'\end{document}'
 mdproc=subprocess.run(['pandoc','-f','latex','-t','markdown+tex_math_dollars','--wrap=none','--shift-heading-level-by=1'],input=mdtex,text=True,capture_output=True,check=True)
 md='# Signal Reconstruction\n\n## Polyphase Sampling, Unknown Edges, and Self-Calibration\n\n**Komorebi P. — Final edition, October 6, 2026**\n\nThe source bundle includes the `.md` files. This manuscript contains complete statements and proofs. SG results are manuscript proofs, not Signal-specific Lean-certified declarations.\n\n'+mdproc.stdout
 md=re.sub(r'\n:::.*?\n','\n',md)
 md=re.sub(r' \{#[^}]+\}', '', md)
 md=re.sub(r'^#+ Proof\.$', '**Proof.**', md, flags=re.M)
 md=re.sub(r'\$\$(.*?)\$\$', lambda m:'\n\n$$\n'+m[1].strip()+'\n$$\n\n', md, flags=re.S)
 md=md.replace('[@vexpa]','[VEXPA 2020](https://doi.org/10.1016/j.sigpro.2020.107722)').replace('[@stewart]','[Stewart 1990](https://drum.lib.umd.edu/bitstreams/a38cc6db-9bb7-4f3b-ae43-55b5827bb9d4/download)')
 md=re.sub(r'\n{3,}','\n\n',md)
 (HERE/'Signal_Reconstruction_Traditional.md').write_text(md)
 print(json.dumps({'claims':len(claims),'source_anchors':sum(len(r['anchors']) for r in claims),'tex_bytes':len(tex.encode()),'md_bytes':len(md.encode())}))

if __name__=='__main__':assemble()
