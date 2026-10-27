from pathlib import Path
import re, json, hashlib
ROOT=Path('/mnt/data/Komorebi_Space_Monograph_v1.7.0')
CH=ROOT/'source/chapters'
changes=[]

def proof(file,label,new,reason):
 p=CH/file;s=p.read_text();pos=s.index('\\label{'+label+'}')
 start=s.index('\\begin{proof}',pos);end=s.index('\\end{proof}',start)+len('\\end{proof}')
 old=s[start:end];new='\\begin{proof}\n'+new.strip()+'\n\\end{proof}'
 assert '\\begin{theorem}' not in s[pos:start] and '\\source{' not in s[pos:start],label
 s=s[:start]+new+s[end:];p.write_text(s)
 changes.append({'id':label,'file':str(p.relative_to(ROOT)),'change':'expanded proof','focus':reason,'old_words':len(old.split()),'new_words':len(new.split()),'old_proof_sha256':hashlib.sha256(old.encode()).hexdigest(),'new_proof_sha256':hashlib.sha256(new.encode()).hexdigest()})

def replace(file,old,new,reason,label):
 p=CH/file;s=p.read_text();assert old in s,(file,old[:60]);assert s.count(old)==1,(file,'ambiguous')
 p.write_text(s.replace(old,new));changes.append({'id':label,'file':str(p.relative_to(ROOT)),'change':reason,'old_words':len(old.split()),'new_words':len(new.split())})

proof('01_views.tex','KS01',r'''
We first verify that the evaluation maps themselves form a compatible family. If $x\in\Gamma(F)$ and $f:v\to w$, the defining equation for $x$ gives
\[
 f^*(\operatorname{ev}_w x)=f^*(x_w)=x_v=\operatorname{ev}_v x.
\]
If $x,y\in\Gamma(F)$ have equal evaluations, then $x_v=y_v$ for every $v$. Equality of functions into a dependent product gives equality of their underlying families. Membership in $\Gamma(F)$ is a property of a family, not a further choice of coordinate. Thus $x=y$.

Now fix the compatible maps $c_v:T\to F_v$. For each $t\in T$ define a family by $x(t)_v=c_v(t)$. For every arrow,
\[
 f^*x(t)_w=f^*c_w(t)=c_v(t)=x(t)_v.
\]
This calculation verifies membership in $\Gamma(F)$, so the rule $c(t)=x(t)$ defines an actual function $c:T\to\Gamma(F)$. Evaluating it gives $\operatorname{ev}_vc(t)=c_v(t)$, as required.

To prove uniqueness, let $b:T\to\Gamma(F)$ be another such function. At every $t$ and $v$,
\[
 (b(t))_v=\operatorname{ev}_v b(t)=c_v(t)=\operatorname{ev}_v c(t).
\]
Joint determination first yields $b(t)=c(t)$, and function extensionality then yields $b=c$. Nothing in this argument assumes that $T$ or $\Gamma(F)$ is inhabited. For example, when $T$ is empty there is the unique empty function. When $T$ is inhabited, existence of the compatible family $(c_v)$ is already substantive data.''','Construct the lift, verify coherence, and separate two extensionality arguments, including empty domains.')

