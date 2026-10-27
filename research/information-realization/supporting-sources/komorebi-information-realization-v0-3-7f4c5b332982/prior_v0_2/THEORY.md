# Information Realization and Obstruction
## A finite, measurable foundation · v0.2.0

**Operation Komorebi / Realization Calculus**  
**Date:** 15 October 2026  
**Scope:** finite deterministic realizations, exact rational probability models, finite Markov channels, and a finite-field specialization.  
**Status:** proofs supplied in this document, executable finite checks supplied separately. No Lean proof was compiled. Neither mathematical novelty nor universal unification is claimed.

## 1. Model and conventions

Let \(X\) be a nonempty finite set. A task is \(F:X\to Y\), an observation or realization is \(r:X\to R\), and an optional prior is \(P\). All codomains can be replaced by their images. Structural recovery means recovery on **every state of \(X\)**. Probabilistic recovery means recovery almost surely under the declared prior. These are not equivalent without a support condition.

Write \(R=r(X)\) and \(Y_F=F(X)\) when the argument is a random state. To avoid notation overload, formulas such as \(H(F\mid R)\) refer to the corresponding random variables.

Define

\[
K_R(F)=\max_{z\in r(X)}|F(r^{-1}(z))|,
\qquad B_R(F)=\lceil\log_2 K_R(F)\rceil,
\]

\[
E_R(F)=1-\sum_z\max_yP(R=z,F=y),
\qquad H_R(F)=H(F\mid R).
\]

The integer \(K\) is an alphabet size, \(B\) is a fixed-width bit budget, \(E\) is a probability, and \(H\) is entropy in bits. These are not interchangeable units and should not be added into a single score without a separately justified objective.

An observation \(r_1\) is at least as informative as \(r_2\) when \(r_2=h\circ r_1\). Equivalently, every fiber of \(r_1\) lies in a fiber of \(r_2\). This structural order is stronger than comparing a few numerical quantities for one chosen task.

## 2. Factorization and its obstruction

**Theorem 1.** The following are equivalent:

\[
\exists g:r(X)\to Y,\quad F=g\circ r;
\qquad
\forall x,x',\ r(x)=r(x')\Rightarrow F(x)=F(x');
\qquad K_R(F)=1.
\]

**Proof.** A factorization preserves equality of observations. Conversely, if every nonempty fiber has one task value, define \(g(z)\) to be that value. This definition is independent of the chosen state in the fiber. Since \(X\) is nonempty, every maximum is over a nonempty collection. ∎

An obstruction certificate is a pair

\[
r(x)=r(x'),\qquad F(x)\ne F(x').
\]

This certifies impossibility for every decoder using only the observation, not merely failure of one proposed decoder.

Under a prior, \(H_R(F)=0\) and \(E_R(F)=0\) are each equivalent to factorization **on the positive-probability support**. They become equivalent to the pointwise theorem when the prior has full support. A null-probability state can retain a structural obstruction without contributing any expected loss.

## 3. Exact and approximate repair with declared encoder access

An additional message \(c:X\to\{1,\ldots,m\}\) is delivered to a decoder that also sees \(r(x)\). The encoder in this section may inspect the state, or at least the pair \((r(x),F(x))\). The decoder does not receive the state.

**Theorem 2. Minimal exact repair.** The least message alphabet permitting pointwise exact recovery is \(K_R(F)\). Hence the least fixed-width binary budget is \(B_R(F)\).

**Proof.** Inside a fixed observation fiber, two distinct task values cannot share a message if both must be recovered. Thus at least \(|F(r^{-1}(z))|\) messages are necessary. For sufficiency, enumerate the distinct task values separately inside each fiber and reuse the same message labels across different fibers. The decoder sees the fiber label and therefore knows which enumeration applies. ∎

This is an information-supply theorem. It does not generate the missing message from the inadequate observation. Nor does it equate the number of transmitted bits with the cost of measuring them.

### The entire optimal success curve

For each observed value \(z\), sort the joint masses \(P(R=z,F=y)\) in decreasing order:

\[
a_{z,1}\ge a_{z,2}\ge\cdots,
\]

padding with zeros beyond the available task values.

**Theorem 3. State-aware repair budget.** The largest achievable exact-answer probability with an \(m\)-symbol supplemental message is

\[
\boxed{A_m^*(R,F)=\sum_z\sum_{j=1}^{m}a_{z,j}.}
\]

The least achievable error is \(1-A_m^*\). For a budget of \(b\) fixed-width bits, use \(m=2^b\).

**Proof of the upper bound.** For each fixed observation \(z\), a deterministic decoder with \(m\) messages can output at most \(m\) distinct task values. All correctly decoded mass lies in those task-value classes. Their total mass is bounded by the sum of the \(m\) largest classes. Summing over observations gives the bound.

