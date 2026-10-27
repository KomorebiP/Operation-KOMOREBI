from ks_proof_helpers import *

proof('05_geometry.tex','KS43',r'''
Let $K=\ker D$ and $K^\perp$ carry the induced Hilbert norm. Define $D_\perp u=Du$, but regard its target as $\ran D$ with the norm inherited from $R$. It is injective: $Du=0$ puts $u$ in both $K$ and $K^\perp$, so $u=0$. It is surjective onto that target: if $r=Dx$, then $u=x-qx\in K^\perp$ and $Du=Dx=r$. Thus it is a bounded linear bijection before any continuity of its inverse is claimed.

Suppose first that the range is closed. Because $R$ is Banach, $\ran D$ is then Banach. The domain $K^\perp$ is also complete. The bounded inverse theorem, proved in Appendix~\ref{app:proof-tools}, gives a bounded inverse $A=D_\perp^{-1}$. Applying it to $Dx=D(x-qx)$ yields
\[
 x-qx=A(Dx),\qquad \norm{x-qx}\le\norm A\norm{Dx}.
\]
Hence condition 2 holds. If any $C\ge0$ satisfies condition 2, then for every $r\in\ran D$ apply it to $u=Ar\in K^\perp$. Since $qu=0$, it gives $\norm{Ar}\le C\norm r$. Taking the operator norm proves $\norm A\le C$. This establishes the least constant, not just a sufficient one. If $D=0$, both $K^\perp$ and the range are zero spaces and $\norm A=0$.

Now assume condition 2. To prove closedness, take an arbitrary sequence $r_n\in\ran D$ with $r_n\to r$ in $R$. Choose $x_n$ with $Dx_n=r_n$ and put $u_n=x_n-qx_n$. Then $u_n\in K^\perp$ and $Du_n=r_n$. Applying the estimate to $u_n-u_m$ gives
\[
 \norm{u_n-u_m}\le C\norm{r_n-r_m}.
\]
Thus $(u_n)$ is Cauchy in the complete space $K^\perp$. Let its limit be $u$. Continuity gives $Du=\lim_n r_n=r$, so $r\in\ran D$. In a normed space, a set containing the limits of all its convergent sequences is closed. This proves condition 1 without presupposing that the initially unbounded inverse is continuous.

Condition 2 implies condition 3 by choosing $y=qx$. Conversely, if condition 3 supplies an exact $y$ for a given $x$, the nearest-point property of $qx$ gives
\[
 \norm{x-qx}\le\norm{x-y}\le C\norm{Dx}.
\]
The same $C$ works for all $x$, proving condition 2. This last implication does not require the selected answers $y$ to depend linearly or continuously on $x$.''','Prove the transverse map is bijective, isolate both completeness assumptions, and establish least gain and the converse.')

proof('05_geometry.tex','KS56',r'''
Feasibility gives some $h_0=x-y_0\in M$ with $Bh_0=Dx$. Conversely, every $h\in M$ satisfying $Bh=Dx$ produces an exact protected answer $y=x-h$. Thus the answer problem and the correction problem are equivalent, with correction set
\[
 \{h\in M:Bh=Dx\}=h_0+\ker B.
\]
This is a nonempty closed affine subset of the Hilbert space $M$. Closedness of $\ker B$ follows from continuity of $B$, independently of whether its image is closed.

Let $k_0=P^M_{\ker B}h_0$ and $h_*=h_0-k_0$. Then $Bh_*=Bh_0=Dx$ and $h_*\perp\ker B$ in $M$. If a different initial correction is chosen, it differs from $h_0$ by an element of $\ker B$. Its orthogonal-complement component is therefore again $h_*$. This proves that the construction is independent of the feasibility witness.

Every other correction can be written uniquely as $h_*+k$ with $k\in\ker B$. Orthogonality gives
\[
 \norm{h_*+k}^2=\norm{h_*}^2+\norm k^2.
\]
Writing $y_*=x-h_*$ and $y=x-h_*-k$, we have $x-y=h_*+k$ and $y_*-y=k$. Substitution proves the stated Pythagorean identity. Its last term vanishes only when $y=y_*$, establishing the unique closest answer.

If $\ran B$ is closed, KS43 applied on $M$ gives a bounded inverse of $B$ on $(\ker B)^{\perp_M}$. The vector $h_*$ is exactly that inverse applied to $Dx$, so its norm obeys the required bound.

For the converse, suppose the bound holds for every feasible raw candidate. Every $x\in M$ is feasible, because $y=0$ has $Dy=0$ and $py=px=0$. Its closest protected exact answer is $P^M_{\ker B}x$. Thus the assumed estimate reduces on $M$ to
\[
 \norm{x-P^M_{\ker B}x}\le C\norm{Bx}\qquad(x\in M).
\]
KS43 forces $\ran B$ to be closed. The same restriction also proves that no smaller nonnegative constant than the transverse inverse norm can work. If the range is zero, feasible candidates are already exact under permitted correction and the least correction is zero, so the optimal gain is zero.''','Identify the full affine correction fiber, track the signs in the distance identity, and prove necessity on the permitted subspace.')

