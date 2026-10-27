from ks_proof_helpers import *
proof('03_towers.tex','KS21',r'''
Put \(B_n=I-s_n\rho^Y_n\). Since \(\rho^Y_ns_n=I\), direct multiplication gives
\[
 B_n^2=B_n,\qquad \rho^Y_nB_n=0,\qquad B_ns_n=0.
\]
Moreover, \(B_ny=y\) whenever \(\rho^Y_ny=0\). Thus \(B_n\) really projects onto the target kernel. Its norm is at most \(1+SB_Y\). Coordinate zero of \(p_L\) is the identity, and every later coordinate applies \(B_n\), so \(p_L^2=p_L\) and \(\norm{p_L}\le1+SB_Y\). In particular the formula defines a map on the bounded product, not just on arbitrary coordinate families.

The recurrence for \(Ar\) gives zero seed and places \((Ar)_{n+1}\) in the image of \(s_n\). The identities just proved make all its innovations zero. Therefore \(p_LA=0\), and
\[
 p_LP=p_L(I-A\partial)=p_L.
\]
We next prove separation on the exact space. If \(f\) is exact, its restriction equation rewrites as
\[
 f_{n+1}=s_n\rho^Y_nf_{n+1}+B_nf_{n+1}
          =s_nf_n\rho^X_n+N_n(f).
\]
Two exact families with the same seed and innovations agree first at level zero and then at every later level by this recurrence. More generally, if two arbitrary families have the same observable and differential, their difference is exact with zero observable, so separation on the exact space makes their difference zero.

The proposed chart has the claimed target because \(p_L(p_Lf)=p_Lf\). Given \(s\in\mathcal S_L\) and \(r\in R\), set \(f=Ps+Ar\). The preceding identities and \(\partial A=I\) give
\[
 p_Lf=p_Ls=s,\qquad \partial f=r.
\]
This proves one round trip. For the other, \(f\) and \(P(p_Lf)+A\partial f\) have the same observable and residual, so the joint separation just proved identifies them. All maps are linear and bounded on their indicated subspaces and finite products, establishing a continuous linear equivalence.

Finally, \(Pf\) has coordinates \((p_Lf,0)\). Any exact answer with the same observable has those same two coordinates, hence equals \(Pf\). This uniqueness is relative to the complete observable of seed and innovations. It is not obtained by assuming that the seed alone determines an exact growing-target family.
''','Verify projection identities and bounded products before the observable separation and both chart inverses.')

proof('03a_observation.tex','KS62',r'''
Realized equality follows from eventual equality by the preceding theorem, so only its converse remains. Suppose \(|f|=|g|\). Fix the output level \(n\), and let \(k=\max\{\phi(n),\psi(n)\}\). To prove equality of two maps defined on \(X_k\), fix an arbitrary element \(a\in X_k\). The assumed surjectivity of \(\operatorname{ev}_k\) supplies a coherent point \(x\) with \(x_k=a\). Equality of the two realized maps gives equality of their output coordinates:
\[
 f_n(x_{\phi(n)})=g_n(x_{\psi(n)}).
\]
Coherence of \(x\) rewrites this as
\[
 f_n\bigl(\rho^X_{\phi(n),k}(a)\bigr)
 =g_n\bigl(\rho^X_{\psi(n),k}(a)\bigr).
\]
The index \(k\) was selected before \(a\), so this is one common finite-stage equality for \emph{all} elements of \(X_k\). It is exactly the witness required by eventual equality at output \(n\). Repeating for each \(n\) proves faithfulness.

For the sufficient condition on bonding maps, fix \(k\) and \(a\in X_k\). Define coordinates below \(k\) by restriction of \(a\). At each later stage use surjectivity of the adjacent bonding map to choose a preimage of the coordinate already chosen. Recursion with classical choice constructs the upper tail. Adjacent equations hold by construction, and induction on the interval length gives every composite equation. This produces a point evaluating to \(a\). If a fiber is empty, the statement that each of its elements lifts is vacuous, as required by surjectivity onto that fiber. Without the projection-surjectivity assumption, equality on realizable inputs alone need not identify finite maps on values that never occur in a global point.
''','Use one common stage before elementwise lifting, then prove the source projection-surjectivity criterion.')

