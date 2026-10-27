from ks_proof_helpers import *

proof('05h_regularized_repair.tex','WR06',r'''
\emph{Step 1: the normal operator has an actual bounded inverse.} Let $B=T^*T+\alpha I:H\to H$. It is bounded and self-adjoint. For every $h\in H$,
\[
 \langle Bh,h\rangle=\norm{Th}^2+\alpha\norm h^2
 \ge\alpha\norm h^2.
\]
If $h\ne0$, Cauchy--Schwarz and division by $\norm h$ give $\norm{Bh}\ge\alpha\norm h$. The same inequality holds at zero. It implies injectivity of $B$.

To prove closedness of its range, suppose $Bh_n\to y$. Applying the lower bound to $h_n-h_m$ gives
\[
 \norm{h_n-h_m}\le\alpha^{-1}\norm{Bh_n-Bh_m}.
\]
Thus $h_n$ is Cauchy. Completeness of $H$ supplies a limit $h$, and continuity gives $Bh=y$. If $y$ is orthogonal to the range of $B$, then for every $h$,
\[
 0=\langle Bh,y\rangle=\langle h,By\rangle.
\]
Taking $h=By$ gives $By=0$, and injectivity gives $y=0$. A closed subspace with zero orthogonal complement is the whole Hilbert space, so $\ran B=H$.

The inverse therefore exists. Its linearity follows from uniqueness of preimages, and its bound is $\norm{B^{-1}y}\le\alpha^{-1}\norm y$. This construction does not assume closedness of $\ran T$. It uses the positive term $\alpha I$ in the normal operator.

\emph{Step 2: define the optimizer and prove its normal equation.} Set $a_\alpha=B^{-1}T^*r$. Then $Ba_\alpha=T^*r$, or equivalently
\[
 T^*(Ta_\alpha-r)+\alpha a_\alpha=0.
\]
Because the construction takes place in $H=\ker p$, it already satisfies the exact protection requirement.

\emph{Step 3: prove global minimality, rather than just stationarity.} Write any proposed correction as $a=a_\alpha+h$ and set $s=Ta_\alpha-r$. Expanding both squared norms gives
\[
\begin{aligned}
 J_\alpha(a_\alpha+h)-J_\alpha(a_\alpha)
 &=\norm{Th}^2+\alpha\norm h^2
     +2\langle s,Th\rangle+2\alpha\langle a_\alpha,h\rangle\\
 &=\norm{Th}^2+\alpha\norm h^2
     +2\langle T^*s+\alpha a_\alpha,h\rangle\\
 &=\norm{Th}^2+\alpha\norm h^2.
\end{aligned}
\]
This is the asserted energy identity. It is nonnegative and, since $\alpha>0$, vanishes only for $h=0$. Therefore $a_\alpha$ is the unique global minimizer. In the zero correction space, the same construction and identities reduce to its single element, zero.''','Construct the inverse from coercivity, show onto-ness rather than assume it, and expand every mixed term in the objective.')