proof('05_geometry.tex','KS47',r'''
Suppose the range of the joint map is closed. To test closedness of $\ran B$, take a sequence $Bk_n\to y$ with $k_n\in\ker D$. The joint images are
\[
 (Dk_n,Ck_n)=(0,Bk_n)\longrightarrow(0,y).
\]
Closedness supplies $x\in E$ with $(Dx,Cx)=(0,y)$. The first coordinate gives $x\in\ker D$, and the second gives $Bx=y$. Hence the matching range is closed. This direction did not require closedness of $\ran D$.

For the reverse direction, assume both $\ran D$ and $\ran B$ are closed, and take joint images converging to $(r,y)$. Thus $Dx_n\to r$ and $Cx_n\to y$. Decompose each input orthogonally as
\[
 x_n=u_n+k_n,\quad
 u_n\in(\ker D)^\perp,\quad k_n\in\ker D.
\]
Because $r\in\ran D$ and the transverse inverse $A$ of $D$ is bounded by KS43, the first components determine
\[
 u_n=A(Dx_n)\longrightarrow A(r)=u,
 \qquad Du=r.
\]
Continuity of $C$ now gives
\[
 Bk_n=Ck_n=Cx_n-Cu_n\longrightarrow y-Cu.
\]
Closedness of $\ran B$ supplies $k\in\ker D$ with $Bk=y-Cu$. There is no need for the sequence $k_n$ itself to converge. The single vector $u+k$ satisfies
\[
 D(u+k)=r,
 \qquad C(u+k)=Cu+Bk=y.
\]
Thus the joint limit lies in the joint range, proving closedness. The target product is Banach under its maximum norm, so KS43 applies to the joint map and gives a finite repair gain. The earlier two-stage estimate supplies an explicit, though not necessarily least, value.''','Separate the two implications and explain why the invisible sequence need not converge.')

proof('05_geometry.tex','KS48',r'''
For $z\in\ker D'$, the old residual bound gives
\[
 \norm{(I-q)z}\le C\norm{Dz}
 =C\norm{(D-D')z}\le C\varepsilon\norm z.
\]
Interchanging the roles gives
\[
 \norm{(I-q')w}\le C'\varepsilon\norm w
 \qquad(w\in\ker D).                                      \tag{*}
\]
We need a dual form of (*). For $v\in(\ker D')^\perp$ and any $y\in E$, self-adjointness of $q$ and $v=(I-q')v$ give
\[
 |\langle qv,y\rangle|
 =|\langle v,qy\rangle|
 =|\langle v,(I-q')qy\rangle|
 \le C'\varepsilon\norm v\norm{qy}
 \le C'\varepsilon\norm v\norm y.
\]
The Hilbert norm equals the supremum of these pairings on the unit ball, so
$\norm{qv}\le C'\varepsilon\norm v$. This proves the precise restriction estimate needed on $(I-q')x$, not just a coarser bound in terms of $\norm x$.

Now write
\[
 (q-q')x=q(I-q')x-(I-q)q'x.
\]
The two displayed terms lie in $\ker D$ and $(\ker D)^\perp$, respectively, so they are orthogonal. The input components $(I-q')x$ and $q'x$ are also orthogonal. Applying the dual estimate to the first and the original cross estimate to the second gives
\[
\begin{aligned}
 \norm{(q-q')x}^2
 &=\norm{q(I-q')x}^2+\norm{(I-q)q'x}^2\\
 &\le (C'\varepsilon)^2\norm{(I-q')x}^2
      +(C\varepsilon)^2\norm{q'x}^2\\
 &\le\varepsilon^2\max(C,C')^2
       \bigl(\norm{(I-q')x}^2+\norm{q'x}^2\bigr)\\
 &=\varepsilon^2\max(C,C')^2\norm x^2.
\end{aligned}
\]
The bound $\norm{D-D'}\le\varepsilon$ implies $\varepsilon\ge0$, so taking square roots yields the operator estimate. If the common gain is $M$, substitute $C=C'=M$ and $\varepsilon=\norm{D-D'}$. This is exactly the Lipschitz inequality on the class carrying that gain. The use of two orthogonal decompositions explains the maximum coefficient instead of a sum.''','Replace the terse adjoint argument with the required restricted dual estimate and two Pythagorean decompositions.')

