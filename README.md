# Operation Komorebi

**Realization Calculus · Komorebi P.**

Komorebi is a mathematical and computational research program developed through sustained human–machine collaboration. Its organizing questions concern transformations, compatibility, residuals, obstructions, and realization: what structure survives a change of representation, what prevents a proposed construction, and what evidence establishes that the construction works?

Packets retain selected components of a resolved object. Transfer blocks describe how maps act between those components. Exact reconstruction, refinement, and named residuals make these objects useful across arithmetic, algebra, signal processing, numerical computation, and experiments in machine reasoning.

This repository connects the papers, formal developments, experiments, and additional software. The installable Python library and the C floating-point library have separate source repositories and version histories.

## Choose an entrance

| Entrance | Contents and current state |
|---|---|
| [Komorebi Math](docs/LIBRARIES.md#komorebi-math) | Independently staged Python library. Its selected source is R4 Block 21 on the `1.0.0b4` line. |
| [Polyphase Float](docs/LIBRARIES.md#polyphase-float) | Independently staged C library, version 0.18.0. |
| [Papers](papers/README.md) | Papers I–XII and further editions, with actual import status. |
| [Formalizations](formal/README.md) | Imported Research Preview 1 and the separate project environments still to recover. |
| [Experiments](experiments/README.md) | AI, scientific, and computational studies being reconciled with their source and controls. |
| [Additional software](packages/README.md) | Numerical engines, research instruments, and other packages awaiting their individual source imports. |

Start with [START_HERE](docs/START_HERE.md) for a guided reading route. The [contribution index](CONTRIBUTIONS.md) records imported components, selected editions, and the full historical Part I register.

## A concrete starting point

[Research Preview 1](formal/research-preview-1/README.md) develops prime-power Cartier systems. It constructs finite coefficient machines and proves a minimum-cardinality reachable-observable linear realization under explicit hypotheses. Its preserved source, mathematical note, claim map, small Python examples, and recorded proof replay are imported here.

From that component directory:

```bash
python -B demo.py
python -B tools/check_release.py
```

These commands run a finite reference computation and artifact checks. The separate [proof reproduction instructions](formal/research-preview-1/REPRODUCE.md) identify its pinned Lean environment.

## Release status

This is a repository assembly candidate. Imported bytes and recorded verification are distinguished from checks executed on this candidate. Selected source editions awaiting import remain visible in the contribution ledger. The historical 87-entry register is an inclusion baseline, not a current theorem census or proof of complete corpus coverage.

The planned destinations are [Operation-KOMOREBI](https://github.com/KomorebiP/Operation-KOMOREBI), [komorebi-math](https://github.com/KomorebiP/komorebi-math), and [polyphase-float](https://github.com/KomorebiP/polyphase-float). These URLs are targets; their remote availability has not been confirmed for this candidate.

[Distribution status](docs/DISTRIBUTION_STATUS.md) records component terms and unresolved choices. No blanket license is applied by this assembly.