proof('05h_regularized_repair.tex','WR07',r'''
Let $A_\alpha=\norm{a_\alpha}^2$ and $R_\alpha=\norm{r-Ta_\alpha}^2$. Comparing the two admissible minimizers in each other's objectives gives
\[
 R_\alpha+\alpha A_\alpha\le R_\gamma+\alpha A_\gamma,
 \qquad R_\gamma+\gamma A_\gamma\le R_\alpha+\gamma A_\alpha.
\]
Add these inequalities and cancel the residual terms. The result is
\[
 (\gamma-\alpha)(A_\alpha-A_\gamma)\ge0.
\]
Since $\gamma>\alpha$, it follows that $A_\alpha\ge A_\gamma$. Return to the first comparison to obtain
\[
 R_\alpha-R_\gamma\le\alpha(A_\gamma-A_\alpha)\le0.
\]
Taking square roots, which preserves order for nonnegative numbers, proves both monotonicity statements.

At $M_\alpha=\norm{a_\alpha}$, the vector $a_\alpha$ is budget-feasible. If another correction $a$ in that ball had strictly smaller residual norm, then
\[
 J_\alpha(a)
 =\norm{r-Ta}^2+\alpha\norm a^2
 <\norm{r-Ta_\alpha}^2+\alpha\norm{a_\alpha}^2,
\]
contradicting its defining minimality. Thus it attains the budget frontier.

For the witness statement, let $v=r-Ta_\alpha\ne0$. The normal equation gives $T^*v=\alpha a_\alpha$. Also $r=v+Ta_\alpha$, hence
\[
 \langle r,v\rangle
 =\norm v^2+\langle a_\alpha,T^*v\rangle
 =\norm v^2+\alpha\norm{a_\alpha}^2.
\]
For $z=v/\norm v$, the support penalty is
\[
 M_\alpha\norm{T^*z}
 =\frac{\alpha\norm{a_\alpha}^2}{\norm v}.
\]
Subtracting it from $\langle r,z\rangle$ yields $\norm v=\beta(M_\alpha)$, so this is an optimizing witness. This calculation also covers a zero correction $a_\alpha$ with nonzero residual. If $v=0$, normalization is unavailable, but the zero witness attains the zero budget residual.''','Keep the sign of each parameter comparison explicit and compute the normalized witness penalty.')

proof('05h_regularized_repair.tex','WR08',r'''
\emph{Step 1: identify the unavoidable component.} Since $r-b\perp\overline{\ran T}$, the adjoint identity gives $T^*(r-b)=0$. Thus $a_\alpha(r)=a_\alpha(b)$. For every correction the orthogonal decomposition is
\[
 \norm{r-Ta}^2=q^2+\norm{b-Ta}^2.
\]
In particular both the residual square and the minimum objective are at least $q^2$.

\emph{Step 2: take the small-parameter limit in the correct order.} Let $\epsilon>0$. Since $b$ lies in the closure of the range, choose a single $a\in H$ with $\norm{r-Ta}^2<q^2+\epsilon$. This $a$ is chosen before $\alpha$. Minimality gives
\[
 q^2\le\norm{r-Ta_\alpha}^2
 \le J_\alpha(a_\alpha)
 \le q^2+\epsilon+\alpha\norm a^2.
\]
For sufficiently small $\alpha$, the last term is below $q^2+2\epsilon$ (and if $a=0$ it is already below $q^2+\epsilon$). Hence both intervening quantities tend to $q^2$. Their difference is $\alpha\norm{a_\alpha}^2$, which tends to zero. The orthogonal decomposition now implies $\norm{Ta_\alpha-b}^2\to0$, and taking square roots gives the first two limits.

\emph{Step 3: when the projected datum is attained, obtain a uniform bound.} Suppose $b\in\ran T$. The preimage set is a nonempty closed affine subset, so projection of zero supplies its unique minimum-norm element $a^\dagger$. Comparing with it and subtracting $q^2$ gives
\[
 \norm{Ta_\alpha-b}^2+\alpha\norm{a_\alpha}^2
 \le\alpha\norm{a^\dagger}^2.
\]
Thus $\norm{a_\alpha}\le\norm{a^\dagger}$ for every $\alpha>0$. This bound does not follow merely from the previously proved vanishing weighted penalty.

\emph{Step 4: strengthen weak convergence to norm convergence.} Take an arbitrary sequence $\alpha_n\downarrow0$, or more generally positive $\alpha_n\to0$. The bound supplies a weakly convergent subsequence $a_{\alpha_{n_k}}\rightharpoonup a$. Since its images converge in norm to $b$, the adjoint pairing argument of WR01 yields $Ta=b$. Weak lower semicontinuity gives
\[
 \norm a\le\liminf_k\norm{a_{\alpha_{n_k}}}
 \le\norm{a^\dagger}.
\]
Minimality and uniqueness of $a^\dagger$ force $a=a^\dagger$. Moreover the same lower bound, together with the uniform upper bound, gives convergence of the norms to $\norm{a^\dagger}$. In a real Hilbert space,
\[
 \norm{a_{\alpha_{n_k}}-a^\dagger}^2
 =\norm{a_{\alpha_{n_k}}}^2+\norm{a^\dagger}^2
       -2\langle a_{\alpha_{n_k}},a^\dagger\rangle\longrightarrow0.
\]
Thus this subsequence converges strongly. If the full positive-parameter family failed to converge strongly, there would be an $\epsilon>0$ and parameters $\alpha_n\to0$ whose corrections all stayed at distance at least $\epsilon$ from $a^\dagger$. The argument just given would produce a strongly convergent subsequence of them, a contradiction. This proves the limit for the entire parameter family.

\emph{Step 5: in the unattained case the norms tend to infinity.} If $b\notin\ran T$ and the norms failed to tend to infinity, there would exist $M<\infty$ and positive $\alpha_n\to0$ with $\norm{a_{\alpha_n}}\le M$. Their images still tend to $b$ by Step 2. WR01 would then put $b$ in the actual range, a contradiction. This proves divergence of the norms, not just unboundedness somewhere along the path.''','Give all epsilon/subsequence quantifiers, distinguish vanishing penalty from boundedness, and justify full-family strong convergence.')