proof('05_geometry.tex','KS49',r'''
The map $T=(D-D')A$ acts on the Banach target $R$ and satisfies $\norm T\le a\varepsilon<1$. The operator series
\[
 Z=\sum_{n=0}^\infty T^n
\]
converges in operator norm and obeys $\norm Z\le(1-a\varepsilon)^{-1}$. Multiplying its finite partial sums on either side by $I-T$ gives $I-T^{N+1}$. Passing to the operator-norm limit proves $(I-T)Z=Z(I-T)=I$. Appendix~\ref{app:proof-tools} supplies the full series argument, including completeness of the operator space.

Since $DA=I$, one has $D'A=DA-(D-D')A=I-T$. Therefore $A'=AZ$ satisfies
\[
 D'A'=(I-T)Z=I,\qquad
 \norm{A'}\le\norm A\norm Z\le\frac a{1-a\varepsilon}.
\]
The first equation explicitly supplies a preimage of every target vector, proving surjectivity.

For any $x$, put $y=x-A'D'x$. Then $D'y=D'x-D'A'D'x=0$, so $y$ is a valid exact competitor for orthogonal projection. Its error gives
\[
 \norm{x-q'x}\le\norm{x-y}=\norm{A'D'x}
 \le\frac a{1-a\varepsilon}\norm{D'x}.
\]
The same argument using $A$ gives $\norm{x-qx}\le a\norm{Dx}$. Both coefficients are nonnegative and $a/(1-a\varepsilon)\ge a$. Substitution into KS48 yields
\[
 \norm{q-q'}\le\frac{a\varepsilon}{1-a\varepsilon}.
\]
No assertion that $I-A'D'$ is orthogonal was needed. It supplies an exact comparison vector, while best approximation supplies the orthogonal bound.''','Construct the inverse by its series, verify both inverse sides and distinguish exact competitors from orthogonal repair.')

proof('05_geometry.tex','KS50',r'''
Let $R_0=I-AD$ and $R_1=I-A'D'$. From $DA=D'A'=I$ we obtain $DR_0=0$ and $D'R_1=0$. Each $R_i$ fixes its corresponding kernel. Thus $R_1$ restricts to a map from $\ker D$ to $\ker D'$, while $R_0$ restricts in the other direction.

The inverse identities require two additional cancellations. First,
\[
 R_0A'=(I-AD)AZ=(A-ADA)Z=0.
\]
Second, using $D'A=I-T$ and $Z(I-T)=I$,
\[
 R_1A=A-AZD'A=A-AZ(I-T)=0.
\]
For $x\in\ker D$, these identities give
\[
 R_0R_1x=R_0(x-A'D'x)=R_0x=x.
\]
For $y\in\ker D'$, they give
\[
 R_1R_0y=R_1(y-ADy)=R_1y=y.
\]
Both restricted maps are bounded and linear as restrictions of bounded linear operators. They are therefore inverse continuous linear maps, establishing the asserted equivalence.

Finally, if $Dx=0$, then $D'x=(D'-D)x$. Hence
\[
 \norm{Jx-x}=\norm{A'D'x}
 \le\norm{A'}\varepsilon\norm x
 \le\frac{a\varepsilon}{1-a\varepsilon}\norm x.
\]
This derivation uses the selected right inverse $A$ throughout. It proves a controlled transport of exact vectors, not a claim that the selected map is the nearest-point projection onto the new kernel.''','Prove the two annihilation identities and both inverse restrictions with correct operator order.')

