# GitHub workflow guide

The collection's workflows have different triggers and scopes: a successful collection check does not mean a manual Lean replay, an AM-SPD package run, or a release operation has also succeeded. Inspect the workflow file and the run's exact commit before interpreting its result.

## Routine checks

| Workflow | Trigger | What it checks |
|---|---|---|
| [Collection and formal artifact checks](../.github/workflows/artifact-checks.yml) | Push, pull request, or manual dispatch | Collection entry points, preserved preview identity, all source receipts, maintained navigation/status pages, tooling regressions, bounded SRIC fixtures, and preview guard/classifier tests. It does not invoke Lean. |
| [Resolution Semantics Lean companion](../.github/workflows/resolution-semantics-lean.yml) | Relevant formal companion/source changes on main pushes or pull requests, or manual dispatch | Pinned Lean 4.24.0 build, fresh theorem/axiom inventories and three rejection controls on Ubuntu and Windows. Limited to the separate 0.2.0 companion and Theorem 7.3; no whole-paper verification. |
| [AM-SPD CI](../.github/workflows/am-spd-ci.yml) | Relevant package/workflow changes on main pushes or pull requests, or manual dispatch | AM-SPD compilation, lint, tests, package verification, and a synthetic-geometry replay on the configured Python 3.13 jobs. The matrix covers Ubuntu and Windows. It does not qualify unrelated packages. |

A documentation-only push normally runs the collection checks without triggering the path-filtered AM-SPD CI. The [verification guide](VERIFICATION.md) gives the local collection commands and explains what they establish.

## Manual or release-specific checks

| Workflow | Trigger | Scope and output |
|---|---|---|
| [Pinned Lean replay](../.github/workflows/lean-replay.yml) | Manual dispatch | Research Preview 1 only: checks sealed inputs, obtains its pinned toolchain/dependencies, runs a clean build, inspects axioms and negative controls, and validates a fresh proof receipt. Its run artifacts include workflow context. Unavailable bootstrap or incomplete controls remain limitations. |
| [AM-SPD paper replay](../.github/workflows/am-spd-paper-replay.yml) | Manual dispatch with selected cases (default: `synthetic_geometry`) | Replays the selected AM-SPD cases against their reference criteria and uploads the replay output. Selected cases are not every experiment in the collection. |
| [AM-SPD full research verification](../.github/workflows/am-spd-full-research-verification.yml) | Manual dispatch | Checks the retained AM-SPD research-source checksums and runs that package's documented verification script, retaining its output as a workflow artifact. “Full” is scoped to this package and script. |
| [Build AM-SPD distribution](../.github/workflows/am-spd-build.yml) | An `am-spd-v*` tag push or manual dispatch | Builds AM-SPD distributions and tests wheel/source-distribution installation separately from the checkout. Distribution artifacts are distinct from publication of a GitHub release. |

These workflows need their own successful run and evidence. The collection's static source records are not a substitute for a fresh execution, and workflow artifacts are retained according to the configured retention period.

## Workflows that publish changes

| Workflow | Trigger | Repository effect |
|---|---|---|
| [Constructive Repair qualified beta](../.github/workflows/constructive-repair-release.yml) | Relevant package, release-tool, license, or workflow changes on main pushes; pull requests and manual runs qualify without publication | Runs the existing release, engine, and isolated installed-wheel acceptance suites on Linux and Windows with CPython 3.13.5. Verifies both source archives, current metadata and byte-identical accepted wheels, then publishes a new qualified beta prerelease after all gates pass. |
| [Reader website](../.github/workflows/reader-site.yml) | Push, pull request, or manual dispatch | Builds the HTML guides, reading ZIPs and source-bound claim links, checks navigation and introductory examples, and deploys successful main builds to GitHub Pages. Pull requests build without deployment. It does not run Lean or review proofs. |
| [Import source collection](../.github/workflows/import-source-collection.yml) | Manual dispatch on main with a committed batch name and exact `expected_base` SHA | Imports and verifies the selected declared source batch, then publishes its changes. Its main-commit check prevents silently importing on an unexpected base. This is a source publication operation. |
| [AM-SPD stable release](../.github/workflows/am-spd-stable-release.yml) | Successful main-branch AM-SPD CI completion, or manual dispatch | Requires successful CI for the exact current main commit, builds and qualifies release assets, and can create the `am-spd-v1.0.0` release/tag. It preserves existing tag/release identities and refuses a conflicting revision. This is a publication operation, not a general test command. |

The retained AM-SPD workflow name and versioned release machinery describe that component's historical release contract. The current collection-wide software label remains **beta / work in progress**. This guide documents the existing workflows. It does not change their triggers, dispatch a run, or publish a release.

## Record the outcome

For an executed check, retain the workflow/run URL, full source SHA, input parameters, relevant environment, conclusion, and artifact/receipt location. A failed setup, a failed intended negative control, and a successful proof rejection are different outcomes. Read the diagnostic record before assigning a status.

The [Actions page](https://github.com/KomorebiP/Operation-KOMOREBI/actions) shows current runs. The [records guide](RECORDS.md) links the collection's retained reports. The [publication status](PUBLICATION_STATUS.md) describes what is publicly available.

[Documentation](README.md) · [Run and verify](VERIFICATION.md) · [Contributing](../CONTRIBUTING.md)
