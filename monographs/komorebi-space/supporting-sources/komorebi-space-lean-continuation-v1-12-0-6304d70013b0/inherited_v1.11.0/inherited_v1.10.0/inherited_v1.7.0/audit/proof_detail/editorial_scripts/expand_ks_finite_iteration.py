from ks_proof_helpers import *

proof('06_boundaries.tex','KS54',r'''
For a fixed terminal level \(N\), the integer \(N\) belongs to every fiber \(X_n\) with \(n\le N\). Assign that same integer at each such level. Every restriction is an inclusion, so it preserves the assigned integer and all finite coherence equations hold. This proves finite solvability with the quantifiers in the order ``for every \(N\), there exists a prefix.''

Suppose instead that \(x=(x_n)\) is a global point. Equality along each inclusion says that the underlying natural numbers of \(x_{n+1}\) and \(x_n\) are equal. Induction therefore makes every underlying coordinate equal to the number \(m\) underlying \(x_0\). Membership of \(x_{m+1}\) in \(X_{m+1}\) now gives \(m\ge m+1\), a contradiction. Thus no global point exists.

There is no conflict with a gluing theorem for prefixes. The prefix chosen above for length \(N+1\) restricts to the value \(N+1\), not to our chosen value \(N\) on the shorter prefix. Nor could another choice of one solution for every length give a matching family: its value at level zero would force the same forbidden global integer. Separate existence at every length is strictly weaker than existence of a compatible family of prefix solutions.
''','Separate the finite-solvability quantifiers from a matching family and use an explicit global contradiction.')

proof('06_boundaries.tex','KS58',r'''
Write \(I_{n,m}=\rho_{n,m}(X_m)\) for \(m\ge n\). Each \(I_{n,m}\) is nonempty. The composition law gives
\[
 I_{n,m+1}=\rho_{n,m}\bigl(\rho_m(X_{m+1})\bigr)\subseteq I_{n,m}.
\]
These are subsets of the finite set \(X_n\). Every strict decrease removes an element permanently, so only finitely many strict decreases are possible. There is an index \(s_n\ge n\) such that \(I_{n,m}=I_{n,s_n}\) for all \(m\ge s_n\). Consequently \(Y_n=I_{n,s_n}\) is nonempty.

We next prove that restriction induces a \emph{surjection} \(Y_{n+1}\to Y_n\), even though \(X_{n+1}\to X_n\) need not be surjective. For membership, let \(z\in Y_{n+1}\). Given \(m\ge n+1\), write \(z=\rho_{n+1,m}(w)\) for some \(w\in X_m\). Then \(\rho_n z=\rho_{n,m}(w)\). Together with the automatic condition at \(m=n\), this shows \(\rho_nz\in Y_n\).

For surjectivity, fix \(y\in Y_n\) and choose
\[
 m\ge\max\{s_n,s_{n+1},n+1\}.
\]
Since \(y\in I_{n,m}\), there is \(w\in X_m\) with \(\rho_{n,m}(w)=y\). Put \(z=\rho_{n+1,m}(w)\). Stabilization at level \(n+1\) gives \(z\in Y_{n+1}\), and composition gives \(\rho_nz=y\).

Choose \(x_0\in Y_0\) and recursively choose \(x_{n+1}\in Y_{n+1}\) above \(x_n\). The preceding surjectivity justifies each step. Adjacent coherence implies every composite coherence equation, so this gives a point. This is an existence construction using countably many choices, not an asserted effective procedure for locating the stabilization indices.

Finally, fix a level \(n\). Every global point satisfies \(x_n=\rho_{n,m}(x_m)\) for each \(m\ge n\), hence \(x_n\in Y_n\). Conversely, start with any \(y\in Y_n\), lift recursively above level \(n\) through the surjections just proved, and define the lower coordinates by \(x_i=\rho_{i,n}(y)\). The composite restriction laws verify coherence across and below level \(n\). The resulting point evaluates to \(y\). These two inclusions prove the asserted equality of evaluation images, not merely nonemptiness of the inverse limit.
''','Prove stabilization, induced surjectivity, seeded lifting, and both evaluation-image inclusions.')