proof('05f_bounded_realization.tex','lem:weak-subsequence',r'''
Choose $M\ge0$ with $\norm{a_n}\le M$. If $M=0$, every term is zero and the conclusion is immediate. Otherwise let $H_0$ be the closed linear span of the countably many vectors $a_n$. Finite rational linear combinations of those vectors form a countable dense set, so $H_0$ is separable. Apply Gram--Schmidt to a countable dense sequence, omitting zero remainders. This gives either a finite orthonormal basis or a countable orthonormal sequence $(e_j)$ whose closed span is $H_0$. The ambient Hilbert space itself need not be separable.

Each scalar sequence $\langle a_n,e_j\rangle$ is bounded by $M$. For the first coordinate choose a convergent subsequence, for the second choose a subsequence of that subsequence, and continue. Taking the $k$th term from the $k$th nested subsequence, with increasing original indices, yields $a_{n_k}$ for which every fixed coordinate converges. Call the coordinate limits $c_j$. In the finite-dimensional case only finitely many successive selections are required.

For each finite $J$, Bessel's inequality and passage to the limit give
\[
 \sum_{j=1}^Jc_j^2
 =\lim_k\sum_{j=1}^J\langle a_{n_k},e_j\rangle^2\le M^2.
\]
The nondecreasing partial sums are therefore bounded. Orthogonality makes the partial vector sums $\sum_{j\le J}c_je_j$ Cauchy, so completeness defines $a\in H_0$ with $\norm a\le M$.

To verify weak convergence against $h\in H_0$, choose a finite basis combination $h_J$ close to $h$. Then
\[
 |\langle a_{n_k}-a,h\rangle|
 \le |\langle a_{n_k}-a,h_J\rangle|
      +2M\norm{h-h_J}.
\]
For a prescribed tolerance, choose $h_J$ first to control the second term and then $k$ to control the first by finitely many coordinate limits. For a general $h$ in the ambient space, write $h=P_{H_0}h+h_\perp$. The orthogonal component pairs to zero with every $a_{n_k}$ and with $a$, reducing to the preceding case. This proves weak convergence against every test vector.

If $a\ne0$, testing against $a/\norm a$ gives
\[
 \norm a=\lim_k\langle a_{n_k},a/\norm a\rangle
 \le\liminf_k\norm{a_{n_k}}.
\]
The zero limit case follows from nonnegativity. Thus the lower-semicontinuity conclusion concerns the actual norms on the selected subsequence, not only the original bound $M$.''','Prove the weak subsequence result without assuming ambient separability; spell out diagonal selection and test-vector approximation.')

proof('05f_bounded_realization.tex','WR01',r'''
If $Ta=r$, the constant sequence $a_n=a$ is bounded and has zero residual. For the converse, let $\norm{a_n}\le M$ and $Ta_n\to r$ in norm. By the preceding lemma there is a subsequence $a_{n_k}$ converging weakly to $a\in H$ with $\norm a\le M$.

For every fixed $y\in Y$, the adjoint identity and weak convergence give
\[
 \langle Ta,y\rangle
 =\langle a,T^*y\rangle
 =\lim_k\langle a_{n_k},T^*y\rangle
 =\lim_k\langle Ta_{n_k},y\rangle.
\]
The last limit equals $\langle r,y\rangle$ because norm convergence implies convergence of each continuous pairing. Thus $\langle Ta-r,y\rangle=0$ for every $y$. Taking $y=Ta-r$ gives $\norm{Ta-r}^2=0$, hence $Ta=r$.

This proof does not claim that $Ta_{n_k}$ converges in norm merely because $a_{n_k}$ converges weakly. Its norm convergence to $r$ was a separate hypothesis. The boundedness of the candidate corrections is used to obtain a weakly convergent subsequence, and their accurate residuals are used to identify its image exactly. The bound $\norm a\le M$ comes from weak lower semicontinuity, so the exact answer stays inside the same closed budget ball.''','Separate weak continuity of the operator from the assumed strong convergence of its images.')

