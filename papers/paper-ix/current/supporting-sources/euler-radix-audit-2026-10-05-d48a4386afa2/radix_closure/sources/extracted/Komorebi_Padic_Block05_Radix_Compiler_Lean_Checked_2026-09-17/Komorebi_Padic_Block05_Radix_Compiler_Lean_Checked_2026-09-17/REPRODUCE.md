# Reproduce Block 05

## Online toolchain route

Install the exact toolchain named in `lean-toolchain`, then from this directory
run:

```bash
lake update
lake build -KwarningAsError=true
lake env lean -DwarningAsError=true verification/LeanCompilerVector.lean
lake env lean -DwarningAsError=true verification/AxiomAudit.lean
python verification/verify_radix_compiler.py
```

The manifest pins the checked mathlib and inherited package revisions.

## Preserved offline runtime route

The checked run used these Library parts:

```text
Lean_Compact_01.zip
Lean_Compact_02.zip
Lean_Compact_03.zip
Lean_Compact_04.zip
Lean_Compact_05.zip
```

Each ZIP contains one sequential chunk. Concatenating the chunks produces
`Lean_Portable_Compact.tar.xz` with

```text
bytes   2220147424
sha256  f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7
```

Verify with `xz -t`, extract, then run the runtime's `attach` command on this
Block 05 directory before invoking Lake.

## One-command project verification

On a machine where the exact Lean environment is active:

```bash
bash verify_all.sh
```

The intentionally failing files `verification/RejectFalse.lean` and
`verification/RejectSorry.lean` are negative controls. `verify_all.sh` expects
both to fail.
