"""Raw-string manuscript chunk: existing contracts SR-49 through SR-64."""

section('Reliable discrepancy with inexact solves', r'''
The discrepancy rule of the preceding section selects an actual regularized
source. A computed vector need not equal that source, and a displayed residual
need not equal its exact norm. Those two errors require separate allowances.
The normal equation provides the connection without assuming the computation
has already solved the inverse problem.

Throughout this section $A:G\to V$ is bounded between real Hilbert spaces,
$N_A=\ker A$, $S_A=N_A^\perp$, and $\lambda>0$. Write
\[
N_\lambda=A^*A+\lambda I,\qquad
x_\lambda=N_\lambda^{-1}A^*v,\qquad
r_\lambda(x)=N_\lambda x-A^*v .
\]
The inverse is the actual positive-parameter constructor already established.
The vector $r_\lambda(x)$ is the normal-equation residual of the computed
source $x$. Its size measures source correction and image correction on
different scales. A fitting residual $\nn{Ax-v}$ alone does not supply
either correction.
''')

claim(49, 'Normal residual, two correction scales',
      'Real Hilbert spaces; bounded A; lambda>0; actual normal residual.',
      'InexactResidual.correction_identity;InexactResidual.correction_bound;InexactResidual.image_correction_bound;InexactResidual.fitting_residual_difference', r'''
For every computed source $x$,
\[
x-x_\lambda=N_\lambda^{-1}r_\lambda(x),\qquad
\nn{x-x_\lambda}\le\frac{\nn{r_\lambda(x)}}{\lambda},
\qquad
\nn{Ax-Ax_\lambda}\le
\frac{\nn{r_\lambda(x)}}{2\sqrt\lambda}.
\]
Consequently
\[
\left|\nn{Ax-v}-\nn{Ax_\lambda-v}\right|
\le\frac{\nn{r_\lambda(x)}}{2\sqrt\lambda}.
\]
The bounds use the same actual residual and the existing Hilbert norms.
''', r'''
Subtract $N_\lambda x_\lambda=A^*v$ from the definition of the normal
residual and apply the inverse. For $u=N_\lambda^{-1}r$, the energy identity
gives
\[
\nn{Au}^2+\lambda\nn u^2=\ip ru
\le\nn r\,\nn u .
\]
Dropping the first term shows $\nn u\le\nn r/\lambda$, including $u=0$.
To control the image, complete the scalar square:
\[
\nn{Au}^2\le\nn r\,\nn u-\lambda\nn u^2
\le\frac{\nn r^2}{4\lambda}.
\]
Both sides of the desired norm inequality are nonnegative, so taking square
roots gives the image bound. Set $r=r_\lambda(x)$ and use linearity of
$A$. Finally the reverse triangle inequality bounds the difference of the
two fitting norms by $\nn{A(x-x_\lambda)}$.

The distinction matters when $\lambda$ is small. A normal residual sufficient
for a prescribed image tolerance may be insufficient for a prescribed
source tolerance. If source correction must be at most $\kappa$ and image
correction at most $\xi$, a sound pair of conditions is
$\nn{r_\lambda(x)}\le\lambda\kappa$ and
$\nn{r_\lambda(x)}\le2\sqrt\lambda\,\xi$.
These are parameter-dependent requirements, not a uniform inverse bound
as $\lambda$ tends to zero.
''')

claim(50, 'Protected measured discrepancy margins',
      'Same Hilbert setting; nonnegative source/image/evaluation budgets; positive parameter; genuine measurement enclosure.',
      'InexactResidual.measured_band_transfer;InexactDiscrepancy.measured_certificate;InexactToleranceCertificates.protected_window_exists_iff;InexactToleranceCertificates.protected_midpoint', r'''
Suppose $m$ is a measured fitting norm with
\[
|m-\nn{Ax-v}|\le\omega,\quad
\nn{r_\lambda(x)}\le\lambda\kappa,\quad
\nn{r_\lambda(x)}\le2\sqrt\lambda\,\xi .
\]
If
\[
\eta+\omega+\xi\le m\le\tau\eta-\omega-\xi,
\]
then the actual exact source $x_\lambda$ has discrepancy in
$[\eta,\tau\eta]$, and $\nn{x-x_\lambda}\le\kappa$.
A protected scalar window exists exactly when
\[
2(\omega+\xi)\le(\tau-1)\eta .
\]
Its midpoint $(\tau+1)\eta/2$ is then admissible.
''', r'''
SR-49 and the measurement enclosure imply
\[
|m-\nn{Ax_\lambda-v}|
\le |m-\nn{Ax-v}|+
|\nn{Ax-v}-\nn{Ax_\lambda-v}|
\le\omega+\xi .
\]
Subtracting this total allowance from the lower protected inequality gives
$\eta\le\nn{Ax_\lambda-v}$. Adding it to the upper inequality gives
$\nn{Ax_\lambda-v}\le\tau\eta$. The source-correction bound follows
from the other residual condition in SR-49. Hence the computed source is
within $\kappa$ of an actual accepted discrepancy source.

The scalar window is nonempty exactly when its lower endpoint is at most
its upper endpoint. Rearrangement gives the displayed condition. The
proposed midpoint is the mean of the endpoints; direct substitution gives
both inequalities. No property of an approximate solver is hidden in this
scalar calculation: its residual, measurement enclosure and correction
allowance have already been supplied.

For example, let $\eta=1/10$, $\tau=2$, and
$\omega=\xi=1/100$. The total protected margin is $1/50$,
and the interval is $[3/25,9/50]$. Its midpoint is $3/20$.
This allocation proves room for the measurement and image-correction
errors; it does not prove that a particular computed source attains the
interval or that $1/10$ is a true data-noise allowance.
''', ('SR-49',))

