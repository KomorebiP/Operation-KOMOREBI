# Reproducing Quantum and Circuits

Run these commands from the extracted release root. Keep `release_tools/`,
`sources/`, `volume/`, and `verification/` together. Commands locate source
projects relative to the wrapper, so the release may be moved without editing
absolute paths.

## Formal replay

Use Python 3.10 or later and the separately stored offline
`Komorebi_Portable_Lean_4.34.0-rc2` kit. The kit requires Linux x86_64, including
a compatible WSL2 distribution. It is not a native Windows or macOS runtime.
Git must be installed for dependency revision checks. Allow sufficient free
space for the full runtime, dependency cache, and new build directories.

The pins are:

| Component | Required revision |
| --- | --- |
| Lean / Lake | `leanprover/lean4:v4.34.0-rc2` |
| Lean commit | `6a10ac8c22beadecabdbb0919c2b50214762f91d` |
| Quantum mathlib | `aeb72f1e9981b6d35b426b16dca7759be3e7ba06` |
| Other quantum dependencies | Exact revisions in the supplied `lake-manifest.json` |
| Circuit dependencies | The pinned toolchain's bundled Std; no mathlib |

Inspect the commands without installing or starting Lean:

```sh
python3 release_tools/replay_formal.py \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --out replay/new-run --dry-run
```

Remove `--dry-run` to execute. The output directory must not already exist.
The wrapper runs each original verifier with its existing flags, writes
separate console logs, and checks the resulting JSON receipt and process exit
status. It performs no downloads. A failing command or receipt produces a
failure exit status. The original verifiers enforce their own per-command
timeouts and proof checks.

The quantum project writes `quantum/REPORT.json`; the circuit project writes
`circuits/verification.json`. `replay_summary.json` records the overall result,
verifier hashes, commands, and receipt hashes. A successful wrapper replay is
evidence for the named formal subsets, not every written theorem in the volume.

On the specific hosted Linux environment that reports **failed to locate
application**, explicitly add `--compat-shim` and use a new output directory.
This loads the existing kit's `compat/app_path.so` through a private temporary
path. The adapter corrects executable-path discovery; it does not alter proof
rules. It is never automatically enabled by this wrapper. The original kit
README and adapter source explain its narrow purpose.

## Counts and supplementary control

The maintained formal counts are **96 quantum declarations and 115 circuit
declarations**. These include supporting lemmas and do not count independent
discoveries. The circuit subset covers C01, the sharing-aware degree dependency,
and the numerical C02 bound. Its other written claims retain their documented
proof status.

`verification/quantum_fresh_20261026/SUPPLEMENTAL_MODE_ONE.json` records a
separate control that proves the first Fourier mode equals twelve and therefore
is not zero, then rejects an explicitly rewritten false equality. Its two
helper lemmas are **not added to the 96-declaration count**. They strengthen the
interpretation of the original false-mode control, whose rejection involved
opaque-decision reduction. The supplementary source and logs are retained;
`replay_formal.py` runs the original project suites and does not automatically
repeat this supplementary experiment.

## Exact computations and documents

The circuit scientific replay uses Python 3.10+ and a C++17 compiler, without
external Python packages or network access:

```sh
cd sources/circuits/Komorebi_Circuit_Obstructions_Research_Edition_1.0/source/komorebi-circuit-obstructions-v1.2.0
python3 scripts/check_integrity.py
python3 scripts/verify.py --all
```

Component READMEs specify their other bounded computational commands and
requirements. Scientific figure generation uses NumPy and Matplotlib; consult
each component's requirements file before rebuilding figures. Finite checks
retain their declared domains and do not replace universal proofs.

To compile the supplied final volume, use XeLaTeX with the packages listed in
`volume/preamble.tex`, Latin Modern Roman and Sans, and DejaVu Sans Mono:

```sh
cd volume
xelatex -interaction=nonstopmode -halt-on-error volume.tex
xelatex -interaction=nonstopmode -halt-on-error volume.tex
xelatex -interaction=nonstopmode -halt-on-error volume.tex
```

Compile the supplied final TeX files directly. Consolidation scripts document
the source lineage; rerunning them may regenerate editorial material. PDF
compilation is separate from Lean verification. Poppler supports visual review.

## Wrapper validation

This release's new wrapper was checked with `--help` and both forms of
`--dry-run`. Those checks executed no Lean process and make no additional proof
claim. The preserved formal receipts record the actual earlier source builds,
axiom audits, kernel replays, and rejected controls.