proof('05h_regularized_repair.tex','WR09',r'''
Both corrections are constructed at the same positive parameter and in the same Hilbert correction space. Let $h=a_\alpha(\widetilde r)-a_\alpha(r)$ and $e=\widetilde r-r$. Subtract the two normal equations to obtain
\[
 (T^*T+\alpha I)h=T^*e.
\]
Pair with $h$ and use the adjoint identity:
\[
 \norm{Th}^2+\alpha\norm h^2
 =\langle e,Th\rangle\le\delta\norm{Th}.
\]
Put $t=\norm{Th}\ge0$. If $t>0$, dropping the nonnegative penalty and dividing by $t$ gives $t\le\delta$. If $t=0$, that inequality is already true. Completing the scalar square gives
\[
 \alpha\norm h^2\le\delta t-t^2
 =\frac{\delta^2}{4}-(t-\delta/2)^2
 \le\frac{\delta^2}{4}.
\]
Because $\alpha>0$, taking square roots proves the correction bound. This also explains why the coefficient is $1/(2\sqrt\alpha)$ rather than the coarser $\norm T/\alpha$ obtained by bounding the inverse alone.

For sharpness at a fixed parameter, take $H=Y=\R$ and $T=\sqrt\alpha\,I$. The solution map is multiplication by
\[
 \frac{\sqrt\alpha}{\alpha+\alpha}=\frac1{2\sqrt\alpha}.
\]
Any nonzero data perturbation attains the first bound. This is worst-case sharpness across operators at that parameter, not a claim of equality for every fixed operator and every parameter.

For the limiting statement, insert the exact-data correction at the selected parameter:
\[
 \norm{a_{\alpha(\delta)}(\widetilde r)-a^\dagger}
 \le\frac{\delta}{2\sqrt{\alpha(\delta)}}
       +\norm{a_{\alpha(\delta)}(r)-a^\dagger}.
\]
The first term tends to zero by the noise/parameter hypothesis. The second tends to zero by the attained-projection case of WR08, because the selected parameter tends to zero. Both statements require the same fixed operator and Hilbert metrics. The conclusion is a least-squares correction when the unavoidable residual component is nonzero.''','Show the scalar square-completion and sharpness separately from the written limiting argument.')

