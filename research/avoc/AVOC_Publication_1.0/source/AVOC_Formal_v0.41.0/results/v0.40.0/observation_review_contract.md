# Independent observation-contract audit

Primary verdict: **conditional on a named input** — the primitive stream and
operational sampling interpretation must be stated explicitly. The proposed
unconditional, fail-closed deployment conclusion is sound under the contract
below. The stronger completion-conditioned count and coverage claims are false.

This is a target-design audit, not an audit of v0.40 Lean proofs. Sources read
were the v0.39 `FiniteCalibration`, `CalibrationSchedule`, `CalibratedPolicy`,
and `CalibrationLog` modules in the fresh v0.40 workspace; their hashes are in
`observation_review_counterexample.json`. The supplied predecessor archive hash
is `298b6daed3875697a59c15caa6d8546c9cfe2d30aa8cfbc4aab0275ad63be44c`.

## Normalized safe claim

Fix finitely many identities and a finite predeclared schedule. Checkpoint j
specifies an identity i(j), sample size n(j), grid m(j)>0, alpha(j)>=0, and true
rational parameter p(i(j)) in [0,1]. Each identity has enough latent bits for its
scheduled prefixes. Its finite latent sequence has the Bernoulli product law
with parameter p(i); the sequence law is a primitive outcome law, not an assumed
count distribution. Cross-identity independence is sufficient but not necessary.

An operational report must consume the next latent bit for its exact identity.
Faults, unfinished attempts, and exact replays must consume no report bit.
Completed observations preserve prefix order; deleting or skipping latent bits
after seeing their values is not this model. Deployment uses the first n(j)
unique accepted reports for a selected scheduled j and refuses when those reports
are unavailable. Warm/cold selected checkpoints must match the true parameters
specified by the eventual policy certificate.

Then, for any selection and completion/deployment gate, even when data-dependent,

    P(deployed and uncertified) <= sum_j alpha(j),

equivalently,

    P(not deployed or certified) >= 1 - sum_j alpha(j).

Here uncertified means the required learned-band or fixed-episode certificate
fails. Deterministic realization membership and fixed-episode assumptions from
v0.39 remain. The theorem does not lower-bound deployment probability.

## Dependency graph

1. Primitive Bernoulli product masses -> valid finite sequence probability law.
2. Count equal-fiber calculation -> binomial law for every fixed prefix.
3. Existing exact interval theorem -> each latent prefix bad event has mass <=alpha.
4. Existing finite union bound -> simultaneous latent-prefix good event.
5. Operational transition induction -> reported first n bits equal latent prefix.
6. Fail-closed selection -> bad deployment is a subset of the scheduled bad union.
7. Existing realization/policy composition -> fixed-episode certificate on coverage.

Steps 1-2 close a real algebraic gap in v0.39; supplying a binomial-law premise
under a new name would not. Step 5 must be proved for the operational model, or
listed as a remaining named premise. Even proved steps 1-7 do not establish that
an actual external provider follows the primitive law.

## Obligation matrix

| Obligation | Target-design status |
| --- | --- |
| Rational p in [0,1], finite spaces | Required, unambiguous |
| n=0, p=0 or1, zero accepted reports | Must be covered in proof |
| Grid m>0 and alpha>=0 | Already explicit in interval theorem |
| Explicit product stream -> binomial count | Required new proof |
| Adaptive identity allocation | Sound with exact identity prefixes |
| Fault/replay prefix invariant | Required operational proof |
| Data-dependent stopping gate | Sound for unconditional bad deployment |
| Coverage conditioned on completion | Refuted below |
| Arbitrary informative deletion of potential outcomes | Excluded; changes target law |
| Arbitrary schedules invented after observing data | Out of scope |
| Empirical stationarity/authentication | Not addressed by finite model |
| Universal Python/log-to-model refinement | Not established by current sources |

## Decisive counterexamples

**Completion conditioning.** Let X1,X2 be independent fair bits. Report X1.
Permit a second report iff X1=true, independently of the current bit X2.
Completion has probability 1/2. Conditional on completion, success count K has
probabilities (0,1/2,1/2) at (0,1,2), unlike Binomial(2,1/2)=(1/4,1/2,1/4).
Thus predictability and independence from the current outcome do not make the
completion event independent of the earlier outcomes.

**Actual calibration failure after conditioning.** Use n=m=10, alpha=1/10,
p=1/2. Obtain the first nine fair bits; allow the tenth report only when the
first nine bits were all successes. Completion mass is 1/512. Conditional on
completion, K=9 and K=10 each have mass 1/2. The exact AVOC intervals are
[2/5,1] at K=9 and [3/5,1] at K=10. Therefore conditional miscoverage is
1/2>1/10. Unconditional bad-and-complete mass is only 1/1024, consistent with
the safe theorem. Independent Fraction arithmetic enumerated all 1024 paths;
the saved JSON records the exact results. This numerical verification supports
this one counterexample and is not a universal theorem.

**Informative censoring.** If uncensored success probability is p and current
success/failure keep probabilities are a and b, the accepted target is
q=pa/(pa+(1-p)b), assuming positive acceptance mass. Taking p=1/2,a=1,b=0 gives
q=1. Discarding faults cannot by itself equate p and q. Equal a=b>0 suffices
for the one-step target identity; additional process assumptions are needed
for a whole accepted stream.

## Interpretation and cheapest next check

An explicit latent accepted-stream construction is mathematically substantive
and avoids assuming the binomial count law. It is not a proof that operational
faults are noninformative for uncensored physical attempts. The release should
say whether p refers to accepted reports or uncensored attempts, and preserve
that target in the planner. An operational constructor that emits reports from
the next latent bit and leaves cursors unchanged on faults can prove the needed
prefix invariant. The independent review should next inspect its raw transition
definition and induction, then inspect the new count-fiber theorem and final
event inclusion without relying on the author's status claims.

No external mathematical theorem was needed for this audit. One exploratory
Python call incorrectly supplied a grid size to an API requiring grid points;
it raised TypeError and was replaced by direct exact enumeration. The failure
is retained in the JSON provenance.
