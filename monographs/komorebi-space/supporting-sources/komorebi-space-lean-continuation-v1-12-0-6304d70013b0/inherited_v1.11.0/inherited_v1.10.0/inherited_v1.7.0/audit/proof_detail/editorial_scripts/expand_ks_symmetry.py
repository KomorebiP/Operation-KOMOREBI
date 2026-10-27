from ks_proof_helpers import *

proof('03a_observation.tex','KS61',r'''
A finite-stage equality remains true after moving to a later stage. Indeed, if it holds on $X_k$ and $\ell\ge k$, precompose both sides with $\rho^X_{k,\ell}$ and use the composite-restriction laws. Reflexivity uses $k=\phi(n)$, symmetry reverses the equality, and transitivity moves two witnesses to their maximum. The shared middle presentation then cancels as a literal function on that common fiber. This proves an equivalence relation without referring to global points.

We check compatibility with composition with all indices displayed. Write $f,f'$ with schedules $\phi,\phi'$ and $g,g'$ with schedules $\psi,\psi'$. Fix an output level $n$. Choose $j\ge\psi(n),\psi'(n)$ with
\[
 g_n\rho^Y_{\psi(n),j}=g'_n\rho^Y_{\psi'(n),j}.
\]
Next choose $k\ge\phi(j),\phi'(j)$ with
\[
 f_j\rho^X_{\phi(j),k}=f'_j\rho^X_{\phi'(j),k}.
\]
Monotonicity implies that $k$ is also at least both composite input levels. Applying the naturality equations and then the two witness equations gives
\[
\begin{aligned}
 g_nf_{\psi(n)}\rho^X_{\phi(\psi(n)),k}
 &=g_n\rho^Y_{\psi(n),j}f_j\rho^X_{\phi(j),k}\\
 &=g'_n\rho^Y_{\psi'(n),j}f_j\rho^X_{\phi(j),k}\\
 &=g'_n\rho^Y_{\psi'(n),j}f'_j\rho^X_{\phi'(j),k}\\
 &=g'_nf'_{\psi'(n)}\rho^X_{\phi'(\psi'(n)),k}.
\end{aligned}
\]
This is the required equality on every element of $X_k$. Thus composition descends to classes. The representative composition is associative because function composition and schedule composition are associative. The schedule $n\mapsto n$ with identity coordinate maps gives both identity laws. Hence the quotient has the claimed category structure.

Finally, evaluate a witness equation at the $k$th coordinate of a coherent point $x$. Its two restricted arguments become $x_{\phi(n)}$ and $x_{\psi(n)}$, proving equality of the realized outputs. Thus realization is well defined on the quotient. For a composite, direct evaluation gives
\[
 |g\circ f|(x)_n=g_n\bigl(f_{\psi(n)}(x_{\phi(\psi(n))})\bigr)
 =(|g|(|f|(x)))_n.
\]
The identity law is equally coordinatewise. Joint determination of output points proves the functor laws.''','Resolve all common-stage indices in quotient composition instead of leaving the naturality moves implicit.')