proof('06_boundaries.tex','KS57',r'''
Set \(T=\begin{pmatrix}A\\P\end{pmatrix}\) and \(b=\begin{pmatrix}0\\Px\end{pmatrix}\). A vector \(y\) is an exact protected answer if and only if \(Ty=b\). Perform Gaussian row operations on the augmented matrix, keeping their product \(U\). Each elementary row operation is invertible over the given field. Thus \(Ty=b\) and \(UTy=Ub\) have exactly the same solutions.

If no row of the reduced augmented system has zero left side and nonzero right side, assign arbitrary values to its free variables and solve for its pivot variables. This supplies a solution \(y_0\). For any vector \(y\),
\[
 Ty=b\quad\Longleftrightarrow\quad T(y-y_0)=0.
\]
Translation by \(y_0\) is therefore a bijection from \(\ker T\) to the answer set, with inverse \(y\mapsto y-y_0\). Rank--nullity applied to the actual linear map \(T:\mathbb F^n\to\mathbb F^{m+p}\) gives the ambiguity dimension. Dependent prescription rows do not alter this argument.

If the reduced system is inconsistent, choose a row with zero left side and right side \(\alpha\ne0\). Let \(w\) be the corresponding row of \(U\), and split it according to the two blocks as \(w=(u,v)\). The retained row operations give the literal identities
\[
 uA+vP=0,\qquad vPx=\alpha.
\]
Division is permitted because \(\alpha\) is a nonzero field element. Define \(\lambda=-\alpha^{-1}u\) and \(\mu=\alpha^{-1}v\). Multiplying the displayed equations by \(\alpha^{-1}\) gives
\[
 \lambda A=\mu P,\qquad \lambda Ax=\mu Px=1.
\]
For every admissible correction \(a\in\ker P\), these same row equations imply \(\lambda Aa=\mu Pa=0\). The witness therefore annihilates the entire correction image while taking value one on the required defect.

The alternatives cannot occur together. If \(y\) were an exact protected answer in the presence of such a witness, then
\[
 1=\lambda Ax=\mu Px=\mu Py=\lambda Ay=0.
\]
A field has \(1\ne0\), so this is impossible. Consistency or inconsistency of the reduced system proves exhaustiveness, and the contradiction proves exclusivity. Empty row or column blocks cause no extra division: normalization is used only in the inconsistent case, where the nonzero scalar has already been obtained. The proof does not transfer to integral coefficients by silently allowing the same division.
''','Carry row operations, field normalization signs, affine parametrization, exclusivity and degenerate dimensions explicitly.')

proof('05c_iteration.tex','KS71',r'''
For integers \(m>n\), apply the triangle inequality successively along the finite chain \(f_n,f_{n+1},\ldots,f_m\). It gives
\[
 \dist(f_n,f_m)\le\sum_{k=n}^{m-1}\dist(f_k,f_{k+1})
 \le\sum_{k=n}^{m-1}b_k\le\sum_{k=n}^{\infty}b_k.
\]
Given \(\varepsilon>0\), convergence of the nonnegative series supplies \(N\) for which the final tail is below \(\varepsilon\) whenever \(n\ge N\). Interchanging \(m,n\) when necessary proves the Cauchy condition for all pairs of indices at least \(N\). Completeness, not residual decay, is the hypothesis that now supplies a limit \(x\in M\).

Keep \(n\) fixed. The reverse triangle inequality says
\[
 \bigl|\dist(f_n,f_m)-\dist(f_n,x)\bigr|\le\dist(f_m,x)\longrightarrow0.
\]
Passing to the limit in the uniform tail bound proves the claimed distance certificate at that \(n\).

It remains to prove exactness of the limit. Fix \(\varepsilon>0\). Since \(\omega(f_m)\to0\), an entire tail of the sequence belongs to the sublevel set \(C_\varepsilon=\{z:\omega(z)\le\varepsilon\}\). Lower semicontinuity makes this set closed, so the limit of that tail belongs to it. Hence \(\omega(x)\le\varepsilon\) for every positive \(\varepsilon\). If \(\omega(x)>0\), choosing \(\varepsilon=\omega(x)/2\) contradicts this inequality. Since \(\omega\) is nonnegative, \(\omega(x)=0\). We have not used, or asserted, continuity of \(\omega\) or the stronger equality \(\omega(f_m)\to\omega(x)\) for arbitrary convergent inputs.
''','Give Cauchy and tail-limit quantifiers, then use closed sublevels rather than incorrectly upgrading lower semicontinuity to continuity.')