proof('05i_diagonal_regularization.tex','WR10',r'''
For $n>m$, one has $(a_n^{(m)})^2\le m^4/n^4$, so the correction sequence is square-summable. The diagonal operator is bounded with norm one, and $w=(1/n)\in\ell^2$, hence the residual sequence is also in $\ell^2$. The operator is self-adjoint, and the coordinate equality
\[
 \frac1n\frac{n}{m^2+n^2}
 =m^{-2}\frac{m^2}{m^2+n^2}
\]
proves $T^*v^{(m)}=\alpha a^{(m)}$ as an equality of Hilbert vectors. WR06 therefore identifies this actual infinite vector as the unique minimizer, rather than just a coordinatewise candidate.

For $1\le n\le m$, $m^2/(m^2+n^2)\ge1/2$. There are $m$ such coordinates, so $A_m\ge m/4$. For the upper bound, the first $m$ squares are at most one, and the decreasing function $x^{-4}$ gives
\[
 \sum_{n>m}\frac1{n^4}\le\int_m^\infty x^{-4}\,dx=\frac1{3m^3}.
\]
Thus $A_m\le m+m^4/(3m^3)=4m/3$.

For $n\le m$, the residual square is at most $n^2/m^4$. The exact identity
\[
 \sum_{n=1}^m n^2=\frac{m(m+1)(2m+1)}6\le m^3
\]
holds for $m\ge1$, so this part contributes at most $1/m$. For $n>m$, each residual square is at most $1/n^2$, whose tail is at most $1/m$. This proves $B_m\le2/m$.

For the lower bound, $n>m$ implies $m^2+n^2\le2n^2$, hence
\[
 \frac{n^2}{(m^2+n^2)^2}\ge\frac1{4n^2}.
\]
The other direction of the decreasing-function integral comparison gives
\[
 \sum_{n>m}\frac1{n^2}\ge\int_{m+1}^\infty x^{-2}\,dx=\frac1{m+1}.
\]
This proves $B_m\ge1/(4(m+1))$.

Finally, for $K\ge m$, both omitted tails consist of nonnegative terms. Bound the first by $m^4\sum_{n>K}n^{-4}$ and the second by $\sum_{n>K}n^{-2}$. The same upper integral comparisons give the two certified remainders in \eqref{eq:soft-tails}. No finite truncation is substituted for an equality of infinite energies.''','Verify Hilbert membership before coordinate optimality and state both directions of each integral tail comparison.')

proof('05i_diagonal_regularization.tex','WR11',r'''
\emph{Step 1: control the infinite Riemann sums uniformly.} Define
\[
 f(x)=\frac1{(1+x^2)^2},\qquad
 g(x)=\frac{x^2}{(1+x^2)^2}.
\]
Then $A_m/m=m^{-1}\sum_{n\ge1}f(n/m)$ and $mB_m=m^{-1}\sum_{n\ge1}g(n/m)$. Fix $L\ge2$ and put $N=\lfloor mL\rfloor$. On $[0,L]$, both functions are uniformly continuous. If $\omega_f(h)$ is a modulus of continuity there, comparison on the $N$ intervals of length $1/m$ gives
\[
 \left|\frac1m\sum_{n=1}^N f(n/m)-\int_0^{N/m}f(x)\,dx\right|
 \le L\omega_f(1/m).
\]
The missing interval $[N/m,L]$ has length below $1/m$ and a bounded integrand, so it contributes a term tending to zero. The same argument applies to $g$. This proves convergence of each truncated sum to its integral on $[0,L]$.

The tails require a bound independent of sufficiently fine discretization. Since $N\ge mL/2$, the inequalities $f(x)\le x^{-4}$ and $g(x)\le x^{-2}$ give
\[
 \frac1m\sum_{n>N}f(n/m)
 \le m^3\sum_{n>N}n^{-4}\le\frac{m^3}{3N^3}
 \le\frac8{3L^3},
\]
\[
 \frac1m\sum_{n>N}g(n/m)
 \le m\sum_{n>N}n^{-2}\le\frac mN\le\frac2L.
\]
The integral tails are at most $1/(3L^3)$ and $1/L$. Given an error tolerance, choose $L$ first to control both discrete and integral tails, then choose $m$ to control the compact-interval sums. This justifies passing from finite-interval Riemann convergence to the full half-line sums. No uncontrolled interchange of two infinite limits is involved.

\emph{Step 2: evaluate the integrals.} The substitution $x=\tan\theta$ gives $dx=\sec^2\theta\,d\theta$ and $1+x^2=\sec^2\theta$, so
\[
 \int_0^\infty f(x)\,dx=\int_0^{\pi/2}\cos^2\theta\,d\theta=\frac\pi4,
 \qquad
 \int_0^\infty g(x)\,dx=\int_0^{\pi/2}\sin^2\theta\,d\theta=\frac\pi4.
\]
Step 1 now proves the two stated asymptotics.

\emph{Step 3: move from regularization parameters to arbitrary budgets.} Set $M_m=\sqrt{A_m}$. Every positive coordinate $m^2/(m^2+n^2)$ increases strictly with $m$, so $A_m$, and hence $M_m$, increases strictly. Since $A_m/m\to c=\pi/4>0$, these budgets tend to infinity and
\[
 \left(\frac{M_{m+1}}{M_m}\right)^2
 =\frac{A_{m+1}/(m+1)}{A_m/m}\frac{m+1}{m}\longrightarrow1.
\]
WR07 identifies $\beta(M_m)=\sqrt{B_m}$. Thus
\[
 M_m\beta(M_m)=\sqrt{(A_m/m)(mB_m)}\longrightarrow c.
\]
For every sufficiently large $M$, choose $m$ with $M_m\le M\le M_{m+1}$. Monotonicity of $\beta$ gives
\[
 M_m\beta(M_{m+1})\le M\beta(M)\le M_{m+1}\beta(M_m).
\]
The lower bound is $(M_m/M_{m+1})[M_{m+1}\beta(M_{m+1})]$ and the upper is $(M_{m+1}/M_m)[M_m\beta(M_m)]$. Both tend to $c$, proving the full budget limit, not merely convergence on a selected subsequence of budgets.

\emph{Step 4: compare the hard-prefix method.} That correction has norm $\sqrt N$ and residual square $\sum_{n>N}n^{-2}$. Integral comparison yields
\[
 \frac{N}{N+1}\le N\sum_{n>N}\frac1{n^2}\le1.
\]
Taking the limit and then a square root gives its leading product one. The two constants are consequently compared at large actual correction budgets, rather than at arbitrarily equated parameter labels.''','Supply explicit uniform tail bounds and the full budget interpolation argument behind the pi/4 limit.')