proof('03a_observation.tex','KS63',r'''
For a reindexed map $(\phi,f)$, the formula $|f|(x)_n=f_n(x_{\phi(n)})$ immediately supplies a finite-observation witness for each $n$. Eventual equality does not affect the realized function by KS61, so this defines a map from the quotient to the stated set of functions.

For surjectivity, let $F$ be finitely observed. Choose one pair $(k_n,a_n)$ at each output level, satisfying $F(x)_n=a_n(x_{k_n})$ for every coherent input. Define
\[
 \phi(n)=\max_{0\le i\le n}k_i,
 \qquad f_n=a_n\rho^X_{k_n,\phi(n)}.
\]
The maximum is of a nonempty finite set. It gives a monotone schedule with $k_n\le\phi(n)$. For every point $x$, coherence in $X$ gives
\[
 f_n(x_{\phi(n)})
 =a_n\bigl(\rho^X_{k_n,\phi(n)}x_{\phi(n)}\bigr)
 =a_n(x_{k_n})=F(x)_n.                                      \tag{*}
\]

The remaining obligation is naturality on \emph{all} finite states. Fix $i\le j$ and $u\in X_{\phi(j)}$. By surjectivity of that point projection, choose $x$ with $x_{\phi(j)}=u$. Equation (*) and output coherence yield
\[
\begin{aligned}
 \rho^Y_{i,j}f_j(u)&=\rho^Y_{i,j}F(x)_j=F(x)_i,\\
 f_i\rho^X_{\phi(i),\phi(j)}(u)&=f_i(x_{\phi(i)})=F(x)_i.
\end{aligned}
\]
The state $u$ was arbitrary. Hence the two finite-level functions are equal, which proves scheduled naturality. The resulting transport realizes $F$ by (*).

Different witness choices can give different schedules and coordinate maps, but the realized function is still $F$. By KS62 these transports are eventually equal, so their quotient class is independent of all choices. The same faithfulness result says that two classes with equal realized functions are identical. We have proved both surjectivity and injectivity, including the well-definedness of the inverse choice construction. No bound on the growth of $\phi$ follows from these quantifiers.''','Prove uniform finite-level naturality using lifts of arbitrary finite states, then independence of witness choices.')

proof('04_symmetry.tex','KS30',r'''
First, $T_c$ really is a view system. For $f:v\to w$, $g:w\to z$, and $x\in G_z$, the homomorphism and cocycle laws give
\[
 T_c(f)T_c(g)(x)=c_ff^*(c_gg^*x)
 =c_ff^*(c_g)f^*g^*x=c_{g\circ f}(g\circ f)^*x.
\]
The identity equation follows from $c_{1_v}=1$. No rearrangement of factors is involved.

Put $d=a\cdot c$. Its identity label is $a_v1a_v^{-1}=1$. For a composite, expand all factors in their original order:
\[
\begin{aligned}
 d_f f^*(d_g)
 &=a_vc_f[f^*(a_w)]^{-1}
   f^*(a_wc_g[g^*(a_z)]^{-1})\\
 &=a_vc_f[f^*(a_w)]^{-1}f^*(a_w)f^*(c_g)
       [f^*g^*(a_z)]^{-1}\\
 &=a_vc_{g\circ f}[(g\circ f)^*(a_z)]^{-1}
 =d_{g\circ f}.
\end{aligned}
\]
Thus the gauge formula preserves the cocycle condition. For two gauges $a,b$, substitution gives
\[
 (a\cdot(b\cdot c))_f
 =a_vb_vc_f[f^*(b_w)]^{-1}[f^*(a_w)]^{-1}
 =((ab)\cdot c)_f.
\]
The reversed order in the two inverse factors is exactly the formula for the inverse of a product. The identity gauge acts trivially.

If $d=a\cdot c$ and $x$ is a section of $T_c$, put $y_v=a_vx_v$. Then
\[
 d_ff^*(y_w)
 =a_vc_f[f^*(a_w)]^{-1}f^*(a_w)f^*(x_w)
 =a_vx_v=y_v.
\]
The inverse map is multiplication by $a_v^{-1}$ at each view, proving an equivalence of the actual section sets.

For the groupoid, an arrow $a:c\to d$ means the equation $a\cdot c=d$. If $b:d\to e$, then $(ba)\cdot c=b\cdot(a\cdot c)=e$, giving composition. The identity label is $1$ and the inverse label is $a^{-1}$. Associativity and the two inverse identities now follow from the corresponding multiplication laws in the product group. The label $ba$ is therefore forced by the order of application, not an arbitrary notational convention.''','Check the twisted view system, cocycle law, action order, section equivalence and groupoid laws separately.')

