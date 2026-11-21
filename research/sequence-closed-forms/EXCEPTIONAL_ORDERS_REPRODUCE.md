# Reproduce the coordinate-boundary classification

Theorem M classifies the minimal eventual scalar constant-coefficient orders
for P(m)=a+bm and D=u+v*partial_x on the entire coordinate boundary abuv=0,
over characteristic-zero fields. The proof is EXCEPTIONAL_ORDERS.md; review
provenance and proof obligations are in EXCEPTIONAL_ORDERS_REVIEW.md.

Download and extract the current sequence-formula source ZIP. From its root,
run with Python 3.10+ and the standard library:

```sh
python -B tools/verify_sequence_sharp_quadratic.py --output sharp-quadratic.json
python -B tools/verify_sequence_uniform_mixed.py --sample-certificate verification/sequence-library/hankel-compression/mixed-certificate.json --output uniform-mixed.json
python -B tools/verify_sequence_exceptional_hankel.py --certificate verification/sequence-library/hankel-compression/exceptional-certificate.json --output exceptional-orders.json
```

The first two commands replay the parent formal-moment identities and generic
mixed theorem. The third uses separate sparse rational polynomial code to
check all ten initial-boundary identities, four complete parameter-polynomial
numerators at 75 degree-complete nodes (1,572 coefficient checks), four cleared
Bezout identities, nine exact critical reductions and their coprimality
witnesses, 947 direct monomial determinants, and 96 intersection checks.
It also checks the rho1 Laurent ODE and finite Rodrigues/norm regressions.

Compare the third output with
verification/sequence-library/hankel-compression/exceptional-replay.json,
ignoring elapsed_seconds. The expected order list is
0, 1, 3, 6, 7, 9, 10, 12, 14, 18, 22, 26, 28, 42. The number zero denotes
eventual vanishing. Orders 10 and 22 occur at the stated quadratic relations
over fields admitting the required square roots; they have no nonzero real
u,v solution. Every reduced recurrence starts at index one, with W0=1 retained.

The certificate is rational JSON with sparse triples [t exponent, s exponent,
rational coefficient], ascending univariate coefficient lists, and exact
Bezout witnesses. Its SHA-256 is
3d3549829159517966dd8802d4b409a825227e2b86dad6c0493baa5e5ff1fd90.
It was constructed using SymPy 1.14.0, but verification needs no SymPy.

The finite checks certify specified polynomial identities. Their universal
coverage follows the written smaller-recurrence and degree-bound arguments;
947 examples alone are not a proof of an infinite classification. Review is
project self-review. The fully nonzero locus abuv!=0, historical novelty,
independent review and Lean formalization are not established here.

The preceding 83-member source edition is retained unchanged at
research/sequence-closed-forms/retained-sources/sequence-formula-source-15a218cb.zip
in the repository. Its SHA-256 is
b58c441239f673ed6b65a7203b20b46636376366b6308a95a47c93c26c3fc93d.
Earlier proofs, coefficients, replay results and reproduction instructions are
preserved in this edition; this document adds a separate new replay command.
