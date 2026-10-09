# Installing AM-SPD 1.0.0 offline

The AM-SPD wheel is pure Python. NumPy, SciPy, OpenCV, scikit-image, Pillow, and Matplotlib include platform-specific dependencies. A wheelhouse must match the destination operating system, architecture, and Python version. The main source release does not assume these packages are already installed.

## Windows Python 3.13 bundle

The separate Windows offline bundle contains a `win_amd64` CPython 3.13 wheelhouse and the installer below. Extract it, then run:

```powershell
.\scripts\install_offline.ps1
```

The script creates an isolated `.venv`, installs wheels with `--no-index` and the included release-lock constraints, and runs full package verification. No environment activation is required. Native failures stop the script. Windows binaries and PowerShell execution cannot be tested on the Linux release host. The included wheel inventory records what was downloaded; execute verification on your laptop before treating Windows runtime compatibility as established.

## Preparing another wheelhouse

While connected to the internet, from the source package directory:

```powershell
python scripts\prepare_offline.py `
  --wheel dist\komorebi_am_spd-1.0.0-py3-none-any.whl `
  --output wheelhouse
```

This downloads wheels for the current interpreter and platform. To target 64-bit Windows Python 3.13 explicitly:

```powershell
python scripts\prepare_offline.py `
  --wheel dist\komorebi_am_spd-1.0.0-py3-none-any.whl `
  --output wheelhouse `
  --platform win_amd64 --python-version 3.13 --abi cp313 `
  --lock requirements-release-lock.txt
```

The exact release lock records the tested Linux numerical-library versions. It is an environment record, not a promise that the same pins support every declared Python version. For Python 3.10, omit that lock so pip can resolve compatible releases within the package bounds; verify the resulting environment independently.

Copy the completed wheelhouse, installer, and `requirements-release-lock.txt` to the disconnected machine. The supplied installers use the release lock. For a differently resolved Python version, replace that constraint file with the independently verified environment pins before installing. Linux/macOS hosts can use `bash scripts/install_offline.sh /absolute/path/to/wheelhouse /absolute/path/to/environment` with a wheelhouse prepared on that platform.

Standard installation also remains available with `python -m pip install dist/komorebi_am_spd-1.0.0-py3-none-any.whl` when network access is permitted.
