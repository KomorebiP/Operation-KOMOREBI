# Continue from v0.27 Continuous Obstruction / Finite-Quotient Vanishing

Read README.md, RESEARCH_BOUNDARY.md, PROOF_LEDGER.md, and FAILURE_LEDGER.md before continuing. Preserve this branch's exact v0.26 base checksum. Do not merge similarly numbered sibling releases by filename alone.

## Strongest endpoint

A compact source and discrete residual coefficients give a finite actual residual image. If its order is invertible in the upper square-zero coefficient ring, a continuous representation lift exists through that same image, with unchanged kernel. This is proved vanishing, not a vanishing assumption.

A continuous cochain obstruction is also constructed for arbitrary topological-group sources and discrete coefficients, with an exact criterion for continuous absolute lifting and strict prescribed-clopen-subgroup lifting. The explicit continuous cochain definition is not silently equated with the separate `continuousCohomology 2` library functor.

## Next target contract

The next arithmetic claim must specify:

- the number field or concrete profinite group and the exact residual representation;
- the actual square-zero coefficient extension and kernel module;
- local conditions, which subgroup maps are fixed, and whether fixing is literal or up to conjugacy;
- the continuous relative/Selmer complex and the distinguished class;
- the new mathematical reason that this particular class vanishes.

Do not propose universal vanishing: the nonzero controls rule it out. Do not reuse finite-image averaging at a coefficient prime dividing that image order. Do not infer arbitrary prescribed local liftability from absolute vanishing.

If pursuing a finite-tower theorem in the order-invertible sector, keep the same quotient at every level and prove compatibility explicitly. That is a separate internal theorem, not a new automorphic carrier theorem.

## Verification

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

For bounded batches use `--max-modules 8`, then `--resume`. Only final PASS with all module return codes zero and all expected axiom reports counts as a full direct-closure replay. Reused Mathlib compiled artifacts are a declared dependency.