proof('03a_observation.tex','KS64',r'''
Let \(s:X\to X_\theta\) be sampling, with schedule \(\theta\) and identity level maps. For recovery choose the least \(j(n)\) with \(n\le\theta(j(n))\). Unboundedness makes this set nonempty. Increasing \(n\) only strengthens the inequality, so \(j\) is monotone. The level map of \(r:X_\theta\to X\) is \(\rho^X_{n,\theta(j(n))}\). Composite restriction proves its naturality.

The composite \(rs:X\to X\) reads level \(\theta(j(n))\) and restricts to \(n\). At that very stage its map agrees with the identity transport after restriction from \(\theta(j(n))\) to \(n\). Thus \(rs\) is eventually equal to the identity.

For \(sr:X_\theta\to X_\theta\), the schedule at output \(n\) is \(j(\theta(n))\), and the level map is \(\rho^X_{\theta(n),\theta(j(\theta(n)))}\). Compare it with the identity at a sampled index
\[
 k\ge\max\{n,j(\theta(n))\}.
\]
Restricting either route from level \(k\) of the sampled system gives the same original restriction \(\rho^X_{\theta(n),\theta(k)}\). This proves eventual equality even when \(\theta\) has repeated values. Hence the two classes are inverse isomorphisms, without requiring them to be literal inverse schedules.

Write \(s_X,r_X\) and \(s_Y,r_Y\) for the sampling and recovery isomorphisms of source and target. The asserted Hom map is
\[
 [f]\longmapsto s_Y[f]r_X,
\]
with inverse \([g]\mapsto r_Y[g]s_X\). Associativity and the two inverse equations cancel the inserted pairs, proving both round trips. Applying the realization functor transports these equations to point spaces, where sampling and recovery are the cofinal point equivalences already constructed. No norm invariance or surjectivity of source point projections is needed for this categorical conjugation argument.
''','Supply both eventual-identity witnesses for repeated schedules and the explicit conjugation inverse.')

proof('03b_repair_transport.tex','KS65',r'''
The identity \(dA=I\) gives \(dP_A=d-dAd=0\), so the proposed first chart coordinate actually belongs to \(K\). If \(u\in K\), then \(du=0\) and \(P_Au=u\). Therefore, for \((u,r)\in K\times R\),
\[
 d(u+Ar)=r,\qquad P_A(u+Ar)=u+Ar-A(r)=u.
\]
In the other direction, \(P_Ax+A(dx)=x-Adx+Adx=x\). These are both inverse equations, including the membership condition for the kernel coordinate. All component maps are bounded linear, so they define a continuous linear equivalence on the standard finite product. Applied to \(P_Ax\), the chart gives \((P_Ax,0)\), proving the repair formula.

For a second right inverse \(B\), the equation \(d(A-B)=I-I=0\) places its difference from \(A\) in \(K\). Direct subtraction gives
\[
 P_B-P_A=(I-Bd)-(I-Ad)=(A-B)d.
\]
Both projections have range \(K\) and fix every point of \(K\). Thus applying \(P_A\) after \(P_B\) gives \(P_B\), while applying \(P_B\) after \(P_A\) gives \(P_A\). These two compositions are equal if and only if the projections are equal.

If \(P_A=P_B\), evaluate their difference at \(Ar\). Since \(dAr=r\), the difference formula yields \((A-B)r=0\) for every \(r\), hence \(A=B\). Equality of sections conversely makes their projection formulas identical. The argument uses the right inverse to test every residual. It does not infer equality of sections merely from agreement on some restricted set of observed residuals.
''','Check kernel membership, both chart identities, commuting-projection equations and the section test.')

proof('03b_repair_transport.tex','KS66',r'''
First \(DS=Cd\) sends \(\ker d\) into \(\ker D\), and
\[
 DM=DSA-DBC=CdA-C=C-C=0.
\]
Thus both terms in the proposed exact coordinate have the correct codomain. Given \(u\in\ker d\), compute the residual and exact coordinates of \(S(u+Ar)\) separately:
\[
 DS(u+Ar)=Cr,\qquad
 S(u+Ar)-BCr=Su+(SA-BC)r.
\]
This proves the triangular formula as an equality in \(\ker D\times T\).

For a general input, use the same commuting square to obtain
\[
 \begin{aligned}
 P_BSx-SP_Ax
 &=Sx-BDSx-Sx+SAdx\\
 &=(SA-BC)dx=M(dx).
 \end{aligned}
\]
Its norm is at most \(\norm M\norm{dx}\). The triangle inequality and submultiplicativity give \(\norm M\le\norm S\norm A+\norm B\norm C\). Exact inputs have \(dx=0\), so the two routes agree there regardless of the section choices. If they agree on \emph{every} input, substitute \(x=Ar\). Then \(dAr=r\) makes \(Mr=0\) for each residual, hence \(SA=BC\). That equality conversely makes the discrepancy vanish everywhere.

For composition, denote the three sections by \(A,B,A_2\). The composite residual map is \(C_2C_1\), so its mismatch is \(S_2S_1A-A_2C_2C_1\). Insert and subtract \(S_2BC_1\):
\[
 \begin{aligned}
 S_2S_1A-A_2C_2C_1
 &=S_2(S_1A-BC_1)+(S_2B-A_2C_2)C_1\\
 &=S_2M_1+M_2C_1.
 \end{aligned}
\]
All terms map the first residual space into the last candidate space, in the written order. Finally, for fixed bounded \(M\), the estimate \(\norm{M(dx_j)}\le\norm M\norm{dx_j}\) proves convergence of the discrepancy when \(dx_j\to0\). Allowing the section or representation norms to grow with \(j\) would require a separate uniform bound.
''','Keep exact-valued mismatch typed and expand the fixed-map convergence and composition law.')

