# Claim and dependency ledger
**Self-Improving Intelligence v0.2.0**

All universal statements below are conditional mathematical results with prose proofs. The executable suites check bounded models. The phrase “independent checker” means a separately coded checking path within this project, not an independent auditor or proof kernel.

| Added result | Main assumptions | Result | Does not establish |
|---|---|---|---|
| Theorem 7.1: fixed unknown model | Finite candidate models, one persistent true label, common actions/cost conventions, represented state and support | The tagged-state construction gives the exact robust repair frontier in a finite horizon | That the true physical model belongs to the supplied class, or that arbitrary model classes can be learned |
| Theorem 11.1: checked search closure | Immutable cases, total binary unit-cost queries, unit-cost repairs each successful for at most one case, literal trees | A valid tree attaining work `1+ceil(log2 n)` and storage `2n-1` proves the complete frontier is that singleton | That every query library attains the bounds, or that a failed proposer proves infeasibility |
| Proposition 12.1: binary-family read cost | `n=2^k`, complete balanced depth `k`, `q` queries, the recorded guard/proposal/check interfaces | `n*q*(k+1)+2*n*k` compilation-phase model-record reads | Complete CPU work, cheapest general compiler, discovery of the query model, or bytecode minimality |
| Proposition 12.2: table audit floor | Direct access to independent arbitrary table entries, a nontrivial per-entry condition, deterministic sound and complete universal checker | Every relevant entry must be read on acceptance | The same floor for trusted generators, authenticated cached summaries, or proof-carrying tables |
| Proposition 13.2: two-worker race | Resumable workers, shared certified output target, alternating unit work, bounded dispatch cost | A constant-factor work bound relative to the faster worker | That the shipped sequential fallback implements this scheduler, or that combined storage is free |
| Theorem 15.1: anytime paired audit | Frozen comparison, scores in [-1,1], conditional mean null, predictable bounded nonnegative bets | Nonnegative supermartingale and time-uniform threshold bound | Validity after hindsight bet selection, altered candidate/contract, or an unsupported task-law assumption |

## Implemented discovery improvement

The finite selector compares the exact parent, a guarded first-query proposal, and a guarded balanced proposal. Their development lookup costs are 10,256, 10,380, and 488 respectively. The total of all three trials is 21,124 lookup units, not the full cost of inventing the candidates. It installs the balanced rule and stores its configuration before the additional evaluations.

At sixteen cells, the parent uses 576,128 compilation-phase model reads and the selected descendant uses 1,728. Each has the same additional common input-shape validation cost of 320. Both produce work 5 and 31 literal stored records. Counting common validation yields 576,448 and 2,048 total model-record reads for those defined stages.

With an allowance of 2,000 compilation-phase reads, the descendant returns the optimum, while the parent is incomplete within the allowance. The parent result must not be relabeled “infeasible.” The lookup saving is not a processor-time ratio.

## Generality and negative controls

Additional checks include a larger cube, a six-case support, a query library without singleton tests, and supplied affine relabelings/report flips. These are finite structural variants, not evidence of broad out-of-distribution intelligence. A four-case equality-only library triggers sequential fallback and costs 472 versus 402 lookup units. The proposal does not universally improve cost.

The proof of bounded slowdown concerns a separately specified resumable race. The software tests that scheduling abstraction on finite worker tapes. The shipped compiler uses sequential fallback and retains its actual overhead.

## What is learned, selected, compiled, or supplied

- Selected: one of the supplied proposal rules, based on its measured finite development costs.
- Compiled: a diagnostic controller for each current problem.
- Checked: scope, complete branch semantics, every represented case, resource bounds, and attained lower bounds.
- Supplied: candidate program templates, the theorem, checker, experiment model, repair semantics, selection procedure, and evaluation family.
- Not demonstrated: creation of a new compiler template, improved second-generation selector, autonomous learned semantic grounding, indefinite recursion, or general intelligence.

The original twelve statements retain their original assumptions. See the preserved source and earlier review notes for their detailed boundaries.