proof('01_views.tex','KS04',r'''
\emph{Step 1: every coordinate can be selected.} Apply the cover condition to the identity arrow of $v$. It gives an index containing $v$. Choose one such index $i(v)$ and put
\[
 x_v=(s_{i(v)})_v.
\]
The choice is an existence construction. It is not an algorithm selecting patches in a preferred order. If $v\in U_j$, matching on the overlap $U_{i(v)}\cap U_j$ gives
\[
 x_v=(s_j)_v.                                                   \tag{*}
\]
In particular the value is independent of the selected index.

\emph{Step 2: the selected coordinates satisfy every arrow equation.} For $f:v\to w$, choose a single index $j$ with $v,w\in U_j$. Formula (*) applies to both endpoints. Since the patch is full, it contains this actual arrow, even when other arrows have the same endpoints. Coherence of $s_j$ gives
\[
 f^*x_w=f^*(s_j)_w=(s_j)_v=x_v.
\]
Thus $x\in\Gamma(F)$. Object coverage alone would not supply the common patch used in this step.

\emph{Step 3: assembly and restriction are inverse.} Formula (*) proves $x|_{U_j}=s_j$ for every $j$. Conversely, start with $y\in\Gamma(F)$ and assemble its restrictions. The resulting coordinate at $v$ is $y_v$, regardless of which containing patch is chosen. Joint determination gives the original $y$. These two identities are exactly the inverse identities for the displayed equivalence.

For uniqueness with a fixed matching family, any other glue has coordinate $(s_{i(v)})_v=x_v$ at every $v$, hence equals $x$. If the view category is empty, its product has one empty family and the same conclusion follows without making any choices.''','Make object coverage, arrow coverage, choice independence and both inverse maps explicit.')

proof('01_views.tex','KS06',r'''
We must first check that the displayed fibers really form a view system. Let $m\in B_{a,b}(w)$ and $f:v\to w$. Naturality of $p$ and coherence of $a$ give
\[
 p_v(f_M^*m)=f_F^*p_w(m)=f_F^*a_w=a_v.
\]
The same calculation with $q,b$ gives $q_v(f_M^*m)=b_v$. Therefore $f_M^*m$ belongs to $B_{a,b}(v)$. Identity and composition of these restricted maps are inherited from $M$, because equality in a subset is equality of its underlying elements.

Given $u\in\Gamma(B_{a,b})$, forget each fiber-membership condition and call the underlying family $z_v\in M_v$. Coherence of $u$ is precisely coherence of $z$, so $z\in\Gamma(M)$. The equations $p_vz_v=a_v$ hold at every coordinate. Joint determination in $\Gamma(F)$ yields $\Gamma(p)z=a$, and the equations for $q$ similarly yield $\Gamma(q)z=b$. Thus $z$ is a global bridge.

In the opposite direction, let $z\in\mathfrak B(a,b)$. Evaluate its two global projection equations at $v$. They show that $z_v$ belongs to $B_{a,b}(v)$, and its original coherence shows that these elements form a section of the fiber system. Forgetting and reattaching membership conditions preserves every coordinate, so the two constructions are inverse.

Finally apply strict gluing to this specific fiber system. The glued section retains its membership in every $B_{a,b}(v)$, which is why both prescribed projections survive gluing. Uniqueness is for the fixed matching bridge family. Different matching families for the same $(a,b)$ can still yield different global bridges.''','Verify the bridge restriction maps before using the gluing theorem and retain both projection equations.')

proof('02_obstructions.tex','KS09',r'''
Let $\pi_U:R\to R/B_U$ be the quotient homomorphism. By the definition of a quotient by a subgroup,
\[
 \pi_U(r)=0\quad\Longleftrightarrow\quad r\in B_U.
\]
Here $B_U$ is the \emph{image} of $\ker p_U$ under $\delta$. Consequently membership of $\delta\widetilde s$ means the existence of a specific $h\in E$ satisfying both $p_Uh=0$ and $\delta h=\delta\widetilde s$. The subgroup need not be closed in any topology. No topology has been introduced.

If such $h$ exists, set $x=\widetilde s-h$. Additivity gives the two equations separately:
\[
 \delta x=\delta\widetilde s-\delta h=0,
 \qquad p_Ux=p_U\widetilde s-p_Uh=s.
\]
The first equation puts $x$ in $\Gamma(A)$, and the second puts that coherent family in $\Ext_U(s)$.

Conversely, take $x\in\Ext_U(s)$ and set $h=\widetilde s-x$. Since both raw families restrict to $s$, one has $p_Uh=0$. Since $\delta x=0$, one has $\delta h=\delta\widetilde s$. This witnesses $\delta\widetilde s\in B_U$, hence vanishing of its quotient class.

The proof is independent of the selected raw lift. Indeed, if $\widetilde s'$ is another lift, $k=\widetilde s'-\widetilde s$ lies in $\ker p_U$, and
\[
 \delta\widetilde s'-\delta\widetilde s=\delta k\in B_U.
\]
Thus the two quotients agree before either feasibility direction is invoked. A raw lift always exists in this additive model by using zero outside $U$. Constructing a raw lift does not solve the coherence equations.''','Unpack image membership, lift independence and both protected correction equations.')

