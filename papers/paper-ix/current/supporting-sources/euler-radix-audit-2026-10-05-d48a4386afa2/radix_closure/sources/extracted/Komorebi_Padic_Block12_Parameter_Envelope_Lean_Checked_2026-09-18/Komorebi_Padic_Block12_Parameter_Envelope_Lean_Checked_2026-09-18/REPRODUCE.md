# Reproduce Block 12

## Runtime

Reassemble `Lean_Compact_01.zip` through `Lean_Compact_05.zip` into:

```text
Lean_Portable_Compact.tar.xz
bytes   2220147424
sha256  f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7
```

Extract it and set `KOMOREBI_LEAN_ROOT` to the resulting
`Komorebi_Portable_Lean_4.34.0-rc2` directory.

## Build and verify

```bash
bash "$KOMOREBI_LEAN_ROOT/run.sh" attach "$PWD"
export PATH="$KOMOREBI_LEAN_ROOT/toolchain/bin:$PATH"
rm -rf .lake/build
lake build -KwarningAsError=true
bash verify_all.sh kernel
bash verify_all.sh vectors
bash verify_all.sh finite
bash verify_all.sh controls
bash verify_all.sh release
```

`RejectFalse.lean` and `RejectSorry.lean` are intentional negative controls and
must fail.  A timeout is inconclusive.