**Proof of attainment.** Assign distinct message labels to the \(m\) largest task-value classes within each observation fiber. Map remaining classes to any existing label. Decode each label to its selected task value. The construction recovers exactly the selected mass. Randomization cannot improve the optimum: a randomized finite encoder/decoder is an average over deterministic choices after fixing its randomness, and an average cannot exceed the best deterministic value. ∎

This formula supplies an operational tradeoff, not just a statement about the endpoint of exact recovery. It is standard finite decision/coding reasoning, newly made explicit in this package rather than claimed as an original discovery.

### Restricted access changes the problem

Suppose the encoder sees only \(u(x)\), so \(c=h\circ u\).

If \((r,u)\) itself fails to determine \(F\), **no message alphabet can repair the task under that access restriction**. The obstruction is a pair with the same \(r\) and \(u\), but different \(F\).

Otherwise, form a graph on \(u(X)\). Join two distinct encoder values when there exist states with those encoder values, the same observation, and different task answers. A valid code is exactly a proper coloring of this graph. Its minimum alphabet is the graph's chromatic number.

**Proof.** Adjacent encoder values must have different messages, or their witnessing states remain indistinguishable to the decoder. Conversely, a proper coloring ensures that equal observation and equal message cannot conceal different task values. The factorization theorem then supplies a decoder. The preliminary no-repair obstruction rules out loops. ∎

For \(u=\mathrm{id}_X\), this recovers Theorem 2. For \(u=F\), different observation fibers can impose incompatible demands on a single global labeling of task values. Example 6 exhibits \(K=2\) but minimum restricted alphabet 3. This is the classical confusability-graph boundary of zero-error coding with side information [4].

## 4. Information loss under deterministic transfer

Let \(S=s(R)\). Then

\[
K_R(F)\le K_S(F)\le K_R(F)K_S(R),
\]

\[
B_R(F)\le B_S(F)\le B_R(F)+B_S(R),
\]

\[
H(F\mid R)\le H(F\mid S)\le H(F\mid R)+H(R\mid S),
\]

\[
E_R(F)\le E_S(F)\le\min\{1,E_R(F)+E_S(R)\}.
\]

**Cardinality proof.** Every fine fiber lies in a coarse fiber. A coarse fiber contains at most \(K_S(R)\) fine fibers, each contributing at most \(K_R(F)\) distinct task answers. The number of answers in their union lies between the stated bounds. Integer bit bounds follow because \(K_R(F)K_S(R)\le2^{B_R(F)+B_S(R)}\).

**Entropy proof.** Since \(S\) is determined by \(R\),

\[
H(F\mid S)-H(F\mid R)=I(F;R\mid S)\in[0,H(R\mid S)].
\]

**Error proof.** A decoder using \(S\) can be simulated from \(R\). For the upper bound, decode \(R\) from \(S\), then decode \(F\) from the guessed \(R\). Failure requires either a mistaken intermediate value or an error in the original task decoder. The union bound gives the result. These entropy and decision-theoretic mechanisms belong to established information theory [2]. ∎

The bounds can be loose because task-value classes in different fine fibers can overlap. They are safe budgets, not assertions that information losses add exactly.

## 5. Exact entropy comparison without floating-point tolerances

Let integer weights \(w_x\ge0\) have total \(W>0\). Write

\[
W_z=\sum_{x:r(x)=z}w_x,\qquad
W_{z,y}=\sum_{x:r(x)=z,F(x)=y}w_x.
\]

Expanding conditional entropy gives

\[
WH(F\mid R)
=\sum_zW_z\log_2W_z-\sum_{z,y}W_{z,y}\log_2W_{z,y},
\]

where zero-weight terms are omitted. Consequently

\[
\boxed{2^{WH(F\mid R)}
=\frac{\prod_{z:W_z>0}W_z^{W_z}}
       {\prod_{z,y:W_{z,y}>0}W_{z,y}^{W_{z,y}}}.}
\]

The right side is an exact rational number \(C_R(F)\). For models on the same weighted state space,

\[
H_R\le H_S\iff C_R\le C_S,
\quad
H_S\le H_R+H_S(R)\iff C_S\le C_R C_S(R).
\]

Thus every entropy inequality in the exhaustive and Markov suites is checked using integer arithmetic and rational comparison. Displayed entropy decimals are approximations, with independent 60-digit Decimal checks on a subset of the channel grid. The certificate does not purport to make an irrational entropy itself rational.

The integer products can grow rapidly. The code therefore has an explicit total-weight resource guard. It is a finite verification technique, not an efficient general-purpose entropy algorithm for arbitrary massive denominators.