claim(51, 'Near-accepted consistency and kernel leakage',
      'Fixed bounded real Hilbert A; actual noise bounds; fixed tau; NearAccepted with source budget tending to zero.',
      'InexactDiscrepancy.NearAccepted;InexactDiscrepancy.near_kernel_leakage;InexactConsistency.near_consistent;InexactConsistency.near_error_norm_limit;InexactConsistency.near_kernel_tendsto_zero', r'''
Call $x$ near accepted with budget $\kappa$ when some exact accepted source
$y$ satisfies $\nn{x-y}\le\kappa$. If
$\nn{Ag-v_i}\le\eta_i$, $\eta_i\to0$, and near-accepted $x_i$ have
$\kappa_i\to0$, then
\[
x_i\longrightarrow P_{S_A}g,\qquad
\nn{x_i-g}\longrightarrow\nn{P_{N_A}g}.
\]
At every index $\nn{P_{N_A}x_i}\le\kappa_i$; therefore the computed true-kernel
component tends to zero. No separate parameter schedule is assumed.
''', r'''
Choose accepted comparison sources $y_i$ from the definition. Exact
accepted consistency gives $y_i\to p=P_{S_A}g$, while
$\nn{x_i-y_i}\le\kappa_i\to0$ gives $x_i-y_i\to0$. Adding the two limits
proves $x_i\to p$. Continuity of the norm gives the source-error limit,
because $p-g=-P_{N_A}g$.

The exact accepted source belongs to $S_A$, including the small-data zero
branch. Orthogonal projection is nonexpansive, so
\[
\nn{P_{N_A}x_i}
=\nn{P_{N_A}(x_i-y_i)}
\le\nn{x_i-y_i}\le\kappa_i .
\]
This pointwise estimate only needs near acceptance, not a truth-noise
premise. Source consistency additionally needs the stated true-noise
allowance tending to zero.

The underlying exact consistency theorem has substantive content even
for a nonclosed range. Accepted sources satisfy norm domination
$\nn{y_i}\le\nn p$ and $\nn{Ay_i-Ap}\to0$. Since
$p\in S_A=\cl\Ran A^*$, approximate $p$ by $A^*w$ and use
\[
\nn{y_i-p}^2
\le2\ip{p}{p-y_i}
\le2\nn{p-A^*w}\nn{p-y_i}
+2\nn w\,\nn{A(p-y_i)} .
\]
The first factor $\nn{p-y_i}$ is bounded by $2\nn p$.
First choose the approximation accurately, then let $i$ tend along the
filter. This proves strong convergence without a bounded inverse.
''', ('SR-49','SR-50'))

claim(52, 'Squared proof-carrying discrepancy certificate',
      'Real Hilbert spaces; positive lambda; nonnegative scalar certificate fields; squared inequalities against actual norms.',
      'InexactToleranceCertificates.squared_enclosure_iff;InexactToleranceCertificates.squared_image_budget;InexactToleranceCertificates.PositiveCertificate;InexactToleranceCertificates.certificate_sound;InexactToleranceCertificates.certificate_consistent', r'''
Suppose a record supplies $\lambda>0$, nonnegative
$\rho,\xi,\kappa,m,\omega$, and
\[
\nn{r_\lambda(x)}^2\le\rho^2,\quad
\rho^2\le(\lambda\kappa)^2,\quad
\rho^2\le4\lambda\xi^2,
\]
\[
\max(0,m-\omega)^2\le\nn{Ax-v}^2\le(m+\omega)^2,
\qquad
\eta+\omega+\xi\le m\le\tau\eta-\omega-\xi .
\]
Then $x$ is near accepted with source budget $\kappa$. Families of such
records give SR-51 when the genuine data allowances and source budgets
tend to zero.
''', r'''
All quantities whose squares are compared are nonnegative. The first
two inequalities therefore give
$\nn{r_\lambda(x)}\le\rho\le\lambda\kappa$.
The third gives $\rho\le2\sqrt\lambda\,\xi$ because
$(2\sqrt\lambda\,\xi)^2=4\lambda\xi^2$.

Put $d=\nn{Ax-v}\ge0$. The squared fitting enclosure is equivalent to
the unsquared enclosure
$\max(0,m-\omega)\le d\le m+\omega$.
Since $d\ge0$, its lower part is equivalent to $m-\omega\le d$.
Together these say $|m-d|\le\omega$. Thus every premise of SR-50 has
been obtained from the supplied record, and its conclusion proves soundness.
Apply SR-51 pointwise for the family statement.

The record does not establish the truth of the data-noise allowance.
It establishes a relation between the computed source, actual normal
residual and actual fitting norm. An implementation may check rational
squared inequalities without numerical square roots, but that requires a
faithful enclosure of these actual quantities. The generic Lean structure
is proof-carrying; a serialized Python record and its parser are separate
implementation evidence.

If the normal residual itself is evaluated approximately as $\widehat r$,
the distinct assumptions
$\nn{r_\lambda(x)-\widehat r}\le\nu$ and
$\nn{\widehat r}\le\widehat\rho$ give the allowance
$\widehat\rho+\nu$. Substituting that sum into both correction tests retains
the evaluation error rather than silently identifying it with zero.
''', ('SR-49','SR-50','SR-51'))

