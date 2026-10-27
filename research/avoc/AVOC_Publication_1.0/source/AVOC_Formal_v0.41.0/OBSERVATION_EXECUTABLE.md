# Exact observation-process executable evidence

`checks/test_observation_process.py` passed its declared finite assertion using
exact integer/rational arithmetic. This is bounded implementation evidence. The
universal mathematical claims require the separate Lean theorems and their
precise hypotheses.

## Contract and independent constructions

The model has two independent latent Bernoulli report streams with fixed
identity-specific probabilities. Each attempt chooses its identity and fault
probability using only the public history. A fault does not consume the next
latent report. An admitted report records either success or rejection, and
advances exactly that identity's report cursor. The complete immutable summary
log is retained; operation identifiers make exact replays idempotent.

One oracle enumerates every complete latent bit table and auxiliary fault tape.
Fault-tape weights use the declared history-dependent conditional kernels;
unused tape bits receive fair padding. For every fixed latent bit table, the
auxiliary weights sum to one. A second oracle recursively unfolds an attempt
tree, generating a fresh Bernoulli bit only after a nonfault transition. Their
entire terminal-trace mass dictionaries agree exactly. They share only the
explicit policy definitions, rather than their probability construction.

The table oracle checks pathwise that every identity's reports form its latent
prefix, including zero-weight rows. Direct latent prefix counts agree with an
independent Bernoulli convolution. Calibration cell envelopes are independently
computed by enumerating binary strings, without calling the production
binomial-coefficient evaluator. The existing Python calibration parser is then
called on every distinct tested trace/checkpoint request and compared with that
independent interval. These calls exercise the actual parser, including faults,
other identities, duplicate records, and incomplete checkpoints.

The fixed schedule contains sample sizes 1 and 2 for each identity, allocating
`1/20` to each pair and `1/5` overall. The grid has 100 cells. Every completed
checkpoint's bad-output mass is compared with its unconditional latent-prefix
bad mass. The union and a data-dependent identity/checkpoint selection are
checked against the total allocation. No-output trajectories remain in the
probability space; no division by checkpoint completion probability occurs.

## Tested family and results

All attempt horizons from 0 through 4 were crossed with four declared policies
and five probability pairs: `(0,1)`, `(1/2,1/2)`, `(1/10,9/10)`, `(1/3,2/3)`, and
`(1,0)`. The policies include alternating identities without faults, switching
identity after success with history-dependent faults, fault-aware identity
selection, and stopping on the first rejection. Endpoint probabilities and
zero-probability paths are included.

| Check | Count |
|---|---:|
| Complete experiment cases | 100 |
| Full latent/auxiliary table rows | 93,620 |
| Pathwise identity-prefix checks | 187,240 |
| Latent prefix count-law comparisons | 600 |
| Positive terminal-trace mass comparisons | 843 |
| Distinct actual-parser trace/checkpoint requests | 736 |
| Finite-schedule coverage cases | 100 |
| Additional interface boundary checks | 5 |

Nine experiments had a nonzero bad-output union probability. The largest was
`199/10000`; the largest selected-bad-output probability was `59/5000`. Both are
below the supplied global allocation `1/5`. These observed maxima apply only to
the enumerated family.

## Counterexamples and trust boundaries

1. **Outcome-dependent consuming censoring.** Let each attempted bit succeed
   with probability `1/10`. Retain successes, label every rejection a fault, and
   consume every attempted bit. After 20 attempts, issue the checkpoint as soon
   as two successes exist. Its interval is `[3/25,1]`, which excludes `1/10`.
   The exact bad-output mass is
   `60825300187483229419/100000000000000000000`, greater than `1/20`. Thus
   arbitrary outcome-dependent thinning cannot justify calibration for attempted
   success probability. A one-attempt fair-bit example also changes success
   probability from `1/2` to `1` conditional on retention.
2. **Conditioning on completion.** With latent report probability `1/10`, obtain
   one report; stop on rejection, otherwise obtain a second. Completion has
   probability `1/10`. The unconditional bad-output mass is `1/100`, below
   `1/20`, but the bad probability conditional on completion is `1/10`, above
   `1/20`. Predictable stopping therefore does not imply the binomial law after
   conditioning on completion.
3. **Nonconsuming outcome-dependent blocking.** If the next latent rejection
   blocks forever without advancing the report cursor, the issued reports still
   form a latent prefix. The same `n=2` bad-output event has mass `1/100`. This
   illustrates that the pathwise prefix domination itself needs no
   noninformativeness assumption: the assumptions needed to construct a latent
   IID stream from an operational model are a separate matter.
4. **Completeness is supplied.** The actual parser accepts a supplied log
   containing two successes. It cannot determine whether a rejection was
   removed before that log was supplied. The explicit thinned-log fixture
   preserves this boundary instead of treating parser success as authentication.

The operational meaning of “fault does not consume the next latent checked
report” must be justified for a real process. These tests do not establish that
actual rejected or timed-out operations obey it. They also do not establish
independence, stationarity, a pre-observation authority commitment, or a complete
authenticated log from real measurements.

## Reproduction and provenance

From the project root:

```bash
python3 checks/test_observation_process.py
```

The release run used the computation-audit bounded runner, Python 3.12.14,
60 seconds wall time, 30 seconds per-process CPU, a 1 GiB per-process address
space cap, one CPU affinity slot, and one cooperative numerical-library thread.
It completed in about 1.8 seconds. No randomness, network service, Lean runtime,
or external operation was used by this oracle.

- Canonical result: `results/v0.40.0/oracle_results.json`.
- Exact bounded-run result: `results/v0.40.0/oracle_run/oracle_results.json`.
- Version 2 manifest and captured logs: `results/v0.40.0/oracle_run/`.
- Canonical-copy equivalence and validator result:
  `results/v0.40.0/oracle_provenance.json`.
- Machine-readable contract and runnable fixtures:
  `examples/observation_process/`.

The result pins every project file used by the oracle, including the inherited
parser and baseline quote fixture. The manifest records unchanged input hashes,
the actual command and effective resource limits, and the output checksum. It
was successfully validated against the project root. A completed manifest is
execution provenance, not a theorem proof.

An initial development run also passed and is retained as
`results/v0.40.0/oracle_development_results.json`; final evidence is the
source-pinned bounded run above. No development counterexample or implementation
failure was suppressed. No historical source file was modified by this work.

There is no universal Python-to-Lean adapter refinement in this test, no
empirical validation, no guarantee conditional on completion, no unrestricted
optional stopping, and no within-episode model-change or cost-accounting claim.