## 6. Projector residuals with an appropriate loss geometry

For a real square-integrable task \(Z\), define

\[
P_RZ=\mathbb E[Z\mid R],\qquad M_R(Z)=\|Z-P_RZ\|_2^2.
\]

Conditional expectation is the orthogonal projection onto observation-measurable functions [1]. When \(S=s(R)\),

\[
\boxed{M_S(Z)-M_R(Z)=\|P_RZ-P_SZ\|_2^2.}
\]

**Proof.** Decompose \(Z-P_SZ=(Z-P_RZ)+(P_RZ-P_SZ)\). The two terms are orthogonal because the first is orthogonal to every \(R\)-measurable function and the second is \(R\)-measurable. Apply Pythagoras. ∎

### Categorical tasks should not inherit an arbitrary numerical metric

Encoding labels as \(0,1\) gives a different scalar MSE than encoding them as \(0,10\), even though the available distinctions are unchanged. For an unordered finite task alphabet, use one-hot task vectors \(e_F\) and define

\[
V_R(F)=\mathbb E\|e_F-\mathbb E[e_F\mid R]\|^2
      =1-\sum_zP(R=z)\sum_yP(F=y\mid R=z)^2.
\]

This is the Bayes risk of the multiclass quadratic or Brier loss, using the **unhalved sum over all class coordinates** [5]. It is unchanged by a permutation of task labels. It is still a chosen loss geometry, not a unique universal information measure.

The same projection theorem yields

\[
\boxed{V_S(F)-V_R(F)
=\mathbb E\|P(F=\cdot\mid R)-P(F=\cdot\mid S)\|^2.}
\]

Moreover,

\[
\boxed{E_R(F)\le V_R(F)\le2E_R(F)-E_R(F)^2,}
\]

\[
\boxed{-\log_2(1-V_R(F))\le H(F\mid R)\le\log_2 K_R(F).}
\]

**Risk-bound proof.** In one observation cell let \(p_{\max}=1-e\). Since \(\sum p_y^2\le p_{\max}\), its quadratic residual is at least \(e\). Since \(\sum p_y^2\ge p_{\max}^2\), it is at most \(2e-e^2\). Average and use \(\mathbb E[e^2]\ge(\mathbb E e)^2\).

**Entropy-bound proof.** In a cell, Jensen's inequality gives
\(H(p)\ge-\log_2\sum_y p_y^2\). A second application of Jensen over observation cells gives the lower bound. Each fiber has at most \(K_R(F)\) supported task values, giving the upper bound. ∎

The test suite independently computes \(V\) as a sum of one-hot scalar MSEs, compares it to the posterior formula, and checks the risk and entropy bounds. The entropy lower bound is checked exactly as

\[
C_R(F)\ge (1/(1-V_R(F)))^W.
\]

## 7. Extension to stochastic transfers

Suppose \(F\to R\to S\) is a finite Markov chain. Here \(S\) is generated from \(R\) by a stochastic channel, not necessarily a deterministic function. For a numerical encoding \(Z\) of the task,

\[
\mathbb E[Z\mid R,S]=\mathbb E[Z\mid R].
\]

This is enough to prove

\[
M_S(Z)-M_R(Z)=\mathbb E[(P_RZ-P_SZ)^2],
\]

and the analogous categorical identity for \(V\).

**Proof.** In the residual decomposition from Section 6, condition the cross term on \((R,S)\). Its factor \(Z-P_RZ\) has conditional mean zero by the Markov condition, so the cross term vanishes. ∎

The \(R\)- and \(S\)-measurable subspaces are not generally nested. The proof is conditional independence, **not** an assertion that the deterministic nested-projector algebra holds for arbitrary noisy observations.

The entropy and Bayes-error transfer inequalities also hold for this Markov chain. The lower bounds use data processing [2]. The upper error bound uses the same decoder composition and union bound as before. The upper entropy bound follows by introducing \(R\) into the joint conditional entropy.

The Markov condition matters. For independent fair bits \(A,B\), set \(R=A\), \(S=F=B\). Then \(M_S-M_R=-1/4\), whereas the squared distance between conditional means is \(+1/4\). The unrestricted identity is false.

## 8. The linear obstruction has an exact information valuation

Let \(V=\mathbb F_q^n\), with linear observation \(R:V\to U\) and linear task \(F:V\to W\). Let

\[
\mathcal O_R(F)=F(\ker R),\qquad d=\dim\mathcal O_R(F).
\]

Then

\[
\boxed{d=\operatorname{rank}\begin{bmatrix}R\\F\end{bmatrix}
-\operatorname{rank}R,\qquad K_R(F)=q^d.}
\]