section('Uncertain operators and changing identifiable models', r'''
Data noise, solver error and model error are different inputs. Let $A$ be
the true forward operator and $C$ the available operator, acting between the
same real Hilbert spaces. The premise $\nn{C-A}\le\delta$ is a whole-operator
allowance. A small residual for one source does not establish it.
This section first uses a fixed cap $M$ on a true comparison source.
The next section removes that cap from the acceptance rule by making the
allowance depend on the candidate itself.
''')

claim(53, 'Effective model-noise allowance',
      'Same normed source/target; bounded A,C; whole operator allowance; genuine data allowance and source cap.',
      'OperatorUncertainty.action_error;OperatorUncertainty.effective_data_noise;OperatorUncertainty.fitting_norm_difference;OperatorUncertainty.measured_true_fitting_envelope;OperatorUncertaintyExamples.inflated_noise_sharp', r'''
If $\nn{C-A}\le\delta$, $\nn p\le M$ and $\nn{Ap-v}\le\eta$, then
\[
\nn{Cp-v}\le\epsilon:=\eta+\delta M.
\]
For every candidate $x$,
\[
|\nn{Ax-v}-\nn{Cx-v}|\le\delta\nn x.
\]
If $|m-\nn{Cx-v}|\le\omega$, then
$|m-\nn{Ax-v}|\le\omega+\delta\nn x$.
The effective-noise allowance is sharp in scalar examples.
''', r'''
The definition of operator norm gives
$\nn{Cp-Ap}\le\delta\nn p$. Because a norm bound implies
$\delta\ge0$, the source cap gives
\[
\nn{Cp-v}\le\nn{Cp-Ap}+\nn{Ap-v}
\le\delta M+\eta .
\]
For the fitting-norm comparison, apply the reverse triangle inequality
to $Ax-v$ and $Cx-v$, whose difference is $(A-C)x$. Combining this
with the measurement enclosure gives the last claim.

To see the possible equality, take real scalar maps
$A=1$, $C=1+\delta$, $p=M$ and $v=M-\eta$, with
$\eta,\delta,M\ge0$. Then
$Cp-v=\delta M+\eta\ge0$, so its absolute value is exactly $\epsilon$.
The source-size factor cannot generally be omitted: for fixed
$\delta>0$, the action difference $\delta|p|$ grows without bound as
$|p|$ grows. Thus replacing $\delta M$ by an operator-only constant
would strengthen the contract incorrectly.
''')

claim(54, 'Transport of actual normal residuals',
      'Same real Hilbert spaces; bounded A,C; positive or arbitrary common normal parameter; whole norm error delta.',
      'OperatorResidualTransport.normal_residual_difference;OperatorResidualTransport.normal_residual_available_bound;OperatorResidualTransport.true_normal_residual_bound', r'''
For the normal residuals formed with the same parameter,
\[
r^A_\lambda(x)-r^C_\lambda(x)
=(A^*-C^*)(Cx-v)+A^*(A-C)x .
\]
If $\nn{C-A}\le\delta$, then
\[
\nn{r^A_\lambda(x)-r^C_\lambda(x)}
\le\delta\bigl(\nn{Cx-v}+(\nn C+\delta)\nn x\bigr).
\]
Hence a computed-model normal allowance $\nn{r^C_\lambda(x)}\le\rho$
gives the corresponding true normal allowance by adding this expression.
''', r'''
Expand the two residuals. The $\lambda x$ terms cancel. Insert and
subtract $A^*Cx$ to obtain the displayed identity. Adjoint isometry
gives $\nn{A^*-C^*}=\nn{A-C}\le\delta$ and $\nn{A^*}=\nn A$.
Submultiplicativity therefore bounds its two terms by
$\delta\nn{Cx-v}$ and $\nn A\,\delta\nn x$.
The triangle inequality gives $\nn A\le\nn C+\delta$, yielding a
bound written in terms of available-model quantities and the allowance.
Finally apply $\nn{r^A}\le\nn{r^C}+\nn{r^A-r^C}$.

The identity itself does not require a positive parameter; positivity
is needed when this transported residual is used in SR-49 to control
an inverse correction. The model error remains distinct from the solver's
normal residual. Both contributions are amplified by the corresponding
positive-parameter correction scale. A small fixed model allowance is
therefore not a uniform guarantee when $\lambda$ tends to zero.
''', ('SR-49','SR-53'))

