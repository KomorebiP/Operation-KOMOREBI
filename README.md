# Realization Calculus and Komorebi Space

**Komorebi P.**

Realization Calculus studies how mathematical structure behaves under decomposition, coordinate change, transfer, and refinement. Its basic objects include packets, operator blocks, compatible realizations, and explicit residuals.

Komorebi Space provides the ambient setting for those constructions. It brings realizations, projections, transfers, compatibility conditions, and obstructions into one framework. Together, the calculus and the space organize the foundations and applications collected here.

Start with the [reading guide](docs/START_HERE.md), the [twelve core papers](papers/README.md), or the [monographs](monographs/README.md).

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
| Signals, quadratic forms, and numerical probability | [Polyphase Signal Calculus](papers/paper-v/current/) |
| Quantum models and circuit constructions | [Quantum Seed Calculus](papers/paper-vii/current/) |
| Algebraic signal models | [Large Signal Model](monographs/large-signal-model/) |
| Machine reasoning, abstraction, and interacting agents | [Machine Societies](monographs/machine-societies/) |
| Discovery, proof, and review | [Proof Path Theory](monographs/proof-path-theory/) and [Komorebi Methodology](monographs/komorebi-methodology/) |

## Software and experiments

**All software is beta and work in progress.** The implementations are available for research, evaluation, and feedback. Each package documents its supported inputs, dependencies, and numerical or computational limits.

- [Komorebi Math](https://github.com/KomorebiP/komorebi-math): Python tools for finite operators, packets, coordinates, signals, arithmetic, and inspectable certificates.
- [Polyphase Float](https://github.com/KomorebiP/polyphase-float): C arithmetic with explicit precision and rounding, constant computation, and selected special functions.
- [Additional packages](packages/README.md): research implementations and their worked examples.
- [Experimental laboratories](experiments/README.md): computational models, protocols, and retained outcomes.

The [software guide](docs/LIBRARIES.md) links documentation and qualification instructions.

## Read the mathematics with its evidence

Each development distinguishes written results, formal statements, exact calculations, and experiments. Conditional results retain their hypotheses. Paper XI's general arithmetic realization endpoint remains Conjecture 66. Physics and machine-model developments state their remaining construction and empirical obligations alongside completed mathematics.

The [formalization guide](formal/README.md) explains the corresponding Lean projects and their recorded contracts. The [research index](research/README.md) connects further constructions, partial results, and open questions.

## Use and contribute

Read the [collection reuse terms](LICENSE.md), together with the license files and third-party notices in the relevant component. The current collection grant explains how to interpret retained historical licensing notices. Cite **Komorebi P.**, the specific work, and the source revision used.

For a correction, identify the paper or package, the statement or function, and the exact discrepancy. For executable behavior, include a small reproducible input and the relevant environment.

[Contribution index](CONTRIBUTIONS.md) · [Complete component index](docs/COMPONENT_INDEX.md) · [Publication status](docs/PUBLICATION_STATUS.md)
