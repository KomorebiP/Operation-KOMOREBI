# Fermat degree-70 Hodge carrier: research checkpoint

Read `PROOF.md` for the statement, geometric proof, classical inputs, and non-claims.

## Replay the exact certificate

From this directory, using Python with SymPy installed:

```text
python verify_certificate.py --out verification.json
```

Expected result: **24 exact checks pass**. This means the finite algebraic certificate passes, not that a proof assistant verified the Hodge-theoretic proof.

The fixed certificate uses no network, floating point, or random sampling. It checks the 24-dimensional rational character orbit, exponent identities, weighted degree, ambient singular-stratum bounds, and an exact radical-gradient-ideal calculation.

`verification.json` contains the recorded successful run. `logs/verification.txt` contains its console output. `MANIFEST.json` records file hashes and proof boundaries.

## Reproduce discovery searches (optional)

These scripts are research search tools, not required for certificate verification. The column LP additionally needs NumPy and SciPy.

```text
python search/carrier_search.py --modulus 70 --character 1 20 24 42 61 62 --out search/reproduced_atomic70.json
python search/carrier_search.py --modulus 33 --character 7 10 13 19 22 28 --out search/reproduced_atomic33.json
python search/general_carrier.py
```

The last command writes `search/general70.json`; preserve the supplied copy before rerunning if retaining discovery provenance matters. Different LP versions may select another optimum. The proof uses the fixed matrix in `verify_certificate.py`, not any optimizer's unverified output.

The degree-33 benchmark search has many labeled candidates. Its included summary omits that large redundant list. Its count is not a count of geometrically distinct varieties.

## Boundaries

The claimed mathematical result is algebraicity of one specified 24-dimensional Fermat packet, and its coordinate-power pullbacks. It is a manuscript-level special-case proof based on established theorems. It has not been independently reviewed, formalized in Lean, or audited for historical novelty.

This is not a proof of the general Hodge conjecture, of every Fermat packet, or of the entire pre-existing Komorebi CM-correspondence program. Equations are provided for the carrier and the monomial map, not for an explicit basis of representing surfaces.