claim(55, 'Strong consistency without matching model kernels',
      'Same real Hilbert spaces; fixed true bounded A, fixed real tau and fixed identifiable p; source cap M; true bounds and exact/near accepted uncertain-model sources; vanishing allowances.',
      'ChangingDiscrepancy.norm_control;ChangingDiscrepancy.near_true_residual;ChangingConsistency.projected_consistent;ChangingConsistency.source_error_limit;ChangingConsistency.true_kernel_leakage_tendsto_zero', r'''
Suppose $p\in S_A$, $\nn p\le M$, and
\[
\nn{C_i-A}\le\delta_i,\qquad
\nn{Ap-v_i}\le\eta_i .
\]
If $x_i$ lies within $\kappa_i$ of an exact accepted source for
$C_i,v_i$ with allowance $\epsilon_i=\eta_i+\delta_iM$, and
$\eta_i,\delta_i,\kappa_i\to0$, then $x_i\to p$.
The model kernels and ranks may change. For arbitrary $g$, using
$p=P_{S_A}g$ yields
$\nn{x_i-g}\to\nn{P_{N_A}g}$ and $P_{N_A}x_i\to0$.
''', r'''
Let $y_i$ be the exact accepted comparison. SR-53 makes $p$ feasible
for the available model at allowance $\epsilon_i$. In the positive
branch, regularized optimality and the lower discrepancy bound give
$\nn{y_i}\le\nn p$: compare the objective at $y_i$ and $p$, then
cancel the fitting terms using
$\nn{C_ip-v_i}\le\epsilon_i\le\nn{C_iy_i-v_i}$.
The small-data branch is zero and satisfies the same domination.

The upper discrepancy bound gives
$\nn{C_iy_i-v_i}\le\tau\epsilon_i$. Returning to the true operator,
\[
\nn{Ay_i-Ap}
\le\delta_i\nn{y_i}+\tau\epsilon_i+\eta_i
\le(\tau+1)\epsilon_i .
\]
Thus $y_i$ is norm dominated by the fixed identifiable $p$ and has true
image residual tending to zero. The density argument printed in SR-51
proves $y_i\to p$ without projecting onto the changing model kernels.
The near-source difference then tends to zero, proving $x_i\to p$.

For arbitrary $g$, $AP_{S_A}g=Ag$, so the same true-data bound applies
to $p=P_{S_A}g$. Continuity of norm and true-kernel projection gives
the remaining limits. The fixed cap concerns this limiting identifiable
source. It is not a claim that the minimum-norm sources for unrelated
models have already converged.
''', ('SR-51','SR-53'))

claim(56, 'Available-model certificate and selected-source soundness',
      'Real Hilbert setting; operational checks use C; external true allowances and source cap; positive effective allowance and tau>1 for selection.',
      'OperatorCertificates.Certified;OperatorCertificates.certified_near;OperatorCertificates.certified_consistent;OperatorCertificates.inflated_feasibility;OperatorCertificates.selected_from_allowances_consistent', r'''
A source is certified using $C$ when either
$\nn v\le\tau\epsilon$ and $\nn x\le\kappa$, or it has an SR-52
positive certificate for $C$ with allowance $\epsilon=\eta+\delta M$.
Such a source is near accepted for the available model.
With the external truth premises of SR-55 and vanishing allowances,
certified sources converge to the true identifiable source.

If $\epsilon>0$ and $\tau>1$, those truth premises also give feasibility
of the total exact discrepancy selector for $C$; the selected exact
sources are consistent under the same vanishing data/operator bounds.
''', r'''
In the small-data branch compare $x$ with the accepted zero source:
$\nn{x-0}\le\kappa$. In the positive branch, SR-52 supplies an actual
accepted comparison source at distance at most $\kappa$. This proves
operational soundness without using $A$.

For the true conclusion, separately supply $\nn{C-A}\le\delta$,
the true-data bound, and $\nn p\le M$. These hypotheses are not fields
established by an observed fitting certificate. They allow SR-55 to
be applied to every certified source.

SR-53 gives the feasible witness $p$ for the available model. A positive
effective allowance and $\tau>1$ ensure a strict residual target above
its attainable floor in the non-small-data case; the total discrepancy
construction chooses an actual positive-parameter source there and zero
in the other branch. Each selected source is exact accepted, so SR-55
applies with $\kappa=0$. This selected object is noncomputable in the
generic formalization. Its existence theorem and soundness are distinct
from a finite numerical search implementation.
''', ('SR-52','SR-53','SR-55'))

