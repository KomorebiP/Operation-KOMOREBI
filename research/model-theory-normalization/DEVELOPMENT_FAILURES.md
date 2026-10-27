# Development failures — v0.10

Seventeen module development commands were retained: ten successful and seven
failed attempts. None of those failed attempts counts as the completed cold audit.
The final cold run is separate and all of its expected outcomes passed.

| Failed source | Failure and repair |
|---|---|
| BinaryWords | Unused simp argument, mismatched simplification in carry reasoning, nonexistent list API. Replaced with explicit case splits and preserved bit equalities. |
| BinaryMulDiv, first attempt | Wrong Boolean lemma name and nonlinear goal sent to a linear arithmetic tactic. Corrected simplification and polynomial bounds. |
| BinaryMulDiv, second attempt | A split was attempted before exposing the let-bound conditional. Unfolded the concrete division stage. |
| BinarySigned | Sign/value expressions overexpanded before the difference lemma and division cast mismatches. Applied the value identity at the correct abstraction level. |
| BinaryEncoding | Strict lint warnings and a residue coercion/option simplification. Removed unused tactics and supplied the exact nonzero/negative branch premises. |
| BinaryCosted | Well-founded definition was not definitionally reduced by rfl; division padding lengths were not exposed. Used explicit recursion equations and length lemmas. |
| BinaryBackend | Simplification retained false=true in the carry literal. Used the Boolean simplifier before the residue equality. |

Every diagnostic log and attempted source hash is retained in evidence/. Failed
source snapshots were not retained, so those failed drafts are not claimed fully
replayable from hashes alone. Accepted sources and the cold run are replayable.

Runtime setup first attempted an unsupported interactive session, then launched a
restore script that had not been created by that rejected command. The script was
created explicitly and its subsequent streaming XZ extraction completed. The
five consumed temporary chunk ZIPs were removed after their hashes were recorded
to avoid exhausting disk space. This removed working copies only, not Library
files. Runtime and upstream cache bytes are not redistributed.

No mathematical counterexample to the stated final scalar theorems was found.
The remaining whole-program lowering gap is a scope limitation, not a successful
claim hidden behind a finite test.
