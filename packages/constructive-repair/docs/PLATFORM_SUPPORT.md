# Declared platform support — 1.0.0rc3

## Release-tested configuration

The scope of this candidate is **Linux x86_64 with CPython 3.13.5**. The fresh host is Linux 6.18.55 with glibc 2.41. The isolated wheel installation uses only Python's standard library and the locally bundled wheel. Lean certification additionally requires the existing Linux x86_64 Lean 4.34.0-rc2 kit and Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

| Configuration | Status |
|---|---|
| Linux x86_64 / CPython 3.13.5 / isolated installed wheel | Release acceptance executed here |
| Same interpreter, POSIX C locale, UTF-8 mode disabled | Encoding regression executed here |
| Same interpreter, directories and filenames containing spaces and Unicode | Installed workflow executed here |
| Native Windows Python | Not executed; acceptance runner provided |
| WSL Linux | Not executed; acceptance runner provided |
| CPython 3.10, 3.11, 3.12, 3.14 | Not runtime-tested in this pass |
| macOS, ARM, PyPy, free-threaded CPython | Not tested |

The precise results, executable paths, versions, wheel hash, and commands are in `evidence/rc3/acceptance_run/platform_acceptance/`. No test row should be interpreted as a broader platform certification. A POSIX C-locale test does not simulate Windows.

The source and package metadata retain their Python 3.10+ syntax/installation target for compatibility. That is not a tested-support claim. The executable-support promise for this candidate is deliberately limited to the configuration above. No previous certificate schema changed.

## Why other Python versions are untested

The earlier rc2 local `uv python install 3.10 3.11 3.12 3.14` attempt could not resolve its download host. The retained log records each failure. Those interpreters were not installed or run. The normal package and acceptance runner do not need network access. Interpreter acquisition was an environment-setup attempt, not part of the offline release workflow.

## Run acceptance on another machine

From the extracted source directory, run the following using the interpreter to be evaluated:

```bash
python scripts/platform_acceptance.py --output /tmp/komorebi-platform-check
```

On native Windows, a corresponding command is:

```powershell
py -3.13 scripts/platform_acceptance.py --output ".\komorebi-platform-check"
```

This is an unexecuted Windows command example, not a Windows PASS. The runner creates an isolated environment under the new output directory, installs the included wheel with `--no-index --no-deps`, checks all 72 archived input/certificate pairs through the installed API, generates new answers, exercises the CLI, and preserves a machine-readable receipt. It does not change an existing output directory. Each interpreter requires its own new directory.

The report records the actual platform. It never infers support from the wheel tag. The receipt is Python acceptance evidence only; the separate source scripts perform Lean checking. Run those Linux-kit scripts inside a tested compatible Linux environment rather than treating native Windows Python as able to execute the Linux compiler.

If `venv` or its local pip bootstrap is unavailable, acceptance reports failure. It does not download missing packages, modify the system interpreter, or silently skip clean installation.
