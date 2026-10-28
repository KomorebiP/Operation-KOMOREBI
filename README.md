# Realization Calculus and Komorebi Space

**Komorebi P. · Work in progress**

> **Author’s note:** This work remains in progress and has, in many respects, been rushed because of circumstances introduced by OpenAI. I am continuing to correct, verify, and organize it.

The [public project and authorship statement](docs/PROJECT_STATEMENT.md#current-state-and-publication-circumstances) records this context. Completion, review, and verification vary by component; all executable software remains **beta / work in progress**.

Realization Calculus studies how mathematical structure behaves under decomposition, coordinate change, transfer, and refinement. Its basic objects include packets, operator blocks, compatible realizations, and explicit residuals.

Komorebi Space provides the ambient setting for those constructions. It brings realizations, projections, transfers, compatibility conditions, and obstructions into one framework. Together, the calculus and the space organize the foundations and applications collected here.

## Start here

| Goal | Starting point |
|---|---|
| Understand the framework | [Reading guide](docs/START_HERE.md), then the foundations below. |
| Read the main developments | [Twelve core papers](papers/README.md) and [monographs](monographs/README.md). |
| Choose by readiness | [Completion stage, Lean coverage, and confidence](docs/COMPLETION_STATUS.md), with links to exact evidence. |
| Run or reproduce something | [Small example](#run-a-small-example), [software guide](docs/LIBRARIES.md), and [verification guide](docs/VERIFICATION.md). |
| Help finish the collection | [Finalization queue](docs/FINALIZATION_QUEUE.md) and [correction guidance](#use-and-contribute). |

The [authorship statement](docs/PROJECT_STATEMENT.md) explains the pseudonym, human–AI collaboration, and standards of evidence.

## Foundations

| Work | Subject |
|---|---|
| [Realization Calculus](monographs/realization-calculus/) | The collected core development, from packets and transfer to refinement and applications. |
| [Komorebi Space](monographs/komorebi-space/) | The ambient framework for realizations, projections, compatibility, residuals, and obstructions. |
| [Realization Boundaries](monographs/realization-boundaries/) | Representability, finite descriptions, and explicit limits of realization. |
| [Sufficient Resolution](monographs/sufficient-resolution/) | Resolution conditions and the information retained by a representation. |

## Further reading

| Interest | Starting point |
|---|---|
| Arithmetic, special functions, and sequence constructions | [Special Functions](monographs/special-functions/) |
| Signals, quadratic forms, and numerical probability | [COS Method](monographs/cos-method/) and [Polyphase Signal Calculus](papers/paper-v/current/) |
| Quantum models and circuit constructions | [Quantum and Circuits](monographs/quantum-and-circuits/) and [Quantum Seed Calculus](papers/paper-vii/current/) |
| Discrete and continuous physical models | [Physics](monographs/physics/) |
| Algebraic signal models | [Large Signal Model](monographs/large-signal-model/) |
| Machine reasoning, abstraction, and interacting agents | [Machine Native Reasoning](monographs/machine-native-reasoning/) and [Machine Societies](monographs/machine-societies/) |
| Discovery, proof, and review | [Proof Path Theory](monographs/proof-path-theory/) and [Komorebi Methodology](monographs/komorebi-methodology/) |

## Software and experiments

**All software is beta and work in progress.** The implementations are available for research, evaluation, and feedback. Each package documents its supported inputs, dependencies, and numerical or computational limits.

- [Komorebi Math](https://github.com/KomorebiP/komorebi-math): Python tools for finite operators, packets, coordinates, signals, arithmetic, and inspectable certificates.
- [Polyphase Float](https://github.com/KomorebiP/polyphase-float): C arithmetic with explicit precision and rounding, constant computation, and selected special functions.
- [Additional packages](packages/README.md): research implementations and their worked examples.
- [Experimental laboratories](experiments/README.md): computational models, protocols, and retained outcomes.

The [software guide](docs/LIBRARIES.md) links documentation and qualification instructions, including [Constructive Repair’s current Windows results and remaining release checks](docs/components/CONSTRUCTIVE_REPAIR.md). This repository is a collection of separate projects; each runnable component has its own setup and supported environment.

## Run a small example

With Python 3.10 or later, run this command from the collection root:

```text
python -B formal/research-preview-1/demo.py
```

The expected JSON reports `status: PASS` and `scalar_coefficient_comparisons: 96`: three polynomial-mask cases with 32 coefficients each. The example uses only the Python standard library. It compares two finite calculation routes; it does not execute Lean or test the minimal-realization compiler. See [Research Preview 1](formal/research-preview-1/README.md) for its mathematical scope.

The [verification guide](docs/VERIFICATION.md) explains how to obtain a Git checkout, run the collection checks, reproduce component results, and interpret failures. The [collection workflow](https://github.com/KomorebiP/Operation-KOMOREBI/actions/workflows/artifact-checks.yml) reports checks for individual commits.

## Read the mathematics with its evidence

Each development distinguishes written results, formal statements, exact calculations, and experiments. Conditional results retain their hypotheses. Paper XI's general arithmetic realization endpoint remains Conjecture 66. Physics and machine-model developments state their remaining construction and empirical obligations alongside completed mathematics.

The [formalization guide](formal/README.md) explains the corresponding Lean projects and their recorded contracts. The [research index](research/README.md) connects further constructions, partial results, and open questions.

| Status field | What it tells you |
|---|---|
| Completion stage | Whether a specific manuscript, release contract, or prototype has reached its stated milestone. |
| Lean coverage | Which formal claims have recorded compiler evidence and which still need a current replay. |
| Confidence basis | The kind and scope of recorded review, proof, calculation, or experimental evidence. |

Lean is optional: a sound written argument can support a result without formalization. Reader inclusion requires a clear claim and appropriate support. The [focused soundness review](docs/SOUNDNESS_REVIEW_2026-10-27.md) and [SRIC admission audit](docs/SRIC_ADMISSION_AUDIT_2026-10-27.md) explain the decisions; incomplete implementation entries are separated into an [incubator](docs/INCUBATOR.md). The [SRIC repair](docs/SRIC_REPAIR_2026-10-27.md) and [first three Machine Societies proof reviews](docs/MACHINE_SOCIETIES_PROOF_REVIEW_2026-10-27.md) record subsequent progress. The [eight-claim review](docs/MACHINE_SOCIETIES_PROOF_REVIEW_BATCH2_2026-10-27.md), [stochastic-closure review](docs/MACHINE_SOCIETIES_PROOF_REVIEW_BATCH3_2026-10-27.md), and [safety, amendment, and computability review](docs/MACHINE_SOCIETIES_PROOF_REVIEW_BATCH4_2026-10-27.md) bring coverage to 38 of 62 pairs: 36 recorded passes, two qualified statements, and 24 unreviewed. The memory bound needs its domain stated explicitly; the computability theorem and its certificate consequence need an event-emitting compilation premise. The [coverage index](manifests/machine-societies-review-index.json) binds each counted claim to the exact source and review. These reviews are limited in scope and do not certify every listed work.

These fields are assessed separately. A finished reading edition can contain open conjectures; a passing collection check verifies its stated integrity and tooling scope. The [27 October audit](docs/AUDIT_2026-10-27.md) records source-integrity checks and partial Windows package qualification. The [finalization queue](docs/FINALIZATION_QUEUE.md) tracks source recovery, fresh proof builds, bounded reviews, and remaining experiments.

## Repository map

| Location | Contents |
|---|---|
| [papers/](papers/README.md) | Core papers, current source editions, and retained earlier editions. |
| [monographs/](monographs/README.md) | Extended foundations, applications, and companion volumes. |
| [research/](research/README.md) | Further developments, partial results, and open programs. |
| [formal/](formal/README.md) | Formalization entry points and the preserved research preview; other Lean projects live with their components. |
| [packages/](packages/README.md) and [experiments/](experiments/README.md) | Research software, examples, protocols, and computational laboratories. |
| [docs/](docs/START_HERE.md) | Maintained reading, status, authorship, and verification guides. |
| [manifests/](manifests/) and [verification/](verification/) | Source inventories, status records, and dated verification evidence. |
| [tools/](tools/) | Collection maintenance and integrity checks. |

The [component index](docs/COMPONENT_INDEX.md) links selected source directories and their file records. Preserved packages can contain historical publication or license wording; consult the current [publication status](docs/PUBLICATION_STATUS.md) and collection terms alongside those records.

## Use and contribute

Read the [collection reuse terms](LICENSE.md), together with the license files and third-party notices in the relevant component. The current collection grant explains how to interpret retained historical licensing notices. Cite **Komorebi P.**, the specific work, and the source revision used.

For a correction, identify the paper or package, commit or edition, file and statement or function, and the exact discrepancy. For executable behavior, include a small reproducible input, command, environment, expected result, and actual output. Submit a [GitHub issue](https://github.com/KomorebiP/Operation-KOMOREBI/issues) or a proposed correction with that information.

Original source packages and dated evidence are preserved. Corrections to a sealed component need an identified revision and new evidence; maintained navigation is generated by `tools/update_source_navigation.py` and refreshed with `python -B tools/update_completion_status.py`. See the [maintenance instructions](docs/VERIFICATION.md#maintaining-reader-pages).

[Contribution index](CONTRIBUTIONS.md) · [Complete component index](docs/COMPONENT_INDEX.md) · [Source coverage](docs/SOURCE_COVERAGE.md) · [Publication status](docs/PUBLICATION_STATUS.md)