**Proof.** A nonempty observation fiber is \(x_0+\ker R\). Its task image is \(F(x_0)+F(\ker R)\), a translate of a \(d\)-dimensional space. It therefore has \(q^d\) elements. For the rank formula, apply rank-nullity to \(F\) restricted to \(\ker R\):

\[
d=\dim\ker R-\dim(\ker R\cap\ker F).
\]

Replace each nullity by ambient dimension minus the appropriate rank. ∎

For a uniform source on \(V\), every conditional task distribution is uniform on its affine image. Thus

\[
\boxed{
B_R(F)=\lceil d\log_2q\rceil,
\quad H(F\mid R)=d\log_2q,
\quad E_R(F)=V_R(F)=1-q^{-d}.}
\]

A \(d\)-coordinate linear supplemental observation suffices. To construct one, extend the row space of \(R\) by independent rows of \(F\), stopping when the full row space of \([R;F]\) is spanned. The added rows form \(C\), and \(F\) is a linear function of \((R,C)\). No nonlinear supplemental encoder can use fewer than \(q^d\) message symbols by Theorem 2.

This is the explicit bridge from a linear obstruction space to worst-case code cost, Shannon uncertainty, Bayes error, and projector residual energy. Its proof is finite-field linear algebra plus the finite information theorems. The implementation supports prime fields only. The theorem also applies to finite extension fields, whose arithmetic is not implemented in this release.

## 9. Predictive refinement

Let \(r_0\) be an initial observation and let \(T_1,\ldots,T_k:X\to X\) be admissible actions. States are operationally equivalent when all observation sequences under all finite action words agree.

Start with the partition induced by \(r_0\). Given partition label \(p_t\), refine by

\[
p_{t+1}(x)=\operatorname{class}\bigl(p_t(x),p_t(T_1x),\ldots,p_t(T_kx)\bigr).
\]

Every strict step increases the number of classes, so there are at most \(|X|-|p_0(X)|\) strict steps.

**Correctness proof.** Induction shows that \(p_t\) retains exactly the distinctions revealed by action words of length at most \(t\). At a fixed point, equivalent states have equivalent successors under every action, so agreement extends to all finite words. Any other stable refinement preserving \(r_0\) must distinguish every pair distinguished by one of these words. The fixed point is therefore the coarsest stable adequate refinement. ∎

The tests compare this algorithm to independent reachability in the product state space \(X\times X\), and, for up to four states, to exhaustive minimality among all candidate partitions. This is the finite observational-equivalence route related to automata and observability, not a claim to have invented state minimization. For linear systems the familiar observability matrix gives the corresponding linear reconstruction criterion [3].

## 10. What has and has not been established

The package now has explicit finite recovery, optimal repair, transport, categorical residual, stochastic-channel, and linear-obstruction formulas, together with counterexamples to several invalid extensions. These statements are mathematical consequences of declared hypotheses and can be tested independently of any Komorebi terminology.

They provide a concrete information layer for Realization Calculus. They do not prove a universal calculus of all information, an extension to unrestricted quantum or semantic information, computationally efficient repair under arbitrary access restrictions, or direct integration with the full Komorebi production libraries. They also do not establish novelty relative to the large existing literature on coding, decision theory, sufficiency, and observability.

The strongest next integration target is to export an existing Komorebi packet/transfer construction into the typed interface used here, preserving its task, observation, admissible repair operations, coefficient field, and probability assumptions. An operational code budget must not silently substitute for sensing cost, and an exact inverse must not silently substitute for a stable numerical inverse.

## References

[1] Jim Pitman, *Conditional Expectation*, Statistics 205 lecture notes, University of California, Berkeley, Sections 10.2.3–10.3. Conditional expectation as orthogonal projection and the tower property.

[2] Yury Polyanskiy and Yihong Wu, *Information Theory*, MIT 6.441 lecture notes, Chapter 2, especially the chain rule and data-processing theorem.

[3] Stephen Boyd, *Observability and State Estimation*, EE263 Lecture 19, Stanford University. Linear observability and the nullspace obstruction to state recovery.

[4] Prashant Koulgi, Ertem Tuncel, Shankar L. Regunathan, and Kenneth Rose, “On Zero-Error Source Coding With Decoder Side Information,” *IEEE Transactions on Information Theory* 49(1), 2003. DOI 10.1109/TIT.2002.806154. Confusability graphs and the importance of encoder access.

[5] Tilmann Gneiting and Adrian E. Raftery, “Strictly Proper Scoring Rules, Prediction, and Estimation,” *Journal of the American Statistical Association* 102(477), 359–378, 2007. DOI 10.1198/016214506000001437. Quadratic scoring rules and their associated information geometry.

The sources establish the classical background. The elementary derivations above, the exact examples, and the verification records identify precisely what was developed and checked for this package.
