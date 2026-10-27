# Part V. Curved domains and continuous observations

Part IV separated a valid predictive model from a successful fit. Its finite positive lift gives a useful certificate, but its rank-three rotation example has no finite polyhedral probability domain. The same block left continuous observations outside the finite-alphabet construction. This part addresses both boundaries in a declared finite sector.

A curved domain can have a short matrix certificate even when it has infinitely many extreme states. A continuous observation can have a finite operator description even when its possible values are uncountable. Neither statement follows from finite predictive dimension alone. The constructions below require an explicit domain, a reference measure and a restricted observation-kernel family.

The block connects matrix positivity, integral observation semantics, population-moment identification, exact coarsening and approximation. It also identifies a defect that is easy to overlook: averaging a matrix transformation before applying its quadratic action does not equal averaging that action. The difference is a positive covariance contribution. Omitting it can destroy normalization even in a very small example.

There are established antecedents. Congruence representations and their positive semidefinite Gram matrices belong to the theory of completely positive maps [R16]. Polynomial Gram certificates are standard sum-of-squares machinery [R17]. Continuous-valued observable operator models already occur in Jaeger's work [R18]. The proofs here develop their specific connection to the realization and defect contracts of the large signal model. They do not claim to originate those ingredients.

This is a discrete-time theory with continuous-valued observations. It is not a continuous-time stochastic dynamics theorem. Production PR-LASM 2.3.0 is unchanged.

\newpage

# 56. A matrix certificate for a curved domain

Let $E=\mathbb R^r$ and let $\mathbb S^d$ be the real symmetric $d\times d$ matrices. Fix an injective linear map

$$
\mathcal J:E\longrightarrow\mathbb S^d,
\qquad \lambda z=\operatorname{tr}\mathcal J(z).
$$

Suppose some $e\in E$ satisfies $\mathcal J(e)\succ0$. Define

$$
C_{\mathcal J}=\{z:\mathcal J(z)\succeq0\},
\qquad K_{\mathcal J}=\{z\in C_{\mathcal J}:\lambda z=1\}.
$$

The map $\mathcal J$ is an embedding, not a many-to-one decoder of a larger positive coordinate space. The cone is an inverse image of the positive semidefinite cone. This is different from the image cone $V\mathbb R_+^m$ used in Proposition 39.

**Proposition 50. Matrix-embedding probability certificate.** The cone $C_{\mathcal J}$ is closed, pointed and generating, and $\lambda$ is strictly positive on its nonzero elements. Its normalized base is compact. Suppose a finite-alphabet predictive model has $z_0\in K_{\mathcal J}$, exact mass conservation and identities

$$
\boxed{\mathcal J B_s=\Phi_s\mathcal J,}
\qquad
\Phi_s(X)=\sum_{j=1}^{m_s} w_{sj}K_{sj}XK_{sj}^{\mathsf T},
\quad w_{sj}\geq0.
$$

Then every $B_s$ preserves $C_{\mathcal J}$, and every finite observation word has a nonnegative, normalized probability. Zero maps may use an empty sum. An invertible change of predictive coordinates transports the certificate by

$$
B'_s=TB_sT^{-1},\qquad
\mathcal J'=\mathcal JT^{-1},\qquad
\lambda'=\lambda T^{-1}.
$$

**Proof.** Closedness follows from continuity. If both $z$ and $-z$ are in the cone, $\mathcal J(z)$ is both positive and negative semidefinite, hence zero. Injectivity gives $z=0$. A sufficiently small neighborhood of $e$ maps into positive definite matrices, so the cone has an interior point and is generating. A nonzero positive semidefinite matrix has positive trace. The trace-one positive semidefinite matrices form a compact set. The image of $\mathcal J$ is a closed finite-dimensional subspace and its inverse on that image is continuous, so $K_{\mathcal J}$ is compact.

Every term $wKXK^{\mathsf T}$ is positive semidefinite when $X$ is. The intertwining identity therefore proves invariance. Iteration gives invariance of every branch state, and the mass identity normalizes every finite observation tree. Substituting the transported quantities proves the final statement. $\square$

This is a sufficient certificate language. It is not asserted that every invariant cone has this form, or that every positive map on a matrix subspace extends through the displayed congruence representation. The extension requirement is stronger than positivity on the represented states alone.

The base norm of Section 46 is also not automatically the ambient trace norm. One always has

$$
\|\mathcal J(z)\|_1\leq\|z\|_{C_{\mathcal J}},
$$

because every positive decomposition in $E$ gives one in the matrix space. Equality holds when $\mathcal J$ maps onto all of $\mathbb S^d$, by the positive and negative spectral parts. For a proper matrix subspace, those spectral parts may leave the subspace. Norm transport therefore needs its own stated hypothesis.

# 57. The earlier disk obstruction has an exact finite matrix witness

For the rank-three model of Section 51, put

$$
\mathcal J(m,x,y)=\frac12
\begin{pmatrix}m+x&y\\y&m-x\end{pmatrix}.
$$

