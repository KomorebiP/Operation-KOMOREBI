# Constructive Repair — qualified beta distribution

**Komorebi P. · Python package 1.0.0rc3 · Beta / work in progress**

Constructive Repair computes exact rational repair certificates through a Python API and command-line interface. Python verifies certificates against the original input. The source also includes separately recorded Lean developments and the monograph.

This distribution keeps the imported component in `source/` and builds its seven runtime files with current release and license metadata. `qualification.json` identifies the source revision, wheel hash, platform, commands, and actual results. The release workflow publishes a qualified beta only after both required platform runs and the final distribution gate pass.

## Install and run

Download a qualified source archive or the standalone wheel from the [GitHub releases](https://github.com/KomorebiP/Operation-KOMOREBI/releases). The wheel has no third-party runtime dependencies. Each source archive includes that same wheel, the complete imported source, current license notices, qualification receipts, and a verifier.

From an extracted archive, verify it before creating any local files:

```text
python -B tools/constructive_repair_release.py verify --root .
```

On Linux, create an environment beside the archive and install offline:

```bash
python -m venv ../repair-env
../repair-env/bin/python -m pip install --no-index --no-deps dist/komorebi_constructive_repair-1.0.0rc3-py3-none-any.whl
../repair-env/bin/python -I -m komorebi_repair doctor
../repair-env/bin/python -I -m komorebi_repair solve source/examples/branch_corpus/Branch018_input.json --output ../repair-solution
```

On Windows PowerShell:

```powershell
python -m venv ..\repair-env
..\repair-env\Scripts\python.exe -m pip install --no-index --no-deps dist/komorebi_constructive_repair-1.0.0rc3-py3-none-any.whl
..\repair-env\Scripts\python.exe -I -m komorebi_repair doctor
..\repair-env\Scripts\python.exe -I -m komorebi_repair solve source/examples/branch_corpus/Branch018_input.json --output ..\repair-solution
```

Choose new environment and result directories. Keep them outside the extracted archive so its file inventory remains verifiable. A successful solve reports `PYTHON_CERTIFICATE_VALID`; `kernel_checked` remains `false`. Inputs, certificates, traces, and receipts are retained in the result directory. The original source's `docs/PUBLIC_API.md` documents the API and certificate scope.

## Qualification contract

| Gate | Required result |
|---|---|
| Imported source | All 2,254 files match the recorded source hashes. |
| Linux x86_64 / CPython 3.13.5 | All 100 release tests, 134 engine tests, and 72 installed acceptance cases pass. |
| Windows x86_64 / CPython 3.13.5 | 97 release tests pass, with only the three named POSIX-specific tests skipped; 134 engine tests and 72 installed cases pass. |
| Symlink rejection controls | Both controls execute and pass on both platforms. |
| Wheel/source binding | Every one of the seven runtime files matches the imported source. |
| Current metadata | The wheel includes this README, the MIT code license, and the collection reuse notice. |
| Platform agreement | Both platforms install and accept byte-identical wheels. |
| Distribution integrity | Both source archives pass full file, checksum, source, wheel, and acceptance-binding checks. |

The checks cover exact rational arithmetic, certificate rejection, malformed inputs, work budgets, command-line use, Unicode paths, overwrite prevention, and isolated offline installation. Receipts state the executed configurations. Other interpreter/platform combinations retain their own qualification requirements.

The qualifier checks the historical proof-source, axiom-record, lineage, and monograph bindings. It performs no new Lean execution. Fresh kernel certification uses the original source scripts and their pinned Lean/Mathlib kit; the compiler and dependency cache are separate.

## Source and build metadata

`SOURCE_IMPORT.json` binds every file under `source/` to its original import. `SOURCE_REVISION` identifies the collection revision used. The original component files, including historical publication notices and evidence, retain their bytes.

The build copies the component to a fresh working directory. Its metadata overlay selects this README and the current licenses; `build-inputs/pyproject.toml` records that overlay. The runtime version and algorithms remain 1.0.0rc3. Wheel metadata line endings, ZIP timestamps, modes, ordering, and RECORD ordering are normalized for a cross-platform byte comparison. The runtime bytes and wheel RECORD hashes are then checked directly.

`MANIFEST.json` and `SHA256SUMS.txt` cover the complete distribution. Published evidence replaces local root/interpreter paths with placeholders and normalizes UTF-8 text line endings to LF. Other evidence bytes and outcomes are retained. Checksums establish consistency with the supplied records.

## Reproduce qualification

Build reproduction needs local `setuptools==84.1.0` and `wheel==0.48.0`. Install those tools in a separate environment before the offline qualification run:

```text
python -m pip install setuptools==84.1.0 wheel==0.48.0
python -B tools/constructive_repair_release.py qualify --root . --output ../fresh-repair-qualification
```

Use the interpreter/platform being evaluated and a new output directory. The runner supplies a canonical temporary directory so Windows path checks do not compare long names with short-name aliases. The qualification runner makes no network requests. The original installed-wheel acceptance runner creates its own environment and installs with `--no-index --no-deps`. A machine that cannot create the symlink fixtures reports failure; the controls are not converted into passing skips.

For a source checkout, use the same command from the collection root with `--revision` set to its exact Git commit. `--build-only` prepares and checks a wheel without reporting acceptance or producing qualified release assets.

## Reuse and attribution

Original software is covered by the MIT license in `LICENSE-CODE.txt`. `LICENSE-COLLECTION.md` gives the collection's current grants for original documents and other material, explains superseded original-author notices, and preserves third-party terms. Attribute the work to **Komorebi P.**