proof('02_obstructions.tex','KS10',r'''
Define $\Theta:H_U\to\Ext_U(s)$ by $\Theta(h)=x_0+h$. It lands in the extension set because
\[
 \delta(x_0+h)=\delta x_0+\delta h=0,
 \qquad p_U(x_0+h)=s+0=s.
\]
Define $\Psi:\Ext_U(s)\to H_U$ by $\Psi(x)=x-x_0$. Its differential is zero, and its restriction is $s-s=0$, so the claimed target is correct. The formulas give
\[
 \Psi\Theta(h)=x_0+h-x_0=h,\qquad
 \Theta\Psi(x)=x_0+(x-x_0)=x.
\]
This proves the equivalence rather than only a comparison of cardinalities.

If $H_U=\{0\}$, the parameter of every extension is zero, so every extension equals $x_0$. Conversely, if $x_0$ is the only extension, then for any $h\in H_U$ the equality $x_0+h=x_0$ forces $h=0$ by cancellation. Combining this observation with the existence criterion proves the stated necessary and sufficient condition for a unique extension.

The choice of $x_0$ only supplies an origin for the parameters. If $x_1=x_0+h_1$ is used instead, the parameter of $x$ changes from $x-x_0$ to $x-x_1=(x-x_0)-h_1$. The affine set of answers itself has not changed.''','Give explicit inverse functions and explain dependence on the selected origin.')

proof('02_obstructions.tex','KS12',r'''
First verify that $\mathfrak o_U$ is a homomorphism, since exactness is being asserted in an additive setting. Given $s,t\in\Gamma_U(A)$, choose raw lifts $\widetilde s,\widetilde t$. Their sum lifts $s+t$. Lift independence and additivity imply
\[
 \mathfrak o_U(s+t)
 =[\delta(\widetilde s+\widetilde t)]
 =[\delta\widetilde s]+[\delta\widetilde t]
 =\mathfrak o_U(s)+\mathfrak o_U(t).
\]
The zero lift gives $\mathfrak o_U(0)=0$. Restriction $r_U$ is a homomorphism because addition of global sections is coordinatewise.

If $s=r_Ux$ for a global section $x$, use $x$ itself as a raw lift. Its differential vanishes, so $\mathfrak o_U(s)=0$. This proves $\im r_U\subseteq\ker\mathfrak o_U$. If $s\in\ker\mathfrak o_U$, the extension criterion constructs a global $x$ restricting to $s$, proving the reverse inclusion.

Finally, $r_U$ is surjective exactly when its image is all of $\Gamma_U(A)$. By the equality just proved, this is equivalent to every partial section having zero obstruction, which says that $\mathfrak o_U$ is the zero homomorphism. Nothing here claims that its image is all of $Q_U$.''','Prove homomorphism structure before exactness, rather than appealing only to a set-level criterion.')