Then $\operatorname{tr}\mathcal J=m$ and

$$
\det\mathcal J=\frac{m^2-x^2-y^2}{4}.
$$

Its eigenvalues are $(m\pm\sqrt{x^2+y^2})/2$, so positivity is exactly the Lorentz-cone condition. The normalized base is the unit disk.

**Proposition 51. Exact rational matrix witness for the rotation model.** Let $T=\operatorname{diag}(1,R)$ with the unchanged rotation

$$
R=\begin{pmatrix}3/5&-4/5\\4/5&3/5\end{pmatrix},
\qquad W=\begin{pmatrix}2&-1\\1&2\end{pmatrix}.
$$

The rotate branch and the two probe branches from Proposition 46 have the identities

$$
\begin{aligned}
\mathcal J(Tz)&=\frac15W\mathcal J(z)W^{\mathsf T},\\
\mathcal J(B_{\mathrm p,0}z)&=E_{00}\mathcal J(z)E_{00}^{\mathsf T},\\
\mathcal J(B_{\mathrm p,1}z)&=E_{01}\mathcal J(z)E_{01}^{\mathsf T},
\end{aligned}
$$

where $E_{ij}$ is the corresponding $2\times2$ matrix unit. The other rotate branch is zero. Thus this exact model has a finite rational matrix certificate without attenuation or a polygonal replacement.

**Proof.** Direct multiplication gives the rotate identity. The two matrix-unit congruences retain, respectively, the upper and lower diagonal entries of $\mathcal J(z)$ and place them in its upper diagonal entry. These are $(m+x)/2$ and $(m-x)/2$, exactly the two probe masses resetting to $(1,1,0)$. Also $W^{\mathsf T}W=5I$ and

$$
E_{00}^{\mathsf T}E_{00}+E_{01}^{\mathsf T}E_{01}=I.
$$

The actions conserve trace. The initial state embeds as $\operatorname{diag}(1,0)$, and $(1,0,0)$ is a strictly positive interior witness. Proposition 50 applies. $\square$

Nothing has been changed in the observation law. Proposition 46 still rules out a finite positive-generator certificate for this model. What changes is the certificate language. A curved matrix domain and a finite set of positive coordinate states are not the same representation class.

This use of symmetric positive semidefinite matrices is mathematical. It neither requires quantum hardware nor claims a quantum description of the measured system. It borrows a well-defined operator representation rather than a physical interpretation.

\newpage

# 58. An observation density is not a branch probability

Let $(Y,\mathcal Y)$ be a standard Borel observation space and let $\mu$ be a fixed probability reference measure. Keep a finite action set. For each action $a$, let $B_a(y):E\to E$ be measurable and integrable in operator norm. Let $(C,\lambda)$ be a proper probability cone and mass functional as in Section 46. Assume that, outside one $\mu$-null set for each action,

$$
B_a(y)C\subseteq C,
\qquad
\lambda\int_Y B_a(y)\,\mu(dy)=\lambda.
$$

The second identity is an equality of linear functionals. The first is a statement on the whole cone, not only on a finite selection of states.

**Proposition 52. Continuous-observation instrument semantics.** For $z\in K=\{z\in C:\lambda z=1\}$,

$$
\boxed{
P_a(A\mid z)=\int_A\lambda B_a(y)z\,\mu(dy),
\qquad
z^+(y)=\frac{B_a(y)z}{\lambda B_a(y)z}
}
$$

define a probability kernel and, for $\mu$-almost every observation with positive denominator, a conditional state. They generate consistent finite record laws under any common measurable history-dependent policy. For prescribed actions, the joint observation density is

$$
\lambda B_{a_T}(y_T)\cdots B_{a_1}(y_1)z_0
$$

with respect to $\mu^{\otimes T}$. Replacing the reference measure by $\mu'=r\mu$, with $r>0$ almost everywhere and $\int r\,d\mu=1$, requires $B'_a(y)=B_a(y)/r(y)$. Event probabilities and normalized states then remain unchanged.

**Proof.** Cone positivity makes the density nonnegative and the integrated mass identity makes its integral one. A positive-density update lies in $K$. Assign any fixed state of $K$ on the common exceptional null set and at zero-density points to obtain a measurable version of the update. This arbitrary choice has no effect on the probability kernel. Repeated integration, or conditioning one step at a time, proves normalization and consistency of the finite laws. Measurable policy factors are nonnegative and sum to one at each history. The reference-measure transformation cancels $r$ in each integral and cancels $1/r$ in the normalized update. $\square$

When $\mu$ has no atoms, an individual point has probability zero even when its density is positive. A density may exceed one. Neither fact is a numerical pathology. Flooring a vanishing denominator changes the model and is not part of this theorem.

A continuous density at an exact point is a version-dependent object on null sets. The update formula specifies a convenient version wherever its denominator is positive. Event probabilities are the invariant statistical objects. Comparing model densities requires a common measure or a declared change-of-measure calculation.

