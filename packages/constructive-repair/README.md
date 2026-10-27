# Constructive Repair in Realization Calculus — 1.0.0rc3

**Komorebi P. · Standalone release candidate · 19 October 2026**

An exact rational repair component with independently checkable certificates and Lean proofs. This candidate retains the frozen mathematics and Python algorithms, adds source-bound release checks, and packages the complete current sources and evidence without recursively embedding old release archives. Its release-tested configuration is Linux x86_64 with CPython 3.13.5. It is not a claim that all of Operation Komorebi is at version 1.0.

The component handles freely chosen rational augmentations, weighted candidate menus, and proof-carrying branch search. Its original equations, costs, admissibility rules, and coefficient ring remain fixed throughout certification.

## Start with the standalone Python wheel

From this source archive, install the included wheel without network access or runtime dependencies:

```bash
python -m pip install --no-index --no-deps dist/komorebi_constructive_repair-1.0.0rc3-py3-none-any.whl
komorebi-repair doctor
komorebi-repair solve examples/branch_corpus/Branch018_input.json --output /tmp/repair-example
komorebi-repair check examples/branch_corpus/Branch018_input.json /tmp/repair-example/certificate.json --output /tmp/repair-recheck
```

Each output directory must be new. The commands preserve original inputs, certificates, traces, and final receipts. They do not publish anything. The Python wheel has no third-party runtime dependencies. The source archive, rather than the wheel alone, carries the Lean projects and monograph.

Python checking returns `PYTHON_CERTIFICATE_VALID`, **never** a kernel-checked status. The certificate's `kind` distinguishes an optimal repair from a scoped no-repair result. Malformed data, an invalid certificate, or exhausted work budgets return `UNRESOLVED`. A rejected certificate is not an impossibility theorem.

## Public Python API

```python
from komorebi_repair import ExactMatrix, menu_problem, solve, verify

D = ExactMatrix.of([[1], [0], [0]])
E = ExactMatrix.of([[0, 0], [1, 0], [1, 1]])
R = ExactMatrix.of([[0], [1], [0]])
original = menu_problem(D, E, R, costs=[1, 1])
result = solve(original)
assert result.status == "PYTHON_CERTIFICATE_VALID", result.error
assert result.certificate["cost"] == 2
assert verify(original, result.certificate).status == "PYTHON_CERTIFICATE_VALID"
assert result.kernel_checked is False
```

`fractions.Fraction` supplies fractional entries. Floating-point matrix entries are rejected rather than approximated. For free minimum-dimensional repair use `free_problem(D, R)`. `load(path)` loads a strictly parsed problem. See `docs/PUBLIC_API.md` for the 1.0 candidate compatibility contract.

## Obtain a Lean-checked result

Use the source archive and the existing complete, pinned Linux x86_64 offline kit:

```bash
python scripts/certify_branch.py examples/branch_corpus/Branch018_input.json \
  --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --output /tmp/repair-kernel
```

Supply `--certificate /path/to/certificate.json` to check a previously generated branch certificate instead of rerunning search. `certify_one.py` handles free repair, and `certify_menu.py` handles the small exhaustive reference menus.

These commands compile the actual original input and witnesses, check theorem axioms, replay modules through Lean's own kernel, and compare the Lean-evaluated input with the external original. The compiler and large Mathlib cache are not duplicated in this release. A complete pinned kit is required; this is not a download/install script.

## Mathematical scope

For free repair, the least added dimension equals the span dimension of the residual classes in the original cokernel. The rational implementation constructs explicit matrices and certifies that dimension using exact identities.

For a weighted finite menu, a returned repair is checked in the original target. A proof tree accounts for every potentially cheaper admissible alternative. Rejection concerns only the directions and admissibility rules in the supplied problem. Search and certificate size can still be exponential.

The 51 proof modules and 526 named theorem declarations from v0.5.0 are unchanged. This candidate does not increase the theorem count. The fresh formal receipt is `evidence/verification/current/verification.json`. Counts measure coverage, not novelty.

## Read and reproduce

- `monograph/Constructive_Repair.pdf` and `.tex`: complete monograph with a consolidated current release contract.
- `docs/RELEASE_READINESS.md`: completed gates and remaining conditions before final 1.0.
- `docs/THREAT_MODEL.md`: exact trust boundary and resource assumptions.
- `evidence/rc3/acceptance_run/release_tests.log`: current API, parser, CLI and portability regressions.
- `evidence/rc3/acceptance_run/platform_acceptance/`: clean installed-wheel test receipt and logs.
- `docs/PLATFORM_SUPPORT.md`: explicit tested/untested configurations and local acceptance commands.
- `evidence/release_coordinate_audit.json`: new exact coordinate-invariance comparisons.
- `DEVELOPMENT_HISTORY.md`: retained failures, changes, and next restart point.

```bash
PYTHONPATH=python python -m unittest discover -s tests -v
(cd python && python -m unittest test_certificates test_rational_menu test_branch_menu)
python scripts/verify_release.py --kit /path/to/PINNED_KIT --output /tmp/fresh-full-verification
python scripts/check_manifest.py
```

A fresh full Lean verification must use a new output directory and may take several minutes. The optional `scripts/audit_release_api.py` needs SymPy; the production API and CLI do not.

## Offline platform acceptance

```bash
python scripts/platform_acceptance.py --output /tmp/komorebi-platform-check
```

The output path must be new. The runner installs the bundled wheel into an isolated environment, exercises the installed API and command-line entry point, checks paths with spaces and Unicode, and records actual interpreter/platform details. It makes no network requests and does not label Python checks as Lean proofs. The same runner is provided for Windows/WSL evaluation, but neither platform was executed here.

The default text-encoding defect was reproduced with the POSIX C locale and Python UTF-8 mode disabled. Export now uses explicit UTF-8 for Lean source, documents and logs. That test is not a Windows simulation.

## Check this exact release

```bash
python scripts/release_gate.py
```

The gate checks the extracted manifest, all historical proof snapshots, the current source against the formal-verification receipt, the wheel against the source and installed-acceptance receipt, and the PDF against its build receipt. It reports technical readiness separately from the outstanding license decision. A PASS is not a signature or an independent proof checker.

The package contains every active source, proof, example and retained log needed for its workflows. `provenance/` replaces nested predecessor ZIPs with 121 exact historical proof-source snapshots. See `docs/DISTRIBUTION.md` for what is retained and what is not recursively bundled. No historical whole-archive replay is implied.

## What “release candidate” means

The mathematical and wire protocols are frozen for this component. The final public 1.0 tag still requires the author's explicit code and document licensing choices. Technical support is now defined by `docs/PLATFORM_SUPPORT.md`; untested Windows/WSL and interpreter combinations are not advertised as validated. No license grant has been invented. Do not describe the package as having a particular open-source license until that choice is made.

Direct integration into the main Komorebi Python library and the authoritative Paper III source tree remains a separate adapter task. That does not require changing the foundations or resolving Conjecture 66. No unrestricted integral, nonlinear, or native arithmetic repair is claimed.
