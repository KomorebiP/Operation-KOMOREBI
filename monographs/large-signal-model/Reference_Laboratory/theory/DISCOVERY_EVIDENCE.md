# Part VI. Certificate discovery, approximation and sequential evidence

A signal model must distinguish a representation that preserves probability from a representation that predicts the observed process accurately. Part V gave an exact curved certificate and a way to recognize a supplied operator template. It also made the polynomial-degree assumption explicit. This block advances both boundaries without identifying them with each other.

The first development is a restricted discovery procedure. It recovers an ellipsoidal probability domain from fitted polynomial operators, without a supplied template, matrix embedding or hidden generator. The second is a positive approximation theorem for operator densities outside a finite polynomial class. The third is sequential evidence under dependent observations, including the cost of action coverage. Together they separate structural validity, approximation error and observable disagreement.

The invariant-form and quadratic-certificate ingredients belong to classical systems theory [R8, R13]. Positive polynomial averaging uses the classical Bernstein--Durrmeyer kernel [R19]. The sequential argument is an elementary martingale confidence sequence, not a new concentration principle [R20]. The contribution of this block is their connection to the large signal model's explicit representation contracts and to independently replayable examples. Propositions 62--70 have proofs below. No proof kernel or production training system is invoked.

# 70. An ellipsoidal certificate with an orientation test

Work in mass-first coordinates $z=(m,x)\in\mathbb R\times\mathbb R^d$, with $\lambda=(1,0,\ldots,0)$. For a center $c\in\mathbb R^d$ and a symmetric positive definite matrix $H$, define

$$
C_{c,H}=\{(m,x):m\geq0,\ (x-mc)^{\mathsf T}H(x-mc)\leq m^2\}.
$$

Its normalized base is an ellipsoid. Set

$$
S_c=\begin{pmatrix}1&0\\-c&I\end{pmatrix},\qquad
Q=S_c^{\mathsf T}\begin{pmatrix}1&0\\0&-H\end{pmatrix}S_c.
$$

Then $C_{c,H}=\{z:m\geq0,\ z^{\mathsf T}Qz\geq0\}$. The cone is proper and generating, and $m$ is strictly positive on every nonzero cone element. These facts follow by an invertible linear transformation to the Lorentz cone. In particular, an output with zero mass in the cone is the zero vector.

Let $B_a(u)$ be polynomial operator densities on $[-1,1]$, relative to $du/2$. Write

$$
\lambda B_a(u)=(b_{a,0}(u),b_a(u)^{\mathsf T}),\qquad
\beta_a(u)=b_{a,0}(u)+b_a(u)^{\mathsf T}c.
$$

**Proposition 62. Oriented quadratic probability certificate.** Suppose that for each action and every $u\in[-1,1]$ there are $\tau_a(u)\geq0$ and $R_a(u)\succeq0$ satisfying

$$
\boxed{B_a(u)^{\mathsf T}QB_a(u)-\tau_a(u)Q=R_a(u),}
$$

and that

$$
\boxed{\beta_a(u)\geq0,\qquad
\beta_a(u)^2-b_a(u)^{\mathsf T}H^{-1}b_a(u)\geq0.}
$$

If $z_0\in C_{c,H}$ has mass one and $\lambda\int B_a(u)\,du/2=\lambda$, then every operator preserves $C_{c,H}$. The supplied model has valid probabilities at every finite horizon. Polynomial sum-of-squares witnesses for the scalar inequalities and for $R_a$ make this a finite certificate.

**Proof.** For $z\in C_{c,H}$, the quadratic identity gives

$$
(B_a z)^{\mathsf T}Q(B_a z)
=\tau_a z^{\mathsf T}Qz+z^{\mathsf T}R_a z\geq0.
$$

For a nonzero $z$, write $x=m(c+w)$ with $w^{\mathsf T}Hw\leq1$. Its output mass is $m(\beta_a+b_a^{\mathsf T}w)$. Cauchy--Schwarz in the $H$ inner product bounds this below by

$$
m\left(\beta_a-\sqrt{b_a^{\mathsf T}H^{-1}b_a}\right)\geq0.
$$

Thus both inequalities defining the desired sheet of the quadratic cone hold. The zero input causes no difficulty. Integrated mass conservation gives normalization, and induction gives the finite-horizon conclusion. For polynomial data, identities between coefficients and nonnegative sums of polynomial squares establish the displayed hypotheses throughout the interval. Terms multiplied by $1-u^2$ are also nonnegative on that interval. $\square$