A representation that lacks an operator-norm integrable density needs a more general operator-valued measure. Such representations are not silently covered by the density hypothesis above.

# 59. A finite certificate over an entire observation interval

Specialize to $Y=[-1,1]$ and $\mu(du)=du/2$. Suppose $B_a(u)$ is a matrix polynomial. A finite congruence certificate can prove positivity for every $u$, not merely for values on a grid.

For a real $d^2\times d^2$ symmetric matrix $F$, define

$$
[\Phi_F(X)]_{ij}=\sum_{p,q=1}^d F_{(i,p),(j,q)}X_{pq}.
$$

Vectorization orders the pairs with output index first inside each input column. If

$$
F=\sum_\nu w_\nu\operatorname{vec}(K_\nu)
\operatorname{vec}(K_\nu)^{\mathsf T},\qquad w_\nu\geq0,
$$

then $\Phi_F(X)=\sum_\nu w_\nu K_\nu X K_\nu^{\mathsf T}$. Every positive semidefinite $F$ has a real factorization of this kind. The matrix is the usual Choi/Gram representation, with an explicit index convention [R16].

**Proposition 53. Polynomial Gram certificate for interval observations.** Fix the injective embedding $\mathcal J$ and its strict interior witness from Proposition 50. Set

$$
Z_q(u)=\begin{pmatrix}I_{d^2}\\uI_{d^2}\\\vdots\\u^qI_{d^2}\end{pmatrix}.
$$

Suppose each action has constant positive semidefinite matrices $G_{a,0},G_{a,1}$, with the second term omitted when $q=0$, such that

$$
\begin{aligned}
F_a(u)&=Z_q(u)^{\mathsf T}G_{a,0}Z_q(u)\\
&\quad +(1-u^2)Z_{q-1}(u)^{\mathsf T}G_{a,1}Z_{q-1}(u),\\
\mathcal J B_a(u)&=\Phi_{F_a(u)}\mathcal J.
\end{aligned}
$$

Assume also $z_0\in K_{\mathcal J}$ and the exact integrated mass identity. Then the model is internally probability-valid for every observation value in $[-1,1]$ and every finite horizon. The intertwining condition is finitely many coefficient equalities. The normalization condition uses only

$$
\int_{-1}^1u^k\,\frac{du}{2}
=\begin{cases}0&k\text{ odd},\\1/(k+1)&k\text{ even}.\end{cases}
$$

**Proof.** Both Gram expressions are positive semidefinite on the interval because $1-u^2\geq0$ there. Factoring $F_a(u)$ at a fixed $u$ gives a positive congruence map, whether or not its individual factors depend polynomially on $u$. The intertwining identity therefore proves $B_a(u)C_{\mathcal J}\subseteq C_{\mathcal J}$. Polynomials on a compact interval are integrable. The mass identity and Proposition 52 prove the assertion. Equality of two finite matrix polynomials is equivalent to equality of every coefficient. The moment values follow by elementary integration. $\square$

For fixed $\mathcal J$ and fixed degree bounds, unknown entries of $B_a$ and the Gram matrices obey linear equalities and positive semidefinite constraints. A convex data-fit objective therefore gives a semidefinite feasibility or optimization problem in this fixed representation. Jointly choosing $\mathcal J$ changes the problem: the intertwining equation then contains products of unknown coefficients.

This is a sufficient certificate, not a completeness theorem for all positive kernels or all curved domains. A negative answer at one degree is not a proof of model invalidity. Approximate Gram feasibility is also not an exact witness. Rational factorizations with nonnegative rational weights, or rigorous matrix-positivity bounds, must survive a separate replay.

The reference checker accepts a factored version:

$$
\Phi_u(X)=\sum_\nu w_\nu g_\nu(u)K_\nu(u)XK_\nu(u)^{\mathsf T},
\qquad g_\nu(u)\in\{1,1-u^2\}.
$$

It checks the polynomial identities, weights, support, embedding, initial state and normalization exactly. It does not run a general semidefinite optimizer. The operator identity holds on the image of $\mathcal J$; trace preservation of an arbitrary extension outside that image is not required.

# 60. Learning from integral observations rather than point probabilities

A finite polynomial family can be identified through moment operators. This gives a continuous-observation analogue of the core-table construction without pretending that a point has positive probability.

Assume the true operator density belongs to the declared class

$$
B_a(u)=\sum_{k=0}^D u^k C_{a,k},
\qquad
M_{a,j}=\int_{-1}^1 u^j B_a(u)\,\frac{du}{2}.
$$

Define the moment Gram matrix $W_D$ by

$$
(W_D)_{jk}=\int_{-1}^1u^{j+k}\,\frac{du}{2},
\qquad 0\leq j,k\leq D.
$$

A history is now a prescribed action sequence with observations constrained to measurable events of positive or zero probability. It produces an unnormalized predictive vector $h_j$. A future event experiment produces a row functional $t_i$. Choose $r$ of each and form

