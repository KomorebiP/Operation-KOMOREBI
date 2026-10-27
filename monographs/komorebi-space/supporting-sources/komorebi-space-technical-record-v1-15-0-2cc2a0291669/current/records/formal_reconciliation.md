# Independent formal reconciliation for v1.15.0

Status: **PASS**.

The source tree contains 162 production modules and four import roots, or 166 Lean source targets. The inherited lexical counting convention gives 1,859 explicit theorem/lemma declarations: the predecessor’s 1,846 plus one inexact-rate theorem and 12 range-obstruction theorems.

Exactly 163 inherited Lean files are byte-identical. Only `KomorebiSpaceDiagonal.lean` changed among inherited files, to import the two additions and describe their coverage. No inherited source is removed. The parent tree itself matches the published v1.14.0 ZIP with SHA256 `73e9c5caa36f4ba05029c01481b345ce24cf9b1905dfb012ed21dd4bcfe86dc0`.

The two inherited declaration inventories contain 5,048 and 273 unique names respectively, with no overlap.

The fresh inventory contains **5,339** declarations. It retains 5,321 inherited names and adds 18 names. Metadata differences: 0. Missing names: 0. Unexpected added-module names: 0. Rejected declarations: 0.

The comparison checks exact names and shared module, safety, axiom, and declaration-kind metadata where both historical and fresh schemas provide them. It does not compare historical readable type strings, which the fresh schema does not contain. All replay-snapshot Lean sources also match the current publication tree.

This report reads source bytes and recorded Lean inventory results. It does not independently audit mathematical statements, rerun Lean, validate theorem-map references, or establish that the entire replay has finished. See the separate replay receipt and statement reviews.
