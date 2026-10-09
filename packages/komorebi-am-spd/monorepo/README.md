# Operation-KOMOREBI integration files

Copy the files under `monorepo/.github/workflows` to the root `.github/workflows` directory of `KomorebiP/Operation-KOMOREBI`.

GitHub does not execute workflows nested under `packages/komorebi-am-spd/.github/workflows`.

The 1.0.0 CI template tests Python 3.10 through 3.13 on Linux and 3.12/3.13 on Windows, lints public source, runs all package tests, and runs full integration verification. The build template independently installs the wheel outside the checkout, replays a strict paper case, then installs and tests the source distribution. Manual research verification checks the preserved checksum ledger before the historical suites.

These files are templates. Their presence does not establish that the target repository has received them or that its hosted Actions runs have passed.
