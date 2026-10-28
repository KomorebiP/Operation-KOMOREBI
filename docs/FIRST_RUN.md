# Run a first example

Choose one of the paths below. Each example has a small, explicit expected
result. Record the source revision with `git rev-parse HEAD` before running it.
All software remains beta and work in progress.

## Komorebi Math on Windows PowerShell

Install Git and a supported Python 3.11, 3.12 or 3.13 interpreter first. The
commands below use Python 3.12 and a new checkout directory.

```powershell
git clone https://github.com/KomorebiP/komorebi-math.git
cd komorebi-math
git rev-parse HEAD
py -3.12 -m venv .venv
$komorebiPython = (Resolve-Path .\.venv\Scripts\python.exe).Path
& $komorebiPython -m pip install .
& $komorebiPython -m pip check
& $komorebiPython examples/first_run.py
```

## Komorebi Math on Linux

From a shell with Git and Python 3.12 available:

```bash
git clone https://github.com/KomorebiP/komorebi-math.git
cd komorebi-math
git rev-parse HEAD
python3.12 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/python -m pip check
.venv/bin/python examples/first_run.py
```

Both routes print:

```text
Numerical reconstruction: [2.0, 3.0]
Exact coordinate change: (7/2, 3)
Exact inverse: (2, 3)
PASS: first examples
```

The first example checks finite projectors and reconstruction with numerical
arithmetic. The second uses exact rational coordinates. Neither establishes a
general theorem about all packet systems. The
[user guide](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md)
explains their assumptions and optional dependencies.

## Polyphase Float on Linux or Windows with WSL

Use a Linux x86-64 environment with LP64 and 64-bit GMP limbs. On Windows,
run these commands inside the Linux/WSL terminal, not PowerShell. Install a
C11 compiler, CMake 3.23 or newer, a build tool and GMP development files using
that Linux distribution's package manager.

```bash
git clone https://github.com/KomorebiP/polyphase-float.git
cd polyphase-float
git rev-parse HEAD
cmake -S . -B build/first-run -DCMAKE_BUILD_TYPE=Release -DPPF_OPENMP=OFF -DPPF_MPFR_SUPPORT=OFF -DPPF_BUILD_EXAMPLES=ON
cmake --build build/first-run --parallel
./build/first-run/example_basic
```

Expected output:

```text
x (256 bits) = 3.10000e1
y (80 bits)  = 3.10000e1
```

Both objects hold the integer 31 exactly at different binary precisions. Read
the [complete example](https://github.com/KomorebiP/polyphase-float/blob/main/examples/basic.c)
for initialization, error handling and cleanup. Follow
[Building](https://github.com/KomorebiP/polyphase-float/blob/main/docs/BUILDING.md)
for installation and use in an application.

## If an example does not run

| Observation | Check |
|---|---|
| Python cannot import the package | Use the same environment's interpreter for pip and the example. Run its `-m pip check`. |
| `py -3.12` is unavailable | Select an installed supported Python minor or install it before creating the environment. |
| GMP cannot be found | Install development headers and the library for the Linux compiler and architecture in use. |
| A command is interpreted as PowerShell syntax | The Polyphase commands belong in a Linux shell. |
| Output differs or an assertion fails | Keep the command, source revision and error output. Check the library's support instructions before relying on the result. |

[Reading routes](READING_ROUTES.md) · [Software guide](LIBRARIES.md) · [Verification](VERIFICATION.md)