proof('02_obstructions.tex','KS14',r'''
The image $d(\ker p)$ is a subgroup of $R$. The defining property of the quotient says
\[
 [dx]=0\quad\Longleftrightarrow\quad
 dx\in d(\ker p)
 \quad\Longleftrightarrow\quad
 \exists h\in E:\ ph=0,\ dh=dx.
\]
This is the first equivalence with its witness made explicit.

For the second, a permitted $h$ gives $y=x-h$. Then
\[
 dy=dx-dh=0,\qquad py=px-ph=px.
\]
Conversely an exact $y$ with $py=px$ gives $h=x-y$, which satisfies $ph=0$ and $dh=dx$. The two witness transformations are inverse: subtracting $h$ from $x$ and then subtracting that answer from $x$ recovers $h$, and conversely.

To verify invariance, fix any $h$ with $ph=0$. Then $d(x-h)=dx-dh$, and $dh$ lies in the subgroup divided out. Therefore $[d(x-h)]=[dx]$. This does not assert that the residual itself is unchanged. It asserts that permitted changes can alter the residual only within its already correctable coset.''','Display witness transformations and distinguish residual invariance from quotient invariance.')

proof('02_obstructions.tex','KS15',r'''
Suppose, for contradiction, that $dy=0$ and $py=px$. Then $h=x-y$ satisfies $ph=0$ and $dh=dx$. By the annihilation hypothesis,
\[
 L(dx)=L(dh)=0,
\]
contrary to the assumed nonzero value. This already proves impossibility directly.

Equivalently, if $r-r'\in d(\ker p)$, then $L(r-r')=0$, so $L(r)=L(r')$. Hence $\overline L([r])=L(r)$ is a well-defined homomorphism on $R/d(\ker p)$. Its value on $[dx]$ is nonzero. This supplies the quotient interpretation of the same contradiction, without assuming that every nonzero quotient class can be detected by a map into one fixed preferred coefficient group.''','Provide the direct contradiction and justify quotient descent without a converse separation claim.')

proof('03_towers.tex','KS18',r'''
Write $\rho_{i,j}:X_j\to X_i$ for the composite restriction when $i\le j$, with $\rho_{i,i}=I$. These maps satisfy $\rho_{i,j}\rho_{j,k}=\rho_{i,k}$. A coherent sampled point obeys
\[
 \rho_{\phi(n),\phi(m)}y_m=y_n\qquad(n\le m),
\]
by iterating its adjacent coherence equations.

For each $k$, unboundedness gives an index $n$ with $k\le\phi(n)$. Set $x_k=\rho_{k,\phi(n)}y_n$. If $m$ is another permissible index, choose $\ell\ge n,m$. Monotonicity permits both composite restrictions, and sampled coherence gives
\[
 \rho_{k,\phi(n)}y_n
 =\rho_{k,\phi(n)}\rho_{\phi(n),\phi(\ell)}y_\ell
 =\rho_{k,\phi(\ell)}y_\ell
 =\rho_{k,\phi(m)}y_m.
\]
Thus $x_k$ is independent of the choice, including when the schedule repeats a level.

For the adjacent equation at $k$, choose one $n$ with $k+1\le\phi(n)$. Then
\[
 \rho_{k,k+1}x_{k+1}
 =\rho_{k,k+1}\rho_{k+1,\phi(n)}y_n
 =\rho_{k,\phi(n)}y_n=x_k.
\]
The recovered family is therefore a point of the original tower.

Sampling a full point and recovering its $k$th coordinate gives $\rho_{k,\phi(n)}x_{\phi(n)}=x_k$ by its original coherence. Recovering a sampled point and evaluating at $k=\phi(n)$ allows the index $n$ itself, giving $\rho_{\phi(n),\phi(n)}y_n=y_n$. These are both inverse identities. No surjectivity of the bonding maps or of the point evaluations was used.''','Use composite restrictions explicitly, handle repeated schedule levels and give both inverse checks.')

