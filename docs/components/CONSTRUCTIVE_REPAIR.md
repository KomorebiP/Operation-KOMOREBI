# Constructive Repair: package and verification guide

**1.0.0rc3 · Beta / work in progress · Updated 27 October 2026**

[Source and original release records](../../packages/constructive-repair/) · [Public API](../../packages/constructive-repair/docs/PUBLIC_API.md) · [Windows evidence](../../verification/constructive-repair/windows-2026-10-27/summary.json)

Constructive Repair provides exact rational repair certificates, a Python API and CLI, and separately recorded Lean proofs. **Python certificate validity and Lean kernel acceptance are separate results.** The current completion label remains **Active development**.

## Fresh Windows check

The following checks used the committed source at [ef52463dbe47](https://github.com/KomorebiP/Operation-KOMOREBI/commit/ef52463dbe476bcf0c027ed00c68c6d6fb2fdfb3), Windows 11 on AMD64, and CPython 3.12.14. All **2,254 selected source files** matched their SHA-256 import receipt before the run and remained unchanged afterward. Work ran in a separate copy.

| Check | Observed result | Scope |
|---|---|---|
| Offline wheel build | Passed | Local setuptools 84.1.0 and wheel 0.48.0. No dependency download. |
| Wheel/source correspondence | Passed, 7 runtime Python files | Every runtime member matches its committed source bytes. |
| Engine regression suite | 134 passed | Existing certificate, rational-menu and branch-menu tests. |
| Release regression suite | 95 passed, 3 skipped, 2 errors out of 100 discovered | The two errors occurred during symlink fixture creation, before the checker assertions. The three skips are explicitly POSIX/Linux-specific. **This suite did not pass.** |
| Isolated installed-wheel acceptance | Passed, 72 cases / 369 probe checks / 20 platform checks | Offline installation, API and CLI use, fresh solutions and retained certificates, Unicode paths, overwrite prevention, resource limits, and rejection of malformed inputs and corrupt certificates. |
| New Lean replay | Not run | Existing compiler and proof records retain their original scope and date. |

Both release-test errors were `WinError 1314`: the executing Windows account could not create a symlink. They occurred in `PathsAndBindings.test_symlink_rejected` and `WheelBinding.test_symlink_wheel`. These are unresolved fixture prerequisites, not successful negative controls or demonstrated checker failures. The tests were not rewritten or converted into passing skips.

The overall result is **partial Python qualification**. It does not establish complete Windows release acceptance, support for other interpreters or platforms, or new mathematical proof coverage.

## Which wheel was checked

The wheel was rebuilt from the published sources because the browsable source import omits nested distribution archives. Its SHA-256 is:

```text
bc9e2916519ebc9e37096e2b39fedf3c949cbc19562e3d59b57d31360cddc419
```

It is not byte-identical to the wheel named in the historical Linux acceptance record. The [source-to-wheel map](../../verification/constructive-repair/windows-2026-10-27/wheel-source-binding.json) records both hashes, build-tool versions, and the exact seven runtime members. The new Windows receipt applies to this rebuilt wheel. It does not replace the historical receipt.

The [evidence directory](../../verification/constructive-repair/windows-2026-10-27/) retains the build, engine, release-test, and installed-workflow logs. Published receipts replace local workspace/interpreter paths with placeholders and normalize line endings to LF. Counts, outcomes, errors, timings, platform details, and content hashes are preserved. The summary records this transformation.

## Reproduce in a new copy

Use the Python interpreter being evaluated, a fresh output directory, and a disposable copy of the source component. Local setuptools 77 or later is needed for the existing build script. Record the actual build-tool versions and wheel hash.

```text
python -B scripts/build_wheel.py
python -B -m unittest discover -s tests -v
python -B -m unittest discover -s python -p "test_*.py"
python -B scripts/platform_acceptance.py --output <new-output-directory>
```

Run the engine command with the component's `python` directory on the import path, or run the three named engine modules from that directory as in the retained command record. Use a writable temporary directory. The acceptance runner creates its own isolated environment and installs the local wheel with `--no-index --no-deps`.

The original archive-wide `release_gate.py` expects the original complete distribution, wheel, and sealed manifest. A source-only checkout or a new wheel requires its own distribution and evidence binding. Adding a rebuilt wheel does not make the old artifact gate pass.

## Remaining finalization work

F08 remains open. Re-run the two symlink controls where their fixtures can be created, complete an artifact-release gate for the intended distribution and current metadata, and retain the exact source/wheel/receipt relationship. Any fresh Lean verification uses the separately pinned runtime and must produce its own receipt.

The [current collection reuse terms](../../LICENSE.md) apply to covered original work and explain the retained historical undecided-license notices. The original package's `PUBLICATION_DECISION.json` and old no-publication statements remain dated records. They do not describe today's GitHub availability. All executable software remains beta / work in progress.

[Completion record](../STATUS_CATALOG.md#constructive-repair) · [Finalization queue](../FINALIZATION_QUEUE.md) · [Repository audit](../AUDIT_2026-10-27.md)
