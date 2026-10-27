# Dyadic Euler Tail Root Laws — v4

**Current proof:** `COMPLETION_04.md`.

This release continues the mounted v3 archive. Earlier notes and logs are preserved as historical material. Where statements about sharp root-emergence thresholds differ, use the v4 theorem and status boundaries.

## What is completed

The five-root wall is fully classified, with root counts **0, 0, 2, 3, 3, 5** at distances one through six. A general necessary-and-sufficient theorem covers every regular wall, including every power-of-two skeleton. The first irregular wall, j=17, is certified at its finite exceptional distances; a general separation theorem handles all larger distances. All shifted-wall labels j<=32 are consequently covered at every valid scale, including pre-wall and equality scales.

Every arbitrary first omitted depth r has an exact finite-polynomial reduction of degree at most floor((s_2(r)-1)/3). This is not an explicit root classification for all arbitrary r, and the code does not pretend to settle a multiple root from an unresolved finite-precision branch.

No Lean checking or historical priority review is claimed.

## Files to use

| File | Role |
|---|---|
| `COMPLETION_04.md` | Definitions, complete proofs, exact cases, error bounds, sources |
| `dyadic_modular.py` | Exact modular Bernoulli/source/tail computation and constructive polynomial preparation |
| `check_completion_v4.py` | Fresh bounded audit and whole-ball certificates |
| `check_wall_boundary_v4.py` | Equality-scale and pre-wall closure checks |
| `RESULTS_COMPLETION_04.json` | Retained results, leaf addresses, reductions, roots and precisions |
| `MANIFEST_COMPLETION_04.json` | Run metadata, tested bounds, input/output hashes |
| `MANIFEST_VALIDATION_04.txt` | Schema validation and explicit input/output hash checks |
| `inspect_tail.py` | Command-line inspection and exact finite-precision tail valuations |
| `CLAIMS_V4.json` | Claim-by-claim status and remaining boundary |
| `DEVELOPMENT_NOTES_04.md` | Corrections, provenance limits, and environment observations |
| `verify_bundle.py` | Check the retained release hashes before rerunning experiments |

`PROOF.md`, `CONTINUATION_02.md`, `CONTINUATION_03.md` and their scripts/logs are the retained prior work. They have not all been rerun as part of the v4 audit. The new audit independently reconstructs small exact coefficients and Euler rows, and tests both the factorized and original tail formulas.

## Reproduce

Tested with Python 3.13.5. The scientific checker uses only the Python standard library. Run these commands from the extracted `dyadic_tail_root_audit` directory:

```text
python verify_bundle.py
python check_completion_v4.py
python check_wall_boundary_v4.py
python support/validate_manifest.py MANIFEST_COMPLETION_04.json --root .
python inspect_tail.py --wall 5 --delta 6 --precision 32 --offset 8
```

The checker regenerates `RESULTS_COMPLETION_04.json` and the run manifest. Runtime and timestamp metadata will change, so validate the retained bundle hashes **before** rerunning the audit. The original `SHA256SUMS.json` authenticates the retained snapshot, not the subsequently regenerated run.

To inspect a general depth:

```text
python inspect_tail.py --r 510 --precision 32
```

Conventions: the target Euler number is E_(2N), r=M+1 is the first omitted depth, and an offset is x=N-r. Root residues are finite approximations to dyadic roots, not rational claims. A zero modulo 2^P is a valuation lower bound, not a proof of exact zero.

## Audit interpretation

The retained v4 audit finished successfully in approximately 10.3 seconds in the provided environment. Its result counts are written in the JSON. A successful execution is evidence about the implementation and its stated finite assertions. Universal conclusions rely on the proofs and coefficientwise error bounds in the note.

A leaf certificate has one of the forms 2^(-c) G(s+2^k Y) = 1 mod 2, or Y+epsilon mod 2, coefficientwise. The first proves a constant valuation on the whole ball. The second proves a unique simple root and an exact root-distance valuation law on the whole ball. Unresolved precision or depth is reported explicitly.