The orientation test is essential. The matrix $-I$ preserves every quadratic form, but maps positive mass to negative mass. A quadratic inequality without its mass orientation can certify the wrong sheet. Likewise, testing finitely many values of $u$ is not a substitute for a polynomial identity and its positivity witness.

This is a sufficient language, not a completeness theorem for all cones. The reference checker accepts rational scalar and matrix sum-of-squares witnesses. Its discovery routine uses the narrower conformal case $R_a=0$, but the checker does not confuse that search restriction with the theorem's scope.

# 71. Geometry can be proposed from the operators themselves

An operator identity can reveal a useful coordinate geometry without specifying that geometry in advance. Suppose two fitted operators evaluated at an anchor $u_*$ give an invertible ratio

$$
F=B_b(u_*)B_a(u_*)^{-1},\qquad \lambda F=\lambda.
$$

This ratio is an algebraic object. It need not be a physically available action or a positive map by itself. In mass-first coordinates write

$$
F=\begin{pmatrix}1&0\\b&A\end{pmatrix}.
$$

If $I-A$ is invertible, its fixed center is $c=(I-A)^{-1}b$. The centered spatial action is $A$. A candidate invariant metric obeys

$$
A^{\mathsf T}HA=H.
$$

With $A$ fixed, this is a linear equation in the independent entries of symmetric $H$. No coordinate template appears in that equation.

**Proposition 63. Conditional operator-only ellipsoid discovery.** Suppose the symmetric solution space of $A^{\mathsf T}HA=H$ is one-dimensional and contains a positive definite matrix $H_0$. Let a rank-one fitted branch at a declared observation have a nonzero-mass image, normalized to $v=(1,x_v)$. If $x_v\neq c$, define

$$
H=\frac{H_0}{(x_v-c)^{\mathsf T}H_0(x_v-c)}.
$$

This gives a unique positive definite metric in that solution space for which $v$ is on the normalized boundary. If this proposed geometry passes every hypothesis of Proposition 62 for the complete fitted family and its initial state, it is an internally valid probability-domain certificate. The proposal requires no supplied template. Failure at any step withholds this certificate and does not establish model invalidity.

**Proof.** Invertibility of $I-A$ gives the unique center. One-dimensionality makes every symmetric invariant form a scalar multiple of $H_0$. The nonzero displacement has strictly positive squared $H_0$ length, so the normalization is well-defined, positive and independent of the initially chosen positive scale. The final acceptance test is exactly Proposition 62. Neither invariance under the ratio nor the choice of a boundary image alone is asserted to certify the full family. $\square$

The rank-one image proposes a scale. It does not prove that every possible probability domain must place that image on its boundary. Some valid models have many admissible domains. The procedure can also fail because there is no suitable ratio, because invariant forms are not unique, because no rational rank-one anchor is found, or because the chosen ellipsoid fails another branch. These are explicit search outcomes.

## 71.1 The continuous example no longer needs its template

Use the same exact population moment tables as Section 66. The existing moment learner first reconstructs the two polynomial operators in test coordinates. The new discovery routine receives those operators, their mass row and initial vector. It does not read `continuous_template.json` or import the population generator.

At $u_*=0$, the operator ratio gives the required invariant-form equation. A rational rank-one observation supplies a boundary image. The recovered center and metric are

$$
\boxed{
c=\begin{pmatrix}1/2\\1/2\end{pmatrix},\qquad
H=\begin{pmatrix}100/9&-20/3\\-20/3&100/9\end{pmatrix}.
}
$$

The two metric eigenvalues are $40/9$ and $160/9$. For both actions the exact certificate is

$$
\begin{aligned}
B_a(u)^{\mathsf T}QB_a(u)&=\frac{(1-9u^2)^2}{16}Q,\\
\beta_a(u)&=\frac{1+9u^2}{4},\\
\beta_a(u)^2-b_a(u)^{\mathsf T}H^{-1}b_a(u)
&=\frac{(1-9u^2)^2}{16}.
\end{aligned}
$$

Every scalar on the right has an exact rational sum-of-squares representation. Integrated mass is unchanged. The fitted initial state is the ellipsoid center, and the two densities $13/16$ and $413/1040$ from Section 66 are unchanged. This is a new certificate construction for the same model, not a change to its predictions.

