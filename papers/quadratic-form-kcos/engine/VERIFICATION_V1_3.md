# Komorebi Quadratic-Form Engine v1.3 verification

## Newly executed / re-executed test suite

- general central positive engine: 7/7 PASS
- noncentral positive engine: 4/4 PASS
- signed central engine: 4/4 PASS
- generalized signed/noncentral legacy regression: PASS
- approximate polyphase light cone: 5/5 PASS
- budget scheduler: 4/4 PASS
- spectral/tail bridge: 5/5 PASS
- residual trace/moment certificates: 5/5 PASS
- residual exact completion: 3/3 PASS

The unittest-based suites account for 37 passing test cases, plus the generalized regression script.

## Signed finite-endpoint exact controls

For Q=-0.02 chi2_80, exact right-tail controls were checked at 1e-8, 1e-30, 1e-100, and 1e-200.

Deepest tested tail: -200 decades.
Maximum absolute error: 2.842e-14 decades.
Maximum reported certificate: 7.230e-13.
All passed.

## Mixed-sign high-rank audit

A rank-340 spectrum with 180 positive and 160 negative coefficients was tested at five increasing saddlepoint tilts.

Deepest packetized result: log10(p)=-81.891936860562.
Maximum packet/full-grid discrepancy: 2.344e-11 decades.
Largest certificate: 7.402e-09.
All five packetized results passed their analytic certificates.

Independent tilted importance sampling placed every discrepancy within 1.411 Monte Carlo standard errors.

## Low-rank mixed-sign boundary

For Q=0.07(chi2_2-chi2_2), the distribution is exactly Laplace with scale 0.14.  Values through 1e-200 agree with the closed form to at most 3.056e-09 decades, but the current analytic COS-series certificate rejects the low-rank mixed cases.  This is a known certification limitation, not promoted as a certified production success.

## Arithmetic hardening

Signed and noncentral packet-error accumulation now uses the same log-sum-exp strategy as the positive engine.  The signed benchmark completes under `python -W error` without overflow warnings.

## Evidence boundary

The v1.3 production API covers:

- central positive Gaussian quadratic forms;
- central signed/indefinite Gaussian quadratic forms when the returned certificate passes;
- positive noncentral Gaussian quadratic forms.

The low-rank mixed-sign certificate remains deliberately conservative.  General noncentral indefinite forms are not yet in the production API.