$$
H_{ij}=t_i h_j,\qquad
(G_{a,j})_{i\ell}=t_i M_{a,j}h_\ell.
$$

The index $j$ in $G_{a,j}$ is a moment order. Odd-order entries can be signed expectations. They are not branch probabilities and are never normalized as if they were.

**Proposition 54. Conditional finite-moment identification.** Suppose the true predictive dimension is $r$, the degree bound $D$ is correct, and the selected $r\times r$ core $H$ is invertible. Exact population values of $H$, every $G_{a,j}$ and the initial test vector determine the complete polynomial operator family in test coordinates:

$$
\boxed{
\widehat M_{a,j}=G_{a,j}H^{-1},
\qquad
\widehat C_{a,k}=\sum_{j=0}^D(W_D^{-1})_{kj}\widehat M_{a,j}.
}
$$

If every moment-operator error is at most $\eta$ in one fixed induced norm, then coefficient reconstruction alone obeys

$$
\|\widetilde C_{a,k}-\widehat C_{a,k}\|
\leq\eta\sum_j|(W_D^{-1})_{kj}|.
$$

**Proof.** A nonzero polynomial has strictly positive squared integral, so its coefficient vector $c$ satisfies $c^{\mathsf T}W_Dc>0$. Thus $W_D$ is invertible. Let $T$ have rows $t_i$ and $S$ have columns $h_j$. Since $H=TS$ is an invertible square core in an $r$-dimensional space, both $T$ and $S$ are invertible. Therefore $G_{a,j}H^{-1}=TM_{a,j}T^{-1}$. The relation $M_{a,j}=\sum_k(W_D)_{jk}C_{a,k}$ is exact integration of the polynomial expansion. Invert it and conjugate by $T$ to obtain the displayed reconstruction. The error bound is the triangle inequality for that same fixed linear inversion. $\square$

The rank and degree assumptions are not learned from the determinant of $H$. The determinant establishes coverage only after the ambient predictive dimension has been justified. The moment Gram can become poorly conditioned at higher degree. An orthogonal polynomial basis can improve this representation without removing an incorrect degree assumption.

The entries have an operational population meaning. A reset experiment for an event word, with one observation weighted by $u^j$, returns a bounded random variable in $[-1,1]$. Its expectation is the corresponding entry of $G_{a,j}$. With $N$ independent trials for each of $M$ predeclared entries, the same exponential-moment argument as Proposition 35 gives the simultaneous bound

$$
\epsilon_N=\sqrt{\frac{2\log(2M/\delta)}{N}}
$$

with failure probability at most $\delta$. The factor differs from the Bernoulli bound because the value range is two. Dependent trajectories, unknown resets and post-selection are not covered by that observation protocol. This edition uses exact constructed population tables, not a new sampling experiment.

# 61. Finite moments cannot validate an unrestricted density class

A finite observation basis is a modeling assumption. Positivity certification does not turn that assumption into a consequence of data.

**Proposition 55. A valid continuous counterexample to finite-moment identification.** Let

$$
L_3(u)=\frac{5u^3-3u}{2},\qquad
p_\pm(u)=1\pm\epsilon L_3(u),\qquad 0<\epsilon<1.
$$

Relative to $du/2$, these are distinct strictly positive normalized densities with the same moments of orders zero, one and two. Their total-variation distance is

$$
\boxed{\|p_+\mu-p_-\mu\|_{\mathrm{TV}}=\frac{13\epsilon}{40}.}
$$

Taking independent observations gives two rank-one processes whose products of these low-order moments agree at every sequence length.

**Proof.** The endpoints and stationary points of $L_3$ show $|L_3(u)|\leq1$ on the interval. Direct integration gives $\int u^jL_3(u)\,du/2=0$ for $j=0,1,2$. This proves normalization and moment agreement, while strict positivity follows from $\epsilon<1$. Its nonnegative root other than zero is $\sqrt{3/5}$. Integrating $|L_3|$ on the two subintervals of $[0,1]$ and using symmetry gives $\int|L_3|\,du/2=13/40$. The density difference is $2\epsilon L_3$, so its half-integral is the stated distance. Independence makes every product moment factor into the identical one-step moments. $\square$

This is not a defect in Proposition 54. These densities lie outside its quadratic class. It is a concrete reason to retain an explicit approximation or misspecification term when increasing the observation basis. Internal probability validity and correct density identification remain different claims even in one predictive dimension.

# 62. Exact observation bins preserve their own event law

Let $A_1,\ldots,A_n$ be a measurable partition of $Y$. Define the cell operators

$$
B_{a,j}=\int_{A_j}B_a(y)\,\mu(dy).
$$

Their role is to represent observed events. They are not point samples of the original density.

**Proposition 56. Exact bin coarsening and its posterior.** Every $B_{a,j}$ preserves the probability cone, and $\lambda\sum_jB_{a,j}=\lambda$. For a policy measurable with respect to bin histories, the finite model $\{B_{a,j}\}$ reproduces exactly the binned observation law of the continuous model at every finite horizon. On an observed cell with $p_j=\lambda B_{a,j}z>0$,

