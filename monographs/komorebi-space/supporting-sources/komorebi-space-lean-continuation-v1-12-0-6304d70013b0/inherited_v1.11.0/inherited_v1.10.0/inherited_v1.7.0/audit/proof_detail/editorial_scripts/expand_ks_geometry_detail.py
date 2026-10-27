from ks_proof_helpers import *
proof('05_geometry.tex','KS40',r'''
Write \(U_0=I\) and \(U_k=\tau_{i_0i_1}\cdots\tau_{i_{k-1}i_k}\) for \(1\le k\le m\). The transport convention makes every \(U_k\) a map from the fiber at \(i_k\) to that at \(i_0\). Since \(U_{k+1}=U_k\tau_{i_ki_{k+1}}\), the \(k\)-th transported defect is
\[
 U_k(dx)_{i_ki_{k+1}}
 =U_{k+1}x_{i_{k+1}}-U_kx_{i_k}.
\]
Summing over \(k=0,\ldots,m-1\) cancels each interior value once with each sign. The remaining terms are \(U_mx_{i_m}-U_0x_{i_0}=T_qx_{i_m}-x_{i_0}\), proving the identity with its actual ordered products. For an empty walk both sides are zero.

The triangle inequality and the operator norm bound now give
\[
 \norm{T_qx_{i_m}-x_{i_0}}
 \le\sum_{k=0}^{m-1}\norm{U_k}\norm{(dx)_{i_ki_{k+1}}}
 \le\left(\sum_{k=0}^{m-1}\prod_{j=0}^{k-1}\norm{\tau_{i_ji_{j+1}}}\right)\norm{dx}_\infty.
\]
The bracket is \(\gamma(q)\), with the empty product equal to one. Repeated vertices or edges do not affect the cancellation. Reordering the edge maps would, in general, invalidate it.
''','Type all prefix transports and exhibit each telescoping difference before taking the norm.')

proof('05_geometry.tex','KS41',r'''
Every \(T_i\) is a continuous linear equivalence, being a finite ordered composition of such maps. Reconstruction is therefore well defined. For an edge \((i,j)\), apply \(T_i\) to its defect:
\[
 T_i\bigl(\tau_{ij}T_j^{-1}z-T_i^{-1}z\bigr)
 =T_i\tau_{ij}T_j^{-1}z-z=K_{ij}z-z.
\]
Because \(T_i\) is injective, that edge defect is zero if and only if the corresponding root loop fixes \(z\). Thus \(dR_pz=0\) holds exactly for \(z\in K\). The root route is empty, so \((R_pz)_o=z\).

Conversely, let \(x\in\ker d\). The path telescope along \(p_i\) has all zero summands, hence \(T_ix_i=x_o\) for every vertex. Applying \(T_i^{-1}\) gives \(x_i=T_i^{-1}x_o\), so \(x=R_p(x_o)\). The first part then places \(x_o\) in \(K\). We have proved both inverse equations and uniqueness of an exact extension of a root value.

The maps are linear. On the finite vertex product,
\[
 \norm{R_pz}_\infty\le\left(\max_i\norm{T_i^{-1}}\right)\norm z,
 \qquad \norm{x_o}\le\norm x_\infty.
\]
These bounds also hold on the subspaces \(K\) and \(\ker d\), proving continuity of both directions. No completeness is needed for these finite bounds.

For route independence, the proved equivalence identifies \(K\) with the image of root evaluation from the intrinsically defined space \(\ker d\). That image does not refer to any chosen routes, so every route system yields the same \(K\). For \(z\in K\), reconstruction using either system is an exact family with root \(z\), and uniqueness makes the families equal. For \(z\notin K\), this uniqueness argument does not assert equality of the two generally inconsistent reconstructed families.
''','Derive fixed-space equivalence, bounded inverse maps and route independence only on the extendable locus.')

proof('05_geometry.tex','KS42',r'''
Boundedness of \(D\) makes \(K=\ker D\) closed. Lemma~\ref{lem:projection-tool} constructs \(q=P_K\) and gives the orthogonal decomposition \(x=qx+(x-qx)\). The first term belongs to \(K\), so \(Dqx=0\). Projection fixes every point of \(K\), giving \(q(qx)=qx\).

Pythagoras applied to that decomposition gives \(\norm x^2=\norm{qx}^2+\norm{x-qx}^2\), hence \(\norm{qx}\le\norm x\). For any \(y\in K\), the vector \(qx-y\) lies in \(K\), whereas \(x-qx\) lies in its orthogonal complement. Consequently
\[
 \norm{x-y}^2=\norm{x-qx}^2+\norm{qx-y}^2\ge\norm{x-qx}^2.
\]
Equality holds only when \(\norm{qx-y}=0\), or \(y=qx\). This proves nearest-point uniqueness without any closedness assumption on \(\ran D\). Closedness of the kernel and of the range serve different purposes.
''','Make the projection background explicit and separate kernel closedness from range closedness.')

