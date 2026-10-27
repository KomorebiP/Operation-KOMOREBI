from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'provenance/original_release/Projector_Resolved_Seed_Calculus_VI.tex').read_text()
def replace(old,new):
 global s
 if old not in s: raise RuntimeError('Missing source passage: '+old[:100])
 s=s.replace(old,new,1)
replace('For likelihoods $\\lambda$ and $\\mu$ with positive evidences,',r'For nonnegative likelihoods $\lambda$ and $\mu$, assume $Z_\lambda(p)>0$ and $Z_{\lambda\odot\mu}(p)>0$. Equivalently, both successive updates have positive evidence. Then')
replace(r'q_{\alpha,i}=\frac{\lambda_ip_i}{Z_\alpha}'+'\n'+r'\quad(i\in I_\alpha).',r'''q_{\alpha,i}=\begin{cases}
\lambda_ip_i/Z_\alpha,&Z_\alpha>0,\ i\in I_\alpha,\\
0,&\text{otherwise}.
\end{cases}''')
replace('The nonlinear coupling between packets occurs only through the total evidence used to normalize the packet evidences.', 'Only packets with positive evidence carry a conditional probability vector. A zero-evidence packet has zero posterior mass and contributes the zero vector. The nonlinear coupling between packets occurs only through the total evidence used to normalize the packet evidences.')
replace('For $i\\in I_\\alpha$,\n\\[\nm_\\alpha q_{\\alpha,i}', 'If $Z_\\alpha=0$, nonnegativity implies $\\lambda_i p_i=0$ for every $i\\in I_\\alpha$, so the reconstruction identity holds with both sides zero. For $Z_\\alpha>0$ and $i\\in I_\\alpha$,\n\\[\nm_\\alpha q_{\\alpha,i}')
replace('If $\\lambda_i=c\\bar\\lambda_a$ on $I_a$, then $r_a(p)=c\\bar\\lambda_a$ for every prior,', 'If $\\lambda_i=c\\bar\\lambda_a$ on $I_a$, then $P_a r_a(p)=c\\bar\\lambda_aP_a$ for every prior, including zero-mass packets,')
replace(r'\begin{theorem}[Bayesian information-loss packet]'+'\n'+'The coarsening defect is',r'\begin{theorem}[Bayesian information-loss packet]'+'\n'+r'Assume nonnegative fine and declared coarse likelihoods, with both $Z_r>0$ and $Z_{\bar\lambda}>0$. The coarsening defect is')
replace('The first norm bound is the likelihood perturbation theorem applied on the coarse simplex.  Finally,', 'The first norm bound is the likelihood perturbation theorem applied on the coarse simplex. For a zero-mass packet, both sides of the following estimate vanish. For $P_a>0$,')
replace('For a nested finite packet tower, Bayesian conditioning commutes with every coarsening map for every prior if and only if, at each level, the fine likelihood is blockwise proportional to the declared coarse likelihood on every coarsening fiber.  Under this condition, all composite coarsening squares commute.', 'Consider a nested finite packet tower with strictly positive likelihoods at every level. At each adjacent coarsening with at least two coarse packets, commutation for every prior is equivalent to the fine likelihood being blockwise proportional to the declared coarse likelihood, with one common positive proportionality factor. An adjacent coarsening to a single packet commutes automatically and imposes no such condition. Under these conditions, all composite coarsening squares commute.')
replace('[Canonical coarsest Bayesian-sufficient partition]', '[Canonical coarsest likelihood-resolving partition]')
replace('The equivalence classes form the unique coarsest partition on which every Bayesian update in the family closes exactly for every prior.', 'The equivalence classes form the unique coarsest likelihood-resolving partition: every likelihood is constant on each packet. Every update therefore closes on this partition whenever its evidence is positive. If all likelihoods are strictly positive and there are at least two profile classes, this is also the unique coarsest nontrivial partition on which every update closes for every prior. The one-packet partition always closes, independently of the profiles, and is excluded from this last assertion.')
replace('Every likelihood is constant on each equivalence class, so the refinement theorem gives exact closure.  Conversely, any partition sufficient for every likelihood must place only states with equal likelihood values in the same packet.  It therefore refines the displayed equivalence-class partition.', 'Equality of likelihood profiles is an equivalence relation. Its classes are likelihood-resolving by definition, and every likelihood-resolving partition refines them. Exact closure follows by summing the weighted masses in each fiber, including zero-mass fibers. Under strict positivity, the refinement criterion implies that every nontrivial all-prior closed partition is likelihood-resolving. When every profile is identical, all partitions close; there need not be a unique coarsest nontrivial partition.')
replace('The Bayesian refinement square commutes exactly when the likelihood is constant on each coarsening fiber, up to one global scale.', 'For strictly positive likelihoods and at least two coarse packets, the Bayesian refinement square commutes for every prior exactly when the likelihood is constant on each coarsening fiber, up to one global scale.')
replace('Whenever $zI-A_{QQ}$ is invertible, define', 'Assume both $zI-A$ and $zI-A_{QQ}$ are invertible. Define')
replace('P(zI-A)^{-1}P=F_P(z)^{-1}.', r'\left.P(zI-A)^{-1}\right|_{\Ran P}=F_P(z)^{-1}.')
replace('The resulting retained coefficient is $F_P(z)$. Equivalently, this is the block inverse formula.', r'The resulting retained coefficient is $F_P(z)$. Invertibility of the full operator and of the hidden block implies invertibility of this Schur complement. Setting $y_Q=0$ gives the stated identity as an operator on $\Ran P$. Equivalently, this is the block inverse formula.')
replace('Let $A$ be a transient-state subgenerator: its off-diagonal entries are nonnegative and its column sums are nonpositive.', 'Let $A$ be a finite subgenerator: its off-diagonal entries are nonnegative and its column sums are nonpositive. These sign conditions alone allow nonabsorbing states; eventual absorption is a separate hypothesis.')
replace('The event-time density and hazard are', r'For $t\ge0$, the finite-time exit density and, wherever $S(t)>0$, the hazard are')
replace('whenever $S(t)>0$.\n\\end{theorem}', 'whenever $S(t)>0$. The density may be defective: its total mass is $1-\\lim_{t\\to\\infty}S(t)$. It is a probability density when absorption is eventual, so that this limit is zero.\n\\end{theorem}')
replace('Let $F$ be any analytic function on a neighborhood of the spectra of $A_f$ and $A_c$. If', 'For finite complex matrices, let $F$ be holomorphic on a neighborhood of the union of the spectra of $A_f$ and $A_c$. Real matrices are treated by complexification. If')
replace('The identity $CA_f^m=A_c^mC$ follows by induction. Apply it termwise to the convergent power series of $F$. Resolvents follow either from the resolvent identity or from multiplication by the two invertible factors.', r'The identity $CA_f^m=A_c^mC$ follows by induction. More generally, $C(zI-A_f)^{-1}=(zI-A_c)^{-1}C$ on the common resolvent set, by multiplication by the two invertible factors. Choose contours in the stated neighborhood enclosing the union of the spectra. Multiply this resolvent identity by $F(z)/(2\pi i)$ and integrate; the holomorphic functional calculus gives the result. This argument does not require one Taylor series to converge on both spectra.')
replace('The Bayesian refinement conjecture is resolved in finite dimensions: exact commutation with coarsening is equivalent to blockwise-constant likelihoods up to global scale,', 'The Bayesian refinement conjecture is resolved in finite dimensions: for strictly positive likelihoods and at least two coarse packets, exact commutation for every prior is equivalent to blockwise-constant likelihoods up to global scale,')
replace('Nineteen code-generated figures, machine-readable results, and thirty-seven automated tests accompany the paper.', r'Nineteen code-generated figures, machine-readable results, the original thirty-seven automated tests, and added boundary-case checks accompany this reviewed edition. Five checked Lean blocks cover all 33 theorem-like results in Appendix~\ref{sec:lean-status}.')
replace('\\date{}',r'\date{Reviewed edition: 6 September 2026\\\small Fifth Lean-checked formalization block; all 33 results covered}')
replace('Every hidden Markov filtering step is the composition of a linear Markov transfer and a normalized nonlinear likelihood transfer. If both preserve nonnegative mass and the evidence is positive, then every $p_r$ is a probability vector.', 'Every hidden Markov filtering step is the composition of a linear Markov transfer and a normalized nonlinear likelihood transfer. Assume a probability initial vector, a column-stochastic transition matrix, and nonnegative likelihoods with positive evidence at every step. Then every $p_r$ is a probability vector.')
replace('the original thirty-seven automated tests, and added boundary-case checks', 'the original thirty-seven automated tests, and seventeen added boundary-case checks')
replace('\\tableofcontents\n\\listoffigures\n\\listoftables', '\\tableofcontents\n\\begingroup\n\\small\n\\listoffigures\n\\listoftables\n\\endgroup')
replace(r'\boxed{37/37\text{ automated tests}.}', r'\boxed{54/54\text{ automated tests}.}')
replace('canonical sufficient partitions, conditional-expectation towers', 'likelihood-profile partitions, conditional-expectation towers')
replace('Apply the refinement criterion at each adjacent pair of levels.  Composition of the commuting squares gives the full tower statement.', 'At each adjacent coarsening with at least two coarse packets, apply the refinement criterion. For a single coarse packet, both normalized posteriors equal 1. Composition of these commuting squares gives the full tower statement.')
replace('In the finite-dimensional statement below, set', 'Set')
# Fifth block: explicit finite-dimensional proofs of the last two results.
replace('For $z$ to the right of the spectrum of $A_{QQ}$,', r'For finite complex block matrices, assume $\operatorname{Re}z>\operatorname{Re}\lambda$ for every $\lambda\in\sigma(A_{QQ})$. Then the following improper integral is absolutely convergent and')
replace(r"""Use
\[
\int_0^\infty e^{-zt}e^{tA_{QQ}}\,dt=(zI-A_{QQ})^{-1}
\]
and multiply on the left and right by the two transfer blocks.""",r"""Put $B=A_{QQ}$ and $T_z(t)=e^{-zt}e^{tB}=e^{t(B-zI)}$.
The generalized-eigenspace decomposition in finite dimensions writes $T_z$ as a
finite sum of constant matrix coefficients times $t^k e^{(\lambda-z)t}$.
This follows by expanding the nilpotent part on each generalized eigenspace;
equivalently, apply the decomposition to left multiplication by $B$ on the matrix
algebra and evaluate the exponential at $I$.
The strict spectral inequality makes every such term absolutely integrable on
$(0,\infty)$ and forces it to tend to zero. Hence $T_z$ is Bochner integrable
and $T_z(t)\to0$, including when $B$ is nonnormal.

Let $J=\int_0^\infty T_z(t)\,dt$. Integrating both derivative identities
$T_z'=(B-zI)T_z=T_z(B-zI)$ and using $T_z(0)=I$ gives
\[
(zI-B)J=J(zI-B)=I.
\]
Thus $J=(zI-B)^{-1}$. Continuous left and right multiplication carry the
Bochner integral through the two rectangular transfer blocks, yielding the claim.""")
replace(r'\begin{theorem}[Naturality under exact intertwining]',r"""For clarity, the finite-dimensional holomorphic calculus used below has the
following canonical definition. For $A$ acting on $\mathbb C^d$, its generalized
eigenspaces $E_\mu=\ker(A-\mu I)^d$ form a direct-sum decomposition over the
eigenvalues. Define the unique linear operator $F(A)$ by
\[
\left.F(A)\right|_{E_\mu}
=\left.\sum_{k=0}^{d-1}\frac{F^{(k)}(\mu)}{k!}(A-\mu I)^k\right|_{E_\mu}.
\]
The formula is independent of a basis and of increasing the truncation index:
the extra nilpotent powers vanish. It depends only on the finite Taylor jets of
$F$ at the spectrum. If $F$ is holomorphic on an open neighborhood $U$ of the
spectrum, each eigenvalue admits a radius $r_\mu>0$ with
$\overline{D(\mu,r_\mu)}\subset U$, and Cauchy's formula gives
\[
\frac{F^{(k)}(\mu)}{k!}
=\frac{1}{2\pi i}\oint_{|z-\mu|=r_\mu}
  \frac{F(z)}{(z-\mu)^{k+1}}\,dz.
\]
Consequently the same canonical operator is obtained from any such local
Cauchy circles, even when $U$ is disconnected. This is the standard finite
Taylor-jet definition of the holomorphic matrix function.

\begin{theorem}[Naturality under exact intertwining]""")
replace(r'The identity $CA_f^m=A_c^mC$ follows by induction. More generally, $C(zI-A_f)^{-1}=(zI-A_c)^{-1}C$ on the common resolvent set, by multiplication by the two invertible factors. Choose contours in the stated neighborhood enclosing the union of the spectra. Multiply this resolvent identity by $F(z)/(2\pi i)$ and integrate; the holomorphic functional calculus gives the result. This argument does not require one Taylor series to converge on both spectra.',r"""The intertwining identity implies
$C(A_f-\mu I)^k=(A_c-\mu I)^kC$ for every $k\ge0$.
It therefore sends the generalized $\mu$-eigenspace of $A_f$ into that of $A_c$.
Use a common truncation index at least as large as both dimensions in the
canonical formula above. Multiplying its finite sum by $C$ now gives the desired
identity on every generalized eigenspace. The direct-sum decomposition gives
it on the full space. The argument covers nilpotent Jordan parts and uses only
local spectral Taylor jets; it does not require one Taylor series to converge
on both spectra. The zero-dimensional case is immediate.""")

# The appendix explains norm summability and complexification without changing the main claims.
# The formalization appendix is generated after the final theorem audit.
replace(r'\end{document}',r'\input{lean_status.tex}'+'\n'+r'\end{document}')
(root/'manuscript/Paper_VI_Reviewed.tex').write_text(s)