$$
\frac{B_{a,j}z}{p_j}
=\frac1{p_j}\int_{A_j}z^+(y)\lambda B_a(y)z\,\mu(dy).
$$

**Proof.** Integrals of vectors in a closed convex cone remain in the cone. Summing over a partition gives the original mass identity. For a fixed bin history, its policy factors are constant across the corresponding cells. Successive integration of the operator product therefore gives the product of the cell operators, in the original temporal order. This establishes every finite binned record probability. In the posterior identity, substitute $z^+(y)\lambda B_a(y)z=B_a(y)z$ on the positive-density set. The remaining outputs are zero because they lie in the cone and have zero mass. $\square$

The coarsened posterior is a conditional average, not the posterior at a representative observation value. It preserves exactly the information retained by the event history. An arbitrary policy that reacts differently to two observations inside the same cell is not bin-measurable, so the preceding exact-policy conclusion does not apply to it.

Cell refinement is compatible with this semantics: a parent operator is the sum of its children. In this setting those cell operators are positive probability branches. This positivity is an extra property of event integration, not a property of every signed spectral packet in the signal archive.

# 63. Averaging transformations has a covariance defect

A common discretization replaces a family of matrices $K(y)$ by its mean and then applies $X\mapsto KXK^{\mathsf T}$. This is generally the wrong mean operation.

**Proposition 57. Exact covariance correction for an averaged congruence.** Let $\nu$ be a probability measure and suppose $K(y)$ has square-integrable entries. Put $\bar K=\int K(y)\,\nu(dy)$. For every symmetric $X$,

$$
\boxed{
\int K(y)XK(y)^{\mathsf T}\,\nu(dy)
=\bar KX\bar K^{\mathsf T}
+\int (K(y)-\bar K)X(K(y)-\bar K)^{\mathsf T}\,\nu(dy).
}
$$

The correction is positive semidefinite when $X\succeq0$. For $K(u)=K_0+uK_1$, it equals $\operatorname{Var}_\nu(u)K_1XK_1^{\mathsf T}$. On a uniform interval of width $h$, the variance is $h^2/12$.

**Proof.** Substitute $K=\bar K+(K-\bar K)$ and expand. The two cross terms integrate to zero. The remaining integrand is a positive congruence when $X$ is positive. For an affine matrix function the centered term is $(u-\mathbb E_\nu u)K_1$, giving the variance formula. Integrating the square of a centered uniform variable gives $h^2/12$. $\square$

This is a defect between two operations: averaging a transformation parameter and applying its quadratic action. It is not the same as the residual from dropping a signal packet, although both fit the framework's requirement to record failures of commutation.

For the example in Section 66, equal bins with midpoint evaluation lose total mass

$$
\boxed{\frac{3}{4n^2}}
$$

when there are $n$ bins. With one bin, midpoint evaluation retains only one quarter of the required mass. Exact integration or the covariance correction restores the missing contribution. Dividing an inaccurate approximation by a guessed normalizer would define another model rather than establish this identity.

# 64. A valid density approximation with a resolution bound

Exact coarsening gives a finite event model. To compare complete continuous observation laws, lift that model back to a density on the same observation space. Assume all cells have positive reference mass and put

$$
B_a^\Pi(y)=\frac{B_{a,j}}{\mu(A_j)}\quad(y\in A_j).
$$

This uses the normalized reference measure inside each cell. It is an explicit density approximation, not an assertion that the original conditional density was constant there.

**Proposition 58. Positive cell-average approximation.** The family $B_a^\Pi$ is cone preserving and mass conserving. It has exactly the same cell operators as $B_a$. Let $Y$ have a metric and suppose

$$
\|B_a(y)-B_a(v)\|_{C\to C}\leq L\,d(y,v)
$$

in the induced base norm, with every cell of diameter at most $h$. Then

$$
\epsilon_\Pi:=\sup_{a,z\in K}\int
\|(B_a(y)-B_a^\Pi(y))z\|_C\,\mu(dy)
\leq Lh.
$$

For equal intervals of width $h$ under the uniform measure on $[-1,1]$, the sharper bound is $\epsilon_\Pi\leq Lh/3$.

**Proof.** Each cell average is a positive scalar multiple of a positive cell operator. Its integral over that cell is $B_{a,j}$, proving both normalization and exact cell agreement. For $y\in A_j$, subtract the cell average and use

$$
\|(B_a(y)-B_a^\Pi(y))z\|_C
\leq\frac{L}{\mu(A_j)}\int_{A_j}d(y,v)\,\mu(dv),
$$

because $\|z\|_C=1$. Integrating over $y$ proves the diameter bound. Two independent uniform points in an interval of width $h$ have mean absolute separation $h/3$, obtained by integrating over its two triangles. Applying this inside every equal interval gives the sharper bound. $\square$