proof('04_symmetry.tex','KS31',r'''
The normalized label $c^q$ is the gauge transform of $c$ by $q^{-1}$, so KS30 makes it a cocycle. If $f:v\to w$ is internal to $U$, the partial-section equation says $q_v=c_ff^*(q_w)$, and therefore $c_f^q=1$ on that arrow.

If $t$ is another raw lift, define $a_v=t_v^{-1}q_v$. On $U$ both lifts equal $s$, so $a_v=1$ and $a\in\mathcal G_U$. Its action is
\[
\begin{aligned}
 (a\cdot c^q)_f
 &=t_v^{-1}q_v\,q_v^{-1}c_ff^*(q_w)
       [f^*(t_w^{-1}q_w)]^{-1}\\
 &=t_v^{-1}c_ff^*(q_w)
       [f^*(q_w)]^{-1}f^*(t_w)
 =t_v^{-1}c_ff^*(t_w)=c_f^t.
\end{aligned}
\]
Thus changing the raw lift leaves the based orbit unchanged.

Suppose the orbit is neutral. Equality of orbit classes means there exists an actual based gauge $b$ with $b\cdot c^q=1$. At an arrow $f:v\to w$, this equation is
\[
 b_vq_v^{-1}c_ff^*(q_w)[f^*(b_w)]^{-1}=1.
\]
Multiply on the left by $q_vb_v^{-1}$. Homomorphic preservation of products then gives
\[
 c_ff^*(q_wb_w^{-1})=q_vb_v^{-1}.
\]
Therefore $x_v=q_vb_v^{-1}$ is a twisted coherent family. On $U$, $b_v=1$ and $q_v=s_v$, so it extends the prescribed section.

Conversely, suppose $x$ is a global twisted section extending $s$. Put $b_v=x_v^{-1}q_v$. This is based, and direct substitution gives
\[
 (b\cdot c^q)_f
 =x_v^{-1}c_ff^*(x_w)=1,
\]
where the last equality is precisely the section equation for $x$. Hence the obstruction is neutral. These arguments establish the result using group cancellation only. In particular they do not assume an additive quotient, a norm on labels, or a decision procedure for finding $b$.''','Display the noncommutative cancellation for normalization independence and both trivialization directions.')

