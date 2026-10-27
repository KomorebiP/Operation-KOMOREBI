# Paper XI formalization and reproducible verification

This project contains the selected Paper XI sources, the actual-monomial terminal with explicit compatibility repairs, and a separately identified comparison interface. It is designed to be copied or unzipped into an ordinary directory. The scripts derive all working paths from their own location.

## Exact source populations

| Population | Modules | Authoritative list | Aggregate import |
|---|---:|---|---|
| Selected publication sources | 423 | `catalogues/SOURCE_CATALOG.json` | `PaperXI.lean` |
| Names indexed by the publication catalogue | 4,342 names | `catalogues/DECLARATION_CATALOG.json` | Within the selected 423 modules |
| Actual-monomial terminal | 1 | `PaperXI/ActualMonomialLocalGlobal.lean` | `PaperXITerminal.lean` |
| Single-candidate comparison interface | 1 | `PaperXI/SingleCandidateComparison.lean` | `PaperXIAdditions.lean` |

The two additional modules are excluded from the selected 423-module and 4,342-name counts. The source catalogue, rather than a directory glob, defines the selected population. Historical absolute paths inside the retained catalogues are provenance fields. The scripts do not use those paths to find files.

The selected 423 source files retain their catalogue SHA-256 fingerprints. The terminal's original text is preserved at `terminal_original/ActualMonomialLocalGlobal.lean`, alongside its failed import-only revision. Its compatibility repair supplies a missing import and namespace openings, names implicit degree arguments, corrects comment syntax, makes already-declared standing hypotheses explicit, repairs local proof elaboration, installs the retained constructed residue-tower instances, and factors the final comparison through five private component lemmas. The lower-inclusion witness uses the retained equality in the exact forward direction of its goal; that correction and factoring preserve the public comparison-package header and conclusion. The exact original-to-final diff and source fingerprints are in `provenance/`. The original text was ill-typed: the release does not claim byte-identical terminal statements or proof bodies, or kernel equivalence to that invalid original. No successful original module build is available for a comparison of kernel declarations. The accompanying independent source review checks the changes against the original mathematical intent under its explicit hypotheses.

The new `PaperXI.SingleCandidateComparison.source` theorem applies to one supplied admissible candidate and an admissible reference. It uses the stated separating factor system and the equality of both factor profiles with the same declared profile. It does not consume an atom-realization existence field.

## Pinned environment

| Component | Pin |
|---|---|
| Lean | `leanprover/lean4:v4.34.0-rc2` |
| Lean source commit | `6a10ac8c22beadecabdbb0919c2b50214762f91d` |
| Linux x86_64 Lean binary SHA-256 | `e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550` |
| Mathlib commit | `aeb72f1e9981b6d35b426b16dca7759be3e7ba06` |
| Transitive dependency pins | Exact revisions in `lake-manifest.json` |

