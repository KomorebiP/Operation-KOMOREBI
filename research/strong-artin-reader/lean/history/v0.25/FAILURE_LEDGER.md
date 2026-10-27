# Failure ledger — v0.25

## Environment, not mathematics

1. The initial container command returned a transport timeout. A subsequent command succeeded.
2. Interactive streaming execution was unavailable. All actual builds were run synchronously in bounded batches.
3. Runtime assembly verified all seven part hashes and the combined archive hash. Extraction exceeded its wrapper partway through. A second skip-existing extraction completed. A manifest size check identified one truncated Mathlib Dual/Lemmas.olean; it was extracted again and its SHA-256 matched the shipped manifest.
4. Lake warned about a type change to Batteries docs/README.md in the restored kit. Inspection showed the warning was confined to that documentation path, not Lean source. The pinned mathlib revision matched.

## Rejected development compiles

- ResidualLayer: RingHom.ker was unavailable under the initial imports; Ideal.Maps was added. The initial last-step simplifier also could not unfold the additive map target.
- ResidualLayer: the remaining simplifier failure was repaired by explicitly changing the goal to q(x_i)=0 before rewriting.
- SquareZeroRepresentationDefect: an import path Algebra/Ring/Hom/Basic did not exist in the pinned version. The actual Defs module was used.
- GradedCompatibilityExamples: warnings-as-errors rejected unused simplifier arguments; a residual zero-vector equality required an explicit equality; norm_num did not finish a small ZMod conjunction. The final examples use exact kernel-checked decide proofs where appropriate.

All failed compile outputs and return codes are in verification/development/attempts.jsonl.
No failed draft, timeout or missing output is counted as a checked theorem.

## Mathematical boundaries retained

- A residual syzygy is not an exact nonlinear relation.
- Compatible defects are not automatically in the correction image.
- A root with auxiliary coordinates is not automatically a root after those coordinates are set to zero.
- Exactness of the needed arithmetic complex and existence of the automorphic carrier remain unproved.