proof('04_symmetry.tex','KS34',r'''
\emph{Step 1: normalize the supplied identifications.} The triple-overlap equation with all indices equal gives $a_{ii}=a_{ii}a_{ii}$, hence $a_{ii}=1$. With indices $i,j,i$ it gives $a_{ji}a_{ij}=1$, hence $a_{ji}=a_{ij}^{-1}$. Composition coverage implies object coverage by inserting identity arrows. Choose a containing patch $\kappa(v)$ for each view and put
\[
 b_i(v)=a_{\kappa(v),i}(v)\quad(v\in U_i).
\]
At a point of $U_i\cap U_j$, the triple law, now on patches $\kappa(v),i,j$, gives
\[
 b_j(v)=a_{ij}(v)b_i(v).                                    \tag{*}
\]
The two endpoints of an arrow may have different reference patches. No common reference patch is being assumed.

\emph{Step 2: obtain literal matching labels.} Define
\[
 \widetilde c_i(f)=b_i(v)^{-1}c_i(f)f^*(b_i(w))
 \quad(f:v\to w\text{ in }U_i).
\]
This is a gauge transform and hence a cocycle on $U_i$. If the arrow lies also in $U_j$, substitute the original overlap equation and (*) at its two endpoints:
\[
\begin{aligned}
 \widetilde c_j(f)
 &=b_i(v)^{-1}a_{ij}(v)^{-1}
   a_{ij}(v)c_i(f)[f^*a_{ij}(w)]^{-1}
   f^*(a_{ij}(w)b_i(w))\\
 &=b_i(v)^{-1}c_i(f)f^*(b_i(w))
 =\widetilde c_i(f).
\end{aligned}
\]
Every cancellation is between neighboring inverse factors. Commutativity is not required.

\emph{Step 3: construct the global cocycle.} Every arrow is contained in a patch, again by inserting an identity in a composable pair. Define $c_f$ to be $\widetilde c_i(f)$ in any such patch. Step 2 proves independence. For an identity arrow, choose a patch through its view to obtain $c_{1_v}=1$. For $f:v\to w$ and $g:w\to z$, composition coverage supplies a patch containing all three vertices. Fullness places $f$, $g$, and $g\circ f$ in that same patch. Its cocycle law therefore proves
\[
 c_{g\circ f}=\widetilde c_i(g\circ f)
 =\widetilde c_i(f)f^*(\widetilde c_i(g))=c_ff^*(c_g).
\]
This is the exact point where composition coverage, rather than arrow coverage alone, is used.

Undoing the normalization proves
\[
 b_i(v)c_f[f^*(b_i(w))]^{-1}=c_i(f).
\]
Together with (*), these gauges constitute an isomorphism from the restriction of $c$ to the supplied descent datum. They implement its original overlaps, proving essential surjectivity of restriction.

\emph{Step 4: retain every morphism.} Let $c,d$ be global cocycles. Their canonical restrictions have identity overlap gauges. A morphism between those restrictions is consequently a family $r_i$ satisfying $r_j(v)=r_i(v)$ on each overlap. Assemble $r_v$ from any containing patch. For an arrow choose a patch containing both endpoints. Its gauge equation proves
\[
 d_f=r_vc_f[f^*(r_w)]^{-1}.
\]
Thus $r$ is a global gauge. Its restriction is the original family. Conversely, assembling the restrictions of a global gauge preserves every coordinate and returns that gauge. Restriction is therefore bijective on each Hom set, not merely injective on isomorphism classes. This is full faithfulness.

\emph{Step 5: obtain an equivalence.} For each descent object choose the global cocycle and isomorphism constructed above. For an arrow between descent objects, conjugate it by these two chosen isomorphisms and use the unique preimage under the Hom bijection of Step 4. This defines the arrow map of a quasi-inverse. Uniqueness of the preimage verifies its identity and composition laws, and the chosen isomorphisms provide the comparison to the identity functor. Hence the restriction functor is an equivalence of groupoids. Different patch choices can alter the representative but not this conclusion.''','Expand the actual nonabelian effectuation, all morphisms, and the construction of a quasi-inverse.')

proof('04_symmetry.tex','KS35',r'''
In the inclusion poset, identify a sieve on $W$ with a downward-closed collection of subsets of $W$. Pullback along $Z\subseteq W$ consists of those subsets of $Z$ that were already members of the original sieve. We verify the three topology axioms using this description.

The maximal sieve contains every subset of $W$, hence every composition support. For stability under pullback, let $\mathcal R$ cover $W$ and let $q$ be a composable pair whose support lies in $Z\subseteq W$. The same pair lies in the full patch $W$, so $|q|\in\mathcal R$. Since $|q|\subseteq Z$, it belongs to the pulled-back sieve on $Z$. Thus that sieve covers $Z$.

For transitivity, suppose $\mathcal R$ covers $W$, and that for every $U\in\mathcal R$ the pullback of a sieve $\mathcal T$ to $U$ covers $U$. Fix a composable pair $q$ in $W$. Its support $S=|q|$ belongs to $\mathcal R$. Since patches are full, $q$ is also a composable pair in $S$. The covering condition for the pullback of $\mathcal T$ to $S$ therefore puts the identity inclusion $S\subseteq S$ in that pullback. By the definition of pullback, this says $S\in\mathcal T$. It holds for every $q$, so $\mathcal T$ covers $W$.

Finally, the sieve generated by $U_i\subseteq W$ consists exactly of the subpatches $Z$ contained in at least one $U_i$. One inclusion follows because a sieve contains all restrictions of its generators. The reverse inclusion follows because this collection is itself downward closed and contains all generators, hence is the smallest such sieve. Consequently a support belongs to the generated sieve exactly when some $U_i$ contains all its endpoints. This proves the family characterization. When $W$ is empty, there are no composable pairs to test, so even the empty sieve is covering.''','Translate sieves into downward-closed subsets and verify every Grothendieck topology axiom explicitly.')