proof('05i_diagonal_regularization.tex','WR12',r'''
The exact-data bias has coordinates $n/(m^2+n^2)$, so its squared norm is precisely $B_m$. By WR10,
\[
 \norm{a_{m^{-2}}(b)-a^\dagger}\le\sqrt{2/m}.
\]
WR09 at the same parameter gives
\[
 \norm{a_{m^{-2}}(\widetilde b)-a_{m^{-2}}(b)}
 \le\frac{\delta}{2\sqrt{m^{-2}}}=\frac{\delta m}{2}.
\]
The triangle inequality proves the first bound.

Because $0<\delta\le1$, the number $u=\delta^{-2/3}$ is at least one. The ceiling satisfies $u\le m<u+1\le2u$. Therefore
\[
 \sqrt{2/m}\le\sqrt2\,\delta^{1/3},
 \qquad \frac{\delta m}{2}\le\delta u=\delta^{1/3}.
\]
Adding these estimates proves the displayed rate with every ceiling factor accounted for. The positive-noise condition is needed to define this particular finite integer choice. The statement does not prescribe an infinite $m$ at $\delta=0$, nor does it use a probabilistic assumption on the perturbation.''','Retain the exact ceiling inequalities and distinguish bias from propagated data noise.')

proof('05j_inexact_certificates.tex','WR13',r'''
Let $e=a-a_\alpha$ and $B=T^*T+\alpha I$. The normal equation of the constructed optimizer gives
\[
 Be=(T^*T+\alpha I)a-T^*r=g.
\]
Pairing with $e$ yields the exact identity
\begin{equation}\label{eq:solver-energy}
 \norm{Te}^2+\alpha\norm e^2=\langle g,e\rangle
 \le\norm g\norm e.
\end{equation}
If $e=0$, all three conclusions hold with zero error. Otherwise drop the first nonnegative term and divide by $\alpha\norm e>0$ to obtain $\norm e\le\norm g/\alpha$.

To obtain the sharper fitted-data bound, retain the quadratic dependence on $\norm e$ instead of substituting the first estimate. Multiplying \eqref{eq:solver-energy} by $\alpha$ and rearranging gives
\[
\begin{aligned}
 \alpha\norm{Te}^2
 &\le\alpha\norm g\norm e-\alpha^2\norm e^2\\
 &=\frac{\norm g^2}{4}
     -\left(\alpha\norm e-\frac{\norm g}{2}\right)^2
 \le\frac{\norm g^2}{4}.
\end{aligned}
\]
Division by $\alpha$ and square roots give the factor $1/(2\sqrt\alpha)$.

By WR06 the objective gap is exactly $\norm{Te}^2+\alpha\norm e^2$, hence by \eqref{eq:solver-energy} it is also $\langle g,e\rangle$. It is nonnegative and satisfies
\[
 J_\alpha(a)-J_\alpha(a_\alpha)
 \le\norm g\norm e\le\frac{\norm g^2}{\alpha}.
\]
Every certificate quantity on the right is computed from the proposal $a$ and the declared problem. The unknown optimizer was used to prove the guarantee, but it is not required to evaluate the certificate.''','Expand the exact error equation and retain the square-completion that produces the sharp fitted-data constant.')

