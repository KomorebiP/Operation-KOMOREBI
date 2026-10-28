# Contributing and reporting corrections

Operation-KOMOREBI is a collection of separate manuscripts, source editions, software packages, and experiments. Start with the [documentation index](docs/README.md), identify the component, and read its [status and evidence](docs/STATUS_CATALOG.md). All software remains beta / work in progress.

## Choose the right report

Use the [issue chooser](https://github.com/KomorebiP/Operation-KOMOREBI/issues/new/choose) for a correction, software problem, or source-record discrepancy. A useful report identifies the exact work, edition or commit, file, and observed problem. An issue is enough to report a finding; a proposed fix is optional.

| Report | Include |
|---|---|
| Documentation or mathematical correction | The exact sentence, statement, or equation; its assumptions; the discrepancy; and supporting reasoning or a small counterexample where relevant. Lean is optional. |
| Software problem | Package and revision, operating system, runtime/dependency versions, command, minimal input, expected and actual behavior, exit status, and relevant diagnostics. |
| Missing source, broken link, or stale record | The page or manifest entry, exact link/path, expected edition or digest, observed result, and any known source reference. |

For a problem specific to the independent [Komorebi Math](https://github.com/KomorebiP/komorebi-math/issues) or [Polyphase Float](https://github.com/KomorebiP/polyphase-float/issues) library, use that repository's issue tracker. Report collection navigation or cross-repository record discrepancies here.

## Preparing a change

Keep the change focused on one correction or related set of files. Explain the problem, resulting behavior, and checks performed. The pull request template provides space for the exact component/edition and any remaining limitations.

The [maintenance guide](docs/MAINTENANCE.md) identifies the relevant scripts, their file/publication effects, and the update rules for dated records.

Maintained guidance and frozen source editions have different update paths:

| Change | Where to work |
|---|---|
| README, reading routes, or category indexes | Edit the relevant template in [update_source_navigation.py](tools/update_source_navigation.py), then regenerate. |
| Documentation or record indexes | Edit [record_navigation.py](tools/record_navigation.py) or the underlying registered record, then regenerate. |
| Completion, Lean, confidence, or queue status | Update [project-status.json](manifests/project-status.json) only to the extent supported by the corresponding evidence. Scheduling alone does not promote scientific status. |
| Authorship, distribution, contribution, citation, or component guidance | Edit the maintained document directly and keep it registered for link checks. |
| A correction to a preserved manuscript, runtime, or sealed evidence | Identify a new edition or correction record with source correspondence and the applicable checks. Retain the original edition and its dated results. |

Reader inclusion depends on a clear claim and suitable support. A written argument, exact finite calculation, compiler result, and experiment have different scopes. A documentation change does not require formalizing a result in Lean.

## Checks for collection maintenance

From a Git checkout with Python and Git available:

```text
python -B tools/update_completion_status.py
python -B tools/update_completion_status.py --check
python -B -m unittest discover -s tools -p "test_*.py" -v
git diff --check
git diff --stat
```

Inspect the generated diff before submitting it. The [verification guide](docs/VERIFICATION.md) covers checkout requirements, source-receipt checks, component-specific commands, and failure interpretation. Source-receipt checks use committed Git trees; an unstaged source correction needs its own identified revision before it can be qualified.

For a software change, run the relevant package's tests and record the environment. For a scientific correction, state precisely which claim and dependencies the evidence covers. Record failed or unavailable checks alongside successful ones.

## Records, attribution, and terms

The [records guide](docs/RECORDS.md) links dated reviews and receipts. Give new evidence its own source revision, scope, inputs, and outcome; keep earlier failures and corrections traceable. The [workflow guide](docs/WORKFLOWS.md) distinguishes routine checks, manual replays, and workflows that publish changes.

Public attribution is **Komorebi P.** Follow the [citation guidance](CITATION.md) and the [collection reuse terms](LICENSE.md), together with applicable component and third-party notices.

[Collection](README.md) · [Documentation](docs/README.md) · [Finalization queue](docs/FINALIZATION_QUEUE.md)
