# Komorebi Unified Inference / Stochastic / Bayesian — v7

Active release: `CHECKED_RELEASES/FD_Exact_Posterior_Certificates_v0.1.0_Checked`.

All v6 checked-release files are preserved byte for byte. Root v7 controls override
historical next-task instructions; v6 controls are under HISTORY/v6_root_control.

## Read first

PROOF_NOTE.md, FINAL_VERIFICATION_RECEIPT.json, AXIOM_AUDIT.json,
Komorebi/RationalCertificateChecker.lean, Komorebi/RationalPosteriorCertificate.lean,
and Komorebi/RationalCandidateAcceptance.lean.

## Closed in this block

Exact rational inputs H,L,N,m,y,sigma encode P=L L^T and R=N N^T+sigma I.
The checker verifies sigma>0, complete self-adjoint packet geometry, each local
residual-energy upper bound b_ab, and an innovation-energy upper bound V.
A successful check proves the actual-posterior bound

    W2^2 <= (sum_ab b_ab)*(sigma+V)/sigma^2.

A square-root-free rational tolerance check implies W2<=epsilon.
The Gram witnesses derive covariance validity and the genuine quadratic noise
floor. No exact Kalman gain, innovation inverse, or eigenvalue solve is required.
The executable exactCandidate producer has a universal validity proof.

For a fixed model and fixed packet resolutions, checked candidate acceptance
preserves certificate validity and never increases the selected score. An
arbitrary finite batch preserves the incumbent's posterior bound and tolerance.
Both example instances have kernel-checked actual-law conclusions. See
results/FORMAL_INSTANCES.json rather than interpreting Python output as a proof.

## Strongest next bounded target

Prove a solver-specific contraction and finite-iteration posterior tolerance.
For an exact rational Richardson gain update

    B_next = B + tau*(P H^T - B S),

first prove the exact residual recurrence

    F_next = F*(I - tau*S).

Under certified 0<sigma<=lambda_min(S)<=lambda_max(S)<=Lambda, take tau=1/Lambda.
Prove a Frobenius contraction with rho=1-sigma/Lambda, handle rho=0 separately,
and derive an explicit or existential finite iteration count for epsilon>0.
Connect the result to exactCandidate, checkTolerance, and the actual posterior
Wasserstein theorem, not just matrix norms. Reuse the current acceptance policy.
Finite diagnostics involving proposals are not a convergence proof.

Alternatively develop genuine interval-input or directed-rounding enclosures,
but do not reopen the completed exact-rational checker or claim it already
certifies uncertain real measurements or arbitrary floating-point computations.

## Other remaining boundaries

Automatic factor/floor discovery for an arbitrary covariance input; parser and
serializer implementation proof; packet-changing/model-changing policies;
factor-alignment sharpness; sequential filtering kernel recursion; the sharper
four-term covariance identity; full transport metric axioms/optimality; general
Ito/nonlinear/singular-innovation extensions; literature-priority audit.

## Verification

51 active modules passed: 40 unchanged inherited modules, 10 new proof modules,
and a full axiom-audit module. All 232 theorem/lemma declarations were audited,
including 67 new declarations. Counts include support identities and regressions.

Use pinned Lean 4.34.0-rc2 / mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
Follow MODULE_ORDER.json with verify_blocks.py, one thread and warnings-as-errors,
40 seconds per Lean process. Outer tool limits must permit the receipt to be
written. A timeout or interrupted invocation is not a successful check.

Concrete rational checks use decide +kernel, never native evaluation. All audited
axioms are contained in propext, Classical.choice, Quot.sound. No placeholders or
custom axioms occur in active sources. The pinned Mathlib cache is reused.
Historical unrelated programs are preserved but not freshly rebuilt.

Do not rewrite source files after checking without recompiling their affected
closure. audit_integrity.py --seal audits recorded runs and hashes; it is not a
replacement for the Lean compilation itself.
