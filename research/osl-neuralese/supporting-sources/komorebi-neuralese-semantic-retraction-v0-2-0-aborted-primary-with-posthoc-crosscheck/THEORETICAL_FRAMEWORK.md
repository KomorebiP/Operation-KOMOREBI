# Behavioral Retraction and Bisimulation Framework

**Author:** Komorebi P.  
**Status:** Prospective interpretation for the semantic retraction block  
**Scope:** Definitions and consequences only. No checkpoint result is used as evidence in this document.

## 1. Systems and claim levels

Let \(c\in\mathcal C\) denote an externally supplied episode context, \(X\subseteq\mathbb R^d\) the latent state space, and \(A=\{r,f\}\) the operator alphabet. For a fixed context, an operator \(a\in A\) induces a transition

\[
T_a^c:X\to X.
\]

The semantic system is

\[
D_4=\langle r,f\mid r^4=e,\ f^2=e,\ frf=r^{-1}\rangle.
\]

Its canonical integer labeling is frozen as

\[
4b+k\ \longleftrightarrow\ r^k f^b,
\qquad
k\in\{0,1,2,3\},
\quad
b\in\{0,1\}.
\]

The generators act from the left. Thus \(\tau_a(s)=as\). Temporal words are consumed from left to right. For a word \(w=a_1\cdots a_k\), the first token \(a_1\) acts first, and

\[
T_w^c=T_{a_k}^c\circ\cdots\circ T_{a_1}^c.
\]

The abstract transition follows the same temporal convention:

\[
\tau_w
=
\tau_{a_k}\circ\cdots\circ\tau_{a_1}.
\]

In particular, for concatenated temporal words \(u,v\),

\[
T_{uv}^c=T_v^c\circ T_u^c,
\qquad
\tau_{uv}=\tau_v\circ\tau_u.
\]

The learned decoder output is \(o:X\to Y\), where \(Y\) may be a probability
simplex, centered logit space, or a finite decision set. Let \(\rho\) be a
metric or pseudometric comparing two learned outputs in the same
representation, and let \(q:X\to V\) be the visible argmax decision. When
logits are used explicitly, \(\ell:X\to\mathbb R^{|V|}\).

The intended semantic state set is \(S=D_4\), with \(|S|=8\) and transitions
\(\tau_a:S\to S\). For every context, assume `phi_c` is a bijection from
canonical states to an eight-element visible set \(V\), so
\(|V|=|S|=8\) and \(\phi_c^{-1}\) is single valued. Its task output is context
dependent:

\[
\bar o_c=\phi_c:S\to V.
\]

No canonical probability or centered-logit vector is assumed for an abstract
state. Continuous metrics below therefore compare learned output with learned
output; concrete-to-abstract task error uses the discrete visible output.

Context is held fixed when two latent states are compared. A context dependent section is therefore a fibered semantic representation, while a single section shared across contexts is the stronger claim of a global representation.

Three output notions must remain separate:

1. **Continuous behavior:** probability or centered logit agreement.
2. **Decision behavior:** equality of the decoded class.
3. **Task correctness:** agreement with \(\phi_c(\tau_w s)\), rather than agreement with the unmodified model.

A reset can correct an originally wrong trajectory. It may therefore have low fidelity to that trajectory while improving task correctness. Both quantities must be reported.

## 2. Finite horizon behavioral pseudometric

For a horizon \(H\geq0\), define

