# AVOC v0.41.0 verification record

Completed the recorder lifecycle and its formal connection to calibrated policy
issuance. This cumulative release contains the Lean theory, executable Python
and Lean interfaces, exact experiments, review records, failures, and reproduction
instructions. The current collector reports PASS with no errors.

## What we have created and proved

The inherited project supplies formal artifact and planning models, robust
quote-based policy bounds, recovery and accounting models, exact finite-sample
calibration, and finite conditional source laws. This release adds four modules
and 69 named theorems/lemmas:

| New module | Named declarations | Result |
| --- | ---: | --- |
| ObservationRecorder | 37 | Global operation-ID invariants, separate pending intents, immutable terminal history, exact replay, rejection of conflicting reuse, and once-only terminal retention |
| RecorderReveal | 24 | Every successful source-generative run refines the raw recorder and reveal machine; actual terminal samples are latent-source prefixes |
| RecorderPolicy | 7 | Rejected runs and any pending operation block counts and issuance; actual log-derived counts compose with scheduled calibration and policy certification |
| RecorderCodec | 1 | The indexed Lean executor's successful result equals the formal core run |

The final policy theorem derives both the binomial count laws and observed-prefix
correspondence from the finite rational source model. For a fixed finite schedule,
the unconditional probability of issuing a plan without the stated episode
certificate is at most the sum of its allocated errors. Failed or unfinished
runs remain in the probability space and issue no plan. This does not assert the
same nominal bound conditional on completion or guarantee eventual issuance.

The raw Lean JSON endpoint and separate Python reducer accept begin/finish
commands, reject conflicting or malformed requests, and expose no snapshot on
rejection. An optional injective identity registry exports fully resolved terminal
logs to the inherited calibration format. These are pure reducers; their supplied
outcome labels are not authenticated, and they perform no external operation.

## Fresh verification

| Gate or comparison | Result |
| --- | ---: |
| Clean warnings-as-errors positive build | 222/222 |
| Exact named theorem/lemma axiom reports | 2,268/2,268 |
| New named declarations | 69 |
| Non-audit mathematical modules | 195 |
| Substantive negative proof rejections | 135/135 |
| Inherited mathematical modules byte-identical | 191/191 |
| Historical evidence files preserved | 15,136 |
| Inherited runtime/check source files preserved | 205 |
| Source shortcut scan | Zero hits |
| Fresh inherited executable regression groups | 5/5 |
| Independent release-tool mutation probes | 72/72 |
| Recorder command sequences against independent Python model | 69,905 |
| Recorder command sequences against actual Lean | 4,381 |

The axiom union is exactly Classical.choice, Quot.sound, and propext. There are
no missing, extra, or duplicate named reports. Lean 4.34.0-rc2 and nine exact
dependency pins were used. Local objects were rebuilt from empty; external pinned
caches were not rebuilt from every source. The source scan is heuristic and is
separate from compilation and kernel axiom checks.

The Python finite family covers all words of lengths 0–4 over the declared
16-command alphabet: 957 accepted and 68,948 rejected. Actual Lean comparison
covers all words of lengths 0–3, plus malformed-input and valid-boundary checks.
Longer scenarios and calibration export are tested separately. An independent
reviewer reproduced the dictionary-model results and 27 raw interface probes.
These finite tests do not establish universal Python/parser refinement.

The final bounded executable run passed in 95.03 seconds. Its compiler and all
73 local transitive source/object pairs were unchanged before and after execution.
The canonical result SHA-256 is
ad6811fcf6d8e2e179386522dff949f4207ff500028ac503d9baef176c892def.
The bounded-run manifest passed its validator. Independent proof review also
reproduced 12 focal theorem axiom checks; both independent reviews have no open
blockers for the claims as stated.

All five inherited replay groups passed freshly: robust quote oracle,
selected-only workflows, recovery, lazy execution, and calibration. Calibration
reproduced 11,193 exact count checks, 45 sequence checks, 18 interface checks, and
184 actual Lean comparisons. The synthetic n=500,k=400 case returns
[361/500,433/500] and changes cold generation to warm inspection. Recovery retains
one warm invocation and zero cold invocations through duplicate resume. These
are controlled local fixtures, not measured real-service savings.

## A newly isolated statistical obstruction

Complete, honest, unique, fully resolved logs do not imply unbiased samples in
completion order. With two independent fair attempted outcomes, completing a
success first makes the first logged bit successful with probability 3/4.
Waiting for both operations does not undo that ordering bias.

The exact twenty-attempt example is stronger: complete all successes before
rejections and wait for every intent to resolve. For n=m=10, alpha=1/10, and true
p=1/2, the event of at least ten successes produces interval [3/5,1]. That event
alone has probability 308333/524288, approximately 0.588, exceeding 0.1.
This finite computation refutes a proposed physical interpretation; it does not
refute the formal theorem, whose source law is stated in report order. It is
preserved as executable evidence, not presented as an additional Lean theorem.
Earlier censoring and completion-conditioning counterexamples remain preserved.

## Failures and corrections retained

Two attempted bounded runs failed before producing scientific results: imposed
2 GiB and 8 GiB address-space limits prevented Lean startup. A diagnostic showed
about 8.56 GiB peak virtual address space and 3.66 GiB resident memory. The final
run used no additional address-space cap, retained the shared 20 GiB cgroup, and
enforced wall, CPU, affinity, thread, and output limits. Both failed records remain.

Review also found and verified corrections to negative-failure classification,
import and fixture provenance, compiler binding, and launcher diagnostics.
Development elaboration failures, the duplicate-output launch refusal, and
review-script/counting corrections are documented. The cause of the duplicate
output's presence was not established. See DEVELOPMENT_FAILURES_v0.41.0.md.

## Remaining gaps and next target

1. **Physical sampling and report order:** justify a universal multi-attempt
   coupling to the stated conditional source law, or formalize an initiation-indexed
   sample contract that prevents outcome-dependent omission and reordering.
2. **Input authority and host correctness:** authenticate outcomes and complete
   provenance; prove universal parser/Python/storage refinement. A unique terminal
   record does not prove exactly-once external execution.
3. **Controller composition:** handle changing bands within an episode and
   cumulative error, reward, and cost across episodes. Current quotes are frozen;
   regret uses the inherited conservative reservation comparator.
4. **Empirical and broader mathematical scope:** validate actual workloads and
   costs; extend beyond finite rational sources, fixed finite schedules, and the
   stated artifact languages to drift, dependence, unrestricted stopping, and
   scalable or sharper confidence methods.

The next statistical task is the report-order/physical-attempt boundary. Resolving
all pending IDs alone is insufficient, as the new counterexample demonstrates.

All 191 inherited mathematical modules match AVOC_Formal_v0.40.0.zip, SHA-256
bf0b87a381ac47e4de215c0cfbcde4e3fcfa710470390e4db8843cb4140e739f.
The historical missing-full-v0.36-source boundary remains documented. See
FORMAL_THEORY.md, PROOF_BOUNDARY.md, GAP_LEDGER.md, RECORDER_EXECUTABLE.md,
REPRODUCE.md, and results/v0.41.0/release_verification.json in the archive.
The separate package report verifies ZIP integrity, membership, and payload hashes.