The Lipschitz constant is a declared operator bound. It is not a fit residual inferred from adjacent samples. The comparison needs a common domain and a common reference measure. If two kernels are only close in Euclidean coefficient norm, the relevant norm-conversion constant must be included.

In the full $2\times2$ symmetric-matrix example, the pullback base norm is

$$
\|(m,x,y)\|_C=\max\{|m|,\sqrt{x^2+y^2}\}=\|\mathcal J(m,x,y)\|_1.
$$

There $\|K(u)\|_2\leq2$ and $\|K(u)-K(v)\|_2\leq(3/2)|u-v|$. The identity

$$
K(u)XK(u)^{\mathsf T}-K(v)XK(v)^{\mathsf T}
=(K(u)-K(v))XK(u)^{\mathsf T}
+K(v)X(K(u)-K(v))^{\mathsf T}
$$

and $\|AXB\|_1\leq\|A\|_2\|X\|_1\|B\|_2$ give $L=6$. The rotated action uses an orthogonal matrix before this map and has the same bound. Equal bins therefore give $\epsilon_\Pi\leq4/n$, capped by two for two valid instruments. The inequality is sufficient, not asserted sharp.

# 65. Full continuous record laws inherit the stability argument

The base-norm proof from Part IV has an integral version. Its hypotheses must be supplied rather than inferred by replacing a finite sum with an integral in a program.

**Proposition 59. Continuous-record total-variation bound.** Let $B_a(y)$ and $\widetilde B_a(y)$ satisfy Proposition 52 on a common $(C,\lambda,\mu)$, and let the two models use the same measurable policy on every common observation history. Suppose their initial states satisfy $\|z_0-\widetilde z_0\|_C\leq e_0$ and their time-$t$ instruments satisfy

$$
\sup_{a,z\in K}\int\|(B_{a,t}(y)-\widetilde B_{a,t}(y))z\|_C\,\mu(dy)
\leq\epsilon_t.
$$

The length-$T$ record laws, including actions when the policy is randomized, obey

$$
\boxed{
\|P_T-\widetilde P_T\|_{\mathrm{TV}}
\leq\min\left\{1,\frac{e_0+\sum_{t=0}^{T-1}\epsilon_t}{2}\right\}.
}
$$

No lower bound on each observation density is required. For identical initial states and the equal-bin approximation in Section 64, the example has the sufficient bound $\min(1,2T/n)$.

**Proof.** For any positive decomposition $x=u-v$, cone preservation and mass conservation give

$$
\int\|B_a(y)x\|_C\,\mu(dy)
\leq\int\lambda B_a(y)(u+v)\,\mu(dy)
=\lambda u+\lambda v.
$$

Taking the infimum proves integrated instrument contraction. At each continuous history let $v_h,\widetilde v_h$ be the unnormalized state densities, including the policy factors. Split the next difference as

$$
B_a(y)(v_h-\widetilde v_h)
+(B_a(y)-\widetilde B_a(y))\widetilde v_h.
$$

Integrate the first term using contraction. The second is bounded by $\epsilon_t\lambda\widetilde v_h$ after normalizing only its nonzero positive mass. Its integral over histories is at most $\epsilon_t$. Tonelli's theorem applies to these nonnegative norm bounds, and operator integrability supplies well-defined finite-dimensional integrals. The integrated state discrepancy therefore satisfies $D_{t+1}\leq D_t+\epsilon_t$. Finally $|\lambda x|\leq\|x\|_C$ bounds the record-density difference, and total variation is half its absolute integral. $\square$

This result compares one common policy, not two policies optimized separately. It concerns the whole law and can become uninformative at long horizons. It is not a uniform posterior contraction theorem.

For a measurable event $H$ of probability $p=P_T(H)>0$, the restriction-and-normalization argument of Proposition 44 works for measures as well as finite vectors. When both conditional laws exist, their total-variation distance is at most $\min(1,\delta/p)$ if the full-law distance is at most $\delta$. The event probability is invariant under a reference-measure change. A density value at one point is not a substitute for that event probability.

The full-law comparison between $B$ and $B^\Pi$ permits any common measurable policy because both are continuous-output models on the same space. The exact equivalence to the finite bin model in Proposition 56 instead requires a bin-measurable policy. These are different conclusions with different observation information.

# 66. A complete continuous-observation example

Use the same three-coordinate matrix embedding as Section 57. Set

$$
K(u)=\frac12\begin{pmatrix}1+3u&0\\0&1-3u\end{pmatrix},
\qquad -1\leq u\leq1,
\qquad \mu(du)=du/2.
$$

The direct action uses $X\mapsto K(u)XK(u)^{\mathsf T}$. The rotated action first applies the unchanged rotation congruence from Section 57, giving

$$
X\longmapsto\frac15 K(u)WXW^{\mathsf T}K(u)^{\mathsf T}.
$$

Both are exactly normalized because $\int K(u)^{\mathsf T}K(u)\,du/2=I$ and $W^{\mathsf T}W=5I$. In predictive coordinates, write