proof('03_towers.tex','KS19',r'''
Put $r_m=df^{(m)}$. Additivity of $d$ gives
\[
 r_{m+1}=r_m-dAr_m.
\]
Each $r_m$ is the residual of an actual candidate, so the stated hypothesis applies at every iteration. Induction yields, for $j\ge0$,
\[
 \norm{r_{m+j}}\le q^j\norm{r_m},\qquad
 \norm{f^{(m+j+1)}-f^{(m+j)}}
 \le\norm A\,q^j\norm{r_m}.
\]
For $n>m$, the finite triangle inequality therefore gives
\[
 \norm{f^{(n)}-f^{(m)}}
 \le\norm A\,\norm{r_m}\sum_{j=0}^{n-m-1}q^j
 \le\frac{\norm A}{1-q}\norm{r_m}.
\]
Since $\norm{r_m}\le q^m\norm{df}$ tends to zero, this is a Cauchy estimate. Completeness of $E$ supplies a limit, denoted $P_Af$. Passing $n\to\infty$ in the same norm inequality proves the required tail estimate.

Continuity of $d$ implies $d(P_Af)=\lim_m r_m=0$. Protection holds before taking a limit: $pA=0$ gives $pf^{(m+1)}=pf^{(m)}$, hence $pf^{(m)}=pf$ for every $m$. Continuity of $p$ gives $p(P_Af)=pf$. This explains why continuity of the observable belongs to this analytic statement.

For linearity, write $L=I-Ad$, so $f^{(m)}=L^mf$. For fixed $f,g$ and scalars $\lambda,\mu$,
\[
 L^m(\lambda f+\mu g)=\lambda L^mf+\mu L^mg.
\]
Continuity of addition and scalar multiplication allows passage to the norm limit and proves linearity of $P_A$. The estimate with $m=0$ gives
\[
 \norm{P_Af}\le\norm f+\frac{\norm A}{1-q}\norm{df}
 \le\left(1+\frac{\norm A\norm d}{1-q}\right)\norm f,
\]
so the linear map is bounded. If $df=0$, every iterate equals $f$, hence $P_Af=f$. Its image is contained in $\ker d$ and it fixes that kernel, proving surjectivity onto its stated image and $P_A^2=P_A$. For $q=0$ the residual vanishes after the first update and the same inequalities remain valid.''','Supply the finite tail estimate, all limit passages and bounded linear projection construction.')

proof('03_towers.tex','KS20',r'''
Let $\theta=SB_X<1$. The number $K=S/(1-\theta)$ is nonnegative and satisfies
\[
 S+SB_XK=K.
\]
Fix $r\in R$ and define its coordinates recursively as in \eqref{eq:greenrecurrence}. The initial coordinate has norm zero. If $\norm{(Ar)_n}\le K\norm r_\infty$, submultiplicativity of operator norms gives
\[
 \begin{aligned}
 \norm{(Ar)_{n+1}}
 &\le\norm{s_n}\bigl(\norm{r_n}+\norm{(Ar)_n}\norm{\rho^X_n}\bigr)\\
 &\le S(1+KB_X)\norm r_\infty=K\norm r_\infty.
 \end{aligned}
\]
Induction proves the estimate at every coordinate, so the recursively defined family actually belongs to the bounded product $E$.

The coordinate recurrence preserves addition and scalar multiplication, starting from the zero initial coordinate. Induction therefore proves these laws for the family map $A$. Its uniform estimate proves $\norm A\le K$, giving a continuous linear map with the claimed domain and codomain.

For every $n$, apply the target restriction to the recurrence. The equation $\rho^Y_ns_n=I$ gives
\[
 \rho^Y_n(Ar)_{n+1}=r_n+(Ar)_n\rho^X_n,
 \qquad (\partial Ar)_n=r_n.
\]
Coordinate equality yields the operator identity $\partial A=I_R$. In particular this identity holds for every bounded residual, not just residuals already known to lie in the image.

Set $P=I-A\partial$. Then
\[
 \partial P=\partial-\partial A\partial=0,\qquad
 P^2=I-2A\partial+A(\partial A)\partial=I-A\partial=P.
\]
The expression $2A\partial$ abbreviates addition of the same operator twice and uses no division by two. Every exact $f$ is fixed because $\partial f=0$. Since $(Ar)_0=0$, the seed of $Pf$ is $f_0$. Finally $f-Pf=A\partial f$, and the bound on $A$ gives the asserted residual estimate. The denominators above are justified exactly by the strict propagation gap.''','Show the recurrence lands in the bounded product before bundling the operator, and prove projection identities.')