The exported JSON contains the fitted operators, center, metric, initial state and all witnesses. Independent replay needs only that JSON. The discovery calculation is also checked on three additional rational coefficient families and affine coordinate changes. Those finite examples exercise the stated sector and do not establish unrestricted discovery.

The procedure currently uses three predictive coordinates, a two-dimensional ellipsoid, a finite rational anchor list, a one-dimensional invariant-form space and rational rank-one roots. It proposes only exactly conformal polynomial branches whose scalar nonnegativity can be resolved by its factor-based sum-of-squares routine. General noisy or jointly optimized curved-domain learning remains outside this implementation.

# 72. Approximate an unknown density without assuming its exact degree

Part V identified a polynomial operator density under an exact degree assumption. A different question is how to approximate a valid density that is not a polynomial at all.

In this section observations lie in $[0,1]$ with Lebesgue reference measure. This is an explicit change from the preceding $[-1,1]$ convention. Under $v=(u+1)/2$, the probability measure $du/2$ becomes $dv$. A Lipschitz constant with respect to $u$ becomes twice as large with respect to $v$.

Write the Bernstein basis and the classical Bernstein--Durrmeyer kernel as

$$
b_{n,k}(x)=\binom nk x^k(1-x)^{n-k},\qquad
D_n(x,v)=(n+1)\sum_{k=0}^n b_{n,k}(x)b_{n,k}(v).
$$

Both variables range over $[0,1]$. The kernel is nonnegative and integrates to one in either variable. Let $B_a(v)$ be any operator-norm integrable density preserving a common probability cone $C$, with mass functional $\lambda$ and normalized base $K$. Define

$$
B_a^{[n]}(x)=\int_0^1D_n(x,v)B_a(v)\,dv
=\sum_{k=0}^n b_{n,k}(x)C_{a,n,k},
$$

where

$$
C_{a,n,k}=(n+1)\int_0^1b_{n,k}(v)B_a(v)\,dv.
$$

**Proposition 64. Valid positive polynomial approximation.** Every $B_a^{[n]}$ preserves $C$, has degree at most $n$, and satisfies exact integrated mass conservation. If

$$
\|B_a(v)-B_a(x)\|_{C\to C}\leq L|v-x|
$$

for all actions, then

$$
\boxed{
\sup_{a,z\in K}\int_0^1
\|(B_a^{[n]}(x)-B_a(x))z\|_C\,dx
\leq\frac{L}{\sqrt{3(n+2)}}.
}
$$

With identical initial states, the corresponding length-$T$ laws under a common policy differ in total variation by at most

$$
\boxed{\min\left(1,\frac{TL}{2\sqrt{3(n+2)}}\right).}
$$

No finite true-degree hypothesis is needed.

**Proof.** Nonnegative integration preserves the closed convex cone. Since $\int_0^1b_{n,k}=1/(n+1)$ and $\sum_k b_{n,k}=1$, the kernel is doubly stochastic. Its integral in $x$ gives $\int B_a^{[n]}=\int B_a$, proving exact mass conservation.

For the error, subtract $B_a(x)$ inside the kernel integral, apply the Lipschitz inequality and use $\|z\|_C=1$. The integrated discrepancy is at most $L\mathbb E|V-X|$ under the joint probability density $D_n(x,v)$. This joint law can be constructed by first choosing $J$ uniformly from $\{0,\ldots,n\}$, and then drawing $X,V$ independently, conditionally on $J=k$, with density $(n+1)b_{n,k}$.

That conditional beta law has variance

$$
\operatorname{Var}(X\mid J=k)
=\frac{(k+1)(n-k+1)}{(n+2)^2(n+3)}.
$$

The average of $(k+1)(n-k+1)$ over $k=0,\ldots,n$ is $(n+2)(n+3)/6$, obtained by summing the first two integer powers. Hence

$$
\mathbb E(V-X)^2
=2\mathbb E\operatorname{Var}(X\mid J)
=\frac1{3(n+2)}.
$$

Cauchy--Schwarz gives the claimed integrated bound. The whole-law conclusion is Proposition 59 applied to the two valid instruments on the same domain. $\square$

This construction approximates the operator density itself. It does not average a congruence factor and omit its covariance. Its coefficients are positive operators even when their entries in predictive coordinates are signed.