proof('05c_iteration.tex','KS72',r'''
The estimate \(\omega(f_n)\le Q_n\omega(f_0)\) follows by induction. At \(n=0\) it is equality. If it holds at \(n\), nonnegativity of \(q_n\) permits multiplication and gives
\[
 \omega(f_{n+1})\le q_n\omega(f_n)
 \le q_nQ_n\omega(f_0)=Q_{n+1}\omega(f_0).
\]
Because \(Q_n\to0\) and \(\omega(f_0)\) is a fixed finite number, the residual tends to zero. The movement assumption then gives
\[
 \dist(f_n,f_{n+1})\le C_nQ_n\omega(f_0).
\]
This is a summable nonnegative budget by the hypothesis on \(\sum C_nQ_n\). All assumptions of Theorem~\ref{KS71} now hold, and its tail certificate is exactly \eqref{eq:variable-tail}. If \(\omega(f_0)=0\), the same estimates make every step zero and every residual zero. No cancellation of that value was used.

For constant rates, the global estimate can be sharpened by restarting at the current index. Fix \(n\). A new induction on \(j\) gives
\[
 \omega(f_{n+j})\le q^j\omega(f_n),\qquad
 \dist(f_{n+j},f_{n+j+1})\le Cq^j\omega(f_n).
\]
Sum the finite chain from \(n\) to \(n+m\), and then let \(m\to\infty\) using the already established limit. The geometric series equals \(1/(1-q)\), including \(q=0\), where its first term is one and all later terms vanish. This proves the restarted bound. The variable-rate proof itself requires only nonnegative \(q_n\), decay of their cumulative products, and summability of the movement weights. It does not insert an unstated upper bound \(q_n<1\) at each step.
''','Separate the two inductions, summability and limiting argument, including zero residual and zero contraction cases.')

proof('05c_iteration.tex','KS73',r'''
The function \(f\mapsto\norm{df}\) is continuous because \(d\) is bounded linear and the norm is continuous. It is therefore an admissible lower semicontinuous residual for Theorem~\ref{KS71}. That theorem supplies a limit \(x\in E\), together with \(\norm{dx}=0\), which means \(dx=0\).

Continuity of \(p\) gives \(p(f_n)\to p(x)\). The left side is the constant sequence with value \(p(f_0)\). Uniqueness of limits in the normed target therefore gives \(p(x)=p(f_0)\). Define the actual vector \(a=f_0-x\). Linearity, rather than a closure argument, now yields
\[
 p(a)=p(f_0)-p(x)=0,\qquad da=df_0-dx=df_0.
\]
Thus \(a\in\ker p\) and \(df_0\in d(\ker p)\). Membership in this algebraic image is precisely what makes the class \([df_0]\) zero. Merely knowing membership in the closure of that image would not justify the same conclusion.
''','Construct the actual limiting admissible correction and distinguish image membership from closure membership.')

proof('05c_iteration.tex','KS74',r'''
For each \(n\), the triangle inequality gives
\[
 \dist(x,y)\le\dist(x,f_n)+\dist(f_n,g_n)+\dist(g_n,y)
 \le\dist(x,f_n)+\beta_n+\dist(g_n,y).
\]
Given any \(\varepsilon>0\), choose \(n\) large enough that the three terms on the right are each below \(\varepsilon/3\). Thus \(\dist(x,y)\le\varepsilon\) for every positive \(\varepsilon\), so the distance is zero. The metric separation axiom gives \(x=y\). In a pseudometric space only zero distance would follow without an additional separation hypothesis.

For the negative assertion let \(E=\R\times(\R\times\R)\), \(d(s,u,r)=r\), and \(p(s,u,r)=s\). Both \(x=(1,0,0)\) and \(y=(1,1,0)\) have zero defect and protected value one, but their middle coordinates differ. They are distinct points of the same feasible fiber. Constant sequences at those points meet exactness and preservation but not a vanishing comparison bound, so these conditions alone cannot imply path independence.
''','Write the three-distance estimate with metric separation and an explicit feasible-fiber counterexample.')

(ROOT/'audit/proof_detail/changes_finite_iteration.json').write_text(json.dumps(changes,indent=2)+'\n')
print(len(changes),'proofs expanded')