proof('05j_inexact_certificates.tex','WR14',r'''
For arbitrary $a,z$, expand the first square as
\[
 \norm{Ta-r+z}^2
 =\norm{Ta-r}^2+\norm z^2+2\langle Ta,z\rangle-2\langle r,z\rangle,
\]
and the scaled second square as
\[
 \frac{\norm{T^*z-\alpha a}^2}{\alpha}
 =\frac{\norm{T^*z}^2}{\alpha}+\alpha\norm a^2
       -2\langle T^*z,a\rangle.
\]
The adjoint identity cancels $2\langle Ta,z\rangle$ against the last term. The remaining expression is
\[
 \norm{Ta-r}^2+\alpha\norm a^2
 -\left(2\langle r,z\rangle-\norm z^2
                    -\alpha^{-1}\norm{T^*z}^2\right),
\]
which is the asserted gap. Its nonnegativity gives weak duality for every pair, without any constraint on the witness norm.

Set $a=a_\alpha$ and $z_\alpha=r-Ta_\alpha$. The first square is zero by this definition. The normal equation gives $T^*z_\alpha=\alpha a_\alpha$, so the second is zero as well. Therefore
\[
 \mathcal D_\alpha(z_\alpha)=J_\alpha(a_\alpha).
\]
For every other $z$, weak duality with $a_\alpha$ gives $\mathcal D_\alpha(z)\le J_\alpha(a_\alpha)$. This proves attainment of the dual maximum and equality with the primal minimum directly.

For a general proposed pair $(a,z)$, decompose its gap as
\[
 J_\alpha(a)-\mathcal D_\alpha(z)
 =[J_\alpha(a)-J_\alpha(a_\alpha)]
  +[J_\alpha(a_\alpha)-\mathcal D_\alpha(z)].
\]
The second bracket is nonnegative by weak duality, while WR06 bounds the first below by $\alpha\norm{a-a_\alpha}^2$. This proves the correction-error certificate.

Finally take $z=r-Ta$. The first square in the gap is zero, while $T^*z-\alpha a=-g$. The second becomes $\norm g^2/\alpha$, proving the residual-witness formula. A small duality gap controls optimizer error only after division by the specified positive parameter.''','Show the cancellation of every dual mixed term, construct the maximizing witness and derive the correction guarantee.')