Operationally, it replaces the raw observation $v$ by a noisy observation $x$ drawn from $D_n(x,v)$. It preserves total mass and underlying unconditioned evolution, not the entire original observation law. That changed law is what the bound measures. A prediction policy must be compared as the same function of the reported history.

## 72.1 A nonpolynomial density and a failed ordinary truncation

Consider the valid scalar density

$$
p(v)=\frac12+2\left|v-\frac12\right|.
$$

It integrates to one, takes values between $1/2$ and $3/2$, and has Lipschitz constant two. It is not a single polynomial on $[0,1]$. Proposition 64 nevertheless supplies normalized positive polynomial approximations at every degree, with an explicit approximation budget.

An ordinary orthogonal truncation need not preserve that validity. The valid density $p(v)=3v^2$ has degree-one $L^2$ projection

$$
q(v)=3v-\frac12,
$$

which is negative near zero. The positive construction at degree one instead gives

$$
p^{[1]}(v)=v+\frac12.
$$

The two approximations solve different mathematical problems. Neither has permission to call its approximation error zero. The reference checks derive both expressions exactly.

# 73. Keep approximation bias separate from coefficient error

The positive approximation theorem assumes access to exact integral coefficients. A fitted model introduces another discrepancy. Its coefficient estimates need their own validity constraints.

**Proposition 65. Certified coefficient error and approximation bias.** Suppose every fitted coefficient $\widetilde C_{a,n,k}$ preserves the same cone $C$, and

$$
\lambda\frac1{n+1}\sum_{k=0}^n\widetilde C_{a,n,k}=\lambda.
$$

Then $\widetilde B_a^{[n]}(x)=\sum_k b_{n,k}(x)\widetilde C_{a,n,k}$ is internally valid. If

$$
\sup_{z\in K}\|(C_{a,n,k}-\widetilde C_{a,n,k})z\|_C
\leq\eta_{a,k},
$$

its integrated discrepancy from the original Lipschitz density is at most

$$
\boxed{
\frac{L}{\sqrt{3(n+2)}}+
\max_a\frac1{n+1}\sum_{k=0}^n\eta_{a,k}.
}
$$

A known additional model-correction discrepancy is added to this budget, not absorbed into the approximation term.

**Proof.** Nonnegative Bernstein weights preserve cone positivity, and their integrals prove normalization. For any $z\in K$, the triangle inequality gives

$$
\int\|\textstyle\sum_k b_{n,k}(x)(C_{a,n,k}-\widetilde C_{a,n,k})z\|_C\,dx
\leq\frac1{n+1}\sum_k\eta_{a,k}.
$$

Add the approximation error from Proposition 64. A separate correction is handled by another application of the triangle inequality. $\square$

This is a conditional approximation-and-estimation theorem, not a claim that more coefficients always improve a finite-data estimator. Increasing $n$ reduces the stated bias bound while changing the number and conditioning of the quantities to be estimated. A cone witness proves that the resulting object is a probability model. It does not prove that the coefficient error budgets cover the generating process.

The moments needed for $C_{a,n,k}$ are bounded Bernstein-weighted experiments. Their interpretation as full operator coefficients still requires suitable predictive-state coverage or a justified observable core. The next section provides sequential evidence for conditional experiments, not an automatic replacement for those identification assumptions.

# 74. Evidence from dependent observations

Let $\mathcal F_{t-1}$ denote the available information immediately before observing the next measurement, including the chosen action, current model and any test selected using past data. A predictable test is a measurable function $\phi_{t,j}$ of the upcoming measurement, chosen from this information, with values in $[0,1]$. Put