$$
\begin{gathered}
a(u)=\frac{1+9u^2}{4},\qquad
b(u)=\frac{3u}{2},\qquad
c(u)=\frac{1-9u^2}{4},\\[3pt]
B_0(u)=\begin{pmatrix}a(u)&b(u)&0\\b(u)&a(u)&0\\0&0&c(u)\end{pmatrix},
\qquad B_1(u)=B_0(u)T.
\end{gathered}
$$

Although $c(u)$ is negative for part of the interval, both actions preserve the disk cone. Entrywise sign is not the positivity criterion in these coordinates. The initial state is $z_0=(1,0,0)^{\mathsf T}$, or the matrix $I/2$.

## 66.1 Event tables and moment reconstruction

Let the three future tests be the empty test, a nonnegative observation after action zero, and a nonnegative observation after action one. Their rows form

$$
Q=\begin{pmatrix}
1&0&0\\
1/2&3/8&0\\
1/2&9/40&-3/10
\end{pmatrix}.
$$

Use histories consisting of the empty history, a nonnegative observation under action zero, and that history followed by a nonnegative observation under action one. Their unnormalized columns are

$$
S=\begin{pmatrix}
1&1/2&107/320\\
0&3/8&3/10\\
0&0&-3/40
\end{pmatrix}.
$$

The learner is supplied only the resulting integral tables and the declared class. Its core is

$$
\boxed{
H=\begin{pmatrix}
1&1/2&107/320\\
1/2&25/64&179/640\\
1/2&107/320&823/3200
\end{pmatrix},\qquad\det H=\frac{81}{25600}.
}
$$

The core is not required to be symmetric. Its rows are tests and its columns are histories, which are different experiments. The three moment orders use

$$
W_2=\begin{pmatrix}1&0&1/3\\0&1/3&0\\1/3&0&1/5\end{pmatrix},
\qquad
W_2^{-1}=\begin{pmatrix}9/4&0&-15/4\\0&3&0\\-15/4&0&45/4\end{pmatrix},
\qquad\det W_2=\frac4{135}.
$$

Proposition 54 reconstructs $QB_a(u)Q^{-1}$ from $H$ and the six inserted-moment tables. The code that performs this reconstruction imports no generating matrices. The separate generator produces the tables and is used only in the verification suite. These are population values from an exact example, not learned sample estimates.

## 66.2 Two densities and a genuine event probability

For a direct observation value $u=1/2$, the density and updated state are

$$
p_1=\frac{13}{16},\qquad z_1=(1,12/13,0)^{\mathsf T}.
$$

If the rotated action next gives $u=-1/2$, they are

$$
p_2=\frac{413}{1040},\qquad
z_2=(1,-312/413,-240/413)^{\mathsf T}.
$$

Their product $413/1280$ is a joint density with respect to $(du/2)^{\otimes2}$, not the probability of those two exact values. The two point values each have zero probability in this nonatomic model.

By contrast, the event $u_1\geq0$ under action zero followed by $u_2\geq0$ under action one has actual probability

$$
\boxed{\frac{107}{320},}
$$

and its conditional state is $(1,96/107,-24/107)^{\mathsf T}$. Exact bin operators produce this value without quadrature.

The final point-conditioned state remains strictly inside the disk:

$$
\det\mathcal J(z_2)=\frac{15625}{682276}>0.
$$

A pure boundary state can instead have zero density at isolated observations. The checker rejects conditioning on such a zero-density branch. It does not manufacture a posterior by flooring its denominator.

## 66.3 The missing covariance is exactly calculable

On an interval with midpoint $v$ and width $h$, the average matrix instrument is

$$
\mathbb E[K(u)XK(u)^{\mathsf T}]
=K(v)XK(v)^{\mathsf T}
+\frac{h^2}{12}K_1XK_1^{\mathsf T},
\qquad K_1=\frac32\operatorname{diag}(1,-1).
$$

The correction is itself a positive congruence. The cell operator multiplies this mean by the cell mass $h/2$. Equal bins have width $2/n$, so omitting the covariance loses trace $3/(4n^2)$ over the full partition. The reference calculation checks both the exact matrix identity and this mass defect for several rational partitions.

# 67. A declared template can be recognized without being rediscovered

General curved-domain learning remains difficult. There is a useful finite case between supplying a finished coordinate certificate and claiming unrestricted domain discovery.

Suppose a structural library supplies a certified template with polynomial coefficients $C_{a,k}$, mass row $\lambda$ and embedding $\mathcal J$. Suppose observed population tables produce coefficients $\widehat C_{a,k}$ and mass row $\widehat\lambda$ of the same dimension.

**Proposition 60. Exact recognition of a fixed certified template.** The equations

$$
\boxed{
\widehat C_{a,k}T=TC_{a,k},\qquad
\widehat\lambda T=\lambda
}
$$

are linear in $T$. Every invertible solution transports the template certificate to the fitted coordinates by $\widehat{\mathcal J}=\mathcal JT^{-1}$. If the fitted coefficient family is observable, meaning the rows $\widehat\lambda\widehat C_w$ span the dual space, the solution is unique. The fitted initial state must still be tested in the transported normalized cone.