proof('05k_stopping_rules.tex','WR15',r'''
Because $B$ has independent columns, for every nonzero coefficient vector $c$,
\[
 c^{\mathsf T}Gc=c^{\mathsf T}B^{\mathsf T}Bc=\norm{Bc}^2>0.
\]
Thus $G$ is positive definite and invertible. The matrix $P=BG^{-1}B^{\mathsf T}$ is symmetric and obeys
\[
 P^2=BG^{-1}(B^{\mathsf T}B)G^{-1}B^{\mathsf T}=P,
 \qquad PB=B.
\]
Its range is precisely the column space $H$, so it is the orthogonal projection onto the entire permitted correction space.

The restricted Hilbert normal residual is
\[
 g=P d^{\mathsf T}(dBc-r)+\alpha Bc.
\]
Substitute $S=dB$, $G=B^{\mathsf T}B$ and the expression for $P$:
\[
 g=BG^{-1}\bigl(S^{\mathsf T}(Sc-r)+\alpha Gc\bigr)=BG^{-1}q.
\]
Equivalently $q=B^{\mathsf T}g$ records the pairings of $g$ with the basis columns. Its squared Hilbert norm is
\[
 g^{\mathsf T}g
 =q^{\mathsf T}G^{-1}B^{\mathsf T}BG^{-1}q
 =q^{\mathsf T}G^{-1}q,
\]
using symmetry of $G^{-1}$. This proves both coordinate formulas.

For the basis change $B'=BC$, the same ambient vector is represented by $c'=C^{-1}c$. Also $S'=SC$ and $G'=C^{\mathsf T}GC$. Substitute these formulas into the new coordinate normal equation:
\[
\begin{aligned}
 q'&=((S')^{\mathsf T}S'+\alpha G')c'-(S')^{\mathsf T}r\\
 &=C^{\mathsf T}(S^{\mathsf T}S+\alpha G)CC^{-1}c
      -C^{\mathsf T}S^{\mathsf T}r=C^{\mathsf T}q.
\end{aligned}
\]
The inverse metric is $(G')^{-1}=C^{-1}G^{-1}(C^{\mathsf T})^{-1}$. Hence
\[
 (q')^{\mathsf T}(G')^{-1}q'
 =q^{\mathsf T}C C^{-1}G^{-1}(C^{\mathsf T})^{-1}C^{\mathsf T}q
 =q^{\mathsf T}G^{-1}q.
\]
For a zero-dimensional kernel these are empty matrices and zero vectors, and the resulting scalar norm is zero. The spanning assumption is indispensable: a basis of a proper subspace would compute a projection to a different correction problem.''','Prove the Gram projection formula, treat the residual as a covector and cancel every basis-change factor.')

proof('05k_stopping_rules.tex','WR16',r'''
At index $n$, distinguish two exact minimizers: let $\widetilde a_n=a_{\alpha_n}(\widetilde r_n)$ solve the measured problem and let $a_n^0=a_{\alpha_n}(r)$ solve the intended-data problem. All three corrections, including the proposal $a_n$, belong to the same space $H$.

The supplied normal-residual bound is for the measured datum. Therefore WR13 applies first to that problem and gives
\[
 \norm{a_n-\widetilde a_n}\le\frac{\varepsilon_n}{\alpha_n}.
\]
The pointwise data estimate WR09, at the same parameter, then gives
\[
 \norm{\widetilde a_n-a_n^0}\le\frac{\delta_n}{2\sqrt{\alpha_n}}.
\]
Insert these two intermediate vectors between $a_n$ and $a^\dagger$ in the triangle inequality to obtain the displayed three-term estimate.

The first term tends to zero by the solver-tolerance hypothesis and the second by the data/parameter hypothesis. Since the projected intended datum is attained and $\alpha_n\to0$, the last term tends to zero by WR08. For a direct epsilon argument, make each term smaller than one third of a prescribed tolerance beyond its own threshold and take the maximum of the three thresholds. This gives norm convergence of the proposals.

Protection is not merely asymptotic: $a_n\in\ker p$ implies $p(f-a_n)=pf$ at every index. The proof compares no changing operators or changing kernels. Its pointwise certificate is formally verified, while the appeal to WR08 is the separately identified written convergence step.''','Insert the measured and intended exact optimizers separately and track which theorem controls each error term.')

(ROOT/'audit/proof_detail/changes_regularization.json').write_text(json.dumps(changes,indent=2)+'\n')
print('expanded',len(changes),'proofs; added words',sum(c['new_words']-c['old_words'] for c in changes))
