# Quadratic-Form Engine / K-COS Lean companion

This project checks 26 exact finite-real algebra and enclosure/error-budget
theorems, with 8 definitions. It is the scoped formal companion to the final
traditional manuscript and visual guide. Gaussian and spectral reduction,
COS/tilting analysis, remainder bounds, and numerical interval-library
correctness are not formalized by these modules.

Read `Quadratic_Form_KCOS_Lean_Guide.pdf` or its `.md`/`.tex` source for exact
hypotheses and remaining obligations. `Declaration_Inventory.json` lists every
project declaration and signature. `Claim_Lean_Concordance.json` maps only the
proved component of each manuscript claim to its declaration.

On a normal Lean installation, from this directory:

```sh
lake update
lake exe cache get
python3 verify.py
```

The toolchain and Mathlib dependency are pinned. `verify.py` runs the project
build, fresh direct source checks, declaration/axiom audit and positive and
negative compiler controls. It fails if counts, source admissions, axiom sets,
compiler version or Mathlib revision differ from the recorded contract.

The accepted mathematical modules are `KomorebiQCOS/FiniteGram.lean` and
`KomorebiQCOS/Certificates.lean`. `verification/controls/FalseArithmetic.lean`
and `verification/controls/MissingBudget.lean` intentionally fail. Do not import
them into the mathematical library. Their rejection is evidence that a false
arithmetic statement and a missing acceptance premise are not silently proved.

Fresh producer evidence is in `verification/BUILD_AUDIT.json` and companion
logs. `verification/runtime/RUNTIME.md` explains runtime retrieval and the
narrow process-self-location adapter used in this environment. Compiler and
Mathlib binaries are omitted from the publication package.