\[
d_{H,c}^{\rho}(x,x')
=
\max_{w\in A^{\leq H}}
\rho\!\left(o(T_w^c x),o(T_w^c x')\right).
\]

This definition is taken on the subset of state pairs whose complete
horizon-\(H\) output traces lie in the domain of \(\rho\). For centered-logit
spherical angle, that means every compared centered-logit vector is nonzero.
Proposition 1 and the pseudometric statements below apply on such a
trace-domain-closed subset. Outside it, the empirical probe records the
undefined case and uses its separate fail-closed score; it does not enlarge
the mathematical domain of the angular pseudometric.

This is task relative because it ignores latent differences that no allowed suffix exposes under the selected output metric. It is a pseudometric, not necessarily a metric, because distinct latent states can have identical finite horizon behavior.

Useful choices include:

- total variation distance between decoded probability vectors
- spherical angle between nonzero normalized centered-logit rays
- the discrete metric between argmax decisions

Pulling spherical angle back to raw centered logits is only a pseudometric:
distinct positive scalar multiples have zero distance, and the zero-centered
ray is outside its domain. A fail-closed gate may assign an operational worst
score to that undefined case, but that score is not a metric extension.

The maximum gives a finite horizon certificate. Means, medians, and upper quantiles are useful diagnostics, but they do not replace the maximum in a universal statement. All operator words should be retained. Collapsing words to unique abstract group elements would erase the path dependence the experiment is intended to detect.

### Proposition 1: recursion, monotonicity, and quotient refinement

For fixed \(c\) and \(\rho\),

\[
d_{H+1,c}(x,x')
=
\max\left\{
\rho(o(x),o(x')),
\max_{a\in A}d_{H,c}(T_a^c x,T_a^c x')
\right\}.
\]

Consequently, \(d_{H,c}\) is a pseudometric and \(d_{H,c}\leq d_{H+1,c}\). The equivalence relation

\[
x\equiv_{H,c}x'\quad\Longleftrightarrow\quad d_{H,c}(x,x')=0
\]

can only refine as \(H\) grows. Thus an apparent eight class quotient at short horizon need not remain eight class at greater depth.

*Proof sketch.* The recursion partitions words into the empty word and words beginning with each generator. Symmetry and nonnegativity follow from \(\rho\). Apply the triangle inequality word by word and then take the maximum. Horizon monotonicity follows from \(A^{\leq H}\subseteq A^{\leq H+1}\).

Exact tested-bank trace equivalence requires the bound for every tested pair.
A statement such as “at least \(1-\eta\) of pairs have zero discrete trace
discrepancy” is instead **high-coverage empirical trace agreement** with an
explicit failure rate \(\eta\). Likewise, a p95 continuous bound is a
quantile statement, not a maximum certificate. Neither aggregate statement
alone defines an equivalence relation on the entire tested bank.

## 3. Semantic sections and retractions

A semantic projection and section are maps

\[
\pi_c:X\to S,
\qquad
\iota_c:S\to X,
\qquad
\pi_c\circ\iota_c=\operatorname{id}_S.
\]

Their induced retraction is

\[
R_c=\iota_c\circ\pi_c.
\]

For the learned-anchor instantiation, anchors are indexed by visible labels,
so \(\iota_c(s)=b_{\phi_c(s)}\). A decoder selector has
\(\pi_c(x)=\phi_c^{-1}(q(x))\); a geometric selector uses the same visible-to-
canonical conversion after selecting an anchor or prototype index. This typed
conversion is essential whenever `phi_c` is nontrivial.

It is automatically idempotent, \(R_c^2=R_c\). The fibers of \(\pi_c\) can be curved, disconnected, or path indexed. Nothing in this definition requires an additive null subspace.

Let \(\delta\) be the zero-one metric on visible labels. For a reachable latent
state \(x\), with \(s=\pi_c(x)\), define:

\[
\begin{aligned}
F_{H,c}^{\rho}(x)
&=d_{H,c}^{\rho}(x,R_cx),\\
E_{H,c}^{\rm task}(x)
&=\max_{|w|\leq H}
\delta\!\left(q(T_w^c x),\phi_c(\tau_w s)\right),\\
C_{H,c}^{\rm task}(s)
&=\max_{|w|\leq H}
\delta\!\left(q(T_w^c\iota_c(s)),\phi_c(\tau_w s)\right).
\end{aligned}
\]

Here \(F^\rho\) is learned-output reset fidelity, \(E^{\rm task}\) is
the original trajectory's discrete semantic realization error, and
\(C^{\rm task}\) is discrete canonical prototype adequacy. The notation
\(F^\delta\) below means the same fidelity definition with `o=q` and the
visible-label metric \(\delta\).

### Proposition 2: the canonical triangle

For \(s=\pi_c(x)\), the triangle applies to discrete reset fidelity
\(F_{H,c}^{\delta}\):

\[
F_{H,c}^{\delta}(x)
\leq E_{H,c}^{\rm task}(x)+C_{H,c}^{\rm task}(s)
\]

and

\[
E_{H,c}^{\rm task}(x)
\leq F_{H,c}^{\delta}(x)+C_{H,c}^{\rm task}(s).
\]

*Proof.* For every suffix, insert the ideal visible label
\(\phi_c(\tau_ws)\), apply the triangle inequality for \(\delta\), and
maximize. This proposition never compares a probability or centered-logit
vector with an integer label.

This separates two failure modes. A prototype can fail because it is a poor realization of the abstract state, or because the path state contains additional future relevant information that the prototype removes.

### Proposition 3: prototype radius controls fiber diameter

Suppose every evaluated \(x\) satisfies

\[
d_{H,c}(x,\iota_c\pi_c(x))\leq\epsilon.
\]

Then any two evaluated states in the same semantic fiber satisfy

\[
\pi_c(x)=\pi_c(x')
\quad\Longrightarrow\quad
d_{H,c}(x,x')\leq2\epsilon.
\]

Conversely, if a prototype belongs to a fiber whose diameter is at most \(\epsilon\), its radius is at most \(\epsilon\).

If the radius premise holds for every state in the stated domain, this gives a
direct empirical route to an approximate nonlinear quotient. A quantile or
coverage-rate version supports only a correspondingly qualified
high-coverage candidate. Neither form assumes that fibers are linear.

## 4. Finite horizon trace equivalence and approximate bisimulation

Define the discrete concrete-to-abstract task trace discrepancy

\[
e_{H,c}(x,s)
=
\max_{w\in A^{\leq H}}
\delta\!\left(q(T_w^c x),\phi_c(\tau_ws)\right).
\]

It obeys the exact recursion

\[
e_{H+1,c}(x,s)
=
\max\left\{
\delta(q(x),\phi_c(s)),
\max_{a\in A}e_{H,c}(T_a^cx,\tau_as)
\right\}.
\]

The relation

\[
\mathcal B_{H,c}(\epsilon)
=
\{(x,s):e_{H,c}(x,s)\leq\epsilon\}
\]

is a finite horizon action synchronized **trace simulation** relation. If it has two way coverage, it supports finite horizon trace equivalence. Trace agreement alone is not called approximate bisimulation here.

Because \(\delta\) is zero-one, any pointwise threshold
\(0\leq\epsilon<1\) requires exact decision agreement for every related pair;
\(\epsilon\geq1\) is vacuous. A 99-percent pass rate is therefore reported as
high-coverage empirical agreement, not as an “approximately correct” instance
of this pointwise relation.

Reserve **finite horizon approximate bisimulation** for an explicit horizon stratified relation family

\[
\mathcal R_{0,c},\mathcal R_{1,c},\ldots,\mathcal R_{H,c}
\subseteq X\times S
\]

that satisfies all three conditions below:

1. **Observation condition.** For every \((x,s)\in\mathcal R_{h,c}\),

   \[
   \delta(q(x),\phi_c(s))\leq\epsilon.
   \]

2. **Successor condition.** For every \(h\geq1\), every \((x,s)\in\mathcal R_{h,c}\), and both generators \(a\in\{r,f\}\),

   \[
   (T_a^c x,\tau_a s)\in\mathcal R_{h-1,c}.
   \]

3. **Two way coverage.** Every tested concrete state is paired with at least one semantic state, and every semantic state has at least one tested concrete representative at the claimed horizon.

For deterministic synchronized actions, the exact family defined from the
pointwise bounds \(e_{h,c}\leq\epsilon\) satisfies the successor implication
algebraically. An empirical approximate bisimulation claim must nevertheless
verify the generator-level successor pairs and two-way coverage explicitly,
rather than infer them from aggregate trace statistics. A continuous
concrete-to-abstract version would additionally require a prespecified
same-type probability or centered-logit representative for every abstract
state; this framework and probe do not invent one after outcomes are seen.
These relations permit large Euclidean separation and nonzero latent loop
angle whenever future decisions remain close.

An empirical claim should specify all of:

- the output metric
- the context population
- the word bank and horizon
- whether the bound is a maximum or a quantile
- whether coverage is one way or two way
- whether the section was fixed before evaluation

### Proposition 4: exact retracted dynamics implement the abstract action

Assume

\[
\pi_c(T_a^c\iota_c(s))=\tau_a(s)
\]

for every \(a,c,s\). Also assume canonical output consistency,

\[
q(\iota_c(s))=\phi_c(s)
\]

for every \(c,s\). Define the reset-after-every-step dynamics by

\[
\widehat T_a^c=R_c\circ T_a^c.
\]

For \(w=a_1\cdots a_k\), define

\[
\widehat T_w^c
=
\widehat T_{a_k}^c\circ\cdots\circ\widehat T_{a_1}^c,
\qquad
\widehat T_{uv}^c=\widehat T_v^c\circ\widehat T_u^c.
\]

Then for every word \(w\),

\[
\widehat T_w^c\iota_c(s)=\iota_c(\tau_ws).
\]

Consequently,

\[
q(\widehat T_w^c\iota_c(s))=\phi_c(\tau_ws).
\]

*Proof.* Induction on word length, using \(R_cx=\iota_c\pi_cx\).

This proposition identifies the cleanest route to an error-correcting operator
language. Exact raw latent closure is unnecessary if projection followed by
retraction closes the semantic dynamics, the section decodes consistently,
and the semantic selector is available online. Empirically calling a map an
autonomous retraction therefore requires exhaustive section validity
\(\pi_c\iota_c=\operatorname{id}\), reset idempotence, and both-generator
one-step commutation, not suffix accuracy alone.

## 5. Sufficiency is not deployability

There are four increasingly strong claims.

1. **Oracle sufficiency.** A reset using the ground truth semantic state preserves or improves future task behavior.
2. **Held-out fitted sufficiency.** A section estimated without the evaluation contexts or paths still works.
3. **Self deployability.** A selector computed from the model's current state chooses the correct prototype reliably enough for reset.
4. **Online stability.** Repeated self selected resets remain accurate over long compositions and alternative presentations of the same semantic element.

Oracle success establishes a possible semantic bottleneck. It does not establish that the frozen model possesses a usable internal mechanism for selecting that bottleneck. Self reset success is therefore the decisive engineering gate.

### Proposition 5: decision preservation from logit margin

Let \(\ell(x)\in\mathbb R^{|V|}\) be the logits at a suffix endpoint, and suppose class \(y\) has margin

\[
m=\ell_y(x)-\max_{j\ne y}\ell_j(x)>0.
\]

If

\[
\|\ell(x')-\ell(x)\|_\infty<m/2,
\]

then \(x'\) has the same argmax class.

*Proof.* Each competing logit gap can shrink by at most twice the infinity norm perturbation.

This explains how substantial continuous or angular drift can coexist with correct decisions. A decision quotient is weaker than an equality sensitive logit quotient, but it can still be computationally useful.

If the conditional probability of a wrong self selection at reset \(t\) is at most \(p_t\), the probability of at least one wrong selection in \(K\) resets is at most \(\sum_{t=1}^K p_t\). No independence assumption is required. One shot selector accuracy can therefore be inadequate for deep recurrent deployment.

## 6. What full observability does and does not rule out

For linear transitions, write \(T_a^c(x)=A_a^c x\). Consistently with the
frozen temporal convention, for \(w=a_1\cdots a_k\) define
\(A_w^c=A_{a_k}^c\cdots A_{a_1}^c\), with the empty-word matrix equal to the
identity. For centered linear logits, write the decoder matrix as
\(C_{\rm dec}\), let \(P\) remove the constant logit direction, and form the
horizon \(H\) observability stack

\[
\mathcal O_{H,c}
=
\begin{bmatrix}
P C_{\rm dec} A_w^c
\end{bmatrix}_{w\in A^{\leq H}}.
\]

### Proposition 6: observability obstruction

If \(\operatorname{rank}(\mathcal O_{H,c})=d\), then equality of centered logits for all suffixes through horizon \(H\) implies \(x=x'\). Consequently, any exact retraction that preserves all centered logits through that horizon must be the identity on its domain.

*Proof.* Equality implies \(\mathcal O_{H,c}(x-x')=0\). Full column rank gives \(x-x'=0\).

This separates every distinct pair in \(X\), including every distinct pair in any restricted reachable subset. It therefore rules out a nonidentity exact continuous output retraction at that context and horizon whether the section itself is linear or nonlinear. Nonlinear geometry of the section alone cannot evade the injectivity of the same linear observability stack.

It does **not** rule out:

- a decision relative quotient based on argmax behavior
- an approximate continuous quotient
- a context indexed approximate or decision relative section
- a system whose transitions or decoder are genuinely nonlinear and are not represented by this linear observability stack
- an error correcting reset that changes logits while improving correctness

The distinction is central. Full short horizon observability and a useful finite semantic controller can coexist only at a weaker decision relative, approximate, or error correcting claim level. It cannot coexist with an exact equality sensitive collapse of distinct states under the stated linear system.

## 7. Identity-word holonomy and relation defect

Let \(\lambda\) be a word representing the identity in the semantic system, so \(\tau_\lambda=\operatorname{id}_S\). Define latent holonomy by the displacement from \(x\) to \(T_\lambda^cx\), and task holonomy by

\[
h_{H,c}(x,\lambda)
=
d_{H,c}(x,T_\lambda^cx).
\]

Large latent angle does not by itself imply large task holonomy. Conversely,
preserved terminal labels do not imply that the latent identity-word action
closes.

### Proposition 7: retraction can remove ambient holonomy

Under the assumptions of Proposition 4, any semantic identity word satisfies

\[
\widehat T_\lambda^c\iota_c(s)=\iota_c(s)
\]

even when

\[
T_\lambda^c\iota_c(s)\ne\iota_c(s).
\]

Thus nonzero ambient holonomy—an identity-word relation defect—is logically
compatible with an exact retracted semantic action.

This yields a disciplined meaning of “essential holonomy.” A successful
minimal joint D4 repair that preserves behavior shows that the measured
holonomy was dispensable on the evaluation domain. Failure of one repair does
not prove that holonomy is essential. It may mean that the repair moved states
off the learned manifold or altered unrelated operator features. Strong
evidence for essential holonomy requires a controlled repair frontier across
several joint projections, matched short-horizon distortion, and failure of
semantic-retraction alternatives.

## 8. Empirical gates and their interpretations

Thresholds should be fixed before inspecting results. The exact compiled control defines the numerical floor, while shuffled semantic and norm matched random resets define negative controls. With only a few training seeds, every seed and its range should be reported rather than treating trajectories as independent population replicates.

| Gate | Required comparison | What a pass supports |
|---|---|---|
| Control validity | Identity and compiled controls pass, shuffled and matched random resets do not mimic the effect | The assay distinguishes semantic reset from generic rescaling or denoising |
| Oracle sufficiency | Ground truth semantic reset is noninferior or improves task correctness across held-out paths and suffixes | Semantic state is sufficient when externally supplied |
| Held-out fitted section | Same class prototypes built on disjoint contexts and paths pass | The result is not path memorization and supports a reusable semantic fiber |
| Learned-output fidelity | Learned-to-learned probability or centered-logit discrepancy remains below its bound | Reset fidelity or native trace agreement in that learned representation; not concrete-to-abstract continuous equivalence |
| Decision fidelity | Every suffix decision is stable, or a stated fraction is stable | A coarse decision quotient only for the universal bound; otherwise high-coverage empirical agreement |
| Self deployability | Model selected resets approach oracle resets and outperform shuffled controls | The frozen system can address the semantic bottleneck online |
| Bisimulation successor | Both generator successors satisfy the horizon stratified relation and coverage is two way | Finite horizon approximate bisimulation when combined with the selected observation bound |
| Repeated closure | Periodic or every step resets remain stable at depth and across multiple word presentations | Approximate retracted dynamics, rather than a one time projection effect |
| Joint relation repair | A jointly constrained D4 operator repair changes long depth outcomes without damaging matched short horizon behavior | Counterfactual evidence that the chosen joint operator intervention changes long-depth behavior; isolating a causal role for the relation defect requires a matched repair frontier |

The main outcome patterns are:

| Oracle reset | Self reset | Joint repair | Best supported interpretation |
|---|---|---|---|
| Pass | Pass | Pass | Online-addressable nonlinear semantics; if repeated closure also passes, a deployable retraction, with ambient holonomy dispensable under the tested repair |
| Pass | Pass | Fail | Online-addressable semantic controller; deployability still requires repeated closure, and the chosen relation-closing repair disrupts the learned implementation |
| Pass | Fail | Either | Semantic sufficiency exists, but selector or online addressability is the bottleneck |
| Fail | N/A | Pass | For the tested sections, the joint repair is more useful than semantic reset; ambient-state usefulness requires broader section controls or a lower bound |
| Fail | N/A | Fail | The tested sections and repair both fail; path-dependent ambient computation remains a candidate only with broader section controls or a lower bound |

Additional diagnostic outcomes matter:

- If random resets match oracle resets, the benefit is not specifically semantic.
- If a one time reset passes but repeated resets fail, there is local sufficiency without transition closure.
- If decisions pass universally while continuous outputs fail, claim only a
  decision-tolerant quotient; if the decision gate is fractional, claim only
  the stated high-coverage agreement.
- If global prototypes fail but context-aligned prototypes pass, report evidence
  consistent with a context-indexed or fibered candidate representation; this
  does not exclude another global section.
- If one prototype family fails, this does not refute all nonlinear sections. A negative conclusion requires several independently constructed sections or an optimization based lower bound.

## 9. Safe interpretation prerequisites

These are prerequisite patterns, not one linear hierarchy. In particular, a
repaired controller can work even when native trace agreement fails, and an
oracle repair can work without autonomous addressability.

1. **Candidate semantic canonicalization:** oracle reset beats semantic shuffle and random controls.
2. **Approximate nonlinear quotient of native dynamics:** every state in the
   claimed domain satisfies the held-out behavioral-diameter bound; a
   fractional pass is labeled high-coverage instead.
3. **Approximate bisimulation:** the chosen observation bound holds and the explicit horizon stratified successor condition is verified for both generators, with two way semantic coverage.
4. **Deployable retraction:** the model passes exhaustive section validity,
   idempotence, both-generator commutation, and can repeatedly apply the
   canonicalization without oracle labels.
5. **Relation-defect diagnosis:** a controlled matched repair frontier can
   isolate whether dispensable holonomy contributes causally; a single joint
   repair supplies counterfactual evidence but does not isolate the defect.

No finite experiment establishes a universal quotient or mathematically
essential holonomy. It can establish a frozen checkpoint, distribution,
horizon, and intervention-relative result. That narrower statement is still
decisive for choosing the next architecture.
