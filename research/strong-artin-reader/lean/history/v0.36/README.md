# Strong Artin Lean v0.36 — Resonant Branch Compactness

Author: Komorebi P.

Exact parent: `Strong_Artin_Lean_v0.35.0_Compatible_Frobenius_Tower_Checked.zip`

Parent SHA-256: `7cd9bec32dec158198b1f79db55d3151b6abe3724eca9fa10fed33b30866452f`

## Main result

For every prime p, finite matrix index type, degree d, prescribed p-adic unit U,
and fixed unit a modulo p^m (m >= 1), an actual p-adic root F with F^d = U and
F = a modulo p^m exists if and only if there is a root above a at every deeper
finite level. Those finite roots need not be chosen compatibly. No residual
norm invertibility, diagonalizability, nilpotence of the adjoint, or degree
restriction is assumed.

The same compactness argument applies to a finite simultaneous family of
prescribed powers up to local conjugacy. It constructs one shared p-adic
Frobenius and one constant p-adic conjugator per prescription, each reducing to
identity modulo p. Compatible conjugator towers are not assumed.

If a fixed root prefix has no p-adic continuation, some finite deeper level has
no extension of that prefix. There is a first such level. At a fixed prefix
level the set of surviving prefixes is detected at some finite horizon, but
this theorem is NON-EFFECTIVE: no numerical horizon bound or decision algorithm
for general p-adic inputs is supplied.

## Indexing and coefficients

Inherited Lean level r is ZMod(p^(r+1)). Thus the displayed mathematical prefix
exponent m is Lean index k+1. Matrix roots are actual units over Mathlib PadicInt.
The new arbitrary-level maps are proved equal to the inherited adjacent maps,
and the inherited unit limit assembles matrices AND their inverses.

## Evidence

31 theorem declarations, 11 definitions, 1 structure, 6 new modules (520 lines).
27 unchanged inherited source modules form the direct dependency closure.
All 43 explicitly named new constants are axiom-audited. Helpers and examples
are included in these counts; constructor-generated fields are not counted.

Run the fresh verifier:

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

For bounded batches use `--max-modules 8`, then `--resume --max-modules 8`.
A batch returning PARTIAL is not a completed verification.

Run the independent finite checks:

```bash
python3 checks/exact_branches.py
```

See RESULT.json, PROOF_LEDGER.md, RESEARCH_BOUNDARY.md, and SELF_REVIEW.md.
No Strong Artin, automorphic-carrier, arithmetic Selmer, or historical novelty
claim is made. The compactness mechanism is classical Koenig's lemma.