proof('05_geometry.tex','KS44',r'''
First quantify the residual seen at the root. The identity \(\mathcal H=N_pdR_p\), applied to \(x_o\), gives
\[
 \begin{aligned}
 \norm{\mathcal H(x_o)}_\infty
 &=\norm{N_p\bigl(d(R_px_o-x)+dx\bigr)}_\infty\\
 &\le\norm{N_p}\bigl(\norm d\norm{R_px_o-x}_\infty+\norm{dx}_\infty\bigr)\\
 &\le\norm{N_p}(\norm d A_p+1)\norm{dx}_\infty.
 \end{aligned}
\]
Closed range of \(\mathcal H\) lets Theorem~\ref{KS43} control the anchor correction by
\(\norm{x_o-qx_o}\le\kappa\norm{\mathcal H(x_o)}_\infty\). Insert the uncorrected reconstruction between \(x\) and \(Px=R_pqx_o\):
\[
 \norm{x-Px}_\infty
 \le\norm{x-R_px_o}_\infty+\norm{R_p}\norm{x_o-qx_o}.
\]
Substituting the two preceding bounds yields \eqref{eq:graphgain}. The finite maximum-norm residual product is a Banach space because its fiber is Hilbert, so the target completeness needed in Theorem~\ref{KS43} is available.

For necessity, suppose a constant \(C\) satisfies
\(\dist(w,\ker d)\le C\norm{dw}_\infty\) for every vertex family \(w\). Fix \(z\in K^\perp\) and take \(w=R_pz\). Every exact family \(e\) has \(e_o\in K\), and root evaluation has norm at most one. Therefore
\[
 \norm z=\dist(z,K)\le\norm{z-e_o}\le\norm{R_pz-e}_\infty.
\]
Taking the infimum over \(e\in\ker d\) is legitimate without assuming that this global nearest point is attained. It gives
\[
 \norm z\le C\norm{dR_pz}_\infty
 \le C\norm{N_p^{-1}}\norm{\mathcal Hz}_\infty.
\]
Here \(N_p\) is a continuous linear equivalence on the finite edge product because every component \(T_i\) is one. For a general root vector, remove its projection onto \(K\); this leaves the same \(\mathcal H\)-image and puts it in \(K^\perp\). Thus the displayed estimate is a uniform residual bound of the kind in Theorem~\ref{KS43}, which forces \(\ran\mathcal H\) to be closed. A finite-dimensional fiber makes that image finite dimensional and hence closed. It does not give a uniform numerical value of the inverse gain across different connections.
''','Derive every amplification factor and prove necessity using infima, without assuming a global nearest exact family.')

proof('05_geometry.tex','KS46',r'''
The subspace \(L=\ker D\) is closed, hence Hilbert with the inherited inner product. The restriction \(B=C|_L\) is continuous, so its kernel is a closed subspace of \(L\). Under the inclusion into \(E\), this kernel is exactly \(M=L\cap\ker C\). Thus both projections used to define \(P\) exist.

For an input \(x\), write \(\ell=P_Lx\) and let \(Px\) be the projection of \(\ell\) onto \(\ker B\) inside \(L\). Then \(Px\in M\), \(u=x-\ell\in L^\perp\), and \(v=\ell-Px\in L\) is orthogonal to \(M\). Since \(M\subseteq L\), the vector \(u\) is also orthogonal to \(M\). Their sum \(x-Px=u+v\) is therefore orthogonal to \(M\). A vector in \(M\) with that error is its unique orthogonal projection, so \(P=P_M\).

The two errors themselves are orthogonal because \(u\in L^\perp\) and \(v\in L\). Expanding the squared norm of their sum gives \(\norm{x-Px}^2=\norm u^2+\norm v^2\). Finally \(\ker(D,C)=\ker D\cap\ker C=M\), so this is also the projection onto the kernel of the joint defect. The proof uses a second projection \emph{inside} \(L\). Replacing it by the ambient projection onto \(\ker C\) would invalidate the membership step and need not preserve local exactness.
''','Establish the inherited Hilbert structures and orthogonal decomposition, not ambient projection commutation.')