**Proof.** All coefficient matrices are fixed, so the displayed constraints are linear. An invertible solution yields $\widehat B_a(u)=TB_a(u)T^{-1}$ coefficient by coefficient. Substitution in the template intertwining identity proves the transported certificate. To prove uniqueness, let $D$ be the difference of two solutions. It satisfies $\widehat C_{a,k}D=DC_{a,k}$ and $\widehat\lambda D=0$. Therefore $\widehat\lambda\widehat C_wD=0$ for every coefficient word. Observability makes every column of $D$ zero. An initial state outside the transported cone is not repaired by this operator identity, which explains the separate check. $\square$

For the worked example, the linear system has the unique solution $T=Q$ from Section 66. The learner receives the population tables and a fixed structural template. It reconstructs the operators, solves the linear match, transports the embedding and exports a certificate. Independent replay then needs only that certificate. It does not refit, search, or import the template or generator.

This is template recognition, not unrestricted geometry discovery. The supplied template includes the specific operator family. An incompatible model is rejected rather than changed to fit the template. The reference routine also withholds a result for an underdetermined or singular match. Noise would require a declared approximate match and a separate validity or correction argument. This edition's recognition example is exact.

For fixed embeddings, polynomial Gram optimization offers a broader construction route than fixed-template matching. That convex proposal problem is stated in Section 59 but is not implemented as a general solver here. The independent checker remains useful regardless of whether a proposal came from a template, symbolic derivation or an optimization routine.

# 68. The combined continuous polynomial sector

**Proposition 61. Conditional continuous realization with a finite domain certificate.** Assume a controlled continuous-observation process has the declared finite predictive dimension and polynomial operator-density degree, a fixed uniform reference measure on $[-1,1]$, and an invertible complete event-test core. Exact moment tables identify its operator density in test coordinates by Proposition 54.

If the fitted family and initial state admit a checked matrix/Gram certificate of Proposition 53, the supplied realization is internally valid at every observation value and finite horizon. A successful invertible fixed-template recognition is one sufficient way to construct such a certificate. Exact coordinate transport and complete packet synthesis preserve the represented event probabilities. Individual signed state packets still need the separate positivity condition before probabilistic interpretation.

Exact observation-cell integration gives the precise finite event model for bin-measurable policies. Positive cell-average density approximations have the resolution bound of Proposition 58. Two certified models on a common cone and common reference measure satisfy Proposition 59's full-law bound whenever the declared instrument discrepancy is controlled.

**Proof.** Moment identification uses the true dimension and degree hypotheses to apply Proposition 54. The independent Gram identity establishes positivity on the whole declared interval, while the exact integral mass identity supplies normalization through Proposition 52. Proposition 60 supplies a transported witness in the template case. Coordinate cancellation and full packet synthesis are exact identities. Proposition 56 proves the cell-model statement. Propositions 58 and 59 provide the two approximation conclusions with their common-domain and common-policy assumptions unchanged. $\square$

For a noisy fitted model, the certificate alone proves only internal validity. A guarantee about the generating process requires a valid uncertainty set covering it. A common-domain certificate over a convex uncertainty family can be checked at complete-family vertices with the same embedding, because the operator identities, Gram positivity and mass constraints survive convex combination. This does not justify an uncertainty set that excludes the true degree, rank or dynamics.

The construction leaves visible what is often collapsed into the phrase signal model: a represented state, an operator-valued observation density, a reference measure, a valid probability domain, an observation protocol and an approximation budget. Each is needed for a different reason.

# 69. Fifth-block checkpoint

The new block addresses the specific curved-domain obstruction without damping the old rotation model. It extends the probability semantics to continuous observations, provides a finite polynomial certificate over an entire interval, and supplies a conditional event-moment reconstruction. It also proves exact bin semantics, the covariance defect of averaging transformations, and a continuous-record stability bound.

The cumulative volume now contains 61 propositions. This count is a navigation aid, not a count of historically novel results or a measure of general intelligence. The general proofs are the arguments in the text. Exact finite checks validate the worked calculations, replay certificates and reject deliberately malformed inputs. No Lean kernel was run for this block.

The release implements a factored polynomial certificate checker, population-moment reconstruction, exact fixed-template recognition and finite examples. It does not implement general curved-domain discovery, a generic semidefinite solver, continuous-time dynamics or a statistically trained production model. Production PR-LASM 2.3.0 remains unchanged.

The remaining work is concentrated in representation discovery rather than in renaming the existing components. It includes useful curved-domain synthesis beyond fixed templates, controlled approximation outside a finite polynomial basis, dependent-data identification, unknown reset mechanisms, and nonlinear observables whose learning and refinement costs are bounded. The continuous moment counterexample shows why those assumptions cannot simply be omitted. The exact curved certificate shows why they also should not be confused with a need to discretize every legitimate signal model into finitely many positive states.
