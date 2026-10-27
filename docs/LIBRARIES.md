# Software guide

**All Komorebi software is beta and work in progress.** Version numbers and historical release names identify revisions; the current public software status is beta.

| Library | Documentation | Current terms |
|---|---|---|
| [Komorebi Math](https://github.com/KomorebiP/komorebi-math) | Repository README, examples, and package-specific qualification instructions | MIT for the current library; retain third-party notices. |
| [Polyphase Float](https://github.com/KomorebiP/polyphase-float) | Repository README and numerical reference documentation | LGPL-3.0-or-later; retain third-party notices. |

The [package index](../packages/README.md) covers software in this collection. The [experimental laboratories](../experiments/README.md) and [research programs](../research/README.md) contain further implementations and protocols.

The [collection verification guide](VERIFICATION.md) provides Git checkout instructions, a small standard-library example, and commands for source and navigation checks. For a concrete package record, see [Constructive Repair](components/CONSTRUCTIVE_REPAIR.md): its engine and installed cases passed on the recorded Windows environment, while full release qualification remains incomplete.

The [corrected SRIC 0.3.3 source runtime](../packages/sric-admission-v0.3.3/README.md) has bounded admission/CLI qualification and remains beta; real-model execution is pending.

## Reproduce a result

1. Select a source revision and read its supported platform and dependency requirements.
2. Run the documented small example before a larger calculation.
3. Use the component's qualification command and compare the exact reported scope and expected output.
4. Record the source revision, inputs, platform, dependencies, arithmetic settings, and output.

A passing test applies to the exercised behavior. A finite computation, numerical approximation, formal theorem, and software qualification record provide different kinds of evidence. Their individual assumptions remain in force.

[Recorded publication and qualification status](GITHUB_IMPORT_STATUS.md) · [Reading guide](START_HERE.md)
