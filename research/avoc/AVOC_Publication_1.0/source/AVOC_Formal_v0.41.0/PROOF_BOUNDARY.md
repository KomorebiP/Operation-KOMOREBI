# Exact proof boundary — AVOC v0.41.0

## New kernel-checked result

The defined finite recorder preserves global operation-ID uniqueness, matching
pending intent, once-only terminal retention, replay idempotence, and rejection
of changed identity/outcome reuse. Pending intents are separate from immutable
terminal samples. The old unfinished-to-terminal lifecycle mismatch is proved.

A generative source machine produces terminal bits from the next latent outcome.
Every successful finite run refines both the raw recorder and inherited reveal
machine. Its actual terminal sample lists are source prefixes. The final policy
theorem derives that correspondence and the binomial count laws, applies the
fixed scheduled calibration, and bounds unconditional uncertified issuance by
the sum of allocated errors. Rejected runs and any globally pending operation
block counts and hence plans. Insufficient selected samples also block plans.

The indexed Lean executor is proved equivalent to the raw core's successful
execution. The JSON parser/wire representation and Python implementation have
bounded tests, not a universal decoding or host refinement proof.

## Physical model boundary

The raw endpoint takes external terminal labels; the generative model constructs
them from finite latent sources. The latter's primitive conditional law is a
model assumption. No theorem derives that law from accepted log syntax or proves
that a real input log was generated this way. Authentication, honest outcome
checking, complete provenance, identity stability, and stationarity remain open.

The terminal log uses finalization order. Full logging and resolved intents do
not suffice for IID samples if outcome-dependent latency reorders independent
attempted outcomes. The exact finite completion-order counterexample is retained
in results/v0.41.0/review_completion_order*. It is a counterexample to a proposed
physical interpretation, not to the formally defined source-generative theorem.

Faults consume no accepted-source position in the model. One-attempt equal
retention formulas, finite scheduler experiments, and the new lifecycle theory
do not constitute a general physical-attempt-to-accepted-stream coupling.
The recorded source probabilities and physical attempted success probabilities
cannot be identified without an additional justified model.

## Exact probability and policy scope

The probability is unconditional over the original finite rational space:
P(issue and not EpisodeCertified) <= total alpha. It is not a posterior statement
about the observed interval or the same nominal bound conditioned on completed,
accepted, or resolved runs. Earlier conditioning counterexamples remain valid.
No issuance, termination, collection-cost, or productivity lower bound is proved.

Schedules, sample sizes, grids, and allowances are fixed before the data used
by them. Selected strata must match their stated true probabilities. The formal
sources are finite and rational. Arbitrary real parameters, drift, infinite
streams, and unrestricted stopping remain outside the result.

Deterministic setup/gross membership is supplied. Quotes remain frozen within a
policy episode. Regret is expected finite-horizon policy-value difference under
a compatible realization, not realized sample-path loss. Its comparator uses
conservative upper-setup reservations. Runtime spent records those reservations;
no refund or physical-spending identity follows. No new cross-episode accounting
or in-episode learning theorem is added.

## State and external execution scope

The new recorder and CLI are pure finite snapshot reducers. They do not persist
a journal, execute or retry an operation, authenticate an endpoint, or implement
a crash-safe transaction. Recording one terminal event per ID does not prove
exactly-once external execution. Reusing a new ID for the same physical work is
not ruled out by ID uniqueness alone.

A semantic rejection yields no final snapshot/export. This is an all-or-nothing
result for pure reduction, not rollback of already performed external work.
Fault completion closes its pending ID and contributes no sample; it is not
permission to repeat a paid operation.

The optional export registry is injective in protected identities, requires all
completed keys to be registered, and rejects any pending operation. Its evidence
labels are deterministic identifiers, not signatures or proof-checker outputs.
The inherited calibration parser and active durable-run protocol are unchanged.
No automatic migration or mutation of existing intents/bands is introduced.

## Verification and trust

The exact named theorem/lemma inventory is checked against kernel axiom reports,
including inherited private helpers. Only propext, Classical.choice, and
Quot.sound are allowed. Local project objects are rebuilt from empty with
warnings as errors. External dependency caches are pin checked, not rebuilt
from every source. Lean/compiler/kernel, Python, OS/filesystem, and inherited
SQLite remain part of the trust boundary.

The source scan is heuristic and separate from compilation/axiom checks. Negative
proofs must fail substantively, not through parser/setup/resource/crash errors.
Exact bounded model comparisons and actual Lean/Python endpoint comparisons do
not prove universal adapter correctness. Final runtime object/compiler hashes
bind executable evidence to the clean build.

All 191 inherited non-audit mathematical modules, historical evidence, and
inherited runtime/check sources remain unchanged. Earlier corrected negative-test
claims and the historical missing-full-v0.36-source provenance boundary remain
preserved. Semantic artifact backends retain their stated languages and cost
models; no universal program minimization, arbitrary Lean-proof ingestion,
measured LLM productivity, or historical novelty claim is added.
