# v0.1.1 confirmatory decision map

## Why this is the next test

The v0.1.0 standard run showed ordinary task learning and partial lexical transfer, but it did not beat the strongest controls reliably on composition, renaming, and counterfactual completeness. Formal state pressure improved canonical composition while degrading renaming. The cleanest next question is therefore not “does a larger model score higher?” It is:

> Is the missing capability stable operator knowledge, or the higher-order ability to bind a new episode-local name to a demonstrated transition?

## Frozen comparison

Each of two dataset seeds is crossed with three model seeds. Within every cell:

- `answer_only` receives the untouched 20,000-record canonical corpus;
- `role_bind_augmented` receives 16,000 deterministic canonical records plus 4,000 calibrated renaming episodes;
- `role_bind_scrambled` receives those same 16,000 canonical records plus token-matched versions of the same 4,000 episodes whose demonstrated nonce meanings are permuted;
- all three arms receive exactly 20,000 answer-supervised optimization records and share one frozen tokenizer and identical initial-model hash;
- no arm receives formal state, program, operator, equivalence, or law labels as model input;
- all arms train for eight epochs and evaluation uses the final checkpoint, eliminating selection and training-budget differences;
- `iid_validation` remains separate from the independently generated `iid_test` and is retained as a diagnostic;
- evaluation uses balanced hard splits, matched canonical/correct/scrambled calibration triplets, and complete counterfactual bundles; and
- training and evaluation nonce vocabularies are disjoint.

The preregistered primary aggregate is the within-cell `role_bind_augmented - role_bind_scrambled` contrast. It asks whether the *meaning* of the calibration, rather than extra records or nonce exposure, teaches binding. Deltas from `answer_only` are context. Neither calibration-arm contrast is evidence of spontaneous emergence.

## Outcome map

| Observed pattern across crossed seeds | Best interpretation | Next theory move |
|---|---|---|
| Answer only passes composition, paired renaming, balance, and counterfactual gates beyond controls | Candidate bounded behavioral evidence for spontaneous operator-sensitive induction | Replicate at a new scale, then add activation intervention, ablation, and rescue before a causal-representation claim |
| Answer only fails renaming; correct calibration beats scrambled calibration on renamed accuracy, pair-joint correctness, and test-time correct-versus-scrambled calibration while preserving hard splits | Calibration meaning induces a transferable binding procedure; the prior bottleneck was meta-binding rather than mere nonce exposure | Model binding as an explicit second-order operator and test new arities/worlds |
| Role binding improves renaming but canonical, lexical, pair, or triple performance collapses | Narrow calibration tradeoff or capacity competition, not a reusable operator language | Separate binding memory from state execution and preregister a capacity-matched architecture test |
| All three arms fail composition and counterfactual completeness | The current sequence architecture/data regime does not support reliable iterative execution | Test an execution-oriented architecture while retaining the same data and evidence gates |
| TF-IDF or question-majority matches either neural arm on hard splits | Remaining surface or class structure dominates | Repair the benchmark before making a symbolic claim |
| Results vary sharply by seed | The phenomenon is unstable at this scale | Report the distribution; increase replication before changing thresholds |

## Claim stop

`EVIDENCE_ADJUDICATION.json` adjudicates only the registered behavioral gates for one answer-only run. A PASS does not establish latent causal mediation, independently invented symbols, general symbolic competence, awareness, or consciousness. The exact/fuzzy quotient file is a benchmark-structure reference unless a later analysis is explicitly fitted to learned representations.