section('Candidate-dependent discrepancy without a supplied source cap', r'''
The acceptance rule can avoid an externally supplied number $M$ by using
the candidate itself in the uncertainty allowance. Put
\[
c_{\eta,\delta}(x)=\eta+\delta\nn x .
\]
A generalized accepted source is either zero in the small-data branch
$\nn v\le\tau\eta$, or an actual Tikhonov source whose residual lies between
$c_{\eta,\delta}(x)$ and $\tau c_{\eta,\delta}(x)$.
This definition contains $C,v,\eta,\delta,\tau,x$ and the positive parameter;
it does not contain a true-source cap. Feasibility remains a separate
question and retains a quantitative relation between model accuracy and
the true noise scale.
''')

claim(57, 'Candidate-dependent self-bounding',
      'Real Hilbert spaces; bounded C; lambda>0; delta≥0; feasible comparison p for candidate noise; actual regularized candidate.',
      'GeneralizedDiscrepancy.regularized_norm_domination;GeneralizedDiscrepancy.accepted_norm_control', r'''
Let $x$ be the actual regularized source for $C,v,\lambda$. If
\[
\nn{Cp-v}\le c_{\eta,\delta}(p),\qquad
c_{\eta,\delta}(x)\le\nn{Cx-v},
\]
then $\nn x\le\nn p$.
In particular, if $\nn{C-A}\le\delta$ and $\nn{Ap-v}\le\eta$,
every generalized accepted source satisfies $\nn x\le\nn p$.
''', r'''
Suppose instead $\nn x>\nn p$. Since $\delta\ge0$, candidate noise
is monotone in source norm:
$c_{\eta,\delta}(p)\le c_{\eta,\delta}(x)$.
The two displayed hypotheses imply
$\nn{Cp-v}\le\nn{Cx-v}$.
Comparing Tikhonov objectives, the fitting-square term at $p$ is no larger,
whereas its positive weighted source-square term is strictly smaller.
The total objective at $p$ is strictly smaller than the objective at its
actual unique minimizer $x$, a contradiction.

With true operator bounds, SR-53 applied using $M=\nn p$ gives the
required candidate-noise feasibility. The operator allowance implies
$\delta\ge0$. The positive accepted branch therefore satisfies the lemma;
the small-data branch $x=0$ satisfies the norm conclusion directly.

The lower discrepancy inequality is decisive. An upper residual bound
alone can allow overly large regularized source norms. Here the lower
bound grows with the candidate norm, and objective minimality prevents
that growth from exceeding a feasible comparison source. The comparison
source enters the proof of soundness, while the acceptance definition
continues to have no externally supplied source cap.
''')

claim(58, 'Generalized true residual and strong consistency',
      'Real Hilbert spaces; true whole-operator/data bounds; tau≥0; generalized accepted or near-accepted sources; vanishing allowances.',
      'GeneralizedDiscrepancy.accepted_true_residual;GeneralizedDiscrepancy.accepted_consistent;GeneralizedInexact.near_true_residual;GeneralizedInexact.near_consistent;GeneralizedInexact.near_source_condition_rate', r'''
A generalized accepted $x$ obeys
\[
\nn{Ax-Ap}\le(\tau+1)c_{\eta,\delta}(p).
\]
A source within $\kappa$ of such an $x$ obeys the same bound with
$\nn A\,\kappa$ added. For $p\in S_A$, vanishing data/operator
allowances and near-source budgets imply strong convergence to $p$.
If $p=A^*w$, an inexact accepted candidate also satisfies
\[
\nn{x-p}^2\le
2\kappa^2+4\nn w(\tau+1)c_{\eta,\delta}(p).
\]
''', r'''
SR-57 gives $\nn x\le\nn p$, so
$c_{\eta,\delta}(x)\le c_{\eta,\delta}(p)$.
The upper generalized discrepancy bound and $\tau\ge0$ yield
$\nn{Cx-v}\le\tau c_{\eta,\delta}(p)$. Insert $Cx$ and $v$ into
the true residual:
\[
\nn{Ax-Ap}\le
\delta\nn x+\nn{Cx-v}+\eta
\le(\tau+1)c_{\eta,\delta}(p).
\]
For a near candidate, split its image difference through the exact accepted
comparison and apply the operator norm bound to the correction.

As $\eta_i,\delta_i\to0$, the comparison-source noise
$\eta_i+\delta_i\nn p$ tends to zero. Exact candidates are norm dominated
by $p$ and have true image error tending to zero; the same density argument
as SR-51 proves their strong convergence. Add a vanishing near-source
difference for inexact candidates. No relative feasibility condition is
needed in this implication once accepted candidates have been supplied.

For the source-condition rate, norm domination and $p=A^*w$ give
\[
\nn{y-p}^2\le2\ip{p}{p-y}\le2\nn w\,\nn{A(p-y)}
\]
for an exact comparison $y$. Bound its image by the first conclusion.
Then $\nn{x-p}\le\nn{x-y}+\nn{y-p}$ and
$(a+b)^2\le2a^2+2b^2$ prove the stated inexact rate.
''', ('SR-51','SR-57'))

