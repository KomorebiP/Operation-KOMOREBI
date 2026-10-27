from pathlib import Path
import hashlib,json,shutil,difflib
R=Path('release_package/Komorebi_Paper_II_Release_2026-10-15');A=Path('paper2_work/audit');B=Path('paper2_work/editorial_before')
changes=[];original={};working={}
def edit(rel,before,after,ref,kind='mathematical clarification'):
 p=R/rel
 if rel not in original:original[rel]=p.read_text();working[rel]=original[rel]
 assert working[rel].count(before)==1,(ref,rel,working[rel].count(before))
 working[rel]=working[rel].replace(before,after)
 changes.append(dict(source=rel,audit_finding=ref,kind=kind,before=before,after=after))
p='editable/traditional/chapters/01_orientation.tex'
edit(p,r'\section{Four kinds of depth}',r'\section{Depth and compatibility}', 'PUB-03','terminology')
edit(p,'Several quantities below are measured by nonnegative integers.  They do not measure the same thing.  Keeping them separate makes the later formulas easier to read.','Packet, filtration, and separation depths describe three different kinds of scale. Compatibility is initially recorded by an operator defect. Keeping these notions separate makes the later formulas easier to read.','PUB-03','terminology')
edit(p,r'The second is filtration depth.  A transfer in $F^r\Bcal$ is invisible modulo $F^r\Bcal$ and becomes visible at greater precision.  Two paths with the same number of edges can have different filtration depths.  A longer path can appear earlier when its edges have smaller weights.',r'The second is filtration depth. A transfer in $F^r\Bcal$ vanishes modulo $F^r\Bcal$. This membership gives a lower bound on its depth. A nonzero transfer may first become visible only at a higher precision. Two paths with the same number of edges can have different filtration depths. A longer path can appear earlier when its edges have smaller weights.','PUB-02')
edit(p,'The fourth is compatibility depth.  A fine operator and a separately chosen coarse operator need not commute with coarsening.  Their discrepancy is','The fourth notion is the compatibility defect. A fine operator and a separately chosen coarse operator need not commute with coarsening. Their discrepancy is','PUB-03','terminology')
edit(p,'This is not a packet depth or a denominator.  It measures the failure of one operator model to represent another exactly.','This operator records the failure of one model to represent another exactly. A chosen norm measures its size, while a chosen filtration can assign a depth. No integer compatibility depth is assigned without that additional structure.','PUB-03')
edit(p,'Compatibility depth measures a discrepancy between two operator models.','The compatibility defect records a discrepancy between two operator models.','PUB-03','terminology')
edit(p,'A simple two packet model already contains all four ideas.','A simple two packet model already contains all four notions.','PUB-03','terminology')
p='editable/traditional/chapters/02_coordinates.tex'
edit(p,r'''that satisfy the composition law for successive levels. The next result shows that the coordinate changes form a coherent system.''',r'''such that $\Pcal_m$ refines $\Pcal_\ell$ through $\rho_{m,\ell}$ for every $m\geq\ell$, and
\[
\rho_{\ell,\ell}=\id_{I_\ell},
\qquad
\rho_{n,\ell}=\rho_{m,\ell}\circ\rho_{n,m}
\qquad(n\geq m\geq\ell).
\]
Thus every parent map witnesses the stated refinement and the maps compose coherently. The next result shows that the coordinate changes form a coherent system.''','coordinates F06')
edit(p,'If $X$ is a Hilbert space and every packet system in the tower consists of orthogonal projections, then analysis and synthesis are unitary.  Every coordinate change in \\cref{thm:coordinate_coherence} is unitary.',r'If $X$ is a real or complex Hilbert space and every packet system in the tower consists of orthogonal projections, equip each finite packet direct sum with the Hilbert inner product $\langle(x_\alpha),(y_\alpha)\rangle=\sum_\alpha\langle x_\alpha,y_\alpha\rangle$. Then analysis and synthesis are unitary. Every coordinate change in \cref{thm:coordinate_coherence} is unitary.','coordinates F09')
edit(p,'systems on $Y$, and let $T:X\\to Y$ be a typed linear map. Its exact coordinate','systems on $Y$, where $X$ and $Y$ are modules over the same scalar ring, and let $T:X\\to Y$ be a linear map over that ring. Its exact coordinate','coordinates F09')
edit(p,'and the same argument works for a fixed $\\beta$.  Iteration proves the finite family statement.',r'''and the same argument works for a fixed $\beta$. Since each $P_\alpha$ and $Q_\beta$ is nonzero, these identities ensure that every parent has a nonzero product child. The two parent maps on the supported product family are therefore surjective. Iteration proves the finite family statement. For the empty collection, use the supported identity family: $(I_X)$ when $X\ne0$ and the empty family when $X=0$.''','coordinates F08')
edit(p,'Every packet of $\\Rcal$ lies in one product packet.  Summing the packets with the same pair of parents reconstructs that product packet.',r'''Every packet of $\Rcal$ lies in one product packet. Multiplying $\sum_\gamma R_\gamma=I_X$ by $P_\alpha Q_\beta$ and using the parent identities gives
\[
P_\alpha Q_\beta
=\sum_{\substack{\gamma:\ P_\alpha R_\gamma=R_\gamma\\Q_\beta R_\gamma=R_\gamma}}R_\gamma.
\]
Thus the packets with the same pair of parents reconstruct the product packet. If that product packet is nonzero, the sum has a child, so the parent map onto the supported product family is surjective.''','coordinates F08')
edit(p,'The four coordinate projections form a fine packet system.','Assume that all four summands are nonzero. The four coordinate projections form a fine packet system.','coordinates F07')
edit(p,'Let $U$ act on coefficient sequences by',r'The coefficient-mask definition of $P_{N,j}$ also makes sense over a commutative semiring: it only retains or sets coefficients to zero. We use that same definition in the following semiring statement.'+'\n\n'+'Let $U$ act on coefficient sequences by','coordinates F09')
edit(p,r'\begin{example}[The shift graph of residue packets]\label{ex:residue_shift}'+'\n'+'Multiplication by $z$',r'\begin{example}[The shift graph of residue packets]\label{ex:residue_shift}'+'\n'+'Assume that $R$ is nonzero and $N>0$. Multiplication by $z$','coordinates F07')
p='editable/traditional/chapters/03_weighted.tex'
edit(p,r'A transfer term $N_e$ has declared weight $w(e)\geq1$ when',r'A transfer term $N_e$ has a declared positive integer weight $w(e)\in\mathbb Z_{>0}$ when','W-WEIGHT-TYPE')
edit(p,r'''If $\OO$ is a complete discrete valuation ring with uniformizer $\pi$, the filtration
\[
F^L\Bcal=\pi^L\Bcal
\]
is the standard example.  Basic facts about completeness in this setting are reviewed in \cite{Serre1979}.''',r'''In the filtration topology, reduction to $\Bcal/F^L\Bcal$ is continuous when the quotient has the discrete topology. Its kernel $F^L\Bcal$ is therefore closed. In particular, a convergent sum of terms in $F^L\Bcal$ remains in that ideal.

If $\OO$ is a complete discrete valuation ring with uniformizer $\pi$ and $\Bcal$ is a separated and complete $\OO$ algebra for the filtration
\[
F^L\Bcal=\pi^L\Bcal,
\]
then this is a standard example. Finite matrix algebras over $\OO$ satisfy these conditions. Completeness of $\OO$ alone does not imply completeness of every $\OO$ algebra. Basic facts about completeness in this setting are reviewed in \cite{Serre1979}.''','W-DVR-COMPLETE; W-CLOSURE')
edit(p,r'''on an $\OO$-algebra $\cB$. Suppose''',r'''on an $\OO$-algebra $\cB$. The finite quotient statements below do not require $\cB$ itself to be complete. Suppose''','W-DVR-COMPLETE')
edit(p,r'''where $a_n$ is the total multiplicity of paths from the vertices selected by $u$ to the vertices selected by $v$ with total weight $n$.''',r'''where
\[
a_n=\sum_{i,j}\ \sum_{\substack{\gamma:i\leadsto j\\W(\gamma)=n}}
 u_i v_j\prod_{\nu=1}^{|\gamma|}m(e_\nu).
\]
Here $\gamma=(e_1,\ldots,e_{|\gamma|})$ is a directed walk. Vertices and edges may repeat, and the empty walk has weight zero and multiplicity one. Thus the endpoint vectors weight the start and end of each walk, rather than only selecting subsets of vertices.''','PUB-04; W-DEF-ENDPOINTS')
edit(p,r'''Then, for every $n>\deg P$,''',r'''Use the convention $\deg 0=-\infty$. Then, for every nonnegative integer $n>\deg P$,''','W-DEG-ZERO')
edit(p,r'''$Q$ after the finite initial range contributed by $P_{s,t}$:''',r'''$Q$ after the finite initial range contributed by $P_{s,t}$, with $\deg 0=-\infty$:''','W-DEG-ZERO')
p='editable/traditional/atlas_macros.tex'
edit(p,r'\pdfbookmark[1]{V#1. #2}{plate#1}\hypertarget{vpage#1}{}\label{visual:#1}',r'\pdfbookmark[1]{V#1. #2}{plate#1}\hypertarget{vpage#1}{}\phantomsection\label{visual:#1}','PUB-06','navigation-only')
p='editable/traditional/chapters/06_models.tex'
edit(p,'For $N=2$ and $k=1$,\n\\[','For $N=2$ and $k=1$,\n\\phantomsection\n\\[','PUB-06','navigation-only')
file_logs=[]
for rel,text in working.items():
 p=R/rel;back=B/rel;back.parent.mkdir(parents=True,exist_ok=True)
 assert not back.exists(),str(back)
 back.write_text(original[rel]);p.write_text(text)
 file_logs.append({'path':rel,'before_sha256':hashlib.sha256(original[rel].encode()).hexdigest(),'after_sha256':hashlib.sha256(text.encode()).hexdigest()})
log={'schema':'komorebi.paper_ii.editorial_wave1.v1','status':'APPLIED_PENDING_REVIEW_AND_PDF_BUILD','authorization':'Root approved specified findings on 2026-10-15; no final coverage/status edits authorized in this wave.','pdf_authoring_marker':{'operation_kind':'edit','expected_output_count':3,'output_format':'pdf','run_once':True,'exit_code':0},'changes':changes,'files':file_logs,'source_and_formal_preservation':'No source/ historical files or formal/current files changed.','validation':'Each before fragment matched exactly once. Changed hunks reread. No PDF build yet.'}
(A/'editorial_wave1.json').write_text(json.dumps(log,indent=2)+'\n')
(A/'editorial_wave1.diff').write_text(''.join(''.join(difflib.unified_diff(original[rel].splitlines(True),text.splitlines(True),fromfile='before/'+rel,tofile='after/'+rel)) for rel,text in working.items()))
print(json.dumps({'files':len(working),'changes':len(changes),'log':str(A/'editorial_wave1.json')},indent=2))