proof('05f_bounded_realization.tex','WR02',r'''
The nearest-point theorem for nonempty closed convex subsets of a Hilbert space, proved in Appendix~\ref{app:proof-tools}, supplies $a_n$. Write $A_n=a_n+L_n$, where $L_n$ is its closed direction subspace. For $\ell\in L_n$ and every real $t$, the vector $a_n+t\ell$ belongs to $A_n$. Minimality implies
\[
 0\le\norm{a_n+t\ell}^2-\norm{a_n}^2
 =2t\langle a_n,\ell\rangle+t^2\norm\ell^2.
\]
Allowing both signs of arbitrarily small $t$ forces $\langle a_n,\ell\rangle=0$.

If $m\ge n$, nesting gives $a_m\in A_n$, so $a_m-a_n\in L_n$. Expanding its norm therefore gives
\[
 \norm{a_m}^2
 =\norm{a_n+(a_m-a_n)}^2
 =\norm{a_n}^2+\norm{a_m-a_n}^2.
\]
This is the exact energy identity. It also makes $m_n^2$ nondecreasing.

Suppose these energies are bounded, and let $L=\lim_n m_n^2$. Given $\epsilon>0$, choose $N$ with $L-m_N^2<\epsilon^2$. For $m\ge n\ge N$,
\[
 \norm{a_m-a_n}^2=m_m^2-m_n^2\le L-m_N^2<\epsilon^2.
\]
Thus $(a_n)$ is Cauchy and has a norm limit $a_*$. For each fixed $n$, all terms from that index onward belong to the closed set $A_n$, so $a_*\in A_n$. This places $a_*$ in their entire intersection.

If $a$ lies in the intersection, then $\norm a\ge\norm{a_n}$ for every $n$. Norm continuity gives $\norm a\ge\norm{a_*}$. Uniqueness follows from the nearest-point theorem applied to the intersection, which is closed and convex and now known to be nonempty. Alternatively, the midpoint of two different minimizers would have strictly smaller norm by the parallelogram identity. Taking $m\to\infty$ in the finite energy identity yields
\[
 \norm{a_*-a_n}^2=\norm{a_*}^2-\norm{a_n}^2.
\]
Conversely, any element of the intersection bounds every minimum norm from above. Therefore an empty intersection forces the nondecreasing sequence $m_n$ to be unbounded. A nondecreasing unbounded nonnegative sequence tends to infinity, giving the last conclusion.''','Derive orthogonality from two-sided line variations and supply the full Cauchy and intersection argument.')

proof('05g_budget_certificates.tex','WR03',r'''
The feasible ball is nonempty because it contains zero, and the infimum lies between zero and $\norm r$. Choose $a_n$ in that ball with $\norm{r-Ta_n}\to\beta(M)$. A weakly convergent subsequence has limit $a$ with $\norm a\le M$. Bounded linearity makes $r-Ta_{n_k}$ converge weakly to $r-Ta$. Applying weak lower semicontinuity in the target gives
\[
 \norm{r-Ta}\le\liminf_k\norm{r-Ta_{n_k}}=\beta(M).
\]
The reverse inequality holds by the definition of the infimum, so $a$ attains it. When $M=0$ the only feasible correction is zero, and the same conclusion reads $\beta(0)=\norm r$.

For convexity, take minimizers $a_1,a_2$ at budgets $M_1,M_2$ and $t\in[0,1]$. The candidate $a_t=ta_1+(1-t)a_2$ satisfies
\[
 \norm{a_t}\le tM_1+(1-t)M_2,
\]
and its residual is $t(r-Ta_1)+(1-t)(r-Ta_2)$. The triangle inequality therefore gives
\[
 \beta(tM_1+(1-t)M_2)\le t\beta(M_1)+(1-t)\beta(M_2).
\]
Monotonicity follows from inclusion of balls. If $0\le M_1\le M_2$ and $M_2>0$, choose a minimizer $a_2$ at $M_2$ and put $a_1'=(M_1/M_2)a_2$. Then $\norm{a_1'}\le M_1$ and $\norm{a_2-a_1'}\le M_2-M_1$, so
\[
 \beta(M_1)\le\norm{r-Ta_1'}
 \le\beta(M_2)+\norm T(M_2-M_1).
\]
Together with monotonicity this proves the Lipschitz estimate. The omitted case $M_2=0$ has $M_1=0$ and is equality.

Since $r-b$ is orthogonal to $C$ and $b-Ta\in C$, every correction satisfies
\begin{equation}\label{eq:range-decomposition}
 \norm{r-Ta}^2=q^2+\norm{b-Ta}^2.
\end{equation}
Thus $\beta(M)\ge q$. Given $\epsilon>0$, range density in $C$ supplies one correction $a$ with $\norm{b-Ta}<\epsilon$. For every $M\ge\norm a$ it follows that
\[
 q\le\beta(M)\le\sqrt{q^2+\epsilon^2}.
\]
First letting the budget increase and then letting $\epsilon\downarrow0$ proves the limit.

Finally, if $\beta(M)=q$, choose an attaining correction in that ball. The orthogonal identity forces $\norm{b-Ta}^2=0$, hence $Ta=b$. Conversely such a correction attains residual $q$. Setting $q=0$ proves the exact-feasibility criterion. Attainment at fixed budget is essential to the forward implication: a zero unrestricted infimum would not itself supply a preimage.''','Prove budget attainment, convexity, endpoint continuity and equality cases with quantifiers and no minimax shortcut.')

