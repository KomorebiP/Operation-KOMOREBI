# Restoring the runtime used for this check

The compiler was restored from existing Library artifacts:

    Lean_Compact_01.zip
    Lean_Compact_02.zip
    Lean_Compact_03.zip
    Lean_Compact_04.zip
    Lean_Compact_05.zip

Each ZIP contains one numbered `.chunk`. Concatenate the extracted chunks in
numeric order into an XZ archive, then extract the archive into a clean directory.
The assembled archive used for this release has SHA-256:

    f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7

Its top directory is `Komorebi_Portable_Lean_4.34.0-rc2`.
The executable is `toolchain/bin/lean`. The matching Mathlib workspace is
`workspace`, with revision:

    aeb72f1e9981b6d35b426b16dca7759be3e7ba06

The compiler reported:

    Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu,
    commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)

This compact five part archive is not byte identical to the older seven part
`Lean_Offline` archive. Their assembly hashes must not be interchanged.

The runtime is an external dependency and is not bundled again in this release.
The project does not modify its files or download replacement dependencies.