proof('04_symmetry.tex','KS36',r'''
We use the equivalence-of-descent-categories formulation of stackhood for the already constructed patch pseudofunctor. Its restriction maps act on actual cocycle labels and gauge values. Their identity and composition laws have been proved, so the descent condition is applied to a specified pseudofunctor, not assumed as part of its definition.

\emph{From standard descent data to overlap labels.} For a covering family $(U_i\subseteq W)$, standard descent data provide local objects and comparison gauges on common subpatches, natural under further restriction. At a view $v\in U_i\cap U_j$, restrict the comparison to the singleton patch $\{v\}$ and call its value $a_{ij}(v)$. To verify the gauge equation along $f:v\to w$ in an overlap, use the comparison on $U_i\cap U_j$, which is a full patch containing the arrow. Naturality identifies its two endpoint values with the singleton values. Its own gauge equation then becomes \eqref{eq:localgauge}. Evaluating the standard triple-comparison identity at a singleton gives \eqref{eq:triple}. Thus these labels form the concrete descent datum of KS34.

\emph{From the concrete realization back to standard data.} By KS34 there is a global cocycle $c$ and local gauges $b_i$ implementing these overlaps. On any common subpatch $Z\subseteq U_i\cap U_j$, the required equation between gauge arrows is an equality of their values at every $v\in Z$. At such a view it is $b_j(v)=a_{ij}(v)b_i(v)$, already proved by the construction. Equality of coordinate functions proves equality of the arrows on $Z$. Thus every standard common-subpatch equation holds, not only the equations on singleton tests. This gives an isomorphism from the standard restriction of $c$ to the original standard descent object.

\emph{Morphisms.} A standard morphism between restrictions of global objects has local gauge components. Its comparison equations at singleton patches show that these components agree on overlaps. The Hom gluing map from KS34 yields a unique global gauge. Conversely, a global gauge restricts to those components and satisfies all common-subpatch equations. Restriction and gluing are inverse on every Hom set. Standard restriction is therefore fully faithful as well as essentially surjective, hence an equivalence.

\emph{Every covering sieve.} Let $\mathcal R$ be an arbitrary covering sieve on $W$. Index a family by all its member inclusions $U\subseteq W$. Each composition support belongs to this family by the covering definition, so it is a composition cover. Its generated sieve is exactly $\mathcal R$: one inclusion uses that $\mathcal R$ is downward closed, and the other uses each member as its own generator. The family argument therefore proves the descent equivalence on the original sieve. Applying it to every covering sieve proves both descent of morphisms and effectiveness of objects. These are the required standard stack conditions \cite{stacks-stack,mathlib-stack}.''','Unpack the bridge from arbitrary common subpatches to singleton values and back, then handle all sieves.')