$$
X_{t,j}=\phi_{t,j}(Y_t),\quad
m_{t,j}=\mathbb E[X_{t,j}\mid\mathcal F_{t-1}],\quad
p_{t,j}=\text{the model's prediction for that test}.
$$

The model prediction is also predictable. It may change as the model learns. The true conditional mean $m_{t,j}$ may depend on the entire past. No independence, stationarity or known reset state is assumed in this paragraph.

Choose budgets $\alpha_j>0$ for a finite or countable prospectively specified family of test rules, with $\sum_j\alpha_j\leq\delta$. Define

$$
R_{t,j}=\sum_{s=1}^t(X_{s,j}-p_{s,j}),\qquad
D_{t,j}=\sum_{s=1}^t(m_{s,j}-p_{s,j}).
$$

**Proposition 66. Time-uniform predictable-residual certificate.** With probability at least $1-\delta$, for every time $t\geq1$ and every registered rule $j$,

$$
\boxed{
|R_{t,j}-D_{t,j}|\leq
b_{t,j},\qquad
b_{t,j}=\sqrt{\frac t2\log\frac{2t(t+1)}{\alpha_j}}.
}
$$

For variables taking values in an interval of width $c$, multiply the boundary by $c$. The simultaneous guarantee remains valid when the observation time is chosen from the data.

**Proof.** For a random variable $X\in[0,1]$ with conditional mean $m$, its conditional centered logarithmic moment-generating function has value and first derivative zero at the origin. Its second derivative is the variance under exponential tilting. A variable supported on $[0,1]$ has variance at most $1/4$, because its squared distance from $1/2$ is at most $1/4$. Integrating twice gives

$$
\mathbb E[e^{\theta(X-m)}\mid\mathcal F]\leq e^{\theta^2/8}.
$$

Iterating this conditional inequality gives the same exponential bound for the martingale sum $\sum_{s\leq t}(X_{s,j}-m_{s,j})$. Optimizing the exponential Markov inequality gives the two-sided bound $2\exp(-2b^2/t)$. At the displayed $b_{t,j}$ this is $\alpha_j/[t(t+1)]$. Sum over $t$, using $\sum_{t\geq1}1/[t(t+1)]=1$, and then over $j$. The resulting event holds at every time, so it also holds at a data-selected time. Scaling the variable proves the range version. $\square$

This elementary boundary pays a logarithmic time-union cost. It is not claimed to be optimal. Stronger confidence-sequence constructions are available in the literature [R20]. The proof here is supplied because the exact assumptions and the estimated object matter more than a sharp constant in this foundation.

The certificate estimates accumulated **conditional predictive drift**, not one fixed unconditional population probability. A prospectively chosen rule may use history, but an analyst cannot inspect an entire data sequence and then retroactively choose an unrestricted test with the same budget. New rules can be registered with fresh budgets and applied to future observations, using elapsed time after registration.

# 75. Actions need coverage, not only more observations

For intervention evidence use the information $\mathcal H_{t-1}$ just before choosing the action. Let the action be randomized from a known history-dependent policy $\pi_t$. The true next-observation kernel under action $a$ is $P_t(\cdot\mid\mathcal H_{t-1},a)$. Randomization uses no unrecorded future information. For a predictable test $\phi_t\in[0,1]$, define

$$
\mu_t^a=\int\phi_t(y)P_t(dy\mid\mathcal H_{t-1},a),\qquad
W_t^a=\frac{\mathbf1_{\{A_t=a\}}\phi_t(Y_t)}{\pi_t(a\mid\mathcal H_{t-1})}.
$$

**Proposition 67. Covered adaptive-action evidence.** If the target action has $\pi_t(a\mid\mathcal H_{t-1})\geq\pi_{\min}>0$ at every time, then

$$
\mathbb E[W_t^a\mid\mathcal H_{t-1}]=\mu_t^a,
\qquad 0\leq W_t^a\leq1/\pi_{\min}.
$$

Consequently Proposition 66 gives a time-uniform certificate for $\sum_{s\leq t}\mu_s^a$ from $\sum_{s\leq t}W_s^a$, with its boundary multiplied by $1/\pi_{\min}$. The target is the average action-conditioned quantity along the encountered contexts, not a reset-population table or the state distribution under a different long-term policy.

**Proof.** Condition first on the action and then on its observation. Only action $a$ contributes, with probability $\pi_t(a\mid\mathcal H_{t-1})$, cancelling the denominator. The range bound follows directly. Apply the scaled conditional moment-generating-function argument to the resulting martingale differences. $\square$

This simple bound is conservative. Variance-aware weighting can improve it, but cannot remove the need for information about the action of interest. When $\pi_{\min}=0$, two models can give exactly the same law under the observed policy and disagree on a never-selected action. For example, both can emit a Bernoulli observation with parameter $1/2$ under action zero, while their action-one parameters are $1/10$ and $9/10$. Repeating action zero cannot distinguish them.

The action randomization and its recorded probabilities are part of the experimental assumption. An observational association with a hidden selection mechanism is not automatically an intervention estimate. Long-horizon off-policy predictions require additional occupancy or trajectory-coverage arguments that this one-step statement does not provide.

# 76. What a residual can prove about misspecification

A certified operator family can still be the wrong model for the observed process. Predictable residuals offer an explicit way to find that mismatch without pretending that internal validity proves empirical adequacy.

Let $P_{t,j}$ and $Q_{t,j}$ denote the true and proposed next-observation laws on the same actual history and action. The proposed law must be defined there. Since $0\leq\phi_{t,j}\leq1$,

$$
|m_{t,j}-p_{t,j}|\leq\|P_{t,j}-Q_{t,j}\|_{\mathrm{TV}}.
$$

**Proposition 68. Sequential evidence gives a lower error certificate.** On the simultaneous event of Proposition 66,

$$
\boxed{
\frac1t\sum_{s=1}^t\|P_{s,j}-Q_{s,j}\|_{\mathrm{TV}}
\geq\frac{(|R_{t,j}|-b_{t,j})_+}{t}.
}
$$

Thus crossing the boundary rejects zero conditional drift for that rule, with the registered false-rejection budget. Failing to cross supplies no general upper bound on total variation, no rank certificate and no guarantee for untested actions.

**Proof.** The triangle inequality gives $|D_{t,j}|\geq(|R_{t,j}|-b_{t,j})_+$. Also $|D_{t,j}|\leq\sum_s|m_{s,j}-p_{s,j}|\leq\sum_s\|P_{s,j}-Q_{s,j}\|_{\mathrm{TV}}$. Combine these inequalities. $\square$

## 76.1 Why one aggregate residual can miss conditional errors

The reference path has binary observations. Its true conditional probability of one is $4/5$ after a one and $1/5$ after a zero. A deliberately inadequate model predicts $1/2$ at every step. Its long-run aggregate frequency can be near one half even though its history-conditioned predictions are wrong.

Three tests are registered before the path is generated. One tests the raw observation. A second tests it only after the preceding observation was one. The third applies the same gate but uses the correct conditional predictor. Gates are functions of past data, not selected after seeing the current measurement.

For the supplied 4,096-step seeded path, the aggregate mean residual is approximately $0.00732$. The gated mean residual is approximately $0.14917$, while its time-uniform mean boundary is approximately $0.05114$. The lower certificate for average conditional total variation is approximately $0.09803$. The correctly predicted gated residual is approximately $-0.00303$.

These are illustrative path calculations, not estimated coverage rates. The theorem supplies the probability guarantee. The example supplies an explicit reason to test conditional structure rather than relying only on cancellation-prone aggregate residuals.

The exact reference suite also checks a dependent likelihood-ratio construction on every binary path through depth eight. Its expectation under the declared null is exactly one. This is an additional finite martingale calculation, not a replacement for the general argument or a claim that every possible test has been run.

# 77. Comparing a model with a process outside its representation

The earlier operator-norm law bounds compare two models on one common probability cone. A misspecified generating process may not have a representation in the fitted cone. It is useful to state the more basic comparison at the level of conditional observation laws.

Let $P$ be any causal process on a standard Borel observation space with finite actions. Let $Q$ be a proposed process. Both use the same measurable policy. Write $P_t(\cdot\mid h,a)$ and $Q_t(\cdot\mid h,a)$ for their next-observation kernels, and define

$$
d_t(h,a)=\|P_t(\cdot\mid h,a)-Q_t(\cdot\mid h,a)\|_{\mathrm{TV}}.
$$

The proposed kernel must be specified on every history needed for the comparison, including histories impossible under $Q$ but possible under $P$. A declared fallback on a model-null history completes a causal kernel without changing $Q$'s own law. An implementation that rejects such a history must report that rejection rather than silently claim to have filtered it.

**Proposition 69. Observation-law error without a shared state space.** With the same initial history, the length-$T$ joint action-and-observation laws satisfy

$$
\boxed{
\|P_T-Q_T\|_{\mathrm{TV}}
\leq\min\left(1,\sum_{t=0}^{T-1}
\mathbb E_{P,\pi}[d_t(H_t,A_t)]\right).
}
$$

An initial-history discrepancy adds its total variation. In particular, uniform bounds $d_t(h,a)\leq\epsilon_t$ give the upper bound $\min(1,\sum_{t<T}\epsilon_t)$.

**Proof.** Introduce hybrid laws that follow $P$ for the first $t$ transitions and $Q$ for the rest, with the common policy throughout. Two successive hybrids have the same $P$ prefix distribution up to time $t$ and the same future $Q$ kernel after the next transition. Conditional on that prefix and its policy-chosen action, changing the next kernel costs $d_t(h,a)$ in total variation. A common continuation kernel cannot increase total variation, because integration of a test bounded between zero and one produces another such test. Average over the shared prefix, sum the adjacent-hybrid bounds, and cap by one. The same contraction argument handles a different initial law. $\square$

This theorem does not make the right-hand side observable without further assumptions. Proposition 68 supplies lower evidence about visited conditional discrepancies, not an upper estimate for every future history. Turning a finite collection of residuals into an upper law guarantee requires additional regularity, coverage or a restricted class with a separating test family.

The distinction prevents a common logical jump: a model can pass several tests and still have a large untested discrepancy. Conversely, a statistically significant residual need not mean that its internal probability algebra is invalid. The model can be a valid distribution and an inadequate approximation at the same time.

# 78. An integrated theory of construction and correction

**Proposition 70. Separate structural acceptance, approximation control and sequential rejection.** Consider a fitted polynomial model in a declared predictive coordinate system, and prospectively registered observation tests with total budget $\delta$.

A successfully replayed quadratic certificate from Proposition 62 establishes internal all-horizon validity. A successful operator-only proposal from Proposition 63 is one way to obtain it, not an assumption that all valid models have such a proposal.

For any generating density on a common probability cone with a justified Lipschitz constant, a positive degree-$n$ approximation and certified coefficient budgets satisfy Propositions 64--65, hence a fixed-horizon upper law bound. If a generating process lies outside that representation, a separately justified bound on its conditional kernels instead invokes Proposition 69.

For predictable tests on actual dependent observations, Propositions 66 and 68 give simultaneous lower discrepancy certificates, including at data-selected stopping times. Covered randomized actions admit the contextual evidence of Proposition 67. These conclusions coexist without implying that structural acceptance or statistical nonrejection proves the generating process belongs to the model class.

**Proof.** Each structural statement is a deterministic consequence of its replayed equalities and inequalities. The approximation statements require their declared common-domain, regularity and coefficient conditions, or alternatively the conditional-kernel discrepancy assumptions. The statistical conclusions hold on the simultaneous probability event of Proposition 66. None of these implications uses nonrejection as an upper bound or infers coverage from a finite determinant. Their conjunction therefore retains the separate hypotheses and conclusions exactly as stated. $\square$

The central object is now more than a fitted operator. It includes an admissible domain with a replayable witness, an explicit approximation class, and an evidence rule specifying which observations could contradict its predictions. Geometry discovery proposes a representation. Verification checks its algebra. Approximation theory accounts for information lost by a chosen finite description. Sequential tests expose conditional discrepancies in observed signals.

Those roles are related but not interchangeable. A failed search means that this construction did not provide a witness. A failed witness means its submitted identities or signs do not establish the claimed validity. A detected residual means a registered predictive condition is inconsistent with the observations at the stated error budget. These three outcomes should be reported differently.

# 79. Sixth-block checkpoint

The cumulative theory contains 70 propositions. The nine additions close a restricted template-free geometry-discovery sector, give positive polynomial approximation without an exact true-degree assumption, and extend residual evidence to dependent, adaptively observed signals. The continuous example retains its operators and predictions while gaining a different certificate construction.

The reference implementation supplies exact invariant-form discovery, an independent rational quadratic checker, finite positive-approximation examples, and a prospectively defined dependent-path experiment. It does not supply a generic noisy curved-domain optimizer, a complete algorithm for all invariant geometries, or identification of arbitrary hidden dynamics from one trajectory.

The next substantial gaps are joint noisy geometry-and-dynamics estimation with certified uncertainty, informative rather than merely sound sequential upper guarantees, state coverage for controlled experiments, and nonlinear observable discovery with a measured representation cost. The present block does not hide those tasks behind a certificate count. It gives precise constructions and boundaries from which they can be developed.

Production PR-LASM remains at 2.3.0. No new Lean verification, remote execution, real-signal training run, repository publication or license change is claimed. The new proofs are mathematical arguments in this volume. The accompanying calculations verify exact examples, counterexamples and certificate replay.