proof('03b_repair_transport.tex','KS67',r'''
For a bounded candidate family, \(\sup_n\norm{f_{\phi(n)}}\le\sup_k\norm{f_k}\), proving the sampling bound. For a bounded residual family, each summand in \eqref{eq:block-defect-sum} is a map from \(X_b\) to \(Y_a\) and has norm at most \(\norm r_\infty\), because every composite bond is contractive. A selected block has length at most \(m\), so the triangle inequality bounds its sum by \(m\norm r_\infty\). Taking the supremum over blocks proves that \(C_\phi\) maps into the bounded residual product and has the asserted operator norm. If a block has length zero its sum is zero, in agreement with the identity restriction.

To verify the commuting square, insert
\(r_k=\rho^Y_kf_{k+1}-f_k\rho^X_k\). The \(k\)-th term becomes
\[
 \rho^Y_{a,k+1}f_{k+1}\rho^X_{k+1,b}
 -\rho^Y_{a,k}f_k\rho^X_{k,b}.
\]
Successive internal terms cancel in the finite sum, leaving \(\rho^Y_{a,b}f_b-f_a\rho^X_{a,b}\). This is exactly the sampled differential. No infinite series interchange is involved.

If the fine differential vanishes, the finite telescope is zero on every selected interval. That conclusion remains true for unbounded gap lengths, because each individual interval is finite. What may fail without a gap bound is boundedness of the residual transformation on \emph{arbitrary} bounded residual families, not preservation of exact inputs.

When the two bounded sections exist, Theorem~\ref{KS66} applies to the commuting square just established. Substitute \(\norm{S_\phi}\le1\) and \(\norm{C_\phi}\le m\) in its estimate to get \((\norm A+m\norm B)\norm{\partial f}\). Existence of those sections is an additional hypothesis, not a consequence of the sampling estimate.
''','Prove actual telescoping and bounded-product membership, separating unbounded-gap exactness from residual boundedness.')

proof('04_symmetry.tex','KS32',r'''
Take \(h\in H_U\). Its pointwise product with the chosen extension \(x_0\) agrees with the prescribed data on \(U\), because \(h|_U=1\). For an arrow \(f:v\to w\), the coefficient homomorphism preserves multiplication and the two coherence equations give
\[
 c_f f^*((x_0)_wh_w)
 =c_f f^*((x_0)_w)f^*(h_w)
 =(x_0)_vh_v.
\]
Thus \(x_0h\) is another twisted extension.

Conversely, if \(x\) is a twisted extension of the same prescribed data, define \(h_v=(x_0)_v^{-1}x_v\). On \(U\) its value is one. For every arrow,
\[
 \begin{aligned}
 h_v
 &=[c_f f^*((x_0)_w)]^{-1}[c_f f^*(x_w)]\\
 &=f^*((x_0)_w)^{-1}c_f^{-1}c_f f^*(x_w)\\
 &=f^*((x_0)_w^{-1}x_w)=f^*(h_w).
 \end{aligned}
\]
The cancellation uses inverse multiplication in its actual order. No commuting factors have been moved past one another. Hence \(h\in H_U\). Pointwise group cancellation shows that \(h\mapsto x_0h\) and \(x\mapsto x_0^{-1}x\) are inverse maps.

The extension set is nonempty precisely when the earlier orbit obstruction is neutral. Once it is nonempty, the displayed bijection makes it a singleton precisely when \(H_U\) has only its identity element. Both conditions are needed for unique existence. Changing the chosen extension changes the parametrization, not the extension set or the criterion.
''','Retain multiplication order, the boundary condition and both torsor inverses.')

(ROOT/'audit/proof_detail/changes_comparisons.json').write_text(json.dumps(changes,indent=2)+'\n')
print(len(changes),'proofs expanded')
