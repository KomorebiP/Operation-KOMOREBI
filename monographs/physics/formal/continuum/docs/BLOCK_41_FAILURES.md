# Block 41 failure ledger

1. Two broad predecessor rebuilds exceeded the command-interface window before
   terminal receipts. They were classified as inconclusive. The narrow import
   closure was then built and checked before proof development.
2. The temporary proof workspace reset once. The source checkpoint and all
   portable-runtime parts remained available. The exact pinned runtime and the
   v0.40 project were restored before continuing.
3. Exploratory API probes requested several nonexistent theorem names, including
   guessed `IsBigO` and finite-sum helpers. Those probes failed and supplied no
   proof evidence. The implemented proof uses the actual APIs
   `ContinuousLinearMap.isBigO_comp`, `IsBigO.const_smul_left`, and `IsBigO.sum`.
4. The first Clifford-square proof left powers of the complex imaginary unit
   unreduced. It was repaired by polynomial normalization followed by the exact
   identity `Complex.I_sq`.
5. Early versions of the central-difference phase proof used deprecated rewrite
   patterns and unfolded only one exponential. The proof was rebuilt to unfold
   both phases, apply `Complex.exp_mul_I`, and simplify the removable quotient
   without deprecated declarations.
6. No failed compile, timeout, status poll, or cached object is counted as a
   theorem verification result.
