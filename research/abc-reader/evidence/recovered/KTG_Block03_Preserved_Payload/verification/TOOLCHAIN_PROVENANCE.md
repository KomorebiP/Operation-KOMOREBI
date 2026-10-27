# Toolchain Provenance

## Active verified release

```text
lean-toolchain: leanprover/lean4:v4.34.0-rc2
Lean: 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d
Lake: 5.0.0-src+6a10ac8
```

The compiler came from the preserved portable offline archive:

```text
Komorebi_Portable_Lean_4.34.0-rc2_Linux_Offline.tar.zst
SHA-256: 66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34
```

Its seven part archives passed their recorded individual hashes and the combined
archive hash before extraction. The extraction command exceeded its execution
cap, so that command is recorded as an environment timeout rather than as a
completed runtime self-test. The resulting compiler and Lake executable were
usable and the project-specific clean verification completed.

## Historical predecessor environment

The pre-Block-02 source declared `leanprover/lean4:v4.19.0` but had not been
compiler-verified. An exact v4.19.0 executable was not available in the active
offline runtime. Block 02 therefore pinned the compiler actually used for its
clean verification. Block 03 retains that pin and reverified the entire project.
The historical source and original pin remain under
`verification/predecessor_uncompiled/`.