claim(59, 'Relative feasibility and noncomputable selection',
      'Real Hilbert spaces; eta>0,tau>1; true operator/data bounds; delta‖p‖<(tau−1)eta.',
      'GeneralizedDiscrepancySelection.positive_parameter_source;GeneralizedDiscrepancySelection.exists_accepted;GeneralizedDiscrepancySelection.selectedSource;GeneralizedFeasibility.relative_accuracy_of_scaled_error;GeneralizedDiscrepancyConsistency.selected_consistent', r'''
If $\nn{C-A}\le\delta$, $\nn{Ap-v}\le\eta$ and
\[
\delta\nn p<(\tau-1)\eta,
\]
then an accepted source exists with norm at most $\nn p$. In the large-data
case one can choose a positive parameter whose residual is exactly
$\tau\eta$. A sufficient ratio condition is
$\delta\le\gamma\eta$ and $\gamma\nn p<\tau-1$.
Noncomputably selected families converge to $p\in S_A$ when the data/operator
allowances vanish and the pointwise feasibility conditions hold.
''', r'''
The true bounds imply
$\nn{Cp-v}\le\eta+\delta\nn p<\tau\eta$.
If $\nn v\le\tau\eta$, the zero source is accepted. Otherwise the strict
attainable-floor bound and $\tau\eta<\nn v$ give a positive exact
discrepancy root for $C$ with residual $\tau\eta$.
Let $x$ be its actual Tikhonov source. Objective comparison, or the
fixed-noise domination lemma, gives $\nn x\le\nn p$.
Consequently
\[
c_{\eta,\delta}(x)\le\eta+\delta\nn p<\tau\eta
=\nn{Cx-v}.
\]
Because $\delta\ge0$ and $\tau>1$,
$\tau\eta\le\tau c_{\eta,\delta}(x)$.
Thus both generalized band inequalities hold.

Multiplying $\delta\le\gamma\eta$ by $\nn p\ge0$ and the strict margin
$\gamma\nn p<\tau-1$ by $\eta>0$ proves the ratio specialization.
The chosen source is defined by classical choice from the existence
theorem. Its raw definition takes $A,p$ and the truth/feasibility proofs
as arguments; it is a theorem-level witness rather than an extracted
algorithm using only available measurements. Each chosen source is
accepted, so SR-58 proves the family convergence. The selection theorem
retains the feasibility premises even though the acceptance predicate has
no supplied scalar source cap.
''', ('SR-57','SR-58'))

claim(60, 'Inexact generalized sources and the zero-model boundary',
      'Same Hilbert setting; near exact generalized acceptance with vanishing correction budget; scalar boundary uses valid but nonvanishing model allowance.',
      'GeneralizedInexact.NearAccepted;GeneralizedInexact.near_consistent;GeneralizedDiscrepancyExamples.identity_candidate_accepted;GeneralizedDiscrepancyExamples.zero_model_not_accepted;GeneralizedDiscrepancyExamples.zero_model_valid_true_bounds;GeneralizedDiscrepancyExamples.zero_model_relative_accuracy_fails', r'''
Near-generalized acceptance is preserved by enlarging a source-correction
budget and gives the consistency conclusion of SR-58 when that budget
tends to zero.
Nevertheless valid true-noise and operator allowances alone do not ensure
generalized feasibility. With
$A=1$, $C=0$, $p=v=1$, $\eta=1/10$, $\delta=1$ and $\tau=2$,
no source is generalized accepted.
''', r'''
Near acceptance means there exists an exact generalized accepted comparison
$y$ with $\nn{x-y}\le\kappa$. Increasing $\kappa$ preserves that
inequality. Along a family, choosing the comparisons and adding the
vanishing difference proves consistency by SR-58.

For the scalar boundary, the true data error is zero and
$\nn{C-A}=1\le\delta$, so both stated truth allowances are valid.
The small-data branch would require $1\le2/10$, which is false.
For every positive parameter, the actual regularized source of $C=0$
is zero and its fitting residual is one. Its candidate noise is
$1/10+1\cdot0=1/10$, so the upper generalized band would again require
$1\le2/10$. Every branch fails. The relative feasibility condition also
fails, since $1<(2-1)/10$ is false. Thus the boundary refutes an
unconditional existence interpretation, not the conditional theorem.

For comparison, take $A=C=1$, $v=1$, $\eta=1/10$, $\delta=0$,
$\tau=2$ and $\lambda=1/4$. Then
$x_\lambda=4/5$ and the residual is $1/5$.
It lies in $[1/10,2/10]$, so the candidate is accepted, and
$0<(2-1)/10$ verifies the strict feasibility margin.
These examples use the actual scalar normal inverse and exact norms,
not a substituted approximate residual.
''', ('SR-57','SR-58','SR-59'))

section('Calibration generates an operator allowance', r'''
The final link connects justified calibration measurements with the
whole-operator premise used above. It does not infer the calibration truth
allowance from the model's own fit. Let $K$ be a real normed calibration
coordinate space, $G$ a real normed source space and $V$ a real normed
response space. A split frame has bounded synthesis $U:K\to G$ and
analysis $R:G\to K$ with $UR=I_G$. Its coordinates may be redundant:
$U$ need not be injective or square. The reconstruction identity requires
coverage of every source direction.

The observed response $Y:K\to V$ is an operator, and the assumptions
$\nn{Y-AU}\le\eta_{\rm cal}$ and $\nn{Y-CU}\le f$ are operator-norm
enclosures. Individual calibration samples do not automatically give these
enclosures. A mathematical or experimental justification of
$\eta_{\rm cal}$ remains a separate input.
''')

