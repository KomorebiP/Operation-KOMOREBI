# Lean status: NOT COMPILED

Neither `lean` nor `lake` was found in the authoring runtime. A bounded attempt to
retrieve a pinned Lean release / source from the official GitHub locations failed
at DNS resolution. No compiler ran. No Lean pass is claimed.

`lean/ABCJet.lean` contains seven elementary algebraic proof scripts. They are
provided as unverified source for a later Lean environment, not as certified theorems.
The proposed toolchain is pinned to Lean/mathlib v4.19.0. The dependency archive and
compiler binaries are not bundled.

With a functioning Lean environment and network, the intended commands are:

```text
cd formalization/lean
lake update
lake exe cache get
lake build
```

After compilation, record the exact version, source hashes, warnings, and theorem
axiom output. Do not change this status merely because the Python verifier passes.

The general determinant, convergence, valuation-minimality and ABC bridge theorems
are not encoded by these seven scripts. Their present status is written mathematical
proof or explicitly open hypothesis, as stated in the proof files.
