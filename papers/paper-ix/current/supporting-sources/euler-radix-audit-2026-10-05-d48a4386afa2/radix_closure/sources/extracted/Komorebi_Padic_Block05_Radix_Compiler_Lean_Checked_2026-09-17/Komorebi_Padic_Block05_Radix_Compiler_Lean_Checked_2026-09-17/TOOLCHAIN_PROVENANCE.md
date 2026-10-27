# Toolchain provenance

## Checked runtime

```text
Lean 4.34.0-rc2
Lean commit 6a10ac8c22beadecabdbb0919c2b50214762f91d
Lake 5.0.0-src+6a10ac8
architecture x86_64-unknown-linux-gnu
```

## Checked package revisions

The exact revisions are recorded in `lake-manifest.json`. The load-bearing
revision is:

```text
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06
```

The inherited exact revisions for Batteries, Aesop, Qq, ProofWidgets,
ImportGraph, LeanSearchClient, Plausible, and Cli remain in the manifest.

## Runtime reconstruction

The runtime was reconstructed from five preserved ZIP parts. The concatenated
XZ archive was 2,220,147,424 bytes with SHA-256

```text
f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7
```

`xz -t` passed. A fresh extraction contained 8,484 cached mathlib `.olean`
files before the project was attached.

## Stable compatibility boundary

This provenance does not establish compatibility with stable Lean 4.34.0 or
mathlib commit `5ed2965256430c3649e86755f9576b54eca72435`.