proof('05g_budget_certificates.tex','WR04',r'''
For every $\norm a\le M$ and $\norm z\le1$, the adjoint identity and Cauchy--Schwarz give
\[
\begin{aligned}
 \langle r,z\rangle-M\norm{T^*z}
 &=\langle r-Ta,z\rangle+\langle a,T^*z\rangle-M\norm{T^*z}\\
 &\le\langle r-Ta,z\rangle
 \le\norm{r-Ta}.
\end{aligned}
\]
Taking the infimum over corrections proves that every proposed dual value is at most $\beta(M)$. This part alone already proves the impossibility certificate.

To prove sharpness, let $a_M$ be an attaining correction from WR03 and put $v=r-Ta_M$. If $v=0$, then $\beta(M)=0$ and $z=0$ attains the dual bound. Assume henceforth $v\ne0$ and set $z=v/\norm v$.

Fix any feasible $a$ and put $h=a-a_M$. The segment $a_M+th$ is feasible for $0\le t\le1$. Minimality gives, for $t>0$,
\[
 0\le\norm{v-tTh}^2-\norm v^2
   =-2t\langle v,Th\rangle+t^2\norm{Th}^2.
\]
Divide by $t$ and let $t\downarrow0$. It follows that $\langle v,T(a-a_M)\rangle\le0$, hence
\[
 \langle T^*z,a\rangle\le\langle T^*z,a_M\rangle
 \quad(\norm a\le M).
\]
The support value of a Hilbert ball can be computed directly. If $T^*z\ne0$ and $M>0$, it is attained at $a=M T^*z/\norm{T^*z}$ and equals $M\norm{T^*z}$. If either factor is zero, every feasible pairing is zero at its maximum and the same formula holds. Thus
\[
 \langle T^*z,a_M\rangle=M\norm{T^*z}.
\]
Substituting this equality gives
\[
 \langle r,z\rangle-M\norm{T^*z}
 =\langle r-Ta_M,z\rangle=\norm v=\beta(M).
\]
We have constructed an attaining witness and thereby justified the word ``maximum.'' The proof uses one-sided variations in a convex ball, not an unproved exchange of an infimum and a supremum.''','Derive the variational inequality without a differentiability shortcut and handle every dual support degeneracy.')

proof('05g_budget_certificates.tex','WR05',r'''
Fix a feasible correction $a$. The two residual vectors have difference
\[
 (r-Ta)-(\widetilde r-\widetilde Ta)
 =(r-\widetilde r)-(T-\widetilde T)a,
\]
whose norm is at most $c=\delta+\eta M$. The reverse triangle inequality therefore gives both inequalities
\[
 \norm{r-Ta}\le\norm{\widetilde r-\widetilde Ta}+c,
 \qquad
 \norm{\widetilde r-\widetilde Ta}\le\norm{r-Ta}+c.
\]
The domain of feasible corrections is identical in the two problems. Taking the infimum of each inequality over that common domain yields
\[
 \beta_{T,r}(M)\le\beta_{\widetilde T,\widetilde r}(M)+c,
 \qquad
 \beta_{\widetilde T,\widetilde r}(M)\le\beta_{T,r}(M)+c.
\]
These are precisely the absolute-value bound. One could equivalently evaluate at the two attained minimizers, but no relation between those minimizers is needed.

For any admissible $z$, WR04 for the nominal problem gives
\[
 \beta_{\widetilde T,\widetilde r}(M)
 \ge\langle\widetilde r,z\rangle-M\norm{\widetilde T^*z}.
\]
Combine this with the lower half of the preceding comparison. The result is a certificate against every correction in the original fixed ball, reduced by the explicit uncertainty allowance. If the correction space itself changed, the common-domain step would fail and this proof would no longer apply.''','Keep the common feasible domain explicit and show both directions of the infimum comparison.')

(ROOT/'audit/proof_detail/changes_analysis.json').write_text(json.dumps(changes,indent=2)+'\n')
print('expanded',len(changes),'proofs; added words',sum(c['new_words']-c['old_words'] for c in changes))
