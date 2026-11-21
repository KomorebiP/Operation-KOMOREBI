# Reproduce the complete interior order rule

Theorem N in INTERIOR_ORDERS.md gives the minimal eventual recurrence order
for every nonzero a,b,u,v over characteristic-zero fields. Theorem M supplies
the coordinate boundary. Review provenance is project self-review; historical
novelty, independent review and Lean formalization are unassessed.

Extract the current sequence-formula source ZIP and run from its root, with
Python 3.10+ and the standard library:

```sh
python -B tools/verify_sequence_interior_hankel.py --coefficients verification/sequence-library/hankel-compression/interior-coefficients.json --certificate verification/sequence-library/hankel-compression/interior-certificate.json --output interior-orders.json
python -B tools/sequence_hankel_orders.py --coefficients verification/sequence-library/hankel-compression/interior-coefficients.json --t 1 --q 1
```

The classifier's second command returns order 98, root type 1+1+1+1, and
14 distinct bases. Its inputs are normalized t=b/a and q=(v/u)^2; q may be
negative when the original operator is interpreted in a quadratic extension.
For a negative fractional CLI argument, use the equals form, such as
`--q=-16/9`. Zero t or q belongs to the separate boundary theorem.

Compare the replay output with
verification/sequence-library/hankel-compression/interior-replay.json,
ignoring elapsed_seconds. Expected checks include 45 complete characteristic
nodes (765 coefficient comparisons), eight triple-root Bezout identities,
342 complete sample parameter nodes, ten exact GF cross multiplications and
degree-preserving modular witnesses, and 2,732 direct monomial determinants.

The sample reconstruction uses L's all-index order-112 bound, not recurrence
fitting. The 57 squared nodes for each fixed t cover the proved q-degree at
most 56 through W112. The universal classification follows the written
collision and confluent degree arguments together with the coefficient leaves.
The jet regressions use some general quartics outside the mixed family and
do not assert that each of their sample orders occurs in the mixed family.

The coefficient JSON has SHA-256
f25679812778bb91af183241ddc7e957b6b265a5b171906e06c92f2bb70f621f.
The certificate JSON has SHA-256
6b385baf526cfd9ad72b526e15a9f06919ffbb5451147c57d5a1c19b4104030c.
Construction used SymPy 1.14.0; the portable replay and classifier need no SymPy.

The source also includes the Python/browser arithmetic checks:

```sh
python -B -m unittest discover -s tools -p test_sequence_hankel_orders.py -v
node --test tools/test_sequence_hankel_orders.mjs
```

These cross-language checks need Node.js 24. Earlier K/L/M proof sources and reproduction
commands remain unchanged. The preceding 89-member source ZIP is retained in
the repository at research/sequence-closed-forms/retained-sources/sequence-formula-source-5ab2d295.zip,
SHA-256 7c1e373b3dd79aa883c0f4b5ecc6ce3ec14785b7757e471074b99227b228d820.
