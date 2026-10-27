# Machine-Native Reasoning — Lean Block 04
## Approximate histories, rare evidence, and policy selection

**Komorebi P. · Operation Komorebi · Formal companion 0.4.0 · 10 October 2026**

This cumulative companion formalizes **eleven of the 27 results** in *Machine-Native Reasoning, Reviewed Core 0.2*. The two new results are **Core 3.8**, whole-history approximation and conditioning, and **Core 5.6**, uniform model error and changed-policy regret. The nine earlier results and all fourteen predecessor substantive modules are retained unchanged. Sixteen source results, including Core 4.1's joint response/record approximation, remain unformalized here.

## The connected result

The complete coarse-state and action/report path is compared under one common history-dependent policy. If initial aggregation error is at most `delta` and each actual joint report/next-coarse-state row has error at most `epsilon t`, then every finite horizon H satisfies

    TV(P_H, Q_H) <= d_H = min(1, delta + sum(t < H, epsilon t)).

The laws are constructed by evolving the actual fine and coarse instruments. Hidden state is never supplied to the policy: its input is only the previous actions and reports. The full history includes the initial state and all subsequent states for mathematical comparison; it is not merely the terminal-state marginal.

After an event E with positive probability under both laws, the conditional final-state distance is at most

    min(1, d_H / max(P_H(E), Q_H(E))).

An event with probability strictly larger than d_H on either side is necessarily possible on both sides. Equality with d_H is insufficient. Impossible events do not receive a claimed posterior.

For a common finite policy class and the same complete path loss in [0,B] for each fixed policy, the expectation error is at most B*d_H. An approximate-model minimizing policy consequently has true regret at most `min(B, 2*B*d_H)` against the true minimizer. Actual finite minimizers exist. The argument first compares each policy with itself across the models; it never applies a same-policy theorem directly to two different controllers.

## New modules

| Module | Role |
|---|---|
| `MachineTheory/Variation.lean` | Finite total variation, aggregation and kernel contraction, perturbed kernels, sharp event/conditioning bounds, bounded expectations. |
| `MachineTheory/ApproximateHistory.lean` | Constructed full path laws, observation-only feedback, time-varying joint-row perturbations, projection, conditioning and event positivity. |
| `MachineTheory/ApproximateDecision.lean` | Uniform fixed-policy error, finite minimizers, changed-policy regret, and the direct full-history composition. |
| `MachineTheory/ApproximationExamples.lean` | Rare evidence, sharp unequal-mass conditioning, sharp regret factor, sensor misspecification, hidden initial history, and invalid-comparison controls. |

Read `docs/BLOCK04_PROOF_GUIDE.md` for the argument and `docs/ASSUMPTION_REVIEW_BLOCK04.md` for its scope. `docs/THEOREM_MAP.md` lists all 27 source results. `CONTINUE_HERE.md` is the next restart point.

## Exact examples and non-claims

A pair of specified finite laws has whole-law distance 1/100 and conditional output distance one after a report of mass 1/100. A second pair has event probabilities 1/10 and 1/5, whole-law distance 1/10, and conditional distance 1/2, attaining the maximum-denominator bound. A binary decision example attains the factor-two regret bound.

The inherited sensor is compared with calibration accuracy 37/50 rather than 3/4. The joint report/state row defect is proved exactly 1/100 for every fine world. Its full-history error at horizon H is at most min(1,H/100). For H=3 and a complete loss bounded by 23/20, the corresponding expectation and regret allowances are 69/2000 and 69/1000. These are mathematical allowances, not observed regrets or a new optimality calculation for the changed sensor.

The common finite policy catalogue and bounded path losses must represent the intended inquiry. The formal generic comparison does not discover permissions or implement a universal compiler from an arbitrary stopping tree to an absorbing process. Such encodings must preserve the same laws and costs. An expected-loss bound does not certify a hard execution budget, zero-probability safety, or physical model truth.

## Verification and reproduction

Current release evidence is in `evidence/final04/report.json`, `evidence/fresh04/report.json`, and `evidence/FRESH_REBUILD_BLOCK04.json`. The authoring-stage cumulative gate is `evidence/preflight04/report.json`. Each receipt is authoritative only for its own pinned source hashes. Earlier block evidence remains historical.

The driver performs an empty-local-object build, independent API restatements, actual environment inspection, transitive axiom audits, same-kernel module replay, negative controls, predecessor preservation and upstream cache consistency checks. The production library has 19 modules including the import-only root. There are 36 expected-outcome controls: 35 must fail compilation for their stated reasons; one must compile with a custom axiom and then fail the axiom policy.

```bash
python3 scripts/verify_release.py
python3 scripts/verify.py \
  --runtime /absolute/path/Komorebi_Portable_Lean_4.34.0-rc2 \
  --out evidence/my_new_replay
```

The driver refuses to overwrite a nonempty evidence directory. Verify the frozen inventory before generating new evidence. The pinned compiler is Lean 4.34.0-rc2 at `6a10ac8c22beadecabdbb0919c2b50214762f91d`; mathlib is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The tested route uses Linux x86-64, Python, Git, and the restored portable runtime with its saved cache inventory. The runtime is not included.

Allowed transitive axioms are only `propext`, `Classical.choice`, and `Quot.sound`. The kernel checks proof terms; the project-authored source scanner and receipt verifier do not replace it. Local `leanchecker` replay uses the same kernel, not an independent implementation. Upstream dependencies are reused and hash-checked rather than rebuilt from source.

No neural training, parent-book Python suite, hardware experiment, external account action, hosted publication, or Windows execution is claimed. Real-valued finite laws and classical finite minimizers are mathematical objects, not an efficient extracted optimizer. No standalone font files, runtime payload, or third-party papers are redistributed. Existing source rights are retained.