proof('04_symmetry.tex','KS37',r'''
Write the unit of the equivalence as $\eta:I_\V\Rightarrow LH$, and take the unit and counit with their triangle identities. Set $t_w=\varepsilon_w^{-1}:w\to HLw$. Given $y\in\Gamma(H^*F)$, define
\[
 (Ry)_w=F(t_w)y_{Lw}.
\]
For an arrow $f:w\to w'$, naturality of the inverse counit states
\[
 HL(f)\,t_w=t_{w'}f.
\]
Contravariance of $F$ and coherence of $y$ therefore give
\[
\begin{aligned}
 F(f)(Ry)_{w'}
 &=F(f)F(t_{w'})y_{Lw'}\\
 &=F(t_w)F(HL(f))y_{Lw'}
 =F(t_w)y_{Lw}=(Ry)_w.
\end{aligned}
\]
Thus recovery gives an actual coherent section.

If $x\in\Gamma(F)$, coherence along $t_w$ gives
\[
 (RH^*x)_w=F(t_w)x_{HLw}=x_w.
\]
For the other composite, the triangle identity says $t_{Hv}=H(\eta_v)$. Coherence of $y$ along $\eta_v:v\to LHv$ yields
\[
 (H^*Ry)_v=F(t_{Hv})y_{LHv}=F(H\eta_v)y_{LHv}=y_v.
\]
These coordinate equations prove both inverse identities.

For the relative claim, pullback clearly sends an extension of $s$ to an extension of $H^*s$ on $U'=H^{-1}U$. Conversely suppose $y$ extends $H^*s$. If $w\in U$, the isomorphism $w\cong HLw$ and isomorphism closure imply $HLw\in U$. Hence $Lw\in U'$ and $y_{Lw}=s_{HLw}$. Both endpoints of $t_w$ lie in $U$, so partial coherence gives
\[
 (Ry)_w=F(t_w)s_{HLw}=s_w.
\]
Recovery therefore preserves the required boundary. The two inverse identities remain valid on the subsets of extensions. Bijections preserve nonemptiness and identify any two elements exactly when their images are equal, proving preservation and reflection of existence and uniqueness.''','Show naturality and both triangle-identity computations, then isolate where saturated prescribed domains are needed.')

proof('04_symmetry.tex','KS39',r'''
For an object $(x,\phi)$ put $\beta_x=K(\phi)\sigma_x^{-1}:R'Ex\to Kb$. This is an isomorphism of the required type. If $a:(x,\phi)\to(y,\psi)$, naturality of $\sigma$ says
\[
 R'E(a)\sigma_x=\sigma_yKR(a),
 \qquad \sigma_y^{-1}R'E(a)=KR(a)\sigma_x^{-1}.
\]
Consequently
\[
 \beta_yR'E(a)
 =K(\psi)KR(a)\sigma_x^{-1}
 =K(\psi R(a))\sigma_x^{-1}
 =K(\phi)\sigma_x^{-1}=\beta_x.
\]
So $E(a)$ is a marked arrow. Identity and composition are preserved because the underlying arrow map is that of the functor $E$.

To prove full faithfulness, start with a marked arrow $u:Ex\to Ey$ between the transported objects. Full faithfulness of $E$ gives a unique $a:x\to y$ with $E(a)=u$. Its marked equation, rewritten by the naturality identity above, is
\[
 K(\psi R(a))\sigma_x^{-1}=K(\phi)\sigma_x^{-1}.
\]
Cancel the isomorphism on the right and use faithfulness of $K$ to obtain $\psi R(a)=\phi$. Thus the lifted arrow is marked. Uniqueness of the underlying lift also proves uniqueness as a marked arrow, giving a bijection on every Hom set.

For essential surjectivity, let $(y,\psi)$ be a target realization. Choose $x$ and an isomorphism $i:Ex\to y$, using essential surjectivity of $E$. Fullness of $K$ lifts the well-typed composite
\[
 KRx\xrightarrow{\sigma_x}R'Ex
 \xrightarrow{R'(i)}R'y\xrightarrow{\psi}Kb
\]
to an arrow $\phi:Rx\to b$. Since $\mathcal D$ is a groupoid, $\phi$ is automatically an isomorphism. Its image satisfies $K(\phi)=\psi R'(i)\sigma_x$, hence $\beta_x=\psi R'(i)$. This is precisely the condition for $i$ to be an arrow from the transported realization to $(y,\psi)$. It is an isomorphism because all categories involved are groupoids.

We have verified full faithfulness and essential surjectivity of the specified transport functor. Choosing these preimages and lifting arrows through the Hom bijections constructs a quasi-inverse, as in KS34, proving the claimed equivalence. No literal equality $KR=R'E$ was used.''','Fully type the transport, reflect the boundary equation through faithfulness, and construct essential-image preimages.')

(ROOT/'audit/proof_detail/changes_symmetry.json').write_text(json.dumps(changes,indent=2)+'\n')
print('expanded',len(changes),'proofs; added words',sum(c['new_words']-c['old_words'] for c in changes))
