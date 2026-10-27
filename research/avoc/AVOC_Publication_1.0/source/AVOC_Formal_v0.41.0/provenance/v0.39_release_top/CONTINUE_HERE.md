# Continue from AVOC v0.39.0

Use this cumulative release as the checked source checkpoint. Read
PROOF_BOUNDARY.md, GAP_LEDGER.md, REPRODUCE.md, and the v0.39 verification and failure
records before extending it. Its exact predecessor is v0.38 with SHA-256
 a54dac36e77636ffd974e849a653995daea78091214921042c5f273b5a8cc6c4.

The finite rational binomial-calibration block is closed for its stated model:
counts -> proved exact intervals -> simultaneous finite-schedule coverage ->
adaptive checkpoint selection -> fresh fixed-model policy guarantee.

The next focused target is the observation process. Formalize a concrete joint
model of attempts, checked success/rejection, and infrastructure faults. Prove
when accepted counts actually have the required binomial marginal law under
adaptive operation selection. Outcome-dependent censoring is the primary known
obstruction. Preserve the counterexample where failures become timeouts.

Keep fault handling, scientific evidence, statistical coverage, and proof checking
separate. Do not turn confidence into certainty or posterior belief. Do not mutate
bands on an existing intent. Preserve inherited non-audit sources where possible,
record false proposals/counterexamples, and rerun substantive negatives through
the pinned project environment. Six old negative setup failures were repaired in
v0.39; never restore the old permissive failure classifier.

The source archive excludes runtime/cache. The separately retained portable kit
is Lean 4.34.0-rc2 with the exact nine pins in lake-manifest.json.