claim(61, 'Redundant split calibration identifies the operator',
      'Real normed spaces; bounded U,R with UR=I; whole calibration truth/model-fit operator bounds.',
      'CalibrationFrame.Frame.factor_through_frame;CalibrationFrame.Frame.difference_factorization;CalibrationFrame.Frame.measured_operator_bound;CalibrationFrame.Frame.measured_operator_bound_of_analysis_bound;CalibrationFrame.Frame.exact_calibration_identifies', r'''
Every bounded source operator $T$ factors as $T=(TU)R$. Therefore
\[
C-A=((CU)-(AU))R,\qquad
\nn{C-A}\le(\eta_{\rm cal}+f)\nn R .
\]
If a supplied analysis bound is $\nn R\le k$, the allowance is at most
$(\eta_{\rm cal}+f)k$. Exact calibration $Y=AU=CU$ forces $A=C$.
''', r'''
For every source $g$, $URg=g$, so $Tg=TU(Rg)$. This proves the actual
factorization, including its application to $C-A$.
The triangle inequality through the common measured operator gives
\[
\nn{CU-AU}\le\nn{CU-Y}+\nn{Y-AU}
\le f+\eta_{\rm cal}.
\]
Submultiplicativity then yields the displayed allowance.
Both measured bounds imply their scalar allowances are nonnegative;
hence replacing $\nn R$ by a larger $k$ preserves the inequality.
With exact calibration, $CU-AU=0$ and the factorization gives $C-A=0$.

Redundancy causes no logical problem. For instance, let
$K=\RR^2$, $G=\RR$, $U(k_1,k_2)=k_1$ and $Rg=(g,0)$, with the
standard product norm. Then $UR=I$, $\nn U=\nn R=1$, but
$U$ has a nontrivial kernel. The frame spans the source even though
it has an unused coordinate. A true scalar map $A=a$ and model $C=c$
with measured row $Y(k_1,k_2)=yk_1$ give
$|y-a|\le\eta_{\rm cal}$ and $|y-c|\le f$,
hence $|c-a|\le\eta_{\rm cal}+f$.
The same estimate comes from the general factorization rather than
assuming the coordinates are square and invertible.
''')

claim(62, 'Calibrated recovery and conditional selected sources',
      'Fixed split calibration frame; real Hilbert G,V; fixed bounded true A and tau≥0; fixed identifiable p; whole calibration truth/model fit and true data allowances; generalized acceptance; relative feasibility for choice.',
      'CalibrationRecovery.generated_operator_bound;CalibrationRecovery.generatedDelta_tendsto_zero;CalibrationRecovery.calibrated_consistent;CalibrationRecovery.calibrated_error_norm_limit;CalibrationSelection.exists_accepted_from_calibration;CalibrationSelection.calibrated_selected_consistent', r'''
For recovery assume $G,V$ are real Hilbert spaces, $A$ is a fixed bounded
true operator, $\tau\ge0$ is fixed, and $p\in(\ker A)^\perp$ is fixed.
Retain the whole calibration bounds and the true data bounds
$\nn{Ap-v_i}\le\eta_i$. Put $\delta_i=(\eta_{{\rm cal},i}+f_i)\nn R$.
If the true data,
calibration-truth and model-fit allowances tend to zero, then
$\delta_i\to0$. Generalized accepted sources using this generated
allowance converge to a fixed identifiable true source $p$.
For an arbitrary true source $g$, apply this with $p=P_{S_A}g$ and genuine
data bounds $\nn{Ag-v_i}\le\eta_i$; then the source-error norm tends to
$\nn{P_{N_A}g}$.

If additionally $\eta_i>0$, $\tau>1$ and
$\delta_i\nn p<(\tau-1)\eta_i$ pointwise, accepted sources exist and the
noncomputable selected sources have the same limit.
''', r'''
Apply SR-61 at every index to obtain the actual operator bound
$\nn{C_i-A}\le\delta_i$. Because the frame is fixed, its finite norm
$\nn R$ is a constant. The sum of the two vanishing calibration
allowances tends to zero, so multiplying by that constant proves
$\delta_i\to0$. With the genuine data-noise bounds, every premise of
the accepted-source consistency theorem SR-58 is now available.

For arbitrary $g$, use $p=P_{S_A}g$. Its forward image is $Ag$, so the
same data bounds hold. The strong source limit is $p$, and continuity
gives $\nn{x_i-g}\to\nn{p-g}=\nn{P_{N_A}g}$.
No calibration can remove source ambiguity in the true forward kernel
without an additional identifying condition.

The relative margin feeds the generated allowance into SR-59 and proves
pointwise existence and norm domination. Its chosen sources are accepted,
so the first conclusion applies to them. The raw selection is still
noncomputable and proof-dependent. Calibration has generated the
operator-error premise; it has not eliminated the distinct truth, data,
feasibility or selection obligations.

In particular, declining observed model-calibration fit alone is
insufficient: the calibration-truth allowance must also vanish.
If the reconstruction frame changes with the index, a growing analysis
norm would require additional control. The printed family theorem uses
the fixed frame it actually assumes.
''', ('SR-58','SR-59','SR-61'))