proof('05_geometry.tex','KS51',r'''
The vector \(v_t=(-t,1)\) spans \(\ker D_t\) and has squared norm \(1+t^2>0\). Projection onto this line is
\[
 x\longmapsto\frac{\langle x,v_t\rangle}{1+t^2}v_t,
\]
which gives the matrix in \eqref{eq:lineprojector}. In particular it is the orthogonal projector, not merely a map whose image is contained in the kernel.

Subtract \(q_0=\operatorname{diag}(0,1)\), obtaining the symmetric matrix
\[
 B_t=q_t-q_0=\frac1{1+t^2}
 \begin{pmatrix}t^2&-t\\-t&-t^2\end{pmatrix}.
\]
The two off-diagonal entries of its square are zero, since \(-t^3+t^3=0\). Both diagonal entries are \((t^4+t^2)/(1+t^2)^2=t^2/(1+t^2)\). Thus
\[
 B_t^{\mathsf T}B_t=B_t^2=\frac{t^2}{1+t^2}I.
\]
Pairing this identity with an arbitrary vector proves the all-vector norm formula. It bounds the operator norm above by \(|t|/\sqrt{1+t^2}\), and evaluating any unit vector gives equality. The argument includes \(t=0\), where both sides vanish.

For the common section \(A(r)=(r,0)\), the perturbation inverse leaves \(A\) unchanged because \(D_tA=I\). The constructed transport is therefore \(Jx=x-AD_tx\) on the old kernel. At \(x=(0,b)\), it gives \((-tb,b)\). Substitution into the projection formula gives instead \((-tb/(1+t^2),b/(1+t^2))\). The strict-radius theorem applies when \(|t|<1\), but these explicit line and projection calculations are valid for every real \(t\).
''','Compute the matrix square and unit-vector lower bound; distinguish general theorem radius from all-real formulas.')

proof('05a_certificates.tex','KS70',r'''
Let \(q=P_{\ker D}\), and write \(u=x-qx\). The stated kernel inclusion makes both \(Dqx\) and \(\widetilde Dqx\) zero. Hence \(Du=Dx\) and \(\widetilde Du=\widetilde Dx\). Applying the reference residual bound to \(u\), whose projection onto \(\ker D\) is zero, gives
\[
 \begin{aligned}
 \norm u&\le C\norm{Du}
 \le C\norm{\widetilde Du}+C\norm{(D-\widetilde D)u}\\
 &\le C\norm{\widetilde Dx}+C\varepsilon\norm u.
 \end{aligned}
\]
Subtract the final term. The strict inequality \(C\varepsilon<1\) makes \(1-C\varepsilon\) positive, so division preserves the inequality and gives the claimed residual estimate. This also covers \(C=0\) without division by \(C\).

If \(\widetilde Dx=0\), the same estimate forces \(u=0\), hence \(x=qx\in\ker D\). This is the inclusion not initially assumed. Combining it with the supplied inclusion proves \(\ker\widetilde D=\ker D\), and their orthogonal projections coincide in the fixed Hilbert geometry. Finally \(\norm{\widetilde Dx-y}\le\eta\) gives \(\norm{\widetilde Dx}\le\norm y+\eta\). Substitution proves the measured certificate. The kernel-preservation hypothesis is what removed \(qx\) before applying the perturbation estimate. Without it, one obtains a term proportional to \(\norm x\), not the absorbable term proportional to \(\norm u\).
''','Locate the use of old-kernel preservation and strict positivity before absorbing the perturbation.')

proof('05d_floors.tex','KS76',r'''
The set of candidate distances is nonempty because \(0\in B\), bounded below by zero, and contains the finite value \(\norm\Omega\). Its infimum is therefore a finite nonnegative real, and the defining lower-bound property gives \(\nu_B(\Omega)\le\norm{\Omega-b}\) for every \(b\in B\).

Suppose \(\nu_B(\Omega)=0\) and fix \(\varepsilon>0\). There must be \(b\in B\) with \(\norm{\Omega-b}<\varepsilon\). Otherwise every candidate distance would be at least \(\varepsilon\), making \(\varepsilon\) a lower bound and forcing the infimum to be at least \(\varepsilon\), a contradiction. Thus every open ball about \(\Omega\) meets \(B\), which is the closure criterion.

Conversely, if \(\Omega\in\overline B\), every such ball supplies \(b\) with \(\norm{\Omega-b}<\varepsilon\). The infimum then lies between zero and \(\varepsilon\) for every positive \(\varepsilon\), so it is zero. If \(B\) is closed, membership in its closure is exactly membership in \(B\). No step asserts that the infimum has a minimizing element when \(B\) is not closed, and closedness alone is being used here only for the zero-floor membership conclusion.
''','Make both infimum/closure implications explicit and avoid silently asserting attainment.')

(ROOT/'audit/proof_detail/changes_geometry_detail.json').write_text(json.dumps(changes,indent=2)+'\n')
print(len(changes),'proofs expanded')