proof('03_towers.tex','KS26',r'''
Let $D_0=I$ and $D_N=C_{N-1}\cdots C_0:R_0\to R_N$. Thus $x_N=D_Nx$, $Q_N=L_ND_N$, and repeated use of $C_jJ_j=I$ gives
\[
 D_NL_N=I_{R_N}.
\]
This cancellation takes place between adjacent maps with matching domains. No identification of different residual spaces is needed.

Since $L_{j+1}=L_jJ_j$ and $x_{j+1}=C_jx_j$,
\[
 L_jh_j=L_j(x_j-J_jx_{j+1})=Q_jx-Q_{j+1}x.
\]
Summing from $j=0$ to $N-1$ leaves $x-Q_Nx$ because $Q_0=I$. This proves both finite reconstruction identities, including $N=0$, when the detail sum is empty.

Idempotence follows from $D_NL_N=I$:
\[
 Q_N^2=L_N(D_NL_N)D_N=Q_N.
\]
For $M\ge N$, put $C_{N,M}=C_{M-1}\cdots C_N$ and $J_{N,M}=J_N\cdots J_{M-1}$, using identities for $M=N$. Then
\[
 D_M=C_{N,M}D_N,\quad L_M=L_NJ_{N,M},\quad C_{N,M}J_{N,M}=I.
\]
The identities $D_NL_M=J_{N,M}$ and $D_ML_N=C_{N,M}$ now give
\[
 Q_NQ_M=L_NJ_{N,M}D_M=Q_M,\qquad
 Q_MQ_N=L_MC_{N,M}D_N=Q_M.
\]
Both orders have been checked, rather than inferred from one range inclusion.

If all $h_j$ vanish, the finite telescope gives $Q_Nx=x$ for every $N$. Conversely, if every $Q_Nx=x$, then $L_jh_j=Q_jx-Q_{j+1}x=0$. Apply the left inverse $D_j$ of $L_j$ to obtain $h_j=0$. The injectivity of the restoration composite is the step that recovers the original detail from its transported value.''','Expose all typed composites and the left-inverse argument needed for the persistent-space converse.')

proof('03_towers.tex','KS27',r'''
The nested identities first imply that the kernels increase: if $Q_My=0$ and $N\ge M$, then $Q_Ny=Q_NQ_My=0$. Thus the finite core really is an increasing union of linear subspaces.

Suppose $Q_Nx\to0$. Put $y_N=S_Nx=x-Q_Nx$. Idempotence gives $Q_Ny_N=Q_Nx-Q_N^2x=0$, so $y_N\in\mathcal F$. Since $x-y_N=Q_Nx\to0$, these are finite-core approximants converging to $x$. Hence $x\in\overline{\mathcal F}$.

Conversely, fix $x\in\overline{\mathcal F}$ and $\epsilon>0$. Choose $y\in\mathcal F$ satisfying $\norm{x-y}<\epsilon/(K+1)$. Some $M$ has $Q_My=0$. For every $N\ge M$, nesting and the common operator bound give
\[
 \norm{Q_Nx}=\norm{Q_N(x-y)}\le K\norm{x-y}
 <\epsilon\frac{K}{K+1}\le\epsilon.
\]
If $K=0$, the norm on the left is already zero, so no division by $K$ is required. The approximation $y$ is chosen before the depth $N$, giving precisely the quantifier order in norm convergence. This proves equality of the two sets. Applying it to every $x\in R_0$ gives the density criterion.''','Make kernel nesting and the approximation/depth quantifiers explicit, including zero uniform gain.')

# Save after each batch to support an interrupted editorial handoff.
(ROOT/'audit/proof_detail/changes_core.json').write_text(json.dumps(changes,indent=2)+'\n')
print('expanded',len(changes),'proofs; added words',sum(c['new_words']-c['old_words'] for c in changes))