claim(63, 'Hierarchical and approximate reconstruction frames',
      'Real normed spaces; bounded split stage frames; or bounded U,R with whole reconstruction defect at most rho<1.',
      'CalibrationHierarchy.comp;CalibrationHierarchy.comp_analysis_norm_le;CalibrationHierarchy.hierarchical_operator_bound;ApproximateCalibration.approximate_factorization;ApproximateCalibration.approximate_frame_bound;ApproximateCalibration.measured_approximate_operator_bound', r'''
For split frames $(U_E,R_E):J\rightleftarrows K$ and
$(U_F,R_F):K\rightleftarrows G$, the composite is split, with analysis
$R_ER_F$ and
$\nn{R_ER_F}\le\nn{R_E}\nn{R_F}$.
The corresponding calibration allowance is at most
$(\eta_{\rm cal}+f)\nn{R_E}\nn{R_F}$.

More generally, if $\nn{I-UR}\le\rho<1$, then
\[
\nn T\le\frac{\nn{TU}\nn R}{1-\rho},\qquad
\nn{C-A}\le\frac{(\eta_{\rm cal}+f)\nn R}{1-\rho}.
\]
''', r'''
The composite synthesis is $U_FU_E$ and analysis is $R_ER_F$.
Their product is
$U_F(U_ER_E)R_F=U_FR_F=I_G$.
Submultiplicativity bounds the composite analysis norm; applying
SR-61 and that bound proves the hierarchical allowance. There is no
requirement that either synthesis be square or injective.

For the approximate frame, use the exact identity
$T=(TU)R+T(I-UR)$.
It gives
\[
\nn T\le\nn{TU}\nn R+\nn T\,\nn{I-UR}
\le\nn{TU}\nn R+\rho\nn T .
\]
Since $1-\rho>0$, absorb the final term and divide.
For $T=C-A$, the measured calibration bounds give
$\nn{TU}\le\eta_{\rm cal}+f$, producing the operator allowance.
This argument only uses norm inequalities; it does not substitute an
assumed exact inverse for the approximate reconstruction.

The denominator records the loss of control. At $\rho=0$ the exact
frame estimate is recovered. At $\rho=1$ the absorption step gives no
bound, and it is not legitimate to reuse the formula by division.
Likewise the product of hierarchical analysis norms is a valid
conservative bound, not generally an equality or the optimal sensitivity
of the composite. These conditioning factors belong in the certificate.
''', ('SR-61',))

claim(64, 'A missed calibration direction permits unbounded error',
      'Actual partial calibration from R to R² with product norm; bounded unseen scalar operators; arbitrary real norm threshold.',
      'CalibrationExamples.partial_not_surjective;CalibrationExamples.unseen_comp_partial;CalibrationExamples.unseen_norm;CalibrationExamples.arbitrarily_large_unseen_error;CalibrationExamples.perfect_partial_calibration_unbounded', r'''
Let $U(t)=(t,0)$ and $C_s(x,y)=sy$. Then $C_sU=0$ and
$\nn{C_s}=|s|$. For every real $M$ there is an operator agreeing
perfectly with zero on the entire calibration subspace yet satisfying
$\nn{C_s}>M$.
The calibration synthesis is not surjective. Thus perfect agreement on a
proper source subspace does not control whole-source operator accuracy.
''', r'''
Direct substitution gives $C_sU(t)=s\cdot0=0$.
The second-coordinate projection has norm one, so scalar multiplication
gives $\nn{C_s}=|s|$; the vector $(0,1)$ also verifies the lower bound.
Choose $s=|M|+1>0$. Then $\nn{C_s}=|M|+1>M$ while its calibrated
response remains zero. Taking the true operator and measured response
both zero shows that both calibration residuals vanish, even though
the whole operator discrepancy exceeds $M$.

The vector $(0,1)$ is outside the range of $U$, proving nonsurjectivity.
A split reconstruction $UR=I_{\RR^2}$ would make every source a range
vector, so no such reconstruction exists here. Nor can any approximate
reconstruction for this synthesis have whole defect below one:
the range of $UR$ has second coordinate zero, and therefore
$(I-UR)(0,1)$ has second coordinate one and norm at least one.
This last observation explains the direction-coverage role of the
strict absorption threshold in SR-63.

The positive redundant example and this negative partial example differ
in coverage, not coordinate count. Extra coordinates can coexist with
complete reconstruction of every source. Calibration of fewer source
directions leaves an operator component that all tested calibration
responses fail to see. The theorem makes that obstruction explicit
without claiming that an externally supplied truth allowance can be
inferred from those responses.
''', ('SR-61','SR-63'))