The compiler version and binary fingerprint match the retained Continuation 113 environment. The public source locations are the [official Lean release](https://github.com/leanprover/lean4/releases/tag/v4.34.0-rc2) and the [pinned mathlib commit](https://github.com/leanprover-community/mathlib4/tree/aeb72f1e9981b6d35b426b16dca7759be3e7ba06).

## Prepare once

The supplied portable bootstrap supports Linux x86_64, including Ubuntu under WSL on Windows. It requires Python 3.10 or newer, Git, `tar`, and `zstd`. The Python scripts use only the standard library.

From this directory run:

```bash
python3 scripts/bootstrap.py
```

The bootstrap downloads the exact official Lean archive, checks its published SHA-256 and the compiler fingerprint, checks out the exact dependency revisions, and retrieves the official mathlib cache for the necessary imports. It stores its runtime and dependencies inside this project. The release archive omits those large downloads.

After preparation, the following verifies the installed pins and direct object roots without downloading anything:

```bash
python3 scripts/bootstrap.py --offline
```

## Run the complete verification

```bash
python3 scripts/verify_all.py --jobs 1 --synchronous
```

This runs the source compilation, the three separately scoped owning-module axiom audits, and the audit's negative controls. It writes a new dated directory under `runs/`, including a `RUN_SUMMARY.json`. There are no dependency-download steps in this command.

Each compiler process is invoked with `-j1` to request one Lean worker thread. The job count bounds the number of simultaneous compiler processes. `--jobs 1` reduces concurrent memory pressure, and `--synchronous` adds the official Lean option `-DElab.async=false` so declarations are elaborated synchronously. The release's first full repaired-terminal attempt and its unchanged-source synchronous retry were both killed when the 8-GiB cgroup exhausted memory. A later bounded diagnostic localized a large kernel conversion to a reversed lower-inclusion witness; the delivered proof factors the comparison and uses that equality in the required forward direction. The final source replay retains synchronous mode. The receipts distinguish bounded diagnostics from the full run that also emits compiled objects. The local-field tower modules also require substantial resources and can take longer after nearly all other files have finished. The default wall-clock limit is 3,600 seconds per module; `replay.py --timeout` can change this resource bound without changing theorem statements.

An explicit output directory makes a run easy to identify:

```bash
python3 scripts/verify_all.py --jobs 1 --synchronous --out runs/my_release_check
```

The scripts refuse to overwrite an existing run directory. To repeat a run, choose a new directory.

A finalized replay with failed or timed-out modules can be continued in a new directory. The resume option verifies the previous receipt, finalized source hashes, source population, compiler and mathlib pins, dependency closure and every successful object's fingerprint before copying those objects. It compiles failed or blocked modules afresh and records the exact earlier-result lineage. If the runner itself was interrupted and its receipt remains `RUNNING`, this command cannot resume it; finalized source hashes are required.

```bash
python3 scripts/replay.py --jobs 1 --synchronous --resume evidence/previous_replay --out evidence/continued_replay
```

By default, resume rejects any changed source. A narrowly scoped compatibility-repair mode allows a finalized failed terminal to change only when its exact old and new SHA-256 fingerprints are supplied through `--terminal-revision OLD_SHA256 NEW_SHA256`. This mode authenticates the prior replay chain and rejects changes to successful selected or interface sources, their dependency closures, the pinned runtime and immediate predecessor's manifest, or successful objects. The final release receipts preserve the failed terminal revisions and the accepted revision separately. The portable verification of the delivered final sources does not require this repair mode.

## Individual checks

The same component commands can be run separately:

```bash
python3 scripts/replay.py --jobs 1 --synchronous --out evidence/my_replay
python3 scripts/axiom_audit.py --replay evidence/my_replay --scope selected --out evidence/my_selected_axioms
python3 scripts/axiom_audit.py --replay evidence/my_replay --scope terminal --out evidence/my_terminal_axioms
python3 scripts/axiom_audit.py --replay evidence/my_replay --scope new_interface --out evidence/my_interface_axioms
python3 scripts/audit_controls.py --replay evidence/my_replay --out evidence/my_audit_controls
```

The optional `kernel_replay.py` command runs the official `leanchecker` on the compiled objects. It uses the same kernel implementation as the compiler, so it is not an independent checker. Source compilation already checks the newly elaborated declarations through that kernel. For a separate additional pass, use:

```bash
python3 scripts/kernel_replay.py --replay evidence/my_replay --jobs 2 --out evidence/my_kernel_replay
```

The complete runner accepts `--kernel-replay` to include this optional pass. It is not a required gate of this release verification.

The `--lean-bin` option accepts another directory containing the matching Lean tools. The default resolves the project-local portable runtime before consulting `PATH`.

The project also includes conventional Lake library targets `PaperXI`, `PaperXITerminal` and `PaperXIAdditions`. The recorded release replay uses the explicit scripts above so that source populations, object provenance and audit counts remain visible.

## What the checks establish

By default, the source replay starts with an empty Paper XI object directory. It authenticates every selected source against the retained catalogue, checks the import graph, and builds each module in dependency order. Source fingerprints are checked again afterward. Selected sources and additions have separate result fields. An explicit resume records which successful objects came from its authenticated earlier replay.

The axiom audit resolves every requested source-catalogue name to its actual owning module and kernel declaration. Four catalogue entries use private kernel names: two explicitly private `GraphTree` theorems and two named local `SpectralLocalField` instances. They are mapped uniquely within the stated owner using Lean's private-name conversion, and both names are retained in the audit output. The audit then enumerates all logical declarations owned by the audited modules in the imported private kernel environment, including generated and private logical declarations. Each declaration's transitive axiom dependencies must lie within `Classical.choice`, `Quot.sound` and `propext`.

Lean's ownership map also records code-generator auxiliary names that are absent from its kernel constant map. The audit lists these separately. The distinction follows the pinned Lean definitions of `ModuleData.extraConstNames` and `Kernel.Environment.const2ModIdx`. Such names are not counted as logical declarations.

The negative controls confirm that the audit detects both public and private uncatalogued custom axioms in an otherwise safely catalogued module, and that it rejects a missing catalogue name. These isolated control sources are not part of Paper XI.

When explicitly requested, the optional `leanchecker` pass replays each target module's declarations through the official Lean kernel over its imported environment. It is an additional check against manipulated environments. It uses the same Lean kernel implementation, and it does not rebuild imported mathlib declarations. The accompanying release receipts distinguish historical checker runs from the checks freshly performed for this release.

## Scope of interpretation

These checks establish the formal declarations at their stated hypotheses. They do not, by themselves, identify an informal manuscript statement with a Lean declaration. They also do not supply the remaining arithmetic realization and normalization inputs to Conjecture 66 or establish unrestricted local-global correspondence.

The exact release outcome, elapsed times, source and object fingerprints, axiom counts, failure history and preserved logs are recorded in the accompanying verification receipts. Historical checks and this fresh source replay remain separately identified.
